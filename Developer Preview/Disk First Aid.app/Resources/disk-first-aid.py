#!/usr/bin/env python3
# Unfortunately python3 does not seem to work on FreeBSD

# Disk First Aid
# Copyright (c) 2020-2021, Simon Peter <probono@puredarwin.org>
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

# Dirsk First Aid icon
# https://www.a2591.com/2008/11/container-icons.html
# Copyright (c) 2008, Antrepo
# License: "It is freeware. Download it, share it, use it!"

import sys, os, re, socket
import shutil
from datetime import datetime
import urllib.request, json
from PyQt5 import QtWidgets, QtGui, QtCore # pkg install py37-qt5-widgets
import disks # Privately bundled file

import ssl

# Since we are running the wizard on Live systems which more likely than not may have
# the clock wrong, we cannot verify SSL certificates. Setting the following allows
# content to be fetched from https locations even if the SSL certification cannot be verified.
# This is needed, e.g., for geolocation.
ssl._create_default_https_context = ssl._create_unverified_context

# Plenty of TODOs and FIXMEs are sprinkled across this code.
# These are invitations for new contributors to implement or comment on how to best implement.
# These things are not necessarily hard, just no one had the time to do them so far.
# TODO: Make translatable


#############################################################################
# Helper functions
#############################################################################

def internetCheckConnected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


#############################################################################
# Initialization
# https://doc.qt.io/qt-5/qwizard.html
#############################################################################

class FirstAidWizard(QtWidgets.QWizard, object):
    def __init__(self):

        super().__init__()
    
        self.showTODO("Actual functionality has not been implemented yet. See https://github.com/helloSystem/hello/issues/90")

        print("Preparing wizard")

        self.selected_disk_device = None
        self.should_show_last_page = False
        self.error_message_nice = "An unknown error occured."

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(os.path.dirname(__file__) + '/background.png'))

        self.setWindowTitle("Disk First Aid")
        self.setFixedSize(600, 400)

    def showErrorPage(self, message):
        print("Show error page")
        self.addPage(ErrorPage())
        # It is not possible jo directly jump to the last page from here, so we need to take a workaround
        self.should_show_last_page = True
        self.error_message_nice = message
        self.next()

    # When we are about to go to the next page, we need to check whether we have to show the error page instead
    def nextId(self):
        if self.should_show_last_page == True:
            return max(wizard.pageIds())
        else:
            return self.currentId() + 1

    def showTODO(self, detailed_text=""):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Developer Preview")
        msg.setText("This application is a preview for developers.<br>It is not fully functional yet.")
        msg.setDetailedText("Please see https://github.com/helloSystem/Utilities if you would like to contribute.\n\n" + detailed_text)
        msg.exec()    
        
        
#############################################################################
# Destination disk
#############################################################################

class DiskPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing DiskPage")
        super().__init__()

        self.timer = QtCore.QTimer() # Used to periodically check the available disks
        self.old_ds = None # The disks we have recognized so far
        self.setTitle('Select Disk')
        self.setSubTitle('Please select the disk that should be checked, recovered, or repaired.')
        self.disk_listwidget = QtWidgets.QListWidget()
        self.disk_listwidget.setIconSize(QtCore.QSize(48, 48))
        self.disk_listwidget.itemSelectionChanged.connect(self.onSelectionChanged)
        disk_vlayout = QtWidgets.QVBoxLayout(self)
        disk_vlayout.addWidget(self.disk_listwidget)
        self.label = QtWidgets.QLabel()
        disk_vlayout.addWidget(self.label)

    def initializePage(self):
        print("Displaying DiskPage")

        self.disk_listwidget.clearSelection() # If the user clicked back and forth, start with nothing selected
        self.periodically_list_disks()

    def cleanupPage(self):
        print("Leaving DiskPage")

    def periodically_list_disks(self):
        print("periodically_list_disks")
        self.list_disks()

        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.list_disks)
        self.timer.start()

    def list_disks(self):

        ds = disks.get_disks()
        # Do not refresh the list of disks if nothing has changed, because it de-selects the selection
        if ds != self.old_ds:
            self.disk_listwidget.clear()
            for d in ds:
                di = disks.get_disk(d)
                # print(di)
                # print(di.get("descr"))
                # print(di.keys())
                available_bytes = int(di.get("mediasize").split(" ")[0])
                if di.get("geomname").startswith("cd") == False:
                    # item.setTextAlignment()
                    title = "%s on %s (%s GiB)" % (di.get("descr"), di.get("geomname"), f"{(available_bytes // (2 ** 30)):,}")
                    if di.get("geomname").startswith("cd") == True:
                        # TODO: Add burning powers
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-optical'), title)
                    elif di.get("geomname").startswith("da") == True:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-removable-media'), title)
                    else:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme('drive-harddisk'), title)
                    self.disk_listwidget.addItem(item)
            self.old_ds = ds

    def onSelectionChanged(self):
        # self.isComplete() # Calling it like this does not make its result get used
        self.completeChanged.emit()  # But like this isComplete() gets called and its result gets used
        # wizard.user_agreed_to_erase = False
        # self.show_warning()

    def show_warning(self):
        # After we remove the selection, do not call this again
        if len(self.disk_listwidget.selectedItems()) != 1:
            return
        wizard.user_agreed_to_erase = False
        reply = QtWidgets.QMessageBox.warning(
            wizard,
            "Warning",
            "This will erase all contents of this disk and install the live system on it. Continue?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            print("User has agreed to erase all contents of this disk")
            wizard.user_agreed_to_erase = True
        else:
            self.disk_listwidget.clearSelection()
            pass
        # self.isComplete() # Calling it like this does not make its result get used
        self.completeChanged.emit() # But like this isComplete() gets called and its result gets used

    def isComplete(self):
        ds = disks.get_disks()
        # Given a clear text label, get back the rdX
        # TODO: Use __setattr__() and __getattribute__() instead; see above for an example on how to use those
        for d in self.old_ds:
            di = disks.get_disk(d)
            searchstring = " on " + str(di.get("geomname")) + " "
            print(searchstring)
            if len(self.disk_listwidget.selectedItems()) < 1:
                return False
            if searchstring in self.disk_listwidget.selectedItems()[0].text():
                wizard.selected_disk_device = str(di.get("geomname"))
                self.timer.stop() # FIXME: This does not belong here, but cleanupPage() gets called only
                # if the user goes back, not when they go forward...
                return True

        selected_disk_device = None
        return False

    def cleanupPage(self):
        self.timer.stop()

#############################################################################
# Work page
#############################################################################

class WorkPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing WorkPage")
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        self.command_label = QtWidgets.QLabel(self)
        self.layout.addWidget(self.command_label)

        self.button = QtWidgets.QPushButton(self)
        self.button.setText("Do it")
        self.layout.addWidget(self.button)

        self.output_label = QtWidgets.QLabel()
        self.output_label.setWordWrap(True)
        self.output_layout = QtWidgets.QVBoxLayout(self)
        self.output_label.setText("...")

        font = wizard.font()
        font.setFamily("monospace")
        self.command_label.setFont(font)
        font.setPointSize(8)
        self.output_label.setFont(font)
        self.output_box = QtWidgets.QScrollArea()
        self.output_box.setWidget(self.output_label)

        self.output_layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_box , True) # True = add stretch vertically


    def initializePage(self):
        print("Displaying WorkPage")
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch])
        self.setTitle('Working')
        self.setSubTitle('A short description what this is doing.')

        self.layout = QtWidgets.QVBoxLayout(self)

        self.save_loc = '/dev/' + wizard.selected_disk_device
        import glob
        partitions = glob.glob(self.save_loc + "*")

        self.command = 'ls'
        self.args = partitions

        self.command_label.setText(self.command + " " + " ".join(self.args))
        self.button.clicked.connect(self.run)

    def run(self):
        print("Running command")
        self.process = QtCore.QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.stateChanged.connect(self.handle_state)
        self.process.finished.connect(self.cleanup)
        self.process.setProgram(self.command)
        self.process.setArguments(self.args)
        print(self.command, self.args)

        self.process.start(self.command, self.args)

        #try:
        #    self.process.start(self.command, self.args)
        #except:
        #    wizard.showErrorPage("Could not run '%s' command." % self.command)
        #    return
        self.process.waitForFinished()

    def handle_stdout(self):
        print("handle_stdout")

    def handle_stderr(self):
        print("handle_stderr")

    def handle_state(self):
        print("handle_state")

    def cleanup(self):
        print("cleanup")

#############################################################################
# Success page
#############################################################################

class SuccessPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing SuccessPage")
        super().__init__()
        self.timer = QtCore.QTimer()  # Used to periodically check the available disks

    def initializePage(self):
        print("Displaying SuccessPage")
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

        self.setTitle('Complete')
        self.setSubTitle('The process has completed.')

        logo_pixmap = QtGui.QPixmap(os.path.dirname(__file__) + '/check.svg').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget =  QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(center_widget, True) # True = add stretch vertically

        label = QtWidgets.QLabel()
        label.setText("You can now close this window.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setButtonText(wizard.CancelButton, "Quit")
        wizard.setButtonLayout([QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

        self.periodically_list_disks()

    def periodically_list_disks(self):
        print("periodically_list_disks")
        self.list_disks()

        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.list_disks)
        self.timer.start()

    def list_disks(self):
        ds = disks.get_disks()
        if "/dev/" + wizard.selected_disk_device not in ds:
            print("Device was unplugged, exiting")
            self.timer.stop()
            sys.exit(0)

#############################################################################
# Error page
#############################################################################

class ErrorPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing ErrorPage")
        super().__init__()

        self.setTitle('Error')
        self.setSubTitle('The operation could not be performed.')

        logo_pixmap = QtGui.QPixmap(os.path.dirname(__file__) + '/cross.png').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget =  QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(center_widget, True) # True = add stretch vertically

        self.label = QtWidgets.QLabel()  # Putting it in initializePage would add another one each time the page is displayed when going back and forth
        self.layout.addWidget(self.label)

    def initializePage(self):
        print("Displaying ErrorPage")
        self.label.setWordWrap(True)
        self.label.clear()
        self.label.setText(wizard.error_message_nice)
        self.setButtonText(wizard.CancelButton, "Quit")
        wizard.setButtonLayout([QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])


#############################################################################
# Pages flow in the wizard
#############################################################################

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    wizard = FirstAidWizard()

    disk_page = DiskPage()
    wizard.addPage(disk_page)

    work_page = WorkPage()
    wizard.addPage(work_page)

    success_page = SuccessPage()
    wizard.addPage(success_page)

    wizard.show()
    sys.exit(app.exec_())
