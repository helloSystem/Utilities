from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)

from dateutil.zoneinfo import getzoneinfofile_stream, ZoneInfoFile
class TimeZone(object):
    TimeZoneChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__timezone = None
        self.TimeZone = None

    @pyqtProperty(str)
    def TimeZone(self):
        return self.__timezone

    @TimeZone.setter
    def TimeZone(self, value):
        if value is None:
            value = "Europe/Paris"
        if self.__timezone != value:
            self.__timezone = value
            self.TimeZoneChanged.emit()

    def setTimeZone(self, value):
        self.TimeZone = value
