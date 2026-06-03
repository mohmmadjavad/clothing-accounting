from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QSplitter, QStackedWidget,
    QSpinBox, QDoubleSpinBox, QTabWidget, QGridLayout,
    QScrollArea, QGroupBox, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor, QBrush
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date
import os
import io
from PIL import Image

class ProductDetailDialog(QDialog):
    """دیالوگ جزئیات کالا"""
    def __init__(self, db, product_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.image_data = None
        self.setWindowTitle("افزودن/ویرایش کالا")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(ModernStyle.get_main_stylesheet())
        self.init_ui()
        if product_id:
            self.load_product()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # تب‌ها
        tabs = QTabWidget()
        
        # تب اطلاعات پایه
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setSpacing(12)
        
        # فرم اطلاعات
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        # کد کالا
        form_layout.addWidget(QLabel("کد کالا:"), 0, 0)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("کد یکتا برای کالا")
        self.code_input.setMinimumHeight(38)
        form_layout.addWidget(self.code_input, 0, 1)
        
        # نام کالا
        form_layout.addWidget(QLabel("نام کالا:*"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثلاً: تیشرت یقه‌گرد ساده")
        self.name_input.setMinimumHeight(38)
        form_layout.addWidget(self.name_input, 1, 1)
        
        # دسته‌بندی
        form_layout.addWidget(QLabel("دسته‌بندی:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(38)
        self.load_categories()
        form_layout.addWidget(self.category_combo, 2, 1)
        
        # نوع پارچه
        form_layout.addWidget(QLabel("نوع پارچه:"), 3, 0)
        self.fabric_input = QLineEdit()
        self.fabric_input.setPlaceholderText("مثلاً: پنبه، نخ، جین")
        self.fabric_input.setMinimumHeight(38)
        form_layout.addWidget(self.fabric_input, 3, 1)
        
        # مدل
        form_layout.addWidget(QLabel("مدل:"), 4, 0)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("شماره یا نام مدل")
        self.model_input.setMinimumHeight(38)
        form_layout.addWidget(self.model_input, 4, 1)
        
        # حداقل موجودی هشدار
        form_layout.addWidget(QLabel("هشدار حداقل موجودی:"), 5, 0)
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setMinimum(0)
        self.min_stock_spin.setMaximum(9999)
        self.min_stock_spin.setValue(10)
        self.min_stock_spin.setMinimumHeight(38)
        form_layout.addWidget(self.min_stock_spin, 5, 1)
        
        # توضیحات
        form_layout.addWidget(QLabel("توضیحات:"), 6, 0)
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(90)
        self.description_text.setMinimumHeight(70)
        self.description_text.setPlaceholderText("توضیحات تکمیلی کالا...")
        form_layout.addWidget(self.description_text, 6, 1)
        
        basic_layout.addLayout(form_layout)
        
        # بخش عکس
        image_layout = QHBoxLayout()
        
        self.image_label = QLabel("🖼️ برای افزودن عکس کلیک کنید")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setMaximumSize(250, 250)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {ModernStyle.PRIMARY};
                border-radius: 16px;
                background-color: #F8F6FF;
                font-size: 13px;
                color: {ModernStyle.TEXT_SECONDARY};
            }}
            QLabel:hover {{
                border-color: {ModernStyle.PRIMARY_DARK};
                background-color: #F0EEFF;
            }}
        """)
        self.image_label.mousePressEvent = self.select_image
        image_layout.addWidget(self.image_label)
        
        # دکمه‌های عکس
        img_btn_layout = QVBoxLayout()
        
        select_img_btn = QPushButton("📁 انتخاب عکس")
        select_img_btn.setMinimumHeight(38)
        select_img_btn.clicked.connect(self.select_image)
        img_btn_layout.addWidget(select_img_btn)
        
        remove_img_btn = QPushButton("🗑️ حذف عکس")
        remove_img_btn.setObjectName("dangerBtn")
        remove_img_btn.setMinimumHeight(38)
        remove_img_btn.clicked.connect(self.remove_image)
        img_btn_layout.addWidget(remove_img_btn)
        
        img_btn_layout.addStretch()
        image_layout.addLayout(img_btn_layout)
        
        basic_layout.addLayout(image_layout)
        tabs.addTab(basic_tab, "📋 اطلاعات پایه")
        
        # تب تنوع (رنگ و سایز)
        variants_tab = QWidget()
        variants_layout = QVBoxLayout(variants_tab)
        variants_layout.setSpacing(10)
        
        # فرم افزودن تنوع
        add_variant_layout = QHBoxLayout()
        add_variant_layout.setSpacing(8)
        
        add_variant_layout.addWidget(QLabel("رنگ:"))
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("مثلاً: قرمز")
        self.color_input.setMinimumHeight(38)
        self.color_input.setMaximumWidth(100)
        add_variant_layout.addWidget(self.color_input)
        
        add_variant_layout.addWidget(QLabel("سایز:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["S", "M", "L", "XL", "XXL", "XXXL", "سفارشی"])
        self.size_combo.setEditable(True)
        self.size_combo.setMinimumHeight(38)
        self.size_combo.setMaximumWidth(100)
        add_variant_layout.addWidget(self.size_combo)
        
        add_variant_layout.addWidget(QLabel("موجودی:"))
        self.stock_spin = QSpinBox()
        self.stock_spin.setMaximum(99999)
        self.stock_spin.setMinimumHeight(38)
        self.stock_spin.setMaximumWidth(80)
        add_variant_layout.addWidget(self.stock_spin)
        
        add_variant_layout.addWidget(QLabel("قیمت:"))
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMaximum(999999999)
        self.price_spin.setSuffix(" تومان")
        self.price_spin.setMinimumHeight(38)
        self.price_spin.setMaximumWidth(130)
        add_variant_layout.addWidget(self.price_spin)
        
        add_variant_btn = QPushButton("➕ افزودن")
        add_variant_btn.setMinimumHeight(38)
        add_variant_btn.clicked.connect(self.add_variant)
        add_variant_layout.addWidget(add_variant_btn)
        
        add_variant_layout.addStretch()
        variants_layout.addLayout(add_variant_layout)
        
        # جدول تنوع‌ها
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(5)
        self.variants_table.setHorizontalHeaderLabels(["رنگ", "سایز", "موجودی", "قیمت (تومان)", "حذف"])
        self.variants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.variants_table.verticalHeader().setDefaultSectionSize(45)
        self.variants_table.verticalHeader().setVisible(False)
        self.variants_table.setMinimumHeight(200)
        self.variants_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        variants_layout.addWidget(self.variants_table)
        
        tabs.addTab(variants_tab, "🎨 تنوع رنگ و سایز")
        layout.addWidget(tabs)
        
        # دکمه‌های پایین
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 ذخیره کالا")
        save_btn.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        save_btn.setMinimumHeight(50)
        save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def load_categories(self):
        self.db.cursor.execute('SELECT id, name FROM categories ORDER BY name')
        categories = self.db.cursor.fetchall()
        self.category_combo.addItem("بدون دسته‌بندی", None)
        for cat_id, name in categories:
            self.category_combo.addItem(name, cat_id)
    
    def select_image(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب عکس کالا", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((400, 400), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True, quality=85)
                self.image_data = buffer.getvalue()
                
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(230, 230, Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"خطا در بارگذاری عکس: {e}")
    
    def remove_image(self):
        self.image_data = None
        self.image_label.setText("🖼️ برای افزودن عکس کلیک کنید")
        self.image_label.setPixmap(QPixmap())
    
    def add_variant(self):
        color = self.color_input.text().strip()
        size = self.size_combo.currentText().strip()
        stock = self.stock_spin.value()
        price = self.price_spin.value()
        
        if not color or not size:
            QMessageBox.warning(self, "خطا", "رنگ و سایز را وارد کنید")
            return
        
        row = self.variants_table.rowCount()
        self.variants_table.insertRow(row)
        self.variants_table.setRowHeight(row, 45)
        
        self.variants_table.setItem(row, 0, QTableWidgetItem(color))
        self.variants_table.setItem(row, 1, QTableWidgetItem(size))
        self.variants_table.setItem(row, 2, QTableWidgetItem(str(stock)))
        self.variants_table.setItem(row, 3, QTableWidgetItem(f"{int(price):,}"))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMaximumWidth(50)
        delete_btn.setMinimumHeight(35)
        delete_btn.clicked.connect(lambda: self.variants_table.removeRow(row))
        self.variants_table.setCellWidget(row, 4, delete_btn)
        
        self.color_input.clear()
        self.stock_spin.setValue(0)
        self.price_spin.setValue(0)
        self.color_input.setFocus()
    
    def load_product(self):
        self.db.cursor.execute('SELECT * FROM products WHERE id=?', (self.product_id,))
        product = self.db.cursor.fetchone()
        
        if product:
            self.code_input.setText(product[1] or '')
            self.name_input.setText(product[2])
            index = self.category_combo.findData(product[3])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            self.fabric_input.setText(product[4] or '')
            self.model_input.setText(product[5] or '')
            self.description_text.setText(product[6] or '')
            self.min_stock_spin.setValue(product[8] or 10)
            
            if product[7]:
                self.image_data = product[7]
                pixmap = QPixmap()
                pixmap.loadFromData(product[7])
                scaled_pixmap = pixmap.scaled(230, 230, Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
            
            self.db.cursor.execute('SELECT * FROM product_variants WHERE product_id=?', (self.product_id,))
            variants = self.db.cursor.fetchall()
            
            for variant in variants:
                row = self.variants_table.rowCount()
                self.variants_table.insertRow(row)
                self.variants_table.setRowHeight(row, 45)
                
                self.variants_table.setItem(row, 0, QTableWidgetItem(variant[2]))
                self.variants_table.setItem(row, 1, QTableWidgetItem(variant[3]))
                self.variants_table.setItem(row, 2, QTableWidgetItem(str(variant[4])))
                self.variants_table.setItem(row, 3, QTableWidgetItem(f"{int(variant[5]):,}"))
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("dangerBtn")
                delete_btn.setMaximumWidth(50)
                delete_btn.setMinimumHeight(35)
                delete_btn.clicked.connect(lambda checked, r=row: self.variants_table.removeRow(r))
                self.variants_table.setCellWidget(row, 4, delete_btn)
    
    def save_product(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "خطا", "نام کالا الزامی است")
            return
        
        try:
            code = self.code_input.text().strip() or None
            category_id = self.category_combo.currentData()
            fabric = self.fabric_input.text().strip() or None
            model = self.model_input.text().strip() or None
            description = self.description_text.toPlainText().strip() or None
            min_stock = self.min_stock_spin.value()
            
            # غیرفعال کردن موقت کلیدهای خارجی
            self.db.cursor.execute("PRAGMA foreign_keys = OFF")
            
            if self.product_id:
                # آپدیت محصول اصلی
                self.db.cursor.execute('''
                    UPDATE products 
                    SET code=?, name=?, category_id=?, fabric_type=?, 
                        model=?, description=?, image=?, min_stock_alert=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (code, name, category_id, fabric, model, 
                    description, self.image_data, min_stock, self.product_id))
                
                # حذف تنوع‌های قبلی
                self.db.cursor.execute('DELETE FROM product_variants WHERE product_id=?', 
                                    (self.product_id,))
            else:
                # درج محصول جدید
                self.db.cursor.execute('''
                    INSERT INTO products (code, name, category_id, fabric_type, model, 
                                        description, image, min_stock_alert)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (code, name, category_id, fabric, model, 
                    description, self.image_data, min_stock))
                self.product_id = self.db.cursor.lastrowid
            
            # افزودن تنوع‌های جدید از جدول
            for row in range(self.variants_table.rowCount()):
                color = self.variants_table.item(row, 0).text()
                size = self.variants_table.item(row, 1).text()
                stock = int(self.variants_table.item(row, 2).text())
                
                # پاکسازی قیمت از کاراکترهای غیرعددی (مثل "تومان" و ",")
                price_text = self.variants_table.item(row, 3).text()
                price = float(''.join(filter(str.isdigit, price_text)))
                
                self.db.cursor.execute('''
                    INSERT INTO product_variants (product_id, color, size, stock, price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.product_id, color, size, stock, price))
            
            # فعال‌سازی مجدد کلیدهای خارجی
            self.db.cursor.execute("PRAGMA foreign_keys = ON")
            
            self.db.conn.commit()
            QMessageBox.information(self, "موفق", "✅ کالا با موفقیت ذخیره شد")
            self.accept()
            
        except Exception as e:
            # در صورت خطا، حتماً foreign_keys رو دوباره فعال کن
            try:
                self.db.cursor.execute("PRAGMA foreign_keys = ON")
            except:
                pass
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره کالا: {e}")


class InventoryPage(QWidget):
    """صفحه مدیریت انبار"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_products()
        self.load_categories_tree()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # هدر
        header_layout = QHBoxLayout()
        
        title = QLabel("📦 مدیریت انبار")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_product_btn = QPushButton("➕ کالای جدید")
        add_product_btn.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        add_product_btn.setMinimumHeight(42)
        add_product_btn.clicked.connect(self.add_product)
        header_layout.addWidget(add_product_btn)
        
        add_category_btn = QPushButton("📁 دسته‌بندی جدید")
        add_category_btn.setObjectName("secondaryBtn")
        add_category_btn.setMinimumHeight(42)
        add_category_btn.clicked.connect(self.add_category)
        header_layout.addWidget(add_category_btn)
        
        main_layout.addLayout(header_layout)
        
        # محتوای اصلی با Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # پنل سمت راست - دسته‌بندی‌ها و فیلترها
        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_panel.setMaximumWidth(300)
        right_panel.setMinimumWidth(250)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        # جستجو
        search_label = QLabel("🔍 جستجوی پیشرفته")
        search_label.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        search_label.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        right_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو در نام، کد، مدل...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self.filter_products)
        right_layout.addWidget(self.search_input)
        
        # فیلتر دسته‌بندی
        cat_label = QLabel("دسته‌بندی:")
        cat_label.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        right_layout.addWidget(cat_label)
        
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderHidden(True)
        self.categories_tree.setMinimumHeight(200)
        self.categories_tree.itemClicked.connect(self.filter_by_category)
        right_layout.addWidget(self.categories_tree)
        
        # فیلتر وضعیت موجودی
        stock_label = QLabel("وضعیت موجودی:")
        stock_label.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        right_layout.addWidget(stock_label)
        
        self.stock_filter = QComboBox()
        self.stock_filter.setMinimumHeight(38)
        self.stock_filter.addItems(["همه", "موجود", "اتمام موجودی", "کمتر از حد هشدار"])
        self.stock_filter.currentTextChanged.connect(self.filter_products)
        right_layout.addWidget(self.stock_filter)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        # پنل اصلی - جدول کالاها
        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        # نوار اطلاعات سریع
        info_layout = QHBoxLayout()
        
        self.total_label = QLabel("کل کالاها: 0")
        self.total_label.setStyleSheet(f"""
            background: {ModernStyle.PRIMARY};
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
        """)
        info_layout.addWidget(self.total_label)
        
        self.low_stock_label = QLabel("⚠️ هشدار موجودی: 0")
        self.low_stock_label.setStyleSheet(f"""
            background: {ModernStyle.WARNING};
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
        """)
        info_layout.addWidget(self.low_stock_label)
        
        info_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 به‌روزرسانی")
        refresh_btn.setMinimumHeight(38)
        refresh_btn.clicked.connect(self.load_products)
        info_layout.addWidget(refresh_btn)
        
        left_layout.addLayout(info_layout)
        
        # جدول کالاها
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "عکس", "کد", "نام کالا", "دسته‌بندی", "نوع پارچه", 
            "مدل", "موجودی کل", "عملیات"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.products_table.verticalHeader().setDefaultSectionSize(55)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.doubleClicked.connect(self.edit_product)
        left_layout.addWidget(self.products_table)
        
        splitter.addWidget(left_panel)
        splitter.setSizes([280, 920])
        
        main_layout.addWidget(splitter)
    
    def load_categories_tree(self):
        self.categories_tree.clear()
        
        all_item = QTreeWidgetItem(self.categories_tree, ["📂 همه دسته‌بندی‌ها"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, None)
        
        self.db.cursor.execute('SELECT id, name, parent_id FROM categories ORDER BY name')
        categories = self.db.cursor.fetchall()
        
        category_items = {}
        for cat_id, name, parent_id in categories:
            item = QTreeWidgetItem([f"📁 {name}"])
            item.setData(0, Qt.ItemDataRole.UserRole, cat_id)
            category_items[cat_id] = item
            
            if parent_id and parent_id in category_items:
                category_items[parent_id].addChild(item)
            else:
                self.categories_tree.addTopLevelItem(item)
        
        self.categories_tree.expandAll()
    
    def load_products(self):
        query = '''
            SELECT p.id, p.code, p.name, c.name as category, p.fabric_type, 
                   p.model, p.image, p.min_stock_alert,
                   COALESCE(SUM(pv.stock), 0) as total_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_variants pv ON p.id = pv.product_id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        '''
        
        self.db.cursor.execute(query)
        products = self.db.cursor.fetchall()
        self.all_products = products
        
        self.products_table.setRowCount(len(products))
        
        low_stock_count = 0
        for row, product in enumerate(products):
            prod_id, code, name, category, fabric, model, image, min_stock, total_stock = product
            
            self.products_table.setRowHeight(row, 55)
            
            if image:
                pixmap = QPixmap()
                pixmap.loadFromData(image)
                icon = QIcon(pixmap.scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio))
                img_item = QTableWidgetItem()
                img_item.setIcon(icon)
                self.products_table.setItem(row, 0, img_item)
            else:
                self.products_table.setItem(row, 0, QTableWidgetItem("🖼️"))
            
            self.products_table.setItem(row, 1, QTableWidgetItem(str(code or '')))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(name)))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(category or 'بدون دسته')))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(fabric or '')))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(model or '')))
            
            stock_item = QTableWidgetItem(str(int(total_stock)))
            if total_stock == 0:
                stock_item.setBackground(QBrush(QColor("#FFE0E0")))
                stock_item.setForeground(QBrush(QColor("#E17055")))
            elif total_stock <= (min_stock or 10):
                stock_item.setBackground(QBrush(QColor("#FFF3E0")))
                stock_item.setForeground(QBrush(QColor("#FDCB6E")))
                low_stock_count += 1
            else:
                stock_item.setBackground(QBrush(QColor("#E8F5E9")))
                stock_item.setForeground(QBrush(QColor("#00B894")))
            self.products_table.setItem(row, 6, stock_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.setMinimumHeight(35)
            edit_btn.clicked.connect(lambda checked, pid=prod_id: self.edit_product_by_id(pid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setMinimumHeight(35)
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(lambda checked, pid=prod_id: self.delete_product(pid))
            actions_layout.addWidget(delete_btn)
            
            self.products_table.setCellWidget(row, 7, actions_widget)
        
        self.total_label.setText(f"کل کالاها: {len(products)}")
        self.low_stock_label.setText(f"⚠️ هشدار موجودی: {low_stock_count}")
    
    def add_product(self):
        dialog = ProductDetailDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
            self.db.data_changed.emit()
    
    def edit_product(self):
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            product_id = self.all_products[current_row][0]
            self.edit_product_by_id(product_id)
    
    def edit_product_by_id(self, product_id):
        dialog = ProductDetailDialog(self.db, product_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
            self.db.data_changed.emit()
    
    def delete_product(self, product_id):
        reply = QMessageBox.question(
            self, "حذف کالا",
            "آیا از حذف این کالا و تمام تنوع‌های آن اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
                self.db.conn.commit()
                self.load_products()
                self.db.data_changed.emit()
                QMessageBox.information(self, "موفق", "کالا با موفقیت حذف شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف کالا: {e}")
    
    def add_category(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "دسته‌بندی جدید", "نام دسته‌بندی:")
        if ok and name.strip():
            try:
                self.db.cursor.execute('INSERT INTO categories (name) VALUES (?)', (name.strip(),))
                self.db.conn.commit()
                self.load_categories_tree()
                QMessageBox.information(self, "موفق", "دسته‌بندی جدید اضافه شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن دسته‌بندی: {e}")
    
    def filter_products(self):
        search_text = self.search_input.text().strip()
        stock_status = self.stock_filter.currentText()
        
        if not search_text and stock_status == "همه":
            self.load_products()
            return
        
        filtered = []
        for product in self.all_products:
            prod_id, code, name, category, fabric, model, image, min_stock, total_stock = product
            
            if search_text:
                search_lower = search_text.lower()
                if not (search_lower in str(code or '').lower() or 
                       search_lower in str(name).lower() or 
                       search_lower in str(fabric or '').lower() or 
                       search_lower in str(model or '').lower()):
                    continue
            
            if stock_status == "موجود" and total_stock == 0:
                continue
            elif stock_status == "اتمام موجودی" and total_stock > 0:
                continue
            elif stock_status == "کمتر از حد هشدار" and total_stock > (min_stock or 10):
                continue
            
            filtered.append(product)
        
        self.display_filtered(filtered)
    
    def filter_by_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        if category_id is None:
            self.load_products()
            return
        
        query = '''
            SELECT p.id, p.code, p.name, c.name as category, p.fabric_type, 
                   p.model, p.image, p.min_stock_alert,
                   COALESCE(SUM(pv.stock), 0) as total_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_variants pv ON p.id = pv.product_id
            WHERE p.category_id = ?
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        '''
        
        self.db.cursor.execute(query, (category_id,))
        products = self.db.cursor.fetchall()
        self.display_filtered(products)
    
    def display_filtered(self, products):
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            prod_id, code, name, category, fabric, model, image, min_stock, total_stock = product
            
            self.products_table.setRowHeight(row, 55)
            
            if image:
                pixmap = QPixmap()
                pixmap.loadFromData(image)
                icon = QIcon(pixmap.scaled(45, 45))
                img_item = QTableWidgetItem()
                img_item.setIcon(icon)
                self.products_table.setItem(row, 0, img_item)
            else:
                self.products_table.setItem(row, 0, QTableWidgetItem("🖼️"))
            
            self.products_table.setItem(row, 1, QTableWidgetItem(str(code or '')))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(name)))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(category or '')))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(fabric or '')))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(model or '')))
            
            stock_item = QTableWidgetItem(str(int(total_stock)))
            if total_stock == 0:
                stock_item.setBackground(QBrush(QColor("#FFE0E0")))
            elif total_stock <= (min_stock or 10):
                stock_item.setBackground(QBrush(QColor("#FFF3E0")))
            else:
                stock_item.setBackground(QBrush(QColor("#E8F5E9")))
            self.products_table.setItem(row, 6, stock_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.setMinimumHeight(35)
            edit_btn.clicked.connect(lambda checked, pid=prod_id: self.edit_product_by_id(pid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setMinimumHeight(35)
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(lambda checked, pid=prod_id: self.delete_product(pid))
            actions_layout.addWidget(delete_btn)
            
            self.products_table.setCellWidget(row, 7, actions_widget)