from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QGridLayout, QTextEdit, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from ui.styles import ModernStyle

class CustomerDetailDialog(QDialog):
    def __init__(self, db, customer_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.customer_id = customer_id
        self.setWindowTitle("اطلاعات مشتری")
        self.setMinimumSize(700, 550)
        self.init_ui()
        if customer_id:
            self.load_customer()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # فرم ساده بدون گروپ باکس
        form = QGridLayout()
        form.setSpacing(10)
        
        row = 0
        # کد مشتری
        form.addWidget(QLabel("کد:"), row, 0)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("کد یکتا")
        self.code_input.setMinimumHeight(38)
        form.addWidget(self.code_input, row, 1)
        row += 1
        
        # نام
        form.addWidget(QLabel("نام:*"), row, 0)
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("نام")
        self.first_name_input.setMinimumHeight(38)
        form.addWidget(self.first_name_input, row, 1)
        row += 1
        
        # نام خانوادگی
        form.addWidget(QLabel("نام خانوادگی:*"), row, 0)
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("نام خانوادگی")
        self.last_name_input.setMinimumHeight(38)
        form.addWidget(self.last_name_input, row, 1)
        row += 1
        
        # موبایل
        form.addWidget(QLabel("موبایل:*"), row, 0)
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("09123456789")
        self.mobile_input.setMinimumHeight(38)
        form.addWidget(self.mobile_input, row, 1)
        row += 1
        
        # تلفن ثابت
        form.addWidget(QLabel("تلفن ثابت:"), row, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("021-12345678")
        self.phone_input.setMinimumHeight(38)
        form.addWidget(self.phone_input, row, 1)
        row += 1
        
        # آدرس
        form.addWidget(QLabel("آدرس:"), row, 0)
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("آدرس کامل...")
        self.address_input.setMaximumHeight(80)
        self.address_input.setMinimumHeight(70)
        form.addWidget(self.address_input, row, 1)
        row += 1
        
        # شماره شبا
        form.addWidget(QLabel("شماره شبا:"), row, 0)
        self.shaba_input = QLineEdit()
        self.shaba_input.setPlaceholderText("IR...")
        self.shaba_input.setMinimumHeight(38)
        form.addWidget(self.shaba_input, row, 1)
        row += 1
        
        # شماره حساب
        form.addWidget(QLabel("شماره حساب:"), row, 0)
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("شماره حساب بانکی")
        self.account_input.setMinimumHeight(38)
        form.addWidget(self.account_input, row, 1)
        row += 1
        
        # بدهی
        form.addWidget(QLabel("بدهی (تومان):"), row, 0)
        self.debt_spin = QLineEdit()
        self.debt_spin.setReadOnly(True)
        self.debt_spin.setText("0")
        self.debt_spin.setMinimumHeight(38)
        form.addWidget(self.debt_spin, row, 1)
        row += 1
        
        # بستانکاری
        form.addWidget(QLabel("بستانکاری (تومان):"), row, 0)
        self.credit_spin = QLineEdit()
        self.credit_spin.setReadOnly(True)
        self.credit_spin.setText("0")
        self.credit_spin.setMinimumHeight(38)
        form.addWidget(self.credit_spin, row, 1)
        row += 1
        
        layout.addLayout(form)
        
        # توضیحات
        layout.addWidget(QLabel("یادداشت:"))
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(70)
        self.notes_text.setMinimumHeight(60)
        self.notes_text.setPlaceholderText("یادداشت‌های مربوط به مشتری...")
        layout.addWidget(self.notes_text)
        
        # دکمه‌ها
        btn = QHBoxLayout()
        btn.setSpacing(10)
        
        save_btn = QPushButton("💾 ذخیره")
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_customer)
        btn.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        btn.addWidget(cancel_btn)
        
        layout.addLayout(btn)
    
    def load_customer(self):
        self.db.cursor.execute('SELECT * FROM customers WHERE id=?', (self.customer_id,))
        c = self.db.cursor.fetchone()
        if c:
            self.code_input.setText(c[1] or '')
            self.first_name_input.setText(c[2] or '')
            self.last_name_input.setText(c[3] or '')
            self.mobile_input.setText(c[4] or '')
            self.phone_input.setText(c[5] or '')
            self.address_input.setText(c[6] or '')
            self.shaba_input.setText(c[7] or '')
            self.account_input.setText(c[8] or '')
            self.debt_spin.setText(f"{c[9] or 0:,.0f}")
            self.credit_spin.setText(f"{c[10] or 0:,.0f}")
            self.notes_text.setText(c[11] or '')
    
    def save_customer(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        
        if not first_name or not last_name:
            QMessageBox.warning(self, "خطا", "نام و نام خانوادگی الزامی است")
            return
        
        # اعتبارسنجی موبایل
        mobile = self.mobile_input.text().strip()
        if mobile and (not mobile.startswith('09') or len(mobile) != 11 or not mobile.isdigit()):
            QMessageBox.warning(self, "خطا", "شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود")
            return
        
        try:
            data = (
                self.code_input.text().strip() or None,
                first_name,
                last_name,
                self.mobile_input.text().strip() or None,
                self.phone_input.text().strip() or None,
                self.address_input.toPlainText().strip() or None,
                self.shaba_input.text().strip() or None,
                self.account_input.text().strip() or None,
                self.notes_text.toPlainText().strip() or None
            )
            
            if self.customer_id:
                self.db.cursor.execute('''
                    UPDATE customers SET code=?, first_name=?, last_name=?, mobile=?, phone=?, 
                        address=?, shaba=?, account_number=?, notes=? WHERE id=?
                ''', (*data, self.customer_id))
            else:
                self.db.cursor.execute('''
                    INSERT INTO customers (code, first_name, last_name, mobile, phone, 
                                          address, shaba, account_number, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
            
            self.db.conn.commit()
            QMessageBox.information(self, "موفق", "✅ ذخیره شد")
            self.accept()
        except Exception as e:
            self.db.conn.rollback()
            if 'UNIQUE' in str(e):
                QMessageBox.critical(self, "خطا", "این کد مشتری قبلاً ثبت شده است")
            else:
                QMessageBox.critical(self, "خطا", f"خطا: {e}")


class CustomersPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # هدر
        h = QHBoxLayout()
        title = QLabel("👥 مدیریت مشتریان")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        h.addWidget(title)
        h.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 جستجو...")
        self.search_input.setMinimumHeight(38)
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self.filter_customers)
        h.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ مشتری جدید")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.add_customer)
        h.addWidget(add_btn)
        
        layout.addLayout(h)
        
        # جدول
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "کد", "نام", "نام خانوادگی", "موبایل", "تلفن", 
            "آدرس", "بدهی", "بستانکاری", "عملیات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_customer)
        layout.addWidget(self.table)
    
    def load_customers(self):
        self.db.cursor.execute('SELECT * FROM customers ORDER BY created_at DESC')
        self.all_customers = self.db.cursor.fetchall()
        self.display(self.all_customers)
    
    def display(self, customers):
        self.table.setRowCount(len(customers))
        for i, c in enumerate(customers):
            self.table.setRowHeight(i, 50)
            self.table.setItem(i, 0, QTableWidgetItem(str(c[1] or '')))
            self.table.setItem(i, 1, QTableWidgetItem(c[2]))
            self.table.setItem(i, 2, QTableWidgetItem(c[3]))
            self.table.setItem(i, 3, QTableWidgetItem(c[4] or ''))
            self.table.setItem(i, 4, QTableWidgetItem(c[5] or ''))
            self.table.setItem(i, 5, QTableWidgetItem(c[6] or ''))
            
            debt = QTableWidgetItem(f"{c[9] or 0:,.0f}")
            if c[9] and c[9] > 0:
                debt.setForeground(QBrush(QColor("#E17055")))
            self.table.setItem(i, 6, debt)
            
            credit = QTableWidgetItem(f"{c[10] or 0:,.0f}")
            if c[10] and c[10] > 0:
                credit.setForeground(QBrush(QColor("#00B894")))
            self.table.setItem(i, 7, credit)
            
            # دکمه‌ها
            w = QWidget()
            l = QHBoxLayout(w)
            l.setSpacing(5)
            l.setContentsMargins(5, 5, 5, 5)
            
            e = QPushButton("✏️")
            e.setMaximumWidth(40)
            e.setMinimumHeight(36)
            e.clicked.connect(lambda checked, cid=c[0]: self.edit_customer_by_id(cid))
            l.addWidget(e)
            
            d = QPushButton("🗑️")
            d.setMaximumWidth(40)
            d.setMinimumHeight(36)
            d.setObjectName("dangerBtn")
            d.clicked.connect(lambda checked, cid=c[0]: self.delete_customer(cid))
            l.addWidget(d)
            
            self.table.setCellWidget(i, 8, w)
    
    def add_customer(self):
        d = CustomerDetailDialog(self.db, parent=self)
        if d.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def edit_customer(self):
        row = self.table.currentRow()
        if row >= 0:
            self.edit_customer_by_id(self.all_customers[row][0])
    
    def edit_customer_by_id(self, cid):
        d = CustomerDetailDialog(self.db, cid, parent=self)
        if d.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def delete_customer(self, cid):
        if QMessageBox.question(self, "حذف", "مطمئنی؟") == QMessageBox.StandardButton.Yes:
            self.db.cursor.execute('DELETE FROM customers WHERE id=?', (cid,))
            self.db.conn.commit()
            self.load_customers()
    
    def filter_customers(self):
        s = self.search_input.text().strip().lower()
        if not s:
            self.display(self.all_customers)
            return
        filtered = [c for c in self.all_customers if 
                   s in str(c[1] or '').lower() or
                   s in str(c[2]).lower() or
                   s in str(c[3]).lower() or
                   s in str(c[4] or '')]
        self.display(filtered)