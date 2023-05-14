from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget,
)


class ChartPieItem(object):
    def __init__(self):
        self.__color = None
        self.__data = None

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        # if not isinstance(value, QColor):
        #     raise TypeError("'color' property value must be a QColor instance")
        if self.color != value:
            self.__color = value

    def setColor(self, color):
        self.color = color

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if type(value) != float and type(value) != int:
            raise TypeError("'data' property value must be a float or a int type")
        if self.data != value:
            self.__data = value

    def setColor(self, color):
        self.color = color

    def setData(self, data):
        self.data = data


class ChartPie(QWidget):

    def __init__(self):
        super().__init__()
        self.__data = None
        self.data = None

        self.setupUI()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if value is None:
            value = []
        if type(value) != list:
            raise TypeError("'data' property value must be a list type or None")
        if self.data != value:
            self.__data = value

    def addItem(self, item):
        if not isinstance(item, ChartPieItem):
            raise TypeError("'item' parameter must be ChartPieItem instance")
        self.data.append(item)

    def addItems(self, items):
        if type(items) != list:
            raise TypeError("'items' parameter must be list type")
        for item in items:
            self.addItem(item)

    def clear(self):
        self.data = None

    def setupUI(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(self.height())
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setRenderHint(QPainter.HighQualityAntialiasing)
        self.draw_pie(qp)
        qp.end()

    def draw_pie(self, qp):
        pen_size = 1
        qp.setPen(QPen(Qt.lightGray, pen_size))
        # Draw back ground circle
        total = 0
        if self.data:
            for item in self.data:
                total += item.data
        qp.drawPie(
            int(self.width() / 2) - int((self.height() - (pen_size * 2)) / 2),
            pen_size,
            self.height() - (pen_size * 2),
            self.height() - (pen_size * 2),
            0 * 16, 360 * 16)

        set_angle = 0
        for item in self.data:
            qp.setPen(QPen(Qt.gray, pen_size))
            qp.setBrush(QBrush(QColor(item.color), Qt.SolidPattern))
            if total > 0:
                angle = round(float(item.data * 5760) / total)
                qp.drawPie(int(self.width() / 2) - int((self.height() - (pen_size * 2)) / 2),
                           pen_size,
                           self.height() - (pen_size * 2),
                           self.height() - (pen_size * 2),
                           set_angle, angle)
                set_angle += angle

        # qp.drawPie(150, 20, 100, 100, 0 * 16, 60 * 16)
        # qp.drawText(190, 100, '60°')
        #
        # qp.drawPie(280, 20, 100, 100, 0 * 16, 90 * 16)
        # qp.drawText(320, 100, '90°')
        #
        # qp.drawPie(20, 140, 100, 100, 0 * 16, 180 * 16)
        # qp.drawText(60, 270, '180°')
        #
        # qp.drawPie(150, 140, 100, 100, 0 * 16, 270 * 16)
        # qp.drawText(190, 270, '270°')
        #
        # qp.drawPie(280, 140, 100, 100, 0 * 16, 360 * 16)
        # qp.drawText(320, 270, '360°')
