#!/usr/bin/env python3.7


# Simple Zeroconf browser written for FreeBSD in PyQt5


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

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except:
    print("Could not import PyQt5. On FreeBSD, sudo pkg install py37-qt5-widgets")

# https://stackoverflow.com/a/377028
def which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class ZeroconfService():
    """

    Represents one service.

    """

    def __init__(self, name, service_type, hostname_with_domain, port):
        self.name = name
        self.service_type = service_type
        self.hostname_with_domain = hostname_with_domain
        self.port = port
        self.url = "%s://%s:%s" % (self.service_type.split("_")[1].split("-")[0].replace(".", ""), self.hostname_with_domain, self.port)

    def __repr__(self):
        return "%s on %s:%s" % (self.service_type, self.hostname_with_domain, self.port)

    def __eq__(self, other):
        return self.url == other.url


class ZeroconfServices():

    def __init__(self):
        self.services = []

    def add(self, service):
        if service.ip_version == "IPv4":
            print("Appending " + str(service))
            self.services.append(service)
            service.handle()
        else:
            print("service.ip_version: %s" % service.ip_version)
            print("Not appending since IPv6; TODO: Show those as well but check for duplicates")

    def remove(self, avahi_browse_line):
        print("TODO: To be implemented: Remove the service from the list if certain criteria match")
        for service in self.services:
            print(service.service_type)
            print(service.hostname_with_domain)

class sshLogin(QtWidgets.QDialog):
    def __init__(self, host=None, parent=None):
        super(sshLogin, self).__init__(parent)
        self.host = host
        self.setWindowTitle("Username")
        self.textName = QtWidgets.QLineEdit(self)
        self.buttonLogin = QtWidgets.QPushButton('Connect', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        self.accept() # Close dialog
        # Launch ssh in QTerminal
        proc = QtCore.QProcess()
        args = ["QTerminal", "-e", "ssh", self.host, "-l", self.textName.text()]
        try:
            proc.startDetached("launch", args)
        except:
            print("Cannot launch browser")
            return

class ZeroconfBrowser:

    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)

        # Window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('Connnect to Server')
        self.window.setMinimumWidth(500)
        self.window.setMinimumHeight(350)
        self.window.closeEvent = self.quit
        self.layout = QtWidgets.QVBoxLayout()

        # List
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.onDoubleClicked)
        self.layout.addWidget(self.list_widget)

        # Label
        # self.label = QtWidgets.QLabel()
        # self.label.setText("This application is written in PyQt5. It is very easy to extend. Look inside the .app to see its source code.")
        # self.label.setWordWrap(True)
        # self.layout.addWidget(self.label)

        self._showMenu()

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.window.setCentralWidget(widget)
        self.window.show()

        self.services = ZeroconfServices()
        self.ext_process = QtCore.QProcess()
        self.long_running_function()

        sys.exit(self.app.exec_())

    def quit(self, event):
        self.app.quit()

    def onDoubleClicked(self):
        print("Double clicked")
        row = self.list_widget.selectedIndexes()[0].row()
        print(self.services.services[row].url)

        if self.services.services[row].url.startswith("http"):

            # Find out the browser
            # TODO: Give preference to the default browser the user may have set in the system.
            # user@FreeBSD$  xdg-settings get default-web-browser
            # userapp-Firefox-59CXP0.desktop
            # Then no one knows where that file actually is, nor what it Exec= line contains. xdg is so convoluted!
            # user@FreeBSD$ LANG=C x-www-browser
            # bash: x-www-browser: command not found
            #
            # browser_candidates = [os.environ.get("BROWSER"), "x-www-browser", "chrome", "chromium-browser", "google-chrome", "firefox", "iceweasel", "seamonkey", "mozilla", "epiphany", "konqueror"]
            # for browser_candidate in browser_candidates:
            #     if browser_candidate != None:
            #         if which(browser_candidate) != None:
            #             browser = browser_candidate
            #             print("Using as browser: %s" % browser)
            #             break

            # Launch the browser
            proc = QtCore.QProcess()
            args = [self.services.services[row].url]
            try:
                proc.startDetached("xdg-open", args)
                return
            except:
                print("Cannot launch browser")
                return
        elif self.services.services[row].url.startswith("scanner") or self.services.services[row].url.startswith("uscan"):
            # Launch Xsane in the hope that it can do something with it
            os.system("xsane")
        if self.services.services[row].url.startswith("ipp") or self.services.services[row].url.startswith("print") or self.services.services[row].url.startswith("pdl"):
            os.system("launch 'Print Settings'")
        elif self.services.services[row].url.startswith("ssh"):
            # Launch the browser
            sshL = sshLogin(host=self.services.services[row].url)
            if sshL.exec_() == QtWidgets.QDialog.Accepted:
                print("Do something")
        else:
            reply = QtWidgets.QMessageBox.information(
                self.window,
                "To be implemented",
                "Something needs to be done here with\n%s\nPull requests welcome!" % self.services.services[row].url,
                QtWidgets.QMessageBox.Yes
            )

    def long_running_function(self):
        self.ext_process.finished.connect(self.onProcessFinished)
        self.ext_process.setProgram("avahi-browse")
        self.ext_process.setArguments(["-arlp"])

        try:
            pid = self.ext_process.start()
            print("avahi-browse started")
        except:
            self.showErrorPage("avahi-browse cannot be launched.")
            return  # Stop doing anything here


        if self.ext_process.waitForStarted(-1):
            while True:
                QtWidgets.QApplication.processEvents()  # Important trick so that the app stays responsive without the need for threading!
                time.sleep(0.1)
                while self.ext_process.canReadLine():
                    # This is a really crude attempt to read line-wise. FIXME: Do better
                    line = str(self.ext_process.readLine())
                    self.processLine(line)

        print("ERROR: We should never reach this!")

    def onProcessFinished(self):
        print("onProcessFinished called")

    def processLine(self, line):
        line = str(line).replace("b'", "").replace("\\n'", "")
        print(line)
        if line.startswith("="):
            s = ZeroconfService(line, self)
            self.services.add(s)
        if line.startswith("-"):
            s = ZeroconfService(line, self)
            self.services.remove(line)

    def _showMenu(self):
        exitAct = QtWidgets.QAction('&Quit', self.window)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(sys.exit, 0)
        menubar = self.window.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        aboutAct = QtWidgets.QAction('&About', self.window)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAct)


    def _showAbout(self):
        print("showDialog")
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Resources/Zeroconf.png"))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Zeroconf</h3>")
        msg.setInformativeText(
            "A simple utility to browse services on the network announced with Zeroconf<br><br>Grateful acknowledgement is made to <a href='https://en.wikipedia.org/wiki/Stuart_Cheshire'>Stuart Cheshire</a> who pioneered this incredibly useful technology<br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

if __name__ == "__main__":

    zb = ZeroconfBrowser()
