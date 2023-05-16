#!/usr/bin/env python3

import os
import time

import psutil
from PyQt5.QtCore import (
    pyqtSignal as Signal,
    QObject,
)

from .utils import bytes2human


class PSUtilsWorker(QObject):
    finished = Signal()
    # CPU
    updated_cpu_user = Signal(float)
    updated_cpu_system = Signal(float)
    updated_cpu_idle = Signal(float)
    updated_cpu_cumulative_threads = Signal(int)
    updated_cpu_process_number = Signal(int)

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
    updated_system_memory_free_raw = Signal(int)
    updated_system_memory_wired_raw = Signal(int)
    updated_system_memory_active_raw = Signal(int)
    updated_system_memory_inactive_raw = Signal(int)

    # Disk Activity
    updated_disk_activity_reads_in = Signal(int)
    updated_disk_activity_writes_out = Signal(int)
    updated_disk_activity_reads_in_sec = Signal(int)
    updated_disk_activity_writes_out_sec = Signal(int)

    updated_disk_activity_data_read = Signal(str)
    updated_disk_activity_data_written = Signal(str)
    updated_disk_activity_data_read_sec = Signal(str)
    updated_disk_activity_data_written_sec = Signal(str)

    updated_disk_activity_bandwidth_value = Signal(str)

    # Disk Usage
    updated_mounted_disk_partitions = Signal(dict)

    # noinspection PyUnresolvedReferences
    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.updated_cpu_user.emit(cpu_times_percent.user)
        self.updated_cpu_system.emit(cpu_times_percent.system)
        self.updated_cpu_idle.emit(cpu_times_percent.idle)

        # CPU
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
            self.updated_system_memory_inactive.emit(bytes2human(virtual_memory.inactive))
            self.updated_system_memory_inactive_raw.emit(virtual_memory.inactive)
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

        # Disk Activity A last because it need to wait 1 entire second
        activity = psutil.disk_io_counters()
        activity_per_sec = disks_statistics_per_sec()

        self.updated_disk_activity_reads_in.emit(activity.read_count)
        self.updated_disk_activity_writes_out.emit(activity.write_count)
        self.updated_disk_activity_reads_in_sec.emit(activity_per_sec["read_count_per_sec"])
        self.updated_disk_activity_writes_out_sec.emit(activity_per_sec["write_count_per_sec"])

        self.updated_disk_activity_data_read.emit(bytes2human(activity.read_bytes))
        self.updated_disk_activity_data_written.emit(bytes2human(activity.write_bytes))
        self.updated_disk_activity_data_read_sec.emit(bytes2human(activity_per_sec["read_bytes_per_sec"], short=False))
        self.updated_disk_activity_data_written_sec.emit(
            bytes2human(activity_per_sec["write_bytes_per_sec"], short=False)
        )

        self.updated_disk_activity_bandwidth_value.emit(
            f"{bytes2human(activity_per_sec['read_bytes_per_sec'] + activity_per_sec['write_bytes_per_sec'])}/sec"
        )

        self.finished.emit()


def disks_statistics_per_sec():
    """
    Calculate IO usage by comparing IO statistics before and
    after 1 sec interval.

     {
     'read_bytes_per_sec': 0,
     'write_bytes_per_sec': 0,
     'read_count_per_sec': 0,
     'write_count_per_sec': 0
     }

    :return: Return a dict including total disks I/O activity.
    :rtype: dict
    """
    # first get disk io counters
    disks_before = psutil.disk_io_counters()

    # sleep 1 sec (yes easy trick)
    time.sleep(1)

    # then retrieve the same info again
    disks_after = psutil.disk_io_counters()

    # finally return calculated results by comparing data before and
    return {
        "read_bytes_per_sec": disks_after.read_bytes - disks_before.read_bytes,
        "write_bytes_per_sec": disks_after.write_bytes - disks_before.write_bytes,
        "read_count_per_sec": disks_after.read_count - disks_before.read_count,
        "write_count_per_sec": disks_after.write_count - disks_before.write_count,
    }
