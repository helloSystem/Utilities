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


import os, sys, time, io

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    from PyQt5.QtCore import QObject, QProcess, pyqtSignal, QThread, QCoreApplication
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


class CommandReader(QObject):
    """

    Runs a program via QProcess, and passes each line of STDOUT to the `lines`
    signal.

    """

    lines = pyqtSignal(bytes)

    def __init__(self, parent, command, arguments):
        super().__init__(parent)
        self.command = command
        self.arguments = arguments

    def kill(self):
        self.process.kill()

    def start(self):
        self.process = QProcess(self)

        self.buffer = io.BytesIO(b"")
        self.process.readyReadStandardOutput.connect(self.handler)
        self.process.start(self.command, self.arguments)

    def wait(self):
        self.process.waitForFinished()

    def handler(self):
        position = self.buffer.tell()
        self.buffer.write(bytes(self.process.readAllStandardOutput()))
        self.buffer.seek(position)

        for line in self.buffer.readlines():
            if line == b"":
                if self.process.state() == QProcess.ProcessState.NotRunning:
                    self.kill()
                break
            self.lines.emit(line)


class ZeroconfDiscoverer(QThread):
    """

    Runs the `dns-sd` tool, creates a ZeroconfService for each service
    discovered, and passes those services to a signal: service_added and
    service_removed.

    It works like so:

    1. `dns-sd -B _services._dns-sd._udp` is run to enumerate all service types
    available on the local network.

    2. `dns-sd -B $SERVICE_TYPE` is run to enumerate all services of the
    specified type.

    3. `dns-sd -L $NAME $SERVICE_TYPE $DOMAIN` is run to get more details on a
    particular service.

    """

    service_added = pyqtSignal(ZeroconfService)
    service_removed = pyqtSignal(ZeroconfService)

    def cleanUpOnQuit(self, cmd):
        # Kill the command
        QCoreApplication.instance().aboutToQuit.connect(cmd.kill)
        # Then wait for it - the main loop won't exit until all commands have finished
        QCoreApplication.instance().aboutToQuit.connect(cmd.wait)

    def start(self):
        # List all service types
        cmd = CommandReader(self, "dns-sd", ["-B", "_services._dns-sd._udp"])
        cmd.lines.connect(self.type_line_handler)
        self.cleanUpOnQuit(cmd)
        cmd.start()

    def type_line_handler(self, line):
        line = line.decode()
        # Parse line
        data = line.split()
        if len(data) < 7:
            return
        if data[1] != "Add":
            return
        service_type = data[6]

        # List all services of this type
        cmd = CommandReader(self, "dns-sd", ["-B", service_type])
        cmd.lines.connect(self.service_line_handler)
        self.cleanUpOnQuit(cmd)
        cmd.start()

    def service_line_handler(self, line):
        line = line.decode()
        # Parse line
        data = line.split()
        if len(data) < 7:
            return
        if data[1] == "A/R":
            # Header line
            return
        adding = data[1] == "Add"

        name = " ".join(data[6:])
        service_type = data[5].strip(".")
        domain = data[4].strip(".")

        # We need a closure here so that we can pass on name, service_type, and domain
        def handler(line):
            line = line.decode()
            data = line.split()

            if len(data) < 7:
                return False
            if data[2] != "can" or data[3] != "be" or data[4] != "reached" or data[5] != "at":
                return False

            hostname_with_domain, port = data[6].split(":")
            hostname_with_domain = hostname_with_domain.strip(".")

            # Create a service
            service = ZeroconfService(name, service_type, hostname_with_domain, port)

            # Pass the service to the appropriate handler
            if adding:
                self.service_added.emit(service)
            else:
                self.service_removed.emit(service)

            return True

        cmd = CommandReader(self, "dns-sd", ["-L", name, service_type, domain])
        def f(line):
            ok = handler(line)
            if ok:
                cmd.kill()
        cmd.lines.connect(f)
        self.cleanUpOnQuit(cmd)
        cmd.start()


class ZeroconfServices():
    """

    Adds and removes services from a QListWidget.

    """

    def __init__(self, browser):
        self.services = []
        self.browser = browser

    def remove(self, service):
        print("Removing " + str(service))

        for i in range(len(self.services)):
            s = self.services[i]
            if s[0] == service:
                s[1].setHidden(True)
                self.services.pop(i)
                break

    # Define here what we should do with detected services. This gets run whenever a service is added
    def add(self, service):
        print("Appending " + str(service))

        # Check for services already in the list
        for s in self.services:
            if s[0] == service:
                return

        icon = "unknown"
        if service.url.startswith("device"):
            icon = "computer"
        if service.url.startswith("ssh"):
            icon = "terminal"
        if service.url.startswith("sftp") or service.url.startswith("smb"):
            icon = "folder"
        if service.url.startswith("raop"):
            # AirPlay
            icon = "network-wireless"
        if service.url.startswith("pulse"):
            # PulseAudio
            icon = "audio-card"
        if service.url.startswith("scanner") or service.url.startswith("uscan"):
            icon = "scanner"
        if service.url.startswith("http"):
            icon = "applications-internet"
        if service.url.startswith("ipp") or service.url.startswith("print") or service.url.startswith("pdl"):
            icon = "printer"
        item = QtWidgets.QListWidgetItem(QtGui.QIcon.fromTheme(icon), service.url)
        self.services.append((service, item))
        self.browser.list_widget.addItem(item)

class sshLogin(QtWidgets.QDialog):
    """

    Requests a username before launching `ssh` inside `QTerminal`.

    """

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

        self.services = ZeroconfServices(self)
        self.start_worker()

        sys.exit(self.app.exec_())

    def quit(self, event):
        self.app.quit()

    def onDoubleClicked(self):
        print("Double clicked")
        row = self.list_widget.selectedIndexes()[0].row()
        service = self.services.services[row][0]

        if service.url.startswith("http"):

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
            args = [service.url]
            try:
                proc.startDetached("xdg-open", args)
                return
            except:
                print("Cannot launch browser")
                return
        elif service.url.startswith("scanner") or service.url.startswith("uscan"):
            # Launch Xsane in the hope that it can do something with it
            os.system("xsane")
        if service.url.startswith("ipp") or service.url.startswith("print") or service.url.startswith("pdl"):
            os.system("launch 'Print Settings'")
        elif service.url.startswith("ssh"):
            # Launch the browser
            sshL = sshLogin(host=service.url)
            if sshL.exec_() == QtWidgets.QDialog.Accepted:
                print("Do something")
        else:
            reply = QtWidgets.QMessageBox.information(
                self.window,
                "To be implemented",
                "Something needs to be done here with\n%s\nPull requests welcome!" % service.url,
                QtWidgets.QMessageBox.Yes
            )

    def start_worker(self):
        self.worker = ZeroconfDiscoverer(None)
        self.worker.service_added.connect(self.add_handler)
        self.worker.service_removed.connect(self.remove_handler)
        self.worker.start()

    def add_handler(self, service):
        self.services.add(service)

    def remove_handler(self, service):
        self.services.remove(service)

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
