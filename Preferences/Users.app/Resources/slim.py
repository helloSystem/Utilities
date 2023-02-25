#!/usr/bin/env python3

"""
Automatic login handler for slim.
"""

import sys

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QMessageBox, QApplication

slim_config_file = "/usr/local/etc/slim.conf"

def run_with_sudo(command):
    """
    Execute a command with sudo privileges and check the exit code.
    """
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E"] + command)
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        return True
    else:
        return False

def check_slim_conf():
    """
    Check whether slim.conf exists and is writable by root.
    """
    return run_with_sudo(["test", "-w", slim_config_file])

def check_autologin():
    """
    Check whether autologin is already enabled.
    """
    return run_with_sudo(["grep", "^auto_login[[:space:]]*yes", slim_config_file])

def disable_autologin():
    """
    Disable automatic login and remove default user.
    """
    print("Removing default user")
    try:
        remove_default_user()
    except:
        pass
    print("Disabling automatic login")
    if not check_slim_conf():
        return False
    if not run_with_sudo(["sed", "-i", "''", "-e", "s/^auto_login.*/#auto_login no/g", slim_config_file]):
        return False
    QMessageBox.information(None, "Automatic login", "Automatic login has been disabled.")
    return True

def get_default_user():
    """
    Get default user from slim.conf.
    """
    print("Getting default user")
    if not check_slim_conf():
        return False
    p = QProcess()
    p.setProgram("sudo")
    p.setArguments(["-A", "-E", "grep", "^default_user", slim_config_file])
    print(p.program() + " " + " ".join(p.arguments()))
    p.start()
    p.waitForFinished()
    if p.exitCode() == 0:
        return p.readAllStandardOutput().data().decode("utf-8").split()[1]
    else:
        return False

def remove_default_user():
    """
    Remove default user from slim.conf.
    """
    print("Removing default user")
    if not check_slim_conf():
        return False
    if not run_with_sudo(["sed", "-i", "''", "-e", "s/^default_user.*/#default_user/g", slim_config_file]):
        return False
    return True

def enable_autologin(user):
    """
    Enable automatic login for user.
    """
    print("Enabling automatic login for user " + user)
    if not check_slim_conf():
        QMessageBox.error(None, "Automatic login", "File slim.conf is not writable by root.")
        return False

    if run_with_sudo(["grep", "^auto_login", slim_config_file]):
        command = ["sed", "-i", "''", "-e", "s/^auto_login.*/auto_login yes/g", slim_config_file]
    else:
        command = ["sed", "-i", "''", "-e", "s/^#auto_login.*/auto_login yes/g", slim_config_file]

    if not run_with_sudo(command):
        QMessageBox.warning(None, "Automatic login", "Automatic login could not be enabled for user " + user + ".")
        return False

    if run_with_sudo(["grep", "^default_user", slim_config_file]):
        command = ["sed", "-i", "''", "-e", "s/^default_user.*/default_user " + user + "/g", slim_config_file]
    else:
        command = ["sed", "-i", "''", "-e", "s/^#default_user.*/default_user " + user + "/g", slim_config_file]

    if not run_with_sudo(command):
        QMessageBox.warning(None, "Automatic login", "Automatic login could not be enabled for user " + user + ".")
        return False

    QMessageBox.information(None, "Automatic login", "Automatic login has been enabled for user " + user + ".")
    return True


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Check if autologin is already enabled
    if check_autologin():
        # Get default user
        user = get_default_user()
        print("Default user: " + user)
        # Disable autologin
        if disable_autologin():
            QMessageBox.information(None, "Automatic login", "Automatic login has been disabled.")
            sys.exit(0)
    else:    
        if len(sys.argv) < 2:
            QMessageBox.warning(None, "Automatic login", "Usage: %s <username>" % sys.argv[0])
            sys.exit(1)

        user = sys.argv[1]
        enable_autologin(user)

        sys.exit(0)
