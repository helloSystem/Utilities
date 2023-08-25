from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)


class TimeZoneOffset(object):
    TimeZoneOffsetChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__timezone_offset = None
        self.TimeZoneOffset = None

    @pyqtProperty(int)
    def TimeZoneOffset(self):
        return self.__timezone_offset

    @TimeZoneOffset.setter
    def TimeZoneOffset(self, value):
        if value is None:
            value = 0
        if self.__timezone_offset != value:
            self.__timezone_offset = value
            self.TimeZoneOffsetChanged.emit()

    def setTimeZoneOffset(self, value):
        self.TimeZoneOffset = value
