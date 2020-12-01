#!/usr/bin/env python3.7
# Unfortunately python3 does not seem to work on FreeBSD

# Sharing
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

        vbox = QtWidgets.QVBoxLayout()

        self.hostname_lineedit = QtWidgets.QLineEdit()

        # hostname = QHostInfo.localHostName() # This gets the currently effective hostname
        # But we want the hostname that will be in effect after a reboot
        proc = QtCore.QProcess()
        command = 'sysrc'
        args = ["-n", "hostname"]
        proc.start(command, args)
        proc.waitForFinished()
        hostname = str(proc.readAllStandardOutput(), 'utf-8').strip()

        self.hostname_lineedit.setText(hostname)

        vbox.addWidget(self.hostname_lineedit)

        self.ssh_cb = QtWidgets.QCheckBox('Remote Login', self)
        vbox.addWidget(self.ssh_cb)

        self.hostname_infolabel = QtWidgets.QLabel()
        vbox.addWidget(self.hostname_infolabel)
        self.hostname_infolabel.setText("Computers on your local network can access this computer at:")
        self.hostname_label = QtWidgets.QLabel()
        vbox.addWidget(self.hostname_label)
        font = QtGui.QFont()
        font.setFamily('monospace')
        font.setFixedPitch(True)
        self.hostname_label.setFont(font)

        self.vnc_cb = QtWidgets.QCheckBox('Screen Sharing', self)
        vbox.addWidget( self.vnc_cb)
        self.vnc_infolabel = QtWidgets.QLabel()
        vbox.addWidget(self.vnc_infolabel)
        self.vnc_infolabel.setText("Computers on your local network can access this screen using VNC over ssh")

        self.setLayout(vbox)

        self.setWindowTitle("Sharing")
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)
        self.onTimer() # Do it right now as well
        self.hostname_lineedit.editingFinished.connect(self.setHostname)
        self.ssh_cb.clicked.connect(self.setSsh) # Do this only after we have set the initial state
        self.vnc_cb.clicked.connect(self.setVnc) # Do this only after we have set the initial state

    def setHostname(self):
        # For unknown reasons, setting the hostname with the 'hostname' command
        # makes FreeBSD behave strangely. Hence we are not doing this, resulting
        # in changes being applied only after a reboot. FIXME
        proc = QtCore.QProcess()
        command = 'sysrc'
        args = ["hostname=" + self.hostname_lineedit.text().replace(" ", "-")]
        proc.start(command, args)
        proc.waitForFinished()
        QtWidgets.QMessageBox.information(
            None,
            None,
            "The changed computer name will be in effect when you restart your computer.",
        )

    def setSsh(self):
        self.timer.stop()
        print("setSsh")
        action = "stop"
        if self.ssh_cb.isChecked() is True:
            # Note: we get called before the checkbox has been toggled, hence this is correct
            action = "start"

        proc = QtCore.QProcess()

        # First, enable/disable
        command = 'sysrc'
        if action == "start":
            yn = "YES"
        else:
            yn = "NO"
        args = ["sshd_enable=" + yn]
        proc.start(command, args)
        proc.waitForFinished()

        # Second, start/stop
        command = 'service'
        args = ["sshd", action]
        try:
            proc.start(command, args)
            proc.waitForFinished()
            print(str(proc.readAllStandardOutput(), 'utf-8')).strip()
            print(str(proc.readAllStandardError(), 'utf-8')).strip()
        except:  # FIXME: do not use bare 'except'
            pass
        self.onTimer() # Make sure the new state is immediately reflected
        self.timer.start()

    def setVnc(self):
        self.timer.stop()

        print("setVnc")
        command = 'killall'
        args = ["x11vnc"]
        if self.vnc_cb.isChecked() is True:
            # Note: we get called before the checkbox has been toggled, hence this is correct
            # x11vnc -ncache 10 -ncache_cr -display $DISPLAY
            command = 'x11vnc'
            args = ["-localhost", "-avahi", "-ncache", "10", "-ncache_cr", "-display", os.getenv("DISPLAY")]
        proc = QtCore.QProcess()
        proc.startDetached(command, args)

        self.onTimer() # Make sure the new state is immediately reflected
        self.timer.start()

    def onTimer(self):
        print("Timer")
        hostname = QHostInfo.localHostName()
        self.hostname_label.setText("ssh <username>@" + hostname + ".local.")
        if checkIfProcessRunning("sshd") == True:
            self.ssh_cb.setChecked(True)
            self.hostname_infolabel.setVisible(True)
            self.hostname_label.setVisible(True)
            self.vnc_cb.setEnabled(True)
        else:
            self.ssh_cb.setChecked(False)
            self.hostname_infolabel.setVisible(False)
            self.hostname_label.setVisible(False)
            self.vnc_infolabel.setVisible(False)
            self.vnc_cb.setEnabled(False)
        if checkIfProcessRunning("x11vnc") and checkIfProcessRunning("sshd") == True:
            self.vnc_cb.setChecked(True)
            self.vnc_infolabel.setVisible(True)
        else:
            self.vnc_cb.setChecked(False)
            self.vnc_infolabel.setVisible(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
