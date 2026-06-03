from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QGridLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTextEdit, QApplication, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QBrush, QPixmap, QIcon
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date, get_current_shamsi_datetime
from utils.pdf_generator import InvoicePDF
import jdatetime
import os

def format_price(amount):
    """فرمت کردن عدد به صورت 1,000,000 تومان"""
    if amount is None:
        amount = 0
    amount = int(amount)
    if amount >= 0:
        return f"{amount:,} تومان"
    else:
        return f"-{abs(amount):,} تومان"

class OrderDetailDialog(QDialog):
    """دیالوگ ثبت/ویرایش سفارش"""
    def __init__(self, db, order_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.order_items = []
        
        self.setWindowTitle("ثبت سفارش / فاکتور")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(ModernStyle.get_main_stylesheet())
        self.init_ui()
        
        if order_id:
            self.load_order()
        else:
            self.generate_invoice_number()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # بخش بالایی - اطلاعات فاکتور
        top_layout = QHBoxLayout()
        
        # اطلاعات فاکتور (راست)
        invoice_group = QFrame()
        invoice_group.setObjectName("card")
        invoice_layout = QGridLayout(invoice_group)
        invoice_layout.setSpacing(10)
        
        # شماره فاکتور
        invoice_layout.addWidget(QLabel("شماره فاکتور:"), 0, 0)
        self.invoice_number = QLineEdit()
        self.invoice_number.setReadOnly(True)
        self.invoice_number.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.invoice_number.setMinimumHeight(38)
        invoice_layout.addWidget(self.invoice_number, 0, 1)
        
        # تاریخ شمسی
        invoice_layout.addWidget(QLabel("تاریخ:"), 1, 0)
        self.date_shamsi = QLineEdit()
        self.date_shamsi.setText(get_current_shamsi_date())
        self.date_shamsi.setMinimumHeight(38)
        invoice_layout.addWidget(self.date_shamsi, 1, 1)
        
        # ساعت
        invoice_layout.addWidget(QLabel("ساعت:"), 2, 0)
        self.time_input = QLineEdit()
        self.time_input.setText(jdatetime.datetime.now().strftime('%H:%M:%S'))
        self.time_input.setMinimumHeight(38)
        invoice_layout.addWidget(self.time_input, 2, 1)
        
        top_layout.addWidget(invoice_group)
        
        # اطلاعات مشتری (چپ)
        customer_group = QFrame()
        customer_group.setObjectName("card")
        customer_layout = QGridLayout(customer_group)
        customer_layout.setSpacing(10)
        
        customer_layout.addWidget(QLabel("مشتری:*"), 0, 0)
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumWidth(200)
        self.customer_combo.setMinimumHeight(38)
        self.load_customers()
        self.customer_combo.currentIndexChanged.connect(self.customer_selected)
        customer_layout.addWidget(self.customer_combo, 0, 1)
        
        # نمایش اطلاعات مشتری
        self.customer_info_label = QLabel("")
        self.customer_info_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        customer_layout.addWidget(self.customer_info_label, 1, 0, 1, 2)
        
        top_layout.addWidget(customer_group)
        layout.addLayout(top_layout)
        
        # بخش افزودن کالا به فاکتور
        add_item_layout = QHBoxLayout()
        
        add_item_layout.addWidget(QLabel("کالا:"))
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(200)
        self.product_combo.setMinimumHeight(38)
        self.load_products()
        self.product_combo.currentIndexChanged.connect(self.product_selected)
        add_item_layout.addWidget(self.product_combo)
        
        add_item_layout.addWidget(QLabel("رنگ/سایز:"))
        self.variant_combo = QComboBox()
        self.variant_combo.setMinimumWidth(150)
        self.variant_combo.setMinimumHeight(38)
        add_item_layout.addWidget(self.variant_combo)
        
        add_item_layout.addWidget(QLabel("تعداد:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(38)
        add_item_layout.addWidget(self.quantity_spin)
        
        add_item_layout.addWidget(QLabel("قیمت واحد:"))
        self.unit_price = QDoubleSpinBox()
        self.unit_price.setMaximum(999999999)
        self.unit_price.setDecimals(0)  # عدد صحیح
        self.unit_price.setGroupSeparatorShown(True)  # نمایش جداکننده هزارگان
        self.unit_price.setSuffix(" تومان")
        self.unit_price.setMinimumHeight(38)
        self.unit_price.setMinimumWidth(150)
        add_item_layout.addWidget(self.unit_price)
        
        add_btn = QPushButton("➕ افزودن به فاکتور")
        add_btn.setMinimumHeight(38)
        add_btn.clicked.connect(self.add_item_to_order)
        add_item_layout.addWidget(add_btn)
        
        layout.addLayout(add_item_layout)
        
        # جدول آیتم‌های فاکتور
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "عکس", "نام کالا", "رنگ/سایز", "تعداد", 
            "قیمت واحد", "قیمت کل", "حذف"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setDefaultSectionSize(50)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setMinimumHeight(250)
        layout.addWidget(self.items_table)
        
        # اطلاعات مالی فاکتور
        financial_layout = QHBoxLayout()
        
        financial_layout.addWidget(QLabel("تخفیف:"))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setMaximum(999999999)
        self.discount_spin.setDecimals(0)
        self.discount_spin.setGroupSeparatorShown(True)
        self.discount_spin.setSuffix(" تومان")
        self.discount_spin.setMinimumHeight(38)
        self.discount_spin.setMinimumWidth(150)
        self.discount_spin.valueChanged.connect(self.calculate_total)
        financial_layout.addWidget(self.discount_spin)
        
        financial_layout.addStretch()
        
        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {ModernStyle.PRIMARY}; background: transparent;")
        self.total_label.setMinimumWidth(250)
        financial_layout.addWidget(self.total_label)
        
        layout.addLayout(financial_layout)
        
        # توضیحات
        layout.addWidget(QLabel("توضیحات:"))
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(60)
        layout.addWidget(self.notes_text)
        
        # دکمه‌های پایین
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 ذخیره فاکتور")
        save_btn.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_order)
        btn_layout.addWidget(save_btn)
        
        print_btn = QPushButton("🖨️ چاپ فاکتور")
        print_btn.setObjectName("secondaryBtn")
        print_btn.setMinimumHeight(45)
        print_btn.clicked.connect(self.print_invoice)
        btn_layout.addWidget(print_btn)
        
        pdf_btn = QPushButton("📄 خروجی PDF")
        pdf_btn.setObjectName("successBtn")
        pdf_btn.setMinimumHeight(45)
        pdf_btn.clicked.connect(self.export_pdf)
        btn_layout.addWidget(pdf_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def load_customers(self):
        self.db.cursor.execute('SELECT id, first_name || " " || last_name, mobile FROM customers ORDER BY first_name')
        customers = self.db.cursor.fetchall()
        self.customer_combo.addItem("انتخاب کنید...", None)
        for cust_id, name, mobile in customers:
            display = f"{name} - {mobile or 'بدون شماره'}"
            self.customer_combo.addItem(display, cust_id)
    
    def load_products(self):
        self.db.cursor.execute('SELECT id, name FROM products ORDER BY name')
        products = self.db.cursor.fetchall()
        self.product_combo.addItem("انتخاب کالا...", None)
        for prod_id, name in products:
            self.product_combo.addItem(name, prod_id)
    
    def customer_selected(self):
        customer_id = self.customer_combo.currentData()
        if customer_id:
            self.db.cursor.execute('SELECT mobile, phone, address, debt FROM customers WHERE id=?', (customer_id,))
            result = self.db.cursor.fetchone()
            if result:
                mobile, phone, address, debt = result
                debt_formatted = format_price(debt or 0)
                info = f"📱 {mobile or '---'} | ☎️ {phone or '---'} | 💰 بدهی: {debt_formatted}"
                self.customer_info_label.setText(info)
    
    def product_selected(self):
        self.variant_combo.clear()
        product_id = self.product_combo.currentData()
        
        if product_id:
            self.db.cursor.execute(
                'SELECT id, color, size, stock, price FROM product_variants WHERE product_id=? AND stock > 0',
                (product_id,)
            )
            variants = self.db.cursor.fetchall()
            
            for var_id, color, size, stock, price in variants:
                self.variant_combo.addItem(f"{color} / {size} (موجودی: {stock})", var_id)
            
            if variants:
                self.unit_price.setValue(int(variants[0][4]))
    
    def add_item_to_order(self):
        product_id = self.product_combo.currentData()
        variant_id = self.variant_combo.currentData()
        
        if not product_id or not variant_id:
            QMessageBox.warning(self, "خطا", "لطفاً کالا و تنوع را انتخاب کنید")
            return
        
        product_name = self.product_combo.currentText()
        variant_text = self.variant_combo.currentText()
        quantity = self.quantity_spin.value()
        unit_price = int(self.unit_price.value())  # تبدیل به عدد صحیح
        total_price = quantity * unit_price
        
        # بررسی موجودی
        self.db.cursor.execute('SELECT stock FROM product_variants WHERE id=?', (variant_id,))
        stock = self.db.cursor.fetchone()[0]
        
        if quantity > stock:
            QMessageBox.warning(self, "خطا", f"موجودی کافی نیست! موجودی فعلی: {stock}")
            return
        
        # افزودن به جدول
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setRowHeight(row, 55)
        
        # عکس کالا
        self.db.cursor.execute('SELECT image FROM products WHERE id=?', (product_id,))
        image_data = self.db.cursor.fetchone()[0]
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            icon = QIcon(pixmap.scaled(40, 40))
            img_item = QTableWidgetItem()
            img_item.setIcon(icon)
            self.items_table.setItem(row, 0, img_item)
        else:
            self.items_table.setItem(row, 0, QTableWidgetItem("🖼️"))
        
        self.items_table.setItem(row, 1, QTableWidgetItem(product_name))
        self.items_table.setItem(row, 2, QTableWidgetItem(variant_text))
        
        # تعداد
        qty_item = QTableWidgetItem(str(quantity))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 3, qty_item)
        
        # قیمت واحد با فرمت
        unit_price_item = QTableWidgetItem(format_price(unit_price))
        unit_price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 4, unit_price_item)
        
        # قیمت کل با فرمت
        total_price_item = QTableWidgetItem(format_price(total_price))
        total_price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_price_item.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        self.items_table.setItem(row, 5, total_price_item)
        
        # دکمه حذف
        delete_btn = QPushButton("🗑️")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMaximumWidth(50)
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(lambda: self.remove_item(row))
        self.items_table.setCellWidget(row, 6, delete_btn)
        
        # ذخیره اطلاعات آیتم
        self.order_items.append({
            'product_id': product_id,
            'variant_id': variant_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price
        })
        
        self.calculate_total()
        self.quantity_spin.setValue(1)
    
    def remove_item(self, row):
        self.items_table.removeRow(row)
        if row < len(self.order_items):
            del self.order_items[row]
        self.calculate_total()
    
    def calculate_total(self):
        total = sum(item['total_price'] for item in self.order_items)
        discount = int(self.discount_spin.value())
        final = max(0, total - discount)
        self.total_label.setText(f"جمع کل: {format_price(final)}")
    
    def generate_invoice_number(self):
        # استفاده از MAX برای جلوگیری از تکرار شماره فاکتور
        date = jdatetime.datetime.now().strftime('%Y%m%d')
        prefix = f"INV-{date}-"
        self.db.cursor.execute(
            "SELECT MAX(CAST(SUBSTR(invoice_number, ?) AS INTEGER)) FROM orders WHERE invoice_number LIKE ?",
            (len(prefix) + 1, prefix + '%')
        )
        result = self.db.cursor.fetchone()[0]
        next_num = (result or 0) + 1
        self.invoice_number.setText(f"INV-{date}-{next_num:04d}")
    
    def save_order(self):
        customer_id = self.customer_combo.currentData()
        
        if not customer_id:
            QMessageBox.warning(self, "خطا", "لطفاً مشتری را انتخاب کنید")
            return
        
        if not self.order_items:
            QMessageBox.warning(self, "خطا", "حداقل یک کالا به فاکتور اضافه کنید")
            return
        
        try:
            invoice_number = self.invoice_number.text()
            date_shamsi = self.date_shamsi.text()
            discount = int(self.discount_spin.value())
            total_amount = sum(item['total_price'] for item in self.order_items)
            final_amount = max(0, total_amount - discount)
            notes = self.notes_text.toPlainText().strip()
            
            if self.order_id:
                self.db.cursor.execute('SELECT variant_id, quantity FROM order_items WHERE order_id=?', 
                                      (self.order_id,))
                old_items = self.db.cursor.fetchall()
                for var_id, qty in old_items:
                    self.db.cursor.execute('UPDATE product_variants SET stock = stock + ? WHERE id=?', 
                                          (qty, var_id))
                
                self.db.cursor.execute('DELETE FROM order_items WHERE order_id=?', (self.order_id,))
                self.db.cursor.execute('DELETE FROM orders WHERE id=?', (self.order_id,))
            
            self.db.cursor.execute('''
                INSERT INTO orders (invoice_number, customer_id, order_date, order_date_shamsi, 
                                   total_amount, discount, final_amount, status, notes)
                VALUES (?, ?, datetime('now'), ?, ?, ?, ?, 'pending', ?)
            ''', (invoice_number, customer_id, date_shamsi, 
                 total_amount, discount, final_amount, notes))
            
            order_id = self.db.cursor.lastrowid
            
            for item in self.order_items:
                self.db.cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, variant_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, item['product_id'], item['variant_id'], 
                     item['quantity'], item['unit_price'], item['total_price']))
                
                self.db.cursor.execute('''
                    UPDATE product_variants SET stock = stock - ? WHERE id=?
                ''', (item['quantity'], item['variant_id']))
            
            self.db.cursor.execute('''
                UPDATE customers SET debt = debt + ? WHERE id=?
            ''', (final_amount, customer_id))
            
            # به‌روزرسانی وضعیت پرداخت اگر مشتری بستانکار است
            self.db.cursor.execute('''
                UPDATE orders SET payment_status = 'paid'
                WHERE id=? AND payment_status='unpaid' AND final_amount <= (
                    SELECT COALESCE(credit, 0) - COALESCE(debt, 0) FROM customers WHERE id=?
                )
            ''', (order_id, customer_id))

            self.db.conn.commit()
            QMessageBox.information(self, "موفق", "✅ فاکتور با موفقیت ثبت شد")
            self.accept()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "خطا", f"خطا در ثبت فاکتور: {e}")
    
    def print_invoice(self):
        """پیش‌نمایش و چاپ فاکتور"""
        try:
            if self.items_table.rowCount() == 0:
                QMessageBox.warning(self, "هشدار", "ابتدا آیتم‌هایی به فاکتور اضافه کنید")
                return
            
            order_data = self.get_order_data()
            
            settings = {
                'brand_name': self.db.get_setting('brand_name') or 'برند پوشاک',
                'brand_address': self.db.get_setting('brand_address') or '',
                'phone': self.db.get_setting('phone') or '',
                'invoice_footer': self.db.get_setting('invoice_footer') or 'با تشکر از خرید شما'
            }
            
            pdf_gen = InvoicePDF(settings)
            pdf_bytes = pdf_gen.generate_invoice(order_data)
            
            temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "temp_invoice.pdf")
            with open(temp_path, 'wb') as f:
                f.write(pdf_bytes)
            
            import subprocess
            subprocess.Popen([temp_path], shell=True)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ فاکتور: {str(e)}")
    
    def export_pdf(self):
        """خروجی PDF فاکتور"""
        try:
            if self.items_table.rowCount() == 0:
                QMessageBox.warning(self, "هشدار", "ابتدا آیتم‌هایی به فاکتور اضافه کنید")
                return
            
            order_data = self.get_order_data()
            
            settings = {
                'brand_name': self.db.get_setting('brand_name') or 'برند پوشاک',
                'brand_address': self.db.get_setting('brand_address') or '',
                'phone': self.db.get_setting('phone') or '',
                'invoice_footer': self.db.get_setting('invoice_footer') or 'با تشکر از خرید شما'
            }
            
            pdf_gen = InvoicePDF(settings)
            pdf_bytes = pdf_gen.generate_invoice(order_data)
            
            invoice_num = self.invoice_number.text()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "ذخیره PDF فاکتور", 
                f"invoice_{invoice_num}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                QMessageBox.information(self, "موفق", f"✅ فاکتور با موفقیت ذخیره شد:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در خروجی PDF: {str(e)}")
    
    def get_order_data(self):
        """آماده‌سازی داده‌های فاکتور"""
        import base64
        
        items = []
        
        for idx, item_data in enumerate(self.order_items):
            try:
                product_id = item_data['product_id']
                
                # اطلاعات از order_items
                product_name = ""
                variant_text = ""
                
                # خوندن از جدول برای نام و رنگ/سایز
                if self.items_table.item(idx, 1):
                    product_name = self.items_table.item(idx, 1).text()
                if self.items_table.item(idx, 2):
                    variant_text = self.items_table.item(idx, 2).text()
                
                color = variant_text.split(' / ')[0] if ' / ' in variant_text else variant_text
                size = variant_text.split(' / ')[1].strip() if ' / ' in variant_text else ''
                
                # تصویر محصول
                product_image = None
                if product_id:
                    try:
                        self.db.cursor.execute('SELECT image FROM products WHERE id=?', (product_id,))
                        result = self.db.cursor.fetchone()
                        if result and result[0]:
                            product_image = base64.b64encode(result[0]).decode('utf-8')
                    except Exception as e:
                        print(f"خطا در دریافت تصویر محصول {product_id}: {e}")
                
                items.append({
                    'product_name': product_name,
                    'color': color,
                    'size': size,
                    'quantity': item_data['quantity'],
                    'unit_price': item_data['unit_price'],
                    'total_price': item_data['total_price'],
                    'product_image': product_image
                })
                
            except Exception as e:
                print(f"خطا در خواندن آیتم {idx}: {e}")
                continue
        
        # دریافت نام مشتری
        customer_text = self.customer_combo.currentText()
        if ' - ' in customer_text:
            customer_name = customer_text.split(' - ')[0].strip()
        else:
            customer_name = customer_text.strip()
        
        # محاسبه مبلغ نهایی
        total = sum(item['total_price'] for item in items)
        discount = int(self.discount_spin.value())
        final_amount = max(0, total - discount)
        
        return {
            'invoice_number': self.invoice_number.text().strip(),
            'date_shamsi': self.date_shamsi.text().strip(),
            'customer_name': customer_name,
            'items': items,
            'final_amount': final_amount,
            'discount': discount,
            'notes': self.notes_text.toPlainText().strip()
        }
    
    def load_order(self):
        self.db.cursor.execute('SELECT * FROM orders WHERE id=?', (self.order_id,))
        order = self.db.cursor.fetchone()
        
        if order:
            _, inv_num, cust_id, _, date_shamsi, total, discount, final, status, pay, notes, _ = order
            
            self.invoice_number.setText(inv_num)
            self.date_shamsi.setText(date_shamsi or '')
            self.discount_spin.setValue(int(discount or 0))
            self.notes_text.setText(notes or '')
            
            index = self.customer_combo.findData(cust_id)
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)
            
            self.db.cursor.execute('''
                SELECT oi.*, p.name, p.image, pv.color, pv.size 
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                LEFT JOIN product_variants pv ON oi.variant_id = pv.id
                WHERE oi.order_id=?
            ''', (self.order_id,))
            
            items = self.db.cursor.fetchall()
            
            self.items_table.setRowCount(0)
            self.order_items = []
            
            for item in items:
                item_id, _, prod_id, var_id, qty, unit_price, total_price, prod_name, image, color, size = item
                
                row = self.items_table.rowCount()
                self.items_table.insertRow(row)
                self.items_table.setRowHeight(row, 55)
                
                if image:
                    pixmap = QPixmap()
                    pixmap.loadFromData(image)
                    icon = QIcon(pixmap.scaled(40, 40))
                    img_item = QTableWidgetItem()
                    img_item.setIcon(icon)
                    self.items_table.setItem(row, 0, img_item)
                else:
                    self.items_table.setItem(row, 0, QTableWidgetItem("🖼️"))
                
                self.items_table.setItem(row, 1, QTableWidgetItem(prod_name))
                self.items_table.setItem(row, 2, QTableWidgetItem(f"{color or ''} / {size or ''}"))
                
                qty_item = QTableWidgetItem(str(qty))
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 3, qty_item)
                
                unit_price_item = QTableWidgetItem(format_price(int(unit_price)))
                unit_price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 4, unit_price_item)
                
                total_price_item = QTableWidgetItem(format_price(int(total_price)))
                total_price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total_price_item.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                self.items_table.setItem(row, 5, total_price_item)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("dangerBtn")
                delete_btn.setMaximumWidth(50)
                delete_btn.setMinimumHeight(40)
                delete_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
                self.items_table.setCellWidget(row, 6, delete_btn)
                
                self.order_items.append({
                    'product_id': prod_id,
                    'variant_id': var_id,
                    'quantity': qty,
                    'unit_price': int(unit_price),
                    'total_price': int(total_price)
                })
            
            self.calculate_total()


class OrdersPage(QWidget):
    """صفحه مدیریت سفارشات"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_orders()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # هدر
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 مدیریت سفارشات")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # فیلترها
        self.date_filter = QComboBox()
        self.date_filter.setMinimumHeight(38)
        self.date_filter.addItems(["همه تاریخ‌ها", "امروز", "دیروز", "هفته جاری", "ماه جاری"])
        self.date_filter.currentTextChanged.connect(self.filter_orders)
        header_layout.addWidget(self.date_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(38)
        self.status_filter.addItems(["همه وضعیت‌ها", "در انتظار", "تکمیل شده", "لغو شده"])
        self.status_filter.currentTextChanged.connect(self.filter_orders)
        header_layout.addWidget(self.status_filter)
        
        add_btn = QPushButton("➕ فاکتور جدید")
        add_btn.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        add_btn.setMinimumHeight(42)
        add_btn.clicked.connect(self.add_order)
        header_layout.addWidget(add_btn)
        
        main_layout.addLayout(header_layout)
        
        # جدول سفارشات
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(9)
        self.orders_table.setHorizontalHeaderLabels([
            "شماره فاکتور", "تاریخ", "مشتری", "مبلغ کل", 
            "تخفیف", "مبلغ نهایی", "وضعیت", "پرداخت", "عملیات"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.orders_table.verticalHeader().setDefaultSectionSize(50)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.doubleClicked.connect(self.edit_order)
        main_layout.addWidget(self.orders_table)
        
        # آمار سریع
        stats_layout = QHBoxLayout()
        
        self.today_orders_label = QLabel("سفارشات امروز: 0")
        self.today_orders_label.setStyleSheet(f"color: {ModernStyle.PRIMARY}; font-weight: bold; background: transparent;")
        stats_layout.addWidget(self.today_orders_label)
        
        self.today_revenue_label = QLabel("درآمد امروز: 0 تومان")
        self.today_revenue_label.setStyleSheet(f"color: {ModernStyle.SUCCESS}; font-weight: bold; background: transparent;")
        stats_layout.addWidget(self.today_revenue_label)
        
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
    
    def load_orders(self):
        query = '''
            SELECT o.*, c.first_name || " " || c.last_name as customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.created_at DESC
        '''
        
        self.db.cursor.execute(query)
        orders = self.db.cursor.fetchall()
        self.all_orders = orders
        self.display_orders(orders)
        self.update_stats()
    
    def display_orders(self, orders):
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            order_id, inv_num, cust_id, _, date_shamsi, total, discount, final, status, payment, notes, _, cust_name = order
            
            self.orders_table.setRowHeight(row, 50)
            
            self.orders_table.setItem(row, 0, QTableWidgetItem(inv_num))
            self.orders_table.setItem(row, 1, QTableWidgetItem(date_shamsi or ''))
            self.orders_table.setItem(row, 2, QTableWidgetItem(cust_name))
            
            # مبلغ کل
            total_item = QTableWidgetItem(format_price(int(total or 0)))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_table.setItem(row, 3, total_item)
            
            # تخفیف
            discount_item = QTableWidgetItem(format_price(int(discount or 0)))
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_table.setItem(row, 4, discount_item)
            
            # مبلغ نهایی
            final_item = QTableWidgetItem(format_price(int(final or 0)))
            final_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            final_item.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
            self.orders_table.setItem(row, 5, final_item)
            
            # وضعیت با رنگ
            status_item = QTableWidgetItem(status or 'pending')
            if status == 'completed':
                status_item.setBackground(QBrush(QColor("#E8F5E9")))
                status_item.setForeground(QBrush(QColor("#00B894")))
            elif status == 'cancelled':
                status_item.setBackground(QBrush(QColor("#FFE0E0")))
                status_item.setForeground(QBrush(QColor("#E17055")))
            else:
                status_item.setBackground(QBrush(QColor("#FFF3E0")))
            self.orders_table.setItem(row, 6, status_item)
            
            # پرداخت
            pay_item = QTableWidgetItem(payment or 'unpaid')
            if payment == 'paid':
                pay_item.setForeground(QBrush(QColor("#00B894")))
            else:
                pay_item.setForeground(QBrush(QColor("#E17055")))
            self.orders_table.setItem(row, 7, pay_item)
            
            # دکمه‌ها
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.setMinimumHeight(35)
            edit_btn.clicked.connect(lambda checked, oid=order_id: self.edit_order_by_id(oid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setMinimumHeight(35)
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(lambda checked, oid=order_id: self.delete_order(oid))
            actions_layout.addWidget(delete_btn)
            
            self.orders_table.setCellWidget(row, 8, actions_widget)
    
    def add_order(self):
        dialog = OrderDetailDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_orders()
            self.db.data_changed.emit()
    
    def edit_order(self):
        current_row = self.orders_table.currentRow()
        if current_row >= 0:
            order_id = self.all_orders[current_row][0]
            self.edit_order_by_id(order_id)
    
    def edit_order_by_id(self, order_id):
        dialog = OrderDetailDialog(self.db, order_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_orders()
            self.db.data_changed.emit()
    
    def delete_order(self, order_id):
        reply = QMessageBox.question(
            self, "حذف سفارش",
            "آیا از حذف این سفارش اطمینان دارید؟\nموجودی کالاها به انبار برمی‌گردد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute('SELECT variant_id, quantity FROM order_items WHERE order_id=?', 
                                      (order_id,))
                items = self.db.cursor.fetchall()
                for var_id, qty in items:
                    self.db.cursor.execute('UPDATE product_variants SET stock = stock + ? WHERE id=?', 
                                          (qty, var_id))
                
                self.db.cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
                self.db.conn.commit()
                self.load_orders()
                self.db.data_changed.emit()
                QMessageBox.information(self, "موفق", "سفارش با موفقیت حذف شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا: {e}")
    
    def filter_orders(self):
        date_filter = self.date_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered = self.all_orders.copy()
        
        today = get_current_shamsi_date()
        if date_filter == "امروز":
            filtered = [o for o in filtered if o[4] == today]
        elif date_filter == "دیروز":
            yesterday = jdatetime.date.today() - jdatetime.timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y/%m/%d')
            filtered = [o for o in filtered if o[4] == yesterday_str]
        
        if status_filter == "تکمیل شده":
            filtered = [o for o in filtered if o[8] == 'completed']
        elif status_filter == "لغو شده":
            filtered = [o for o in filtered if o[8] == 'cancelled']
        elif status_filter == "در انتظار":
            filtered = [o for o in filtered if o[8] == 'pending']
        
        self.display_orders(filtered)
    
    def update_stats(self):
        today = get_current_shamsi_date()
        
        self.db.cursor.execute('SELECT COUNT(*), COALESCE(SUM(final_amount), 0) FROM orders WHERE order_date_shamsi=?', 
                              (today,))
        count, revenue = self.db.cursor.fetchone()
        
        self.today_orders_label.setText(f"سفارشات امروز: {count}")
        self.today_revenue_label.setText(f"درآمد امروز: {format_price(int(revenue or 0))}")