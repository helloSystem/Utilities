#!/usr/bin/env python3

"""
Automatic login handler for slim.
"""

import sys

from PyQt5.QtCore import  QProcess
from PyQt5.QtWidgets import QMessageBox, QApplication

slim_config_file = "/usr/local/etc/slim.conf"

def check_slim_conf():
    """
    Check whether file /usr/local/etc/slim.conf exists and is writable by root.
    """
    print("Checking whether file /usr/local/etc/slim.conf exists and is writable by root")
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "test", "-w", slim_config_file])
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        print("File /usr/local/etc/slim.conf is writable by root.")
        return True
    else:
        print("File /usr/local/etc/slim.conf is not writable by root.")
        QMessageBox.error(None, "Automatic login", "File /usr/local/etc/slim.conf is not writable by root.")
        return False

def enable_autologin(user):
    """
    Enable automatic login for user.
    """
    print("Enabling automatic login for user " + user)
    check_slim_conf()
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "grep", "^auto_login", slim_config_file])
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        p = QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^auto_login.*/auto_login yes/g", slim_config_file])
        print(p.program() + " " + " ".join(p.arguments()))
        p.start()
        p.waitForFinished()
        if p.exitCode() == 0:
            p = QProcess()
            p.setProgram("sudo")
            p.setArguments(["-A", "-E", "grep", "^default_user", slim_config_file])
            print(p.program() + " " + " ".join(p.arguments()))
            p.start()
            p.waitForFinished()
            if p.exitCode() == 0:
                p = QProcess()
                p.setProgram("sudo")
                p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^default_user.*/default_user " + user + "/g", slim_config_file])
                print(p.program() + " " + " ".join(p.arguments()))
                p.start()
                p.waitForFinished()
                if p.exitCode() == 0:
                    QMessageBox.information(None, "Automatic login", "Automatic login has been enabled for user " + user + ".")
                    return True
                else:
                    QMessageBox.warning(None, "Automatic login", "Automatic login could not be enabled for user " + user + ".")
                    return False
            else:
                p = QProcess()
                p.setProgram("sudo")
                p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^#default_user.*/default_user " + user + "/g", slim_config_file])
                print(p.program() + " " + " ".join(p.arguments()))
                p.start()
                p.waitForFinished()
                if p.exitCode() == 0:
                    QMessageBox.information(None, "Automatic login", "Automatic login has been enabled for user " + user + ".")
                    return True
                else:
                    QMessageBox.warning(None, "Automatic login", "Automatic login could not be enabled for user " + user + ".")
                    return False
        else:
            return False
    else:
        p = QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^#auto_login.*/auto_login yes/g", slim_config_file])
        print(p.program() + " " + " ".join(p.arguments()))
        p.start()
        p.waitForFinished()
        if p.exitCode() == 0:
            p = QProcess()
            p.setProgram("sudo")
            p.setArguments(["-A", "-E", "grep", "^default_user", slim_config_file])
            print(p.program() + " " + " ".join(p.arguments()))
            p.start()
            p.waitForFinished()
            if p.exitCode() == 0:
                p = QProcess()
                p.setProgram("sudo")
                p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^default_user.*/default_user " + user + "/g", slim_config_file])
                print(p.program() + " " + " ".join(p.arguments()))
                p.start()
                p.waitForFinished()
                if p.exitCode() == 0:
                    QMessageBox.information(None, "Automatic login",  "Automatic login has been enabled for user " + user + ".")
                    return True
                else:
                    QMessageBox.warning(None, "Automatic login",  "Automatic login could not be enabled for user " + user + ".")
                    return False
            else:
                p = QProcess()
                p.setProgram("sudo")
                p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^#default_user.*/default_user " + user + "/g", slim_config_file])
                print(p.program() + " " + " ".join(p.arguments()))
                p.start()
                p.waitForFinished()
                if p.exitCode() == 0:
                    QMessageBox.information(None, "Automatic login",  "Automatic login has been enabled for user " + user + ".")
                    return True
                else:
                    QMessageBox.warning(None, "Automatic login",  "Automatic login could not be enabled for user " + user + ".")
                    return False
        else:
            return False

def disable_autologin():
    """
    Disable automatic login.
    """
    check_slim_conf()
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "grep", "^auto_login", slim_config_file])
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        p = QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^auto_login.*/auto_login no/g", slim_config_file])
        print(p.program() + " " + " ".join(p.arguments()))
        p.start()
        p.waitForFinished()
        if p.exitCode() == 0:
            p = QProcess()
            p.setProgram("sudo")
            p.setArguments(["-A", "-E", "grep", "^default_user", slim_config_file])
            print(p.program() + " " + " ".join(p.arguments()))
            p.start()
            p.waitForFinished()
            if p.exitCode() == 0:
                p = QProcess()
                p.setProgram("sudo")
                p.setArguments(["-A", "-E", "sed", "-i", "''", "-e", "s/^default_user.*/#default_user/g", slim_config_file])
                print(p.program() + " " + " ".join(p.arguments()))
                p.start()
                p.waitForFinished()
                if p.exitCode() == 0:
                    QMessageBox.information(None, "Automatic login",  "Automatic login has been disabled.")
                    return True
                else:
                    QMessageBox.warning(None, "Automatic login",  "Automatic login could not be disabled.")
                    return False
            else:
                QMessageBox.information(None, "Automatic login",  "Automatic login has been disabled.")
                return True
        else:
            QMessageBox.warning(None, "Automatic login",  "Automatic login could not be disabled.")
            return False
    else:
        QMessageBox.information(None, "Automatic login",  "Automatic login was already disabled.")
        return True


def check_autologin_user():
    """
    Returns the user that is set to autologin or None if no user is set.
    """
    check_slim_conf()
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "grep", "^default_user", slim_config_file])
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        return p.readAllStandardOutput().data().decode("utf-8").split(" ")[1].strip()
    else:
        return None

def check_autologin():
    check_slim_conf()
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "grep", "^auto_login[[:space:]]*yes", slim_config_file])
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        return True
    else:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if check_autologin():
        # Check for which user autologin is enabled
        user = check_autologin_user()
        print("Autologin is enabled for user " + user)
        if disable_autologin():
            print("Autologin has been disabled")
            sys.exit(0)
        else:
            print("Autologin could not be disabled")
            sys.exit(1)
    else:
        print("Autologin is disabled")
        if enable_autologin("user"):
            print("Autologin has been enabled for user user")
            sys.exit(0)
        else:
            print("Autologin could not be enabled")
            sys.exit(1)