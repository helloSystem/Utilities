#!/usr/bin/env python3

from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)

from PyQt5.QtWidgets import QWidget
from .ui_tab_cpu import Ui_TabCPU


class TabCpu(QWidget, Ui_TabCPU):
    data_user_changed = pyqtSignal()
    data_system_changed = pyqtSignal()
    data_idle_changed = pyqtSignal()
    data_nice_changed = pyqtSignal()
    data_irq_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()

        self.__user = None
        self.__idle = None
        self.__system = None
        self.__nice = None
        self.__irq = None

        self.setupUi(self)

        self.setupConnect()
        self.color_picker_user_value.setColor("green")
        self.color_picker_system_value.setColor("red")
        self.color_picker_nice_value.setColor("blue")
        self.color_picker_irq_value.setColor("orange")
        self.color_picker_idle_value.setColor("black")

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

    @pyqtProperty(float)
    def nice(self):
        return self.__nice

    @nice.setter
    def nice(self, value):
        if self.__nice != value:
            self.__nice = value
            self.data_nice_changed.emit()

    def set_nice(self, value):
        self.nice = value

    @pyqtProperty(float)
    def irq(self):
        return self.__irq

    @irq.setter
    def irq(self, value):
        if self.__irq != value:
            self.__irq = value
            self.data_irq_changed.emit()

    def set_irq(self, value):
        self.irq = value

    def setupConnect(self):
        self.data_idle_changed.connect(self.refresh_idle)
        self.data_user_changed.connect(self.refresh_user)
        self.data_system_changed.connect(self.refresh_system)
        self.data_nice_changed.connect(self.refresh_nice)
        self.data_irq_changed.connect(self.refresh_irq)

        self.color_picker_system_value.colorChanged.connect(self.refresh_color_system)
        self.color_picker_user_value.colorChanged.connect(self.refresh_color_user)
        self.color_picker_idle_value.colorChanged.connect(self.refresh_color_idle)
        self.color_picker_nice_value.colorChanged.connect(self.refresh_color_nice)
        self.color_picker_irq_value.colorChanged.connect(self.refresh_color_irq)

    def refresh_user(self):
        if self.__user is not None:
            if self.label_user_value.text() != f"{self.__user}":
                self.label_user_value.setText(f"{self.__user}")
            if self.widget_graph.user != self.__user / 2:
                self.widget_graph.user = self.__user / 2

    def refresh_system(self):
        if self.__system is not None:
            if self.label_system_value.text() != f"{self.__system}":
                self.label_system_value.setText(f"{self.__system}")
            if self.widget_graph.system != self.__system / 2:
                self.widget_graph.system = self.__system / 2

    def refresh_idle(self):
        if self.__idle is not None:
            if self.label_idle_value.text() != f"{self.__idle}":
                self.label_idle_value.setText(f"{self.__idle}")

            # idle color is just the background color, then it is bind to refresh
            self.widget_graph.refresh()

    def refresh_nice(self):
        if self.__nice is not None and self.label_nice_value.text() != f"{self.__nice}":
            self.label_nice_value.setText(f"{self.__nice}")

    def refresh_irq(self):
        if self.__irq is not None and self.label_irq_value.text() != f"{self.__irq}":
            self.label_irq_value.setText(f"{self.__irq}")

    def refresh_process_number(self, process_number: int):
        self.label_processes_value.setText("%d" % process_number)

    def refresh_cumulative_threads(self, cumulative_threads: int):
        if self.label_threads_value.text() != f"{cumulative_threads}":
            self.label_threads_value.setText(f"{cumulative_threads}")

    def refresh_color_system(self):
        self.label_system_value.setStyleSheet("color: %s;" % self.color_picker_system_value.color())
        self.label_system_unit.setStyleSheet("color: %s;" % self.color_picker_system_value.color())
        self.widget_graph.color_system = self.color_picker_system_value.color()

    def refresh_color_user(self):
        self.label_user_value.setStyleSheet("color: %s;" % self.color_picker_user_value.color())
        self.label_user_unit.setStyleSheet("color: %s;" % self.color_picker_user_value.color())
        self.widget_graph.color_user = self.color_picker_user_value.color()

    def refresh_color_idle(self):
        self.label_idle_value.setStyleSheet("color: %s;" % self.color_picker_idle_value.color())
        self.label_idle_unit.setStyleSheet("color: %s;" % self.color_picker_idle_value.color())
        self.widget_graph.color_idle = self.color_picker_idle_value.color()

    def refresh_color_nice(self):
        self.label_nice_value.setStyleSheet("color: %s;" % self.color_picker_nice_value.color())
        self.label_nice_unit.setStyleSheet("color: %s;" % self.color_picker_nice_value.color())
        # self.widget_graph.color_nice = self.color_picker_nice_value.color()

    def refresh_color_irq(self):
        self.label_irq_value.setStyleSheet("color: %s;" % self.color_picker_irq_value.color())
        self.label_irq_unit.setStyleSheet("color: %s;" % self.color_picker_irq_value.color())
        # self.widget_graph.color_irq = self.color_picker_irq_value.color()
