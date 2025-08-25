from general import ICONS_DIR
from PyQt5 import QtCore, QtGui, QtWidgets


class CollapsibleWidget(QtWidgets.QWidget):
    # function that auto-starts up when CollapsibleHeader() is called
    def __init__(self, text, parent=None, window=None):
        super().__init__(parent)

        self.tool_window = window
        # calls for Header
        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)

        # Creates body widget for part below header
        self.body_wdg = QtWidgets.QWidget()

        # parents body layout to the body widget and sets spacing settings
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(
            4,
            2,
            4,
            2,
        )
        self.body_layout.setSpacing(3)

        # creates main layout to house header and the body widget
        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setSpacing(1)
        self.details_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.details_layout.addWidget(self.header_wdg)
        self.details_layout.addWidget(self.body_wdg)

        # set default states of collapsible widget
        self.set_expanded(True)

        # making addWidget function for class

    def add_widget(
        self,
        widget,
    ):
        self.body_layout.addWidget(widget)

        # making addLayout function for class

    def add_layout(
        self,
        layout,
    ):
        self.body_layout.addLayout(layout)

        # making setState function for class

    def set_expanded(
        self,
        expanded,
    ):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

        # making easy color change function to class

    def set_header_background_color(
        self,
        color,
    ):
        self.header_wdg.set_background_color(color)

        # sends signal

    def on_header_clicked(
        self,
    ):
        self.set_expanded(not self.header_wdg.is_expanded())

class CollapsibleHeader(QtWidgets.QWidget):

    clicked = QtCore.pyqtSignal()

    # function that auto-starts up when CollapsibleHeader() is called
    def __init__(self, text, parent=None):
        super().__init__(parent)
        collapsed_pixmap = QtGui.QPixmap(f"{ICONS_DIR}/right_arrow.png")
        expanded_pixmap = QtGui.QPixmap(f"{ICONS_DIR}/down_arrow.png")

        # Scale to 2/3 of original size
        self.collapsed_pixmap = collapsed_pixmap.scaled(
            collapsed_pixmap.width() * 2 // 3,
            collapsed_pixmap.height() * 2 // 3,
        )

        self.expanded_pixmap = expanded_pixmap.scaled(
            expanded_pixmap.width() * 2 // 3,
            expanded_pixmap.height() * 2 // 3,
        )

        # Creating a signal for clicking the header
        # need to set this or the header won't get color despite setting
        self.setAutoFillBackground(True)
        self.set_background_color(None)
        # icon that uses the arrow pngs' and setting width to width of png
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.collapsed_pixmap.width())
        # text label that uses text passes in function creation and enabling
        # mouse clicked on it
        self.text_label = QtWidgets.QLabel()
        self.color_spacer_left = QtWidgets.QWidget()
        self.color_spacer_left.setFixedWidth(5)
        self.color_spacer_right = QtWidgets.QWidget()
        self.color_spacer_right.setFixedWidth(5)
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # creating main layout and setting its margins, then adding all
        # previous widgets to the layout
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.main_layout.addWidget(self.color_spacer_left)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.color_spacer_right)

        self.main_layout.addWidget(self.text_label)

        # setting defaults, calling below functions
        self.set_text(text)
        self.set_expanded(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )

    # sets text label with passed text and formats it as bold
    def set_text(
        self,
        text,
    ):
        self.text_label.setText(f"<b>{text}</b>")

    # gets the background color from qpushbutton pallete which carries mayas
    # default grey
    def set_background_color(self, color=None):
        if color is None:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        elif isinstance(color, tuple) and len(color) == 3:
            color = QtGui.QColor(*color)

        css_color = color.name()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {css_color};
            }}
            QLabel, QPushButton {{
                background-color: {css_color};
            }}
        """)

    # returns or = if widget is expanded
    def is_expanded(
        self,
    ):
        return self._expanded

    # function that sets state of widget collapsed or expanded
    def set_expanded(
        self,
        expanded,
    ):
        self._expanded = expanded

        # changes the png arrow for either state
        if self._expanded:
            self.icon_label.setPixmap(self.expanded_pixmap)
        else:
            self.icon_label.setPixmap(self.collapsed_pixmap)

    # overrides mouseReleaseEvent to emit a signal
    def mouseReleaseEvent(
        self,
        event,
    ):
        self.clicked.emit()  # pylint: disable=E1101
