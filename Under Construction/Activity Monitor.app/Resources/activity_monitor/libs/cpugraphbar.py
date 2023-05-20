#!/usr/bin/env python3
import sys

from PyQt5.QtCore import Qt, QRect, QSize, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QApplication,
    QSizePolicy
)


class CPUBar(QWidget):
    color1_value_changed = pyqtSignal(object)
    color2_value_changed = pyqtSignal(object)
    color3_value_changed = pyqtSignal(object)
    value1_value_changed = pyqtSignal(object)
    value2_value_changed = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(CPUBar, self).__init__(*args, **kwargs)
        self.__system = 0.0
        self.__user = 0.0
        self.__color_system = QColor("black")
        self.__color_user = QColor("black")
        self.__color_idle = QColor("black")

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding,
        )

        self.__step_number = 50
        self.qp = None

    @pyqtProperty(float)
    def system(self):
        return self.__system

    @system.setter
    def system(self, value):
        if self.__system != value:
            self.__system = value

    @pyqtProperty(float)
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if self.__user != value:
            self.__user = value

    @pyqtProperty(QColor)
    def color_system(self):
        return self.__color_system

    @color_system.setter
    def color_system(self, value):
        if self.__color_system != value:
            self.__color_system = value

    @pyqtProperty(QColor)
    def color_user(self):
        return self.__color_user

    @color_user.setter
    def color_user(self, value):
        if self.__color_user != value:
            self.__color_user = value

    @pyqtProperty(QColor)
    def color_idle(self):
        return self.__color_idle

    @color_idle.setter
    def color_idle(self, value):
        if self.__color_idle != value:
            self.__color_idle = value

    def sizeHint(self):
        return QSize(4, 100)

    def resizeEvent(self, event):
        super(CPUBar, self).resizeEvent(event)

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
        brush.setColor(QColor(self.__color_idle))
        x = 0
        rect = QRect(x, 0, self.qp.device().width(), self.qp.device().height())
        self.qp.fillRect(rect, brush)

        pos_y = 0
        for i in range(0, self.__step_number):
            # First Value
            if i >= self.__step_number - self.__system:
                brush.setColor(QColor(self.__color_system))
            # Second Value just follow location of the first value
            elif i >= self.__step_number - (self.__system + self.__user):
                brush.setColor(QColor(self.__color_user))

            rect = QRect(x, pos_y, self.qp.device().width(), step_size)
            self.qp.fillRect(rect, brush)
            pos_y += step_size


class CPUGraphBar(QWidget):
    color_system_changed = pyqtSignal()
    color_user_changed = pyqtSignal()
    color_idle_changed = pyqtSignal()
    user_changed = pyqtSignal()
    system_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CPUGraphBar, self).__init__(*args, **kwargs)

        self.bars = []
        self.__bars_number = 25

        self.__system = 0.0
        self.__user = 0.0
        self.__color_system = QColor("red")
        self.__color_user = QColor("green")
        self.__color_idle = QColor("black")

        self.setupUI()
        self.setupConnect()

    @pyqtProperty(float)
    def system(self):
        return self.__system

    @system.setter
    def system(self, value):
        if self.__system != value:
            self.__system = value
            self.system_changed.emit()

    @pyqtProperty(float)
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if self.__user != value:
            self.__user = value
            self.user_changed.emit()

    @pyqtProperty(QColor)
    def color_system(self):
        return self.__color_system

    @color_system.setter
    def color_system(self, value):
        if self.__color_system != value:
            self.__color_system = value
            self.color_system_changed.emit()

    @pyqtProperty(QColor)
    def color_user(self):
        return self.__color_user

    @color_user.setter
    def color_user(self, value):
        if self.__color_user != value:
            self.__color_user = value
            self.color_user_changed.emit()

    @pyqtProperty(QColor)
    def color_idle(self):
        return self.__color_idle

    @color_idle.setter
    def color_idle(self, value):
        if self.__color_idle != value:
            self.__color_idle = value
            self.color_idle_changed.emit()

    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Create Bars
        for i in range(0, self.__bars_number):
            bar = CPUBar()
            bar.color_system = self.__color_system
            bar.color_user = self.__color_user
            bar.color_idle = self.__color_idle
            bar.user = self.__user
            bar.system = self.__system
            self.bars.append(bar)

        # Pack end bars in Layout
        for bar in reversed(self.bars):
            layout.addWidget(bar)

    def setupConnect(self):
        self.user_changed.connect(self.refresh_user)
        self.system_changed.connect(self.refresh_system)
        self.color_system_changed.connect(self.refresh_color_system)
        self.color_user_changed.connect(self.refresh_color_user)
        self.color_idle_changed.connect(self.refresh_color_idle)

    def refresh(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].system = self.bars[i - 1].system
            self.bars[i].user = self.bars[i - 1].user
            self.bars[i].color_system = self.bars[i - 1].color_system
            self.bars[i].color_user = self.bars[i - 1].color_user
            self.bars[i].color_idle = self.bars[i - 1].color_idle

    def refresh_system(self):
        self.bars[0].system = self.__system

    def refresh_user(self):
        self.bars[0].user = self.__user

    def refresh_color_system(self):
        for bar in self.bars:
            bar.color_system = self.__color_system

    def refresh_color_user(self):
        for bar in self.bars:
            bar.color_user = self.__color_user

    def refresh_color_idle(self):
        for bar in self.bars:
            bar.color_idle = self.__color_idle


if __name__ == "__main__":
    app = QApplication([])
    graph = CPUGraphBar()
    graph.system = 50
    graph.user = 25
    graph.color_system = Qt.red
    graph.color_user = Qt.green
    graph.color_idle = Qt.darkGray
    graph.repaint()
    sys.exit(app.exec())
