#!/usr/bin/env python3

import os
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import (
    QPaintEvent,
    QPainter,
    QPen,
    QColor,
    QFontMetrics,
    QFont,
    QPainterPath,
    QLinearGradient
)
from PyQt5.QtWidgets import QAbstractButton


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
        self._color_border = None
        self.bordersize = 2
        self.state_pressed = False
        self.painter = None

        self._height = None

        self.setupUI()

    def setupUI(self):
        self.font = QFont("Nimbus Sans", 13)
        self.font_metric = QFontMetrics(self.font)
        self.setColorBorder(QColor("#1e1e1f"))
        self.painter = QPainter()

    def paintEvent(self, e: QPaintEvent) -> None:

        self.painter.begin(self)
        self.draw_square(event=e)
        self.draw_text()
        self.painter.end()

    def draw_text(self):
        if self.color_font():
            self.painter.setPen(QPen(self.color_font(), 1, Qt.SolidLine))
        else:
            self.painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        self.painter.setFont(self.font)
        self.painter.drawText((self.width() / 2) - (self.font_metric.width(self.text()) / 2),
                    (self.height() / 2) + self.font_metric.height() / 4,
                    self.text())

    def draw_square(self, event):
        self.painter.setRenderHint(QPainter.Antialiasing)
        # Create the path
        path = QPainterPath()

        if not self.state_pressed:
            gradient = QLinearGradient(0, 0, 0, self.height() * 5)
            gradient.setColorAt(0.0, Qt.white)
            gradient.setColorAt(0.06, self.color())
            gradient.setColorAt(0.7, Qt.black)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height() * 5)
            gradient.setColorAt(0.0, Qt.darkGray)
            gradient.setColorAt(0.06, self.color())
            gradient.setColorAt(0.95, Qt.white)

        # Set painter colors to given values.
        pen = QPen(self.color_border(), self.bordersize)
        self.painter.setPen(pen)
        self.painter.setBrush(gradient)

        rect = QRectF(event.rect())
        # Slighly shrink dimensions to account for bordersize.
        rect.adjust(self.bordersize / 2, self.bordersize / 2, -self.bordersize / 2, -self.bordersize / 2)

        # Add the rect to path.
        path.addRoundedRect(rect, 14, 14)
        self.painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        self.painter.fillPath(path, self.painter.brush())
        self.painter.strokePath(path, self.painter.pen())

        # TExt is use a drop shadow
        self.painter.drawText(rect, Qt.AlignCenter, self.text())

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

    def setColorBorder(self, color_border):
        if color_border != self._color_border:
            self._color_border = color_border

    def color_border(self):
        return self._color_border

    def mousePressEvent(self, e):
        self.state_pressed = True
        self.update()
        return super(CalculatorButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.state_pressed = False
        self.update()
        return super(CalculatorButton, self).mouseReleaseEvent(e)


