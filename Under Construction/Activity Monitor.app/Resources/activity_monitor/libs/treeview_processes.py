#!/usr/bin/env python3

import os
import signal
import time

import psutil
from PyQt5.QtCore import (
    Qt,
    QSize,
    QItemSelectionModel,
    QItemSelection,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QAbstractItemView,
    QTreeView,
    QSizePolicy,
)
from .utils import bytes2human


class TreeViewProcess(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

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
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout = QGridLayout()
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

        self.process_tree.setModel(self.tree_view_model)

        for pos, title in enumerate(self.header):
            self.process_tree.resizeColumnToContents(pos)

        if self.selected_pid >= 0:
            self.selectItem(str(self.selected_pid))

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