#!/usr/bin/env python3

# Hardware Probe
# Copyright (c) 2020-2023, Simon Peter <probono@puredarwin.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QListWidget, QTextBrowser, \
    QWidget, QVBoxLayout, QListWidgetItem, QMessageBox, QInputDialog, QAction, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from functools import partial

class FileViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Set the window title
        with open("/root/HW_PROBE/LATEST/hw.info/host", 'r') as file:
            for line in file:
                if line.startswith("vendor:"):
                    vendor = line.replace("vendor:", "").strip()
                if line.startswith("model:"):
                    model = line.replace("model:", "").strip()
        self.setWindowTitle(vendor + " " + model)

        # Set up the main window
        self.setGeometry(100, 100, 620, 440)

        # Create a splitter to divide the window into two columns
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left column - List of file names
        left_column = QWidget()
        left_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(False)
        left_layout.addWidget(self.file_list)
        left_column.setLayout(left_layout)

        # Set the left column width to 100 pixels and remove padding/border
        left_column.setMaximumWidth(180)
        left_column.setStyleSheet("QListWidget { border: none; padding: 0px; }")
        self.setStyleSheet("QMainWindow { border: none; padding: 0px; }")
        splitter.setStyleSheet("QSplitter { border: none; padding: 0px; }")

        # Right column - Display file content
        self.right_column = QTextBrowser()

        # Set monospaced font with 9pt size for the right column
        font = QFont("Monospace")
        font.setPointSize(8)
        self.right_column.setFont(font)

        # Add both columns to the splitter
        splitter.addWidget(left_column)
        splitter.addWidget(self.right_column)

        # Connect the item selection to display file content
        self.file_list.itemSelectionChanged.connect(lambda: self.display_file_content(self.file_list.currentItem()))

        # Add File menu with Close and Quit items
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction("&Close", self.close, "Ctrl+W")
        self.file_menu.addSeparator()
        self.file_menu.addAction("&Quit", self.close, "Ctrl+Q")

        # Add Edit menu with Cut, Copy, and Paste items;
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction("&Undo", self.right_column.undo, "Ctrl+Z")
        self.edit_menu.addSeparator()
        self.edit_menu.addAction("&Cut", self.right_column.cut, "Ctrl+X")
        self.edit_menu.addAction("&Copy", self.right_column.copy, "Ctrl+C")
        self.edit_menu.addAction("&Paste", self.right_column.paste, "Ctrl+V")
        self.edit_menu.addSeparator()
        self.edit_menu.addAction("&Find", self.find, "Ctrl+F")
        # self.edit_menu.addAction("Find &Next", self.right_column.findNext, "Ctrl+G")
        self.edit_menu.addSeparator()
        self.edit_menu.addAction("&Select All", self.right_column.selectAll, "Ctrl+A")

        # Add Help menu with About item
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction("&About", self.about)

        # Define the files, visible names, and groups
        file_data = {
            "Machine": [
                {"name": "Host", "path": "/root/HW_PROBE/LATEST/hw.info/host"},
                {"name": "CPU", "path": "/root/HW_PROBE/LATEST/hw.info/logs/lscpu"},
                {"name": "Devices", "path": "/root/HW_PROBE/LATEST/hw.info/devices"},
                {"name": "BIOS", "path": "/root/HW_PROBE/LATEST/hw.info/logs/biosdecode"},
                {"name": "DMI", "path": "/root/HW_PROBE/LATEST/hw.info/logs/dmidecode"},
                {"name": "Summary", "path": "/root/HW_PROBE/LATEST/hw.info/logs/neofetch"},
                {"name": "Uptime", "path": "/root/HW_PROBE/LATEST/hw.info/logs/uptime"},
            ],
            "Audio": [
                # {"name": "Mixer", "path": "/root/HW_PROBE/LATEST/hw.info/logs/amixer"},
                # {"name": "Play", "path": "/root/HW_PROBE/LATEST/hw.info/logs/aplay"},
                # {"name": "Record", "path": "/root/HW_PROBE/LATEST/hw.info/logs/arecord"},
                {"name": "Devices", "path": "/root/HW_PROBE/LATEST/hw.info/logs/sndstat"},
            ],
            "Devices": [
                {"name": "Device Information", "path": "/root/HW_PROBE/LATEST/hw.info/logs/devinfo"},
                {"name": "Device Nodes", "path": "/root/HW_PROBE/LATEST/hw.info/logs/dev"},
                {"name": "PCI Devices", "path": "/root/HW_PROBE/LATEST/hw.info/logs/lspci"},
                # {"name": "PCI Devices (All)", "path": "/root/HW_PROBE/LATEST/hw.info/logs/lspci_all"},
                {"name": "PCI Configuration", "path": "/root/HW_PROBE/LATEST/hw.info/logs/pciconf"},
                {"name": "USB Devices", "path": "/root/HW_PROBE/LATEST/hw.info/logs/lsusb"},
                {"name": "USB Configuration", "path": "/root/HW_PROBE/LATEST/hw.info/logs/usbconf"},
                {"name": "I/O Stat", "path": "/root/HW_PROBE/LATEST/hw.info/logs/iostat"},
            ],
            "Graphics": [
                {"name": "Xorg Configuration", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xorg.conf.d"},
                {"name": "GLX Information", "path": "/root/HW_PROBE/LATEST/hw.info/logs/glxinfo"},
                {"name": "X11 Input", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xinput"},
                # {"name": "Xorg Configuration", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xorg.conf"},
                {"name": "Xorg Log", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xorg.log"},
                # {"name": "Xorg Log (1)", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xorg.log.1"},
                {"name": "Screens", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xrandr"},
                {"name": "Xrandr Providers", "path": "/root/HW_PROBE/LATEST/hw.info/logs/xrandr_providers"},
            ],
            "Network": [
                {"name": "Interfaces", "path": "/root/HW_PROBE/LATEST/hw.info/logs/ifconfig"},
            ],
            "Power Management": [
                {"name": "APM", "path": "/root/HW_PROBE/LATEST/hw.info/logs/apm"},
                {"name": "Hardware Stat", "path": "/root/HW_PROBE/LATEST/hw.info/logs/hwstat"},
            ],
            "Storage": [
                {"name": "Block Devices", "path": "/root/HW_PROBE/LATEST/hw.info/logs/lsblk"},
                {"name": "Disk Information", "path": "/root/HW_PROBE/LATEST/hw.info/logs/diskinfo"},
                {"name": "Disk Space", "path": "/root/HW_PROBE/LATEST/hw.info/logs/df"},
                {"name": "Geometry", "path": "/root/HW_PROBE/LATEST/hw.info/logs/geom"},
                {"name": "Partitions", "path": "/root/HW_PROBE/LATEST/hw.info/logs/gpart"},
                {"name": "Partitions List", "path": "/root/HW_PROBE/LATEST/hw.info/logs/gpart_list"},
                {"name": "SMART", "path": "/root/HW_PROBE/LATEST/hw.info/logs/smartctl"},
                # {"name": "CAM subsystem", "path": "/root/HW_PROBE/LATEST/hw.info/logs/camcontrol"},
            ],
            "System": [
                {"name": "FreeBSD Version", "path": "/root/HW_PROBE/LATEST/hw.info/logs/freebsd-version"},
                # {"name": "OS Name", "path": "/root/HW_PROBE/LATEST/hw.info/logs/osname"},
                {"name": "uname", "path": "/root/HW_PROBE/LATEST/hw.info/logs/uname"},
                {"name": "OS Release", "path": "/root/HW_PROBE/LATEST/hw.info/logs/os-release"},
                {"name": "dmesg", "path": "/root/HW_PROBE/LATEST/hw.info/logs/dmesg"},
                {"name": "Kernel Configuration", "path": "/root/HW_PROBE/LATEST/hw.info/logs/config"},
                {"name": "Kernel Modules", "path": "/root/HW_PROBE/LATEST/hw.info/logs/kldstat"},
                # {"name": "Kernel Modules (v)", "path": "/root/HW_PROBE/LATEST/hw.info/logs/kldstat_v"},
                {"name": "Locale", "path": "/root/HW_PROBE/LATEST/hw.info/logs/locale"},
                {"name": "sysctl", "path": "/root/HW_PROBE/LATEST/hw.info/logs/sysctl"},
                {"name": "Processes", "path": "/root/HW_PROBE/LATEST/hw.info/logs/top_head"},
                {"name": "Virtual Memory", "path": "/root/HW_PROBE/LATEST/hw.info/logs/vmstat"},
            ],
            "Software": [
                {"name": "Packages", "path": "/root/HW_PROBE/LATEST/hw.info/logs/pkglist"},
            ]
        }

        # Populate the list with file names and groups
        self.populate_file_list(file_data)

        # Store the file data for later use
        self.file_data = file_data

    def populate_file_list(self, file_data):
        for group, files in file_data.items():
            group_item = QListWidgetItem(group)  # Create a group item
            group_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.file_list.addItem(group_item)

            for file_info in files:
                file_item = QListWidgetItem(file_info["name"])  # Create a file item with the visible name
                file_item.setData(Qt.UserRole, file_info["path"])  # Store the file path as user data
                file_item.setToolTip(file_info["path"])
                self.file_list.addItem(file_item)

    def find(self):
        # Dialog to enter the text to search
        text, ok = QInputDialog.getText(self, "Find", "Text:")
        if ok and text != "":
            self.right_column.find(text)

    def display_file_content(self, item):
        selected_file_path = item.data(Qt.UserRole)  # Retrieve the file path from user data

        if selected_file_path:
            if os.path.isfile(selected_file_path):
                with open(selected_file_path, 'r') as file:
                    file_content = file.read()
                    if not file_content:
                        file_content = "Empty file"
                    self.centralWidget().widget(1).setPlainText(file_content)
            else:
                self.centralWidget().widget(1).setPlainText("File not found: " + selected_file_path)

    def about(self):
        print("showDialog")
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Hardware Probe.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Hardware Probe</h3>")
        msg.setInformativeText("Fontend for <a href='https://github.com/linuxhw/hw-probe'>hw-probe</a><br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

def main():
    app = QApplication(sys.argv)
    file_viewer = FileViewerApp()
    file_viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
