#!/usr/bin/env python3

import os

import psutil
from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)

from utility import bytes2human


class PSUtilsWorker(QObject):
    finished = pyqtSignal()
    # CPU
    updated_cpu_user = pyqtSignal(object)
    updated_cpu_system = pyqtSignal(object)
    updated_cpu_idle = pyqtSignal(object)
    updated_cpu_nice = pyqtSignal(object)
    updated_cpu_irq = pyqtSignal(object)
    updated_cpu_cumulative_threads = pyqtSignal(object)
    updated_cpu_process_number = pyqtSignal(object)
    clear_cpu_graph_history = pyqtSignal(object)

    # System Memory
    updated_system_memory_total = pyqtSignal(object)
    updated_system_memory_available = pyqtSignal(object)
    updated_system_memory_percent = pyqtSignal(object)
    updated_system_memory_used = pyqtSignal(object)
    updated_system_memory_free = pyqtSignal(object)
    updated_system_memory_active = pyqtSignal(object)
    updated_system_memory_inactive = pyqtSignal(object)
    updated_system_memory_buffers = pyqtSignal(object)
    updated_system_memory_cached = pyqtSignal(object)
    updated_system_memory_shared = pyqtSignal(object)
    updated_system_memory_slab = pyqtSignal(object)
    updated_system_memory_wired = pyqtSignal(object)

    # Disk Activity
    updated_disk_activity_read_count = pyqtSignal(object)
    updated_disk_activity_write_count = pyqtSignal(object)
    updated_disk_activity_read_bytes = pyqtSignal(object)
    updated_disk_activity_write_bytes = pyqtSignal(object)
    updated_disk_activity_read_time = pyqtSignal(object)
    updated_disk_activity_write_time = pyqtSignal(object)
    updated_disk_activity_read_merged_count = pyqtSignal(object)
    updated_disk_activity_write_merged_count = pyqtSignal(object)

    # Disk Usage
    updated_mounted_disk_partitions = pyqtSignal(dict)

    # Network
    updated_network_packets_in = pyqtSignal(object)
    updated_network_packets_out = pyqtSignal(object)
    updated_network_data_received = pyqtSignal(object)
    updated_network_data_sent = pyqtSignal(object)

    # Icon Cache
    updated_icons_cache = pyqtSignal(object)

    # noinspection PyUnresolvedReferences
    def refresh(self):
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

        # CPU
        cpu_times_percent = psutil.cpu_times_percent()
        self.updated_cpu_user.emit(cpu_times_percent.user)
        self.updated_cpu_system.emit(cpu_times_percent.system)
        self.updated_cpu_nice.emit(cpu_times_percent.nice)
        self.updated_cpu_irq.emit(cpu_times_percent.irq)
        self.updated_cpu_idle.emit(cpu_times_percent.idle)

        cumulative_threads = 0
        for proc in psutil.process_iter():
            try:
                cumulative_threads += proc.num_threads()
            except psutil.NoSuchProcess:
                pass
        self.updated_cpu_cumulative_threads.emit(cumulative_threads)
        self.updated_cpu_process_number.emit(len(psutil.pids()))

        # System Memory
        virtual_memory = psutil.virtual_memory()
        if hasattr(virtual_memory, "total"):
            self.updated_system_memory_total.emit(virtual_memory.total)
        if hasattr(virtual_memory, "available"):
            self.updated_system_memory_available.emit(virtual_memory.available)
        if hasattr(virtual_memory, "percent"):
            self.updated_system_memory_percent.emit(virtual_memory.percent)
        if hasattr(virtual_memory, "used"):
            self.updated_system_memory_used.emit(virtual_memory.used)
        if hasattr(virtual_memory, "free"):
            self.updated_system_memory_free.emit(virtual_memory.free)
        if hasattr(virtual_memory, "active"):
            self.updated_system_memory_active.emit(virtual_memory.active)
        if hasattr(virtual_memory, "inactive"):
            self.updated_system_memory_inactive.emit(virtual_memory.inactive)
        if hasattr(virtual_memory, "buffers"):
            self.updated_system_memory_buffers.emit(virtual_memory.buffers)
        if hasattr(virtual_memory, "cached"):
            self.updated_system_memory_cached.emit(virtual_memory.cached)
        if hasattr(virtual_memory, "shared"):
            self.updated_system_memory_shared.emit(virtual_memory.shared)
        if hasattr(virtual_memory, "slab"):
            self.updated_system_memory_slab.emit(virtual_memory.slab)
        if hasattr(virtual_memory, "wired"):
            self.updated_system_memory_wired.emit(virtual_memory.wired)

        # Disk activity
        disk_io_counters = psutil.disk_io_counters()
        if hasattr(disk_io_counters, "read_count"):
            self.updated_disk_activity_read_count.emit(disk_io_counters.read_count)
        if hasattr(disk_io_counters, "write_count"):
            self.updated_disk_activity_write_count.emit(disk_io_counters.write_count)
        if hasattr(disk_io_counters, "read_bytes"):
            self.updated_disk_activity_read_bytes.emit(disk_io_counters.read_bytes)
        if hasattr(disk_io_counters, "write_bytes"):
            self.updated_disk_activity_write_bytes.emit(disk_io_counters.write_bytes)
        if hasattr(disk_io_counters, "read_time"):
            self.updated_disk_activity_read_time.emit(disk_io_counters.read_time)
        if hasattr(disk_io_counters, "write_time"):
            self.updated_disk_activity_write_time.emit(disk_io_counters.write_time)
        if hasattr(disk_io_counters, "busy_time"):
            self.updated_disk_activity_write_time.emit(disk_io_counters.busy_time)
        if hasattr(disk_io_counters, "read_merged_count"):
            self.updated_disk_activity_read_merged_count.emit(disk_io_counters.read_merged_count)
        if hasattr(disk_io_counters, "write_merged_count"):
            self.updated_disk_activity_write_merged_count.emit(disk_io_counters.write_merged_count)

        # Network
        net_io_counters = psutil.net_io_counters()

        self.updated_network_packets_in.emit(net_io_counters.packets_recv)
        self.updated_network_packets_out.emit(net_io_counters.packets_sent)
        self.updated_network_data_received.emit(net_io_counters.bytes_recv)
        self.updated_network_data_sent.emit(net_io_counters.bytes_sent)

        self.finished.emit()
