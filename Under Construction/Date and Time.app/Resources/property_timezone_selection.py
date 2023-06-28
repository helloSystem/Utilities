from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)


class TimeZoneSelection(object):
    TimeZoneSelectionChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__timezone_selection = None
        self.TimeZoneSelection = None

    @pyqtProperty(int)
    def TimeZoneSelection(self):
        return self.__timezone_selection

    @TimeZoneSelection.setter
    def TimeZoneSelection(self, value):
        if value is None:
            value = 0
        if self.__timezone_selection != value:
            self.__timezone_selection = value
            self.TimeZoneSelectionChanged.emit()

    def setTimeZoneSelection(self, value):
        self.TimeZoneSelection = value
