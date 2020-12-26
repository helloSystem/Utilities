#!/usr/bin/env python3.7

# This Python file uses the following encoding: utf-8
import sys
import os


from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QTreeWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
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
        
        # self._showMenu() # FIXME: Make the global menu work for applications that are running as root
        # https://bugs.launchpad.net/indicator-appmenu/+bug/592842
        
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
        self.detailsPlainTextEdit.setPlainText(pp.pformat(getattr(self.geomTreeWidget.selectedItems()[0], "di")))

    def _showMenu(self):
        exitAct = QAction('&Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.quit)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        aboutAct = QAction('&About', self)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAct)
        
    def _showAbout(self):
        print("showDialog")
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Disk Utility.png"))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Disk Utility</h3>")
        msg.setInformativeText("A simple utility to format and image disks<br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()
        

if __name__ == "__main__":
    app = QApplication([])
    widget = Disks()
    widget.show()
    sys.exit(app.exec_())
