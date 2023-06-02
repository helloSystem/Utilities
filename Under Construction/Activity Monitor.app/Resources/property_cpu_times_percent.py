from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)
from PyQt5.QtGui import QColor


class CPUTimesPercent(object):
    cpu_user_changed = pyqtSignal()
    cpu_system_changed = pyqtSignal()
    cpu_idle_changed = pyqtSignal()
    cpu_nice_changed = pyqtSignal()
    cpu_irq_changed = pyqtSignal()

    cpu_user_color_changed = pyqtSignal()
    cpu_system_color_changed = pyqtSignal()
    cpu_idle_color_changed = pyqtSignal()
    cpu_nice_color_changed = pyqtSignal()
    cpu_irq_color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__user = 0.0
        self.__idle = 0.0
        self.__system = 0.0
        self.__nice = 0.0
        self.__irq = 0.0

        self.__user_color = QColor("black")
        self.__idle_color = QColor("black")
        self.__system_color = QColor("black")
        self.__nice_color = QColor("black")
        self.__irq_color = QColor("black")

    @pyqtProperty(float)
    def idle(self):
        return self.__idle

    @idle.setter
    def idle(self, value):
        if self.__idle != value:
            self.__idle = value
            self.cpu_idle_changed.emit()

    @pyqtProperty(float)
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if self.__user != value:
            self.__user = value
            self.cpu_user_changed.emit()

    @pyqtProperty(float)
    def system(self):
        return self.__system

    @system.setter
    def system(self, value):
        if self.__system != value:
            self.__system = value
            self.cpu_system_changed.emit()

    @pyqtProperty(float)
    def nice(self):
        return self.__nice

    @nice.setter
    def nice(self, value):
        if self.__nice != value:
            self.__nice = value
            self.cpu_nice_changed.emit()

    @pyqtProperty(float)
    def irq(self):
        return self.__irq

    @irq.setter
    def irq(self, value):
        if self.__irq != value:
            self.__irq = value
            self.cpu_irq_changed.emit()

    @pyqtProperty(QColor)
    def color_system(self):
        return self.__system_color

    @color_system.setter
    def color_system(self, value):
        if self.__system_color != value:
            self.__system_color = value
            self.cpu_system_color_changed.emit()

    @pyqtProperty(QColor)
    def color_user(self):
        return self.__user_color

    @color_user.setter
    def color_user(self, value):
        if self.__user_color != value:
            self.__user_color = value
            self.cpu_user_color_changed.emit()


    @pyqtProperty(QColor)
    def color_idle(self):
        return self.__idle_color

    @color_idle.setter
    def color_idle(self, value):
        if self.__idle_color != value:
            self.__idle_color = value
            self.cpu_idle_color_changed.emit()

    @pyqtProperty(QColor)
    def color_nice(self):
        return self.__nice_color

    @color_nice.setter
    def color_nice(self, value):
        if self.__nice_color != value:
            self.__nice_color = value
            self.cpu_nice_color_changed.emit()

    @pyqtProperty(QColor)
    def color_irq(self):
        return self.__irq_color

    @color_irq.setter
    def color_irq(self, value):
        if self.__irq_color != value:
            self.__irq_color = value
            self.cpu_irq_color_changed.emit()

    def set_idle(self, value):
        self.idle = value

    def set_user(self, value):
        self.user = value

    def set_system(self, value):
        self.system = value

    def set_nice(self, value):
        self.nice = value

    def set_irq(self, value):
        self.irq = value
