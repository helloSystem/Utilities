from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)


class Time(object):
    TimeChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__time = None
        self.Time = None

    @pyqtProperty(int)
    def Time(self):
        return self.__time

    @Time.setter
    def Time(self, value):
        if value is None:
            value = 0.0
        if self.__time != value:
            self.__time = value
            self.TimeChanged.emit()

    def setTime(self, value):
        self.Time = value
