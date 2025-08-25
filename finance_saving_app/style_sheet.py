from PyQt5 import QtWidgets


def light_style(main_widget: QtWidgets.QWidget) -> str:
    """
    Returns a light, neutral color scheme.
    Includes QPushButton, QLineEdit, QTabs, and QGroupBox.
    """
    return f"""
        /* Main container only */
        #{main_widget.objectName()} {{
            background-color: rgb(205, 205, 205);  /* Slightly darker than rest */
            color: rgb(60, 30, 50);
        }}
        QWidget {{
            background-color: rgb(225, 225, 225);  /* Light gray background */
            color: rgb(30, 30, 30);                /* Dark text */
        }}
        QPushButton {{
            background-color: rgb(230, 230, 230);
            color: rgb(30, 30, 30);
            border: 1px solid rgb(180, 180, 180);
            padding: 5px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background-color: rgb(210, 225, 240);
            border: 1px solid rgb(140, 170, 200);
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: rgb(255, 255, 255);
            color: rgb(30, 30, 30);
            border: 1px solid rgb(180, 180, 180);
        }}
        QLabel {{
            color: rgb(30, 30, 30);
        }}
        QTabWidget::pane {{
            border: 1px solid rgb(180, 180, 180);
            background: rgb(245, 245, 245);
        }}
        QTabBar::tab {{
            background: rgb(230, 230, 230);
            color: rgb(30, 30, 30);
            padding: 6px 10px;
            border: 1px solid rgb(180, 180, 180);
            border-bottom: none; /* merge with content */
            min-width: 80px;
        }}
        QTabBar::tab:selected {{
            background: rgb(210, 225, 240);
            border-color: rgb(140, 170, 200);
            color: rgb(0, 0, 0);
        }}
        QTabBar::tab:hover:!selected {{
            background: rgb(240, 240, 240);
        }}
        QGroupBox {{
            border: 1px solid rgb(180, 180, 180);
            margin-top: 12px; /* space for the title text */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px; /* horizontal padding around title */
        }}
    """


def dark_style(main_widget: QtWidgets.QWidget) -> str:
    """
    Returns a dark, Maya-inspired color scheme using RGB values.
    Includes QPushButton, QLineEdit, QTabs, and QGroupBox.
    """
    return f"""
        /* Main container only */
        #{main_widget.objectName()} {{
            background-color: rgb(42, 42, 42);  /* Slightly darker than rest */
            color: rgb(60, 30, 50);
        }}
        QWidget {{
            background-color: rgb(52, 52, 52);  /* Maya dark gray */
            color: rgb(200, 200, 200);          /* Soft light text */
        }}
        QPushButton {{
            background-color: rgb(55, 55, 55);
            color: rgb(210, 210, 210);
            border: 1px solid rgb(80, 80, 80);
            padding: 5px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background-color: rgb(70, 100, 130);
            border: 1px solid rgb(100, 130, 160);
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: rgb(60, 60, 60);
            color: rgb(230, 230, 230);
            border: 1px solid rgb(80, 80, 80);
        }}
        QLabel {{
            color: rgb(200, 200, 200);
        }}
        QTabWidget::pane {{
            border: 1px solid rgb(80, 80, 80);
            background: rgb(42, 42, 42);
        }}
        QTabBar::tab {{
            background: rgb(55, 55, 55);
            color: rgb(210, 210, 210);
            padding: 6px 10px;
            border: 1px solid rgb(80, 80, 80);
            border-bottom: none; /* merge with content */
            min-width: 80px;
        }}
        QTabBar::tab:selected {{
            background: rgb(70, 100, 130);
            border-color: rgb(100, 130, 160);
            color: rgb(240, 240, 240);
        }}
        QTabBar::tab:hover:!selected {{
            background: rgb(65, 65, 65);
        }}
        QGroupBox {{
            border: 1px solid rgb(80, 80, 80);
            margin-top: 12px; /* space for the title text */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px; /* horizontal padding around title */
        }}
    """


def pink_style(main_widget: QtWidgets.QWidget) -> str:
    """
    Returns a soft pink-themed color scheme.
    Includes QPushButton, QLineEdit, QTabs, and QGroupBox.
    """
    return f"""
        /* Main container only */
        #{main_widget.objectName()} {{
            background-color: rgb(245, 230, 235);  /* Slightly darker than rest */
            color: rgb(60, 30, 50);
        }}
        QWidget {{
            background-color: rgb(255, 245, 248);  /* Lighter pink for child widgets */
            color: rgb(60, 30, 50);
        }}
        QPushButton {{
            background-color: rgb(255, 220, 230);
            color: rgb(60, 30, 50);
            border: 1px solid rgb(200, 150, 170);
            padding: 5px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: rgb(255, 200, 215);
            border: 1px solid rgb(190, 120, 150);
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: rgb(255, 250, 252);
            color: rgb(60, 30, 50);
            border: 1px solid rgb(200, 150, 170);
        }}
        QLabel {{
            color: rgb(60, 30, 50);
        }}
        QTabWidget::pane {{
            border: 1px solid rgb(200, 150, 170);
            background: rgb(255, 245, 248);
        }}
        QTabBar::tab {{
            background: rgb(255, 220, 230);
            color: rgb(60, 30, 50);
            padding: 6px 10px;
            border: 1px solid rgb(200, 150, 170);
            border-bottom: none;
            min-width: 80px;
        }}
        QTabBar::tab:selected {{
            background: rgb(255, 180, 200);
            border-color: rgb(190, 120, 150);
            color: rgb(40, 20, 35);
        }}
        QTabBar::tab:hover:!selected {{
            background: rgb(255, 200, 215);
        }}
        QGroupBox {{
            border: 1px solid rgb(200, 150, 170);
            margin-top: 12px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px;
        }}
    """
