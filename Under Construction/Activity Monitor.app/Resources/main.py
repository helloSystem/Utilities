#!/usr/bin/env python3

import sys
from PyQt5.QtCore import Qt, QTimer, QThread
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

)
from ui import Ui_MainWindow
from libs import PSUtilsWorker
from libs import TabCpu


class Window(QMainWindow, Ui_MainWindow, TabCpu):
    def __init__(self, parent=None):
        super().__init__(parent)
        TabCpu.__init__(self)
        # Worker
        self.threads = []

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

        self.setupUi(self)
        self.setupCustomUi()

        self.timer = QTimer()
        self._timer_change_for_5_secs()

        self.connectSignalsSlots()
        self.setupCustomUiColorPicker()

    def setupCustomUi(self):
        self.setupCustomUiGroups()
        self.setupCustomUiToolBar()

    def setupCustomUiColorPicker(self):
        self.color_picker_user_value.setColor("green")
        self.color_picker_system_value.setColor("red")
        self.color_picker_nice_value.setColor("blue")
        self.color_picker_irq_value.setColor("orange")
        self.color_picker_idle_value.setColor("black")

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

        self.ActionUpdateFrequencyTo5Secs.triggered.connect(self._timer_change_for_5_secs)
        self.ActionUpdateFrequencyTo3Secs.triggered.connect(self._timer_change_for_3_secs)
        self.ActionUpdateFrequencyTo1Sec.triggered.connect(self._timer_change_for_1_sec)

        # self.searchLineEdit.textChanged.connect(self.process_monitor.refresh)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)

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

    def createThread(self):
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

        # System MEmory
        # worker.updated_system_memory_total.connect(self.tab_system_memory.refresh_total)
        # worker.updated_system_memory_available.connect(self.tab_system_memory.refresh_available)
        # worker.updated_system_memory_used.connect(self.tab_system_memory.refresh_used)
        # worker.updated_system_memory_free.connect(self.tab_system_memory.refresh_free)
        # worker.updated_system_memory_active.connect(self.tab_system_memory.refresh_active)
        # worker.updated_system_memory_inactive.connect(self.tab_system_memory.refresh_inactive)
        # worker.updated_system_memory_buffers.connect(self.tab_system_memory.refresh_buffers)
        # worker.updated_system_memory_cached.connect(self.tab_system_memory.refresh_cached)
        # worker.updated_system_memory_shared.connect(self.tab_system_memory.refresh_shared)
        # worker.updated_system_memory_slab.connect(self.tab_system_memory.refresh_slab)
        # worker.updated_system_memory_wired.connect(self.tab_system_memory.refresh_wired)

        # System Memory Chart Pie
        # worker.updated_system_memory_free_raw.connect(self.tab_system_memory.refresh_free_raw)
        # worker.updated_system_memory_wired_raw.connect(self.tab_system_memory.refresh_wired_raw)
        # worker.updated_system_memory_active_raw.connect(self.tab_system_memory.refresh_active_raw)
        # worker.updated_system_memory_inactive_raw.connect(self.tab_system_memory.refresh_inactive_raw)

        # Disk Usage
        # worker.updated_mounted_disk_partitions.connect(self.tab_disk_usage.setMoutedDiskPartitions)

        # Disk Activity
        # worker.updated_disk_activity_reads_in.connect(self.tab_disk_activity.refresh_reads_in)
        # worker.updated_disk_activity_writes_out.connect(self.tab_disk_activity.refresh_writes_out)
        # worker.updated_disk_activity_data_read.connect(self.tab_disk_activity.refresh_data_read)
        # worker.updated_disk_activity_data_written.connect(self.tab_disk_activity.refresh_data_written)

        # Network
        # worker.updated_network_packets_in.connect(self.tab_network.refresh_packets_in)
        # worker.updated_network_packets_out.connect(self.tab_network.refresh_packets_out)
        # worker.updated_network_data_received.connect(self.tab_network.refresh_data_received)
        # worker.updated_network_data_sent.connect(self.tab_network.refresh_data_sent)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh(self):
        # self.process_monitor.refresh()

        self.threads.clear()
        self.threads = [self.createThread()]
        for thread in self.threads:
            thread.start()

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

        # self.process_monitor.refresh()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
