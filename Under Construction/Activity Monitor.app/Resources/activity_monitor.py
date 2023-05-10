#!/usr/bin/env python3

import os
import signal
import sys
import time

import psutil
from PyQt5.QtCore import QTimer, Qt, QSize, pyqtSignal as Signal, QPoint, QObject, QItemSelectionModel, QItemSelection
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
    QPushButton,
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

)

from activity_monitor.libs.about import About

__app_name__ = "Activity Monitor"
__app_version__ = "0.1a"
__app_authors__ = ["Hierosme Alias Tuuux", "Contributors ..."]
__app_description__ = "View CPU, Memory, Network, Disk activities and interact with processes"
__app_url__ = "https://github.com/helloSystem/Utilities"


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.80 KB'
    # >>> bytes2human(100001221)
    # '95.40 MB'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            return f"{round(float(n) / prefix[s], 2):.2f} {s}B"
    return f"{n} B"


class ColorButton(QPushButton):
    """
    Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to the default color (None by default).
    """

    colorChanged = Signal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.setColor(self._default)
        self.setContentsMargins(3, 3, 3, 3)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.brushSize = 28
        self.brushColor = Qt.black
        self.lastPoint = QPoint()

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)


class TabCpu(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # User label
        self.lbl_user = QLabel("User:")
        self.lbl_user.setAlignment(Qt.AlignRight)
        # User label value
        self.lbl_user_value = QLabel("")
        self.lbl_user_value.setAlignment(Qt.AlignRight)
        # User Color button
        self.color_button_user = ColorButton(color="green")
        # Insert user labels on the right position
        self.layout.addWidget(self.lbl_user, 1, 0, 1, 1)
        self.layout.addWidget(self.lbl_user_value, 1, 1, 1, 1)
        self.layout.addWidget(self.color_button_user, 1, 2, 1, 1)

        # System label
        self.lbl_system = QLabel("System:")
        self.lbl_system.setAlignment(Qt.AlignRight)
        # System label value
        self.lbl_system_value = QLabel("")
        self.lbl_system_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_system = ColorButton(color="red")
        # Insert system labels on the right position
        self.layout.addWidget(self.lbl_system, 2, 0, 1, 1)
        self.layout.addWidget(self.lbl_system_value, 2, 1, 1, 1)
        self.layout.addWidget(self.color_button_system, 2, 2, 1, 1)

        # Label Idle
        self.lbl_idle = QLabel("Idle:")
        self.lbl_idle.setAlignment(Qt.AlignRight)
        # Label Idle value
        self.lbl_idle_value = QLabel("")
        self.lbl_idle_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_idle = ColorButton(color="black")

        # Insert idle labels on the right position
        self.layout.addWidget(self.lbl_idle, 3, 0, 1, 1)
        self.layout.addWidget(self.lbl_idle_value, 3, 1, 1, 1)
        self.layout.addWidget(self.color_button_idle, 3, 2, 1, 1)

        # Label threads
        self.lbl_threads = QLabel("Threads:")
        self.lbl_threads.setAlignment(Qt.AlignRight)
        # Label threads value
        self.lbl_threads_value = QLabel("")
        self.lbl_threads_value.setAlignment(Qt.AlignLeft)
        # Insert threads labels on the right position
        self.layout.addWidget(self.lbl_threads, 1, 3, 1, 1)
        self.layout.addWidget(self.lbl_threads_value, 1, 4, 1, 1)

        # Label Processes
        self.lbl_processes = QLabel("Processes:")
        self.lbl_processes.setAlignment(Qt.AlignRight)
        # Label Processes value
        self.lbl_processes_value = QLabel("")
        self.lbl_processes_value.setAlignment(Qt.AlignLeft)
        # Insert Processes labels on the right position
        self.layout.addWidget(self.lbl_processes, 2, 3, 1, 1)
        self.layout.addWidget(self.lbl_processes_value, 2, 4, 1, 1)

        self.lbl_cpu_usage = QLabel("CPU Usage")
        self.lbl_cpu_usage.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_cpu_usage, 0, 6, 1, 1)

        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.lbl_user_value.setText(f'<font color="{self.color_button_user.color()}">{cpu_times_percent.user} %</font>')
        self.lbl_system_value.setText(
            f'<font color="{self.color_button_system.color()}">{cpu_times_percent.system} %</font>'
        )
        self.lbl_idle_value.setText(f'<font color="{self.color_button_idle.color()}">{cpu_times_percent.idle} %</font>')

        cumulative_threads = 0
        process_number = 0
        # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        p = psutil.Process()
        with p.oneshot():
            # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
            for proc in psutil.process_iter():
                try:
                    # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.cpu_times
                    cumulative_threads += proc.num_threads()
                    process_number += 1
                except psutil.NoSuchProcess:
                    pass

        self.lbl_processes_value.setText(f"{process_number}")
        self.lbl_threads_value.setText(f"{cumulative_threads}")


class TabSystemMemoryWorker(QObject):
    finished = Signal()

    def run(self):
        self.finished.emit()


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

        self.layout = QGridLayout()
        # self.layout.setAlignment(Qt.AlignTop)

        self.setLayout(self.layout)

        # widget Position management
        grid_col = 0
        grid_row = 0
        if self.memory_os_capability["free"]:
            # Free label
            self.lbl_free = QLabel("Free:")
            self.lbl_free.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_free_value = QLabel("")
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setToolTip(
                "Memory not being used at all (zeroed) that is readily available; note that this doesn’t reflect the actual memory available (use available instead). total - used does not necessarily match free."
            )
            # Free Color button
            self.color_button_free = ColorButton(color="green")
            # Insert Free labels on the right position
            self.layout.addWidget(self.lbl_free, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_free_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_free, grid_row, grid_col + 2, 1, 1)

            self.layout.setRowStretch(grid_col, 0)
            grid_row += 1

        if self.memory_os_capability["wired"]:
            # Wired label
            self.lbl_wired = QLabel("Wired:")
            self.lbl_wired.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_wired_value = QLabel("")
            self.lbl_wired_value.setAlignment(Qt.AlignRight)
            self.lbl_wired_value.setToolTip("Memory that is marked to always stay in RAM. It is never moved to disk.")
            # Free Color button
            self.color_button_wired = ColorButton(color="red")
            # Insert Free labels on the right position
            self.layout.addWidget(self.lbl_wired, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_wired_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_wired, grid_row, grid_col + 2, 1, 1)

            grid_row += 1

        # PSUtil can return active
        if self.memory_os_capability["active"]:
            # Active label
            self.lbl_active = QLabel("Active:")
            self.lbl_active.setAlignment(Qt.AlignRight)
            # Active label value
            self.lbl_active_value = QLabel("")
            self.lbl_active_value.setAlignment(Qt.AlignRight)
            self.lbl_active_value.setToolTip("Memory currently in use or very recently used, and so it is in RAM.")
            # Active Color button
            self.color_button_active = ColorButton(color="orange")
            # Insert Active labels on the right position
            self.layout.addWidget(self.lbl_active, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_active_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_active, grid_row, grid_col + 2, 1, 1)
            grid_row += 1

        # PSUtil can return inactive
        if self.memory_os_capability["inactive"]:
            # Inactive label
            self.lbl_inactive = QLabel("Inactive:")
            self.lbl_inactive.setAlignment(Qt.AlignRight)
            # Inactive label value
            self.lbl_inactive_value = QLabel("")
            self.lbl_inactive_value.setAlignment(Qt.AlignRight)
            self.lbl_inactive_value.setToolTip("Memory that is marked as not used.")
            # Inactive Color button
            self.color_button_inactive = ColorButton(color="blue")
            # Insert Inactive labels on the right position
            self.layout.addWidget(self.lbl_inactive, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_inactive_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_inactive, grid_row, grid_col + 2, 1, 1)
            grid_row += 1

        # PSUtil can return used
        if self.memory_os_capability["used"]:
            # Used label
            self.lbl_used = QLabel("Used:")
            self.lbl_used.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_used_value = QLabel("")
            self.lbl_used_value.setAlignment(Qt.AlignRight)
            self.lbl_used_value.setToolTip(
                "Memory used, calculated differently depending on the platform and designed for informational purposes only. <b>total - free</b> does not necessarily match <b>used</b>."
            )
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_used, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_used_value, grid_row, grid_col + 1, 1, 1)

        # Position management
        # Set col and row to the second widget Position
        grid_row = 0
        grid_col += 3

        # PSUtil can return available
        if self.memory_os_capability["available"]:
            # Used label
            self.lbl_available = QLabel("Available:")
            self.lbl_available.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_available_value = QLabel("")
            self.lbl_available_value.setAlignment(Qt.AlignRight)
            self.lbl_available_value.setToolTip(
                "The memory that can be given instantly to processes without the system going into swap. <br>"
            )
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_available, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_available_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return buffers
        if self.memory_os_capability["buffers"]:
            # Used label
            self.lbl_buffers = QLabel("Buffers:")
            self.lbl_buffers.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_buffers_value = QLabel("")
            self.lbl_buffers_value.setAlignment(Qt.AlignRight)
            self.lbl_buffers_value.setToolTip("Cache for things like file system metadata.<br>")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_buffers, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_buffers_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return cached
        if self.memory_os_capability["cached"]:
            # Used label
            self.lbl_cached = QLabel("Cached:")
            self.lbl_cached.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_cached_value = QLabel("")
            self.lbl_cached_value.setAlignment(Qt.AlignRight)
            self.lbl_cached_value.setToolTip("Cache for various things.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_cached, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_cached_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return shared
        if self.memory_os_capability["shared"]:
            # Used label
            self.lbl_shared = QLabel("Shared:")
            self.lbl_shared.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_shared_value = QLabel("")
            self.lbl_shared_value.setAlignment(Qt.AlignRight)
            self.lbl_shared_value.setToolTip("Memory that may be simultaneously accessed by multiple processes.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_shared, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_shared_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return lab
        if self.memory_os_capability["slab"]:
            # Used label
            self.lbl_slab = QLabel("Slab:")
            self.lbl_slab.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_slab_value = QLabel("")
            self.lbl_slab_value.setAlignment(Qt.AlignRight)
            self.lbl_slab_value.setToolTip("in-kernel data structures cache.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_slab, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_slab_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        grid_col += 2
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.refresh()

    def refresh(self):
        # >>> psutil.virtual_memory()
        # svmem(total=10367352832, available=6472179712, percent=37.6, used=8186245120,
        # free=2181107712, active=4748992512, inactive=2758115328, buffers=790724608,
        # cached=3500347392, shared=787554304)
        vm = psutil.virtual_memory()
        # Free
        if self.memory_os_capability["free"]:
            self.lbl_free_value.setText(f"<font color={self.color_button_free.color()}>{bytes2human(vm.free)}</font>")

        # Wired
        if self.memory_os_capability["wired"]:
            self.lbl_wired_value.setText(
                f"<font color={self.color_button_wired.color()}>{bytes2human(vm.wired)}</font>"
            )

        # Active
        if self.memory_os_capability["active"]:
            self.lbl_active_value.setText(
                f"<font color={self.color_button_active.color()}>{bytes2human(vm.active)}</font>"
            )

        # Inactive
        if self.memory_os_capability["inactive"]:
            self.lbl_inactive_value.setText(
                f"<font color={self.color_button_inactive.color()}>{bytes2human(vm.inactive)}</font>"
            )

        # Used
        if self.memory_os_capability["used"]:
            self.lbl_used_value.setText(bytes2human(vm.used))

        # Available
        if self.memory_os_capability["available"]:
            self.lbl_available_value.setText(bytes2human(vm.available))

        # Buffers
        if self.memory_os_capability["buffers"]:
            self.lbl_buffers_value.setText(bytes2human(vm.buffers))

        # Cached
        if self.memory_os_capability["cached"]:
            self.lbl_cached_value.setText(bytes2human(vm.cached))

        # Shared
        if self.memory_os_capability["shared"]:
            self.lbl_shared_value.setText(bytes2human(vm.shared))

        # Slab
        if self.memory_os_capability["slab"]:
            self.lbl_slab_value.setText(bytes2human(vm.slab))

        # # VM Size
        # vm_size = 0
        # # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        # p = psutil.Process()
        # with p.oneshot():
        #     # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
        #     for proc in psutil.process_iter():
        #         # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.memory_info
        #         vm_size += proc.memory_info().vms
        #
        # self.lbl_vm_size_value.setText(bytes2human(vm_size))

        # Swap used
        # self.lbl_swap_used_value.setText(bytes2human(psutil.swap_memory().used))


class TabDiskActivity(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class TabDiskUsage(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class ProcessMonitor(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.searchLineEdit = None
        self.filterComboBox = None
        self.tree_view_model = None
        self.process_tree = None
        self.tree_view_model = None
        self.kill_process_action = None
        self.inspect_process_action = None
        self.selected_pid = -1
        self.my_username = os.getlogin()

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
        header = ["Process ID", "Process Name", "User", "% CPU", "# Threads", "Real Memory", "Virtual Memory"]

        self.tree_view_model = QStandardItemModel()

        for p in psutil.process_iter():
            with p.oneshot():
                row = [
                    QStandardItem(f'{p.pid}'),
                    QStandardItem(f'{p.name()}'),
                    QStandardItem(f'{p.username()}'),
                    QStandardItem(f'{p.cpu_percent()}'),
                    QStandardItem(f'{p.num_threads()}'),
                    QStandardItem(f'{bytes2human(p.memory_info().rss)}'),
                    QStandardItem(f'{bytes2human(p.memory_info().vms)}'),
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
                    elif combo_box_current_index == 8:
                        pass

                    if combo_box_current_index == 9:
                        if (time.time() - p.create_time()) % 60 <= 43200:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)

        for pos, title in enumerate(header):
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, title)

            self.process_tree.resizeColumnToContents(pos)

        self.process_tree.setModel(self.tree_view_model)
        if self.selected_pid > 0:
            self.selectItem(str(self.selected_pid))

        for pos in range(len(header) - 1):
            self.process_tree.resizeColumnToContents(pos)

    def selectClear(self):
        self.selected_pid = -1
        self.process_tree.clearSelection()
        self.kill_process_action.setEnabled(False)
        self.inspect_process_action.setEnabled(False)

    def selectItem(self, itemOrText):
        oldIndex = self.process_tree.selectionModel().currentIndex()
        newIndex = None
        try:  # an item is given--------------------------------------------
            newIndex = self.process_tree.model().indexFromItem(itemOrText)
        except:  # a text is given and we are looking for the first match---
            # for toto in self.process_tree.model().index(0, 0):
            #     print(toto)
            listIndexes = self.process_tree.model().match(self.process_tree.model().index(0, 0),
                                                          Qt.DisplayRole,
                                                          itemOrText,
                                                          Qt.MatchStartsWith)
            if listIndexes:
                newIndex = listIndexes[0]
        if newIndex:
            self.process_tree.selectionModel().select(  # programmatical selection---------
                newIndex,
                QItemSelectionModel.ClearAndSelect)

    def onClicked(self):
        self.selected_pid = int(self.tree_view_model.itemData(self.process_tree.selectedIndexes()[0])[0])
        if self.selected_pid:
            self.kill_process_action.setEnabled(True)
            self.inspect_process_action.setEnabled(True)

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
        print(selected)
        if selected is not None:
            pid = int(selected.text(0))
            try:
                self.selected_pid = -1
            except:
                pass


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.icon_size = 32
        self.filters = [
            'All Processes',
            'All Processes, Hierarchically',
            'My Processes',
            'System Processes',
            'Other User Processes',
            'Active Processes',
            'Inactive Processes',
            'Windowed Processes',
            'Selected Processes',
            'Application in last 12 hours',
        ]

        # vars
        self.filterComboBox = None
        self.searchLineEdit = None
        self.process_monitor = None
        self.tabs = None
        self.timer = QTimer()

        self.setupUi()

        self._timer_change_for_5_secs()
        self.timer.timeout.connect(self.refresh)


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
        self.searchLineEdit = QLineEdit()
        self.filterComboBox = QComboBox()
        self.process_monitor = ProcessMonitor()
        self.process_monitor.filterComboBox = self.filterComboBox
        self.process_monitor.searchLineEdit = self.searchLineEdit

        self.searchLineEdit.textChanged.connect(self.process_monitor.refresh)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)

        self._createMenuBar()
        self._createActions()
        self._createToolBars()

        self.process_monitor.kill_process_action = self.kill_process_action
        self.process_monitor.inspect_process_action = self.inspect_process_action
        self.quitShortcut1 = QShortcut(QKeySequence('Escape'), self)
        self.quitShortcut1.activated.connect(self.process_monitor.selectClear)

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

        self.tabs = QTabWidget()
        self.tabs.addTab(TabCpu(), "CPU")
        self.tabs.addTab(TabSystemMemory(), "System Memory")
        self.tabs.addTab(TabDiskActivity(), "Disk Activity")
        self.tabs.addTab(TabDiskUsage(), "Disk Usage")
        self.tabs.addTab(TabNetwork(), "Network")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_monitor, 1)
        layout.addWidget(QLabel(""))
        layout.addWidget(self.tabs)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        self.window_minimized = False

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

    def refresh(self):
        self.process_monitor.refresh()
        self.tabs.currentWidget().refresh()

    def _createMenuBar(self):
        self.menuBar = QMenuBar()

        # File Menu
        fileMenu = self.menuBar.addMenu("&File")

        quitAct = QAction('Quit', self)
        quitAct.setStatusTip('Quit this application')
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

        viewMenuUpdateFrequency = viewMenu.addMenu("Update Frequency")

        ActionMenuViewUpdateFrequency5Secs = QAction('5 Secs', self)
        ActionMenuViewUpdateFrequency5Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency5Secs.triggered.connect(self._timer_change_for_5_secs)

        ActionMenuViewUpdateFrequency3Secs = QAction('3 Secs', self)
        ActionMenuViewUpdateFrequency3Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency3Secs.triggered.connect(self._timer_change_for_3_secs)

        ActionMenuViewUpdateFrequency1Sec = QAction('1 Secs', self)
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

        self.ActionMenuViewAllProcesses = QAction('All Processes', self)
        self.ActionMenuViewAllProcesses.setCheckable(True)
        self.ActionMenuViewAllProcesses.triggered.connect(self._filter_by_all_processes)

        self.ActionMenuViewAllProcessesHierarchically = QAction('All Processes, Hierarchically', self)
        self.ActionMenuViewAllProcessesHierarchically.setCheckable(True)
        self.ActionMenuViewAllProcessesHierarchically.triggered.connect(self._filter_by_all_process_hierarchically)

        self.ActionMenuViewMyProcesses = QAction('My Processes', self)
        self.ActionMenuViewMyProcesses.setCheckable(True)
        self.ActionMenuViewMyProcesses.triggered.connect(self._filter_by_my_processes)

        self.ActionMenuViewSystemProcesses = QAction('System Processes', self)
        self.ActionMenuViewSystemProcesses.setCheckable(True)
        self.ActionMenuViewSystemProcesses.triggered.connect(self._filter_by_system_processes)

        self.ActionMenuViewOtherUserProcesses = QAction('Other User Processes', self)
        self.ActionMenuViewOtherUserProcesses.setCheckable(True)
        self.ActionMenuViewOtherUserProcesses.triggered.connect(self._filter_by_other_user_processes)

        self.ActionMenuViewActiveProcesses = QAction('Active Processes', self)
        self.ActionMenuViewActiveProcesses.setCheckable(True)
        self.ActionMenuViewActiveProcesses.triggered.connect(self._filter_by_active_processes)

        self.ActionMenuViewInactiveProcesses = QAction('Inactive Processes', self)
        self.ActionMenuViewInactiveProcesses.setCheckable(True)
        self.ActionMenuViewInactiveProcesses.triggered.connect(self._filter_by_inactive_processes)

        self.ActionMenuViewWindowedProcesses = QAction('Windowed Processes', self)
        self.ActionMenuViewWindowedProcesses.setCheckable(True)
        self.ActionMenuViewWindowedProcesses.triggered.connect(self._filter_by_windowed_processes)

        self.ActionMenuViewSelectedProcesses = QAction('Selected Processes', self)
        self.ActionMenuViewSelectedProcesses.setCheckable(True)
        self.ActionMenuViewSelectedProcesses.setEnabled(False)
        self.ActionMenuViewSelectedProcesses.triggered.connect(self._filter_by_selected_processes)

        self.ActionMenuViewApplicationInLast12Hours = QAction('Application in last 12 hours', self)
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

        viewMenu.addActions([self.ActionMenuViewAllProcesses,
                             self.ActionMenuViewAllProcessesHierarchically,
                             self.ActionMenuViewMyProcesses,
                             self.ActionMenuViewSystemProcesses,
                             self.ActionMenuViewOtherUserProcesses,
                             self.ActionMenuViewActiveProcesses,
                             self.ActionMenuViewInactiveProcesses,
                             self.ActionMenuViewWindowedProcesses,
                             self.ActionMenuViewSelectedProcesses,
                             self.ActionMenuViewApplicationInLast12Hours,
                             ])

        viewMenu.addSeparator()

        viewFilterProcesses = QAction('Filter Processes', self)
        viewFilterProcesses.setShortcut("Ctrl+Meta+F")
        viewFilterProcesses.setEnabled(False)

        viewInspectProcess = QAction('Inspect Process', self)
        viewInspectProcess.setShortcut("Ctrl+I")
        viewInspectProcess.setEnabled(False)

        viewSampleProcess = QAction('Sample Process', self)
        viewSampleProcess.setShortcut("Ctrl+Meta+S")
        viewSampleProcess.setEnabled(False)

        viewRunSpindump = QAction('Run Spindump', self)
        viewRunSpindump.setShortcut("Alt+Ctrl+Meta+S")
        viewRunSpindump.setEnabled(False)

        viewRunSystemDiagnostics = QAction('Run system Diagnostics', self)
        viewRunSystemDiagnostics.setEnabled(False)

        viewQuitProcess = QAction('Quit Process', self)
        viewQuitProcess.setShortcut("Ctrl+Meta+Q")
        viewQuitProcess.setEnabled(False)

        viewSendSignalToProcesses = QAction('Send Signal to Processes', self)
        viewSendSignalToProcesses.setEnabled(False)

        viewShowDeltasForProcess = QAction('Show Deltas for Process', self)
        viewShowDeltasForProcess.setShortcut("Ctrl+Meta+J")
        viewShowDeltasForProcess.setEnabled(False)

        viewMenu.addActions([
            viewFilterProcesses,
            viewInspectProcess,
            viewSampleProcess,
            viewRunSpindump,
            viewRunSystemDiagnostics,
            viewQuitProcess,
            viewSendSignalToProcesses,
            viewShowDeltasForProcess,
        ])

        viewMenu.addSeparator()

        viewClearCPUHistory = QAction('Clear CPU History', self)
        viewClearCPUHistory.setShortcut("Ctrl+K")

        viewEnterFullScreen = QAction('Enter Full Screen', self)
        viewEnterFullScreen.setEnabled(False)

        viewMenu.addActions([
            viewClearCPUHistory,
            viewEnterFullScreen,
        ])

        # Window Menu
        windowMenu = self.menuBar.addMenu("Window")

        ActionMenuWindowMinimize = QAction('Minimize', self)
        ActionMenuWindowMinimize.setShortcut("Ctrl+M")
        ActionMenuWindowMinimize.triggered.connect(self._window_minimize)

        self.ActionMenuWindowZoom = QAction('Zoom', self)
        self.ActionMenuWindowZoom.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowMinimize)
        windowMenu.addAction(self.ActionMenuWindowZoom)
        windowMenu.addSeparator()

        ActionMenuWindowActivityMonitor = QAction('Activity Monitor', self)
        ActionMenuWindowActivityMonitor.setShortcut("Ctrl+1")
        ActionMenuWindowActivityMonitor.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowActivityMonitor)

        # Help Menu
        helpMenu = self.menuBar.addMenu("&Help")

        aboutAct = QAction('&About', self)
        aboutAct.setStatusTip('About this application')
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
        # self.filterComboBox = QComboBox()
        # for pos, text in enumerate(self.filters):
        #     self.filterComboBox.addItem(text)
        self.filterComboBox.addItems(self.filters)

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

    def _showAbout(self):
        about = About()
        about.size = 300, 340
        about.icon = QPixmap(
            os.path.join(
                os.path.dirname(__file__),
                "activity_monitor",
                "ui",
                "Processes.png",
            )).scaledToWidth(96, Qt.SmoothTransformation)
        about.name = __app_name__
        about.version = f"Version {__app_version__}"
        about.text = f"This project is open source, contributions are welcomed.<br><br>" \
                     f"Visit <a href='{__app_url__}'>{__app_url__}</a> for more information, " \
                     f"report bug or to suggest a new feature<br>"
        about.credit = "Copyright 2023-2023 helloSystem team. All rights reserved"
        about.show()

    # def close(self):
    #     print("Quitting...")
    #     sys.exit(0)
    def _filter_ComboBox_refresh(self):
        print(self.filterComboBox.currentIndex())
        for pos, text in enumerate(self.filters):
            if self.filterComboBox.currentIndex() == pos:
                self.filterComboBox.setItemText(pos, f"√ {text}")
            else:
                self.filterComboBox.setItemText(pos, f" {text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        win = Window()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass
