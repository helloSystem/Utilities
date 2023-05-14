#!/usr/bin/env python3

import os
import signal
import sys
import time

import psutil
from PyQt5.QtCore import (
    QTimer,
    Qt,
    QSize,
    pyqtSignal as Signal,
    QItemSelectionModel,
    QItemSelection,
    QObject,
    QThread

)
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QShortcut,
    QLabel,
    QColorDialog,
    QAction,
    QActionGroup,
    QWidgetAction,
    QMenuBar,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QTreeView,
    QFileIconProvider,

)

from activity_monitor.libs.about import About
from activity_monitor.libs.buttons import ColorButton
from activity_monitor.libs.utils import bytes2human
from activity_monitor.libs.chartpie import ChartPieItem, ChartPie

__app_name__ = "Activity Monitor"
__app_version__ = "0.1a"
__app_authors__ = ["Hierosme Alias Tuuux", "Contributors ..."]
__app_description__ = "View CPU, Memory, Network, Disk activities and interact with processes"
__app_url__ = "https://github.com/helloSystem/Utilities"


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

    # Disk Usage
    updated_mounted_disk_partitions = Signal(dict)

    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.updated_cpu_user.emit(cpu_times_percent.user)
        self.updated_cpu_system.emit(cpu_times_percent.system)
        self.updated_cpu_idle.emit(cpu_times_percent.idle)

        # CPU
        cumulative_threads = 0
        process_number = 0
        # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        p = psutil.Process()
        with p.oneshot():
            # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
            for proc in psutil.process_iter():
                try:
                    cumulative_threads += proc.num_threads()
                    process_number += 1
                except psutil.NoSuchProcess:
                    pass
        self.updated_cpu_cumulative_threads.emit(cumulative_threads)
        self.updated_cpu_process_number.emit(process_number)

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
        # Disks usage
        data = {}
        item_number = 0
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
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

        self.finished.emit()


class TabCpu(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.lbl_user_value = None
        self.color_button_user = None
        self.lbl_system_value = None
        self.color_button_system = None
        self.lbl_idle_value = None

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout_grid = QGridLayout()


        # User label
        lbl_user = QLabel("User:")
        lbl_user.setAlignment(Qt.AlignRight)
        # User label value
        self.lbl_user_value = QLabel("")
        self.lbl_user_value.setAlignment(Qt.AlignRight)
        # User Color button
        self.color_button_user = ColorButton(color="green")
        # Insert user labels on the right position
        layout_grid.addWidget(lbl_user, 1, 0, 1, 1)
        layout_grid.addWidget(self.lbl_user_value, 1, 1, 1, 1)
        layout_grid.addWidget(self.color_button_user, 1, 2, 1, 1)

        # System label
        lbl_system = QLabel("System:")
        lbl_system.setAlignment(Qt.AlignRight)
        # System label value
        self.lbl_system_value = QLabel("")
        self.lbl_system_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_system = ColorButton(color="blue")
        # self.color_button_system.clicked.connect(self._set_color_button_system())

        # Insert system labels on the right position
        layout_grid.addWidget(lbl_system, 2, 0, 1, 1)
        layout_grid.addWidget(self.lbl_system_value, 2, 1, 1, 1)
        layout_grid.addWidget(self.color_button_system, 2, 2, 1, 1)

        # Label Idle
        lbl_idle = QLabel("Idle:")
        lbl_idle.setAlignment(Qt.AlignRight)
        # Label Idle value
        self.lbl_idle_value = QLabel("")
        self.lbl_idle_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_idle = ColorButton(color="black")

        # Insert idle labels on the right position
        layout_grid.addWidget(lbl_idle, 3, 0, 1, 1)
        layout_grid.addWidget(self.lbl_idle_value, 3, 1, 1, 1)
        layout_grid.addWidget(self.color_button_idle, 3, 2, 1, 1)

        # Label threads
        lbl_threads = QLabel("Threads:")
        lbl_threads.setAlignment(Qt.AlignRight)
        # Label threads value
        self.lbl_threads_value = QLabel("")
        self.lbl_threads_value.setAlignment(Qt.AlignLeft)
        # Insert threads labels on the right position
        layout_grid.addWidget(lbl_threads, 1, 3, 1, 1)
        layout_grid.addWidget(self.lbl_threads_value, 1, 4, 1, 1)

        # Label Processes
        lbl_processes = QLabel("Processes:")
        lbl_processes.setAlignment(Qt.AlignRight)
        # Label Processes value
        self.lbl_processes_value = QLabel("")
        self.lbl_processes_value.setAlignment(Qt.AlignLeft)
        # Insert Processes labels on the right position
        layout_grid.addWidget(lbl_processes, 2, 3, 1, 1)
        layout_grid.addWidget(self.lbl_processes_value, 2, 4, 1, 1)

        lbl_cpu_usage = QLabel("CPU Usage")
        lbl_cpu_usage.setAlignment(Qt.AlignCenter)
        layout_grid.addWidget(lbl_cpu_usage, 0, 6, 1, 1)


        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def _set_color_button_system(self):
        color = QColorDialog.getColor()  # OpenColorDialog
        if color.isValid():
            print(color.name())  # ff5b87
            print(color.red(), color.green(), color.blue())  # 255 91 135

        r, g, b = color.red(), color.green(), color.blue()
        strRGB = "{:^3d}, {:^3d}, {:^3d}".format(r, g, b)

        self.color_button_system.setStyleSheet("background-color:rgb({});".format(strRGB))

    def refresh_user(self, user: float):
        self.lbl_user_value.setText(f'<font color="{self.color_button_user.color()}">{user} %</font>')

    def refresh_system(self, system: float):
        self.lbl_system_value.setText(f'<font color="{self.color_button_system.color()}">{system} %</font>')

    def refresh_idle(self, idle: float):
        self.lbl_idle_value.setText(f'<font color="{self.color_button_idle.color()}">{idle} %</font>')

    def refresh_process_number(self, process_number: int):
        self.lbl_processes_value.setText(f"{process_number}")

    def refresh_cumulative_threads(self, cumulative_threads: int):
        self.lbl_threads_value.setText(f"{cumulative_threads}")


class TabSystemMemory(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Internal class settings
        __virtual_memory = psutil.virtual_memory()
        self.memory_os_capability = {
            "total": hasattr(__virtual_memory, "total"),
            "available": hasattr(__virtual_memory, "available"),
            "percent": hasattr(__virtual_memory, "percent"),
            "used": hasattr(__virtual_memory, "used"),
            "free": hasattr(__virtual_memory, "free"),
            "active": hasattr(__virtual_memory, "active"),
            "inactive": hasattr(__virtual_memory, "inactive"),
            "buffers": hasattr(__virtual_memory, "buffers"),
            "cached": hasattr(__virtual_memory, "cached"),
            "shared": hasattr(__virtual_memory, "shared"),
            "slab": hasattr(__virtual_memory, "slab"),
            "wired": hasattr(__virtual_memory, "wired"),
        }
        self.lbl_free_value = None
        self.color_button_free = None
        self.lbl_buffers_value = None

        # System Memory Chart Pie
        self.chart_pie = None
        self.chart_pie_item_free = None
        self.chart_pie_item_wired = None
        self.chart_pie_item_active= None
        self.chart_pie_item_inactive = None

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()
        layout_grid.setRowStretch(0 | 1 | 2 | 3 | 4 | 5, 25)
        layout_grid.setColumnStretch(0 | 1 | 2 , 25)
        layout_grid.setHorizontalSpacing(10)
        layout_grid.setVerticalSpacing(5)

        layout_col2 = QGridLayout()
        layout_col2.setRowStretch(0 | 1 | 2 | 3 | 4 | 5, 25)
        layout_col2.setColumnStretch(0 | 1 , 25)
        layout_col2.setHorizontalSpacing(10)
        layout_col2.setVerticalSpacing(5)

        # widget Position management
        grid_col = 0
        grid_row = 0

        self.chart_pie = ChartPie()

        if self.memory_os_capability["free"]:
            # Free label
            lbl_free = QLabel("Free:")
            lbl_free.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_free_value = QLabel("")
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setToolTip(
                "Memory not being used at all (zeroed) that is readily available; note that this doesn't reflect the "
                "actual memory available (use available instead). total - used does not necessarily match free. "
            )
            # Free Color button
            self.color_button_free = ColorButton(color="green")
            self.color_button_free.setToolTip("Change Free color display")
            # Insert Free labels on the right position
            layout_grid.addWidget(lbl_free, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_free_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_free, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_free = ChartPieItem()
            self.chart_pie_item_free.setColor(self.color_button_free.color())
            self.chart_pie_item_free.data = 0

            self.chart_pie.addItem(self.chart_pie_item_free)

            # layout_grid.setRowStretch(grid_col, 0)
            grid_row += 1

        if self.memory_os_capability["wired"]:
            # Wired label
            lbl_wired = QLabel("Wired:")
            lbl_wired.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_wired_value = QLabel("")
            self.lbl_wired_value.setAlignment(Qt.AlignRight)
            self.lbl_wired_value.setToolTip("Memory that is marked to always stay in RAM. It is never moved to disk.")
            # Free Color button
            self.color_button_wired = ColorButton(color="red")
            # Insert Free labels on the right position
            layout_grid.addWidget(lbl_wired, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_wired_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_wired, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_wired = ChartPieItem()
            self.chart_pie_item_wired.setColor(self.color_button_wired.color())
            self.chart_pie_item_wired.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_wired)

            grid_row += 1

        # PSUtil can return active
        if self.memory_os_capability["active"]:
            # Active label
            lbl_active = QLabel("Active:")
            lbl_active.setAlignment(Qt.AlignRight)
            # Active label value
            self.lbl_active_value = QLabel("")
            self.lbl_active_value.setAlignment(Qt.AlignRight)
            self.lbl_active_value.setToolTip("Memory currently in use or very recently used, and so it is in RAM.")
            # Active Color button
            self.color_button_active = ColorButton(color="orange")
            # Insert Active labels on the right position
            layout_grid.addWidget(lbl_active, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_active_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_active, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_active = ChartPieItem()
            self.chart_pie_item_active.setColor(self.color_button_active.color())
            self.chart_pie_item_active.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_active)

            grid_row += 1

        # PSUtil can return inactive
        if self.memory_os_capability["inactive"]:
            # Inactive label
            lbl_inactive = QLabel("Inactive:")
            lbl_inactive.setAlignment(Qt.AlignRight)
            # Inactive label value
            self.lbl_inactive_value = QLabel("")
            self.lbl_inactive_value.setAlignment(Qt.AlignRight)
            self.lbl_inactive_value.setToolTip("Memory that is marked as not used.")
            # Inactive Color button
            self.color_button_inactive = ColorButton(color="blue")
            # Insert Inactive labels on the right position
            layout_grid.addWidget(lbl_inactive, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_inactive_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_inactive, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_inactive = ChartPieItem()
            self.chart_pie_item_inactive.setColor(self.color_button_inactive.color())
            self.chart_pie_item_inactive.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_inactive)

            grid_row += 1

        # PSUtil can return used
        if self.memory_os_capability["used"]:
            # Used label
            lbl_used = QLabel("Used:")
            lbl_used.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_used_value = QLabel("")
            self.lbl_used_value.setAlignment(Qt.AlignRight)
            self.lbl_used_value.setToolTip(
                "Memory used, calculated differently depending on the platform and designed for informational "
                "purposes only. <b>total - free</b> does not necessarily match <b>used</b>. "
            )
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_used, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_used_value, grid_row, grid_col + 1, 1, 1)

        # Position management
        # Set col and row to the second widget Position
        grid_row = 0
        grid_col += 3

        # PSUtil can return available
        if self.memory_os_capability["available"]:
            # Used label
            lbl_available = QLabel("Available:")
            lbl_available.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_available_value = QLabel("")
            self.lbl_available_value.setAlignment(Qt.AlignRight)
            self.lbl_available_value.setToolTip(
                "The memory that can be given instantly to processes without the system going into swap. <br>"
            )
            # Insert Used labels on the right position
            layout_col2.addWidget(lbl_available, grid_row, grid_col, 1, 1)
            layout_col2.addWidget(self.lbl_available_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return buffers
        if self.memory_os_capability["buffers"]:
            # Used label
            lbl_buffers = QLabel("Buffers:")
            lbl_buffers.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_buffers_value = QLabel("")
            self.lbl_buffers_value.setAlignment(Qt.AlignRight)
            self.lbl_buffers_value.setToolTip("Cache for things like file system metadata.<br>")
            # Insert Used labels on the right position
            layout_col2.addWidget(lbl_buffers, grid_row, grid_col, 1, 1)
            layout_col2.addWidget(self.lbl_buffers_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return cached
        if self.memory_os_capability["cached"]:
            # Used label
            lbl_cached = QLabel("Cached:")
            lbl_cached.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_cached_value = QLabel("")
            self.lbl_cached_value.setAlignment(Qt.AlignRight)
            self.lbl_cached_value.setToolTip("Cache for various things.")
            # Insert Used labels on the right position
            layout_col2.addWidget(lbl_cached, grid_row, grid_col, 1, 1)
            layout_col2.addWidget(self.lbl_cached_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return shared
        if self.memory_os_capability["shared"]:
            # Used label
            lbl_shared = QLabel("Shared:")
            lbl_shared.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_shared_value = QLabel("")
            self.lbl_shared_value.setAlignment(Qt.AlignRight)
            self.lbl_shared_value.setToolTip("Memory that may be simultaneously accessed by multiple processes.")
            # Insert Used labels on the right position
            layout_col2.addWidget(lbl_shared, grid_row, grid_col, 1, 1)
            layout_col2.addWidget(self.lbl_shared_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return lab
        if self.memory_os_capability["slab"]:
            # Used label
            lbl_slab = QLabel("Slab:")
            lbl_slab.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_slab_value = QLabel("")
            self.lbl_slab_value.setAlignment(Qt.AlignRight)
            self.lbl_slab_value.setToolTip("in-kernel data structures cache.")
            # Insert Used labels on the right position
            layout_col2.addWidget(lbl_slab, grid_row, grid_col, 1, 1)
            layout_col2.addWidget(self.lbl_slab_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        widgets_col2 = QWidget()
        widgets_col2.setLayout(layout_col2)

        widgets_col3 = self.chart_pie


        layout_vbox = QHBoxLayout()
        layout_vbox.addWidget(widget_grid, 1)
        layout_vbox.addWidget(widgets_col2, 1)
        layout_vbox.addWidget(widgets_col3, 1)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(20, 30, 0, 0)

        self.setLayout(layout_vbox)

    def refresh_free_raw(self, free_raw):
        if free_raw < 0:
            free_raw = abs(free_raw)
        self.chart_pie_item_free.setData(free_raw)
        self.chart_pie_item_free.setColor(self.color_button_free.color())
        self.chart_pie.repaint()

    def refresh_free(self, free):
        self.lbl_free_value.setText(f"<font color={self.color_button_free.color()}>{free}</font>")

    def refresh_wired_raw(self, wired_raw):
        if wired_raw < 0:
            wired_raw = abs(wired_raw)
        self.chart_pie_item_wired.setData(wired_raw)
        self.chart_pie_item_wired.setColor(self.color_button_wired.color())
        self.chart_pie.repaint()

    def refresh_wired(self, wired):
        self.lbl_wired_value.setText(f"<font color={self.color_button_wired.color()}>{wired}</font>")

    def refresh_active_raw(self, active_raw):
        if active_raw < 0:
            active_raw = abs(active_raw)
        self.chart_pie_item_active.setData(active_raw)
        self.chart_pie_item_active.setColor(self.color_button_active.color())
        self.chart_pie.repaint()

    def refresh_active(self, active):
        self.lbl_active_value.setText(f"<font color={self.color_button_active.color()}>{active}</font>")

    def refresh_inactive_raw(self, inactive_raw):
        if inactive_raw < 0:
            inactive_raw = abs(inactive_raw)
        self.chart_pie_item_inactive.setData(inactive_raw)
        self.chart_pie_item_inactive.setColor(self.color_button_inactive.color())
        self.chart_pie.repaint()

    def refresh_inactive(self, inactive):
        self.lbl_inactive_value.setText(f"<font color={self.color_button_inactive.color()}>{inactive}</font>")

    def refresh_used(self, used):
        self.lbl_used_value.setText(used)

    def refresh_available(self, available):
        self.lbl_available_value.setText(available)

    def refresh_buffers(self, buffers):
        self.lbl_buffers_value.setText(buffers)

    def refresh_cached(self, cached):
        self.lbl_cached_value.setText(cached)

    def refresh_shared(self, shared):
        self.lbl_shared_value.setText(shared)

    def refresh_slab(self, slab):
        self.lbl_slab_value.setText(slab)


class TabDiskActivity(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh(self):
        pass


class TabDiskUsage(QWidget):
    mounted_disk_partitions_changed = Signal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.__mounted_disk_partitions = None
        self.mounted_disk_partitions = None
        self.combobox_devices = None
        self.label_space_utilized_value = None
        self.label_space_utilized_value_in_bytes = None
        self.color_button_space_utilized = None
        self.label_space_free_value = None
        self.label_space_free_value_in_bytes = None
        self.color_button_space_free = None
        self.label_space_total_value = None
        self.chartpie = None
        self.chartpie_item_utilized = None
        self.chartpie_item_free = None
        # self.mounted_disk_partitions = self.scan_mounted_disk_partitions()

        self.setupUI()
        # self.combobox_refresh()
        # self.combobox_index_changed()

        self.combobox_devices.currentIndexChanged.connect(self.combobox_index_changed)
        # self.combobox_devices.activated.connect(self.combobox_index_changed)
        # self.combobox_devices.activated.connect(lambda: self.mounted_disk_partitions(self.combobox_refresh))

        self.mounted_disk_partitions_changed.connect(self.combobox_refresh)

    @property
    def mounted_disk_partitions(self):
        return self.__mounted_disk_partitions

    @mounted_disk_partitions.setter
    def mounted_disk_partitions(self, value: dict):
        if value is None:
            value = {}
        if self.mounted_disk_partitions != value:
            self.__mounted_disk_partitions = value

            self.mounted_disk_partitions_changed.emit()

    def setMoutedDiskPartitions(self, value):
        self.mounted_disk_partitions = value

    def combobox_refresh(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
        self.combobox_devices.clear()
        for item_number, data in self.mounted_disk_partitions.items():
            self.combobox_devices.addItem(QFileIconProvider().icon(QFileIconProvider.Drive), data["mountpoint"])
        self.combobox_devices.setCurrentIndex(index)

    def combobox_index_changed(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
            self.combobox_devices.setCurrentIndex(index)

        self.label_space_utilized_value.setText(
            f"<font color='{self.color_button_space_utilized.color()}'>"
            f"{self.mounted_disk_partitions[index]['used']}"
            f"</font>"
        )
        self.label_space_utilized_value_in_bytes.setText(
            f"<font color='{self.color_button_space_utilized.color()}'>"
            f"{self.mounted_disk_partitions[index]['used_in_bytes']}"
            f"</font>"
        )
        self.label_space_free_value.setText(
            f"<font color='{self.color_button_space_free.color()}'>"
            f"{self.mounted_disk_partitions[index]['free']}"
            f"</font>"
        )
        self.label_space_free_value_in_bytes.setText(
            f"<font color='{self.color_button_space_free.color()}'>"
            f"{self.mounted_disk_partitions[index]['free_in_bytes']}"
            f"</font>"
        )
        self.label_space_total_value.setText(
            f"{self.mounted_disk_partitions[index]['total']}"
        )

        self.chartpie_item_utilized.color = self.color_button_space_utilized.color()
        self.chartpie_item_utilized.data = self.mounted_disk_partitions[index]['used_raw']
        self.chartpie_item_free.color = self.color_button_space_free.color()
        self.chartpie_item_free.data = self.mounted_disk_partitions[index]['free_raw']

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()

        self.combobox_devices = QComboBox()
        layout_grid.addWidget(self.combobox_devices, 0, 0, 1, 2)

        label_space_utilized = QLabel("Space utilized:")
        label_space_utilized.setAlignment(Qt.AlignRight)
        # Used label value
        self.label_space_utilized_value = QLabel("")
        self.label_space_utilized_value.setAlignment(Qt.AlignRight)

        self.label_space_utilized_value_in_bytes = QLabel("")
        self.label_space_utilized_value_in_bytes.setAlignment(Qt.AlignRight)

        self.color_button_space_utilized = ColorButton(color="red")

        # Insert Space utilized labels on the right position
        layout_grid.addWidget(label_space_utilized, 1, 0, 1, 1)
        layout_grid.addWidget(self.label_space_utilized_value, 1, 1, 1, 1)
        layout_grid.addWidget(self.label_space_utilized_value_in_bytes, 1, 2, 1, 1)
        layout_grid.addWidget(self.color_button_space_utilized, 1, 3, 1, 1)

        label_space_free = QLabel("Space free:")
        label_space_free.setAlignment(Qt.AlignRight)
        # Used label value
        self.label_space_free_value = QLabel("")
        self.label_space_free_value.setAlignment(Qt.AlignRight)

        self.label_space_free_value_in_bytes = QLabel("")
        self.label_space_free_value_in_bytes.setAlignment(Qt.AlignRight)

        self.color_button_space_free = ColorButton(color="green")

        # Insert Space utilized labels on the right position
        layout_grid.addWidget(label_space_free, 2, 0, 1, 1)
        layout_grid.addWidget(self.label_space_free_value, 2, 1, 1, 1)
        layout_grid.addWidget(self.label_space_free_value_in_bytes, 2, 2, 1, 1)
        layout_grid.addWidget(self.color_button_space_free, 2, 3, 1, 1)

        self.label_space_total_value = QLabel("")
        self.label_space_total_value.setAlignment(Qt.AlignLeft)
        self.label_space_total_value.setContentsMargins(10, 0, 0, 0)
        layout_grid.addWidget(self.label_space_total_value, 3, 4, 1, 3)

        self.chartpie_item_utilized = ChartPieItem()
        self.chartpie_item_utilized.color = self.color_button_space_utilized.color()
        self.chartpie_item_utilized.data = 0

        self.chartpie_item_free = ChartPieItem()
        self.chartpie_item_free.color = self.color_button_space_free.color()
        self.chartpie_item_free.data = 0

        self.chartpie = ChartPie()
        self.chartpie.addItems([
            self.chartpie_item_utilized,
            self.chartpie_item_free,

        ])
        layout_grid.addWidget(self.chartpie, 0, 4, 3, 1)


        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh(self):
        pass


class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh(self):
        pass


class ProcessMonitor(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout()

        self.searchLineEdit = None
        self.filterComboBox = None
        self.tree_view_model = None
        self.process_tree = None
        self.tree_view_model = None
        self.kill_process_action = None
        self.inspect_process_action = None
        self.selected_pid = -1
        self.my_username = os.getlogin()
        self.header = ["Process ID", "Process Name", "User", "% CPU", "# Threads", "Real Memory", "Virtual Memory"]

        self.setupUi()

    def setupUi(self):
        self.tree_view_model = QStandardItemModel()

        self.process_tree = QTreeView()
        self.process_tree.setModel(self.tree_view_model)
        self.process_tree.setIconSize(QSize(16, 16))
        self.process_tree.setUniformRowHeights(True)
        self.process_tree.setSortingEnabled(True)
        self.process_tree.sortByColumn(3, Qt.DescendingOrder)
        self.process_tree.setAlternatingRowColors(True)
        self.process_tree.clicked.connect(self.onClicked)
        self.process_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.process_tree.setSelectionMode(QAbstractItemView.SingleSelection)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_tree)
        self.setLayout(layout)

        self.refresh()

    def save_selection(self):
        selection = self.process_tree.selectionModel().selectedRows()
        blocks = []
        for count, index in enumerate(sorted(selection)):
            row = index.row()

            if count > 0 and row == block[1] + 1:
                block[1] = row
            else:
                block = [row, row]
                blocks.append(block)
        return blocks

    def create_selection(self, blocks):
        mod = self.process_tree.model()
        columns = mod.columnCount() - 1
        flags = QItemSelectionModel.Select
        selection = QItemSelection()
        for start, end in blocks:
            start, end = mod.index(start, 0), mod.index(end, columns)
            if selection.indexes():
                selection.merge(QItemSelection(start, end), flags)
            else:
                selection.select(start, end)
        self.process_tree.selectionModel().clear()
        self.process_tree.selectionModel().select(selection, flags)

    def filter_by_line(self, row, text):
        if hasattr(self.searchLineEdit, "text") and self.searchLineEdit.text():
            if self.searchLineEdit.text() in text:
                return row
            else:
                return None
        else:
            return row

    def refresh(self):
        self.tree_view_model = QStandardItemModel()

        for p in psutil.process_iter():
            with p.oneshot():
                row = [
                    QStandardItem(f"{p.pid}"),
                    QStandardItem(f"{p.name()}"),
                    QStandardItem(f"{p.username()}"),
                    QStandardItem(f"{p.cpu_percent()}"),
                    QStandardItem(f"{p.num_threads()}"),
                    QStandardItem(f"{bytes2human(p.memory_info().rss)}"),
                    QStandardItem(f"{bytes2human(p.memory_info().vms)}"),
                ]

                # Filter Line
                filtered_row = None
                if hasattr(self.searchLineEdit, "text") and self.searchLineEdit.text():
                    if self.searchLineEdit.text() in p.name():
                        filtered_row = row
                else:
                    filtered_row = row

                # Filter by ComboBox index
                #             0: 'All Processes',
                #             1: 'All Processes, Hierarchically',
                #             2: 'My Processes',
                #             3: 'System Processes',
                #             4: 'Other User Processes',
                #             5: 'Active Processes',
                #             6: 'Inactive Processes',
                #             7: 'Windowed Processes',
                #             8: 'Selected Processes',
                #             9: 'Application in last 12 hours',
                if hasattr(self.filterComboBox, "currentIndex"):
                    combo_box_current_index = self.filterComboBox.currentIndex()
                    if combo_box_current_index == 0:
                        pass

                    if combo_box_current_index == 1:
                        pass
                    else:
                        pass

                    if combo_box_current_index == 2:
                        if p.username() == self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 3:
                        if p.uids().real < 1000:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 4:
                        if p.username() != self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 5:
                        pass
                    elif combo_box_current_index == 6:
                        pass
                    elif combo_box_current_index == 7:
                        pass

                    if combo_box_current_index == 8:
                        if p.pid == self.selected_pid:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 9:
                        if (time.time() - p.create_time()) % 60 <= 43200:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)

        for pos, title in enumerate(self.header):
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, title)
            self.process_tree.resizeColumnToContents(pos)

        self.process_tree.setModel(self.tree_view_model)

        if self.selected_pid >= 0:
            self.selectItem(str(self.selected_pid))

        # for pos in range(len(self.header) - 1):
        #     self.process_tree.resizeColumnToContents(pos)

    def selectClear(self):
        self.selected_pid = -1
        self.process_tree.clearSelection()
        self.kill_process_action.setEnabled(False)
        self.inspect_process_action.setEnabled(False)
        if self.filterComboBox.currentIndex() == 8:
            self.filterComboBox.setCurrentIndex(0)
        self.filterComboBox.model().item(8).setEnabled(False)

    def selectItem(self, itemOrText):
        oldIndex = self.process_tree.selectionModel().currentIndex()
        newIndex = None
        try:  # an item is given--------------------------------------------
            newIndex = self.process_tree.model().indexFromItem(itemOrText)
        except:  # a text is given and we are looking for the first match---
            # for toto in self.process_tree.model().index(0, 0):
            #     print(toto)
            listIndexes = self.process_tree.model().match(
                self.process_tree.model().index(0, 0), Qt.DisplayRole, itemOrText, Qt.MatchStartsWith
            )
            if listIndexes:
                newIndex = listIndexes[0]
        if newIndex:
            self.process_tree.selectionModel().select(  # programmatically selection---------
                newIndex, QItemSelectionModel.ClearAndSelect
            )

    def onClicked(self):
        self.selected_pid = int(self.tree_view_model.itemData(self.process_tree.selectedIndexes()[0])[0])
        if self.selected_pid:
            self.kill_process_action.setEnabled(True)
            self.inspect_process_action.setEnabled(True)
            self.filterComboBox.model().item(8).setEnabled(True)

    def killProcess(self):
        if self.selected_pid:
            os.kill(self.selected_pid, signal.SIGKILL)

    def killSelectedProcess(self):
        if self.selected_pid and self.selected_pid != -1:
            try:
                os.kill(self.selected_pid, signal.SIGKILL)
                self.selected_pid = -1
                self.process_tree.clearSelection()
                self.process_tree.refresh()
            except (Exception, BaseException):
                pass

    def InspectSelectedProcess(self):
        selected = self.process_tree.currentItem()
        if selected is not None:
            pid = int(selected.text(0))
            try:
                self.selected_pid = -1
            except (Exception, BaseException):
                pass


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.icon_size = 32
        self.filters = [
            "All Processes",
            "All Processes, Hierarchically",
            "My Processes",
            "System Processes",
            "Other User Processes",
            "Active Processes",
            "Inactive Processes",
            "Windowed Processes",
            "Selected Processes",
            "Application in last 12 hours",
        ]

        # vars
        self.threads = []
        self.filterComboBox = None
        self.searchLineEdit = None
        self.process_monitor = None

        self.tab_cpu = None
        self.tab_system_memory = None
        self.tab_disk_activity = None
        self.tab_disk_usage = None
        self.tab_network = None
        self.timer = None

        self.setupUi()

        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def setupUi(self):
        self.setWindowTitle("Activity Monitor")
        self.resize(800, 600)
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "Processes.png",
                )
            )
        )
        self.timer = QTimer()
        self._timer_change_for_5_secs()
        self.tab_cpu = TabCpu()
        self.tab_system_memory = TabSystemMemory()
        self.tab_disk_usage = TabDiskUsage()
        self.tab_disk_activity = TabDiskActivity()
        self.tab_network = TabNetwork()
        self.searchLineEdit = QLineEdit()
        # self.searchLineEdit.setStyleSheet("QLineEdit {  border: 2px inner gray;"
        #                                 "border-radius: 30px}")
        self.filterComboBox = QComboBox()

        self.process_monitor = ProcessMonitor()
        self.process_monitor.filterComboBox = self.filterComboBox
        self.process_monitor.searchLineEdit = self.searchLineEdit

        # Ping / Pong for ComboBox
        self.searchLineEdit.textChanged.connect(self.process_monitor.refresh)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)

        self._createMenuBar()
        self._createActions()
        self._createToolBars()

        self.process_monitor.kill_process_action = self.kill_process_action
        self.process_monitor.inspect_process_action = self.inspect_process_action

        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.process_monitor.selectClear)

        self.setStyleSheet(
            """
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabWidget::pane { /* The tab widget frame */
                position: absolute;
                top: -0.9em;
            }
            """
        )

        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        tabs.addTab(self.tab_cpu, "CPU")
        tabs.addTab(self.tab_system_memory, "System Memory")
        tabs.addTab(self.tab_disk_activity, "Disk Activity")
        tabs.addTab(self.tab_disk_usage, "Disk Usage")
        tabs.addTab(self.tab_network, "Network")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_monitor, 1)
        layout.addWidget(QLabel(""))
        layout.addWidget(tabs)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def createThread(self):
        thread = QThread()
        worker = PSUtilsWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # CPU
        worker.updated_cpu_user.connect(self.tab_cpu.refresh_user)
        worker.updated_cpu_system.connect(self.tab_cpu.refresh_system)
        worker.updated_cpu_idle.connect(self.tab_cpu.refresh_idle)
        worker.updated_cpu_cumulative_threads.connect(self.tab_cpu.refresh_cumulative_threads)
        worker.updated_cpu_process_number.connect(self.tab_cpu.refresh_process_number)

        # System MEmory
        # worker.updated_system_memory_total.connect(self.tab_system_memory.refresh_total)
        worker.updated_system_memory_available.connect(self.tab_system_memory.refresh_available)
        worker.updated_system_memory_used.connect(self.tab_system_memory.refresh_used)
        worker.updated_system_memory_free.connect(self.tab_system_memory.refresh_free)
        worker.updated_system_memory_active.connect(self.tab_system_memory.refresh_active)
        worker.updated_system_memory_inactive.connect(self.tab_system_memory.refresh_inactive)
        worker.updated_system_memory_buffers.connect(self.tab_system_memory.refresh_buffers)
        worker.updated_system_memory_cached.connect(self.tab_system_memory.refresh_cached)
        worker.updated_system_memory_shared.connect(self.tab_system_memory.refresh_shared)
        worker.updated_system_memory_slab.connect(self.tab_system_memory.refresh_slab)
        worker.updated_system_memory_wired.connect(self.tab_system_memory.refresh_wired)

        # System Memory Chart Pie
        worker.updated_system_memory_free_raw.connect(self.tab_system_memory.refresh_free_raw)
        worker.updated_system_memory_wired_raw.connect(self.tab_system_memory.refresh_wired_raw)
        worker.updated_system_memory_active_raw.connect(self.tab_system_memory.refresh_active_raw)
        worker.updated_system_memory_inactive_raw.connect(self.tab_system_memory.refresh_inactive_raw)

        # Disk Usage
        worker.updated_mounted_disk_partitions.connect(self.tab_disk_usage.setMoutedDiskPartitions)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh(self):
        self.process_monitor.refresh()

        self.threads.clear()
        self.threads = [self.createThread()]
        for thread in self.threads:
            thread.start()

    def _close(self):
        self.close()
        return 0

    def _window_minimize(self):
        self.showMinimized()

    def _timer_change_for_1_sec(self):
        self.timer.start(1000)

    def _timer_change_for_3_secs(self):
        self.timer.start(3000)

    def _timer_change_for_5_secs(self):
        self.timer.start(5000)

    def _filter_by_changed(self):
        #             0: 'All Processes',
        #             1: 'All Processes, Hierarchically',
        #             2: 'My Processes',
        #             3: 'System Processes',
        #             4: 'Other User Processes',
        #             5: 'Active Processes',
        #             6: 'Inactive Processes',
        #             7: 'Windowed Processes',
        #             8: 'Selected Processes',
        #             9: 'Application in last 12 hours',
        if hasattr(self.filterComboBox, "currentIndex"):
            if self.filterComboBox.currentIndex() == 0:
                self.ActionMenuViewAllProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 1:
                self.ActionMenuViewAllProcessesHierarchically.setChecked(True)
            elif self.filterComboBox.currentIndex() == 2:
                self.ActionMenuViewMyProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 3:
                self.ActionMenuViewSystemProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 4:
                self.ActionMenuViewOtherUserProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 5:
                self.ActionMenuViewActiveProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 6:
                self.ActionMenuViewInactiveProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 7:
                self.ActionMenuViewWindowedProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 8:
                self.ActionMenuViewSelectedProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 9:
                self.ActionMenuViewApplicationInLast12Hours.setChecked(True)

        self.process_monitor.refresh()

    def _filter_by_all_processes(self):
        self.filterComboBox.setCurrentIndex(0)

    def _filter_by_all_process_hierarchically(self):
        self.filterComboBox.setCurrentIndex(1)

    def _filter_by_my_processes(self):
        self.filterComboBox.setCurrentIndex(2)

    def _filter_by_system_processes(self):
        self.filterComboBox.setCurrentIndex(3)

    def _filter_by_other_user_processes(self):
        self.filterComboBox.setCurrentIndex(4)

    def _filter_by_active_processes(self):
        self.filterComboBox.setCurrentIndex(5)

    def _filter_by_inactive_processes(self):
        self.filterComboBox.setCurrentIndex(6)

    def _filter_by_windowed_processes(self):
        self.filterComboBox.setCurrentIndex(7)

    def _filter_by_selected_processes(self):
        self.filterComboBox.setCurrentIndex(8)

    def _filter_by_application_in_last_12_hours(self):
        self.filterComboBox.setCurrentIndex(9)

    def _createMenuBar(self):
        self.menuBar = QMenuBar()

        # File Menu
        fileMenu = self.menuBar.addMenu("&File")

        quitAct = QAction("Quit", self)
        quitAct.setStatusTip("Quit this application")
        quitAct.setShortcut(QKeySequence.Quit)
        quitAct.triggered.connect(self._close)

        fileMenu.addAction(quitAct)

        # Edit Menu
        editMenu = self.menuBar.addMenu("&Edit")

        # View Menu
        viewMenu = self.menuBar.addMenu("&View")

        view_columns = viewMenu.addMenu("Columns")
        view_columns.setEnabled(False)

        view_dock = viewMenu.addMenu("Dock Icon")
        view_dock.setEnabled(False)

        # Update Frequency Menu
        viewMenuUpdateFrequency = viewMenu.addMenu("Update Frequency")

        ActionMenuViewUpdateFrequency5Secs = QAction("5 Secs", self)
        ActionMenuViewUpdateFrequency5Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency5Secs.triggered.connect(self._timer_change_for_5_secs)

        ActionMenuViewUpdateFrequency3Secs = QAction("3 Secs", self)
        ActionMenuViewUpdateFrequency3Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency3Secs.triggered.connect(self._timer_change_for_3_secs)

        ActionMenuViewUpdateFrequency1Sec = QAction("1 Secs", self)
        ActionMenuViewUpdateFrequency1Sec.setCheckable(True)
        ActionMenuViewUpdateFrequency1Sec.triggered.connect(self._timer_change_for_1_sec)

        update_frequency_group = QActionGroup(self)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency1Sec)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency3Secs)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency5Secs)

        ActionMenuViewUpdateFrequency5Secs.setChecked(True)

        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency1Sec)
        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency3Secs)
        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency5Secs)

        viewMenu.addSeparator()

        self.ActionMenuViewAllProcesses = QAction("All Processes", self)
        self.ActionMenuViewAllProcesses.setCheckable(True)
        self.ActionMenuViewAllProcesses.triggered.connect(self._filter_by_all_processes)

        self.ActionMenuViewAllProcessesHierarchically = QAction("All Processes, Hierarchically", self)
        self.ActionMenuViewAllProcessesHierarchically.setCheckable(True)
        self.ActionMenuViewAllProcessesHierarchically.triggered.connect(self._filter_by_all_process_hierarchically)

        self.ActionMenuViewMyProcesses = QAction("My Processes", self)
        self.ActionMenuViewMyProcesses.setCheckable(True)
        self.ActionMenuViewMyProcesses.triggered.connect(self._filter_by_my_processes)

        self.ActionMenuViewSystemProcesses = QAction("System Processes", self)
        self.ActionMenuViewSystemProcesses.setCheckable(True)
        self.ActionMenuViewSystemProcesses.triggered.connect(self._filter_by_system_processes)

        self.ActionMenuViewOtherUserProcesses = QAction("Other User Processes", self)
        self.ActionMenuViewOtherUserProcesses.setCheckable(True)
        self.ActionMenuViewOtherUserProcesses.triggered.connect(self._filter_by_other_user_processes)

        self.ActionMenuViewActiveProcesses = QAction("Active Processes", self)
        self.ActionMenuViewActiveProcesses.setCheckable(True)
        self.ActionMenuViewActiveProcesses.triggered.connect(self._filter_by_active_processes)

        self.ActionMenuViewInactiveProcesses = QAction("Inactive Processes", self)
        self.ActionMenuViewInactiveProcesses.setCheckable(True)
        self.ActionMenuViewInactiveProcesses.triggered.connect(self._filter_by_inactive_processes)

        self.ActionMenuViewWindowedProcesses = QAction("Windowed Processes", self)
        self.ActionMenuViewWindowedProcesses.setCheckable(True)
        self.ActionMenuViewWindowedProcesses.triggered.connect(self._filter_by_windowed_processes)

        self.ActionMenuViewSelectedProcesses = QAction("Selected Processes", self)
        self.ActionMenuViewSelectedProcesses.setCheckable(True)
        self.ActionMenuViewSelectedProcesses.setEnabled(False)
        self.ActionMenuViewSelectedProcesses.triggered.connect(self._filter_by_selected_processes)

        self.ActionMenuViewApplicationInLast12Hours = QAction("Application in last 12 hours", self)
        self.ActionMenuViewApplicationInLast12Hours.setCheckable(True)
        self.ActionMenuViewApplicationInLast12Hours.triggered.connect(self._filter_by_application_in_last_12_hours)

        alignmentViewBy = QActionGroup(self)
        alignmentViewBy.addAction(self.ActionMenuViewAllProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewAllProcessesHierarchically)
        alignmentViewBy.addAction(self.ActionMenuViewMyProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewSystemProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewOtherUserProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewActiveProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewInactiveProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewWindowedProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewSelectedProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewApplicationInLast12Hours)

        self.ActionMenuViewAllProcesses.setChecked(True)

        viewMenu.addActions(
            [
                self.ActionMenuViewAllProcesses,
                self.ActionMenuViewAllProcessesHierarchically,
                self.ActionMenuViewMyProcesses,
                self.ActionMenuViewSystemProcesses,
                self.ActionMenuViewOtherUserProcesses,
                self.ActionMenuViewActiveProcesses,
                self.ActionMenuViewInactiveProcesses,
                self.ActionMenuViewWindowedProcesses,
                self.ActionMenuViewSelectedProcesses,
                self.ActionMenuViewApplicationInLast12Hours,
            ]
        )

        viewMenu.addSeparator()

        viewFilterProcesses = QAction("Filter Processes", self)
        viewFilterProcesses.setShortcut("Ctrl+Meta+F")
        viewFilterProcesses.setEnabled(False)

        viewInspectProcess = QAction("Inspect Process", self)
        viewInspectProcess.setShortcut("Ctrl+I")
        viewInspectProcess.setEnabled(False)

        viewSampleProcess = QAction("Sample Process", self)
        viewSampleProcess.setShortcut("Ctrl+Meta+S")
        viewSampleProcess.setEnabled(False)

        viewRunSpindump = QAction("Run Spindump", self)
        viewRunSpindump.setShortcut("Alt+Ctrl+Meta+S")
        viewRunSpindump.setEnabled(False)

        viewRunSystemDiagnostics = QAction("Run system Diagnostics", self)
        viewRunSystemDiagnostics.setEnabled(False)

        viewQuitProcess = QAction("Quit Process", self)
        viewQuitProcess.setShortcut("Ctrl+Meta+Q")
        viewQuitProcess.setEnabled(False)

        viewSendSignalToProcesses = QAction("Send Signal to Processes", self)
        viewSendSignalToProcesses.setEnabled(False)

        viewShowDeltasForProcess = QAction("Show Deltas for Process", self)
        viewShowDeltasForProcess.setShortcut("Ctrl+Meta+J")
        viewShowDeltasForProcess.setEnabled(False)

        viewMenu.addActions(
            [
                viewFilterProcesses,
                viewInspectProcess,
                viewSampleProcess,
                viewRunSpindump,
                viewRunSystemDiagnostics,
                viewQuitProcess,
                viewSendSignalToProcesses,
                viewShowDeltasForProcess,
            ]
        )

        viewMenu.addSeparator()

        viewClearCPUHistory = QAction("Clear CPU History", self)
        viewClearCPUHistory.setShortcut("Ctrl+K")
        viewClearCPUHistory.setEnabled(False)

        viewEnterFullScreen = QAction("Enter Full Screen", self)
        viewEnterFullScreen.setEnabled(False)

        viewMenu.addActions(
            [
                viewClearCPUHistory,
                viewEnterFullScreen,
            ]
        )

        # Window Menu
        windowMenu = self.menuBar.addMenu("Window")

        ActionMenuWindowMinimize = QAction("Minimize", self)
        ActionMenuWindowMinimize.setShortcut("Ctrl+M")
        ActionMenuWindowMinimize.triggered.connect(self._window_minimize)

        self.ActionMenuWindowZoom = QAction("Zoom", self)
        self.ActionMenuWindowZoom.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowMinimize)
        windowMenu.addAction(self.ActionMenuWindowZoom)
        windowMenu.addSeparator()

        ActionMenuWindowActivityMonitor = QAction("Activity Monitor", self)
        ActionMenuWindowActivityMonitor.setShortcut("Ctrl+1")
        ActionMenuWindowActivityMonitor.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowActivityMonitor)

        # Help Menu
        helpMenu = self.menuBar.addMenu("&Help")

        aboutAct = QAction("&About", self)
        aboutAct.setStatusTip("About this application")
        aboutAct.triggered.connect(self._showAbout)

        helpMenu.addAction(aboutAct)

        self.setMenuBar(self.menuBar)

    def _createActions(self):
        self.kill_process_action = QAction(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "KillProcess.png",
                )
            ),
            "Quit Process",
            self,
        )
        self.kill_process_action.setStatusTip("Kill process")
        self.kill_process_action.triggered.connect(self.process_monitor.killSelectedProcess)
        self.kill_process_action.setEnabled(False)

        self.inspect_process_action = QAction(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "Inspect.png",
                )
            ),
            "Inspect",
            self,
        )
        self.inspect_process_action.setStatusTip("Inspect the selected process")
        self.inspect_process_action.setEnabled(False)
        # self.inspect_process_action.triggered.connect(self.InspectSelectedProcess)

        showLabel = QLabel("Show")
        showLabel.setAlignment(Qt.AlignCenter)

        showVBoxLayout = QVBoxLayout()

        self.filterComboBox.addItems(self.filters)
        self.filterComboBox.model().item(8).setEnabled(False)

        self.filterComboBox.setCurrentIndex(0)

        showVBoxLayout.addWidget(self.filterComboBox)
        showVBoxLayout.addWidget(showLabel)

        showWidget = QWidget()
        showWidget.setLayout(showVBoxLayout)

        self.filter_process_action = QWidgetAction(self)
        self.filter_process_action.setDefaultWidget(showWidget)

        searchLabel = QLabel("Search")
        searchLabel.setAlignment(Qt.AlignCenter)

        searchVBoxLayout = QVBoxLayout()
        searchVBoxLayout.addWidget(self.searchLineEdit)
        searchVBoxLayout.addWidget(searchLabel)

        searchWidget = QWidget()
        searchWidget.setLayout(searchVBoxLayout)

        self.search_process_action = QWidgetAction(self)
        self.search_process_action.setDefaultWidget(searchWidget)

    def _createToolBars(self):
        toolbar = QToolBar("Main ToolBar")
        toolbar.setIconSize(QSize(self.icon_size, self.icon_size))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setOrientation(Qt.Horizontal)

        toolbar.addAction(self.kill_process_action)
        toolbar.addAction(self.inspect_process_action)
        toolbar.addAction(self.filter_process_action)
        toolbar.addAction(self.search_process_action)

        self.addToolBar(toolbar)

    @staticmethod
    def _showAbout():
        about = About()
        about.size = 300, 340
        about.icon = QPixmap(
            os.path.join(
                os.path.dirname(__file__),
                "activity_monitor",
                "ui",
                "Processes.png",
            )
        ).scaledToWidth(96, Qt.SmoothTransformation)
        about.name = __app_name__
        about.version = f"Version {__app_version__}"
        about.text = (
            f"This project is open source, contributions are welcomed.<br><br>"
            f"Visit <a href='{__app_url__}'>{__app_url__}</a> for more information, "
            f"report bug or to suggest a new feature<br>"
        )
        about.credit = "Copyright 2023-2023 helloSystem team. All rights reserved"
        about.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        win = Window()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass
