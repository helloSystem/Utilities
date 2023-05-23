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

    def __init__(self, parent=None):
        super().__init__()

        self.__user = None
        self.__idle = None
        self.__system = None

        self.setupUi(self)

        self.setupConnect()
        self.color_picker_user_value.setColor("green")
        self.color_picker_system_value.setColor("red")
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

    def setupConnect(self):
        self.data_idle_changed.connect(self.refresh_idle)
        self.data_user_changed.connect(self.refresh_user)
        self.data_system_changed.connect(self.refresh_system)

        self.color_picker_system_value.colorChanged.connect(self.refresh_color_system)
        self.color_picker_user_value.colorChanged.connect(self.refresh_color_user)
        self.color_picker_idle_value.colorChanged.connect(self.refresh_color_idle)

    def refresh_user(self):
        if self.__user:
            self.label_user_value.setText("%s %s" % (self.__user, "%"))
            self.widget_graph.user = self.__user / 2

    def refresh_system(self):
        if self.__system:
            self.label_system_value.setText("%s %s" % (self.__system, "%"))
            self.widget_graph.system = self.__system / 2

    def refresh_idle(self):
        if self.__idle:
            self.label_idle_value.setText("%s %s" % (self.__idle, "%"))
            # idle color is just the background color, then it is bind to refresh
            self.widget_graph.refresh()

    def refresh_process_number(self, process_number: int):
        self.label_processes_value.setText("%d" % process_number)

    def refresh_cumulative_threads(self, cumulative_threads: int):
        self.label_threads_value.setText("%d" % cumulative_threads)

    def refresh_color_system(self):
        self.label_system_value.setStyleSheet("color: %s;" % self.color_picker_system_value.color())
        self.widget_graph.color_system = self.color_picker_system_value.color()

    def refresh_color_user(self):
        self.label_user_value.setStyleSheet("color: %s;" % self.color_picker_user_value.color())
        self.widget_graph.color_user = self.color_picker_user_value.color()

    def refresh_color_idle(self):
        self.label_idle_value.setStyleSheet("color: %s;" % self.color_picker_idle_value.color())
        self.widget_graph.color_idle = self.color_picker_idle_value.color()
