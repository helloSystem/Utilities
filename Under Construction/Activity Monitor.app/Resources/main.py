#!/usr/bin/env python3

import sys
import psutil
import time
import os

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

# Back end libs
from widget_chartpie import ChartPieItem
from worker import PSUtilsWorker
from worker_cpu import CPUWorker
from worker_system_memory import SystemMemoryWorker
from worker_icons_cache import IconsCacheWorker

from utility_bytes2human import bytes2human
from utility_application_name import get_application_name


class Window(QMainWindow, Ui_MainWindow, TabCpu, TabSystemMemory,
             TabDiskActivity, TabDiskUsage, TabNetwork, TreeViewProcess):
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

        self.setupUi(self)
        self.setupCustomUi()

        self.timer = QTimer()
        self._timer_change_for_5_secs()

        self.connectSignalsSlots()

        self.setupInitialState()

        self.refresh()
        for header_pos in range(len(self.process_tree.header())):
            self.process_tree.resizeColumnToContents(header_pos)

    def setupCustomUi(self):
        self.setupCustomUiGroups()
        self.setupCustomUiToolBar()

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

        self.system_memory_chart_pie.addItems([
            self.chart_pie_item_memory_free,
            self.chart_pie_item_memory_wired,
            self.chart_pie_item_memory_active,
            self.chart_pie_item_memory_inactive,
        ])

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
        self.system_memory_total_value.setText("%s" % bytes2human(virtual_memory.total))

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
        self.ActionMenuViewKillDialog.triggered.connect(self._showKillDialog)
        self.ActionToolBarQuitProcess.triggered.connect(self._showKillDialog)
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)

        # Tab CPU
        self.data_idle_changed.connect(self.refresh_idle)
        self.data_user_changed.connect(self.refresh_user)
        self.data_system_changed.connect(self.refresh_system)
        self.data_nice_changed.connect(self.refresh_nice)
        self.data_irq_changed.connect(self.refresh_irq)

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

        # Tab Disk Usage
        self.combobox_devices.currentIndexChanged.connect(self.combobox_index_changed)
        self.mounted_disk_partitions_changed.connect(self.combobox_refresh)
        self.color_button_space_free.colorChanged.connect(self.refresh_color_space_free)
        self.color_button_space_utilized.colorChanged.connect(self.refresh_color_space_utilized)

        # TreeView
        self.process_tree.clicked.connect(self.onClicked)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self._escape_pressed)

    def createPSUtilsThread(self):
        thread = QThread()
        worker = PSUtilsWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

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

    def createCPUThread(self):
        thread = QThread()
        worker = CPUWorker()
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

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # self.threadpool.start(worker)
        return thread

    def createSystemMemoryThread(self):
        thread = QThread()
        worker = SystemMemoryWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # System Memory
        worker.updated_system_memory_available.connect(self.refresh_available)
        worker.updated_system_memory_used.connect(self.refresh_used)
        worker.updated_system_memory_free.connect(self.refresh_free)
        worker.updated_system_memory_active.connect(self.refresh_active)
        worker.updated_system_memory_inactive.connect(self.refresh_inactive)
        worker.updated_system_memory_buffers.connect(self.refresh_buffers)
        worker.updated_system_memory_cached.connect(self.refresh_cached)
        worker.updated_system_memory_shared.connect(self.refresh_shared)
        worker.updated_system_memory_slab.connect(self.refresh_slab)
        worker.updated_system_memory_wired.connect(self.refresh_wired)

        # System Memory Chart Pie
        worker.updated_system_memory_free_raw.connect(self.refresh_free_raw)
        worker.updated_system_memory_wired_raw.connect(self.refresh_wired_raw)
        worker.updated_system_memory_active_raw.connect(self.refresh_active_raw)
        worker.updated_system_memory_inactive_raw.connect(self.refresh_inactive_raw)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh(self):
        self.refresh_treeview_model()

        self.threads.clear()
        self.threads = [
            self.createSystemMemoryThread(),
            self.createCPUThread(),
            self.createPSUtilsThread(),
            self.createIconsCacheThread()
        ]
        for thread in self.threads:
            thread.start()

    def refresh_treeview_model(self):

        self.tree_view_model = QStandardItemModel()
        for p in psutil.process_iter():
            QApplication.processEvents()

            with p.oneshot():
                try:
                    environ = p.environ()
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    environ = None
                application_name = get_application_name(p)

                row = []
                # PID can't be disabled because it is use for selection tracking
                item = QStandardItem(f"{p.pid}")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                row.append(item)

                if self.ActionViewColumnProcessName.isChecked():
                    item = QStandardItem()
                    if application_name in self.__icons:
                        item.setIcon(self.__icons[application_name])
                    item.setText(application_name)
                    row.append(item)

                if self.ActionViewColumnUser.isChecked():
                    item = QStandardItem(f"{p.username()}")
                    row.append(item)

                if self.ActionViewColumnPercentCPU.isChecked():
                    item = QStandardItem(f"{p.cpu_percent()}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)

                if self.ActionViewColumnNumThreads.isChecked():
                    item = QStandardItem(f"{p.num_threads()}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)

                if self.ActionViewColumnRealMemory.isChecked():
                    item = QStandardItem(f"{bytes2human(p.memory_info().rss)}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)

                if self.ActionViewColumnVirtualMemory.isChecked():
                    item = QStandardItem(f"{bytes2human(p.memory_info().vms)}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)

                filtered_row = self.apply_searchline_filter(application_name, row)
                filtered_row = self.apply_combobox_filter(application_name, environ, filtered_row, p)

                # If a after filters it still have something then ad it to the model
                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)

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

        # Impose the Model to TreeView Processes
        self.process_tree.setModel(self.tree_view_model)


        # Restore the selection
        if self.selected_pid and self.selected_pid >= 0:
            self.selectItem(str(self.selected_pid))

    def apply_searchline_filter(self, application_name, row):
        # Filter Line
        filtered_row = None
        if self.searchLineEdit.text():
            if self.searchLineEdit.text().lower() in application_name.lower():
                filtered_row = row
        else:
            filtered_row = row
        return filtered_row

    def apply_combobox_filter(self, application_name, environ, filtered_row, p):
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
        if self.filterComboBox.currentIndex() == 0:
            pass
        elif self.filterComboBox.currentIndex() == 1:
            pass
        elif self.filterComboBox.currentIndex() == 2:
            if p.username() == self.my_username:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 3:
            if p.uids().real < 1000:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 4:
            if p.username() != self.my_username:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 5:
            if p.status() == psutil.STATUS_RUNNING:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 6:
            if p.status() == psutil.STATUS_WAITING or p.status() == psutil.STATUS_SLEEPING:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 7:
            if environ and "LAUNCHED_BUNDLE" in environ:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 8:
            if p.pid == self.selected_pid:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        elif self.filterComboBox.currentIndex() == 9:
            if (time.time() - p.create_time()) % 60 <= 43200:
                filtered_row = self.filter_by_line(filtered_row, application_name)
            else:
                filtered_row = None
        return filtered_row

    def _refresh_icons_cache(self, application_icons):
        for application_name, icon in application_icons.items():
            if application_name not in self.__icons:
                self.__icons[application_name] = icon

    def _showInspectProcessDialog(self):
        if self.ActionMenuViewInspectProcess.isEnabled():
            self.inspect_process_dialog = InspectProcess(process=psutil.Process(self.selected_pid))
            self.inspect_process_dialog.run()
            self.inspect_process_dialog.show()

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

    def _showAboutDialog(self):
        self.AboutDialog = AboutDialog()
        self.AboutDialog.show()

    def _escape_pressed(self):
        if self.process_tree.hasFocus():
            self.selectClear()
        if self.searchLineEdit.hasFocus():
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
        self.widget_graph.clear_history()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
