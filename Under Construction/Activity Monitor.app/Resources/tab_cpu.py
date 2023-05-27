#!/usr/bin/env python3

from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)


class TabCpu(object):
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

    def refresh_user(self):
        self.label_user_value.setText(f"{self.__user}")
        self.widget_graph.user = self.__user / 2

    def refresh_system(self):
        self.label_system_value.setText(f"{self.__system}")
        self.widget_graph.system = self.__system / 2

    def refresh_idle(self):
        self.label_idle_value.setText(f"{self.__idle}")
        # idle color is just the background color, then it is bind to refresh
        self.widget_graph.refresh()

    def refresh_nice(self):
        self.label_nice_value.setText(f"{self.__nice}")

    def refresh_irq(self):
        self.label_irq_value.setText(f"{self.__irq}")

    def refresh_process_number(self, process_number: int):
        self.label_processes_value.setText("%d" % process_number)

    def refresh_cumulative_threads(self, cumulative_threads: int):
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
