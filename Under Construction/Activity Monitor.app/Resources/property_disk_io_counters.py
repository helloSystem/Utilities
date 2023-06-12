from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)
from PyQt5.QtGui import QColor


class DiskIOCounters(object):
    # A Storage Class in charge to emit signal when truly change a value
    # that is a lot of code but save the CPU then the planet ...

    disk_io_counters_read_count_changed = pyqtSignal()
    disk_io_counters_write_count_changed = pyqtSignal()
    disk_io_counters_read_bytes_changed = pyqtSignal()
    disk_io_counters_write_bytes_changed = pyqtSignal()
    disk_io_counters_read_time_changed = pyqtSignal()
    disk_io_counters_write_time_changed = pyqtSignal()
    disk_io_counters_busy_time_changed = pyqtSignal()
    disk_io_counters_read_merged_count_changed = pyqtSignal()
    disk_io_counters_write_merged_count_changed = pyqtSignal()

    disk_io_counters_read_count_color_changed = pyqtSignal()
    disk_io_counters_write_count_color_changed = pyqtSignal()
    disk_io_counters_read_bytes_color_changed = pyqtSignal()
    disk_io_counters_write_bytes_color_changed = pyqtSignal()
    disk_io_counters_read_time_color_changed = pyqtSignal()
    disk_io_counters_write_time_color_changed = pyqtSignal()
    disk_io_counters_busy_time_color_changed = pyqtSignal()
    disk_io_counters_read_merged_count_color_changed = pyqtSignal()
    disk_io_counters_write_merged_count_color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__disk_io_counters_read_count = None
        self.__disk_io_counters_write_count = None
        self.__disk_io_counters_read_bytes = None
        self.__disk_io_counters_write_bytes = None
        self.__disk_io_counters_read_time = None
        self.__disk_io_counters_write_time = None
        self.__disk_io_counters_busy_time = None
        self.__disk_io_counters_read_merged_count = None
        self.__disk_io_counters_write_merged_count = None

        self.__disk_io_counters_read_count_color = None
        self.__disk_io_counters_write_count_color = None
        self.__disk_io_counters_read_bytes_color = None
        self.__disk_io_counters_write_bytes_color = None
        self.__disk_io_counters_read_time_color = None
        self.__disk_io_counters_write_time_color = None
        self.__disk_io_counters_busy_time_color = None
        self.__disk_io_counters_read_merged_count_color = None
        self.__disk_io_counters_write_merged_count_color = None

        self.disk_io_counters_read_count = None
        self.disk_io_counters_write_count = None
        self.disk_io_counters_read_bytes = None
        self.disk_io_counters_write_bytes = None
        self.disk_io_counters_read_time = None
        self.disk_io_counters_write_time = None
        self.disk_io_counters_busy_time = None
        self.disk_io_counters_read_merged_count = None
        self.disk_io_counters_write_merged_count = None

        self.disk_io_counters_read_count_color = None
        self.disk_io_counters_write_count_color = None
        self.disk_io_counters_read_bytes_color = None
        self.disk_io_counters_write_bytes_color = None
        self.disk_io_counters_read_time_color = None
        self.disk_io_counters_write_time_color = None
        self.disk_io_counters_busy_time_color = None
        self.disk_io_counters_read_merged_count_color = None
        self.disk_io_counters_write_merged_count_color = None

    def set_disk_io_counters_read_count(self, value):
        self.disk_io_counters_read_count = value

    def set_disk_io_counters_write_count(self, value):
        self.disk_io_counters_write_count = value

    def set_disk_io_counters_read_bytes(self, value):
        self.disk_io_counters_read_bytes = value

    def set_disk_io_counters_write_bytes(self, value):
        self.disk_io_counters_write_bytes = value

    def set_disk_io_counters_read_time(self, value):
        self.disk_io_counters_read_time = value

    def set_disk_io_counters_write_time(self, value):
        self.disk_io_counters_write_time = value

    def set_disk_io_counters_busy_time(self, value):
        self.disk_io_counters_busy_time = value

    def set_disk_io_counters_read_merged_count(self, value):
        self.disk_io_counters_read_merged_count = value

    def set_disk_io_counters_write_merged_count(self, value):
        self.disk_io_counters_write_merged_count = value

    @pyqtProperty(int)
    def disk_io_counters_read_count(self):
        return self.__disk_io_counters_read_count

    @disk_io_counters_read_count.setter
    def disk_io_counters_read_count(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_read_count != value:
            self.__disk_io_counters_read_count = value
            self.disk_io_counters_read_count_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_write_count(self):
        return self.__disk_io_counters_write_count

    @disk_io_counters_write_count.setter
    def disk_io_counters_write_count(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_write_count != value:
            self.__disk_io_counters_write_count = value
            self.disk_io_counters_write_count_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_read_bytes(self):
        return self.__disk_io_counters_read_bytes

    @disk_io_counters_read_bytes.setter
    def disk_io_counters_read_bytes(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_read_bytes != value:
            self.__disk_io_counters_read_bytes = value
            self.disk_io_counters_read_bytes_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_write_bytes(self):
        return self.__disk_io_counters_write_bytes

    @disk_io_counters_write_bytes.setter
    def disk_io_counters_write_bytes(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_write_bytes != value:
            self.__disk_io_counters_write_bytes = value
            self.disk_io_counters_write_bytes_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_read_time(self):
        return self.__disk_io_counters_read_time

    @disk_io_counters_read_time.setter
    def disk_io_counters_read_time(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_read_time != value:
            self.__disk_io_counters_read_time = value
            self.disk_io_counters_read_time_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_write_time(self):
        return self.__disk_io_counters_write_time

    @disk_io_counters_write_time.setter
    def disk_io_counters_write_time(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_write_time != value:
            self.__disk_io_counters_write_time = value
            self.disk_io_counters_write_time_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_busy_time(self):
        return self.__disk_io_counters_busy_time

    @disk_io_counters_busy_time.setter
    def disk_io_counters_busy_time(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_busy_time != value:
            self.__disk_io_counters_busy_time = value
            self.disk_io_counters_busy_time_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_read_merged_count(self):
        return self.__disk_io_counters_read_merged_count

    @disk_io_counters_read_merged_count.setter
    def disk_io_counters_read_merged_count(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_read_merged_count != value:
            self.__disk_io_counters_read_merged_count = value
            self.disk_io_counters_read_merged_count_changed.emit()

    @pyqtProperty(int)
    def disk_io_counters_write_merged_count(self):
        return self.__disk_io_counters_write_merged_count

    @disk_io_counters_write_merged_count.setter
    def disk_io_counters_write_merged_count(self, value):
        if value is None:
            value = 0
        if self.__disk_io_counters_write_merged_count != value:
            self.__disk_io_counters_write_merged_count = value
            self.disk_io_counters_write_merged_count_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_read_count_color(self):
        return self.__disk_io_counters_read_count_color

    @disk_io_counters_read_count_color.setter
    def disk_io_counters_read_count_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_read_count_color != value:
            self.__disk_io_counters_read_count_color = value
            self.disk_io_counters_read_count_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_write_count_color(self):
        return self.__disk_io_counters_write_count_color

    @disk_io_counters_write_count_color.setter
    def disk_io_counters_write_count_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_write_count_color != value:
            self.__disk_io_counters_write_count_color = value
            self.disk_io_counters_write_count_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_read_bytes_color(self):
        return self.__disk_io_counters_read_bytes_color

    @disk_io_counters_read_bytes_color.setter
    def disk_io_counters_read_bytes_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_read_bytes_color != value:
            self.__disk_io_counters_read_bytes_color = value
            self.disk_io_counters_read_bytes_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_write_bytes_color(self):
        return self.__disk_io_counters_write_bytes_color

    @disk_io_counters_write_bytes_color.setter
    def disk_io_counters_write_bytes_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_write_bytes_color != value:
            self.__disk_io_counters_write_bytes_color = value
            self.disk_io_counters_write_bytes_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_read_time_color(self):
        return self.__disk_io_counters_read_time_color

    @disk_io_counters_read_time_color.setter
    def disk_io_counters_read_time_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_read_time_color != value:
            self.__disk_io_counters_read_time_color = value
            self.disk_io_counters_read_time_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_write_time_color(self):
        return self.__disk_io_counters_write_time_color

    @disk_io_counters_write_time_color.setter
    def disk_io_counters_write_time_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_write_time_color != value:
            self.__disk_io_counters_write_time_color = value
            self.disk_io_counters_write_time_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_busy_time_color(self):
        return self.__disk_io_counters_busy_time_color

    @disk_io_counters_busy_time_color.setter
    def disk_io_counters_busy_time_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_busy_time_color != value:
            self.__disk_io_counters_busy_time_color = value
            self.disk_io_counters_busy_time_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_read_merged_count_color(self):
        return self.__disk_io_counters_read_merged_count_color

    @disk_io_counters_read_merged_count_color.setter
    def disk_io_counters_read_merged_count_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_read_merged_count_color != value:
            self.__disk_io_counters_read_merged_count_color = value
            self.disk_io_counters_read_merged_count_color_changed.emit()

    @pyqtProperty(QColor)
    def disk_io_counters_write_merged_count_color(self):
        return self.__disk_io_counters_write_merged_count_color

    @disk_io_counters_write_merged_count_color.setter
    def disk_io_counters_write_merged_count_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__disk_io_counters_write_merged_count_color != value:
            self.__disk_io_counters_write_merged_count_color = value
            self.disk_io_counters_write_merged_count_color_changed.emit()
