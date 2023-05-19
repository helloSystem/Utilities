#!/usr/bin/env python3

from PyQt5.QtCore import (
    Qt, pyqtProperty, pyqtSignal
)
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QBrush, QFontMetrics, QFont
from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QColorDialog,
    QSpacerItem,
    QSizePolicy,
)

from .buttons import ColorButton


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

        self.setupUI()

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
        layout_grid = QGridLayout()
        layout_grid.setContentsMargins(0, 0, 0, 0)
        layout_grid.setSpacing(3)

        # User label
        lbl_user = QLabel("User:")
        lbl_user.setAlignment(Qt.AlignRight)
        # User label value
        self.lbl_user_value = QLabel("")
        self.lbl_user_value.setAlignment(Qt.AlignRight)
        # User Color button
        self.color_button_user = ColorButton(color="green")
        # Insert user labels on the right position
        layout_grid.addWidget(lbl_user, 1, 0, 1, 1)
        layout_grid.addWidget(self.lbl_user_value, 1, 1, 1, 1)
        layout_grid.addWidget(self.color_button_user, 1, 2, 1, 1)

        # System label
        lbl_system = QLabel("System:")
        lbl_system.setAlignment(Qt.AlignRight)
        # System label value
        self.lbl_system_value = QLabel("")
        self.lbl_system_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_system = ColorButton(color="blue")

        # Insert system labels on the right position
        layout_grid.addWidget(lbl_system, 2, 0, 1, 1)
        layout_grid.addWidget(self.lbl_system_value, 2, 1, 1, 1)
        layout_grid.addWidget(self.color_button_system, 2, 2, 1, 1)

        # Label Idle
        lbl_idle = QLabel("Idle:")
        lbl_idle.setAlignment(Qt.AlignRight)
        # Label Idle value
        self.lbl_idle_value = QLabel("")
        self.lbl_idle_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_idle = ColorButton(color="black")

        # Insert idle labels on the right position
        layout_grid.addWidget(lbl_idle, 3, 0, 1, 1)
        layout_grid.addWidget(self.lbl_idle_value, 3, 1, 1, 1)
        layout_grid.addWidget(self.color_button_idle, 3, 2, 1, 1)

        # Label threads
        lbl_threads = QLabel("Threads:")
        lbl_threads.setAlignment(Qt.AlignRight)
        # Label threads value
        self.lbl_threads_value = QLabel("")
        self.lbl_threads_value.setAlignment(Qt.AlignLeft)
        # Insert threads labels on the right position
        layout_grid.addWidget(lbl_threads, 1, 3, 1, 1)
        layout_grid.addWidget(self.lbl_threads_value, 1, 4, 1, 1)

        # Label Processes
        lbl_processes = QLabel("Processes:")
        lbl_processes.setAlignment(Qt.AlignRight)
        # Label Processes value
        self.lbl_processes_value = QLabel("")
        self.lbl_processes_value.setAlignment(Qt.AlignLeft)
        # Insert Processes labels on the right position
        layout_grid.addWidget(lbl_processes, 2, 3, 1, 1)
        layout_grid.addWidget(self.lbl_processes_value, 2, 4, 1, 1)

        lbl_cpu_usage = QLabel("CPU Usage")
        lbl_cpu_usage.setAlignment(Qt.AlignCenter)
        layout_grid.addWidget(lbl_cpu_usage, 0, 6, 1, 1, Qt.AlignCenter)

        # Force top position of widget
        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
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
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        # Update color label by the color of the color picker
        self.refresh_color_system()
        self.refresh_color_user()
        self.refresh_color_idle()

        # Notre the good place but where ?
        self.data_idle_changed.connect(self.refresh_idle)
        self.data_user_changed.connect(self.refresh_user)
        self.data_system_changed.connect(self.refresh_system)

        self.color_button_system.colorChanged.connect(self.refresh_color_system)
        self.color_button_user.colorChanged.connect(self.refresh_color_user)
        self.color_button_idle.colorChanged.connect(self.refresh_color_idle)

        self.setLayout(layout_vbox)

    def refresh_user(self):
        if self.__user:
            self.lbl_user_value.setText("%s %s" % (self.__user, "%"))

    def refresh_system(self):
        if self.__system:
            self.lbl_system_value.setText("%s %s" % (self.__system, "%"))

    def refresh_idle(self):
        if self.__idle:
            self.lbl_idle_value.setText("%s %s" % (self.__idle, "%"))

    def refresh_process_number(self, process_number: int):
        self.lbl_processes_value.setText("%d" % process_number)

    def refresh_cumulative_threads(self, cumulative_threads: int):
        self.lbl_threads_value.setText("%d" % cumulative_threads)

    def refresh_color_system(self):
        self.lbl_system_value.setStyleSheet("color: %s;" % self.color_button_system.color())

    def refresh_color_user(self):
        self.lbl_user_value.setStyleSheet("color: %s;" % self.color_button_user.color())

    def refresh_color_idle(self):
        self.lbl_idle_value.setStyleSheet("color: %s;" % self.color_button_idle.color())
