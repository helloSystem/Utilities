from PyQt5.QtCore import (
    pyqtProperty, pyqtSignal
)
from PyQt5.QtGui import QColor


class VirtualMemory(object):
    # A Storage Class in charge to emit signal when truly change a value
    # that is a lot of code but save the CPU then the planet ...

    virtual_memory_total_changed = pyqtSignal()
    virtual_memory_available_changed = pyqtSignal()
    virtual_memory_percent_changed = pyqtSignal()
    virtual_memory_used_changed = pyqtSignal()
    virtual_memory_free_changed = pyqtSignal()
    virtual_memory_active_changed = pyqtSignal()
    virtual_memory_inactive_changed = pyqtSignal()
    virtual_memory_buffers_changed = pyqtSignal()
    virtual_memory_cached_changed = pyqtSignal()
    virtual_memory_shared_changed = pyqtSignal()
    virtual_memory_slab_changed = pyqtSignal()
    virtual_memory_wired_changed = pyqtSignal()

    virtual_memory_total_color_changed = pyqtSignal()
    virtual_memory_available_color_changed = pyqtSignal()
    virtual_memory_percent_color_changed = pyqtSignal()
    virtual_memory_used_color_changed = pyqtSignal()
    virtual_memory_free_color_changed = pyqtSignal()
    virtual_memory_active_color_changed = pyqtSignal()
    virtual_memory_inactive_color_changed = pyqtSignal()
    virtual_memory_buffers_color_changed = pyqtSignal()
    virtual_memory_cached_color_changed = pyqtSignal()
    virtual_memory_shared_color_changed = pyqtSignal()
    virtual_memory_slab_color_changed = pyqtSignal()
    virtual_memory_wired_color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__virtual_memory_total = None
        self.__virtual_memory_available = None
        self.__virtual_memory_percent = None
        self.__virtual_memory_used = None
        self.__virtual_memory_free = None
        self.__virtual_memory_active = None
        self.__virtual_memory_inactive = None
        self.__virtual_memory_buffers = None
        self.__virtual_memory_cached = None
        self.__virtual_memory_shared = None
        self.__virtual_memory_slab = None
        self.__virtual_memory_wired = None

        self.__virtual_memory_total_color = None
        self.__virtual_memory_available_color = None
        self.__virtual_memory_percent_color = None
        self.__virtual_memory_used_color = None
        self.__virtual_memory_free_color = None
        self.__virtual_memory_active_color = None
        self.__virtual_memory_inactive_color = None
        self.__virtual_memory_buffers_color = None
        self.__virtual_memory_cached_color = None
        self.__virtual_memory_shared_color = None
        self.__virtual_memory_slab_color = None
        self.__virtual_memory_wired_color = None

        self.virtual_memory_total = None
        self.virtual_memory_available = None
        self.virtual_memory_percent = None
        self.virtual_memory_used = None
        self.virtual_memory_free = None
        self.virtual_memory_active = None
        self.virtual_memory_inactive = None
        self.virtual_memory_buffers = None
        self.virtual_memory_cached = None
        self.virtual_memory_shared = None
        self.virtual_memory_slab = None
        self.virtual_memory_wired = None

        self.virtual_memory_total_color = None
        self.virtual_memory_available_color = None
        self.virtual_memory_percent_color = None
        self.virtual_memory_used_color = None
        self.virtual_memory_free_color = None
        self.virtual_memory_active_color = None
        self.virtual_memory_inactive_color = None
        self.virtual_memory_buffers_color = None
        self.virtual_memory_cached_color = None
        self.virtual_memory_shared_color = None
        self.virtual_memory_slab_color = None
        self.virtual_memory_wired_color = None

    @pyqtProperty(int)
    def virtual_memory_total(self):
        return self.__virtual_memory_total

    @virtual_memory_total.setter
    def virtual_memory_total(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_total != value:
            self.__virtual_memory_total = value
            self.virtual_memory_total_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_available(self):
        return self.__virtual_memory_available

    @virtual_memory_available.setter
    def virtual_memory_available(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_available != value:
            self.__virtual_memory_available = value
            self.virtual_memory_available_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_percent(self):
        return self.__virtual_memory_percent

    @virtual_memory_percent.setter
    def virtual_memory_percent(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_percent != value:
            self.__virtual_memory_percent = value
            self.virtual_memory_percent_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_used(self):
        return self.__virtual_memory_used

    @virtual_memory_used.setter
    def virtual_memory_used(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_used != value:
            self.__virtual_memory_used = value
            self.virtual_memory_used_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_free(self):
        return self.__virtual_memory_free

    @virtual_memory_free.setter
    def virtual_memory_free(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_free != value:
            self.__virtual_memory_free = value
            self.virtual_memory_free_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_active(self):
        return self.__virtual_memory_active

    @virtual_memory_active.setter
    def virtual_memory_active(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_active != value:
            self.__virtual_memory_active = value
            self.virtual_memory_active_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_inactive(self):
        return self.__virtual_memory_inactive

    @virtual_memory_inactive.setter
    def virtual_memory_inactive(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_inactive != value:
            self.__virtual_memory_inactive = value
            self.virtual_memory_inactive_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_buffers(self):
        return self.__virtual_memory_buffers

    @virtual_memory_buffers.setter
    def virtual_memory_buffers(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_buffers != value:
            self.__virtual_memory_buffers = value
            self.virtual_memory_buffers_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_cached(self):
        return self.__virtual_memory_cached

    @virtual_memory_cached.setter
    def virtual_memory_cached(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_cached != value:
            self.__virtual_memory_cached = value
            self.virtual_memory_cached_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_shared(self):
        return self.__virtual_memory_shared

    @virtual_memory_shared.setter
    def virtual_memory_shared(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_shared != value:
            self.__virtual_memory_shared = value
            self.virtual_memory_shared_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_slab(self):
        return self.__virtual_memory_slab

    @virtual_memory_slab.setter
    def virtual_memory_slab(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_slab != value:
            self.__virtual_memory_slab = value
            self.virtual_memory_slab_changed.emit()

    @pyqtProperty(int)
    def virtual_memory_wired(self):
        return self.__virtual_memory_wired

    @virtual_memory_wired.setter
    def virtual_memory_wired(self, value):
        if value is None:
            value = 0
        if self.__virtual_memory_wired != value:
            self.__virtual_memory_wired = value
            self.virtual_memory_wired_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_total_color(self):
        return self.__virtual_memory_total_color

    @virtual_memory_total_color.setter
    def virtual_memory_total_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_total_color != value:
            self.__virtual_memory_total_color = value
            self.virtual_memory_total_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_available_color(self):
        return self.__virtual_memory_available_color

    @virtual_memory_available_color.setter
    def virtual_memory_available_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_available_color != value:
            self.__virtual_memory_available_color = value
            self.virtual_memory_available_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_percent_color(self):
        return self.__virtual_memory_percent_color

    @virtual_memory_percent_color.setter
    def virtual_memory_percent_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_percent_color != value:
            self.__virtual_memory_percent_color = value
            self.virtual_memory_percent_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_used_color(self):
        return self.__virtual_memory_used_color

    @virtual_memory_used_color.setter
    def virtual_memory_used_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_used_color != value:
            self.__virtual_memory_used_color = value
            self.virtual_memory_used_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_free_color(self):
        return self.__virtual_memory_free_color

    @virtual_memory_free_color.setter
    def virtual_memory_free_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_free_color != value:
            self.__virtual_memory_free_color = value
            self.virtual_memory_free_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_active_color(self):
        return self.__virtual_memory_active_color

    @virtual_memory_active_color.setter
    def virtual_memory_active_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_active_color != value:
            self.__virtual_memory_active_color = value
            self.virtual_memory_active_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_inactive_color(self):
        return self.__virtual_memory_inactive_color

    @virtual_memory_inactive_color.setter
    def virtual_memory_inactive_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_inactive_color != value:
            self.__virtual_memory_inactive_color = value
            self.virtual_memory_inactive_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_buffers_color(self):
        return self.__virtual_memory_buffers_color

    @virtual_memory_buffers_color.setter
    def virtual_memory_buffers_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_buffers_color != value:
            self.__virtual_memory_buffers_color = value
            self.virtual_memory_buffers_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_cached_color(self):
        return self.__virtual_memory_cached_color

    @virtual_memory_cached_color.setter
    def virtual_memory_cached_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_cached_color != value:
            self.__virtual_memory_cached_color = value
            self.virtual_memory_cached_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_shared_color(self):
        return self.__virtual_memory_shared_color

    @virtual_memory_shared_color.setter
    def virtual_memory_shared_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_shared_color != value:
            self.__virtual_memory_shared_color = value
            self.virtual_memory_shared_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_slab_color(self):
        return self.__virtual_memory_slab_color

    @virtual_memory_slab_color.setter
    def virtual_memory_slab_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_slab_color != value:
            self.__virtual_memory_slab_color = value
            self.virtual_memory_slab_color_changed.emit()

    @pyqtProperty(QColor)
    def virtual_memory_wired_color(self):
        return self.__virtual_memory_wired_color

    @virtual_memory_wired_color.setter
    def virtual_memory_wired_color(self, value):
        if value is None:
            value = QColor("black")
        if self.__virtual_memory_wired_color != value:
            self.__virtual_memory_wired_color = value
            self.virtual_memory_wired_color_changed.emit()

    def set_virtual_memory_total(self, value):
        self.virtual_memory_total = value

    def set_virtual_memory_available(self, value):
        self.virtual_memory_available = value

    def set_virtual_memory_used(self, value):
        self.virtual_memory_used = value

    def set_virtual_memory_free(self, value):
        self.virtual_memory_free = value

    def set_virtual_memory_active(self, value):
        self.virtual_memory_active = value

    def set_virtual_memory_inactive(self, value):
        self.virtual_memory_inactive = value

    def set_virtual_memory_buffers(self, value):
        self.virtual_memory_buffers = value

    def set_virtual_memory_cached(self, value):
        self.virtual_memory_cached = value

    def set_virtual_memory_shared(self, value):
        self.virtual_memory_shared = value

    def set_virtual_memory_slab(self, value):
        self.virtual_memory_slab = value

    def set_virtual_memory_wired(self, value):
        self.virtual_memory_wired = value