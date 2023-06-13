#!/usr/bin/env python3

import sys
import psutil
import time
import os
from collections import deque

# Qt import
from PyQt5.QtCore import Qt, QTimer, QThread, QThreadPool
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QActionGroup,
    QLabel,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
    QLineEdit,
    QComboBox,
    QShortcut,
)

# The Main Window
from main_window_ui import Ui_MainWindow

# The Process TreeView
from treeview_processes import TreeViewProcess

# Tabs
from tab_cpu import TabCpu
from tab_system_memory import TabSystemMemory
from tab_disk_activity import TabDiskActivity
from tab_disk_usage import TabDiskUsage
from tab_network import TabNetwork

# Dialog's
from dialog_send_signal import SendSignalDialog
from dialog_kill_process import KillProcessDialog
from dialog_about import AboutDialog
from dialog_inspect_process import InspectProcess
from dialog_sample_process import SampleProcess
from dialog_cpu_history import CPUHistory

# Back end libs
from widget_chartpie import ChartPieItem
from worker_psutil import PSUtilsWorker
from worker_icons_cache import IconsCacheWorker

from utility import bytes2human, get_process_application_name, get_process_environ


class Window(
    QMainWindow, Ui_MainWindow, TabCpu, TabSystemMemory, TabDiskActivity, TabDiskUsage, TabNetwork, TreeViewProcess
):
    def __init__(self, parent=None):
        super().__init__(parent)
        TabCpu.__init__(self)
        TabSystemMemory.__init__(self)
        TabDiskActivity.__init__(self)
        TabDiskUsage.__init__(self)
        TabNetwork.__init__(self)
        TreeViewProcess.__init__(self)

        # Worker
        self.threads = []
        self.threadpool = QThreadPool()
        self.__icons = {}

        # ToolBar custom widgets
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
        self.filter_process_action = None
        self.search_process_action = None
        self.searchLineEdit = None
        self.filterComboBox = None

        self.cpu_history_dialog = None

        # Tab System Memory
        self.memory_os_capability = None
        self.chart_pie_item_memory_free = None
        self.chart_pie_item_memory_wired = None
        self.chart_pie_item_memory_active = None
        self.chart_pie_item_memory_inactive = None

        # Tab Disk Usage
        self.chart_pie_item_utilized = None
        self.chart_pie_item_free = None

        # TreeView
        self.tree_view_model = None

        # Multi windows inspection and sample capability
        self.inspect_process_dialogs = {}
        self.sample_process_dialogs = {}

        self.setupUi(self)
        self.setupCustomUi()

        self.timer = QTimer()
        self._timer_change_for_5_secs()

        self.connectSignalsSlots()

        self.setupInitialState()

        self.refresh()
        for header_pos in range(len(self.process_tree.header())):
            self.process_tree.resizeColumnToContents(header_pos)

    def focusOutEvent(self, event):
        self.showNormal()

    def setupCustomUi(self):
        self.setupCustomUiGroups()
        self.setupCustomUiToolBar()

        # CPU History
        self.cpu_history_dialog = CPUHistory()
        self.cpu_history_dialog.hide()

        # Configure Chart Data
        # System Memory
        self.chart_pie_item_memory_free = ChartPieItem()
        self.chart_pie_item_memory_free.setColor(Qt.black)
        self.chart_pie_item_memory_free.data = 0

        self.chart_pie_item_memory_wired = ChartPieItem()
        self.chart_pie_item_memory_wired.setColor(Qt.black)
        self.chart_pie_item_memory_wired.setData(0)

        self.chart_pie_item_memory_active = ChartPieItem()
        self.chart_pie_item_memory_active.setColor(Qt.black)
        self.chart_pie_item_memory_active.setData(0)

        self.chart_pie_item_memory_inactive = ChartPieItem()
        self.chart_pie_item_memory_inactive.setColor(Qt.black)
        self.chart_pie_item_memory_inactive.setData(0)

        self.system_memory_chart_pie.addItems(
            [
                self.chart_pie_item_memory_free,
                self.chart_pie_item_memory_wired,
                self.chart_pie_item_memory_active,
                self.chart_pie_item_memory_inactive,
            ]
        )

        # Disk Usage
        self.chart_pie_item_utilized = None
        self.chart_pie_item_free = None

        self.chart_pie_item_utilized = ChartPieItem()
        self.chart_pie_item_utilized.color = Qt.black
        self.chart_pie_item_utilized.data = 0

        self.chart_pie_item_free = ChartPieItem()
        self.chart_pie_item_free.color = Qt.black
        self.chart_pie_item_free.data = 0

        self.chart_pie.addItems(
            [
                self.chart_pie_item_utilized,
                self.chart_pie_item_free,
            ]
        )

    def setupInitialState(self):
        # Set Menu ShortCut With Meta Key
        self.ActionMenuViewFilterProcesses.setShortcut("Ctrl+Meta+F")
        self.ActionMenuViewSampleProcess.setShortcut("Ctrl+Meta+S")
        self.ActionMenuViewRunSpindump.setShortcut("Alt+Ctrl+Meta+S")
        self.ActionMenuViewKillDialog.setShortcut("Ctrl+Meta+Q")
        self.ActionMenuViewShowDeltasforProcess.setShortcut("Ctrl+Meta+J")

        self.setupCustomUiColorPicker()

        virtual_memory = psutil.virtual_memory()
        self.memory_os_capability = {
            "total": hasattr(virtual_memory, "total"),
            "available": hasattr(virtual_memory, "available"),
            "percent": hasattr(virtual_memory, "percent"),
            "used": hasattr(virtual_memory, "used"),
            "free": hasattr(virtual_memory, "free"),
            "active": hasattr(virtual_memory, "active"),
            "inactive": hasattr(virtual_memory, "inactive"),
            "buffers": hasattr(virtual_memory, "buffers"),
            "cached": hasattr(virtual_memory, "cached"),
            "shared": hasattr(virtual_memory, "shared"),
            "slab": hasattr(virtual_memory, "slab"),
            "wired": hasattr(virtual_memory, "wired"),
        }
        # self.system_memory_total_value.setText("%s" % bytes2human(virtual_memory.total))

        if self.memory_os_capability["wired"] is False:
            self.system_memory_wired.hide()
            self.system_memory_wired_value.hide()
            self.color_picker_wired_value.hide()

        if self.memory_os_capability["slab"] is False:
            self.system_memory_slab.hide()
            self.system_memory_slab_value.hide()

        self.tree_view_model = QStandardItemModel()
        self.process_tree.setModel(self.tree_view_model)
        self.process_tree.sortByColumn(3, Qt.DescendingOrder)

    def setupCustomUiColorPicker(self):
        # Tab CPU
        self.color_picker_user_value.setColor("green")
        self.color_picker_system_value.setColor("red")
        self.color_picker_nice_value.setColor("blue")
        self.color_picker_irq_value.setColor("orange")
        self.color_picker_idle_value.setColor("black")
        # Tab System Memory
        self.color_picker_free_value.setColor("green")
        self.color_picker_wired_value.setColor("red")
        self.color_picker_active_value.setColor("orange")
        self.color_picker_inactive_value.setColor("blue")
        # Tab Disk Activity
        self.color_picker_data_read_sec_value.setColor("green")
        self.color_picker_data_written_sec_value.setColor("red")
        # Disk Usage
        self.color_button_space_free.setColor("green")
        self.color_button_space_utilized.setColor("red")
        # Network
        self.color_picker_data_received_sec_value.setColor("green")
        self.color_picker_data_sent_sec_value.setColor("red")

    def setupCustomUiGroups(self):
        menu_frequency_group = QActionGroup(self)
        menu_frequency_group.addAction(self.ActionUpdateFrequencyTo1Sec)
        menu_frequency_group.addAction(self.ActionUpdateFrequencyTo3Secs)
        menu_frequency_group.addAction(self.ActionUpdateFrequencyTo5Secs)

        menu_filter_by_group = QActionGroup(self)
        menu_filter_by_group.addAction(self.ActionMenuViewAllProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewAllProcessesHierarchically)
        menu_filter_by_group.addAction(self.ActionMenuViewMyProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewSystemProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewOtherUserProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewActiveProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewInactiveProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewWindowedProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewSelectedProcesses)
        menu_filter_by_group.addAction(self.ActionMenuViewApplicationInLast12Hours)

    def setupCustomUiToolBar(self):
        showLabel = QLabel("Show")
        showLabel.setAlignment(Qt.AlignCenter)

        showVBoxLayout = QVBoxLayout()
        self.filterComboBox = QComboBox()
        self.filterComboBox.addItems(self.filters)
        self.filterComboBox.model().item(8).setEnabled(False)

        self.filterComboBox.setCurrentIndex(0)

        showVBoxLayout.addWidget(self.filterComboBox)
        showVBoxLayout.addWidget(showLabel)

        showWidget = QWidget()
        showWidget.setLayout(showVBoxLayout)

        self.filter_process_action = QWidgetAction(self)
        self.filter_process_action.setDefaultWidget(showWidget)

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setClearButtonEnabled(True)

        searchLabel = QLabel("Search")
        searchLabel.setAlignment(Qt.AlignCenter)

        searchVBoxLayout = QVBoxLayout()
        searchVBoxLayout.addWidget(self.searchLineEdit)
        searchVBoxLayout.addWidget(searchLabel)

        searchWidget = QWidget()
        searchWidget.setLayout(searchVBoxLayout)

        self.search_process_action = QWidgetAction(self)
        self.search_process_action.setDefaultWidget(searchWidget)

        self.toolBar.addAction(self.filter_process_action)
        self.toolBar.addAction(self.search_process_action)

    def connectSignalsSlots(self):
        self.timer.timeout.connect(self.refresh)

        # Menu and ToolBar
        self.ActionToolBarInspectProcess.triggered.connect(self._showInspectProcessDialog)
        self.ActionToolBarSampleProcess.triggered.connect(self._showSampleProcessDialog)
        self.ActionUpdateFrequencyTo5Secs.triggered.connect(self._timer_change_for_5_secs)
        self.ActionUpdateFrequencyTo3Secs.triggered.connect(self._timer_change_for_3_secs)
        self.ActionUpdateFrequencyTo1Sec.triggered.connect(self._timer_change_for_1_sec)

        self.searchLineEdit.textChanged.connect(self.refresh_treeview_model)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)
        self.ActionMenuViewFilterProcesses.triggered.connect(self._searchLineEdit_get_focus)

        self.ActionMenuViewAllProcesses.triggered.connect(self._filter_by_all_processes)
        self.ActionMenuViewAllProcessesHierarchically.triggered.connect(self._filter_by_all_process_hierarchically)
        self.ActionMenuViewMyProcesses.triggered.connect(self._filter_by_my_processes)
        self.ActionMenuViewSystemProcesses.triggered.connect(self._filter_by_system_processes)
        self.ActionMenuViewOtherUserProcesses.triggered.connect(self._filter_by_other_user_processes)
        self.ActionMenuViewActiveProcesses.triggered.connect(self._filter_by_active_processes)
        self.ActionMenuViewInactiveProcesses.triggered.connect(self._filter_by_inactive_processes)
        self.ActionMenuViewWindowedProcesses.triggered.connect(self._filter_by_windowed_processes)
        self.ActionMenuViewSelectedProcesses.triggered.connect(self._filter_by_selected_processes)
        self.ActionMenuViewApplicationInLast12Hours.triggered.connect(self._filter_by_application_in_last_12_hours)

        self.ActionMenuViewSendSignaltoProcesses.triggered.connect(self._showSendSignalDialog)
        self.ActionMenuViewSample.triggered.connect(self._showSampleProcessDialog)
        self.ActionMenuViewInspectProcess.triggered.connect(self._showInspectProcessDialog)

        self.ActionMenuViewKillDialog.triggered.connect(self._showKillDialog)
        self.ActionToolBarQuitProcess.triggered.connect(self._showKillDialog)
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)

        # CPU History
        self.ActionMenuWindowCPUHistory.triggered.connect(self._showCPUHistoryDialog)

        self.color_picker_system_value.colorChanged.connect(self.refresh_color_system)
        self.color_picker_user_value.colorChanged.connect(self.refresh_color_user)
        self.color_picker_idle_value.colorChanged.connect(self.refresh_color_idle)
        self.color_picker_nice_value.colorChanged.connect(self.refresh_color_nice)
        self.color_picker_irq_value.colorChanged.connect(self.refresh_color_irq)

        self.ActionMenuViewClearCPUHistory.triggered.connect(self._clear_cpu_history)

        # Tab system Memory
        self.color_picker_free_value.colorChanged.connect(self.refresh_color_free)
        self.color_picker_active_value.colorChanged.connect(self.refresh_color_active)
        self.color_picker_inactive_value.colorChanged.connect(self.refresh_color_inactive)
        self.color_picker_wired_value.colorChanged.connect(self.refresh_color_wired)

        # Tab Disk Activity
        self.disk_activity_data_radiobutton.toggled.connect(self.refresh_disk_activity_bandwidth)
        self.color_picker_data_read_sec_value.colorChanged.connect(self.refresh_color_data_read_sec)
        self.color_picker_data_written_sec_value.colorChanged.connect(self.refresh_color_data_written_sec)

        # Tab Disk Usage
        self.combobox_devices.currentIndexChanged.connect(self.combobox_index_changed)
        self.mounted_disk_partitions_changed.connect(self.combobox_refresh)
        self.color_button_space_free.colorChanged.connect(self.refresh_color_space_free)
        self.color_button_space_utilized.colorChanged.connect(self.refresh_color_space_utilized)

        # Tab Network
        self.network_packets_radiobutton.toggled.connect(self.refresh_network_bandwidth)
        self.color_picker_data_received_sec_value.colorChanged.connect(self.refresh_color_data_received_sec)
        self.color_picker_data_sent_sec_value.colorChanged.connect(self.refresh_color_data_sent_sec)

        # TreeView
        self.process_tree.clicked.connect(self.onClicked)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self._escape_pressed)

    def createPSUtilsThread(self):
        thread = QThread()
        worker = PSUtilsWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # CPU
        worker.updated_cpu_user.connect(self.set_user)
        worker.updated_cpu_system.connect(self.set_system)
        worker.updated_cpu_idle.connect(self.set_idle)
        worker.updated_cpu_nice.connect(self.set_nice)
        worker.updated_cpu_irq.connect(self.set_irq)
        worker.updated_cpu_cumulative_threads.connect(self.refresh_cumulative_threads)
        worker.updated_cpu_process_number.connect(self.refresh_process_number)

        # System Memory
        worker.updated_system_memory_total.connect(self.set_virtual_memory_total)
        worker.updated_system_memory_available.connect(self.set_virtual_memory_available)
        worker.updated_system_memory_used.connect(self.set_virtual_memory_used)
        worker.updated_system_memory_free.connect(self.set_virtual_memory_free)
        worker.updated_system_memory_active.connect(self.set_virtual_memory_active)
        worker.updated_system_memory_inactive.connect(self.set_virtual_memory_inactive)
        worker.updated_system_memory_buffers.connect(self.set_virtual_memory_buffers)
        worker.updated_system_memory_cached.connect(self.set_virtual_memory_cached)
        worker.updated_system_memory_shared.connect(self.set_virtual_memory_shared)
        worker.updated_system_memory_slab.connect(self.set_virtual_memory_slab)
        worker.updated_system_memory_wired.connect(self.set_virtual_memory_wired)

        # Disk Usage
        worker.updated_mounted_disk_partitions.connect(self.setMoutedDiskPartitions)

        # Disk Activity
        worker.updated_disk_activity_reads_in.connect(self.refresh_reads_in)
        worker.updated_disk_activity_writes_out.connect(self.refresh_writes_out)
        worker.updated_disk_activity_data_read.connect(self.refresh_data_read)
        worker.updated_disk_activity_data_written.connect(self.refresh_data_written)

        # Network
        worker.updated_network_packets_in.connect(self.refresh_packets_in)
        worker.updated_network_packets_out.connect(self.refresh_packets_out)
        worker.updated_network_data_received.connect(self.refresh_data_received)
        worker.updated_network_data_sent.connect(self.refresh_data_sent)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def createIconsCacheThread(self):
        thread = QThread()
        worker = IconsCacheWorker(cache=self.__icons)
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # Icons Cache
        worker.updated_icons_cache.connect(self._refresh_icons_cache)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh(self):
        self.refresh_treeview_model()

        self.threads.clear()
        self.threads = [
            self.createPSUtilsThread(),
            self.createIconsCacheThread(),
        ]
        for thread in self.threads:
            thread.start()

    def refresh_treeview_model(self):
        self.tree_view_model = QStandardItemModel()
        data = []
        for p in psutil.process_iter():
            with p.oneshot():
                try:
                    environ = p.environ()
                except (
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                        psutil.NoSuchProcess,
                ):
                    environ = None
                if environ and "LAUNCHED_BUNDLE" in environ:
                    application_name = os.path.basename(environ["LAUNCHED_BUNDLE"]).rsplit(".", 1)[0]
                else:
                    application_name = p.name()
                data.append({
                    'treeview_id': p.pid,
                    'treeview_parent_id': p.ppid(),
                    "pid": p.pid,
                    "application_name": application_name,
                    'username': p.username(),
                    'cpu_percent': p.cpu_percent(),
                    'num_threads': p.num_threads(),
                    'rss': p.memory_info().rss,
                    'vms': p.memory_info().vms,
                    'environ': environ,
                    'status': p.status(),
                    "uids": p.uids(),
                    "create_time": p.create_time(),
                })

        seen = {}  # List of  QStandardItem
        values = deque(data)
        if self.filterComboBox.currentIndex() == 1:
            is_hierarchical_view = True
        else:
            is_hierarchical_view = False

        while values:
            QApplication.processEvents()
            value = values.popleft()
            if is_hierarchical_view:
                # self.tree_view_model.setRowCount(0)

                if value['treeview_parent_id'] == 0 or value['treeview_parent_id'] is None:
                    parent = self.tree_view_model.invisibleRootItem()
                else:
                    if value['treeview_parent_id'] not in seen:
                        values.append(value)
                        continue
                    parent = seen[value['treeview_parent_id']]

                row = self.treeview_get_row(
                    pid=value['pid'],
                    application_name=value['application_name'],
                    username=value['username'],
                    cpu_percent=value['cpu_percent'],
                    num_threads=value['num_threads'],
                    rss=value['rss'],
                    vms=value['vms'],
                )
                filtered_row = self.apply_search_line_filter(
                    value['application_name'],
                    row
                )

                if filtered_row and parent:
                    parent.appendRow(filtered_row)

                if parent:
                    seen[value['treeview_id']] = parent.child(parent.rowCount() - 1)
            else:
                row = self.treeview_get_row(
                    pid=value['pid'],
                    application_name=value['application_name'],
                    username=value['username'],
                    cpu_percent=value['cpu_percent'],
                    num_threads=value['num_threads'],
                    rss=value['rss'],
                    vms=value['vms'],
                )
                filtered_row = self.apply_search_line_filter(
                    value['application_name'],
                    row
                )
                filtered_row = self.apply_combobox_filter(
                    filtered_row=filtered_row,
                    pid=value['pid'],
                    application_name=value['application_name'],
                    username=value['username'],
                    uids=value['uids'],
                    environ=value['environ'],
                    create_time=value['create_time'],
                    status=value['status'],
                )
                # If after filters it still have something then ad it to the model
                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)

        # Set header it depends on the View menu
        self.set_treeview_headers()

        # Impose the Model to TreeView Processes
        self.tree_view_model.setSortRole(Qt.UserRole)
        self.process_tree.setSortingEnabled(False)
        self.process_tree.setModel(self.tree_view_model)
        self.process_tree.setSortingEnabled(True)
        # if self.filterComboBox.currentIndex() == 1:
        #     self.process_tree.expandAll()

        # Restore the selection
        if self.selected_pid and self.selected_pid >= 0:
            self.selectItem(str(self.selected_pid))

    def treeview_get_row(self, pid, application_name, username, cpu_percent, num_threads, rss, vms):
        row = []
        # PID can't be disabled because it is use for selection tracking
        item = QStandardItem(f"{pid}")
        item.setData(pid, Qt.UserRole)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.append(item)
        if self.ActionViewColumnProcessName.isChecked():
            item = QStandardItem(application_name)
            if application_name in self.__icons:
                item.setIcon(self.__icons[application_name])
            item.setData(application_name, Qt.UserRole)
            row.append(item)
        if self.ActionViewColumnUser.isChecked():
            item = QStandardItem(username)
            item.setData(username, Qt.UserRole)
            row.append(item)
        if self.ActionViewColumnPercentCPU.isChecked():
            item = QStandardItem(f"{cpu_percent}")
            item.setData(float(cpu_percent), Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)
        if self.ActionViewColumnNumThreads.isChecked():
            item = QStandardItem(f"{num_threads}")
            item.setData(num_threads, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)
        if self.ActionViewColumnRealMemory.isChecked():
            item = QStandardItem(bytes2human(rss))
            item.setData(rss, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)
        if self.ActionViewColumnVirtualMemory.isChecked():
            item = QStandardItem(bytes2human(vms))
            item.setData(vms, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)
        return row

    def set_treeview_headers(self):
        # Headers
        # PID is imposed because it is use for selection tracking
        pos = 0
        self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnProcessID.text())
        pos += 1
        if self.ActionViewColumnProcessName.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnProcessName.text())
            pos += 1
        if self.ActionViewColumnUser.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnUser.text())
            pos += 1
        if self.ActionViewColumnPercentCPU.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnPercentCPU.text())
            pos += 1
        if self.ActionViewColumnNumThreads.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnNumThreads.text())
            pos += 1
        if self.ActionViewColumnRealMemory.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnRealMemory.text())
            pos += 1
        if self.ActionViewColumnVirtualMemory.isChecked():
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, self.ActionViewColumnVirtualMemory.text())
            pos += 1

    def apply_search_line_filter(self, application_name, row):
        # Filter Line
        filtered_row = None
        if self.searchLineEdit.text():
            if self.searchLineEdit.text().lower() in application_name.lower():
                filtered_row = row
        else:
            filtered_row = row
        return filtered_row

    def apply_combobox_filter(self, filtered_row, pid, application_name, username, uids, environ, create_time, status):

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
        # 1 - do not touch anything
        # 2 - is a pre-processing
        if self.filterComboBox.currentIndex() == 2:
            if username == self.my_username:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 3:
            if uids.real < 1000:  # Not totally exact but the result is the same
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 4:
            if username != self.my_username:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 5:
            if status == psutil.STATUS_RUNNING:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 6:
            if status == psutil.STATUS_WAITING or status == psutil.STATUS_SLEEPING:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 7:
            if environ and "LAUNCHED_BUNDLE" in environ:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 8:
            if pid == self.selected_pid:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 9:
            if (time.time() - create_time) % 60 <= 43200:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        return filtered_row

    def closeEvent(self, evnt):
        self.cpu_history_dialog.have_to_close = True
        self.cpu_history_dialog.close()

        for pid, inspection_dialog in self.inspect_process_dialogs.items():
            inspection_dialog.close()

        for pid, sample_dialog in self.sample_process_dialogs.items():
            sample_dialog.close()

        super(Window, self).closeEvent(evnt)

    def _refresh_icons_cache(self, application_icons):
        for application_name, icon in application_icons.items():
            if application_name not in self.__icons:
                self.__icons[application_name] = icon

    def _showInspectProcessDialog(self):
        if self.ActionMenuViewInspectProcess.isEnabled():
            if self.selected_pid not in self.inspect_process_dialogs:
                inspect_process_dialog = InspectProcess(process=psutil.Process(self.selected_pid))
                inspect_process_dialog.buttonSample.clicked.connect(self._showSampleProcessDialog)
                inspect_process_dialog.run()
                inspect_process_dialog.show()
                self.inspect_process_dialogs[self.selected_pid] = inspect_process_dialog
            else:
                self.inspect_process_dialogs[self.selected_pid].run()
                self.inspect_process_dialogs[self.selected_pid].show()

    def _showSampleProcessDialog(self):
        if self.ActionToolBarSampleProcess.isEnabled():
            if self.selected_pid not in self.sample_process_dialogs:
                sample_process_dialog = SampleProcess(process=psutil.Process(self.selected_pid))
                sample_process_dialog.show()
                self.sample_process_dialogs[self.selected_pid] = sample_process_dialog
            else:
                self.sample_process_dialogs[self.selected_pid].run()
                self.sample_process_dialogs[self.selected_pid].show()

    def _showSendSignalDialog(self):
        if self.ActionMenuViewSendSignaltoProcesses.isEnabled():
            self.send_signal_dialog = SendSignalDialog(process=psutil.Process(self.selected_pid))
            self.send_signal_dialog.show()

    def _showKillDialog(self):
        if self.ActionMenuViewKillDialog.isEnabled():
            self.KillDialog = KillProcessDialog(process=psutil.Process(self.selected_pid))

            self.KillDialog.process_signal_quit.connect(self.SIGQUITSelectedProcess)
            self.KillDialog.process_signal_kill.connect(self.SIGKILLSelectedProcess)

            self.KillDialog.show()

    def _showCPUHistoryDialog(self):
        if self.cpu_history_dialog.isVisible():
            self.cpu_history_dialog.hide()
        else:
            self.cpu_history_dialog.show()
        self.activateWindow()
        self.setFocus()

        # self.cpu_history_dialog.process_signal_quit.connect(self.SIGQUITSelectedProcess)
        # self.cpu_history_dialog.process_signal_kill.connect(self.SIGKILLSelectedProcess)
        #
        # self.cpu_history_dialog.show()

    def _showAboutDialog(self):
        self.AboutDialog = AboutDialog()
        self.AboutDialog.show()

    def _escape_pressed(self):
        if self.process_tree.hasFocus():
            self.selectClear()
        if self.searchLineEdit.hasFocus():
            self.process_tree.setFocus()
        if self.filterComboBox.hasFocus():
            self.process_tree.setFocus()

    def _timer_change_for_1_sec(self):
        self.timer_value = 1
        self.timer.start(1000)

    def _timer_change_for_3_secs(self):
        self.timer_value = 3
        self.timer.start(3000)

    def _timer_change_for_5_secs(self):
        self.timer_value = 5
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
            if self.ActionMenuViewSelectedProcesses.isEnabled():
                self.ActionMenuViewSelectedProcesses.setChecked(True)
        elif self.filterComboBox.currentIndex() == 9:
            self.ActionMenuViewApplicationInLast12Hours.setChecked(True)

        self.refresh_treeview_model()

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
        if self.ActionMenuViewSelectedProcesses.isEnabled():
            self.filterComboBox.setCurrentIndex(8)

    def _filter_by_application_in_last_12_hours(self):
        self.filterComboBox.setCurrentIndex(9)

    def _searchLineEdit_get_focus(self):
        self.searchLineEdit.setFocus()

    def _clear_cpu_history(self):
        self.cpu_widget_graph.clear_history()
        self.cpu_history_dialog.cpu_history_graph.clear_history()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
