from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QGridLayout, QSpinBox, QDoubleSpinBox, QTextEdit,
    QDateEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QBrush
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date, get_current_shamsi_datetime
import jdatetime

class TransactionDialog(QDialog):
    """دیالوگ ثبت تراکنش مالی"""
    def __init__(self, db, transaction_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.transaction_id = transaction_id
        
        self.setWindowTitle("ثبت تراکنش مالی")
        self.setMinimumSize(650, 500)
        self.setStyleSheet(ModernStyle.get_main_stylesheet())
        self.init_ui()
        
        if transaction_id:
            self.load_transaction()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # فرم تراکنش
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        # نوع تراکنش
        form_layout.addWidget(QLabel("نوع تراکنش:*"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["دریافت (بستانکاری)", "پرداخت (بدهکاری)", "تسویه حساب"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addWidget(self.type_combo, 0, 1)
        
        # مشتری
        form_layout.addWidget(QLabel("مشتری:*"), 1, 0)
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumWidth(250)
        self.load_customers()
        self.customer_combo.currentIndexChanged.connect(self.customer_selected)
        form_layout.addWidget(self.customer_combo, 1, 1)
        
        # نمایش مانده حساب مشتری
        self.balance_label = QLabel("")
        self.balance_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 11px;")
        form_layout.addWidget(self.balance_label, 2, 0, 1, 2)
        
        # مبلغ
        form_layout.addWidget(QLabel("مبلغ (تومان):*"), 3, 0)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMaximum(999999999)
        self.amount_spin.setMinimum(1)
        self.amount_spin.setValue(0)
        self.amount_spin.setSuffix(" تومان")
        self.amount_spin.valueChanged.connect(self.update_final_amount)
        form_layout.addWidget(self.amount_spin, 3, 1)
        
        # تخفیف/کارمزد
        form_layout.addWidget(QLabel("کارمزد/تخفیف:"), 4, 0)
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setMaximum(999999999)
        self.fee_spin.setSuffix(" تومان")
        self.fee_spin.valueChanged.connect(self.update_final_amount)
        form_layout.addWidget(self.fee_spin, 4, 1)
        
        # مبلغ نهایی
        form_layout.addWidget(QLabel("مبلغ نهایی:"), 5, 0)
        self.final_amount_label = QLabel("0 تومان")
        self.final_amount_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        self.final_amount_label.setStyleSheet(f"color: {ModernStyle.PRIMARY};")
        form_layout.addWidget(self.final_amount_label, 5, 1)
        
        # تاریخ
        form_layout.addWidget(QLabel("تاریخ:"), 6, 0)
        self.date_input = QLineEdit()
        self.date_input.setText(get_current_shamsi_date())
        form_layout.addWidget(self.date_input, 6, 1)
        
        # شماره حساب
        form_layout.addWidget(QLabel("شماره حساب:"), 7, 0)
        self.account_combo = QComboBox()
        self.account_combo.setEditable(True)
        self.load_accounts()
        form_layout.addWidget(self.account_combo, 7, 1)
        
        # شماره مرجع
        form_layout.addWidget(QLabel("شماره پیگیری/مرجع:"), 8, 0)
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("شماره پیگیری یا رسید")
        form_layout.addWidget(self.reference_input, 8, 1)
        
        layout.addLayout(form_layout)
        
        # توضیحات
        layout.addWidget(QLabel("توضیحات:"))
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(80)
        self.description_text.setPlaceholderText("شرح تراکنش...")
        layout.addWidget(self.description_text)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 ثبت تراکنش")
        save_btn.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        save_btn.clicked.connect(self.save_transaction)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def load_customers(self):
        self.db.cursor.execute('SELECT id, first_name || " " || last_name, mobile FROM customers ORDER BY first_name')
        customers = self.db.cursor.fetchall()
        self.customer_combo.addItem("انتخاب کنید...", None)
        for cust_id, name, mobile in customers:
            self.customer_combo.addItem(f"{name} - {mobile or 'بدون شماره'}", cust_id)
    
    def load_accounts(self):
        # بارگذاری حساب‌های ثبت شده در تنظیمات
        main_account = self.db.get_setting('account_number')
        if main_account:
            self.account_combo.addItem(f"🏦 اصلی: {main_account}")
        
        holder = self.db.get_setting('account_holder')
        if holder:
            self.account_combo.addItem(f"👤 {holder}")
    
    def customer_selected(self):
        customer_id = self.customer_combo.currentData()
        if customer_id:
            self.db.cursor.execute('SELECT debt, credit FROM customers WHERE id=?', (customer_id,))
            result = self.db.cursor.fetchone()
            if result:
                debt, credit = result
                balance = (credit or 0) - (debt or 0)
                color = ModernStyle.SUCCESS if balance >= 0 else ModernStyle.DANGER
                self.balance_label.setText(f"💰 مانده حساب: {balance:,.0f} تومان | بدهی: {debt or 0:,.0f} | بستانکاری: {credit or 0:,.0f}")
                self.balance_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def on_type_changed(self, text):
        if text == "پرداخت (بدهکاری)":
            self.amount_spin.setStyleSheet(f"color: {ModernStyle.DANGER};")
        elif text == "دریافت (بستانکاری)":
            self.amount_spin.setStyleSheet(f"color: {ModernStyle.SUCCESS};")
    
    def update_final_amount(self):
        amount = self.amount_spin.value()
        fee = self.fee_spin.value()
        final = amount - fee
        self.final_amount_label.setText(f"{max(0, final):,.0f} تومان")
    
    def save_transaction(self):
        customer_id = self.customer_combo.currentData()
        
        if not customer_id:
            QMessageBox.warning(self, "خطا", "لطفاً مشتری را انتخاب کنید")
            return
        
        amount = self.amount_spin.value()
        if amount <= 0:
            QMessageBox.warning(self, "خطا", "مبلغ باید بیشتر از صفر باشد")
            return
        
        try:
            trans_type = self.type_combo.currentText()
            fee = self.fee_spin.value()
            final_amount = max(0, amount - fee)
            date_shamsi = self.date_input.text()
            account = self.account_combo.currentText()
            reference = self.reference_input.text().strip() or None
            description = self.description_text.toPlainText().strip() or None
            
            if self.transaction_id:
                # برگرداندن تراکنش قبلی
                self.db.cursor.execute('SELECT customer_id, transaction_type, amount FROM transactions WHERE id=?', 
                                      (self.transaction_id,))
                old_trans = self.db.cursor.fetchone()
                if old_trans:
                    old_cust_id, old_type, old_amount = old_trans
                    if "بستانکاری" in old_type:
                        self.db.cursor.execute('UPDATE customers SET credit = credit - ? WHERE id=?', 
                                              (old_amount, old_cust_id))
                    elif "بدهکاری" in old_type:
                        self.db.cursor.execute('UPDATE customers SET debt = debt - ? WHERE id=?', 
                                              (old_amount, old_cust_id))
                
                self.db.cursor.execute('''
                    UPDATE transactions 
                    SET customer_id=?, transaction_type=?, amount=?, description=?, 
                        reference_number=?, account_number=?, transaction_date_shamsi=?
                    WHERE id=?
                ''', (customer_id, trans_type, final_amount, description, 
                     reference, account, date_shamsi, self.transaction_id))
            else:
                self.db.cursor.execute('''
                    INSERT INTO transactions (customer_id, transaction_type, amount, description, 
                                             reference_number, account_number, transaction_date, 
                                             transaction_date_shamsi)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
                ''', (customer_id, trans_type, final_amount, description, 
                     reference, account, date_shamsi))
            
            # به‌روزرسانی حساب مشتری
            if "بستانکاری" in trans_type:
                # دریافت: مشتری پول داده، بدهی کاهش می‌یابد
                self.db.cursor.execute('''
                    UPDATE customers SET
                        debt = MAX(0, debt - ?),
                        credit = credit + MAX(0, ? - debt)
                    WHERE id=?
                ''', (final_amount, final_amount, customer_id))
            elif "بدهکاری" in trans_type:
                # پرداخت به مشتری: بستانکاری کاهش یا بدهی افزایش
                self.db.cursor.execute('''
                    UPDATE customers SET
                        credit = MAX(0, credit - ?),
                        debt = debt + MAX(0, ? - credit)
                    WHERE id=?
                ''', (final_amount, final_amount, customer_id))
            elif "تسویه" in trans_type:
                # تسویه کامل حساب
                self.db.cursor.execute('''
                    UPDATE customers SET debt = 0, credit = 0 WHERE id=?
                ''', (customer_id,))
            
            # به‌روزرسانی وضعیت پرداخت سفارشات
            self.db.cursor.execute('''
                UPDATE orders SET payment_status = 'paid' 
                WHERE customer_id=? AND payment_status='unpaid' AND final_amount <= (
                    SELECT COALESCE(credit, 0) - COALESCE(debt, 0) FROM customers WHERE id=?
                )
            ''', (customer_id, customer_id))
            
            self.db.conn.commit()
            QMessageBox.information(self, "موفق", "✅ تراکنش با موفقیت ثبت شد")
            self.accept()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "خطا", f"خطا در ثبت تراکنش: {e}")
    
    def load_transaction(self):
        self.db.cursor.execute('SELECT * FROM transactions WHERE id=?', (self.transaction_id,))
        trans = self.db.cursor.fetchone()
        
        if trans:
            _, cust_id, trans_type, amount, desc, ref, acc, _, date_shamsi, _ = trans
            
            # تنظیم نوع تراکنش
            index = self.type_combo.findText(trans_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            # تنظیم مشتری
            index = self.customer_combo.findData(cust_id)
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)
            
            self.amount_spin.setValue(amount)
            self.date_input.setText(date_shamsi or '')
            self.reference_input.setText(ref or '')
            self.description_text.setText(desc or '')
            
            if acc:
                self.account_combo.setCurrentText(acc)


class AccountingPage(QWidget):
    """صفحه مدیریت مالی و حسابداری"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_transactions()
        self.load_summary()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # هدر
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 مدیریت مالی و حسابداری")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ تراکنش جدید")
        add_btn.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        add_btn.clicked.connect(self.add_transaction)
        header_layout.addWidget(add_btn)
        
        main_layout.addLayout(header_layout)
        
        # کارت‌های خلاصه مالی
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # کارت کل دریافت‌ها
        self.total_credit_card = self.create_summary_card(
            "📥 کل دریافت‌ها", "0 تومان", ModernStyle.SUCCESS
        )
        summary_layout.addWidget(self.total_credit_card)
        
        # کارت کل پرداخت‌ها
        self.total_debit_card = self.create_summary_card(
            "📤 کل پرداخت‌ها", "0 تومان", ModernStyle.DANGER
        )
        summary_layout.addWidget(self.total_debit_card)
        
        # کارت مانده حساب
        self.balance_card = self.create_summary_card(
            "💎 مانده حساب", "0 تومان", ModernStyle.PRIMARY
        )
        summary_layout.addWidget(self.balance_card)
        
        # کارت بدهکاران
        self.debtors_card = self.create_summary_card(
            "👥 بدهکاران", "0 نفر", ModernStyle.WARNING
        )
        summary_layout.addWidget(self.debtors_card)
        
        main_layout.addLayout(summary_layout)
        
        # فیلترهای جستجو
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("🔍 جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو در نام مشتری، شماره مرجع، توضیحات...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("نوع:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["همه", "دریافت", "پرداخت", "تسویه"])
        self.type_filter.currentTextChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("مشتری:"))
        self.customer_filter = QComboBox()
        self.customer_filter.addItem("همه", None)
        self.load_customers_filter()
        self.customer_filter.currentIndexChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.customer_filter)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # جدول تراکنش‌ها
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(9)
        self.transactions_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع", "مشتری", "مبلغ (تومان)", 
            "شماره حساب", "شماره مرجع", "توضیحات", "زمان ثبت", "عملیات"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.doubleClicked.connect(self.edit_transaction)
        main_layout.addWidget(self.transactions_table)
        
        # جدول وضعیت مشتریان
        customers_group = QGroupBox("👥 وضعیت مالی مشتریان")
        customers_layout = QVBoxLayout()
        
        self.customers_summary_table = QTableWidget()
        self.customers_summary_table.setColumnCount(6)
        self.customers_summary_table.setHorizontalHeaderLabels([
            "مشتری", "موبایل", "بدهی (تومان)", 
            "بستانکاری (تومان)", "مانده", "عملیات"
        ])
        self.customers_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.customers_summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        customers_layout.addWidget(self.customers_summary_table)
        
        customers_group.setLayout(customers_layout)
        main_layout.addWidget(customers_group)
    
    def create_summary_card(self, title, value, color):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background: white;
                border-radius: 16px;
                border: 1px solid {ModernStyle.BORDER};
                padding: 15px;
            }}
            QFrame#card:hover {{
                border-color: {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        
        return card
    
    def load_customers_filter(self):
        self.db.cursor.execute('SELECT id, first_name || " " || last_name FROM customers ORDER BY first_name')
        for cust_id, name in self.db.cursor.fetchall():
            self.customer_filter.addItem(name, cust_id)
    
    def load_summary(self):
        # محاسبه خلاصه مالی
        self.db.cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN transaction_type LIKE "%بستانکاری%" THEN amount ELSE 0 END), 0) as total_credit,
                COALESCE(SUM(CASE WHEN transaction_type LIKE "%بدهکاری%" THEN amount ELSE 0 END), 0) as total_debit
            FROM transactions
        ''')
        total_credit, total_debit = self.db.cursor.fetchone()
        
        balance = total_credit - total_debit
        
        # به‌روزرسانی کارت‌ها
        self.total_credit_card.findChild(QLabel, "value_label").setText(f"{total_credit:,.0f} تومان")
        self.total_debit_card.findChild(QLabel, "value_label").setText(f"{total_debit:,.0f} تومان")
        self.balance_card.findChild(QLabel, "value_label").setText(f"{balance:,.0f} تومان")
        
        # تعداد بدهکاران
        self.db.cursor.execute('SELECT COUNT(*) FROM customers WHERE debt > credit')
        debtors = self.db.cursor.fetchone()[0]
        self.debtors_card.findChild(QLabel, "value_label").setText(f"{debtors} نفر")
        
        # بارگذاری جدول وضعیت مشتریان
        self.load_customers_summary()
    
    def load_customers_summary(self):
        self.db.cursor.execute('''
            SELECT first_name || " " || last_name, mobile, debt, credit, 
                   (COALESCE(credit, 0) - COALESCE(debt, 0)) as balance, id
            FROM customers
            ORDER BY balance ASC
        ''')
        customers = self.db.cursor.fetchall()
        
        self.customers_summary_table.setRowCount(len(customers))
        
        for row, (name, mobile, debt, credit, balance, cust_id) in enumerate(customers):
            self.customers_summary_table.setItem(row, 0, QTableWidgetItem(name))
            self.customers_summary_table.setItem(row, 1, QTableWidgetItem(mobile or ''))
            
            # بدهی
            debt_item = QTableWidgetItem(f"{debt or 0:,.0f}")
            if debt and debt > 0:
                debt_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
            self.customers_summary_table.setItem(row, 2, debt_item)
            
            # بستانکاری
            credit_item = QTableWidgetItem(f"{credit or 0:,.0f}")
            if credit and credit > 0:
                credit_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
            self.customers_summary_table.setItem(row, 3, credit_item)
            
            # مانده
            balance_item = QTableWidgetItem(f"{balance:,.0f}")
            if balance < 0:
                balance_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
                balance_item.setBackground(QBrush(QColor("#FFE0E0")))
            elif balance > 0:
                balance_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
                balance_item.setBackground(QBrush(QColor("#E8F5E9")))
            self.customers_summary_table.setItem(row, 4, balance_item)
            
            # دکمه عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            trans_btn = QPushButton("💳 تراکنش")
            trans_btn.setMaximumWidth(90)
            trans_btn.setStyleSheet(f"background: {ModernStyle.PRIMARY}; color: white; font-size: 10px;")
            trans_btn.clicked.connect(lambda checked, cid=cust_id: self.add_transaction_for_customer(cid))
            actions_layout.addWidget(trans_btn)
            
            self.customers_summary_table.setCellWidget(row, 5, actions_widget)
    
    def load_transactions(self):
        query = '''
            SELECT t.*, c.first_name || " " || c.last_name as customer_name
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            ORDER BY t.created_at DESC
        '''
        
        self.db.cursor.execute(query)
        transactions = self.db.cursor.fetchall()
        self.all_transactions = transactions
        self.display_transactions(transactions)
    
    def display_transactions(self, transactions):
        self.transactions_table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            trans_id, cust_id, trans_type, amount, desc, ref, acc, _, date_shamsi, _, cust_name = trans
            
            self.transactions_table.setItem(row, 0, QTableWidgetItem(date_shamsi or ''))
            
            # نوع تراکنش با رنگ
            type_item = QTableWidgetItem(trans_type)
            if "بستانکاری" in trans_type:
                type_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
                type_item.setBackground(QBrush(QColor("#E8F5E9")))
            elif "بدهکاری" in trans_type:
                type_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
                type_item.setBackground(QBrush(QColor("#FFE0E0")))
            self.transactions_table.setItem(row, 1, type_item)
            
            self.transactions_table.setItem(row, 2, QTableWidgetItem(cust_name))
            
            # مبلغ با رنگ
            amount_item = QTableWidgetItem(f"{amount:,.0f}")
            if "بستانکاری" in trans_type:
                amount_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
            else:
                amount_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
            self.transactions_table.setItem(row, 3, amount_item)
            
            self.transactions_table.setItem(row, 4, QTableWidgetItem(acc or ''))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(ref or ''))
            self.transactions_table.setItem(row, 6, QTableWidgetItem(desc or ''))
            self.transactions_table.setItem(row, 7, QTableWidgetItem(date_shamsi or ''))
            
            # دکمه‌ها
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, tid=trans_id: self.edit_transaction_by_id(tid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(lambda checked, tid=trans_id: self.delete_transaction(tid))
            actions_layout.addWidget(delete_btn)
            
            self.transactions_table.setCellWidget(row, 8, actions_widget)
    
    def add_transaction(self):
        dialog = TransactionDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_transactions()
            self.load_summary()
            self.db.data_changed.emit()
    
    def add_transaction_for_customer(self, customer_id):
        dialog = TransactionDialog(self.db, parent=self)
        # تنظیم مشتری
        index = dialog.customer_combo.findData(customer_id)
        if index >= 0:
            dialog.customer_combo.setCurrentIndex(index)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_transactions()
            self.load_summary()
            self.db.data_changed.emit()
    
    def edit_transaction(self):
        current_row = self.transactions_table.currentRow()
        if current_row >= 0:
            trans_id = self.all_transactions[current_row][0]
            self.edit_transaction_by_id(trans_id)
    
    def edit_transaction_by_id(self, trans_id):
        dialog = TransactionDialog(self.db, trans_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_transactions()
            self.load_summary()
            self.db.data_changed.emit()
    
    def delete_transaction(self, trans_id):
        reply = QMessageBox.question(
            self, "حذف تراکنش",
            "آیا از حذف این تراکنش اطمینان دارید؟\nتغییرات در حساب مشتری اعمال خواهد شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # برگرداندن مبلغ به حساب مشتری
                self.db.cursor.execute('SELECT customer_id, transaction_type, amount FROM transactions WHERE id=?', 
                                      (trans_id,))
                result = self.db.cursor.fetchone()
                if result:
                    cust_id, trans_type, amount = result
                    if "بستانکاری" in trans_type:
                        self.db.cursor.execute('UPDATE customers SET credit = credit - ? WHERE id=?', 
                                              (amount, cust_id))
                    elif "بدهکاری" in trans_type:
                        self.db.cursor.execute('UPDATE customers SET debt = debt - ? WHERE id=?', 
                                              (amount, cust_id))
                
                self.db.cursor.execute('DELETE FROM transactions WHERE id=?', (trans_id,))
                self.db.conn.commit()
                self.load_transactions()
                self.load_summary()
                self.db.data_changed.emit()
                QMessageBox.information(self, "موفق", "تراکنش با موفقیت حذف شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا: {e}")
    
    def filter_transactions(self):
        search = self.search_input.text().strip()
        trans_type = self.type_filter.currentText()
        customer_id = self.customer_filter.currentData()
        
        filtered = self.all_transactions.copy()
        
        if search:
            filtered = [t for t in filtered if 
                       search.lower() in str(t[11] or '').lower() or  # نام مشتری
                       search in str(t[6] or '') or  # شماره مرجع
                       search.lower() in str(t[4] or '').lower()]  # توضیحات
        
        if trans_type == "دریافت":
            filtered = [t for t in filtered if "بستانکاری" in t[2]]
        elif trans_type == "پرداخت":
            filtered = [t for t in filtered if "بدهکاری" in t[2]]
        elif trans_type == "تسویه":
            filtered = [t for t in filtered if "تسویه" in t[2]]
        
        if customer_id:
            filtered = [t for t in filtered if t[1] == customer_id]
        
        self.display_transactions(filtered)