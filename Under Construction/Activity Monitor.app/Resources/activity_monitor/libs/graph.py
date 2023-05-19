#!/usr/bin/env python3
import sys
from collections import deque

from PyQt5.QtCore import Qt, QRect, QSize
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
        self.value1 = 0
        self.value2 = 0
        self.color1 = QColor("black")
        self.color2 = QColor("black")

        self.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self.__padding = 0
        self.__step_number = 100
        self.__step_size = 10

    def sizeHint(self):
        return QSize(10, 100)

    def resizeEvent(self, event):
        super(_Bar, self).resizeEvent(event)

    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        # Dynamic size
        self.__step_size = int((painter.device().height() / self.__step_number))

        # Create background
        pos_y = 0
        for i in range(0, self.__step_number):
            brush.setColor(QColor('black'))
            rect = QRect(0, pos_y, painter.device().width(), self.__step_size)
            pos_y += self.__step_size + self.__padding
            painter.fillRect(rect, brush)

        pos_y = 0
        for i in range(0, self.__step_number):
            # Frist Value
            if i >= self.__step_number - self.value1:
                brush.setColor(QColor(self.color1))
            # Second Value just follow location of teh frist value
            elif i >= self.__step_number - (self.value1 + self.value2):
                brush.setColor(QColor(self.color2))

            rect = QRect(0, pos_y, painter.device().width(), self.__step_size)
            pos_y += self.__step_size + self.__padding
            painter.fillRect(rect, brush)


class Graph(QWidget):
    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)

        self.bars = []
        self.__bars_number = 10

        self.value1 = 0
        self.value2 = 0
        self.color1 = QColor("red")
        self.color2 = QColor("green")

        self.setupUI()

    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Create Bars
        for i in range(0, 10):
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
        for i in range(9, 0, -1):
            self.bars[i].value1 = self.bars[i - 1].value1
            self.bars[i].value2 = self.bars[i - 1].value2
            self.bars[i].color1 = self.bars[i - 1].color1
            self.bars[i].color2 = self.bars[i - 1].color2

    def refresh_color1(self):
        for i in range(9, 0, -1):
            self.bars[i].color1 = self.color1

    def refresh_color2(self):
        for i in range(9, 0, -1):
            self.bars[i].color2 = self.color2


if __name__ == "__main__":
    app = QApplication([])
    graph = Graph()

    sys.exit(app.exec())
