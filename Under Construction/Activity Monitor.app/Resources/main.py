#!/usr/bin/env python3

import sys
from PyQt5.QtCore import Qt, QTimer
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


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
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

    def setupCustomUi(self):
        self.setupCustomUiGroups()
        self.setupCustomUiToolBar()

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

    def refresh(self):
        pass

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
