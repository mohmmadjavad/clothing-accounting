from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QGridLayout, QSpinBox, QDoubleSpinBox, QTextEdit,
    QGroupBox, QScrollArea, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QBrush
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date, get_current_shamsi_datetime
import jdatetime

class CuttingDetailDialog(QDialog):
    """دیالوگ ثبت برش جدید"""
    def __init__(self, db, record_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.record_id = record_id
        self.cutting_items = []
        
        self.setWindowTitle("ثبت برش جدید")
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(ModernStyle.get_main_stylesheet())
        self.init_ui()
        
        if record_id:
            self.load_record()
        else:
            self.generate_record_number()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # فرم اطلاعات اصلی
        form_group = QGroupBox("📋 اطلاعات برش")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # شماره برش
        form_layout.addWidget(QLabel("شماره برش:"), 0, 0)
        self.record_number = QLineEdit()
        self.record_number.setReadOnly(True)
        self.record_number.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(self.record_number, 0, 1)
        
        # تاریخ
        form_layout.addWidget(QLabel("تاریخ:"), 0, 2)
        self.date_input = QLineEdit()
        self.date_input.setText(get_current_shamsi_date())
        form_layout.addWidget(self.date_input, 0, 3)
        
        # ساعت
        form_layout.addWidget(QLabel("ساعت:"), 0, 4)
        self.time_input = QLineEdit()
        self.time_input.setText(jdatetime.datetime.now().strftime('%H:%M'))
        form_layout.addWidget(self.time_input, 0, 5)
        
        # اسم برشکار
        form_layout.addWidget(QLabel("اسم برشکار:*"), 1, 0)
        self.cutter_name = QLineEdit()
        self.cutter_name.setPlaceholderText("نام و نام خانوادگی برشکار")
        form_layout.addWidget(self.cutter_name, 1, 1)
        
        # نام مشتری
        form_layout.addWidget(QLabel("نام مشتری:*"), 1, 2)
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("نام مشتری یا سفارش‌دهنده")
        form_layout.addWidget(self.customer_name, 1, 3)
        
        # نام مدل
        form_layout.addWidget(QLabel("نام مدل:*"), 1, 4)
        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText("مدل لباس")
        form_layout.addWidget(self.model_name, 1, 5)
        
        # نوع پارچه
        form_layout.addWidget(QLabel("نوع پارچه:*"), 2, 0)
        self.fabric_type = QLineEdit()
        self.fabric_type.setPlaceholderText("مثلاً: نخ پنبه، جین، کتان")
        form_layout.addWidget(self.fabric_type, 2, 1)
        
        # وزن کل
        form_layout.addWidget(QLabel("وزن کل (kg):"), 2, 2)
        self.total_weight = QDoubleSpinBox()
        self.total_weight.setMaximum(99999)
        self.total_weight.setDecimals(2)
        self.total_weight.setSuffix(" kg")
        form_layout.addWidget(self.total_weight, 2, 3)
        
        # تعداد کل قد
        form_layout.addWidget(QLabel("تعداد کل قد:"), 2, 4)
        self.total_length = QSpinBox()
        self.total_length.setMaximum(99999)
        form_layout.addWidget(self.total_length, 2, 5)
        
        # تعداد کل کار
        form_layout.addWidget(QLabel("تعداد کل کار (تعداد لباس):"), 3, 0)
        self.total_units = QSpinBox()
        self.total_units.setMaximum(999999)
        form_layout.addWidget(self.total_units, 3, 1)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # بخش آیتم‌های برش
        items_group = QGroupBox("✂️ جزئیات برش (رنگ‌ها)")
        items_layout = QVBoxLayout()
        
        # فرم افزودن آیتم
        add_item_layout = QHBoxLayout()
        add_item_layout.setSpacing(8)
        
        add_item_layout.addWidget(QLabel("رنگ:"))
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("مثلاً: مشکی")
        self.color_input.setMaximumWidth(100)
        add_item_layout.addWidget(self.color_input)
        
        add_item_layout.addWidget(QLabel("وزن طاقه:"))
        self.roll_weight = QDoubleSpinBox()
        self.roll_weight.setMaximum(99999)
        self.roll_weight.setDecimals(2)
        self.roll_weight.setSuffix(" kg")
        self.roll_weight.setMaximumWidth(120)
        add_item_layout.addWidget(self.roll_weight)
        
        add_item_layout.addWidget(QLabel("تعداد قد:"))
        self.length_spin = QSpinBox()
        self.length_spin.setMaximum(99999)
        self.length_spin.setMaximumWidth(80)
        add_item_layout.addWidget(self.length_spin)
        
        add_item_layout.addWidget(QLabel("تعداد کار:"))
        self.units_spin = QSpinBox()
        self.units_spin.setMaximum(999999)
        self.units_spin.setMaximumWidth(80)
        add_item_layout.addWidget(self.units_spin)
        
        add_item_layout.addWidget(QLabel("توضیحات:"))
        self.item_notes = QLineEdit()
        self.item_notes.setPlaceholderText("توضیحات اضافه")
        self.item_notes.setMaximumWidth(120)
        add_item_layout.addWidget(self.item_notes)
        
        add_item_btn = QPushButton("➕ افزودن")
        add_item_btn.setMaximumWidth(100)
        add_item_btn.clicked.connect(self.add_item)
        add_item_layout.addWidget(add_item_btn)
        
        add_item_layout.addStretch()
        items_layout.addLayout(add_item_layout)
        
        # جدول آیتم‌های برش
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            "رنگ", "وزن طاقه (kg)", "تعداد قد", 
            "تعداد کار", "توضیحات", "حذف"
        ])
        
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.items_table.setColumnWidth(5, 60)
        self.items_table.verticalHeader().setDefaultSectionSize(55)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setMinimumHeight(250)
        self.items_table.setMaximumHeight(400)
        self.items_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.items_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        items_layout.addWidget(self.items_table)
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # توضیحات کل
        layout.addWidget(QLabel("توضیحات کلی:"))
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(60)
        self.notes_text.setPlaceholderText("یادداشت‌های مربوط به این برش...")
        layout.addWidget(self.notes_text)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 ذخیره برش")
        save_btn.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_record)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def add_item(self):
        color = self.color_input.text().strip()
        
        if not color:
            QMessageBox.warning(self, "خطا", "نام رنگ را وارد کنید")
            return
        
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setRowHeight(row, 55)
        
        color_item = QTableWidgetItem(color)
        color_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 0, color_item)
        
        weight_item = QTableWidgetItem(f"{self.roll_weight.value():.2f}")
        weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 1, weight_item)
        
        length_item = QTableWidgetItem(str(self.length_spin.value()))
        length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 2, length_item)
        
        units_item = QTableWidgetItem(str(self.units_spin.value()))
        units_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 3, units_item)
        
        notes_item = QTableWidgetItem(self.item_notes.text())
        self.items_table.setItem(row, 4, notes_item)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMaximumWidth(50)
        delete_btn.setMinimumHeight(45)
        delete_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
        self.items_table.setCellWidget(row, 5, delete_btn)
        
        self.cutting_items.append({
            'color': color,
            'roll_weight': self.roll_weight.value(),
            'length': self.length_spin.value(),
            'units': self.units_spin.value(),
            'notes': self.item_notes.text()
        })
        
        self.update_totals()
        self.items_table.scrollToBottom()
        
        self.color_input.clear()
        self.roll_weight.setValue(0)
        self.length_spin.setValue(0)
        self.units_spin.setValue(0)
        self.item_notes.clear()
        self.color_input.setFocus()
    
    def remove_item(self, row):
        self.items_table.removeRow(row)
        if row < len(self.cutting_items):
            del self.cutting_items[row]
        self.update_totals()
    
    def update_totals(self):
        total_weight = sum(item['roll_weight'] for item in self.cutting_items)
        total_length = sum(item['length'] for item in self.cutting_items)
        total_units = sum(item['units'] for item in self.cutting_items)
        
        self.total_weight.setValue(total_weight)
        self.total_length.setValue(total_length)
        self.total_units.setValue(total_units)
    
    def generate_record_number(self):
        self.db.cursor.execute('SELECT COUNT(*) FROM cutting_records')
        count = self.db.cursor.fetchone()[0] + 1
        date = jdatetime.datetime.now().strftime('%Y%m%d')
        self.record_number.setText(f"BR-{date}-{count:04d}")
    
    def save_record(self):
        cutter_name = self.cutter_name.text().strip()
        customer_name = self.customer_name.text().strip()
        model_name = self.model_name.text().strip()
        fabric_type = self.fabric_type.text().strip()
        
        if not all([cutter_name, customer_name, model_name, fabric_type]):
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدهای الزامی را پر کنید")
            return
        
        if not self.cutting_items:
            QMessageBox.warning(self, "خطا", "حداقل یک آیتم (رنگ) به برش اضافه کنید")
            return
        
        try:
            record_number = self.record_number.text()
            date_shamsi = self.date_input.text()
            total_weight = self.total_weight.value()
            total_length = self.total_length.value()
            total_units = self.total_units.value()
            notes = self.notes_text.toPlainText().strip()
            
            if self.record_id:
                self.db.cursor.execute('DELETE FROM cutting_items WHERE record_id=?', (self.record_id,))
                self.db.cursor.execute('DELETE FROM cutting_records WHERE id=?', (self.record_id,))
            
            self.db.cursor.execute('''
                INSERT INTO cutting_records (record_number, cutter_name, customer_name, 
                                            model_name, fabric_type, total_weight, 
                                            total_length, total_units, record_date, 
                                            record_date_shamsi, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)
            ''', (record_number, cutter_name, customer_name, model_name, 
                 fabric_type, total_weight, total_length, total_units, 
                 date_shamsi, notes))
            
            record_id = self.db.cursor.lastrowid
            
            for item in self.cutting_items:
                self.db.cursor.execute('''
                    INSERT INTO cutting_items (record_id, color, roll_weight, length, units, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (record_id, item['color'], item['roll_weight'], 
                     item['length'], item['units'], item['notes']))
            
            self.db.conn.commit()
            QMessageBox.information(self, "موفق", "✅ برش با موفقیت ثبت شد")
            self.accept()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "خطا", f"خطا در ثبت برش: {e}")
    
    def load_record(self):
        self.db.cursor.execute('SELECT * FROM cutting_records WHERE id=?', (self.record_id,))
        record = self.db.cursor.fetchone()
        
        if record:
            _, rec_num, cutter, customer, model, fabric, weight, length, units, _, date_shamsi, notes, _ = record
            
            self.record_number.setText(rec_num)
            self.cutter_name.setText(cutter)
            self.customer_name.setText(customer)
            self.model_name.setText(model)
            self.fabric_type.setText(fabric)
            self.total_weight.setValue(float(weight or 0))
            self.total_length.setValue(int(length or 0))
            self.total_units.setValue(int(units or 0))
            self.date_input.setText(date_shamsi or '')
            self.notes_text.setText(notes or '')
            
            self.db.cursor.execute('SELECT * FROM cutting_items WHERE record_id=?', (self.record_id,))
            items = self.db.cursor.fetchall()
            
            self.items_table.setRowCount(0)
            self.cutting_items = []
            
            for item in items:
                _, _, color, roll_weight, length_val, units_val, item_notes = item
                
                row = self.items_table.rowCount()
                self.items_table.insertRow(row)
                self.items_table.setRowHeight(row, 55)
                
                color_item = QTableWidgetItem(color)
                color_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 0, color_item)
                
                weight_item = QTableWidgetItem(f"{float(roll_weight or 0):.2f}")
                weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 1, weight_item)
                
                length_item = QTableWidgetItem(str(int(length_val or 0)))
                length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 2, length_item)
                
                units_item = QTableWidgetItem(str(int(units_val or 0)))
                units_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(row, 3, units_item)
                
                self.items_table.setItem(row, 4, QTableWidgetItem(str(item_notes or '')))
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("dangerBtn")
                delete_btn.setMinimumHeight(45)
                delete_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
                self.items_table.setCellWidget(row, 5, delete_btn)
                
                self.cutting_items.append({
                    'color': color,
                    'roll_weight': float(roll_weight or 0),
                    'length': int(length_val or 0),
                    'units': int(units_val or 0),
                    'notes': str(item_notes or '')
                })


class CuttingPage(QWidget):
    """صفحه دفتر برش"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_records()
        self.load_statistics()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("✂️ دفتر برش")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ برش جدید")
        add_btn.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        add_btn.clicked.connect(self.add_record)
        header_layout.addWidget(add_btn)
        
        main_layout.addLayout(header_layout)
        
        # بخش آمار
        stats_group = QGroupBox("📊 آمار برش")
        stats_layout = QHBoxLayout()
        
        stats_layout.addWidget(QLabel("از تاریخ:"))
        self.date_from = QLineEdit()
        self.date_from.setMaximumWidth(120)
        self.date_from.setText(jdatetime.date.today().replace(day=1).strftime('%Y/%m/%d'))
        stats_layout.addWidget(self.date_from)
        
        stats_layout.addWidget(QLabel("تا تاریخ:"))
        self.date_to = QLineEdit()
        self.date_to.setMaximumWidth(120)
        self.date_to.setText(get_current_shamsi_date())
        stats_layout.addWidget(self.date_to)
        
        stats_layout.addWidget(QLabel("مشتری:"))
        self.customer_stats_filter = QLineEdit()
        self.customer_stats_filter.setMaximumWidth(150)
        self.customer_stats_filter.setPlaceholderText("نام مشتری...")
        stats_layout.addWidget(self.customer_stats_filter)
        
        show_stats_btn = QPushButton("📊 نمایش آمار")
        show_stats_btn.clicked.connect(self.load_statistics)
        stats_layout.addWidget(show_stats_btn)
        
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # کارت‌های آمار
        stats_cards_layout = QHBoxLayout()
        
        self.total_records_card = self.create_stat_card("📋 کل برش‌ها", "0", ModernStyle.PRIMARY)
        stats_cards_layout.addWidget(self.total_records_card)
        
        self.total_units_card = self.create_stat_card("👕 کل تولید", "0", ModernStyle.SUCCESS)
        stats_cards_layout.addWidget(self.total_units_card)
        
        self.total_weight_card = self.create_stat_card("⚖️ وزن کل", "0 kg", ModernStyle.WARNING)
        stats_cards_layout.addWidget(self.total_weight_card)
        
        self.unique_customers_card = self.create_stat_card("👥 مشتریان", "0", ModernStyle.SECONDARY)
        stats_cards_layout.addWidget(self.unique_customers_card)
        
        main_layout.addLayout(stats_cards_layout)
        
        # فیلترهای جستجو
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("🔍 جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو در شماره برش، مشتری، مدل، پارچه...")
        self.search_input.setMaximumWidth(350)
        self.search_input.textChanged.connect(self.filter_records)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("برشکار:"))
        self.cutter_filter = QLineEdit()
        self.cutter_filter.setMaximumWidth(150)
        self.cutter_filter.textChanged.connect(self.filter_records)
        filter_layout.addWidget(self.cutter_filter)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # جدول اصلی
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(11)
        self.records_table.setHorizontalHeaderLabels([
            "شماره برش", "تاریخ", "برشکار", "مشتری", 
            "مدل", "پارچه", "وزن کل", "قد کل",
            "تعداد کار", "توضیحات", "عملیات"
        ])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.records_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.records_table.verticalHeader().setDefaultSectionSize(50)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.doubleClicked.connect(self.edit_record)
        main_layout.addWidget(self.records_table)
    
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setObjectName("card")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Tahoma", 15, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; background: transparent;")
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)
        
        return card
    
    def load_records(self):
        query = 'SELECT * FROM cutting_records ORDER BY created_at DESC'
        self.db.cursor.execute(query)
        records = self.db.cursor.fetchall()
        self.all_records = records
        self.display_records(records)
    
    def display_records(self, records):
        self.records_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            rec_id, rec_num, cutter, customer, model, fabric, weight, length, units, _, date_shamsi, notes, _ = record
            
            self.records_table.setRowHeight(row, 50)
            
            self.records_table.setItem(row, 0, QTableWidgetItem(rec_num))
            self.records_table.setItem(row, 1, QTableWidgetItem(date_shamsi or ''))
            self.records_table.setItem(row, 2, QTableWidgetItem(cutter))
            self.records_table.setItem(row, 3, QTableWidgetItem(customer))
            self.records_table.setItem(row, 4, QTableWidgetItem(model))
            self.records_table.setItem(row, 5, QTableWidgetItem(fabric))
            self.records_table.setItem(row, 6, QTableWidgetItem(f"{float(weight or 0):.2f}"))
            self.records_table.setItem(row, 7, QTableWidgetItem(str(int(length or 0))))
            self.records_table.setItem(row, 8, QTableWidgetItem(str(int(units or 0))))
            self.records_table.setItem(row, 9, QTableWidgetItem(str(notes or '')))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(45)
            edit_btn.setMinimumHeight(40)
            edit_btn.clicked.connect(lambda checked, rid=rec_id: self.edit_record_by_id(rid))
            actions_layout.addWidget(edit_btn)
            
            details_btn = QPushButton("🔍")
            details_btn.setMaximumWidth(45)
            details_btn.setMinimumHeight(40)
            details_btn.setToolTip("مشاهده جزئیات")
            details_btn.clicked.connect(lambda checked, rid=rec_id: self.view_record_details(rid))
            actions_layout.addWidget(details_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(45)
            delete_btn.setMinimumHeight(40)
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(lambda checked, rid=rec_id: self.delete_record(rid))
            actions_layout.addWidget(delete_btn)
            
            self.records_table.setCellWidget(row, 10, actions_widget)
    
    def load_statistics(self):
        date_from = self.date_from.text()
        date_to = self.date_to.text()
        customer_filter = self.customer_stats_filter.text().strip()
        
        where_clauses = []
        params = []
        
        if date_from and date_to:
            where_clauses.append("record_date_shamsi BETWEEN ? AND ?")
            params.extend([date_from, date_to])
        
        if customer_filter:
            where_clauses.append("customer_name LIKE ?")
            params.append(f"%{customer_filter}%")
        
        where = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f'''
            SELECT 
                COUNT(*) as total_records,
                COALESCE(SUM(total_units), 0) as total_units,
                COALESCE(SUM(total_weight), 0) as total_weight,
                COUNT(DISTINCT customer_name) as unique_customers
            FROM cutting_records
            {where}
        '''
        
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchone()
        
        if result:
            total_records, total_units, total_weight, unique_customers = result
            
            self.total_records_card.findChild(QLabel, "stat_value").setText(str(total_records))
            self.total_units_card.findChild(QLabel, "stat_value").setText(f"{total_units:,}")
            self.total_weight_card.findChild(QLabel, "stat_value").setText(f"{total_weight:,.2f} kg")
            self.unique_customers_card.findChild(QLabel, "stat_value").setText(str(unique_customers))
    
    def add_record(self):
        dialog = CuttingDetailDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_records()
            self.load_statistics()
            self.db.data_changed.emit()
    
    def edit_record(self):
        current_row = self.records_table.currentRow()
        if current_row >= 0:
            record_id = self.all_records[current_row][0]
            self.edit_record_by_id(record_id)
    
    def edit_record_by_id(self, record_id):
        dialog = CuttingDetailDialog(self.db, record_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_records()
            self.load_statistics()
            self.db.data_changed.emit()
    
    def view_record_details(self, record_id):
        self.db.cursor.execute('''
            SELECT cr.*, GROUP_CONCAT(ci.color || ': ' || ci.units || ' عدد', ' | ')
            FROM cutting_records cr
            LEFT JOIN cutting_items ci ON cr.id = ci.record_id
            WHERE cr.id = ?
            GROUP BY cr.id
        ''', (record_id,))
        
        record = self.db.cursor.fetchone()
        if record:
            details = f"""
            📋 شماره برش: {record[1]}
            📅 تاریخ: {record[9] or '---'}
            👤 برشکار: {record[2]}
            👥 مشتری: {record[3]}
            📦 مدل: {record[4]}
            🧵 پارچه: {record[5]}
            ⚖️ وزن کل: {record[6]:.2f} kg
            📏 تعداد قد: {record[7]}
            👕 تعداد کار: {record[8]}
            
            🎨 جزئیات رنگ‌ها:
            {record[12] or 'اطلاعاتی موجود نیست'}
            
            📝 توضیحات: {record[10] or '---'}
            """
            
            msg = QMessageBox()
            msg.setWindowTitle("جزئیات برش")
            msg.setText(details)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
    
    def delete_record(self, record_id):
        reply = QMessageBox.question(
            self, "حذف برش",
            "آیا از حذف این رکورد برش اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute('DELETE FROM cutting_records WHERE id=?', (record_id,))
                self.db.conn.commit()
                self.load_records()
                self.load_statistics()
                self.db.data_changed.emit()
                QMessageBox.information(self, "موفق", "رکورد برش با موفقیت حذف شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا: {e}")
    
    def filter_records(self):
        search = self.search_input.text().strip()
        cutter = self.cutter_filter.text().strip()
        
        filtered = self.all_records.copy()
        
        if search:
            filtered = [r for r in filtered if 
                       search.lower() in str(r[1] or '').lower() or
                       search.lower() in str(r[3] or '').lower() or
                       search.lower() in str(r[4] or '').lower() or
                       search.lower() in str(r[5] or '').lower()]
        
        if cutter:
            filtered = [r for r in filtered if cutter.lower() in str(r[2] or '').lower()]
        
        self.display_records(filtered)