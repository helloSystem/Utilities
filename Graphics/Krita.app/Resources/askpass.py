#!/usr/bin/env python3.7


# man sudo(8)
#      -A, --askpass
#                  Normally, if sudo requires a password, it will read it from
#                  the user's terminal.  If the -A (askpass) option is
#                  specified, a (possibly graphical) helper program is executed
#                  to read the user's password and output the password to the
#                  standard output.  If the SUDO_ASKPASS environment variable is
#                  set, it specifies the path to the helper program.  Otherwise,
#                  if sudo.conf(5) contains a line specifying the askpass
#                  program, that value will be used.  For example:
#
#                      # Path to askpass helper program
#                      Path askpass /usr/X11R6/bin/ssh-askpass
#
#                  If no askpass program is available, sudo will exit with an
#                  error.

import os
from PyQt5 import QtWidgets

text = "Password"

# SUDO_ASKPASS_TEXT is a non-standard environment variable.
# If it is set, we show its value in the dialog as a way for the program
# requesting root rights to let the user know the reason for doing so.
if os.environ.get('SUDO_ASKPASS_TEXT') is not None:
    text = os.environ.get('SUDO_ASKPASS_TEXT') + "\n\n" + text

app = QtWidgets.QApplication([])
password, ok = QtWidgets.QInputDialog.getText(None, "sudo", text, QtWidgets.QLineEdit.Password)
if ok:
    print(password)
app.exit(0)
