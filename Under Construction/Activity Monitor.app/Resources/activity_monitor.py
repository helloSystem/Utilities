#!/usr/bin/env python3

import os
import sys

import psutil
from PyQt5.QtCore import (
    QTimer,
    Qt,
    QSize,
    QThread
)
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
    QShortcut,
    QLabel,
    QAction,
    QActionGroup,
    QWidgetAction,
    QMenuBar,
    QComboBox,
    QLineEdit,
)

from activity_monitor.libs.dialog_about import About
from activity_monitor.libs.dialog_kill import Kill
# Load each tab class
from activity_monitor.libs.tab_cpu import TabCpu
from activity_monitor.libs.tab_disk_activity import TabDiskActivity
from activity_monitor.libs.tab_disk_usage import TabDiskUsage
from activity_monitor.libs.tab_network import TabNetwork
from activity_monitor.libs.tab_system_memory import TabSystemMemory
from activity_monitor.libs.treeview_processes import TreeViewProcess

from activity_monitor.libs.dialog_send_signal import SendSignalDialog
# In charge to background long time process
from activity_monitor.libs.worker import PSUtilsWorker

__app_name__ = "Activity Monitor"
__app_version__ = "0.1a"
__app_authors__ = ["Hierosme Alias Tuuux", "Contributors ..."]
__app_description__ = "View CPU, Memory, Network, Disk activities and interact with processes"
__app_url__ = "https://github.com/helloSystem/Utilities"


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.hide()

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

        self.ActionViewColumnProcessID = None
        self.ActionColumnProcessName = None
        self.ActionViewColumnUser = None
        self.ActionViewColumnPercentCPU = None
        self.ActionViewColumnNumThreads = None
        self.ActionViewColumnRealMemory = None
        self.ActionViewColumnVirtualMemory = None

        self.ActionViewKillDialog = None
        self.ActionViewSendSignalDialog = None

        self.setupUi()

        self.timer.timeout.connect(self.refresh)

        self.refresh()

        # Wait a bit for UI stabilisation then send Signals about setting
        # Can be remove when a true setting manager will be implemented
        # THAT IS A TRIVIAL SETTING MANAGER
        QTimer.singleShot(2000, self.restore_settings)

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

        self.process_monitor = TreeViewProcess()
        self.process_monitor.filterComboBox = self.filterComboBox
        self.process_monitor.searchLineEdit = self.searchLineEdit

        # Ping / Pong for ComboBox
        self.searchLineEdit.textChanged.connect(self.process_monitor.refresh)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)

        self._createMenuBar()
        self._createActions()
        self._createToolBars()

        # Pass Action from Menu and ToolBar to the Process Treeview Widget
        self.process_monitor.ActionViewColumnProcessName = self.ActionColumnProcessName
        self.process_monitor.ActionViewColumnUser = self.ActionViewColumnUser
        self.process_monitor.ActionViewColumnPercentCPU = self.ActionViewColumnPercentCPU
        self.process_monitor.ActionViewColumnNumThreads = self.ActionViewColumnNumThreads
        self.process_monitor.ActionViewColumnRealMemory = self.ActionViewColumnRealMemory
        self.process_monitor.ActionViewColumnVirtualMemory = self.ActionViewColumnVirtualMemory

        self.process_monitor.ActionMenuViewSelectedProcesses = self.ActionMenuViewSelectedProcesses
        self.process_monitor.ActionViewKillDialog = self.ActionViewKillDialog
        self.process_monitor.ActionViewSendSignalDialog = self.ActionViewSendSignalDialog

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
        tabs.setMaximumHeight(190)

        tabs.addTab(self.tab_cpu, "CPU")
        tabs.addTab(self.tab_system_memory, "System Memory")
        tabs.addTab(self.tab_disk_activity, "Disk Activity")
        tabs.addTab(self.tab_disk_usage, "Disk Usage")
        tabs.addTab(self.tab_network, "Network")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.process_monitor, 1)
        layout.addWidget(QLabel(), 0)
        layout.addWidget(tabs, 0)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.restore_settings()

    def createThread(self):
        thread = QThread()
        worker = PSUtilsWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # CPU
        worker.updated_cpu_user.connect(self.tab_cpu.set_user)
        worker.updated_cpu_system.connect(self.tab_cpu.set_system)
        worker.updated_cpu_idle.connect(self.tab_cpu.set_idle)
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

        # Disk Activity
        worker.updated_disk_activity_reads_in.connect(self.tab_disk_activity.refresh_reads_in)
        worker.updated_disk_activity_writes_out.connect(self.tab_disk_activity.refresh_writes_out)
        worker.updated_disk_activity_data_read.connect(self.tab_disk_activity.refresh_data_read)
        worker.updated_disk_activity_data_written.connect(self.tab_disk_activity.refresh_data_written)

        # Network
        worker.updated_network_packets_in.connect(self.tab_network.refresh_packets_in)
        worker.updated_network_packets_out.connect(self.tab_network.refresh_packets_out)
        worker.updated_network_data_received.connect(self.tab_network.refresh_data_received)
        worker.updated_network_data_sent.connect(self.tab_network.refresh_data_sent)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def restore_settings(self):
        # Menu docker
        self.ActionViewColumnProcessID.setCheckable(True)
        self.ActionViewColumnProcessID.setEnabled(False)
        self.ActionViewColumnProcessID.setChecked(False)
        self.ActionViewColumnProcessID.setChecked(True)

        self.ActionColumnProcessName.setCheckable(True)
        self.ActionColumnProcessName.setChecked(True)

        self.ActionViewColumnUser.setCheckable(True)
        self.ActionViewColumnUser.setChecked(True)

        self.ActionViewColumnPercentCPU.setCheckable(True)
        self.ActionViewColumnPercentCPU.setChecked(True)

        self.ActionViewColumnNumThreads.setCheckable(True)
        self.ActionViewColumnNumThreads.setChecked(True)

        self.ActionViewColumnRealMemory.setCheckable(True)
        self.ActionViewColumnRealMemory.setChecked(True)

        self.ActionViewColumnVirtualMemory.setCheckable(True)
        self.ActionViewColumnVirtualMemory.setChecked(True)

        # Filter
        self.ActionMenuViewSelectedProcesses.setCheckable(True)
        self.ActionMenuViewSelectedProcesses.setEnabled(False)
        self.ActionMenuViewSelectedProcesses.setChecked(False)
        self.ActionMenuViewSelectedProcesses.setChecked(True)

        self.ActionMenuViewAllProcesses.setChecked(True)

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
        if self.tab_disk_activity:
            self.tab_disk_activity.timer_value = 1

    def _timer_change_for_3_secs(self):
        self.timer.start(3000)
        if self.tab_disk_activity:
            self.tab_disk_activity.timer_value = 3

    def _timer_change_for_5_secs(self):
        self.timer.start(5000)
        if self.tab_disk_activity:
            self.tab_disk_activity.timer_value = 5

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

    def _clear_cpu_history(self):
        self.tab_cpu.widget_graph.clear_history()

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

        # ViewColumns sub menu
        view_columns = viewMenu.addMenu("Columns")

        self.ActionViewColumnProcessID = QAction("Process ID", self)
        self.ActionColumnProcessName = QAction("Process Name", self)
        self.ActionViewColumnUser = QAction("User", self)
        self.ActionViewColumnPercentCPU = QAction("% CPU", self)
        self.ActionViewColumnNumThreads = QAction("# Threads", self)
        self.ActionViewColumnRealMemory = QAction("Real Memory", self)
        self.ActionViewColumnVirtualMemory = QAction("Virtual Memory", self)

        view_columns.addActions([
            self.ActionViewColumnProcessID,
            self.ActionColumnProcessName,
            self.ActionViewColumnUser,
            self.ActionViewColumnPercentCPU,
            self.ActionViewColumnNumThreads,
            self.ActionViewColumnRealMemory,
            self.ActionViewColumnVirtualMemory,
        ])

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

        self.ActionViewKillDialog = QAction("Quit Process", self)
        self.ActionViewKillDialog.triggered.connect(self._showKill)
        self.ActionViewKillDialog.setShortcut("Ctrl+Meta+Q")
        self.ActionViewKillDialog.setEnabled(False)

        self.ActionViewSendSignalDialog = QAction("Send Signal to Processes", self)
        self.ActionViewSendSignalDialog.triggered.connect(self._showSendSignal)
        self.ActionViewSendSignalDialog.setEnabled(False)

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
                self.ActionViewKillDialog,
                self.ActionViewSendSignalDialog,
                viewShowDeltasForProcess,
            ]
        )

        viewMenu.addSeparator()

        viewClearCPUHistory = QAction("Clear CPU History", self)
        viewClearCPUHistory.setShortcut("Ctrl+K")
        viewClearCPUHistory.triggered.connect(self._clear_cpu_history)

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

        ActionMenuWindowCPUUsage = QAction("CPU Usage", self)
        ActionMenuWindowCPUUsage.setShortcut("Ctrl+2")
        ActionMenuWindowCPUUsage.setEnabled(False)

        ActionMenuWindowCPUHistory = QAction("CPU History", self)
        ActionMenuWindowCPUHistory.setShortcut("Ctrl+3")
        ActionMenuWindowCPUHistory.setEnabled(False)

        windowMenu.addActions(
            [ActionMenuWindowActivityMonitor,
             ActionMenuWindowCPUUsage,
             ActionMenuWindowCPUHistory]
        )
        # Show Floating CPU Window sub menu
        window_show_floating_cpu_window_Menu = windowMenu.addMenu("Show Floating CPU Window")
        windowMenu.addMenu(window_show_floating_cpu_window_Menu)

        ActionMenuWindowShowFloatingHorizontally = QAction("Horizontally", self)
        ActionMenuWindowShowFloatingHorizontally.setShortcut("Ctrl+4")
        ActionMenuWindowShowFloatingHorizontally.setCheckable(True)
        ActionMenuWindowShowFloatingHorizontally.setEnabled(False)

        ActionMenuWindowShowFloatingVertically = QAction("Vertically", self)
        ActionMenuWindowShowFloatingVertically.setShortcut("Ctrl+5")
        ActionMenuWindowShowFloatingVertically.setCheckable(True)
        ActionMenuWindowShowFloatingVertically.setEnabled(False)

        ActionMenuWindowShowFloatingDoNotShow = QAction("Do not show", self)
        ActionMenuWindowShowFloatingDoNotShow.setCheckable(True)

        show_floating_group = QActionGroup(self)
        show_floating_group.addAction(ActionMenuWindowShowFloatingHorizontally)
        show_floating_group.addAction(ActionMenuWindowShowFloatingVertically)
        show_floating_group.addAction(ActionMenuWindowShowFloatingDoNotShow)

        window_show_floating_cpu_window_Menu.addActions([
            ActionMenuWindowShowFloatingHorizontally,
            ActionMenuWindowShowFloatingVertically,
            ActionMenuWindowShowFloatingDoNotShow

        ])
        ActionMenuWindowShowFloatingDoNotShow.setChecked(True)

        windowMenu.addSeparator()

        viewBringAllToFront = QAction("Bring All to Front", self)
        viewBringAllToFront.triggered.connect(self._bring_to_front)
        windowMenu.addAction(viewBringAllToFront)

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
        self.kill_process_action.triggered.connect(self._showKill)
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

    def _bring_to_front(self):
        self.showMinimized()
        self.setWindowState(self.windowState() and (not Qt.WindowMinimized or Qt.WindowActive))

    def _showSendSignal(self):
        self.send_signal_dialog = SendSignalDialog(process=psutil.Process(self.process_monitor.selected_pid))
        self.send_signal_dialog.exec()

    def _showKill(self):
        self.kill = Kill(
            title="Are you sure you want to quit this process ?",
            text="Do you really want to quit '%s'?" % psutil.Process(self.process_monitor.selected_pid).name(),
            size=(450, 155),
            icon=QPixmap(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "Processes.png",
                )
            ).scaledToWidth(76, Qt.SmoothTransformation)
        )

        self.kill.process_signal_quit.connect(self.process_monitor.SIGQUITSelectedProcess)
        self.kill.process_signal_kill.connect(self.process_monitor.SIGKILLSelectedProcess)

        self.kill.show()

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
