#!/usr/bin/env python3

import os

import psutil
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal as Signal,
    QObject,
)

from bytes2human import bytes2human


class PSUtilsWorker(QObject):
    finished = Signal()
    # CPU
    updated_cpu_user = Signal(object)
    updated_cpu_system = Signal(object)
    updated_cpu_idle = Signal(object)
    updated_cpu_nice = Signal(object)
    updated_cpu_irq = Signal(object)
    updated_cpu_cumulative_threads = Signal(object)
    updated_cpu_process_number = Signal(object)
    clear_cpu_graph_history = Signal(object)

    # System Memory
    updated_system_memory_total = Signal(str)
    updated_system_memory_available = Signal(str)
    updated_system_memory_percent = Signal(str)
    updated_system_memory_used = Signal(str)
    updated_system_memory_free = Signal(str)
    updated_system_memory_active = Signal(str)
    updated_system_memory_inactive = Signal(str)
    updated_system_memory_buffers = Signal(str)
    updated_system_memory_cached = Signal(str)
    updated_system_memory_shared = Signal(str)
    updated_system_memory_slab = Signal(str)
    updated_system_memory_wired = Signal(str)

    # System Memory Chart Pie
    updated_system_memory_free_raw = Signal(object)
    updated_system_memory_wired_raw = Signal(object)
    updated_system_memory_active_raw = Signal(object)
    updated_system_memory_inactive_raw = Signal(object)

    # Disk Activity
    updated_disk_activity_reads_in = Signal(object)
    updated_disk_activity_writes_out = Signal(object)
    updated_disk_activity_data_read = Signal(object)
    updated_disk_activity_data_written = Signal(object)

    # Disk Usage
    updated_mounted_disk_partitions = Signal(dict)

    # Network
    updated_network_packets_in = Signal(object)
    updated_network_packets_out = Signal(object)
    updated_network_data_received = Signal(object)
    updated_network_data_sent = Signal(object)

    # Icon Cache
    updated_icons_cache = Signal(object)

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

        # Disk Usage
        data = {}
        item_number = 0
        for part in psutil.disk_partitions(all=False):
            if os.name == "nt":
                if "cdrom" in part.opts or part.fstype == "":
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            data[item_number] = {
                "device": part.device,
                "total": bytes2human(usage.total),
                "used": bytes2human(usage.used),
                "used_in_bytes": f"{'{:,}'.format(usage.used)} bytes",
                "used_raw": usage.used,
                "free": bytes2human(usage.free),
                "free_in_bytes": f"{'{:,}'.format(usage.free)} bytes",
                "free_raw": usage.free,
                "percent": int(usage.percent),
                "fstype": part.fstype,
                "mountpoint": part.mountpoint,
            }
            item_number += 1
        self.updated_mounted_disk_partitions.emit(data)

        # Disk activity
        activity = psutil.disk_io_counters()

        self.updated_disk_activity_reads_in.emit(activity.read_count)
        self.updated_disk_activity_writes_out.emit(activity.write_count)
        self.updated_disk_activity_data_read.emit(activity.read_bytes)
        self.updated_disk_activity_data_written.emit(activity.write_bytes)

        # Network
        net_io_counters = psutil.net_io_counters()

        self.updated_network_packets_in.emit(net_io_counters.packets_recv)
        self.updated_network_packets_out.emit(net_io_counters.packets_sent)
        self.updated_network_data_received.emit(net_io_counters.bytes_recv)
        self.updated_network_data_sent.emit(net_io_counters.bytes_sent)

        self.finished.emit()
