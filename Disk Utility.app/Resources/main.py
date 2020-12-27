#!/usr/local/bin/env python3.7

# This Python file uses the following encoding: utf-8
import sys
import os


from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QTreeWidgetItem, QListWidgetItem
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
            # TODO: Add the partitions as children?
            partitions = disks.get_partitions(di["name"])
            if len(partitions) > 0:
                partitions.pop(0)
                for partition in partitions:
                    if partition["name"] == "":
                        continue
                    child = QTreeWidgetItem()
                    child.setText(0, (partition["name"] + " " + partition["partition_type_or_label"]))
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

        self.mountAction = QAction(self)
        self.mountAction.setText("&Mount")
        self.mountAction.setIcon(QIcon.fromTheme('drive-harddisk')) # TODO: Add proper icon

        self.unmountAction = QAction(self)
        self.unmountAction.setText("&Unmount")
        self.unmountAction.setIcon(QIcon.fromTheme('drive-harddisk')) # TODO: Add proper icon

        self.burnAction = QAction(self)
        self.burnAction.setText("&Burn")
        self.burnAction.setIcon(QIcon.fromTheme('drive-optical')) # TODO: Add proper icon

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
    def geomTreeWidgetChanged(self):
        print("geomTreeWidgetChanged")
        pp = pprint.PrettyPrinter(width=41)

        if not hasattr(self.geomTreeWidget.selectedItems()[0], "di"):
            return

        di = getattr(self.geomTreeWidget.selectedItems()[0], "di")

        self.partitionsListWidget.clear()

        self.partitionsListWidget.setStyleSheet("QListWidget::item { text-align: center; margin-left: 2px; margin-right: 2px; margin-top: 2px; border: 2px solid grey }")

        partitions = disks.get_partitions(di["name"])
        self.detailsPlainTextEdit.setPlainText(pp.pformat(di) + "\n\n" + pp.pformat(partitions))
        if len(partitions) > 0:
            partitions.pop(0)
            for partition in partitions:
                if partition["name"] == "":
                    continue
                item = QListWidgetItem(partition["name"] + "\n" + partition["partition_type_or_label"] + " " + partition["human_readable_partition_size"])
                self.partitionsListWidget.addItem(item)


if __name__ == "__main__":
    app = QApplication([])
    widget = Disks()
    widget.show()
    sys.exit(app.exec_())
