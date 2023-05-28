#!/usr/bin/env python3

import psutil

from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)

from utility_bytes2human import bytes2human


class SystemMemoryWorker(QObject):
    finished = pyqtSignal()

    updated_system_memory_total = pyqtSignal(str)
    updated_system_memory_available = pyqtSignal(str)
    updated_system_memory_percent = pyqtSignal(str)
    updated_system_memory_used = pyqtSignal(str)
    updated_system_memory_free = pyqtSignal(str)
    updated_system_memory_active = pyqtSignal(str)
    updated_system_memory_inactive = pyqtSignal(str)
    updated_system_memory_buffers = pyqtSignal(str)
    updated_system_memory_cached = pyqtSignal(str)
    updated_system_memory_shared = pyqtSignal(str)
    updated_system_memory_slab = pyqtSignal(str)
    updated_system_memory_wired = pyqtSignal(str)

    # System Memory Chart Pie
    updated_system_memory_free_raw = pyqtSignal(object)
    updated_system_memory_wired_raw = pyqtSignal(object)
    updated_system_memory_active_raw = pyqtSignal(object)
    updated_system_memory_inactive_raw = pyqtSignal(object)

    # noinspection PyUnresolvedReferences
    def refresh(self):
        # System Memory
        virtual_memory = psutil.virtual_memory()
        if hasattr(virtual_memory, "total"):
            self.updated_system_memory_total.emit(bytes2human(virtual_memory.total))
        if hasattr(virtual_memory, "available"):
            self.updated_system_memory_available.emit(bytes2human(virtual_memory.available))
        if hasattr(virtual_memory, "percent"):
            self.updated_system_memory_percent.emit(bytes2human(virtual_memory.percent))
        if hasattr(virtual_memory, "used"):
            self.updated_system_memory_used.emit(bytes2human(virtual_memory.used))
        if hasattr(virtual_memory, "free"):
            self.updated_system_memory_free.emit(bytes2human(virtual_memory.free))
            self.updated_system_memory_free_raw.emit(virtual_memory.free)
        if hasattr(virtual_memory, "active"):
            self.updated_system_memory_active.emit(bytes2human(virtual_memory.active))
            self.updated_system_memory_active_raw.emit(virtual_memory.active)
        if hasattr(virtual_memory, "inactive"):
            tmp_value = virtual_memory.inactive
            self.updated_system_memory_inactive.emit(bytes2human(tmp_value))
            self.updated_system_memory_inactive_raw.emit(tmp_value)
        if hasattr(virtual_memory, "buffers"):
            self.updated_system_memory_buffers.emit(bytes2human(virtual_memory.buffers))
        if hasattr(virtual_memory, "cached"):
            self.updated_system_memory_cached.emit(bytes2human(virtual_memory.cached))
        if hasattr(virtual_memory, "shared"):
            self.updated_system_memory_shared.emit(bytes2human(virtual_memory.shared))
        if hasattr(virtual_memory, "slab"):
            self.updated_system_memory_slab.emit(bytes2human(virtual_memory.slab))
        if hasattr(virtual_memory, "wired"):
            self.updated_system_memory_wired.emit(bytes2human(virtual_memory.wired))
            self.updated_system_memory_wired_raw.emit(virtual_memory.wired)

        self.finished.emit()
