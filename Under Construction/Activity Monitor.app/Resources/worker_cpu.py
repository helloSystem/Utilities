#!/usr/bin/env python3


import psutil

from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)


class CPUWorker(QObject):
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

    # noinspection PyUnresolvedReferences
    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.updated_cpu_user.emit(cpu_times_percent.user)
        self.updated_cpu_system.emit(cpu_times_percent.system)
        self.updated_cpu_nice.emit(cpu_times_percent.nice)
        self.updated_cpu_irq.emit(cpu_times_percent.irq)
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

        self.finished.emit()
