#!/usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import os
import re
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QFile, pyqtSlot, QObject, QProcess, QStorageInfo
from PyQt5.uic import loadUi

import filesystems # bundled
import disks # bundled

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
# FIXME: Do not import translations from outside of the appliction bundle
# which currently is difficult because we have all translations for all applications
# in the whole repository in the same .ts files
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "formatdisk")
def tr(input):
    return tstr.tr(input)


class User(object):

    def __init__(self, line_from_passwd_file):
        parts = line_from_passwd_file.split(":")
        self.username = parts[0]
        self.password = parts[1]
        self.uid = parts[2]
        self.gid = parts[3]
        self.info = parts[4] # The comment field. It allows you to add extra information about the user such as full name, phone number etc. This field use by finger command.
        self.home = parts[5]
        self.shell = parts[6]

    def __repr__(self):
        return "User %s" % self.username

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        if len(sys.argv) < 2:
            print("Usage: %s <device node>" % sys.argv[0])
            exit(1)
        self.device = sys.argv[1]
        self.readable_capacity = None
        self.readable_descr = None
        if "p" in self.device:
            self.is_partition = True
            self.get_partition_details()
        else:
            self.is_partition = False
            self.get_geom_details()
        self.load_ui()

    def load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "formatdisk.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()
        self.statusBar().hide()
        self.setWindowModality(Qt.ApplicationModal)
        self.buttonBox.button(QDialogButtonBox.Ok).setText(tr("Erase"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(tr("Cancel"))

        if self.is_partition == True:
            self.scheme.hide()
            self.schemeLabel.hide()

        # Prepare spinner using an animated GIF
        self.spinner.hide()
        self.movie = QMovie("small_spinner.gif") # Generated using http://ajaxload.info/
        self.spinner.setMovie(self.movie)
        self.movie.start()

        # Translate the widgets in the UI objects that were just loaded from the .ui file
        self.setWindowTitle(tr(self.windowTitle()))
        for e in self.findChildren(QObject, None, Qt.FindChildrenRecursively):
            if hasattr(e, 'text') and hasattr(e, 'setText'):
                e.setText(tr(e.text()))

        # Populate details in the messages
        self.headlineLabel.setText(self.headlineLabel.text().replace("%2", self.readable_capacity))
        self.headlineLabel.setText(self.headlineLabel.text().replace("%1", self.readable_descr))
        self.detailsLabel.setText(self.detailsLabel.text().replace("%1", self.readable_descr))

        self._showMenu()

        # Populate formats
        # TODO: Only add ExFAT if mount.exfat is on the PATH and format_command[0] is also on the PATH,
        # similar for NTFS and ext2
        fsystems = [filesystems.ufs2(self.device), filesystems.fat32(self.device), filesystems.fat16(self.device),
                    filesystems.ntfs(self.device), filesystems.exfat(self.device), filesystems.ext2(self.device)]
        self.formatComboBox.clear()
        for fs in fsystems:
            self.formatComboBox.addItem(fs.nice_name, fs)

        # Populate schemes
        self.schemeComboBox.clear()
        self.schemeComboBox.addItem(tr("GUID Partition Map"), "GPT")
        self.schemeComboBox.addItem(tr("Master Boot Record"), "MBR")


    def get_geom_details(self):
        # Find out which unpartitioned disk we are working on
        # We could also use get_disk() from disks.py but that one does not give us the readable capacity (yet)
        p = QProcess()
        p.setProgram("geom")
        p.setArguments(["disk", "list", self.device.replace("/dev/", "")])
        p.start()
        p.waitForFinished()

        err = p.readAllStandardError().data().decode()
        if err:
            self.fatalError(err)

        out = p.readAllStandardOutput().data().decode()
        if out:
            lines = out.split("\n")
            for line in lines:
                if not ":" in line:
                    continue
                parts = line.split(":")
                key = parts[0].strip()
                val = ":".join(parts[1:len(parts)]).strip()
                if key == "descr":
                    self.readable_descr = val
                    print(self.readable_descr)
                if key == "Mediasize":
                    regex = r"\((.+)\)"
                    matches = re.findall(regex, val)
                    self.readable_capacity = matches[0]
                    print(self.readable_capacity)

    def get_partition_details(self):
        our_partition = None
        partitions = disks.get_partitions(self.device.split("p")[0])
        for partition in partitions:
            if not partition.name:
                # What are these even? Blank unused spaces?
                continue
            # FIXME: What is the difference between daXs1 and daXp1? This distinction is lost on Linux users...
            # Things like this make FreeBSD look "complicated"
            if partition.name == self.device.replace("/dev/", ""):
                our_partition = partition
                print(partition)

        self.readable_descr = our_partition.get_volume_label()

        self.readable_capacity = our_partition.human_readable_size.replace("(", "").replace(")", "")
        print(self.readable_capacity)

    @pyqtSlot()
    def onCancelled(self):
        print("Cancel button clicked")
        sys.exit(0)

    @pyqtSlot()
    def okButtonClicked(self):
        print("OK button clicked")

        # Make all widgets unclickable
        for e in self.findChildren(QObject, None, Qt.FindChildrenRecursively):
            if hasattr(e, 'setDisabled'):
                e.setDisabled(True)

        fs = self.formatComboBox.itemData(self.formatComboBox.currentIndex())
        if self.nameLineEdit.text():
            fs.volume_label = self.nameLineEdit.text()
        print("Name: %s" % fs.volume_label)
        print("Format: %s" % fs.nice_name)
        # print(fs.create_command)
        # print(fs.modify_command)
        # print(fs.format_command)
        scheme = self.schemeComboBox.itemData(self.schemeComboBox.currentIndex())
        print("Scheme: %s" % scheme)
        self.spinner.show()

        # Unmount the necessary devices
        # FIXME: This fails for FUSE-mounted devices, as their device is /dev/fuse...
        # How can we find out that e.g., /dev/da0s1 has been mounted with FUSE ExFAT
        # to /media/exfat so that we can unmount that?
        # 'mount' does not show any mention of /dev/da0s1 at all!
        # /dev/fuse on /media/exfat (fusefs)
        vols = QStorageInfo.mountedVolumes()
        for vol in vols:
            candidate = vol.device().data().decode()
            if self.device == candidate:
                self.runCommandAsRootAndAbortOnError(["umount", self.device])
            # Not just unmount the device itself but also the devices for its partitions
            if candidate.startswith(self.device + "p"):
                self.runCommandAsRootAndAbortOnError(["umount", candidate])

        if self.overwriteCheckBox.isChecked():
            self.runCommandAsRootAndAbortOnError = ["dd", "if=/dev/zero", "of=" + self.device, "bs=8M"]

        if self.is_partition == False:
            # Clean out any pre-existing partition table in a robust way
            cmd = ["dd", "if=/dev/zero", "of="+self.device, "bs=1M", "count=1"]
            self.runCommandAsRootAndAbortOnError(cmd)
            # Create a new partition table
            cmd = ["/sbin/gpart", "create", "-s", scheme, self.device.replace("/dev/", "")]
            self.runCommandAsRootAndAbortOnError(cmd)

        if self.is_partition == False:
            cmd = fs.add_command
            # fs.device = fs.device + "p0" # We have created a partition, so use it # FIXME: What is correct to do here?
        else:
            cmd = fs.modify_command
        self.runCommandAsRootAndAbortOnError(cmd)

        cmd = fs.format_command
        self.runCommandAsRootAndAbortOnError(cmd)

        self.runCommandAsRootAndAbortOnError(["/usr/local/sbin/automount", fs.device.replace("/dev/", ""), "attach"])

        sys.exit(0)

    def runCommandAsRootAndAbortOnError(self, command=["ls"]):
        p = QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E"] + command)
        print("Running: 'sudo' '" + "' '".join(p.arguments()) +"'")
        # p.finished.connect(self.onProcessFinished)
        p.start()

        # Important trick so that the app stays responsive without the need for threading!
        if p.waitForStarted(-1):
            while p.state() == 2:
                QApplication.processEvents()
                time.sleep(0.1)

        out = p.readAllStandardOutput().data().decode()
        if out:
            print(out)

        if p.exitStatus() != 0:
            err = p.readAllStandardError().data().decode()
            if err:
                self.fatalError(err)

    def fatalError(self, errorstring, title=tr("Error")):
        print("Error: %s" % errorstring)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(errorstring)
        # msg.setInformativeText('More information')
        msg.setWindowTitle(title)
        self.hide()
        msg.exec_()
        sys.exit(1)

    def _showMenu(self):
        exit_act = QAction('&Quit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(QApplication.quit)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_act)
        about_act = QAction('&About', self)
        about_act.setStatusTip('About this application')
        about_act.triggered.connect(self._showAbout)
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_act)

    def _showAbout(self):
        print("showDialog")
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Format Disk.png"))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Format Disk</h3>")
        msg.setInformativeText(
            "A simple utility to format volumes using <a href='https://www.freebsd.org/cgi/man.cgi?query=gpart&sektion=8'>gpart</a><br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()


if __name__ == "__main__":
    app = QApplication([])
    widget = Window()
    widget.show()

    # Handle Python exceptions in the GUI; https://stackoverflow.com/a/47275100
    # TODO: Make a class out of this that is consumed by all of our applications?
    def my_exception_hook(exctype, value, traceback):
        sys._excepthook(exctype, value, traceback) # Run the original exception hook for the text console
        widget.fatalError(str(value)) # Show simplified error message in the GUI
        sys.exit(1) # widget.fatalError does this anyway, so in this case this is redundant
    # Back up the reference to the exception hook, because we call it from our one
    sys._excepthook = sys.excepthook
    # Install our exception hook as the active one
    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
