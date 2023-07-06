from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal, QTime
)


class Time(object):
    TimeChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__time = None
        self.time = None

    @pyqtProperty(QTime)
    def time(self):
        return self.__time

    @time.setter
    def time(self, value):
        if value is None:
            value = QTime.currentTime()
        if self.__time != value:
            self.__time = value
            self.TimeChanged.emit()

    def setTime(self, value):
        self.time = value
