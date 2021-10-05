#!/usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import os
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QFile, pyqtSlot, QProcess, QProcessEnvironment
from PyQt5.uic import loadUi

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
# FIXME: Do not import translations from outside of the appliction bundle
# which currently is difficult because we have all translations for all applications
# in the whole repository in the same .ts files
tstr = tstranslator.TsTranslator(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + "/i18n", None)
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

class Users(QMainWindow):
    def __init__(self):
        super(Users, self).__init__()
        self.load_ui()

    def load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "adduser.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()

        # Translate the widgets in the UI objects that were just loaded from the .ui file
        self.setWindowTitle(tr(self.windowTitle()))
        for e in self.findChildren(QObject, None, Qt.FindChildrenRecursively):
            if hasattr(e, 'text') and hasattr(e, 'setText'):
                e.setText(tr(e.text()))

        self._showMenu()
        self.noMatchLabel.setHidden(True)
        self.addUserButton.setDisabled(True)
        self.users = self.get_existing_users()
        print(self.users)

    def get_existing_users(self):
        p = QProcess()
        p.setProgram("cat")
        p.setArguments(["/etc/passwd"])
        p.start()
        p.waitForFinished()
        lines = p.readAllStandardOutput().data().decode().split("\n")
        users = []
        for line in lines:
            if line == "":
                continue
            if line.startswith("#"):
                continue
            u = User(line)
            print(u)
            users.append(u)
        return(users)

    @pyqtSlot()
    def populateUsername(self):
        if " " in self.fullName.text():
            generated_username = self.fullName.text().split(" ")[0].lower()[0] + self.fullName.text().split(" ")[len(self.fullName.text().split(" ")) - 1].lower()
        else:
            generated_username = self.fullName.text().lower()
        # Clean auto-populated username of special characters
        generated_username = re.sub('\W+', '', generated_username)

        if generated_username != self.username.text():
            self.username.setText(generated_username)

    @pyqtSlot()
    def okButtonClicked(self):
        print("OK button clicked")
        p = QProcess()
        env = QProcessEnvironment.systemEnvironment()
        env.insert("SUDO_ASKPASS",  os.path.dirname(__file__) + "/askpass.py") # FIXME: This is not working
        p.setProcessEnvironment(env)
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", os.path.dirname(__file__) + "/adduser.sh", self.username.text(), self.password.text()])
        p.start()
        p.waitForFinished()

        err = p.readAllStandardError().data().decode()
        err = err.replace("QKqueueFileSystemWatcherEngine::addPaths: open: No such file or directory", "").strip() # FIXME: Where is this coming from, remove it at the root of the problem
        if err and err != "":
            print(err)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(err)
            # msg.setInformativeText('More information')
            msg.setWindowTitle("Error")
            msg.exec_()
        out = p.readAllStandardOutput().data().decode()
        if out:
            print(out)
            if "Successfully added" in out:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Successfully added the user.")
                # msg.setInformativeText('More information')
                msg.setWindowTitle(" ")
                msg.exec_()
                self.close()
        print("p.exitStatus():", p.exitStatus())
        if p.exitStatus() != 0:
            print("An error occured; TODO: Handle it in the GUI")

    @pyqtSlot()
    def removeUsers(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText('Not yet implemented')
        # msg.setInformativeText('Not yet implemented')
        msg.setWindowTitle(" ")
        msg.exec_()

    @pyqtSlot()
    def check(self):
        all_checked = True
        if self.username.text() == "":
            all_checked = False
        if self.password.text() != self.passwordRepeat.text():
            all_checked = False
            self.noMatchLabel.setHidden(False)
        else:
            self.noMatchLabel.setHidden(True)
        # Prevent from adding a user with an already-existing username
        for user in self.users:
            if user.username == self.username.text():
                all_checked = False

        if all_checked == False:
            self.addUserButton.setDisabled(True)
        else:
            self.addUserButton.setDisabled(False)

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
        msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Users.png"))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Users</h3>")
        msg.setInformativeText(
            "A simple preferences application to add users using <a href='https://www.freebsd.org/cgi/man.cgi?adduser'>adduser</a>, <a href='https://www.freebsd.org/cgi/man.cgi?usermod'>usermod</a>, and <a href='https://www.freebsd.org/cgi/man.cgi?groupmod'>groupmod</a><br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()


if __name__ == "__main__":
    app = QApplication([])
    widget = Users()
    widget.show()
    sys.exit(app.exec_())
