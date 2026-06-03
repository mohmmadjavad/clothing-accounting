from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
from ui.styles import ModernStyle
from utils.jdatetime_utils import get_current_shamsi_date


class StatCard(QFrame):
    def __init__(self, title, value, icon, color, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._color = color
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid {ModernStyle.BORDER};
                padding: 4px;
            }}
            QFrame#card:hover {{
                border-color: {color};
                border-width: 2px;
            }}
        """)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 12, 16, 12)

        top_row = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setStyleSheet("background: transparent; border: none;")
        top_row.addWidget(icon_label)

        top_row.addStretch()

        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        top_row.addWidget(self.value_label)

        layout.addLayout(top_row)

        title_label = QLabel(title)
        title_label.setFont(QFont("Tahoma", 11))
        title_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; background: transparent; border: none;")
        layout.addWidget(title_label)

        if subtitle:
            self.sub_label = QLabel(subtitle)
            self.sub_label.setFont(QFont("Tahoma", 9))
            self.sub_label.setStyleSheet(f"color: {ModernStyle.TEXT_LIGHT}; background: transparent; border: none;")
            layout.addWidget(self.sub_label)
        else:
            self.sub_label = None

    def set_value(self, value):
        self.value_label.setText(str(value))

    def set_subtitle(self, text):
        if self.sub_label:
            self.sub_label.setText(text)


class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)

    def init_ui(self):
        # اسکرول کل صفحه
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

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
        title_layout = QHBoxLayout()
        title = QLabel("📊 داشبورد مدیریتی")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernStyle.TEXT_PRIMARY};")
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.date_label = QLabel(f"📅 {get_current_shamsi_date()}")
        self.date_label.setFont(QFont("Tahoma", 14))
        self.date_label.setStyleSheet(f"color: {ModernStyle.PRIMARY};")
        title_layout.addWidget(self.date_label)

        refresh_btn = QPushButton("🔄 به‌روزرسانی")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setMaximumWidth(130)
        refresh_btn.clicked.connect(self.load_data)
        title_layout.addWidget(refresh_btn)

        main_layout.addLayout(title_layout)

        # ردیف اول کارت‌ها
        row1 = QGridLayout()
        row1.setSpacing(16)

        self.card_products = StatCard("کل کالاها", "0", "📦", ModernStyle.PRIMARY, "محصول ثبت‌شده")
        row1.addWidget(self.card_products, 0, 0)

        self.card_customers = StatCard("مشتریان", "0", "👥", ModernStyle.SECONDARY, "مشتری فعال")
        row1.addWidget(self.card_customers, 0, 1)

        self.card_today_orders = StatCard("سفارشات امروز", "0", "📋", ModernStyle.ACCENT, "فاکتور صادرشده")
        row1.addWidget(self.card_today_orders, 0, 2)

        self.card_today_revenue = StatCard("درآمد امروز", "0 تومان", "💰", ModernStyle.SUCCESS, "فروش تکمیل‌شده")
        row1.addWidget(self.card_today_revenue, 0, 3)

        main_layout.addLayout(row1)

        # ردیف دوم کارت‌ها
        row2 = QGridLayout()
        row2.setSpacing(16)

        self.card_pending = StatCard("سفارشات معلق", "0", "⏳", ModernStyle.WARNING, "در انتظار تکمیل")
        row2.addWidget(self.card_pending, 0, 0)

        self.card_low_stock = StatCard("کم‌موجودی", "0", "⚠️", ModernStyle.DANGER, "نیاز به تأمین")
        row2.addWidget(self.card_low_stock, 0, 1)

        self.card_debtors = StatCard("بدهکاران", "0", "👤", "#E84393", "مشتری بدهکار")
        row2.addWidget(self.card_debtors, 0, 2)

        self.card_pending_amount = StatCard("مبلغ معلق", "0 تومان", "💳", ModernStyle.INFO, "مبلغ در انتظار")
        row2.addWidget(self.card_pending_amount, 0, 3)

        main_layout.addLayout(row2)

        # بخش آخرین سفارشات
        orders_label = QLabel("📋 آخرین سفارشات")
        orders_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        main_layout.addWidget(orders_label)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["شماره فاکتور", "تاریخ", "مشتری", "مبلغ (تومان)", "وضعیت"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setMaximumHeight(220)
        self.orders_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.orders_table)

        # بخش هشدار موجودی
        alerts_label = QLabel("⚠️ کالاهای کم‌موجودی")
        alerts_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        main_layout.addWidget(alerts_label)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels(["کالا", "رنگ / سایز", "موجودی فعلی", "حداقل موجودی"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.alerts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setMaximumHeight(200)
        self.alerts_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.alerts_table)

        main_layout.addStretch()

    def load_data(self):
        try:
            self.date_label.setText(f"📅 {get_current_shamsi_date()}")

            stats = self.db.get_dashboard_stats()

            self.card_products.set_value(stats['products'])
            self.card_customers.set_value(stats['customers'])
            self.card_today_orders.set_value(stats['today_orders'])
            self.card_today_revenue.set_value(f"{int(stats['today_revenue']):,} تومان")
            self.card_pending.set_value(stats['pending_orders'])
            self.card_pending_amount.set_value(f"{int(stats['pending_amount']):,} تومان")
            self.card_low_stock.set_value(stats['low_stock'])
            self.card_debtors.set_value(stats['debtors'])

            # آخرین سفارشات
            self.db.cursor.execute('''
                SELECT o.invoice_number, o.order_date_shamsi,
                       c.first_name || " " || c.last_name,
                       o.final_amount, o.payment_status
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.created_at DESC
                LIMIT 8
            ''')
            orders = self.db.cursor.fetchall()
            self.orders_table.setRowCount(len(orders))
            for row, (inv, date, cust, amount, payment) in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(inv or ''))
                self.orders_table.setItem(row, 1, QTableWidgetItem(date or ''))
                self.orders_table.setItem(row, 2, QTableWidgetItem(cust or ''))
                amt_item = QTableWidgetItem(f"{int(amount or 0):,}")
                amt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.orders_table.setItem(row, 3, amt_item)
                pay_item = QTableWidgetItem("✅ پرداخت‌شده" if payment == 'paid' else "❌ پرداخت‌نشده")
                if payment == 'paid':
                    pay_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
                else:
                    pay_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
                self.orders_table.setItem(row, 4, pay_item)

            # کالاهای کم‌موجودی
            self.db.cursor.execute(
                'SELECT p.name, pv.color, pv.size, pv.stock, p.min_stock_alert '
                'FROM product_variants pv '
                'JOIN products p ON p.id = pv.product_id '
                'WHERE pv.stock <= p.min_stock_alert '
                'ORDER BY pv.stock ASC LIMIT 10'
            )
            alerts = self.db.cursor.fetchall()
            self.alerts_table.setRowCount(len(alerts))
            if alerts:
                for row, (name, color, size, stock, min_alert) in enumerate(alerts):
                    self.alerts_table.setItem(row, 0, QTableWidgetItem(name or ''))
                    self.alerts_table.setItem(row, 1, QTableWidgetItem(f"{color} / {size}"))
                    stock_item = QTableWidgetItem(str(stock))
                    stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if stock == 0:
                        stock_item.setBackground(QBrush(QColor("#FFE0E0")))
                        stock_item.setForeground(QBrush(QColor(ModernStyle.DANGER)))
                    else:
                        stock_item.setBackground(QBrush(QColor("#FFF3E0")))
                        stock_item.setForeground(QBrush(QColor(ModernStyle.WARNING)))
                    self.alerts_table.setItem(row, 2, stock_item)
                    min_item = QTableWidgetItem(str(min_alert))
                    min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.alerts_table.setItem(row, 3, min_item)
            else:
                self.alerts_table.setRowCount(1)
                ok_item = QTableWidgetItem("✅ تمام کالاها موجودی کافی دارند")
                ok_item.setForeground(QBrush(QColor(ModernStyle.SUCCESS)))
                self.alerts_table.setItem(0, 0, ok_item)

        except Exception as e:
            print(f"Dashboard error: {e}")
