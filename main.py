import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from ui.main_window import MainWindow


def main():
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setApplicationName("مدیریت تولید پوشاک")
    app.setOrganizationName("ClothingERP")
    
    # ========== تنظیم آیکون برنامه ==========
    # پیدا کردن مسیر آیکون (هم در حالت عادی و هم در حالت EXE)
    if getattr(sys, 'frozen', False):
        # حالت EXE
        base_path = sys._MEIPASS
    else:
        # حالت توسعه (Python)
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_path, 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    # =======================================

    font = QFont("Tahoma", 10)
    app.setFont(font)

    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()