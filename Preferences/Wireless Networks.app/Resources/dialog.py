#!/usr/bin/env python3

import sys
import subprocess

from PyQt5 import QtWidgets, QtGui, QtCore

def show_message(message="Text would go here"):
    reply = QtWidgets.QMessageBox.warning(
        None,
        " ",
        message,
        QtWidgets.QMessageBox.Cancel
    )

class Dialog(QtWidgets.QInputDialog):

    def __init__(self):
        super().__init__()

        # Get list of WLAN devices in FreeBSD
        # sysctl -b net.wlan.devices
        items = str(subprocess.check_output(["sysctl", "-b", "net.wlan.devices"]), "utf-8").split(" ")

        if(len(items) == 0):
            show_message("No wireless devices found.")
            exit(0)
        elif(len(items) == 1):
            print(items[0])
        else:
            dialog = QtWidgets.QInputDialog(
                None, QtCore.Qt.WindowFlags())
            dialog.setWindowTitle(" ")
            dialog.setLabelText("Select a device:")
            dialog.setComboBoxItems(items)
            dialog.setComboBoxEditable(True)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                print(dialog.textValue())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    if sys.argv.pop() == "warning":
        show_message("No wireless devices found.")
    else:
        Dialog()

