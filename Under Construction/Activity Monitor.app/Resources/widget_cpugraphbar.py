#!/usr/bin/env python3
import sys

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QApplication,
    QSizePolicy,
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

        self.grid_size = 10
        self.grid_spacing = 1

        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(0)
        self.setMaximumWidth(self.grid_size)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding,
        )

        self.qp = QPainter()
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)
        self.pen = QPen(QColor(self.color_idle))
        self.pen.setWidth(self.grid_spacing)

    def paintEvent(self, e):
        if self.isVisible():
            self.qp.begin(self)
            self.draw_graph()
            self.qp.end()

    def draw_graph(self):
        step_size = int(self.height() / 100)

        # Background
        self.brush.setColor(QColor(self.color_idle))
        rect = QRect(0, 0, self.grid_size, self.height())
        self.qp.fillRect(rect, self.brush)

        pos_y = 0
        for i in range(0, 100):
            if i >= 100 - self.system:
                self.brush.setColor(QColor(self.color_system))
            elif i >= 100 - (self.system + self.user):
                self.brush.setColor(QColor(self.color_user))
            elif i >= 100 - (self.system + self.user + self.nice):
                self.brush.setColor(QColor(self.color_nice))
            elif i >= 100 - (self.system + self.user + self.nice + self.irq):
                self.brush.setColor(QColor(self.color_irq))

            rect = QRect(0, pos_y, self.grid_size, step_size)
            self.qp.fillRect(rect, self.brush)
            pos_y += step_size

        # Display The Grid
        # Row
        # self.qp.setPen(self.pen)
        # for r in range(int(self.height()/self.grid_size)):
        #     self.qp.drawLine(0, self.grid_size * r, self.width(), self.grid_size * r)


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

        self.grid_size = 10
        self.grid_spacing = 1

        self.bars = {}
        self.layout = None
        self.qp = None
        self.brush = None

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
        self.qp = QPainter()
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(self.grid_spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Create Bars
        self.add_needed_bar()

    def paintEvent(self, e):
        if self.isVisible():
            self.qp.begin(self)
            rect = QRect(self.grid_size, 0, self.width() - self.grid_size, self.height())
            self.qp.fillRect(rect, self.brush)
            self.qp.end()

    def get_bars_number_it_can_be_display(self):
        count = 0
        while (self.grid_size + self.grid_spacing) * count <= self.width():
            count += 1
        return count - 1

    def remove_unneeded_bar(self):
        have_to_remove = []
        for key, bar in self.bars.items():
            if key > self.get_bars_number_it_can_be_display():
                if key > 1:
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
            self.layout.addWidget(value, 0, len(self.bars) - key, 1, 1)
        self.repaint()

    def add_needed_bar(self):
        while len(self.bars) < self.get_bars_number_it_can_be_display():
            self.add_a_bar()
        self.refresh_layout_display()

    def add_a_bar(self):
        try:
            self.bars[len(self.bars) + 1] = CPUBar()
            self.bars[len(self.bars) + 1].setMaximumWidth(self.grid_size)
        except KeyError:
            pass

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
        for i in range(len(self.bars), 1, - 1):
            # print("Move data from bar%s to bar%s" % (i, i - 1))
            self.bars[i].user = self.bars[i - 1].user
            self.bars[i].system = self.bars[i - 1].system
            self.bars[i].nice = self.bars[i - 1].nice
            self.bars[i].irq = self.bars[i - 1].irq
            self.bars[i].color_user = self.bars[i - 1].color_user
            self.bars[i].color_system = self.bars[i - 1].color_system
            self.bars[1].color_idle = self.bars[i - 1].color_idle
            self.bars[1].color_nice = self.bars[i - 1].color_nice
            self.bars[1].color_irq = self.bars[i - 1].color_irq
        self.refresh_layout_display()

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
        self.repaint()

    def refresh_color_user(self):
        for keyname, bar in self.bars.items():
            bar.color_user = self.color_user
        self.repaint()

    def refresh_color_idle(self):
        self.brush.setColor(QColor(self.color_idle))
        for keyname, bar in self.bars.items():
            bar.color_idle = self.color_idle
        self.repaint()

    def refresh_color_nice(self):
        for keyname, bar in self.bars.items():
            bar.color_nice = self.color_nice
        self.repaint()

    def refresh_color_irq(self):
        for keyname, bar in self.bars.items():
            bar.color_irq = self.color_irq
        self.repaint()

    def clear_history(self):
        for i in range(len(self.bars), 0, -1):
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
