#!/usr/bin/env python3
import sys

from PyQt5.QtCore import Qt, QRect, QSize, pyqtProperty
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QApplication,
    QSizePolicy
)


class _Bar(QWidget):
    def __init__(self, *args, **kwargs):
        super(_Bar, self).__init__(*args, **kwargs)
        self.__value1 = 0.0
        self.__value2 = 0.0
        self.__color1 = QColor("black")
        self.__color2 = QColor("black")
        self.__color3 = QColor("black")

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding,
        )

        self.__step_number = 100
        self.qp = None

    @pyqtProperty(float)
    def value1(self):
        return self.__value1

    @value1.setter
    def value1(self, value):
        if self.__value1 != value:
            self.__value1 = value

    @pyqtProperty(float)
    def value2(self):
        return self.__value2

    @value2.setter
    def value2(self, value):
        if self.__value2 != value:
            self.__value2 = value

    @pyqtProperty(QColor)
    def color1(self):
        return self.__color1

    @color1.setter
    def color1(self, value):
        if self.__color1 != value:
            self.__color1 = value

    @pyqtProperty(QColor)
    def color2(self):
        return self.__color2

    @color2.setter
    def color2(self, value):
        if self.__color2 != value:
            self.__color2 = value

    @pyqtProperty(QColor)
    def color2(self):
        return self.__color2

    @color2.setter
    def color2(self, value):
        if self.__color2 != value:
            self.__color2 = value

    @pyqtProperty(QColor)
    def color3(self):
        return self.__color3

    @color3.setter
    def color3(self, value):
        if self.__color3 != value:
            self.__color3 = value

    def sizeHint(self):
        return QSize(4, 100)

    def resizeEvent(self, event):
        super(_Bar, self).resizeEvent(event)

    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        self.qp.setRenderHint(QPainter.Antialiasing)
        self.draw_graph()
        self.qp.end()

    def draw_graph(self):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        # Dynamic size
        step_size = int((self.qp.device().height() / self.__step_number))

        # Background
        brush.setColor(QColor(self.__color3))
        x = int(self.width() / 2) - int(self.qp.device().width() / 2)
        rect = QRect(x, 0, self.qp.device().width(), self.qp.device().height())
        self.qp.fillRect(rect, brush)

        pos_y = 0
        for i in range(0, self.__step_number):
            # First Value
            if i >= self.__step_number - self.__value1:
                brush.setColor(QColor(self.__color1))
            # Second Value just follow location of the first value
            elif i >= self.__step_number - (self.__value1 + self.__value2):
                brush.setColor(QColor(self.__color2))

            rect = QRect(x, pos_y, self.qp.device().width(), step_size)
            self.qp.fillRect(rect, brush)
            pos_y += step_size


class Graph(QWidget):
    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)

        self.bars = []
        self.__bars_number = 25

        self.value1 = 0
        self.value2 = 0
        self.color1 = QColor("red")
        self.color2 = QColor("green")
        self.color3 = QColor("black")

        self.setupUI()

    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Create Bars
        for i in range(0, self.__bars_number):
            bar = _Bar()
            bar.color1 = self.color1
            bar.color2 = self.color2
            self.bars.append(bar)

        # Add in Layout
        for bar in reversed(self.bars):
            layout.addWidget(bar)

        self.setLayout(layout)
        self.show()

    def refresh(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].value1 = self.bars[i - 1].value1
            self.bars[i].value2 = self.bars[i - 1].value2
            self.bars[i].color1 = self.bars[i - 1].color1
            self.bars[i].color2 = self.bars[i - 1].color2

    def refresh_color1(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].color1 = self.color1

    def refresh_color2(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].color2 = self.color2

    def refresh_color3(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].color3 = self.color3


if __name__ == "__main__":
    app = QApplication([])
    graph = Graph()
    graph.value1 = 50
    graph.value2 = 25
    graph.color1 = Qt.red
    graph.color2 = Qt.green
    graph.color2 = Qt.darkGray
    graph.repaint()
    sys.exit(app.exec())
