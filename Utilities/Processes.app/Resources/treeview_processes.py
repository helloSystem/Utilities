#!/usr/bin/env python3

import os
import signal

from PyQt5.QtCore import (
    Qt,
    QItemSelectionModel,
)

from PyQt5.QtWidgets import QAction, QLineEdit, QTreeView, QComboBox


class TreeViewProcess(object):
    actionToolBarQuit_Process: QAction
    actionToolBar_Inspect_Process: QAction
    searchLineEdit: QLineEdit
    process_tree: QTreeView
    ActionMenuViewSelectedProcesses: QAction
    ActionMenuViewInspectProcess: QAction
    filterComboBox: QComboBox
    ActionViewKillDialog: QAction
    ActionMenuViewSendSignaltoProcesses: QAction
    ActionMenuViewSample: QAction
    ActionToolBarQuitProcess: QAction
    ActionMenuViewKillDialog: QAction
    ActionToolBarInspectProcess: QAction
    ActionToolBarSampleProcess: QAction

    def __init__(self):

        self.tree_view_model = None
        self.selected_pid = -1
        self.my_username = os.getlogin()

    def filter_by_line(self, row, text):
        if self.searchLineEdit.text():
            if self.searchLineEdit.text().lower() in text.lower():
                return row
            else:
                return None
        else:
            return row

    def selectClear(self):
        self.selected_pid = None
        self.process_tree.clearSelection()

        self.ActionToolBarQuitProcess.setEnabled(False)
        self.ActionToolBarSampleProcess.setEnabled(False)
        self.ActionToolBarInspectProcess.setEnabled(False)

        if self.filterComboBox.currentIndex() == 8:
            self.filterComboBox.setCurrentIndex(0)
        self.filterComboBox.model().item(8).setEnabled(False)
        self.ActionMenuViewInspectProcess.setEnabled(False)
        self.ActionMenuViewSelectedProcesses.setEnabled(False)
        self.ActionMenuViewSample.setEnabled(False)
        self.ActionMenuViewKillDialog.setEnabled(False)
        self.ActionMenuViewSendSignaltoProcesses.setEnabled(False)

    def selectItem(self, itemOrText):
        # oldIndex = self.process_tree.selectionModel().currentIndex()
        newIndex = None
        try:  # an item is given
            newIndex = self.process_tree.model().indexFromItem(itemOrText)
        except (Exception, BaseException):  # a text is given and we are looking for the first match
            listIndexes = self.process_tree.model().match(
                self.process_tree.model().index(0, 0), Qt.DisplayRole, itemOrText, Qt.MatchStartsWith
            )
            if listIndexes:
                newIndex = listIndexes[0]
        if newIndex:
            self.process_tree.selectionModel().setCurrentIndex(
                newIndex, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
            self.process_tree.selectionModel().select(
                newIndex, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )

    def onClicked(self):
        try:
            self.selected_pid = int(self.tree_view_model.itemData(self.process_tree.selectedIndexes()[0])[0])
            if self.selected_pid:
                self.ActionToolBarQuitProcess.setEnabled(True)
                self.ActionToolBarInspectProcess.setEnabled(True)
                self.ActionToolBarSampleProcess.setEnabled(True)
                self.filterComboBox.model().item(8).setEnabled(True)
                self.ActionMenuViewSendSignaltoProcesses.setEnabled(True)
                self.ActionMenuViewSample.setEnabled(True)
                self.ActionMenuViewSelectedProcesses.setEnabled(True)
                self.ActionMenuViewInspectProcess.setEnabled(True)
                self.ActionMenuViewKillDialog.setEnabled(True)
        except KeyError:
            self.selectClear()

    def killProcess(self):
        if self.selected_pid:
            os.kill(self.selected_pid, signal.SIGKILL)

    def SIGKILLSelectedProcess(self):
        if self.selected_pid:
            try:
                os.kill(self.selected_pid, signal.SIGKILL)
                self.selected_pid = None
                self.process_tree.clearSelection()
                self.refresh()
            except (Exception, BaseException):
                pass

    def SIGQUITSelectedProcess(self):
        if self.selected_pid:
            try:
                os.kill(self.selected_pid, signal.SIGTERM)
                self.selected_pid = None
                self.process_tree.clearSelection()
                self.refresh()
            except (Exception, BaseException):
                pass

    def refresh(self):
        pass
