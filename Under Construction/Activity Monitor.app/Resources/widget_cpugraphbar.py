#!/usr/bin/env python3
import sys

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
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

        self.bar_width = 10
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(0)
        self.setMaximumWidth(self.bar_width)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding,
        )

        self.grid_size = 10
        self.qp = None

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
        #  (value() - minimum()) divided by maximum() - minimum().

        step_size = int((self.height() / 100))

        # Background
        brush.setColor(QColor(self.color_idle))
        x = 0
        rect = QRect(x, 0, self.bar_width, self.height())
        self.qp.fillRect(rect, brush)

        pos_y = 0
        for i in range(0, 100):
            if i >= 100 - self.system:
                brush.setColor(QColor(self.color_system))
            elif i >= 100 - (self.system + self.user):
                brush.setColor(QColor(self.color_user))
            elif i >= 100 - (self.system + self.user + self.nice):
                brush.setColor(QColor(self.color_nice))
            elif i >= 100 - (self.system + self.user + self.nice + self.irq):
                brush.setColor(QColor(self.color_irq))

            rect = QRect(x + 1, pos_y + 1, self.bar_width - 1, step_size)
            self.qp.fillRect(rect, brush)
            pos_y += step_size
        self.qp.setPen(QPen(QColor(self.color_idle)))
        for r in range(int(self.height()/self.grid_size)):
            self.qp.drawLine(0, self.grid_size * r, self.width(), self.grid_size * r)

            # if self.grid_size * r / 100 <= 100 - self.system:
            #     brush.setColor(QColor(self.color_system))
            #     rect = QRect(x + 1, self.grid_size * r, self.bar_width - 1, self.grid_size)
            #     self.qp.fillRect(rect, brush)
            pos_y += self.grid_size


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

        self.bars = {}
        self.layout = None

        self.setupUI()
        self.setupConnect()

    def sizeHint(self):
        return QSize(100, 100)

    def resizeEvent(self, event):
        super(CPUGraphBar, self).resizeEvent(event)
        self.remove_unneeded_bar()
        self.add_needed_bar()
        # print("bar_it_can_be_display = %s" % self.get_bars_number_it_can_be_display())
        # print("Bar list size = %s" % len(self.bars))

    def setupUI(self):
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.add_needed_bar()

        # Create Bars
        self.setLayout(self.layout)

    def get_bars_number_it_can_be_display(self):
        count = 0
        while 10 * count <= self.width():
            count += 1
        return count -1

    def remove_unneeded_bar(self):
        have_to_remove = []
        for key, bar in self.bars.items():
            if key > self.get_bars_number_it_can_be_display():
                have_to_remove.append(key)
        for key in have_to_remove:
            self.bars[key].setParent(None)
            self.bars[key].hide()
            self.bars[key].close()
            self.bars[key].deleteLater()
            del self.bars[key]
            self.refresh_layout_display()

    def refresh_layout_display(self):
        for key, value in self.bars.items():
            self.layout.addWidget(value, 0, self.get_bars_number_it_can_be_display() + 1 - key, 1, 1)

    def add_needed_bar(self):
        while len(self.bars) < self.get_bars_number_it_can_be_display():
            self.add_a_bar()
            self.refresh_layout_display()

    def add_a_bar(self):
        # for i in range(0, int(self.__bars_number)):

        max_value = 0
        for value, bar in self.bars.items():
            if value > max_value:
                max_value = value

        self.bars[max_value + 1] = CPUBar()
        self.bars[max_value + 1].user = self.user
        self.bars[max_value + 1].system = self.system
        self.bars[max_value + 1].irq = self.irq
        self.bars[max_value + 1].nice = self.nice
        self.bars[max_value + 1].idle = self.idle

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

    def slice(self):
        for i in range(self.get_bars_number_it_can_be_display(), 1, - 1):
            # print("Move data from bar%s to bar%s" % (i, i - 1))
            self.bars[i].idle = self.bars[i - 1].idle
            self.bars[i].user = self.bars[i - 1].user
            self.bars[i].system = self.bars[i - 1].system
            self.bars[i].nice = self.bars[i - 1].nice
            self.bars[i].irq = self.bars[i - 1].irq
            self.bars[i].color_idle = self.bars[i - 1].color_idle
            self.bars[i].color_system = self.bars[i - 1].color_system
            self.bars[i].color_user = self.bars[i - 1].color_user
            self.bars[i].color_nice = self.bars[i - 1].color_nice
            self.bars[i].color_irq = self.bars[i - 1].color_irq
        self.refresh_layout_display()
        self.repaint()

    def refresh_system(self):
        self.bars[1].system = self.system

    def refresh_user(self):
        self.bars[1].user = self.user

    def refresh_idle(self):
        self.bars[1].idle = self.idle

    def refresh_nice(self):
        self.bars[1].nice = self.nice

    def refresh_irq(self):
        self.bars[1].irq = self.irq

    def refresh_color_system(self):
        for keyname, bar in self.bars.items():
            bar.color_system = self.color_system

    def refresh_color_user(self):
        for keyname, bar in self.bars.items():
            bar.color_user = self.color_user

    def refresh_color_idle(self):
        for keyname, bar in self.bars.items():
            bar.color_idle = self.color_idle

    def refresh_color_nice(self):
        for keyname, bar in self.bars.items():
            bar.color_nice = self.color_nice

    def refresh_color_irq(self):
        for keyname, bar in self.bars.items():
            bar.color_irq = self.color_irq

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
    graph.slice()
    graph.show()
    sys.exit(app.exec())
