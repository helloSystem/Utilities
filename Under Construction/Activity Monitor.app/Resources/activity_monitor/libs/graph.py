#!/usr/bin/env python3
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QSizePolicy
)


class _Bar(QWidget):
    def __init__(self, *args, **kwargs):
        super(_Bar, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

    def sizeHint(self):
        return QSize(40, 15)

    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setColor(QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)


class Graph(QWidget):
    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)

        self.__bars = []
        self.__bars_number = 10

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Create Bars
        for i in range(0, self.__bars_number):
            self.__bars.append(_Bar())

        # Add in Layout
        for bar in self.__bars:
            layout.addWidget(bar)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    graph = Graph()
    graph.show()
    app.exec_()
