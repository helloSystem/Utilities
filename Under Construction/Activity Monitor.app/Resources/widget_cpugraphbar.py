#!/usr/bin/env python3
import sys

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QApplication,
    QSizePolicy
)

from property_cpu_times_percent import CPUTimesPercent


class CPUBar(QWidget, CPUTimesPercent):
    user: float
    system: float
    idle: float
    nice: float
    irq: float

    color_user: QColor
    color_system: QColor
    color_idle: QColor
    color_nice: QColor
    color_irq: QColor

    def __init__(self, *args, **kwargs):
        super(CPUBar, self).__init__(*args, **kwargs)
        CPUTimesPercent.__init__(self)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding,
        )

        self.__step_number = 50
        self.qp = None

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
        brush.setColor(QColor(self.color_idle))
        x = 0
        rect = QRect(x, 0, self.qp.device().width(), self.qp.device().height())
        self.qp.fillRect(rect, brush)

        pos_y = 0
        for i in range(0, self.__step_number):
            # First Value
            if type(self.system) == float and type(self.user) == float:
                if i >= self.__step_number - self.system:
                    brush.setColor(QColor(self.color_system))
                # Second Value just follow location of the first value
                elif i >= self.__step_number - (self.system + self.user):
                    brush.setColor(QColor(self.color_user))

                rect = QRect(x, pos_y, self.qp.device().width(), step_size)
                self.qp.fillRect(rect, brush)
                pos_y += step_size


class CPUGraphBar(QWidget, CPUTimesPercent):
    color_system_changed = pyqtSignal()
    color_user_changed = pyqtSignal()
    color_idle_changed = pyqtSignal()
    user_changed = pyqtSignal()
    system_changed = pyqtSignal()

    user: float
    system: float
    idle: float
    nice: float
    irq: float

    color_user: QColor
    color_system: QColor
    color_idle: QColor
    color_nice: QColor
    color_irq: QColor

    def __init__(self, *args, **kwargs):
        super(CPUGraphBar, self).__init__(*args, **kwargs)
        CPUTimesPercent.__init__(self)

        self.bars = []
        self.__bars_number = 25

        self.setupUI()
        self.setupConnect()

    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Create Bars
        for i in range(0, self.__bars_number):
            bar = CPUBar()
            bar.color_system = self.color_system
            bar.color_user = self.color_user
            bar.color_idle = self.color_idle
            bar.user = self.user
            bar.system = self.system
            self.bars.append(bar)

        # Pack end bars in Layout
        for bar in reversed(self.bars):
            layout.addWidget(bar)

    def setupConnect(self):
        self.cpu_idle_changed.connect(self.refresh_idle)
        self.cpu_user_changed.connect(self.refresh_user)
        self.cpu_system_changed.connect(self.refresh_system)
        self.cpu_nice_changed.connect(self.refresh_nice)
        self.cpu_irq_changed.connect(self.refresh_irq)

        self.cpu_user_color_changed.connect(self.refresh_color_user)
        self.cpu_system_color_changed.connect(self.refresh_color_system)
        self.cpu_idle_color_changed.connect(self.refresh_color_idle)
        self.cpu_nice_color_changed.connect(self.refresh_color_nice)
        self.cpu_irq_color_changed.connect(self.refresh_color_irq)

    def refresh(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].idle = self.bars[i - 1].idle
            self.bars[i].user = self.bars[i - 1].user
            self.bars[i].system = self.bars[i - 1].system
            self.bars[i].nice = self.bars[i - 1].nice
            self.bars[i].irq = self.bars[i - 1].irq
            self.bars[i].color_idle = self.bars[i - 1].color_idle
            self.bars[i].color_system = self.bars[i - 1].color_system
            self.bars[i].color_user = self.bars[i - 1].color_user
            self.bars[i].color_nice = self.bars[i - 1].color_nice
            self.bars[i].color_nirq = self.bars[i - 1].color_irq
        self.repaint()

    def refresh_system(self):
        self.bars[0].system = self.system

    def refresh_user(self):
        self.bars[0].user = self.user

    def refresh_idle(self):
        self.bars[0].idle = self.idle

    def refresh_nice(self):
        self.bars[0].nice = self.nice

    def refresh_irq(self):
        self.bars[0].irq = self.irq

    def refresh_color_system(self):
        for bar in self.bars:
            bar.color_system = self.color_system
        self.repaint()

    def refresh_color_user(self):
        for bar in self.bars:
            bar.color_user = self.color_user
        self.repaint()

    def refresh_color_idle(self):
        for bar in self.bars:
            bar.color_idle = self.color_idle
        self.repaint()

    def refresh_color_nice(self):
        for bar in self.bars:
            bar.color_nice = self.color_nice
        self.repaint()

    def refresh_color_irq(self):
        for bar in self.bars:
            bar.color_irq = self.color_irq
        self.repaint()

    def clear_history(self):
        for i in range(len(self.bars) - 1, 0, -1):
            self.bars[i].user = 0.0
            self.bars[i].system = 0.0
            self.bars[i].idle = 0.0
            self.bars[i].irq = 0.0
            self.bars[i].nice = 0.0
        self.repaint()


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
