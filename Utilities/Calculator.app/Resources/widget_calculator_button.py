#!/usr/bin/env python3

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QBrush, QFontMetrics, QFont
from PyQt5.QtWidgets import QColorDialog, QVBoxLayout, QAbstractButton


class CalculatorButton(QAbstractButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, text=None, **kwargs):
        super(CalculatorButton, self).__init__(*args, **kwargs)

        self._text = text
        self._color = None
        self._color_font = None

        self._height = None
        # self.pressed.connect(self.onColorPicker)

        self.setupUI()

    def setupUI(self):
        self.font = QFont("Nimbus Sans", 13)
        self.font_metric = QFontMetrics(self.font)

        # self.setFixedHeight(self._height)
        # self.setFixedWidth(self._height)

        # layout = QVBoxLayout()
        # self.setLayout(layout)

    def paintEvent(self, e: QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        self.draw_square(qp)
        self.draw_text(qp)
        qp.end()

    def draw_text(self, qp):
        if self.color_font():
            qp.setPen(QPen(self.color_font(), 1, Qt.SolidLine))
        else:
            qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        qp.setFont(self.font)
        qp.drawText((self.width() / 2) - (self.font_metric.width(self.text()) / 2),
                    (self.height() / 2) + self.font_metric.height() / 4,
                    self.text())

    def draw_square(self, qp):

        pen_size = 1
        pen_size_half = pen_size / 2

        qp.setPen(QPen(Qt.black, pen_size, Qt.SolidLine, Qt.RoundCap))
        if self.color():
            qp.setBrush(QBrush(self.color(), Qt.SolidPattern))
        qp.drawRect(pen_size_half, pen_size_half, self.width() - pen_size, self.height() - pen_size)

    def setText(self, text):
        if text != self._text:
            self._text = text
            # self.textChanged.emit(self._text)

    def text(self):
        return self._text

    def setColor(self, color):
        if color != self._color:
            self._color = color
            # self.textChanged.emit(self._text)

    def color(self):
        return self._color

    def setColorFont(self, color_font):
        if color_font != self._color_font:
            self._color_font = color_font
            # self.textChanged.emit(self._text)

    def color_font(self):
        return self._color_font

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        # if e.button() == Qt.RightButton:
        #     self.setColor(self._default)

        return super(CalculatorButton, self).mousePressEvent(e)
