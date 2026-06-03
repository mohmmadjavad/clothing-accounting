from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, Frame, PageTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
import os
from io import BytesIO
from PIL import Image as PILImage
import base64


class InvoicePDF:
    def __init__(self, settings):
        self.settings = settings
        self.width, self.height = A4
        self.font_name = 'PersianFont'
        self.font_bold = 'PersianFont-Bold'
        self.setup_fonts()
        self.primary_color = HexColor('#6C5CE7')
        self.secondary_color = HexColor('#2D3436')
        self.light_bg = HexColor('#F8F7FF')
        self.border_color = HexColor('#E0DDFF')

    def setup_fonts(self):
        """راه‌اندازی فونت فارسی - اولویت با فونت داخلی پروژه"""

        # مسیر فونت داخلی پروژه
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bundled_font = os.path.join(base_dir, 'fonts', 'Bidad Medium.otf')

        # مسیرهای احتمالی فونت
        windows_font_dir = os.environ.get('WINDIR', 'C:\\Windows')
        font_candidates = [
            # فونت داخلی پروژه (اولویت اول)
            (bundled_font, bundled_font),
            # Tahoma ویندوز
            (
                os.path.join(windows_font_dir, 'Fonts', 'tahoma.ttf'),
                os.path.join(windows_font_dir, 'Fonts', 'tahomabd.ttf')
            ),
            # Arial ویندوز
            (
                os.path.join(windows_font_dir, 'Fonts', 'arial.ttf'),
                os.path.join(windows_font_dir, 'Fonts', 'arialbd.ttf')
            ),
        ]

        for normal_path, bold_path in font_candidates:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont(self.font_name, normal_path))
                    bp = bold_path if os.path.exists(bold_path) else normal_path
                    pdfmetrics.registerFont(TTFont(self.font_bold, bp))
                    return
                except Exception:
                    continue

        raise Exception("هیچ فونت فارسی‌ای پیدا نشد. لطفاً فایل fonts/Bidad Medium.otf را بررسی کنید.")

    def reshape(self, text):
        """اصلاح متن فارسی برای PDF"""
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception:
            return str(text)

    def generate_invoice(self, order_data):
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        story = []

        # هدر
        header_data = [[
            self.reshape(self.settings.get('brand_name', 'برند پوشاک')),
            self.reshape('فاکتور فروش'),
        ]]
        header_table = Table(header_data, colWidths=[doc.width * 0.6, doc.width * 0.4])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), white),
            ('FONTNAME', (0, 0), (-1, -1), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8 * mm))

        # اطلاعات فاکتور
        invoice_info = [
            [self.reshape(f"شماره فاکتور: {order_data.get('invoice_number', '')}"),
             self.reshape(f"تاریخ: {order_data.get('date', '')}")],
            [self.reshape(f"مشتری: {order_data.get('customer_name', '')}"),
             self.reshape(f"موبایل: {order_data.get('customer_mobile', '')}")],
        ]
        info_table = Table(invoice_info, colWidths=[doc.width * 0.5, doc.width * 0.5])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.light_bg),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, self.border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, self.border_color),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 6 * mm))

        # جدول اقلام
        items = order_data.get('items', [])
        table_data = [[
            self.reshape('ردیف'),
            self.reshape('کالا'),
            self.reshape('رنگ / سایز'),
            self.reshape('تعداد'),
            self.reshape('قیمت واحد'),
            self.reshape('جمع'),
        ]]

        for i, item in enumerate(items, 1):
            table_data.append([
                str(i),
                self.reshape(item.get('name', '')),
                self.reshape(f"{item.get('color', '')} / {item.get('size', '')}"),
                str(item.get('quantity', '')),
                f"{int(item.get('unit_price', 0)):,}",
                f"{int(item.get('total_price', 0)):,}",
            ])

        col_widths = [
            doc.width * 0.06,
            doc.width * 0.30,
            doc.width * 0.20,
            doc.width * 0.10,
            doc.width * 0.17,
            doc.width * 0.17,
        ]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F7FF')]),
            ('BOX', (0, 0), (-1, -1), 0.5, self.border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, self.border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 5 * mm))

        # جمع‌بندی
        total = order_data.get('total_amount', 0)
        discount = order_data.get('discount', 0)
        final = order_data.get('final_amount', 0)

        summary_data = [
            [self.reshape('جمع کل:'), f"{int(total):,} تومان"],
            [self.reshape('تخفیف:'), f"{int(discount):,} تومان"],
            [self.reshape('مبلغ قابل پرداخت:'), f"{int(final):,} تومان"],
        ]
        summary_table = Table(summary_data, colWidths=[doc.width * 0.7, doc.width * 0.3])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTNAME', (0, 2), (-1, 2), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (0, 2), (-1, 2), 13),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BACKGROUND', (0, 2), (-1, 2), self.primary_color),
            ('TEXTCOLOR', (0, 2), (-1, 2), white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, self.border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, self.border_color),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 8 * mm))

        # پاورقی
        footer_text = self.settings.get('invoice_footer', '')
        if footer_text:
            footer_style = ParagraphStyle(
                'Footer',
                fontName=self.font_name,
                fontSize=9,
                alignment=TA_CENTER,
                textColor=HexColor('#636E72'),
            )
            story.append(Paragraph(self.reshape(footer_text), footer_style))

        doc.build(story)
        return buffer.getvalue()
