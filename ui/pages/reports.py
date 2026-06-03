from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QMessageBox, QFileDialog, QTabWidget,
    QGroupBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date
import jdatetime
import os


class ReportsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_all()

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # هدر
        header = QHBoxLayout()
        title = QLabel("📈 گزارش‌گیری و آمار")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()

        self.year_combo = QComboBox()
        current_year = jdatetime.datetime.now().year
        for y in range(current_year - 2, current_year + 1):
            self.year_combo.addItem(str(y), y)
        self.year_combo.setCurrentIndex(self.year_combo.count() - 1)
        self.year_combo.currentIndexChanged.connect(self.load_all)
        self.year_combo.setMinimumWidth(100)
        header.addWidget(QLabel("سال:"))
        header.addWidget(self.year_combo)

        main_layout.addLayout(header)

        # تب‌ها
        tabs = QTabWidget()

        # تب فروش ماهانه
        tabs.addTab(self._create_monthly_tab(), "📅 فروش ماهانه")
        # تب محصولات برتر
        tabs.addTab(self._create_products_tab(), "🏆 محصولات برتر")
        # تب مشتریان برتر
        tabs.addTab(self._create_customers_tab(), "👑 مشتریان برتر")
        # تب موجودی
        tabs.addTab(self._create_inventory_tab(), "📦 گزارش انبار")

        main_layout.addWidget(tabs)

    def _create_monthly_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)

        # نمودار متنی فروش
        chart_group = QGroupBox("📊 نمودار فروش ماهانه")
        chart_layout = QVBoxLayout(chart_group)

        self.chart_widget = QWidget()
        self.chart_widget.setMinimumHeight(200)
        self.chart_widget.setStyleSheet("background: white; border-radius: 8px;")
        chart_layout.addWidget(self.chart_widget)
        self.chart_inner = QVBoxLayout(self.chart_widget)
        self.chart_inner.setSpacing(4)
        self.chart_inner.setContentsMargins(15, 10, 15, 10)

        layout.addWidget(chart_group)

        # جدول فروش ماهانه
        export_btn = QPushButton("📥 خروجی Excel")
        export_btn.setMaximumWidth(150)
        export_btn.setObjectName("successBtn")
        export_btn.clicked.connect(self.export_monthly_excel)
        layout.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(4)
        self.monthly_table.setHorizontalHeaderLabels(["ماه", "تعداد سفارش", "مبلغ کل (تومان)", "میانگین (تومان)"])
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.monthly_table.verticalHeader().setVisible(False)
        self.monthly_table.setAlternatingRowColors(True)
        self.monthly_table.setMaximumHeight(400)
        layout.addWidget(self.monthly_table)

        return w

    def _create_products_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)

        export_btn = QPushButton("📥 خروجی Excel")
        export_btn.setMaximumWidth(150)
        export_btn.setObjectName("successBtn")
        export_btn.clicked.connect(self.export_products_excel)
        layout.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["نام محصول", "تعداد فروخته‌شده", "درآمد کل (تومان)"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setAlternatingRowColors(True)
        layout.addWidget(self.products_table)

        return w

    def _create_customers_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)

        export_btn = QPushButton("📥 خروجی Excel")
        export_btn.setMaximumWidth(150)
        export_btn.setObjectName("successBtn")
        export_btn.clicked.connect(self.export_customers_excel)
        layout.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["نام مشتری", "موبایل", "تعداد سفارش", "کل خرید (تومان)"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_table.verticalHeader().setVisible(False)
        self.customers_table.setAlternatingRowColors(True)
        layout.addWidget(self.customers_table)

        return w

    def _create_inventory_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)

        btn_row = QHBoxLayout()

        export_btn = QPushButton("📥 خروجی Excel")
        export_btn.setMaximumWidth(150)
        export_btn.setObjectName("successBtn")
        export_btn.clicked.connect(self.export_inventory_excel)
        btn_row.addWidget(export_btn)
        btn_row.addStretch()

        self.inv_filter = QComboBox()
        self.inv_filter.addItems(["همه", "کم‌موجودی", "بدون موجودی"])
        self.inv_filter.currentTextChanged.connect(self.filter_inventory)
        btn_row.addWidget(QLabel("فیلتر:"))
        btn_row.addWidget(self.inv_filter)

        layout.addLayout(btn_row)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "کد", "نام کالا", "دسته‌بندی", "رنگ", "سایز", "موجودی", "وضعیت"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.setAlternatingRowColors(True)
        layout.addWidget(self.inventory_table)

        return w

    def load_all(self):
        year = self.year_combo.currentData()
        self.load_monthly(year)
        self.load_products()
        self.load_customers()
        self.load_inventory()

    def load_monthly(self, year):
        try:
            data = self.db.get_monthly_sales(year)

            # پاک کردن نمودار قبلی
            while self.chart_inner.count():
                item = self.chart_inner.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # پیدا کردن حداکثر برای مقیاس
            max_amount = max((d['amount'] for d in data), default=1) or 1

            colors = [ModernStyle.PRIMARY, ModernStyle.SECONDARY, ModernStyle.ACCENT,
                      ModernStyle.SUCCESS, ModernStyle.WARNING, ModernStyle.INFO]

            for i, d in enumerate(data):
                row = QHBoxLayout()

                month_lbl = QLabel(d['month'])
                month_lbl.setFixedWidth(70)
                month_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                month_lbl.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 11px;")
                row.addWidget(month_lbl)

                bar_frame = QFrame()
                bar_frame.setFixedHeight(22)
                bar_width = max(4, int((d['amount'] / max_amount) * 400))
                bar_frame.setFixedWidth(bar_width)
                color = colors[i % len(colors)]
                bar_frame.setStyleSheet(f"background: {color}; border-radius: 4px;")
                row.addWidget(bar_frame)

                val_lbl = QLabel(f"{int(d['amount']):,} تومان  ({d['count']} سفارش)")
                val_lbl.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; font-size: 11px;")
                row.addWidget(val_lbl)
                row.addStretch()

                row_widget = QWidget()
                row_widget.setLayout(row)
                self.chart_inner.addWidget(row_widget)

            # جدول
            self.monthly_table.setRowCount(len(data))
            total_sum = 0
            total_count = 0
            for row, d in enumerate(data):
                self.monthly_table.setItem(row, 0, QTableWidgetItem(d['month']))
                count_item = QTableWidgetItem(str(d['count']))
                count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.monthly_table.setItem(row, 1, count_item)
                amt_item = QTableWidgetItem(f"{int(d['amount']):,}")
                amt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.monthly_table.setItem(row, 2, amt_item)
                avg = int(d['amount'] / d['count']) if d['count'] > 0 else 0
                avg_item = QTableWidgetItem(f"{avg:,}")
                avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.monthly_table.setItem(row, 3, avg_item)
                total_sum += d['amount']
                total_count += d['count']

            # ردیف جمع
            self.monthly_table.setRowCount(len(data) + 1)
            total_row = len(data)
            bold_font = QFont("Tahoma", 11, QFont.Weight.Bold)
            lbl = QTableWidgetItem("🔢 جمع کل سال")
            lbl.setFont(bold_font)
            lbl.setBackground(QBrush(QColor("#EDE7FF")))
            self.monthly_table.setItem(total_row, 0, lbl)
            c = QTableWidgetItem(str(total_count))
            c.setFont(bold_font)
            c.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            c.setBackground(QBrush(QColor("#EDE7FF")))
            self.monthly_table.setItem(total_row, 1, c)
            s = QTableWidgetItem(f"{int(total_sum):,}")
            s.setFont(bold_font)
            s.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            s.setBackground(QBrush(QColor("#EDE7FF")))
            self.monthly_table.setItem(total_row, 2, s)
            self.monthly_table.setItem(total_row, 3, QTableWidgetItem(""))

        except Exception as e:
            print(f"Reports monthly error: {e}")

    def load_products(self):
        try:
            data = self.db.get_top_products(20)
            self.products_data = data
            self.products_table.setRowCount(len(data))
            for row, (name, qty, revenue) in enumerate(data):
                self.products_table.setItem(row, 0, QTableWidgetItem(name or ''))
                qty_item = QTableWidgetItem(str(qty or 0))
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.products_table.setItem(row, 1, qty_item)
                rev_item = QTableWidgetItem(f"{int(revenue or 0):,}")
                rev_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.products_table.setItem(row, 2, rev_item)
                if row == 0:
                    for col in range(3):
                        item = self.products_table.item(row, col)
                        if item:
                            item.setBackground(QBrush(QColor("#FFF3CD")))
        except Exception as e:
            print(f"Reports products error: {e}")

    def load_customers(self):
        try:
            data = self.db.get_top_customers(20)
            self.customers_data = data
            self.customers_table.setRowCount(len(data))
            for row, (name, mobile, count, total) in enumerate(data):
                self.customers_table.setItem(row, 0, QTableWidgetItem(name or ''))
                self.customers_table.setItem(row, 1, QTableWidgetItem(mobile or ''))
                count_item = QTableWidgetItem(str(count or 0))
                count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.customers_table.setItem(row, 2, count_item)
                total_item = QTableWidgetItem(f"{int(total or 0):,}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.customers_table.setItem(row, 3, total_item)
                if row == 0:
                    for col in range(4):
                        item = self.customers_table.item(row, col)
                        if item:
                            item.setBackground(QBrush(QColor("#FFF3CD")))
        except Exception as e:
            print(f"Reports customers error: {e}")

    def load_inventory(self):
        try:
            data = self.db.get_inventory_report()
            self.inventory_data = data
            self._display_inventory(data)
        except Exception as e:
            print(f"Reports inventory error: {e}")

    def filter_inventory(self, filter_text):
        if not hasattr(self, 'inventory_data'):
            return
        if filter_text == "کم‌موجودی":
            filtered = [r for r in self.inventory_data if r[8] == 'کم' and r[5] > 0]
        elif filter_text == "بدون موجودی":
            filtered = [r for r in self.inventory_data if r[5] == 0]
        else:
            filtered = self.inventory_data
        self._display_inventory(filtered)

    def _display_inventory(self, data):
        self.inventory_table.setRowCount(len(data))
        for row, (code, name, cat, color, size, stock, price, min_alert, status) in enumerate(data):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(code or ''))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(name or ''))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(cat or ''))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(color or ''))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(size or ''))
            stock_item = QTableWidgetItem(str(stock or 0))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stock == 0:
                stock_item.setBackground(QBrush(QColor("#FFE0E0")))
                stock_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
            elif status == 'کم':
                stock_item.setBackground(QBrush(QColor("#FFF3E0")))
                stock_item.setForeground(QBrush(QColor(ModernStyle.WARNING)))
            self.inventory_table.setItem(row, 5, stock_item)
            status_item = QTableWidgetItem("🔴 کم" if status == 'کم' else "✅ کافی")
            self.inventory_table.setItem(row, 6, status_item)

    # ============ خروجی Excel ============

    def export_monthly_excel(self):
        self._export_table_to_excel(self.monthly_table, "فروش_ماهانه")

    def export_products_excel(self):
        self._export_table_to_excel(self.products_table, "محصولات_برتر")

    def export_customers_excel(self):
        self._export_table_to_excel(self.customers_table, "مشتریان_برتر")

    def export_inventory_excel(self):
        self._export_table_to_excel(self.inventory_table, "گزارش_انبار")

    def _export_table_to_excel(self, table, filename_prefix):
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            QMessageBox.warning(self, "خطا", "برای خروجی Excel، کتابخانه openpyxl را نصب کنید:\npip install openpyxl")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره فایل Excel",
            f"{filename_prefix}_{get_current_shamsi_date().replace('/', '-')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = filename_prefix

            header_fill = PatternFill("solid", fgColor="6C5CE7")
            header_font = Font(bold=True, color="FFFFFF", name="Tahoma")
            center_align = Alignment(horizontal="center", vertical="center")

            # هدرها
            headers = []
            for col in range(table.columnCount()):
                item = table.horizontalHeaderItem(col)
                headers.append(item.text() if item else f"ستون {col + 1}")

            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                ws.column_dimensions[cell.column_letter].width = 20

            # داده‌ها
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    val = item.text() if item else ""
                    ws.cell(row=row + 2, column=col + 1, value=val).alignment = center_align

            wb.save(path)
            QMessageBox.information(self, "موفق", f"✅ فایل Excel با موفقیت ذخیره شد:\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {e}")
