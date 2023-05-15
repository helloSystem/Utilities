#!/usr/bin/env python3

from PyQt5.QtCore import (
    Qt,
)
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
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.lbl_user_value = None
        self.color_button_user = None
        self.lbl_system_value = None
        self.color_button_system = None
        self.lbl_idle_value = None
        self.color_button_idle = None
        self.lbl_threads_value = None
        self.lbl_processes_value = None

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout_grid = QGridLayout()

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
        # self.color_button_system.clicked.connect(self._set_color_button_system())

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

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def _set_color_button_system(self):
        color = QColorDialog.getColor()  # OpenColorDialog
        if color.isValid():
            print(color.name())  # ff5b87
            print(color.red(), color.green(), color.blue())  # 255 91 135

        r, g, b = color.red(), color.green(), color.blue()
        strRGB = "{:^3d}, {:^3d}, {:^3d}".format(r, g, b)

        self.color_button_system.setStyleSheet("background-color:rgb({});".format(strRGB))

    def refresh_user(self, user: float):
        self.lbl_user_value.setText(f'<font color="{self.color_button_user.color()}">{user} %</font>')

    def refresh_system(self, system: float):
        self.lbl_system_value.setText(f'<font color="{self.color_button_system.color()}">{system} %</font>')

    def refresh_idle(self, idle: float):
        self.lbl_idle_value.setText(f'<font color="{self.color_button_idle.color()}">{idle} %</font>')

    def refresh_process_number(self, process_number: int):
        self.lbl_processes_value.setText(f"{process_number}")

    def refresh_cumulative_threads(self, cumulative_threads: int):
        self.lbl_threads_value.setText(f"{cumulative_threads}")
