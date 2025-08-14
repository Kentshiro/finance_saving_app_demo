from PyQt5 import QtWidgets, QtGui, QtCore


class CollapsibleHeader(QtWidgets.QWidget):
    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")

    clicked = QtCore.pyqtSignal()

    def __init__(self, text, parent=None):
        super(CollapsibleHeader, self).__init__(parent)

        self._expanded = False  # ✅ Safely define this before usage
        self.setAutoFillBackground(True)
        self.set_background_color(None)

        self.icon_label = QtWidgets.QLabel()
        if not self.COLLAPSED_PIXMAP.isNull():
            self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(6)

        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        self.set_text(text)
        self.set_expanded(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )

    def set_text(self, text):
        self.text_label.setText(f"<b>{text}</b>")

    def set_background_color(self, color=None):
        if color is None:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        elif isinstance(color, tuple) and len(color) == 3:
            color = QtGui.QColor(*color)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded
        pixmap = self.EXPANDED_PIXMAP if expanded else self.COLLAPSED_PIXMAP
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()
        super().mouseReleaseEvent(event)


class CollapsibleWidget(QtWidgets.QWidget):
    def __init__(self, text, parent=None, window=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.tool_window = window

        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)

        self.body_wdg = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setSpacing(1)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.addWidget(self.header_wdg)
        self.details_layout.addWidget(self.body_wdg)

        self.set_expanded(True)

    def add_widget(self, widget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)

    def set_expanded(self, expanded):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

    def set_header_background_color(self, color):
        self.header_wdg.set_background_color(color)

    def on_header_clicked(self):
        self.set_expanded(not self.header_wdg.is_expanded())
