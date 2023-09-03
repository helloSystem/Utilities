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
    QImage,
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
        self.bordersize = 2
        self.outlineColor = QColor("#1e1e1f")
        self.state_pressed = False

        self._height = None

        self.button_1 = QImage(os.path.join(os.path.dirname(__file__), "button_1.png"))
        # self.pressed.connect(self.onColorPicker)

        self.setupUI()



    def setupUI(self):
        self.font = QFont("Nimbus Sans", 13)
        self.font_metric = QFontMetrics(self.font)

    def paintEvent(self, e: QPaintEvent) -> None:
        qp = QPainter()

        qp.begin(self)
        self.draw_square(qp, event=e)
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

    def draw_square(self, painter, event):
        painter.setRenderHint(QPainter.Antialiasing)
        # Create the path
        path = QPainterPath()

        if not self.state_pressed:
            gradient = QLinearGradient(0, 0, 0, self.height() * 3)
            gradient.setColorAt(0.0, Qt.white)
            gradient.setColorAt(0.06, self.color())
            gradient.setColorAt(0.94, Qt.black)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height() * 3)
            gradient.setColorAt(0.0, Qt.gray)
            gradient.setColorAt(0.06, self.color())
            gradient.setColorAt(0.94, Qt.lightGray)

        # Set painter colors to given values.
        pen = QPen(self.outlineColor, self.bordersize)
        painter.setPen(pen)
        painter.setBrush(gradient)

        rect = QRectF(event.rect())
        # Slighly shrink dimensions to account for bordersize.
        rect.adjust(self.bordersize / 2, self.bordersize / 2, -self.bordersize / 2, -self.bordersize / 2)

        # Add the rect to path.
        path.addRoundedRect(rect, 10, 10)
        painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())
        painter.drawText(rect, Qt.AlignCenter, self.text())

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

    def mousePressEvent(self, e):
        self.state_pressed = True
        self.update()
        return super(CalculatorButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.state_pressed = False
        self.update()
        return super(CalculatorButton, self).mouseReleaseEvent(e)


