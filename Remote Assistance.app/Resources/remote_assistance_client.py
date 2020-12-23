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
import shutil


# TODO: Reimplement tuntox in Python using https://github.com/TokTok/py-toxcore-c
# According to https://github.com/gjedeer/tuntox/issues/33#issuecomment-439614638
# the protocol is very simple and the tuntox author would be happy
# to help anyone who wants to reimplement it.
# Especially with Python and its robust data types, the reimplementation
# shouldn't take more than 500 lines of code.


def cmd_exists(cmd):
    return shutil.which(cmd) is not None
    
class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.checkPrerequisites(["/usr/local/lib/ssvnc/vncviewer", "tuntox"])

        self.closeEvent = self.closeEvent
        self._showMenu()
        
        self.tuntox_process = None
        self.vncviewer_process = None

        # Init QSystemTrayIcon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)) # TODO: Replace by binoculars icon
        self.tray_icon.show() # Works only if not running as root with sudo

        vbox = QtWidgets.QVBoxLayout()

        self.tuntox_infolabel = QtWidgets.QLabel()
        vbox.addWidget(self.tuntox_infolabel)
        self.tuntox_infolabel.setText(self.tr(self.tr("Enter ID of the computer asking for support:")))

        self.tox_btn = QtWidgets.QPushButton()
        self.tox_btn.setText(self.tr("Connect"))
        
        self.tox_btn.clicked.connect(self.startTuntox)
        self.tox_btn.setEnabled(False)
        self.tox_id_lineedit = QtWidgets.QLineEdit()
        vbox.addWidget(self.tox_id_lineedit)
        vbox.addWidget(self.tox_btn)
        self.tox_id_lineedit.returnPressed.connect(self.tox_btn.click)
        self.tox_id_lineedit.textChanged.connect(lambda: self.tox_btn.setEnabled(True))

        self.vnc_infolabel = QtWidgets.QLabel()
        self.tox_id = ""
        self.vnc_infolabel.setText(self.tox_id)
        #self.vnc_infolabel.setFont(font)
        self.vnc_infolabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.vnc_infolabel.setVisible(False)
        vbox.addWidget(self.vnc_infolabel)

        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setWindowTitle(self.tr("Remote Assistance Client"))
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)

        self.x11vnc_port = 0

    def checkPrerequisites(self, prerequisites):
        for prerequisite in prerequisites:
            if not cmd_exists(prerequisite):
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle(" ")
                msg.setText(self.tr("Could not start Remote Assistance because %s is missing." ) % prerequisite)
                msg.setInformativeText(self.tr("Please install it and try again."))
                msg.exec_()
                sys.exit(0)
                
    def startTuntox(self):
        self.tuntox_infolabel.setText(self.tr(self.tr("Starting tuntox client mode")))
        self.tox_btn.setEnabled(False)
        self.tox_id_lineedit.setEnabled(False)
        command = "tuntox"
        # -L localport:127.0.0.1:dest_port
        args = ["-i", self.tox_id_lineedit.text(), "-L", "59000:127.0.0.1:5900"]
        self.tuntox_process = QtCore.QProcess()
        self.tuntox_process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.tuntox_process.readyReadStandardError.connect(self.onReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.tuntox_process.start(command, args)

    def startVncClient(self, use_alternate_syntax=False):
        self.timer.stop()
        print("startVncClient")
        self.tuntox_infolabel.setText(self.tr(self.tr("Starting vncviewer")))
        command = '/usr/local/lib/ssvnc/vncviewer' # SSVNC Viewer (based on TightVNC viewer); normal TightVNC viewer refuses connection
        args  = ["-noraiseonbeep", "-encodings", "tight", "127.0.0.1::59000"] #xxxxxxx localhost???
        self.vncviewer_process = QtCore.QProcess()
        self.vncviewer_process.readyReadStandardOutput.connect(self.onVncReadyReadStandardOutput)
        self.vncviewer_process.readyReadStandardError.connect(self.onVncReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.vncviewer_process.start(command, args)
        self.timer.start(1000)

    def stopVncClient(self):
        self.timer.stop()
        print("stopVncClient")

        try:
            self.vncviewer_process.kill()
        except:
            pass
        try:
            self.tuntox_process.kill()
        except:
            pass

        self.timer.start()

    def onVncReadyReadStandardOutput(self):
        print("onVncReadyReadStandardOutput")
        data = self.vncviewer_process.readAllStandardOutput().data().decode()
        print(data)

        x = re.findall("PORT=(.*)", data)
        if len(x) > 0:
            self.x11vnc_port = x[0]
            self.startTuntox()

    def onVncReadyReadStandardError(self):
        print("onVncReadyReadStandardError")
        data = self.vncviewer_process.readAllStandardError().data().decode()
        print(data)

        # Desktop name = We are connected, now we can hide this window
        x = re.findall("Desktop name \"(.*)\"", data)
        if len(x) > 0:
            print("Connected to %s" % x)
            self.tuntox_infolabel.setText(self.tr(self.tr("Remote control in action")))
            self.hide()  # Hide this window to tray
            self.tray_icon.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_DriveNetIcon))  # TODO: Replace by blinking or red binoculars icon
            
    def onReadyReadStandardOutput(self):
        print("onReadyReadStandardOutput")
        data = self.tuntox_process.readAllStandardOutput().data().decode()
        print(data)

    def onReadyReadStandardError(self):
        print("onReadyReadStandardError")
        data = self.tuntox_process.readAllStandardError().data().decode()
        print(data)
        lines = data.split("\n")
        if len(lines) > 1:
            last_line = lines[len(lines)-2] # The last line seems to be blank
            x = re.findall("\[.*\](.*)", last_line)
            if len(x) > 0:
                self.tuntox_infolabel.setText(x[0].strip())

        x = re.findall("Friend request accepted", data)
        if len(x) > 0:
            self.startVncClient()
            # self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveNetIcon)) # TODO: Replace by blinking or red binoculars icon

        x = re.findall("Invalid Tox ID", data)
        if len(x) > 0:
            self.tox_btn.setEnabled(True)
            self.tox_id_lineedit.clear()
            self.tox_id_lineedit.setEnabled(True)
            self.tox_id_lineedit.setFocus()
            self.tox_btn.setEnabled(False)

    def onTimer(self):
        # print("Timer")
        if (self.tuntox_process == None):
            print("tuntox process has not yet been started")
        elif (self.tuntox_process.processId() != 0) and (self.vncviewer_process == None):
            print("tuntox process is running but x11vnc process has not yet been started")
        elif (self.tuntox_process.processId() != 0) and (self.vncviewer_process.processId() != 0):
            self.tuntox_infolabel.setVisible(True)
            self.vnc_infolabel.setVisible(True)
        else:
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        "This gets called automatically when the window is closed"
        print("closeEvent")
        self.stopVncClient()
        event.accept()

    def _showMenu(self):
        exitAct = QtWidgets.QAction('&Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.QApplication.quit)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        aboutAct = QtWidgets.QAction('&About', self)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAct)
        
    def _showAbout(self):
        print("showDialog")
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Remote Assistance.png"))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Remote Assistance Client</h3>")
        msg.setInformativeText("A simple Remote Assistance application using the encrypted peer-to-peer Tox protocol<br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    app.aboutToQuit.connect(ex.stopVncClient) # This gets called when the application is quit by other means than closing the window
    sys.exit(app.exec_())
