class ModernStyle:
    # رنگ‌های اصلی
    PRIMARY = "#6C5CE7"
    PRIMARY_DARK = "#5A4BD1"
    PRIMARY_LIGHT = "#A29BFE"
    SECONDARY = "#00CEC9"
    ACCENT = "#FD79A8"
    SUCCESS = "#00B894"
    WARNING = "#FDCB6E"
    DANGER = "#E17055"
    INFO = "#74B9FF"

    # رنگ‌های پس‌زمینه
    BG_LIGHT = "#F5F6FA"
    BG_WHITE = "#FFFFFF"
    BG_DARK = "#2D3436"
    BG_DARK_SECONDARY = "#353B48"

    # رنگ‌های متن
    TEXT_PRIMARY = "#2D3436"
    TEXT_SECONDARY = "#636E72"
    TEXT_LIGHT = "#B2BEC3"
    TEXT_WHITE = "#FFFFFF"
    TEXT_BLACK = "#000000"

    # رنگ‌های مرزی
    BORDER = "#DFE6E9"
    BORDER_LIGHT = "#E9ECEF"
    BORDER_DARK = "#B2BEC3"

    @staticmethod
    def get_main_stylesheet():
        return f"""
        QMainWindow {{
            background-color: {ModernStyle.BG_LIGHT};
        }}

        QWidget {{
            font-family: 'Tahoma', 'IRANSans', 'Segoe UI', sans-serif;
            color: {ModernStyle.TEXT_PRIMARY};
            font-size: 12px;
        }}

        QMenuBar {{
            background-color: {ModernStyle.BG_WHITE};
            border-bottom: 2px solid {ModernStyle.BORDER};
            padding: 4px;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QMenuBar::item {{
            padding: 8px 16px;
            border-radius: 8px;
            margin: 2px 4px;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QMenuBar::item:selected {{
            background: {ModernStyle.PRIMARY};
            color: white;
        }}

        QPushButton {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: bold;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {ModernStyle.PRIMARY_DARK};
        }}

        QPushButton:pressed {{
            background-color: {ModernStyle.PRIMARY};
            padding: 9px 23px;
        }}

        QPushButton:disabled {{
            background-color: {ModernStyle.BORDER};
            color: {ModernStyle.TEXT_LIGHT};
        }}

        QPushButton#dangerBtn {{
            background-color: {ModernStyle.DANGER};
            color: white;
        }}

        QPushButton#successBtn {{
            background-color: {ModernStyle.SUCCESS};
            color: white;
        }}

        QPushButton#warningBtn {{
            background-color: {ModernStyle.WARNING};
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QPushButton#secondaryBtn {{
            background-color: transparent;
            color: {ModernStyle.PRIMARY};
            border: 2px solid {ModernStyle.PRIMARY};
        }}

        QPushButton#secondaryBtn:hover {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}

        QLabel {{
            color: {ModernStyle.TEXT_PRIMARY};
            background: transparent;
            border: none;
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 10px;
            padding: 10px 14px;
            background-color: {ModernStyle.BG_WHITE};
            font-size: 13px;
            color: {ModernStyle.TEXT_PRIMARY};
            selection-background-color: {ModernStyle.PRIMARY};
            selection-color: white;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {ModernStyle.PRIMARY};
            background-color: #FAFAFF;
        }}

        QTableWidget {{
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 10px;
            background-color: {ModernStyle.BG_WHITE};
            gridline-color: {ModernStyle.BORDER_LIGHT};
            font-size: 12px;
            color: {ModernStyle.TEXT_PRIMARY};
            alternate-background-color: #F8F9FC;
        }}

        QTableWidget::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {ModernStyle.BORDER_LIGHT};
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QTableWidget::item:selected {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}

        QTableWidget::item:hover {{
            background-color: #F0EEFF;
        }}

        QHeaderView::section {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
            padding: 12px 8px;
            border: none;
            font-weight: bold;
            font-size: 13px;
        }}

        QFrame#card {{
            background-color: {ModernStyle.BG_WHITE};
            border-radius: 16px;
            border: 1px solid {ModernStyle.BORDER};
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QFrame#card:hover {{
            border-color: {ModernStyle.PRIMARY_LIGHT};
        }}

        QGroupBox {{
            background-color: {ModernStyle.BG_WHITE};
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            padding-top: 35px;
            font-weight: bold;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            color: {ModernStyle.PRIMARY};
            font-weight: bold;
        }}

        QTabWidget::pane {{
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 12px;
            background: {ModernStyle.BG_WHITE};
            padding: 15px;
            top: -1px;
        }}

        QTabBar::tab {{
            background: {ModernStyle.BG_LIGHT};
            color: {ModernStyle.TEXT_PRIMARY};
            padding: 10px 24px;
            margin: 2px 4px;
            border-radius: 10px 10px 0 0;
            font-size: 13px;
            border: 1px solid {ModernStyle.BORDER};
            border-bottom: none;
        }}

        QTabBar::tab:selected {{
            background: {ModernStyle.BG_WHITE};
            color: {ModernStyle.PRIMARY};
            font-weight: bold;
            border-bottom: 2px solid {ModernStyle.PRIMARY};
        }}

        QTabBar::tab:hover {{
            background: #F0EEFF;
        }}

        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: {ModernStyle.BORDER_DARK};
            border-radius: 5px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {ModernStyle.PRIMARY_LIGHT};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QComboBox {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 10px;
            padding: 10px 14px;
            background: {ModernStyle.BG_WHITE};
            font-size: 13px;
            min-width: 100px;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QComboBox:hover {{
            border-color: {ModernStyle.PRIMARY_LIGHT};
        }}

        QComboBox:focus {{
            border-color: {ModernStyle.PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            padding: 0px 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {ModernStyle.BG_WHITE};
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 8px;
            color: {ModernStyle.TEXT_PRIMARY};
            selection-background-color: {ModernStyle.PRIMARY};
            selection-color: white;
        }}

        QSpinBox, QDoubleSpinBox {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 10px;
            padding: 10px;
            background: {ModernStyle.BG_WHITE};
            font-size: 13px;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {ModernStyle.PRIMARY};
        }}

        QCheckBox, QRadioButton {{
            color: {ModernStyle.TEXT_PRIMARY};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 4px;
            background: white;
        }}

        QCheckBox::indicator:checked {{
            background: {ModernStyle.PRIMARY};
            border-color: {ModernStyle.PRIMARY};
        }}

        QProgressBar {{
            border: none;
            border-radius: 8px;
            background-color: {ModernStyle.BORDER_LIGHT};
            text-align: center;
            font-weight: bold;
            height: 10px;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QProgressBar::chunk {{
            background-color: {ModernStyle.PRIMARY};
            border-radius: 8px;
        }}

        QDateEdit {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 10px;
            padding: 10px;
            background: white;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QListWidget {{
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 10px;
            background: white;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {ModernStyle.BORDER_LIGHT};
        }}

        QListWidget::item:selected {{
            background: {ModernStyle.PRIMARY};
            color: white;
        }}

        QTreeWidget {{
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 10px;
            background: white;
            color: {ModernStyle.TEXT_PRIMARY};
        }}

        QTreeWidget::item {{
            padding: 6px;
        }}

        QTreeWidget::item:selected {{
            background: {ModernStyle.PRIMARY};
            color: white;
        }}

        QSplitter::handle {{
            background: {ModernStyle.BORDER};
            width: 2px;
        }}

        QToolTip {{
            background: {ModernStyle.TEXT_PRIMARY};
            color: white;
            border: none;
            padding: 8px;
            border-radius: 6px;
            font-size: 11px;
        }}

        QStatusBar {{
            background: {ModernStyle.BG_WHITE};
            border-top: 1px solid {ModernStyle.BORDER};
            color: {ModernStyle.TEXT_SECONDARY};
            font-size: 12px;
        }}
        """

    @staticmethod
    def get_dark_stylesheet():
        return f"""
        QMainWindow {{
            background-color: {ModernStyle.BG_DARK};
        }}

        QWidget {{
            color: {ModernStyle.TEXT_WHITE};
            font-family: 'Tahoma', 'Segoe UI', sans-serif;
        }}

        QLabel {{
            color: #E0E0E0;
            background: transparent;
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
            border-color: #4A5568;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {ModernStyle.PRIMARY_LIGHT};
        }}

        QFrame#card {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            border-color: #4A5568;
        }}

        QTableWidget {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            border-color: #4A5568;
            color: white;
            gridline-color: #4A5568;
        }}

        QTableWidget::item {{
            color: white;
        }}

        QHeaderView::section {{
            background-color: {ModernStyle.PRIMARY_DARK};
            color: white;
        }}

        QComboBox {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
            border-color: #4A5568;
        }}

        QComboBox QAbstractItemView {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
        }}

        QTabBar::tab {{
            background-color: {ModernStyle.BG_DARK};
            color: #B0B0B0;
        }}

        QTabBar::tab:selected {{
            background: {ModernStyle.BG_DARK_SECONDARY};
            color: {ModernStyle.PRIMARY_LIGHT};
        }}

        QGroupBox {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            border-color: #4A5568;
            color: white;
        }}

        QMenuBar {{
            background-color: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
        }}

        QPushButton#secondaryBtn {{
            color: {ModernStyle.PRIMARY_LIGHT};
            border-color: {ModernStyle.PRIMARY_LIGHT};
        }}

        QStatusBar {{
            background: {ModernStyle.BG_DARK_SECONDARY};
            color: #B0B0B0;
        }}

        QSpinBox, QDoubleSpinBox {{
            background: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
            border-color: #4A5568;
        }}

        QTreeWidget {{
            background: {ModernStyle.BG_DARK_SECONDARY};
            color: white;
            border-color: #4A5568;
        }}
        """
