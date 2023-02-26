#!/usr/bin/env python3

"""
Lets the user select a disk to format.
"""

import sys
import gettext
import locale
import os

from PyQt5 import QtCore, QtGui, QtWidgets

import disks

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
# FIXME: Do not import translations from outside of the application bundle
# which currently is difficult because we have all translations for all applications
# in the whole repository in the same .ts files
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "")
def tr(input):
    return tstr.tr(input)


class DiskSelectionWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.user_agreed_to_erase = False
        self.selected_disk = None

        self.old_ds = None  # The disks we have recognized so far
        self.disk_listwidget = QtWidgets.QListWidget()
        self.disk_listwidget.setIconSize(QtCore.QSize(48, 48))
        self.disk_listwidget.itemSelectionChanged.connect(self.onSelectionChanged)
        disk_vlayout = QtWidgets.QVBoxLayout(self)
        disk_vlayout.addWidget(self.disk_listwidget)
        self.label = QtWidgets.QLabel()
        disk_vlayout.addWidget(self.label)
        self.required_mib_on_disk = 0
        self.periodically_list_disks()

        # Add a ButtonBox with an OK button and a Cancel button
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # Cancel button is the default (blue button)
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setDefault(True)
        # button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # Disable the OK button until the user has selected a disk
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        disk_vlayout.addWidget(self.button_box)

        # When user presses escape, close the dialog box
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        self.shortcut.activated.connect(self.reject)

        # When user presses enter, simulate a click on the OK button
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), self)
        self.shortcut.activated.connect(self.accept)
        
        # Start a timer to periodically refresh the list of disks
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.periodically_list_disks)
        self.timer.start(1000)

    def accept(self):
        if self.user_agreed_to_erase == True:
            self.timer.stop()
            self.close()

    def reject(self):
        self.timer.stop()
        self.close()

    def periodically_list_disks(self):
        print("periodically_list_disks")
        self.list_disks()

    def list_disks(self):
        ds = disks.get_disks()
        # Do not refresh the list of disks if nothing has changed, because it de-selects the selection
        if ds != self.old_ds:
            self.disk_listwidget.clear()
            for d in ds:
                di = disks.get_disk(d)
                available_bytes = int(di.get("mediasize").split(" ")[0])
                if (available_bytes >= self.required_mib_on_disk) and di.get("geomname").startswith("cd") == False:
                    title = "%s on %s (%s GiB)" % (di.get("descr"), di.get("geomname"), f"{(available_bytes // (2 ** 30)):,}")
                    if di.get("geomname").startswith("cd") == True:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-optical'), title)
                    elif di.get("geomname").startswith("da") == True:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-removable-media'), title)
                    else:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-harddisk'), title)
                        item.setFlags(QtCore.Qt.ItemIsSelectable)
                    if available_bytes < self.required_mib_on_disk*1024*1024:
                        item.setFlags(QtCore.Qt.ItemIsSelectable)
                    self.disk_listwidget.addItem(item)
            self.old_ds = ds

    def onSelectionChanged(self):
        result = self.show_warning()
        button = self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        if result != None:
            print("User has agreed to erase the disk %s" % result)
            button.setEnabled(True)
        else:
            print("User has not agreed to erase the disk")
            button.setEnabled(False)
            self.disk_listwidget.clearSelection()

    def show_warning(self):
        if len(self.disk_listwidget.selectedItems()) != 1:
            return
        self.user_agreed_to_erase = False
        
        # Make a dialog box to ask the user if they really want to erase the disk
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle(tr("Warning"))
        dialog.setText(tr("This will erase all contents of all partitions\non this disk and format it.\n\nContinue?"))
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.addButton(QtWidgets.QMessageBox.Yes)
        dialog.addButton(QtWidgets.QMessageBox.No)
        dialog.setDefaultButton(QtWidgets.QMessageBox.No)
        result = dialog.exec_()
        if result == QtWidgets.QMessageBox.Yes:
            print("User has agreed to erase the disk")
            self.user_agreed_to_erase = True
            self.selected_disk = self.disk_listwidget.selectedItems()[0].text().split(" ")[-3]
            return self.selected_disk
        else:
            print("User has not agreed to erase the disk")
            self.disk_listwidget.clearSelection()
            self.user_agreed_to_erase = False
            self.selected_disk = None
            return None

if __name__ == "__main__":
    # Wait for the user to click the OK button
    app.exec_()
    w = DiskSelectionWidget()
    w.show()
    # Print the selected disk to stdout
    if w.selected_disk != None:
        print("/dev/%s" % w.selected_disk)
    else:
        print("No disk selected")
        sys.exit(1)

