#!/usr/bin/env python3

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QBrush, QFontMetrics, QFont
from PyQt5.QtWidgets import QColorDialog, QVBoxLayout, QAbstractButton


class ColorButton(QAbstractButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self._height = None
        self.pressed.connect(self.onColorPicker)
        self.setColor(self._default)

        self.setupUI()

    def setupUI(self):
        font = QFont()
        font_metric = QFontMetrics(font)
        self._height = font_metric.height()
        self.setFixedHeight(self._height)
        self.setFixedWidth(self._height)

        layout = QVBoxLayout()
        self.setLayout(layout)

    def paintEvent(self, e: QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        self.draw_square(qp)
        qp.end()

    def draw_square(self, qp):
        spacing = int(self._height * 0.45)
        pen_size = 1

        qp.setPen(QPen(Qt.gray, pen_size))
        qp.drawRect(0, 0, self._height - pen_size, self._height - pen_size)

        qp.setPen(QPen(Qt.gray, pen_size))
        qp.setBrush(QBrush(QColor(self._color), Qt.SolidPattern))
        qp.drawRect(spacing / 2, spacing / 2, self._height - pen_size - spacing, self._height - pen_size - spacing)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

    def color(self):
        return self._color

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
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)
