from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QStatusBar, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
import jdatetime
from database.db_manager import DatabaseManager
from ui.styles import ModernStyle
from ui.pages.dashboard import DashboardPage
from ui.pages.inventory import InventoryPage
from ui.pages.customers import CustomersPage
from ui.pages.orders import OrdersPage
from ui.pages.accounting import AccountingPage
from ui.pages.cutting import CuttingPage
from ui.pages.settings import SettingsPage
from ui.pages.reports import ReportsPage
from utils.backup_manager import BackupManager


class ModernSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6C5CE7, stop:1 #4834D4);
                border-radius: 0px;
                border: none;
            }
        """)
        self.badge_labels = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 30, 16, 30)

        logo_label = QLabel("🏭")
        logo_label.setFont(QFont("Segoe UI Emoji", 35))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("color: white; background: transparent; border: none;")
        layout.addWidget(logo_label)

        brand_label = QLabel("مدیریت تولید پوشاک")
        brand_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_label.setStyleSheet("color: white; background: transparent; border: none; padding: 8px;")
        layout.addWidget(brand_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255,255,255,0.2); min-height: 2px; max-height: 2px; border: none;")
        layout.addWidget(separator)

        self.buttons = {}
        menu_items = [
            ("dashboard", "📊", "داشبورد"),
            ("inventory", "📦", "مدیریت انبار"),
            ("customers", "👥", "مشتریان"),
            ("orders", "📋", "سفارشات / فاکتور"),
            ("accounting", "💰", "حسابداری"),
            ("cutting", "✂️", "دفتر برش"),
            ("reports", "📈", "گزارش‌ها"),
            ("settings", "⚙️", "تنظیمات"),
        ]

        for key, icon, text in menu_items:
            # wrapper برای badge
            btn_wrapper = QWidget()
            btn_wrapper.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_wrapper)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(0)

            btn = QPushButton(f"  {icon}  {text}")
            btn.setFont(QFont("Tahoma", 11))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: rgba(255, 255, 255, 0.85);
                    border: none;
                    padding: 12px 16px;
                    border-radius: 10px;
                    text-align: right;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                }}
                QPushButton:checked {{
                    background: rgba(255, 255, 255, 0.25);
                    color: white;
                    font-weight: bold;
                    border-left: 3px solid white;
                }}
            """)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_layout.addWidget(btn)

            # badge (برای کم‌موجودی)
            badge = QLabel("")
            badge.setFixedSize(20, 20)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet("""
                QLabel {
                    background: #E17055;
                    color: white;
                    border-radius: 10px;
                    font-size: 9px;
                    font-weight: bold;
                    border: none;
                }
            """)
            badge.hide()
            btn_layout.addWidget(badge)

            self.buttons[key] = btn
            self.badge_labels[key] = badge
            layout.addWidget(btn_wrapper)

        layout.addStretch()

        copyright_label = QLabel("🛠️ توسعه‌دهنده: @immdjavad\n📦 نسخه 2.1.0")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px; padding: 10px; background: transparent; border: none;")
        layout.addWidget(copyright_label)

    def set_badge(self, key, count):
        if key in self.badge_labels:
            badge = self.badge_labels[key]
            if count > 0:
                badge.setText(str(count) if count < 100 else "99+")
                badge.show()
            else:
                badge.hide()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.backup_manager = BackupManager()
        self.setup_backup_system()

        self.setWindowTitle("مدیریت تولید پوشاک - نسخه حرفه‌ای")

        self.init_ui()
        self.load_theme()
        self.setup_backup_timer()
        self.setup_badge_timer()

    def setup_backup_system(self):
        drive1 = self.db.get_setting('backup_drive1')
        drive2 = self.db.get_setting('backup_drive2')
        self.backup_manager.set_backup_drives(drive1, drive2)
        self.backup_manager.backup_completed.connect(self.on_backup_completed)
        self.backup_manager.backup_failed.connect(self.on_backup_failed)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F5F6FA;")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = ModernSidebar()
        main_layout.addWidget(self.sidebar)

        for key, btn in self.sidebar.buttons.items():
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("QStackedWidget { background-color: #F5F6FA; }")

        self.pages = {
            "dashboard": DashboardPage(self.db),
            "inventory": InventoryPage(self.db),
            "customers": CustomersPage(self.db),
            "orders": OrdersPage(self.db),
            "accounting": AccountingPage(self.db),
            "cutting": CuttingPage(self.db),
            "reports": ReportsPage(self.db),
            "settings": SettingsPage(self.db),
        }

        for page in self.pages.values():
            self.content_stack.addWidget(page)

        main_layout.addWidget(self.content_stack)

        self.sidebar.buttons["dashboard"].setChecked(True)
        self.content_stack.setCurrentWidget(self.pages["dashboard"])

        # اتصال سیگنال theme_changed از صفحه تنظیمات
        if hasattr(self.pages["settings"], 'theme_changed'):
            self.pages["settings"].theme_changed.connect(self.change_theme)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: white;
                border-top: 1px solid {ModernStyle.BORDER};
                font-size: 12px;
                color: {ModernStyle.TEXT_SECONDARY};
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

        self.apply_light_theme()

    def switch_page(self, page_name):
        new_page = self.pages[page_name]
        self.animate_page_transition(new_page)
        self.content_stack.setCurrentWidget(new_page)

        for key, btn in self.sidebar.buttons.items():
            btn.setChecked(key == page_name)

        # refresh گزارشات هنگام ورود
        if page_name == "reports":
            new_page.load_all()

    def animate_page_transition(self, new_page):
        animation = QPropertyAnimation(new_page, b"windowOpacity")
        animation.setDuration(200)
        animation.setStartValue(0.6)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

    def apply_light_theme(self):
        self.setStyleSheet(ModernStyle.get_main_stylesheet())
        self.centralWidget().setStyleSheet("background-color: #F5F6FA;")
        self.content_stack.setStyleSheet("background-color: #F5F6FA;")
        for page in self.pages.values():
            page.setStyleSheet(ModernStyle.get_main_stylesheet())

    def apply_dark_theme(self):
        self.setStyleSheet(ModernStyle.get_dark_stylesheet())
        self.centralWidget().setStyleSheet("background-color: #2D3436;")
        self.content_stack.setStyleSheet("background-color: #2D3436;")
        for page in self.pages.values():
            page.setStyleSheet(ModernStyle.get_dark_stylesheet())

    def load_theme(self):
        theme = self.db.get_setting('theme')
        if theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def change_theme(self, theme):
        if theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.db.set_setting('theme', theme)

    def setup_backup_timer(self):
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.check_backup_reminder)
        self.backup_timer.start(43200000)
        QTimer.singleShot(5000, self.check_backup_reminder)

    def setup_badge_timer(self):
        """تایمر برای به‌روزرسانی badge کم‌موجودی"""
        self.badge_timer = QTimer()
        self.badge_timer.timeout.connect(self.update_badges)
        self.badge_timer.start(60000)  # هر ۱ دقیقه
        QTimer.singleShot(2000, self.update_badges)

    def update_badges(self):
        try:
            low_stock = self.db.get_low_stock_count()
            self.sidebar.set_badge("inventory", low_stock)
        except Exception as e:
            print(f"Badge update error: {e}")

    def check_backup_reminder(self):
        """بررسی نیاز به یادآوری بکاپ"""
        try:
            reminder_days = int(self.db.get_setting('backup_reminder_days') or 7)

            if self.backup_manager.should_remind_backup(reminder_days):
                last_reminder = self.db.get_setting('last_backup_reminder_date')
                today = jdatetime.date.today().strftime('%Y/%m/%d')

                if last_reminder != today:
                    if not hasattr(self, '_backup_reminder_shown_today'):
                        self._backup_reminder_shown_today = True
                        self.show_backup_reminder()
                        self.db.set_setting('last_backup_reminder_date', today)

        except Exception as e:
            print(f"خطا در بررسی یادآوری بکاپ: {e}")

    def show_backup_reminder(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("یادآوری پشتیبان‌گیری")
        msg.setText("💾 یادآوری پشتیبان‌گیری هفتگی")
        msg.setInformativeText(
            "زمان پشتیبان‌گیری دوره‌ای فرا رسیده است.\n\n"
            "✅ با پشتیبان‌گیری از اطلاعات خود محافظت کنید.\n"
            "✅ فقط ۳ نسخه آخر در هر درایو نگهداری می‌شود.\n\n"
            "آیا مایل به انجام پشتیبان‌گیری هستید؟"
        )

        backup_now_btn = msg.addButton("🔄 بکاپ الآن", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("⏰ یادآوری فردا", QMessageBox.ButtonRole.RejectRole)
        dont_remind_btn = msg.addButton("❌ این هفته یادآوری نشود", QMessageBox.ButtonRole.DestructiveRole)

        msg.setDefaultButton(backup_now_btn)
        msg.exec()

        clicked_button = msg.clickedButton()

        if clicked_button == backup_now_btn:
            self.perform_backup()
        elif clicked_button == dont_remind_btn:
            self.db.set_setting('last_backup_reminder_date', jdatetime.date.today().strftime('%Y/%m/%d'))
            self.status_bar.showMessage("🔕 یادآوری بکاپ تا ۷ روز آینده غیرفعال شد", 5000)

    def perform_backup(self):
        self.status_bar.showMessage("⏳ در حال پشتیبان‌گیری...", 2000)
        QApplication.processEvents()

        success = self.backup_manager.create_backup()

        if success:
            drives = "\n".join([f"📁 {d}\\ClothingERP_Backups" for d in self.backup_manager.backup_drives])
            QMessageBox.information(
                self,
                "پشتیبان‌گیری موفق",
                f"✅ پشتیبان‌گیری با موفقیت انجام شد!\n\n📍 محل ذخیره:\n{drives}\n\n💡 فقط ۳ نسخه آخر نگهداری می‌شود."
            )
            self.status_bar.showMessage("✅ پشتیبان‌گیری با موفقیت انجام شد", 5000)
        else:
            QMessageBox.warning(
                self,
                "خطا در پشتیبان‌گیری",
                "⚠️ پشتیبان‌گیری با خطا مواجه شد!\n\n"
                "لطفاً موارد زیر را بررسی کنید:\n"
                "• درایوهای مقصد در دسترس باشند\n"
                "• فضای کافی در درایوها وجود داشته باشد\n"
                "• مسیرهای تنظیم شده در بخش تنظیمات صحیح باشند"
            )
            self.status_bar.showMessage("❌ خطا در پشتیبان‌گیری", 5000)

    def on_backup_completed(self, path):
        self.status_bar.showMessage(f"✅ پشتیبان‌گیری انجام شد: {path}", 5000)

    def on_backup_failed(self, error):
        self.status_bar.showMessage(f"❌ خطا در پشتیبان‌گیری: {error}", 5000)

    def update_status_bar(self):
        from utils.jdatetime_utils import get_current_shamsi_date
        shamsi_date = get_current_shamsi_date()
        self.status_bar.showMessage(f"📅 {shamsi_date} | ✅ نرم‌افزار فعال | نسخه 2.1.0 | توسعه‌دهنده: @immdjavad")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'خروج',
            'آیا از خروج از برنامه اطمینان دارید؟\nپیشنهاد می‌شود قبل از خروج پشتیبان‌گیری انجام دهید.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.close()
            event.accept()
        else:
            event.ignore()
