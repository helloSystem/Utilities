#!/usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import os
import re
import getpass

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox, QPushButton, QDialog, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QFile, pyqtSlot, QProcess, QProcessEnvironment, QObject, Qt
from PyQt5.uic import loadUi

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
# FIXME: Do not import translations from outside of the application bundle
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
        # env.insert("SUDO_ASKPASS",  os.path.dirname(__file__) + "/askpass.py") # FIXME: This is not working
        p.setProcessEnvironment(env)
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", os.path.dirname(__file__) + "/adduser.sh", self.username.text(), self.fullName.text(), self.password.text()])
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
                msg.setText(tr("Successfully added the user."))
                # msg.setInformativeText('More information')
                msg.setWindowTitle(" ")
                msg.exec_()

        print("p.exitStatus():", p.exitStatus())
        if p.exitStatus() != 0:
            # Error dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(tr("Failed to add the user."))
            # msg.setInformativeText('More information')
            msg.setWindowTitle(tr("Error"))
            msg.exec_()
        
        # Refresh the list of users
        self.users = self.get_existing_users()

    @pyqtSlot()
    def removeUsers(self):

        # Show a list of users in the system with UID 1000 and above
        # and allow the user to select one user to remove

        # Open a dialog with a list of users
        # and a button to remove the selected user
        # and a button to cancel

        self.remove_user_dialog = QDialog()
        self.remove_user_dialog.setWindowTitle(tr("Remove user"))
        self.remove_user_dialog.setWindowModality(Qt.ApplicationModal)
        self.remove_user_dialog.resize(400, 300)
        layout = QVBoxLayout()
        self.remove_user_dialog.setLayout(layout)

        # Add a list of users
        users = QListWidget()
        for user in self.users:
            if int(user.uid) >= 1000 and int(user.uid) < 65534:
                item = QListWidgetItem(user.info + " (" + user.username + ")")
                item.setToolTip(user.uid + " " + user.gid + " " + user.home + " " + user.shell)
                item.setData(Qt.UserRole, user.username)

                users.addItem(item)
                # Disable if the user is the current user
                if user.username == getpass.getuser():
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

        layout.addWidget(users)

        # Add a button to remove the selected user
        removeButton = QPushButton(tr("Remove"))
        
        removeButton.clicked.connect(lambda: self.removeUser(users.currentItem().data(Qt.UserRole)))
        layout.addWidget(removeButton)
        removeButton.setDisabled(True)
        users.itemSelectionChanged.connect(lambda: removeButton.setDisabled(users.selectedItems() == []))

        # Add a button to cancel
        cancelButton = QPushButton(tr("Cancel"))
        cancelButton.clicked.connect(self.remove_user_dialog.close)
        layout.addWidget(cancelButton)

        self.remove_user_dialog.exec_()

    def removeUser(self, username):

        # Ask for confirmation
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(tr("Are you sure you want to remove the user %s?") % username)
        msg.setInformativeText(tr("The user's home directory will be deleted. This cannot be undone."))
        msg.setWindowTitle(tr("Remove user"))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        if ret == QMessageBox.No:
            return
            
        print("Removing user", username)
        p = QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", "pw", "userdel", "-n", username, "-r"])
        print(p.program() + " " + " ".join(p.arguments()))
        p.start()
        p.waitForFinished()

        err = p.readAllStandardError().data().decode()
        if err and err != "":
            self.remove_user_dialog.close()
            print(err)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(err)
            msg.setWindowTitle(tr("Error"))
            msg.exec_()
        else:
            self.remove_user_dialog.close()
            print(tr("Successfully removed user %s") % username)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(tr("Successfully removed user %s") % username)
            msg.setWindowTitle(" ")
            msg.exec_()

        # Refresh the list of users
        self.users = self.get_existing_users()

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
