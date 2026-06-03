import sqlite3
import os
from datetime import datetime
import jdatetime
from PyQt6.QtCore import QObject, pyqtSignal


class DatabaseManager(QObject):
    data_changed = pyqtSignal()

    def __init__(self, db_path="database/clothing_erp.db"):
        super().__init__()
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                parent_id INTEGER,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT NOT NULL,
                category_id INTEGER,
                fabric_type TEXT,
                model TEXT,
                description TEXT,
                image BLOB,
                min_stock_alert INTEGER DEFAULT 10,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                color TEXT NOT NULL,
                size TEXT NOT NULL,
                stock INTEGER DEFAULT 0,
                price REAL DEFAULT 0,
                barcode TEXT,
                UNIQUE(product_id, color, size),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                mobile TEXT,
                phone TEXT,
                address TEXT,
                shaba TEXT,
                account_number TEXT,
                debt REAL DEFAULT 0,
                credit REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                order_date_shamsi TEXT,
                total_amount REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                final_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                variant_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (variant_id) REFERENCES product_variants(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                reference_number TEXT,
                account_number TEXT,
                transaction_date TEXT NOT NULL,
                transaction_date_shamsi TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutting_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_number TEXT UNIQUE NOT NULL,
                cutter_name TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                fabric_type TEXT NOT NULL,
                total_weight REAL,
                total_length REAL,
                total_units INTEGER,
                record_date TEXT NOT NULL,
                record_date_shamsi TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutting_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                color TEXT NOT NULL,
                roll_weight REAL,
                length REAL,
                units INTEGER,
                notes TEXT,
                FOREIGN KEY (record_id) REFERENCES cutting_records(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                backup_date TEXT NOT NULL,
                backup_type TEXT,
                size_mb REAL
            )
        ''')

        # ایندکس‌ها برای بهبود سرعت کوئری‌ها
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date_shamsi)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id)')

        self.conn.commit()
        self.insert_default_settings()
        self.insert_default_categories()

    def insert_default_settings(self):
        defaults = [
            ('brand_name', 'برند پوشاک من'),
            ('brand_address', 'تهران، بازار بزرگ'),
            ('phone', '021-12345678'),
            ('mobile', '09123456789'),
            ('invoice_footer', 'با تشکر از خرید شما - لطفاً فاکتور خود را نزد خود نگه دارید'),
            ('logo_path', ''),
            ('theme', 'light'),
            ('font_family', 'Tahoma'),
            ('font_size', '10'),
            ('backup_drive1', 'D:\\'),
            ('backup_drive2', 'E:\\'),
            ('backup_reminder_days', '7'),
            ('account_number', 'IR123456789012345678901234'),
            ('account_holder', 'شرکت پوشاک'),
            ('invoice_person', 'مدیر فروش')
        ]
        self.cursor.executemany(
            'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
            defaults
        )
        self.conn.commit()

    def insert_default_categories(self):
        defaults = ['تیشرت', 'پیراهن', 'شلوار', 'مانتو', 'کت', 'سویشرت', 'هودی']
        for cat in defaults:
            self.cursor.execute(
                'INSERT OR IGNORE INTO categories (name) VALUES (?)',
                (cat,)
            )
        self.conn.commit()

    def get_setting(self, key):
        self.cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
        result = self.cursor.fetchone()
        return result[0] if result else ''

    def set_setting(self, key, value):
        self.cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, value)
        )
        self.conn.commit()
        self.data_changed.emit()

    def get_shamsi_date(self):
        return jdatetime.datetime.now().strftime('%Y/%m/%d')

    def get_shamsi_datetime(self):
        return jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    # ============ گزارش‌گیری ============

    def get_monthly_sales(self, year=None):
        """فروش ماهانه سال جاری شمسی"""
        if year is None:
            year = jdatetime.datetime.now().year
        result = []
        months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        for m in range(1, 13):
            prefix = f"{year}/{m:02d}"
            self.cursor.execute(
                "SELECT COALESCE(SUM(final_amount),0), COUNT(*) FROM orders "
                "WHERE order_date_shamsi LIKE ? AND status != 'cancelled'",
                (f"{prefix}%",)
            )
            amount, count = self.cursor.fetchone()
            result.append({'month': months[m - 1], 'amount': amount, 'count': count})
        return result

    def get_top_products(self, limit=10):
        """پرفروش‌ترین محصولات"""
        self.cursor.execute('''
            SELECT p.name, SUM(oi.quantity) as total_qty, SUM(oi.total_price) as total_revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status != 'cancelled'
            GROUP BY p.id
            ORDER BY total_qty DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_top_customers(self, limit=10):
        """مشتریان برتر بر اساس خرید"""
        self.cursor.execute('''
            SELECT c.first_name || ' ' || c.last_name, c.mobile,
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.final_amount), 0) as total_paid
            FROM customers c
            LEFT JOIN orders o ON o.customer_id = c.id AND o.status != 'cancelled'
            GROUP BY c.id
            ORDER BY total_paid DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_inventory_report(self):
        """گزارش موجودی انبار"""
        self.cursor.execute('''
            SELECT p.code, p.name, cat.name, pv.color, pv.size,
                   pv.stock, pv.price, p.min_stock_alert,
                   CASE WHEN pv.stock <= p.min_stock_alert THEN 'کم' ELSE 'کافی' END as stock_status
            FROM product_variants pv
            JOIN products p ON p.id = pv.product_id
            LEFT JOIN categories cat ON cat.id = p.category_id
            ORDER BY pv.stock ASC
        ''')
        return self.cursor.fetchall()

    def get_low_stock_count(self):
        """تعداد کالاهای کم‌موجودی"""
        self.cursor.execute(
            'SELECT COUNT(*) FROM product_variants pv '
            'JOIN products p ON p.id = pv.product_id '
            'WHERE pv.stock <= p.min_stock_alert'
        )
        return self.cursor.fetchone()[0]

    def get_dashboard_stats(self):
        """آمار کلی برای داشبورد"""
        today = jdatetime.datetime.now().strftime('%Y/%m/%d')

        self.cursor.execute('SELECT COUNT(*) FROM products')
        products = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM customers')
        customers = self.cursor.fetchone()[0]

        self.cursor.execute(
            'SELECT COUNT(*), COALESCE(SUM(final_amount),0) FROM orders WHERE order_date_shamsi=?',
            (today,)
        )
        today_orders, today_revenue = self.cursor.fetchone()

        self.cursor.execute(
            "SELECT COUNT(*), COALESCE(SUM(final_amount),0) FROM orders WHERE status='pending'"
        )
        pending_orders, pending_amount = self.cursor.fetchone()

        low_stock = self.get_low_stock_count()

        self.cursor.execute(
            "SELECT COUNT(*) FROM customers WHERE debt > credit"
        )
        debtors = self.cursor.fetchone()[0]

        return {
            'products': products,
            'customers': customers,
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'pending_orders': pending_orders,
            'pending_amount': pending_amount,
            'low_stock': low_stock,
            'debtors': debtors,
        }

    def get_financial_summary(self):
        """خلاصه مالی کل کسب‌وکار"""        
        self.cursor.execute("SELECT COALESCE(SUM(final_amount),0) FROM orders WHERE status != 'cancelled'")
        total_sales = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(debt),0), COALESCE(SUM(credit),0) FROM customers")
        total_debt, total_credit = self.cursor.fetchone()

        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE payment_status='unpaid' AND status != 'cancelled'")
        unpaid_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(final_amount),0) FROM orders WHERE payment_status='unpaid' AND status != 'cancelled'")
        unpaid_amount = self.cursor.fetchone()[0]

        return {
            'total_sales': total_sales,
            'total_debt': total_debt,
            'total_credit': total_credit,
            'net_receivable': total_debt - total_credit,
            'unpaid_orders': unpaid_count,
            'unpaid_amount': unpaid_amount,
        }

    def search_orders(self, query='', status=None, payment_status=None):
        """جستجوی پیشرفته در سفارشات"""
        sql = '''
            SELECT o.id, o.invoice_number, c.first_name || ' ' || c.last_name,
                   o.order_date_shamsi, o.final_amount, o.status, o.payment_status
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            WHERE 1=1
        '''
        params = []
        if query:
            sql += " AND (o.invoice_number LIKE ? OR c.first_name LIKE ? OR c.last_name LIKE ?)"
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        if status:
            sql += " AND o.status = ?"
            params.append(status)
        if payment_status:
            sql += " AND o.payment_status = ?"
            params.append(payment_status)
        sql += " ORDER BY o.created_at DESC"
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
