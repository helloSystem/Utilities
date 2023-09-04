#!/usr/bin/env python3

import os
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QSize
from PyQt5.QtGui import (
    QPaintEvent,
    QPainter,
    QPen,
    QColor,
    QFontMetrics,
    QFont,
    QPainterPath,
    QLinearGradient,

)
from PyQt5.QtWidgets import QAbstractButton, QSizePolicy


class CalculatorButton(QAbstractButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal(object)
    clicked = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(CalculatorButton, self).__init__(*args, **kwargs)

        self._text = kwargs.get("text") or None
        self._color = None
        self._font_color = None
        self._font_size = None
        self._border_color = None
        self._border_size = None
        self._border_pen = None

        self.__mouse_checked = False
        self.__mouse_over = False

        self.font = None
        self.font_metric = None
        self.painter = None


        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.font = QFont("Nimbus Sans", 11)
        self.font_metric = QFontMetrics(self.font)
        self.setBorderColor(QColor("#1e1e1f"))
        self.setBorderSize(2)
        self.setBorderPen(QPen(self.border_color(), self.border_size()))
        self.setMouseTracking(True)
        self.painter = QPainter()

    def minimumSizeHint(self):
        return QSize(
            self.font_metric.width(self.text()) + (self.border_size() * 2),
            self.font_metric.height() + (self.border_size() * 2)
        )

    # def sizeHint(self):
    #     return QSize(
    #         self.font_metric.width(self.text()) + (self.border_size() * 2),
    #         self.font_metric.height() + (self.border_size() * 2)
    #     )

    def paintEvent(self, e: QPaintEvent) -> None:

        self.painter.begin(self)
        self.draw_square(event=e)
        self.draw_text()
        self.painter.end()

    def draw_text(self):
        if self.text() not in ["cos", "cosh", "tan", "tanh", "sin", "sinh", "log", "Rad", "EE", "RN",
                               "2nd", "ln", "1/x"]:
            if self.font_color():
                self.painter.setPen(QPen(self.font_color(), 1, Qt.SolidLine))
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

        if not self.__mouse_checked:
            if self.__mouse_over:
                gradient = QLinearGradient(0, 0, 0, self.height() * 5)
                gradient.setColorAt(0.0, Qt.white)
                gradient.setColorAt(0.1, self.color())
                gradient.setColorAt(1.0, Qt.black)
            else:
                gradient = QLinearGradient(0, 0, 0, self.height() * 5)
                gradient.setColorAt(0.0, Qt.white)
                gradient.setColorAt(0.08, self.color())
                gradient.setColorAt(0.7, Qt.black)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height() * 5)
            gradient.setColorAt(0.0, Qt.lightGray)
            gradient.setColorAt(0.06, self.color())
            gradient.setColorAt(0.95, Qt.lightGray)

        # Set painter colors to given values.

        self.painter.setPen(self.border_pen())
        self.painter.setBrush(gradient)

        rect = QRectF(event.rect())
        # Slighly shrink dimensions to account for self.border_size().
        rect.adjust(self.border_size() / 2, self.border_size() / 2, -self.border_size() / 2, -self.border_size() / 2)

        # Add the rect to path.
        path.addRoundedRect(rect, 12, 12)
        self.painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        self.painter.fillPath(path, self.painter.brush())
        self.painter.strokePath(path, self.painter.pen())

        # Text is use a drop shadow
        self.painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        self.painter.setFont(self.font)
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

    def setFontColor(self, color):
        if color is None:
            color = Qt.black
        if color != self._font_color:
            self._font_color = color
            # self.textChanged.emit(self._text)

    def font_color(self):
        return self._font_color

    def setBorderColor(self, color):
        if color is None:
            color = Qt.gray
        if color != self._border_color:
            self._border_color = color

    def border_color(self):
        return self._border_color

    def setBorderSize(self, size):
        if size is None:
            size = 2
        if type(size) != int:
            raise TypeError("'size' must be  int type or None")
        if size != self._border_size:
            self._border_size = size

    def border_size(self):
        return self._border_size

    def setBorderPen(self, pen):
        if pen is None:
            pen = QPen(self.border_color(), self.border_size())
        if not isinstance(pen, QPen):
            raise TypeError("'pen' must be QPen instance or None")
        if pen != self._border_pen:
            self._border_pen = pen

    def border_pen(self):
        return self._border_pen

    def mousePressEvent(self, event):
        self.__mouse_checked = True
        self.update()

    def mouseReleaseEvent(self, event):
        self.__mouse_checked = False
        self.clicked.emit(True)
        self.update()

    def mouseMoveEvent(self, event):
        self.__mouse_over = True

    def leaveEvent(self, event):
        self.__mouse_over = False
