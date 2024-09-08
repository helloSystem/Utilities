import os

from PyQt5.QtCore import QFile, QFileInfo, QTextCodec
from PyQt5.QtCore import pyqtProperty, pyqtSignal


class TimeZoneProperty(object):
    TimeZoneChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):

        self.__timezone_default_path = "/etc/timezone"
        self.__timezone = None
        self.TimeZone = None
        self.timezone_file = None

    @pyqtProperty(str)
    def TimeZone(self):
        return self.__timezone

    @TimeZone.setter
    def TimeZone(self, value):
        if value is None:
            info1 = QFileInfo(self.__timezone_default_path)
            if os.getenv("TZ"):
                value = os.environ.get("TZ")
            elif info1.exists() and (info1.isFile() or info1.isSymLink()):
                if info1.isSymLink():
                    info1 = QFileInfo(info1.symLinkTarget())
                if info1.isFile() and info1.isReadable():
                    try:
                        file_handle = QFile(info1.absoluteFilePath())
                        file_handle.open(QFile.ReadOnly)
                        data = file_handle.readAll()
                        codec = QTextCodec.codecForUtfText(data)
                        value = codec.toUnicode(data).strip("\n")

                        # for line in QTextCodec.codecForUtfText(data):
                        #     if line.startswith("#"):
                        #         pass
                        #     else:
                        #         value =  line.strip("\n")
                    except (Exception, BaseException):
                        raise IOError("Problem reading file %s" % info1.absoluteFilePath())

        if self.__timezone != value:
            self.__timezone = value
            self.TimeZoneChanged.emit()

    def setTimeZone(self, value):
        self.TimeZone = value
