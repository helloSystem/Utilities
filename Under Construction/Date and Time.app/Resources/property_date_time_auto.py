from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)


class DateTimeAutomatically(object):
    DateTimeAutomaticallyChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__date_time_auto = None
        self.DateTimeAutomatically = None

    @pyqtProperty(int)
    def DateTimeAutomatically(self):
        return self.__date_time_auto

    @DateTimeAutomatically.setter
    def DateTimeAutomatically(self, value):
        if value is None:
            value = False
        if self.__date_time_auto != value:
            self.__date_time_auto = value
            self.DateTimeAutomaticallyChanged.emit()

    def setDateTimeAutomatically(self, value):
        self.DateTimeAutomatically = value
