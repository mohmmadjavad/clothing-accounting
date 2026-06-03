import os
import shutil
import sqlite3
from datetime import datetime
import jdatetime
from PyQt6.QtCore import QObject, pyqtSignal


class BackupManager(QObject):
    backup_completed = pyqtSignal(str)
    backup_failed = pyqtSignal(str)

    def __init__(self, db_path="database/clothing_erp.db"):
        super().__init__()
        self.db_path = db_path
        self.backup_drives = []
        self.max_backups = 10  # افزایش از ۳ به ۱۰ برای امنیت بیشتر

    def set_backup_drives(self, drive1, drive2):
        self.backup_drives = []
        if drive1 and os.path.exists(drive1):
            self.backup_drives.append(drive1)
        if drive2 and os.path.exists(drive2):
            self.backup_drives.append(drive2)

    def create_backup(self):
        """ایجاد بکاپ در تمام درایوهای تنظیم شده"""
        success = False

        if not self.backup_drives:
            self.backup_failed.emit("هیچ درایوی برای بکاپ تنظیم نشده است")
            return False

        timestamp = jdatetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"clothing_erp_backup_{timestamp}.db"

        for drive in self.backup_drives:
            try:
                backup_dir = os.path.join(drive, "ClothingERP_Backups")
                os.makedirs(backup_dir, exist_ok=True)

                full_path = os.path.join(backup_dir, backup_name)
                shutil.copy2(self.db_path, full_path)
                self.log_backup(full_path)
                self.clean_old_backups(backup_dir)
                self.backup_completed.emit(full_path)
                success = True

            except Exception as e:
                self.backup_failed.emit(f"خطا در بکاپ‌گیری از {drive}: {str(e)}")

        return success

    def clean_old_backups(self, backup_dir):
        """نگه داشتن فقط ۳ بکاپ آخر"""
        try:
            backups = []
            for file in os.listdir(backup_dir):
                if file.startswith("clothing_erp_backup_") and file.endswith(".db"):
                    full_path = os.path.join(backup_dir, file)
                    backups.append((full_path, os.path.getmtime(full_path)))

            backups.sort(key=lambda x: x[1], reverse=True)

            for backup_path, _ in backups[self.max_backups:]:
                try:
                    os.remove(backup_path)
                except Exception as e:
                    print(f"خطا در حذف بکاپ قدیمی: {e}")

        except Exception as e:
            print(f"خطا در پاکسازی بکاپ‌ها: {e}")

    def log_backup(self, backup_path):
        """ثبت بکاپ در دیتابیس"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            cursor.execute(
                'INSERT INTO backup_log (backup_path, backup_date, backup_type, size_mb) VALUES (?, ?, ?, ?)',
                (backup_path, jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 'auto', round(size_mb, 2))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطا در لاگ بکاپ: {e}")

    def should_remind_backup(self, reminder_days=7):
        """بررسی نیاز به یادآوری بکاپ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT backup_date FROM backup_log ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()

            if not result:
                return True

            last_backup_str = result[0]
            try:
                parts = last_backup_str.split(' ')[0].split('/')
                year, month, day = map(int, parts)
                last_backup_date = jdatetime.date(year, month, day).togregorian()
                today = jdatetime.date.today().togregorian()
                days_passed = (today - last_backup_date).days
                return days_passed >= reminder_days
            except Exception:
                return True

        except Exception as e:
            print(f"خطا در بررسی بکاپ: {e}")
            return False

    def restore_backup(self, backup_path):
        """بازیابی از یک فایل بکاپ"""        
        import shutil
        import sqlite3
        try:
            # اعتبارسنجی فایل بکاپ
            test_conn = sqlite3.connect(backup_path)
            test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
            # کپی به مسیر اصلی
            shutil.copy2(backup_path, self.db_path)
            self.backup_completed.emit(f"بازیابی موفق از: {backup_path}")
            return True
        except Exception as e:
            self.backup_failed.emit(f"خطا در بازیابی: {str(e)}")
            return False

    def get_backup_info(self):
        """دریافت اطلاعات بکاپ‌های موجود"""
        try:
            backups_info = []
            for drive in self.backup_drives:
                backup_dir = os.path.join(drive, "ClothingERP_Backups")
                if os.path.exists(backup_dir):
                    for file in os.listdir(backup_dir):
                        if file.endswith(".db"):
                            full_path = os.path.join(backup_dir, file)
                            size_mb = os.path.getsize(full_path) / (1024 * 1024)
                            mtime = os.path.getmtime(full_path)
                            backups_info.append({
                                'path': full_path,
                                'name': file,
                                'size': round(size_mb, 2),
                                'date': datetime.fromtimestamp(mtime)
                            })

            backups_info.sort(key=lambda x: x['date'], reverse=True)
            return backups_info[:self.max_backups]

        except Exception as e:
            print(f"خطا در دریافت اطلاعات بکاپ: {e}")
            return []
