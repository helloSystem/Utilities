from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy,
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
        if self.__data != value:
            self.__data = value

    def setData(self, data):
        self.data = data


class ChartPie(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data = None

        self.data = None
        self._circular_size = 100
        self._thickness = 1
        self.qp = None

        self.setupUI()

    def sizeHint(self):
        return QSize(100, 100)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._circular_size = (
            (self.width() - (self._thickness * 2))
            if self.width() < self.height()
            else (self.height() - (self._thickness * 2))
        )

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
        self.qp = QPainter()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setContentsMargins(0, 0, 0, 0)
        self.setBaseSize(100, 100)
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.setMaximumWidth(self.height())

        self.setLayout(QVBoxLayout())
        self.show()

    def paintEvent(self, e):
        if self.isVisible():
            self.qp.begin(self)
            self.qp.setRenderHint(QPainter.Antialiasing)
            self.draw_pie()
            self.qp.end()

    def draw_pie(self):
        pen_size = 1
        off_set = 2

        # x: int, y: int, w: int, h: int, a: int, alen: int
        d_height = self.height()
        d_width = self.width()
        self._circular_size = (
            (self.height() - (self._thickness * 2))
            if self.width() < self.height()
            else (self.height() - (self._thickness * 2))
        )

        x = int(d_width / 2) - int((d_height - (self._thickness * 2)) / 2)
        y = self._thickness
        w = self._circular_size
        h = self._circular_size

        # Micro Drop Shadow
        self.qp.setPen(QPen(Qt.gray, self._thickness))
        self.qp.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        self.qp.drawPie(
            x + int(off_set / 2),
            y + int(off_set / 2),
            self._circular_size - int(off_set / 2),
            self._circular_size - int(off_set / 2),
            0 * 16,
            360 * 16,
        )

        # Overlap the Chart Pie
        total = 0
        if self.data:
            for item in self.data:
                total += item.data
        set_angle = 0
        for item in self.data:
            self.qp.setPen(QPen(QColor(item.color), self._thickness))
            self.qp.setBrush(QBrush(QColor(item.color), Qt.SolidPattern))
            if total > 0:
                angle = item.data * 5760 / total
                self.qp.drawPie(int(x),
                                int(y),
                                int(w - off_set),
                                int(h - off_set),
                                int(set_angle),
                                int(angle)
                                )
                set_angle += angle
