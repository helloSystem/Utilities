#!/usr/bin/env python3

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
    Custom Qt Widget to show a colored button color.
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

        self.color_disable = QColor(Qt.lightGray)
        self.font_color_disable = QColor(Qt.lightGray)
        self.font_shadow_color_disable = QColor(Qt.darkGray)
        self.border_color_disable = QColor(Qt.lightGray)

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.font = QFont("Nimbus Sans", 13)
        self.font_metric = QFontMetrics(self.font)
        self.setBorderColor()
        self.setBorderSize(2)
        self.setBorderPen(QPen(self.border_color(), self.border_size()))
        self.setMouseTracking(True)
        self.painter = QPainter()

    def minimumSizeHint(self):
        return QSize(
            self.font_metric.width(self.text()) + (self.border_size() * 2),
            self.font_metric.height() + (self.border_size() * 2),
        )

    def paintEvent(self, e: QPaintEvent) -> None:
        self.painter.begin(self)
        self.draw_square(event=e)
        self.draw_text()
        self.painter.end()

    def draw_text(self):
        if self.text() not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            if self.isEnabled():
                if self.font_color():
                    self.painter.setPen(QPen(self.font_color(), 1, Qt.SolidLine))
                else:
                    self.painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            else:
                self.painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))

            self.painter.setFont(self.font)
            self.painter.drawText(
                (self.width() / 2) - (self.font_metric.width(self.text()) / 2),
                (self.height() / 2) + self.font_metric.height() / 4,
                self.text(),
            )

    def draw_square(self, event):
        self.painter.setRenderHint(QPainter.Antialiasing)
        # Create the path
        path = QPainterPath()
        if self.isEnabled():
            if not self.__mouse_checked:
                if self.__mouse_over:
                    gradient = QLinearGradient(0, 0, 0, self.height())
                    gradient.setColorAt(0.0, self.color().darker(110))
                    gradient.setColorAt(0.1, self.color().lighter(180))
                    gradient.setColorAt(0.15, self.color().lighter(140))
                    gradient.setColorAt(0.40, self.color().lighter(130))
                    gradient.setColorAt(0.45, self.color())
                    gradient.setColorAt(0.51, self.color().darker(110))
                    gradient.setColorAt(0.9, self.color().darker(120))
                    gradient.setColorAt(0.95, self.color().darker(180))
                    gradient.setColorAt(1.0, self.color().darker(160))
                else:
                    gradient = QLinearGradient(0, 0, 0, self.height())
                    gradient.setColorAt(0.0, self.color().darker(110))
                    gradient.setColorAt(0.1, self.color().lighter(190))
                    gradient.setColorAt(0.15, self.color().lighter(130))
                    gradient.setColorAt(0.40, self.color().lighter(120))
                    gradient.setColorAt(0.45, self.color())
                    gradient.setColorAt(0.51, self.color().darker(120))
                    gradient.setColorAt(0.9, self.color().darker(130))
                    gradient.setColorAt(0.95, self.color().darker(190))
                    gradient.setColorAt(1.0, self.color().darker(160))
            else:
                gradient = QLinearGradient(0, 0, 0, self.height())
                gradient.setColorAt(0.0, self.color().darker(110))
                gradient.setColorAt(0.1, self.color().darker(120))
                gradient.setColorAt(0.15, self.color().darker(110))
                gradient.setColorAt(0.40, self.color().darker(105))
                gradient.setColorAt(0.5, self.color())
                gradient.setColorAt(0.51, self.color().lighter(105))
                gradient.setColorAt(0.9, self.color().lighter(110))
                gradient.setColorAt(0.95, self.color().lighter(170))
                gradient.setColorAt(1.0, self.color().lighter(140))
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, self.color().darker(110))
            gradient.setColorAt(0.1, self.color().darker(120))
            gradient.setColorAt(0.15, self.color().darker(110))
            gradient.setColorAt(0.40, self.color().darker(105))
            gradient.setColorAt(0.5, self.color())
            gradient.setColorAt(0.51, self.color().lighter(105))
            gradient.setColorAt(0.9, self.color().lighter(110))
            gradient.setColorAt(0.95, self.color().lighter(170))
            gradient.setColorAt(1.0, self.color().lighter(140))

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
        if self.isEnabled():
            self.painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        else:
            self.painter.setPen(QPen(self.font_shadow_color_disable, 1, Qt.SolidLine))
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
            # self.colorChanged.emit(self._text)

    def color(self):
        if self.isEnabled():
            return self._color
        else:
            return self.color_disable

    def setFontColor(self, color):
        if color is None:
            color = Qt.black
        if color != self._font_color:
            self._font_color = color
            # self.fontChanged.emit(self._text)

    def font_color(self):
        if self.isEnabled():
            return self._font_color
        else:
            return self.font_color_disable

    def setBorderColor(self, color=None):
        if color is None:
            color = QColor("#1e1e1f")
        if color != self._border_color:
            self._border_color = color

    def border_color(self):
        if self.isEnabled():
            return self._border_color
        else:
            return self.border_color_disable

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
        # noinspection PyUnresolvedReferences
        self.clicked.emit(True)
        self.update()

    def mouseMoveEvent(self, event):
        self.__mouse_over = True

    def leaveEvent(self, event):
        self.__mouse_over = False
