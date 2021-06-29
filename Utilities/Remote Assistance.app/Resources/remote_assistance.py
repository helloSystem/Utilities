#!/usr/bin/env python3

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


import os, sys, time, socket
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtNetwork import QHostInfo
import psutil
import re
from time import sleep
import shutil


# TODO: Reimplement tuntox in Python using https://github.com/TokTok/py-toxcore-c
# According to https://github.com/gjedeer/tuntox/issues/33#issuecomment-439614638
# the protocol is very simple and the tuntox author would be happy
# to help anyone who wants to reimplement it.
# Especially with Python and its robust data types, the reimplementation
# shouldn't take more than 500 lines of code.


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

def cmd_exists(cmd):
    return shutil.which(cmd) is not None
    
class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.checkPrerequisites(["x11vnc", "tuntox"])

        if internetCheckConnected() == False:
            print("Offline?")
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(self.tr("You need an active internet connection in order to use Remote Assistance."))
            msg.exec_()
            sys.exit(0)

        self.closeEvent = self.closeEvent
        self._showMenu()
        
        self.tuntox_process = None
        self.x11vnc_process = None

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

        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setWindowTitle(self.tr("Remote Assistance"))
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)

        self.x11vnc_port = 0

        self.startSharing()

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

    def startSharing(self):
        self.timer.stop()
        self.tuntox_infolabel.setText(self.tr("Starting remote control..."))
        self.tuntox_infolabel.setVisible(True)
        command = 'x11vnc'
        args = ["-no6", "-noshm", "-listen", "localhost", "-localhost", "-noxdamage", "-ncache", "10", "-ncache_cr", "-display", os.getenv("DISPLAY")]
        self.x11vnc_process = QtCore.QProcess()
        # proc.startDetached(command, args)
        self.x11vnc_process.readyReadStandardOutput.connect(self.onVncReadyReadStandardOutput)
        self.x11vnc_process.readyReadStandardError.connect(self.onVncReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.x11vnc_process.start(command, args)
        self.onTimer() # Make sure the new state is immediately reflected

    def startTuntox(self):
        self.tuntox_infolabel.setText(self.tr("Starting encrypted tunnel..."))
        command = "tuntox"
        # FIXME: Restrict sharing to only the port needed for x11vnc
        args = [] # "-f", "127.0.0.1:" + str(self.x11vnc_port) # -f is an undocumented switch that limits sharing to the selected host and port
        self.tuntox_process = QtCore.QProcess()
        self.tuntox_process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.tuntox_process.readyReadStandardError.connect(self.onReadyReadStandardError)
        print("Starting " + command + " " + " ".join(args))
        self.tuntox_process.start(command, args)
        self.onTimer() # Make sure the new state is immediately reflected
        self.timer.start()

    def stopSharing(self):
        self.timer.stop()
        print("stopSharing")
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

        # Address already in use = Another instance of x11vnc is already running on this port
        x = re.findall(self.tr("Address already in use"), data)
        if len(x) > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(self.tr("Could not start Remote Assistance because another instance is already running."))
            msg.setInformativeText(self.tr("Quit the other instance and try again."))
            msg.setDetailedText(data) # Text that appears when user clicks the "Show Details..." button
            msg.exec_()
            QtWidgets.QApplication.quit()

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
            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard )
            cb.setText(self.tox_id, mode=cb.Clipboard)
    
        x = re.findall("been established", data)
        if len(x) > 0:
            self.tuntox_infolabel.setText(self.tr("A peer on the internet can access all ports on the local machine. For example:"))
            self.vnc_infolabel.setText("tuntox -i " + self.tox_id + " -L " + "59000:127.0.0.1:" + str(self.x11vnc_port))
            self.vnc_infolabel.setVisible(True)
            
        # Accepted friend request from ... as 0
        x = re.findall(self.tr("Accepted friend request from (.*) as"), data)
        if len(x) > 0:
            remote_tox_id = x[0]
            self.tuntox_infolabel.setText(self.tr(self.tr("Once they see the 'Accepted friend request' message, your peer can run TightVNC Viewer:")))
            self.vnc_infolabel.setText("vncviewer -noraiseonbeep -encodings 'tight' 127.0.0.1::59000") #xxxxxxx localhost???
            self.vnc_infolabel.setVisible(True)
            # self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveNetIcon)) # TODO: Replace by blinking or red binoculars icon

    def onTimer(self):
        # print("Timer")
        if (self.tuntox_process == None):
            print("tuntox process has not yet been started")
        elif (self.tuntox_process.processId() != 0) and (self.x11vnc_process == None):
            print("tuntox process is running but x11vnc process has not yet been started")
        elif (self.tuntox_process.processId() != 0) and (self.x11vnc_process.processId() != 0):
            pass
        else:
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        "This gets called automatically when the window is closed"
        print("closeEvent")
        self.stopSharing()
        event.accept()

    def _showMenu(self):
        giveAct = QtWidgets.QAction('&Give Assistance', self)
        giveAct.setShortcut('Ctrl+G')
        giveAct.setStatusTip('Give Assistance')
        giveAct.triggered.connect(self.giveAssistance)
        exitAct = QtWidgets.QAction('&Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.QApplication.quit)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(giveAct)
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
        msg.setText("<h3>Remote Assistance</h3>")
        msg.setInformativeText("A simple Remote Assistance application using the encrypted peer-to-peer Tox protocol<br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

    def giveAssistance(self):
        self.assistance_process = QtCore.QProcess()
        command = os.path.dirname(__file__) + "/remote_assistance_client.py"
        args = []
        print("Starting " + command + " " + " ".join(args))
        self.assistance_process.startDetached(command, args)
        QtWidgets.QApplication.quit()
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    app.aboutToQuit.connect(ex.stopSharing) # This gets called when the application is quit by other means than closing the window
    sys.exit(app.exec_())
