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
