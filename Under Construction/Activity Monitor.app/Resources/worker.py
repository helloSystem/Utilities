#!/usr/bin/env python3

import os
import traceback, sys

import psutil
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QObject,
    QRunnable,
)

from bytes2human import bytes2human


class PSUtilsWorker(QObject):
    finished = pyqtSignal()

    # Disk Activity
    updated_disk_activity_reads_in = pyqtSignal(object)
    updated_disk_activity_writes_out = pyqtSignal(object)
    updated_disk_activity_data_read = pyqtSignal(object)
    updated_disk_activity_data_written = pyqtSignal(object)

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


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except(Exception, BaseException):
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
