#!/usr/bin/env python3.7
# Unfortunately python3 does not seem to work on FreeBSD

# Remote Assistance
# Copyright (c) 2020, Simon Peter <probono@puredarwin.org>
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

import os, sys, time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtNetwork import QHostInfo
import psutil
import re
from time import sleep

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.closeEvent = self.closeEvent

        # Init QSystemTrayIcon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)) # TODO: Replace by binoculars icon
        self.tray_icon.show() # Works only if not running as root with sudo

        vbox = QtWidgets.QVBoxLayout()

        self.tuntox_infolabel = QtWidgets.QLabel()

        vbox.addWidget(self.tuntox_infolabel)

        self.vnc_infolabel = QtWidgets.QLabel()
        self.tox_id = ""
        self.vnc_infolabel.setText(self.tox_id)
        #self.vnc_infolabel.setFont(font)
        self.vnc_infolabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.vnc_infolabel.setVisible(False)
        vbox.addWidget(self.vnc_infolabel)

        self.setLayout(vbox)

        self.setWindowTitle(self.tr("Remote Assistance"))
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)

        self.x11vnc_port = 0

        self.startSharing()

    def startSharing(self):
        self.timer.stop()
        self.tuntox_infolabel.setText(self.tr(self.tr("Starting x11vnc")))
        command = 'x11vnc'
        args = ["-noxdamage", "-ncache", "10", "-ncache_cr", "-display", os.getenv("DISPLAY")] # "-localhost", "-no6"
        self.x11vnc_process = QtCore.QProcess()
        # proc.startDetached(command, args)
        self.x11vnc_process.readyReadStandardOutput.connect(self.onVncReadyReadStandardOutput)
        self.x11vnc_process.readyReadStandardError.connect(self.onVncReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.x11vnc_process.start(command, args)
        self.onTimer() # Make sure the new state is immediately reflected

    def startTuntox(self):
        self.tuntox_infolabel.setText(self.tr(self.tr("Starting tuntox")))
        command = "tuntox"
        args = [] # "-f", "localhost:" + str(self.x11vnc_port)]
        self.tuntox_process = QtCore.QProcess()
        self.tuntox_process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.tuntox_process.readyReadStandardError.connect(self.onReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.tuntox_process.start(command, args)
        self.onTimer() # Make sure the new state is immediately reflected
        self.timer.start()

    def stopSharing(self):
        self.timer.stop()

        try:
            self.x11vnc_process.kill()
        except:
            pass
        try:
            self.tuntox_process.kill()
        except:
            pass

        self.onTimer() # Make sure the new state is immediately reflected
        self.timer.start()

    def onVncReadyReadStandardOutput(self):
        print("onVncReadyReadStandardOutput")
        data = self.x11vnc_process.readAllStandardOutput().data().decode()
        print(data)

        x = re.findall("PORT=(.*)", data)
        if len(x) > 0:
            self.x11vnc_port = x[0]
            self.startTuntox()

    def onVncReadyReadStandardError(self):
        print("onVncReadyReadStandardError")
        data = self.x11vnc_process.readAllStandardError().data().decode()
        if "\n" in data:
            lines = data.split("\n")
            for line in lines:
                if not line.startswith("#"): # Those might confuse users
                    print(line)

        # "Got connection from client" = A VNC client has connected
        x = re.findall(self.tr("Got connection from client"), data)
        if len(x) > 0:
            self.tuntox_infolabel.setText(self.tr(self.tr("Remote control in action")))
            self.hide() # Hide this window to tray
            self.tray_icon.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_DriveNetIcon))  # TODO: Replace by blinking or red binoculars icon

#        # Address already in use = Another instance of x11vnc is already running on this port
#        x = re.findall(self.tr("Address already in use"), data)
#        if len(x) > 0:
#            msg = QtWidgets.QMessageBox()
#            msg.setIcon(QtWidgets.QMessageBox.Critical)
#            msg.setWindowTitle(" ")
#            msg.setText(self.tr("Could not start Remote Assistance because another instance is already running."))
#            msg.setInformativeText(self.tr("Quit the other instance and try again."))
#            msg.setDetailedText(data) # Text that appears when user clicks the "Show Details..." button
#            msg.exec_()
#            QtWidgets.QApplication.quit()

        # failed = catch-all for x11vnc errors (hopefully)
        x = re.findall(self.tr("failed"), data)
        if len(x) > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(self.tr("Could not start Remote Assistance."))
           #  msg.setInformativeText(self.tr("Quit the other instance and try again."))
            msg.setDetailedText(data) # Text that appears when user clicks the "Show Details..." button
            msg.exec_()
            QtWidgets.QApplication.quit()
            
    def onReadyReadStandardOutput(self):
        print("onReadyReadStandardOutput")
        data = self.tuntox_process.readAllStandardOutput().data().decode()
        print(data)

    def onReadyReadStandardError(self):
        print("onReadyReadStandardError")
        data = self.tuntox_process.readAllStandardError().data().decode()
        if "\n" in data:
            lines = data.split("\n")
            for line in lines:
                if not "[WARNING]" in line: # Those might confuse users
                    print(line)

        x = re.findall("Using Tox ID: (.*)", data)
        if len(x) > 0:
            self.tox_id = x[0]
            self.tuntox_infolabel.setText(self.tr(self.tr("A peer on the internet can now connect to:")))
            self.vnc_infolabel.setText("tuntox -i " + self.tox_id + " -L " + "59000:127.0.0.1:" + str(self.x11vnc_port))

        # Accepted friend request from ... as 0
        x = re.findall(self.tr("Accepted friend request from (.*) as"), data)
        if len(x) > 0:
            remote_tox_id = x[0]
            self.tuntox_infolabel.setText(self.tr(self.tr("Once they see the 'Accepted friend request' message, your peer can run TightVNC Viewer:")))
            self.vnc_infolabel.setText("vncviewer -noraiseonbeep -encodings 'copyrect tight zlib hextile' localhost::59000")
            # self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveNetIcon)) # TODO: Replace by blinking or red binoculars icon

    def onTimer(self):
        # print("Timer")
        if (checkIfProcessRunning("x11vnc") == True) and (checkIfProcessRunning("tuntox") == True):
            self.tuntox_infolabel.setVisible(True)
            self.vnc_infolabel.setVisible(True)
        else:
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        "This gets called automatically when the window is closed"
        print("closeEvent")
        self.stopSharing()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    app.aboutToQuit.connect(ex.stopSharing) # This gets called when the application is quit by other means than closing the window
    sys.exit(app.exec_())
