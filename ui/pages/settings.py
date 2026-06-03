from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QMessageBox, QFrame,
    QGridLayout, QTextEdit, QGroupBox, QFileDialog,
    QSpinBox, QTabWidget, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from ui.styles import ModernStyle
import os

class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.logo_data = None
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        # لایه اصلی با اسکرول
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # اسکرول area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {ModernStyle.BG_LIGHT};
            }}
        """)
        
        # ویجت محتوای اسکرول
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(30, 20, 30, 20)
        
        # هدر
        title = QLabel("⚙️ تنظیمات نرم‌افزار")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY}; background: transparent;")
        scroll_layout.addWidget(title)
        
        # تب‌های تنظیمات
        tabs = QTabWidget()
        
        # تب اطلاعات برند
        tabs.addTab(self.create_brand_tab(), "🏢 اطلاعات برند")
        
        # تب ظاهری
        tabs.addTab(self.create_appearance_tab(), "🎨 ظاهر")
        
        # تب پشتیبان‌گیری
        tabs.addTab(self.create_backup_tab(), "💾 پشتیبان‌گیری")
        
        # تب حساب‌ها
        tabs.addTab(self.create_accounts_tab(), "🏦 حساب‌ها")
        
        scroll_layout.addWidget(tabs)
        
        # دکمه ذخیره - بیرون از تب‌ها
        save_btn = QPushButton("💾 ذخیره تمام تنظیمات")
        save_btn.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        save_btn.setMinimumHeight(55)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernStyle.PRIMARY}, stop:1 #A29BFE);
                color: white;
                border-radius: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A4BD1, stop:1 {ModernStyle.PRIMARY});
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        scroll_layout.addWidget(save_btn)
        
        # دکمه پشتیبان‌گیری دستی
        backup_btn = QPushButton("🔄 پشتیبان‌گیری دستی الآن")
        backup_btn.setMinimumHeight(45)
        backup_btn.setObjectName("secondaryBtn")
        backup_btn.clicked.connect(self.manual_backup)
        scroll_layout.addWidget(backup_btn)
        
        # امضای توسعه‌دهنده
        dev_label = QLabel("🛠️ توسعه‌دهنده: @immdjavad | نسخه 2.0.0")
        dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_label.setStyleSheet(f"""
            color: {ModernStyle.TEXT_LIGHT};
            font-size: 11px;
            padding: 15px;
            margin-top: 10px;
            border-top: 1px solid {ModernStyle.BORDER};
            background: transparent;
        """)
        scroll_layout.addWidget(dev_label)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
    
    def create_brand_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # لوگو
        logo_group = QGroupBox("🖼️ لوگو برند")
        logo_layout = QHBoxLayout()
        
        self.logo_label = QLabel("لوگو انتخاب نشده")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumSize(150, 150)
        self.logo_label.setMaximumSize(180, 180)
        self.logo_label.setStyleSheet(f"""
            border: 2px dashed {ModernStyle.PRIMARY};
            border-radius: 12px;
            background: #F8F6FF;
        """)
        logo_layout.addWidget(self.logo_label)
        
        logo_btn_layout = QVBoxLayout()
        
        select_logo_btn = QPushButton("📁 انتخاب لوگو")
        select_logo_btn.setMinimumHeight(38)
        select_logo_btn.clicked.connect(self.select_logo)
        logo_btn_layout.addWidget(select_logo_btn)
        
        remove_logo_btn = QPushButton("🗑️ حذف لوگو")
        remove_logo_btn.setObjectName("dangerBtn")
        remove_logo_btn.setMinimumHeight(38)
        remove_logo_btn.clicked.connect(self.remove_logo)
        logo_btn_layout.addWidget(remove_logo_btn)
        
        logo_btn_layout.addStretch()
        logo_layout.addLayout(logo_btn_layout)
        
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)
        
        # اطلاعات برند
        brand_group = QGroupBox("📋 اطلاعات برند")
        brand_layout = QGridLayout()
        brand_layout.setSpacing(10)
        
        brand_layout.addWidget(QLabel("نام برند:"), 0, 0)
        self.brand_name = QLineEdit()
        self.brand_name.setPlaceholderText("نام برند یا شرکت")
        self.brand_name.setMinimumHeight(38)
        brand_layout.addWidget(self.brand_name, 0, 1)
        
        brand_layout.addWidget(QLabel("آدرس:"), 1, 0)
        self.brand_address = QTextEdit()
        self.brand_address.setMaximumHeight(80)
        self.brand_address.setMinimumHeight(70)
        self.brand_address.setPlaceholderText("آدرس کامل شرکت/فروشگاه")
        brand_layout.addWidget(self.brand_address, 1, 1)
        
        brand_layout.addWidget(QLabel("تلفن:"), 2, 0)
        self.brand_phone = QLineEdit()
        self.brand_phone.setPlaceholderText("021-12345678")
        self.brand_phone.setMinimumHeight(38)
        brand_layout.addWidget(self.brand_phone, 2, 1)
        
        brand_layout.addWidget(QLabel("موبایل:"), 3, 0)
        self.brand_mobile = QLineEdit()
        self.brand_mobile.setPlaceholderText("09123456789")
        self.brand_mobile.setMinimumHeight(38)
        brand_layout.addWidget(self.brand_mobile, 3, 1)
        
        brand_group.setLayout(brand_layout)
        layout.addWidget(brand_group)
        
        # متن فوتر فاکتور
        footer_group = QGroupBox("📄 تنظیمات فاکتور")
        footer_layout = QVBoxLayout()
        
        footer_layout.addWidget(QLabel("متن پایین فاکتور:"))
        self.invoice_footer = QTextEdit()
        self.invoice_footer.setMaximumHeight(70)
        self.invoice_footer.setMinimumHeight(60)
        self.invoice_footer.setPlaceholderText("متن پایین فاکتور")
        footer_layout.addWidget(self.invoice_footer)
        
        footer_layout.addWidget(QLabel("نام شخص صادرکننده فاکتور:"))
        self.invoice_person = QLineEdit()
        self.invoice_person.setPlaceholderText("نام شخص حقیقی")
        self.invoice_person.setMinimumHeight(38)
        footer_layout.addWidget(self.invoice_person)
        
        footer_group.setLayout(footer_layout)
        layout.addWidget(footer_group)
        
        layout.addStretch()
        return widget
    
    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # تم
        theme_group = QGroupBox("🎨 تم برنامه")
        theme_layout = QHBoxLayout()
        
        theme_layout.addWidget(QLabel("انتخاب تم:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["روشن ☀️", "تاریک 🌙"])
        self.theme_combo.setMinimumHeight(38)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # فونت
        font_group = QGroupBox("🔤 تنظیمات فونت")
        font_layout = QGridLayout()
        font_layout.setSpacing(10)
        
        font_layout.addWidget(QLabel("نوع فونت:"), 0, 0)
        self.font_family = QComboBox()
        self.font_family.addItems(["Tahoma", "Arial", "IRANSans", "B Nazanin", "B Yekan"])
        self.font_family.setEditable(True)
        self.font_family.setMinimumHeight(38)
        font_layout.addWidget(self.font_family, 0, 1)
        
        font_layout.addWidget(QLabel("سایز فونت:"), 0, 2)
        self.font_size = QSpinBox()
        self.font_size.setMinimum(8)
        self.font_size.setMaximum(16)
        self.font_size.setValue(10)
        self.font_size.setMinimumHeight(38)
        font_layout.addWidget(self.font_size, 0, 3)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
    
    def create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        backup_group = QGroupBox("💾 پشتیبان‌گیری خودکار")
        backup_layout = QGridLayout()
        backup_layout.setSpacing(10)
        
        backup_layout.addWidget(QLabel("درایو اول:"), 0, 0)
        self.backup_drive1 = QLineEdit()
        self.backup_drive1.setPlaceholderText("مثلاً: D:\\")
        self.backup_drive1.setMinimumHeight(38)
        backup_layout.addWidget(self.backup_drive1, 0, 1)
        
        browse1 = QPushButton("📁 انتخاب")
        browse1.setMinimumHeight(38)
        browse1.clicked.connect(lambda: self.browse_drive(self.backup_drive1))
        backup_layout.addWidget(browse1, 0, 2)
        
        backup_layout.addWidget(QLabel("درایو دوم:"), 1, 0)
        self.backup_drive2 = QLineEdit()
        self.backup_drive2.setPlaceholderText("مثلاً: E:\\")
        self.backup_drive2.setMinimumHeight(38)
        backup_layout.addWidget(self.backup_drive2, 1, 1)
        
        browse2 = QPushButton("📁 انتخاب")
        browse2.setMinimumHeight(38)
        browse2.clicked.connect(lambda: self.browse_drive(self.backup_drive2))
        backup_layout.addWidget(browse2, 1, 2)
        
        backup_layout.addWidget(QLabel("یادآوری (روز):"), 2, 0)
        self.backup_reminder = QSpinBox()
        self.backup_reminder.setMinimum(1)
        self.backup_reminder.setMaximum(30)
        self.backup_reminder.setValue(7)
        self.backup_reminder.setSuffix(" روز")
        self.backup_reminder.setMinimumHeight(38)
        backup_layout.addWidget(self.backup_reminder, 2, 1)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # دکمه‌های بکاپ
        btn_layout = QHBoxLayout()
        
        take_backup_btn = QPushButton("💾 گرفتن بکاپ همین الان")
        take_backup_btn.setMinimumHeight(40)
        take_backup_btn.setObjectName("successBtn")
        take_backup_btn.clicked.connect(self.take_backup_now)
        btn_layout.addWidget(take_backup_btn)
        
        restore_btn = QPushButton("🔄 بازیابی از بکاپ")
        restore_btn.setMinimumHeight(40)
        restore_btn.setObjectName("dangerBtn")
        restore_btn.clicked.connect(self.restore_from_backup)
        btn_layout.addWidget(restore_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget
    
    def create_accounts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        accounts_group = QGroupBox("🏦 حساب‌های بانکی")
        accounts_layout = QGridLayout()
        accounts_layout.setSpacing(10)
        
        accounts_layout.addWidget(QLabel("شماره حساب:"), 0, 0)
        self.account_number = QLineEdit()
        self.account_number.setPlaceholderText("شماره حساب بانکی")
        self.account_number.setMinimumHeight(38)
        accounts_layout.addWidget(self.account_number, 0, 1)
        
        accounts_layout.addWidget(QLabel("شماره شبا:"), 1, 0)
        self.shaba_number = QLineEdit()
        self.shaba_number.setPlaceholderText("IR...")
        self.shaba_number.setMinimumHeight(38)
        accounts_layout.addWidget(self.shaba_number, 1, 1)
        
        accounts_layout.addWidget(QLabel("نام صاحب حساب:"), 2, 0)
        self.account_holder = QLineEdit()
        self.account_holder.setPlaceholderText("نام شخص یا شرکت")
        self.account_holder.setMinimumHeight(38)
        accounts_layout.addWidget(self.account_holder, 2, 1)
        
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)
        
        layout.addStretch()
        return widget
    
    def select_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب لوگو", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            with open(file_path, 'rb') as f:
                self.logo_data = f.read()
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(170, 170, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
    
    def remove_logo(self):
        self.logo_data = None
        self.logo_label.setText("لوگو انتخاب نشده")
        self.logo_label.setPixmap(QPixmap())
    
    def browse_drive(self, line_edit):
        drive = QFileDialog.getExistingDirectory(self, "انتخاب درایو")
        if drive:
            line_edit.setText(drive)
    
    def take_backup_now(self):
        """گرفتن بکاپ فوری"""        from utils.backup_manager import BackupManager
        from PyQt6.QtWidgets import QMessageBox
        backup_mgr = BackupManager(self.db.db_path)
        drive1 = self.backup_drive1.text().strip()
        drive2 = self.backup_drive2.text().strip()
        backup_mgr.set_backup_drives(drive1, drive2)
        backup_mgr.backup_completed.connect(
            lambda path: QMessageBox.information(self, "موفق", f"✅ بکاپ ذخیره شد:\n{path}")
        )
        backup_mgr.backup_failed.connect(
            lambda msg: QMessageBox.critical(self, "خطا", f"❌ {msg}")
        )
        if not backup_mgr.backup_drives:
            QMessageBox.warning(self, "هشدار", "ابتدا یک درایو برای بکاپ انتخاب کنید")
            return
        backup_mgr.create_backup()
    
    def restore_from_backup(self):
        """بازیابی از بکاپ"""        from utils.backup_manager import BackupManager
        from PyQt6.QtWidgets import QMessageBox, QFileDialog
        reply = QMessageBox.warning(
            self, "هشدار",
            "⚠️ بازیابی از بکاپ تمام داده‌های فعلی را جایگزین می‌کند.\nآیا مطمئن هستید?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        backup_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل بکاپ", "", "Database Files (*.db)"
        )
        if not backup_path:
            return
        backup_mgr = BackupManager(self.db.db_path)
        if backup_mgr.restore_backup(backup_path):
            QMessageBox.information(self, "موفق", "✅ بازیابی با موفقیت انجام شد. لطفاً برنامه را مجدداً اجرا کنید.")
        else:
            QMessageBox.critical(self, "خطا", "❌ خطا در بازیابی فایل بکاپ")
    
    def on_theme_changed(self):
        pass
    
    def load_settings(self):
        self.brand_name.setText(self.db.get_setting('brand_name') or '')
        self.brand_address.setText(self.db.get_setting('brand_address') or '')
        self.brand_phone.setText(self.db.get_setting('phone') or '')
        self.brand_mobile.setText(self.db.get_setting('mobile') or '')
        self.invoice_footer.setText(self.db.get_setting('invoice_footer') or '')
        self.invoice_person.setText(self.db.get_setting('invoice_person') or '')
        
        theme = self.db.get_setting('theme')
        if theme == 'dark':
            self.theme_combo.setCurrentIndex(1)
        
        font_family = self.db.get_setting('font_family')
        if font_family:
            idx = self.font_family.findText(font_family)
            if idx >= 0:
                self.font_family.setCurrentIndex(idx)
        
        font_size = self.db.get_setting('font_size')
        if font_size:
            self.font_size.setValue(int(font_size))
        
        self.backup_drive1.setText(self.db.get_setting('backup_drive1') or '')
        self.backup_drive2.setText(self.db.get_setting('backup_drive2') or '')
        
        reminder = self.db.get_setting('backup_reminder_days')
        if reminder:
            self.backup_reminder.setValue(int(reminder))
        
        self.account_number.setText(self.db.get_setting('account_number') or '')
        self.shaba_number.setText(self.db.get_setting('shaba_number') or '')
        self.account_holder.setText(self.db.get_setting('account_holder') or '')
        
        # لوگو
        logo_path = self.db.get_setting('logo_path')
        if logo_path:
            try:
                import base64
                self.logo_data = base64.b64decode(logo_path)
                pixmap = QPixmap()
                pixmap.loadFromData(self.logo_data)
                scaled = pixmap.scaled(170, 170, Qt.AspectRatioMode.KeepAspectRatio)
                self.logo_label.setPixmap(scaled)
            except:
                pass
    
    def save_settings(self):
        try:
            import base64
            
            settings = {
                'brand_name': self.brand_name.text(),
                'brand_address': self.brand_address.toPlainText(),
                'phone': self.brand_phone.text(),
                'mobile': self.brand_mobile.text(),
                'invoice_footer': self.invoice_footer.toPlainText(),
                'invoice_person': self.invoice_person.text(),
                'theme': 'dark' if self.theme_combo.currentIndex() == 1 else 'light',
                'font_family': self.font_family.currentText(),
                'font_size': str(self.font_size.value()),
                'backup_drive1': self.backup_drive1.text(),
                'backup_drive2': self.backup_drive2.text(),
                'backup_reminder_days': str(self.backup_reminder.value()),
                'account_number': self.account_number.text(),
                'shaba_number': self.shaba_number.text(),
                'account_holder': self.account_holder.text(),
                'logo_path': base64.b64encode(self.logo_data).decode('utf-8') if self.logo_data else ''
            }
            
            for key, value in settings.items():
                self.db.set_setting(key, value)
            
            # آپدیت مسیرهای بکاپ در منیجر اصلی
            try:
                from ui.main_window import MainWindow
                main_window = None
                for widget in QApplication.topLevelWidgets():
                    if isinstance(widget, MainWindow):
                        main_window = widget
                        break
                
                if main_window:
                    main_window.backup_manager.set_backup_drives(
                        self.backup_drive1.text(),
                        self.backup_drive2.text()
                    )
            except Exception as e:
                print(f"خطا در آپدیت مسیر بکاپ: {e}")
            
            QMessageBox.information(self, "موفق", "✅ تمام تنظیمات با موفقیت ذخیره شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات: {e}")
    
    def manual_backup(self):
        from utils.backup_manager import BackupManager
        
        backup_mgr = BackupManager()
        backup_mgr.set_backup_drives(
            self.backup_drive1.text(),
            self.backup_drive2.text()
        )
        
        if backup_mgr.create_backup():
            QMessageBox.information(self, "موفق", "✅ پشتیبان‌گیری با موفقیت انجام شد")
        else:
            QMessageBox.critical(self, "خطا", "❌ پشتیبان‌گیری با خطا مواجه شد")