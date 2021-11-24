#!/usr/bin/env python3


# Copyright (c) 2021, Simon Peter <probono@puredarwin.org>
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


import os, sys
import re

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except:
    print("Could not import PyQt5. On FreeBSD, sudo pkg install py37-qt5-widgets")


class EnergySavingsManager(object):

    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)
        
        self.showTODO()

        # Red current settings
        p = QtCore.QProcess()
        p.setProgram("xset")
        p.setArguments(["q"])
        print(p.program() + " " + " ".join(p.arguments()))
        p.start()
        p.waitForFinished()
        lines = str(p.readAllStandardOutput(), 'utf-8').strip().split("\n")
        for line in lines:
            if "timeout" in line:
                print(line) #   timeout:  0    cycle:  0
                line = line.replace(" ", "")
                print(line)
                value = re.findall('timeout:[0-9]*', line)
                print(value)
                value = int(value[0].split(":")[1])
                print(value)

        # Window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('Energy Saving')
        self.window.setMinimumWidth(450)
        self.window.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                        QtWidgets.QSizePolicy.MinimumExpanding))
        self.window.closeEvent = self.quit
        self.layout = QtWidgets.QVBoxLayout()
        
        # Menu
        self._showMenu()

        # Horizontal layout inside the box
        hlayout = QtWidgets.QHBoxLayout()

        l = QtWidgets.QLabel()
        l.setText("10 Minutes")
        hlayout.addWidget(l)

        # Slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(7)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(2) # Ticks Below
        self.slider.setValue(value / 10 / 60)
        if value == 0:
            self.slider.setValue(7)
        self.slider.setToolTip(str(self.slider.value() * 10))
        if self.slider.value() == 7:
            self.slider.setToolTip("Never")
        self.slider.valueChanged.connect(self.onSliderValueChanged)
        self.slider.sliderReleased.connect(self.persist)

        hlayout.addWidget(self.slider)

        l = QtWidgets.QLabel()
        l.setText("Never")
        hlayout.addWidget(l)

        self.box = QtWidgets.QGroupBox()
        self.box.setLayout(hlayout)

        self.box.setTitle("Turn display off after")

        self.layout.addWidget(self.box)

        # Set window icon if one exists in Resources/ with the same name as the main PyQt file plus the png extension
        candidate = os.path.dirname(__file__) + "/Resources/" + QtCore.QFileInfo(str(__file__)).baseName() + ".png"
        if os.path.exists(candidate):
            print(candidate)
            self.window.setWindowIcon(QtGui.QIcon(candidate))

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.window.setCentralWidget(widget)
        
        self.window.show()

        sys.exit(self.app.exec_())

    def onSliderValueChanged(self):
        print("onSliderValueChanged triggered")
        self.slider.setToolTip(str(self.slider.value() * 10))
        if self.slider.value() == 7:
            self.slider.setToolTip("Never")

        p = QtCore.QProcess()
        p.setProgram("xset")

        # Set new value
        if self.slider.value() == 7:
            seconds = 0
        else:
            seconds = self.slider.value() * 10 * 60
        p.setArguments(["s", str(seconds), str(seconds)])
        p.startDetached()

        # Print results
        p.setArguments(["q"])
        p.startDetached()

    def persist(self):

        print("persist called")
        # Persist new value
        if self.slider.value() == 7:
            minutes = 0
        else:
            minutes = self.slider.value() * 10
        p = QtCore.QProcess()
        p.setProgram("sudo")
        p.setArguments(["-A", "-E", os.path.dirname(__file__) + "/set-10-monitor.sh", str(minutes)])
        p.startDetached()

        # Print results
        p.setProgram("xset")
        p.setArguments(["q"])
        p.startDetached()

    def quit(self, event):
        sys.exit(0)

    def _showMenu(self):
        exitAct = QtWidgets.QAction('&Quit', self.window)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.QApplication.quit)
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
        msg.setIconPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Energy Saving.png").scaledToWidth(64, QtCore.Qt.SmoothTransformation))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Energy Saving</h3>")
        msg.setInformativeText(
            "A simple preferences application to modify Energy Saving using <a href='https://www.freebsd.org/cgi/man.cgi?xset'>xset</a> and <a href='file:///usr/local/etc/X11/xorg.conf.d/10-monitor.conf'>/usr/local/etc/X11/xorg.conf.d/10-monitor.conf</a><br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

    def showTODO(self, detailed_text=""):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Developer Preview")
        msg.setText("This application is a preview for developers.<br>It is not fully functional yet.")
        msg.setDetailedText("Please see https://github.com/helloSystem/Utilities if you would like to contribute.\n\n" + detailed_text)
        msg.exec()  


if __name__ == "__main__":
    EnergySavingsManager()
    
