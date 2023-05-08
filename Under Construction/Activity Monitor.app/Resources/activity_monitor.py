#!/usr/bin/env python3

import hashlib
import os
import signal
import sys

import psutil
from PyQt5.QtCore import QTimer, Qt, QSize, pyqtSignal as Signal, QPoint, QObject, QModelIndex, QItemSelectionModel
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QTreeWidgetItem,
    QToolBar,
    QVBoxLayout,
    QPushButton,
    QAbstractItemView,
    QShortcut,
    QLabel,
    QColorDialog,
    QAction,
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

        self.selected_pid = -1
        self.my_username = os.getlogin()

        self.setupUi()

    def setupUi(self):
        self.tree_view_model = QStandardItemModel()
        self.process_tree = QTreeView()
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

    def refresh_process_tree(self):

        self.process_tree.clear()
        for p in psutil.process_iter():
            with p.oneshot():
                # print(p.info["pid"])
                # print(p.info["name"])
                item = QTreeWidgetItem()
                item.setText(0, f'{p.pid}')
                item.setText(1, f'{p.name()}')
                item.setText(2, f'{p.username()}')
                item.setText(3, f'{p.cpu_percent()}')
                item.setText(4, f'{p.num_threads()}')
                item.setText(5, f'{bytes2human(p.memory_info().rss)}')
                item.setText(6, f'{bytes2human(p.memory_info().vms)}')

                # Filter
                if self.searchLineEdit.text():
                    if self.searchLineEdit.text() in p.name():
                        self.process_tree.addTopLevelItem(item)
                else:
                    self.process_tree.addTopLevelItem(item)

                # if p.pid in self.selectedPid:
                #     self.process_tree.setCurrentIndex(somemodelindex);
                #     self.process_tree.setCurrentItem(item)
        # item.selectedIndexes(self.selected_processes_id)

        for i in range(self.process_tree.columnCount()):
            self.process_tree.resizeColumnToContents(i)

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
        pos = 0
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

                # Filter
                filtered_row = None
                if hasattr(self.searchLineEdit, "text") and self.searchLineEdit.text():
                    if self.searchLineEdit.text() in p.name():
                        filtered_row = row
                else:
                    filtered_row = row

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
                        pass

                    if self.filterComboBox.currentIndex() == 1:
                        pass
                    else:
                        pass

                    if self.filterComboBox.currentIndex() == 2:
                        if p.username() == self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if self.filterComboBox.currentIndex() == 3:
                        if p.uids().real < 1000:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if self.filterComboBox.currentIndex() == 4:
                        if p.username() != self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if self.filterComboBox.currentIndex() == 5:
                        pass
                    elif self.filterComboBox.currentIndex() == 6:
                        pass
                    elif self.filterComboBox.currentIndex() == 7:
                        pass
                    elif self.filterComboBox.currentIndex() == 8:
                        pass
                    elif self.filterComboBox.currentIndex() == 9:
                        pass
                    else:
                        pass

                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)
                    if self.selected_pid == p.pid:
                        print(f"select: {p.pid} {p.name()}")
                        # index = self.treeview_model.index(pos, pos)
                        # self.treeview_model.setCurrentIndex(index, QItemSelectionModel.NoUpdate)
            pos += 1

        for pos, title in enumerate(header):
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, title)

            self.process_tree.resizeColumnToContents(pos)

        self.process_tree.setModel(self.tree_view_model)
        for pos in range(len(header) - 1):
            self.process_tree.resizeColumnToContents(pos)

    def onClicked(self):
        self.selected_pid = int(self.tree_view_model.itemData(self.process_tree.selectedIndexes()[0])[0])

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
        self.selected_filter_index = 1
        # self.filters = {
        #     1: 'All Processes',
        #     2: 'All Processes, Hierarchically',
        #     3: 'My Processes',
        #     4: 'System Processes',
        #     5: 'Other User Processes',
        #     6: 'Active Processes',
        #     7: 'Inactive Processes',
        #     8: 'Windowed Processes',
        #     9: 'Selected Processes',
        #     10: 'Application in last 12 hours',
        # }
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

        self.setupUi()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

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
        self.filterComboBox.currentIndexChanged.connect(self.process_monitor.refresh)


        self._createMenuBar()
        self._createActions()
        self._createToolBars()

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

        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close)

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

    def refresh(self):
        self.process_monitor.refresh()
        self.tabs.currentWidget().refresh()

    def _createMenuBar(self):
        menuBar = QMenuBar()

        fileMenu = menuBar.addMenu("&File")
        editMenu = menuBar.addMenu("&Edit")

        aboutAct = QAction('&About', self)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(aboutAct)

        self.setMenuBar(menuBar)

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
        self.inspect_process_action.setShortcut("Ctrl+i")
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
