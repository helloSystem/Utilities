#!/usr/bin/env python3
# Unfortunately python3 does not seem to work on FreeBSD

# Welcome Wizard
# Copyright (c) 2020-2021, Simon Peter <probono@puredarwin.org>
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

class Wizard(QtWidgets.QWizard, object):
    def __init__(self):
        print("Preparing wizard")
        super().__init__()

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)
        # self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(os.path.dirname(__file__) + '/Welcome.png'))
        self.setOption(QtWidgets.QWizard.ExtendedWatermarkPixmap, True) # Extend WatermarkPixmap all the way down to the window's edge; https://doc.qt.io/qt-5/qwizard.html#wizard-look-and-feel

        self.setWindowTitle("Welcome")
        self.setFixedSize(600, 400)

        self.setSubTitleFormat(QtCore.Qt.PlainText)
        # Qt 5.14+ also have an option for Markdown
        # AttributeError: type object 'Qt' has no attribute 'MarkdownText'
        # FIXME: Make it work
        with open(os.path.dirname(__file__) + '/content.en.md', 'r') as file:
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
                open(done_file, 'a').close()

if __name__ == "__main__":
    # The following are needed here so that these thingss get loaded while the Intro is running, and provide for a smooth transition out
    subprocess.Popen(["/System/Menu.AppDir/usr/bin/menubar"], start_new_session=True) # FIXME: Remove the need for this
    subprocess.Popen(["/usr/local/bin/gmenudbusmenuproxy"], start_new_session=True) # FIXME: Remove the need for this
    subprocess.Popen(["/System/Filer.AppDir/AppRun", "--desktop"], start_new_session=True) # FIXME: Remove the need for this
    subprocess.Popen(["/System/Dock.AppDir/usr/bin/cyber-dock"], start_new_session=True) # FIXME: Remove the need for this
    wizard = Wizard()
    wizard.show()
    sys.exit(app.exec_())
