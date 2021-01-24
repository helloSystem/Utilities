#!/usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import os


from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QTreeWidgetItem, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QSize
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtCore import Qt
import pprint

import disks

class Disks(QMainWindow):
    def __init__(self):
        super(Disks, self).__init__()
        
        self.showTODO("Please see https://github.com/helloSystem/hello/issues/61")

        self.load_ui()
        self._createToolBars()
        self.geomTreeWidget.setIconSize(QSize(16, 16))
        self.populate_geom_tree()

    def populate_geom_tree(self):
        ds = disks.get_disks()
        for d in ds:
            di = disks.get_disk(d)
            print(di)
            print(di.get("descr"))
            item = QTreeWidgetItem()
            item.setText(0, di["descr"])
            item.__setattr__("di", di)
            if di.get("geomname").startswith("cd") == True:
                item.setIcon(0, QIcon.fromTheme('drive-optical'))
            elif di.get("geomname").startswith("da") == True:
                item.setIcon(0, QIcon.fromTheme('drive-removable-media'))
            else:
                item.setIcon(0, QIcon.fromTheme('drive-harddisk'))
            self.geomTreeWidget.addTopLevelItem(item)
            # Add the partitions that are on the hardware devices as children
            partitions = disks.get_partitions(di["name"])
            if len(partitions) > 0:
                partitions.pop(0)
                for p in partitions:
                    if p.name == None:
                        continue
                    child = QTreeWidgetItem()
                    child.setText(0, (p.name + " " + p.type_or_label))
                    child.setFlags(Qt.ItemIsSelectable) # Make it greyed out here for now
                    item.addChild(child)
        # In addition to hardware devices, also show ZFS zpools
        # Not entirely sure if this is the best place to do this in the UI,#
        # but zpools are neither strictly a child nor a parent of hardware devices...
        zpools = disks.get_zpools()
        if len(zpools) > 0:
            for zp in zpools:
                item = QTreeWidgetItem()
                item.setText(0, zp.name)
                if zp.health == "ONLINE":
                    item.setIcon(0, QIcon.fromTheme('emblem-colors-green'))
                else:
                    item.setIcon(0, QIcon.fromTheme('emblem-colors-white'))
                self.geomTreeWidget.addTopLevelItem(item)
                # Show the datasets (volumes, snapshots, file systems) on the zpool
                datasets = disks.get_datasets(zp.name)
                for dataset in datasets:
                    child = QTreeWidgetItem()
                    child.setText(0, (dataset))
                    child.setFlags(Qt.ItemIsSelectable) # Make it greyed out here for now
                    item.addChild(child)

    def load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()

    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")

        self.newAction = QAction(self)
        self.newAction.setText("&New Image")
        self.newAction.setIcon(QIcon.fromTheme('document')) # TODO: Add proper icon
        self.newAction.setEnabled(False)

        self.mountAction = QAction(self)
        self.mountAction.setText("&Mount")
        self.mountAction.setIcon(QIcon.fromTheme('drive-harddisk')) # TODO: Add proper icon
        self.mountAction.setEnabled(False)

        self.unmountAction = QAction(self)
        self.unmountAction.setText("&Unmount")
        self.unmountAction.setIcon(QIcon.fromTheme('drive-harddisk')) # TODO: Add proper icon
        self.unmountAction.setEnabled(False)

        self.burnAction = QAction(self)
        self.burnAction.setText("&Burn")
        self.burnAction.setIcon(QIcon.fromTheme('drive-optical')) # TODO: Add proper icon
        self.burnAction.setEnabled(False)

        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.mountAction)
        fileToolBar.addAction(self.unmountAction)
        fileToolBar.addAction(self.burnAction)
        fileToolBar.setMovable(False)
        fileToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    @pyqtSlot()
    def plusButtonClicked(self):
        print("+ button clicked")

    @pyqtSlot()
    def minusButtonClicked(self):
        print("- button clicked")

    @pyqtSlot()
    def optionsButtonClicked(self):
        print("Options button clicked")

    @pyqtSlot()
    def partitionsListWidgetItemClicked(self):
        print("partitionsListWidgetChanged")

        self.mountAction.setEnabled(True)
        self.unmountAction.setEnabled(True)

        self.detailsPlainTextEdit.setPlainText(getattr(self.partitionsListWidget.currentItem(), "partition").__repr__())


    @pyqtSlot()
    def geomTreeWidgetChanged(self):
        print("geomTreeWidgetChanged")

        self.partitionsListWidget.clear()

        self.mountAction.setEnabled(False)
        self.unmountAction.setEnabled(False)

        pp = pprint.PrettyPrinter(width=41)

        # If a physical device was selected
        if hasattr(self.geomTreeWidget.selectedItems()[0], "di"):
            di = getattr(self.geomTreeWidget.selectedItems()[0], "di")
            self.partitionsListWidget.setStyleSheet("QListWidget::item { text-align: center; margin-left: 2px; margin-right: 2px; margin-top: 2px; border: 2px solid grey }")
            partitions = disks.get_partitions(di["name"])
            self.detailsPlainTextEdit.setPlainText(pp.pformat(di) + "\n\n" + pp.pformat(partitions))
            if len(partitions) > 0:
                partitions.pop(0)
                for p in partitions:
                    if p.name == None:
                        continue
                    item = QListWidgetItem(p.name + "\n" + p.type_or_label + " " + p.human_readable_size)
                    item.__setattr__("partition", p)
                    self.partitionsListWidget.addItem(item)

    def showTODO(self, detailed_text=""):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Developer Preview")
        msg.setText("This application is a preview for developers.<br>It is not fully functional yet.")
        msg.setDetailedText("Please see https://github.com/helloSystem/Utilities if you would like to contribute.\n\n" + detailed_text)
        msg.exec() 


if __name__ == "__main__":
    app = QApplication([])
    widget = Disks()
    widget.show()
    sys.exit(app.exec_())
