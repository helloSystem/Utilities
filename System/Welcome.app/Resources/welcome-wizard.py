#!/usr/bin/env python3

# Welcome Wizard
# Copyright (c) 2020-21, Simon Peter <probono@puredarwin.org>
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


import sys, os, re, socket, subprocess
import shutil
from datetime import datetime

from PyQt5 import QtWidgets, QtGui, QtCore # pkg install py37-qt5-widgets


app = QtWidgets.QApplication(sys.argv)

def show_message(message="Text would go here"):
    reply = QtWidgets.QMessageBox.warning(
        None,
        " ",
        message,
        QtWidgets.QMessageBox.Default
    )
        

class Wizard(QtWidgets.QWizard, object):
    def __init__(self):
        print("Preparing wizard")
        super().__init__()

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)
        # self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(os.path.dirname(__file__) + '/Welcome.png'))
        self.setOption(QtWidgets.QWizard.ExtendedWatermarkPixmap, True) # Extend WatermarkPixmap all the way down to the window's edge; https://doc.qt.io/qt-5/qwizard.html#wizard-look-and-feel

        self.setWindowTitle("Welcome")
        self.setFixedSize(600, 400)

        self.setOption(QtWidgets.QWizard.NoCancelButton, True)

        self.setSubTitleFormat(QtCore.Qt.PlainText)
        # Qt 5.14+ also have an option for Markdown
        # AttributeError: type object 'Qt' has no attribute 'MarkdownText'
        # FIXME: Make it work

        md_file = os.path.dirname(__file__) + '/content.en.md'
        # Find localized md file if it exists
        cmd = 'env | grep "^LANG=" | cut -d "=" -f 2 | cut -d "_" -f 1 | cut -d "." -f 1'
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode("utf-8").strip()
        if os.path.exists(os.path.dirname(__file__) + '/content.' + output + '.md'):
            md_file = os.path.dirname(__file__) + '/content.' + output + '.md'

        with open(md_file, 'r') as file:
            sections = file.read().split("#")

        for section in sections[1:]:
            self.addPage(IntroPage(section))


class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, section):

        print("Preparing IntroPage")
        super().__init__()

        # print(section)
        all_lines = section.split("\n")
        # print(all_lines)
        lines = []
        for line in all_lines:
            if line != "":
                lines.append(line)

        self.setTitle(lines[0])
        self.setSubTitle("\n\n".join(lines[1:]))

        layout = QtWidgets.QVBoxLayout(self)

    def initializePage(self):
        print("Displaying Page")
        if self.isFinalPage():
            # Write a file that start-hello can check to not start this again for this user
            done_file = os.path.expanduser("~/.config/hello/.helloSetupDone")
            print(done_file)
            if os.path.exists(done_file):
                os.utime(done_file, None)
            else:
                try:
                    os.makedirs(os.path.expanduser("~/.config/hello/"))
                except FileExistsError:
                    pass
                open(done_file, 'a').close()
            sys.exit()

if __name__ == "__main__":
    if os.getenv("VIRTUAL_MACHINE") is not None:
        show_message("It appears that this system is running inside a virtual machine.\n\nThis system has been optimized to run as a desktop system on real hardware.\n\nPlease consider running it on real hardware. A Live ISO is provided that can be written to a removable USB storage device to act as a boot medium.")
        cmd = subprocess.run(['sysctl', 'machdep.bootmethod'], capture_output=True)
        print(cmd.stdout)
        if b'UEFI' in cmd.stdout:
            print('Running in EFI mode')
        else:
            show_message("It appears that this virtual machine is not running in EFI mode.\n\nSome features, such as persisting keyboard and language settings, will not be available.\n\nPlease consider configuring the virtual machine to run in EFI mode.")
    wizard = Wizard()
    wizard.show()
    sys.exit(app.exec_())
