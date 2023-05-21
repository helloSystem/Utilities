#!/usr/bin/env python3

from PyQt5.QtCore import (
    Qt, pyqtProperty, pyqtSignal
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
)

from .buttons import ColorButton
from .widget_cpugraphbar import CPUGraphBar


class TabCpu(QWidget):
    data_user_changed = pyqtSignal()
    data_system_changed = pyqtSignal()
    data_idle_changed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.__user = None
        self.__idle = None
        self.__system = None

        self.lbl_user_value = None
        self.color_button_user = None
        self.lbl_system_value = None
        self.color_button_system = None
        self.lbl_idle_value = None
        self.color_button_idle = None
        self.lbl_threads_value = None
        self.lbl_processes_value = None
        self.widget_graph = None

        self.setupUI()
        self.setupConnect()

    @pyqtProperty(float)
    def idle(self):
        return self.__idle

    @idle.setter
    def idle(self, value):
        if self.__idle != value:
            self.__idle = value
            self.data_idle_changed.emit()

    def set_idle(self, value):
        self.idle = value

    @pyqtProperty(float)
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if self.__user != value:
            self.__user = value
            self.data_user_changed.emit()

    def set_user(self, value):
        self.user = value

    @pyqtProperty(float)
    def system(self):
        return self.__system

    @system.setter
    def system(self, value):
        if self.__system != value:
            self.__system = value
            self.data_system_changed.emit()

    def set_system(self, value):
        self.system = value

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        lbl_user = QLabel("User:")
        lbl_user.setAlignment(Qt.AlignRight)
        lbl_system = QLabel("System:")
        lbl_system.setAlignment(Qt.AlignRight)
        lbl_idle = QLabel("Idle:")
        lbl_idle.setAlignment(Qt.AlignRight)
        lbl_threads = QLabel("Threads:")
        lbl_threads.setAlignment(Qt.AlignRight)
        lbl_processes = QLabel("Processes:")
        lbl_processes.setAlignment(Qt.AlignRight)
        lbl_cpu_usage = QLabel("CPU Usage")
        lbl_cpu_usage.setAlignment(Qt.AlignCenter)

        self.lbl_user_value = QLabel()
        self.lbl_user_value.setAlignment(Qt.AlignRight)
        self.color_button_user = ColorButton(color="green")
        self.lbl_system_value = QLabel("")
        self.lbl_system_value.setAlignment(Qt.AlignRight)
        self.color_button_system = ColorButton(color="red")
        self.lbl_idle_value = QLabel("")
        self.lbl_idle_value.setAlignment(Qt.AlignRight)
        self.color_button_idle = ColorButton(color="black")
        self.lbl_threads_value = QLabel("")
        self.lbl_threads_value.setAlignment(Qt.AlignLeft)
        self.lbl_processes_value = QLabel("")
        self.lbl_processes_value.setAlignment(Qt.AlignLeft)
        self.widget_graph = CPUGraphBar()

        layout_grid = QGridLayout()
        layout_grid.setContentsMargins(0, 0, 0, 0)
        layout_grid.setSpacing(3)
        layout_grid.addWidget(lbl_user, 1, 0, 1, 1)
        layout_grid.addWidget(self.lbl_user_value, 1, 1, 1, 1)
        layout_grid.addWidget(self.color_button_user, 1, 2, 1, 1)
        layout_grid.addWidget(lbl_system, 2, 0, 1, 1)
        layout_grid.addWidget(self.lbl_system_value, 2, 1, 1, 1)
        layout_grid.addWidget(self.color_button_system, 2, 2, 1, 1)
        layout_grid.addWidget(lbl_idle, 3, 0, 1, 1)
        layout_grid.addWidget(self.lbl_idle_value, 3, 1, 1, 1)
        layout_grid.addWidget(self.color_button_idle, 3, 2, 1, 1)
        layout_grid.addWidget(lbl_threads, 1, 3, 1, 1)
        layout_grid.addWidget(self.lbl_threads_value, 1, 4, 1, 1)
        layout_grid.addWidget(lbl_processes, 2, 3, 1, 1)
        layout_grid.addWidget(self.lbl_processes_value, 2, 4, 1, 1)
        layout_grid.addWidget(lbl_cpu_usage, 0, 6, 1, 1, Qt.AlignCenter)
        layout_grid.addWidget(self.widget_graph, 1, 6, 4, 1, Qt.AlignCenter)
        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        widget_grid.setLayout(layout_grid)
        widget_grid.setContentsMargins(0, 0, 0, 0)

        space_label = QLabel()
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(20, 0, 20, 0)

        self.setLayout(layout_vbox)

        # Update color label by the color of the color picker
        self.refresh_color_system()
        self.refresh_color_user()
        self.refresh_color_idle()

    def setupConnect(self):
        self.data_idle_changed.connect(self.refresh_idle)
        self.data_user_changed.connect(self.refresh_user)
        self.data_system_changed.connect(self.refresh_system)

        self.color_button_system.colorChanged.connect(self.refresh_color_system)
        self.color_button_user.colorChanged.connect(self.refresh_color_user)
        self.color_button_idle.colorChanged.connect(self.refresh_color_idle)

    def refresh_user(self):
        if self.__user:
            self.lbl_user_value.setText("%s %s" % (self.__user, "%"))
            self.widget_graph.user = self.__user / 2

    def refresh_system(self):
        if self.__system:
            self.lbl_system_value.setText("%s %s" % (self.__system, "%"))
            self.widget_graph.system = self.__system / 2

    def refresh_idle(self):
        if self.__idle:
            self.lbl_idle_value.setText("%s %s" % (self.__idle, "%"))
            # idle color is just the background color, then it is bind to refresh
            self.widget_graph.refresh()

    def refresh_process_number(self, process_number: int):
        self.lbl_processes_value.setText("%d" % process_number)

    def refresh_cumulative_threads(self, cumulative_threads: int):
        self.lbl_threads_value.setText("%d" % cumulative_threads)

    def refresh_color_system(self):
        self.lbl_system_value.setStyleSheet("color: %s;" % self.color_button_system.color())
        self.widget_graph.color_system = self.color_button_system.color()

    def refresh_color_user(self):
        self.lbl_user_value.setStyleSheet("color: %s;" % self.color_button_user.color())
        self.widget_graph.color_user = self.color_button_user.color()

    def refresh_color_idle(self):
        self.lbl_idle_value.setStyleSheet("color: %s;" % self.color_button_idle.color())
        self.widget_graph.color_idle = self.color_button_idle.color()
