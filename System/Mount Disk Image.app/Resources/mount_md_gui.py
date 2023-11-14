#!/usr/bin/env python3

import os, sys, socket, subprocess, time

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "")
def tr(input):
    return tstr.tr(input)

from PyQt5 import QtWidgets, QtGui, QtCore


class GUI(object):

    def __init__(self):

        app = QtWidgets.QApplication(sys.argv)
            
        if len(sys.argv) < 2:
            filedialog = QtWidgets.QFileDialog()
            filedialog.setDefaultSuffix("iso")
            filedialog.setNameFilter(tr("Disk images (*.iso *.img *.ufs *.uzip);;All files (*.*)"))
            filename = None
            if filedialog.exec_():
                filename = filedialog.selectedFiles()[0]
            if not filename:
                exit(0)
            else:
                self.image = filename
        else:
            self.image = sys.argv[1]

        self.iconfile = None
        self.device = None
        self.file_symlink_resolved = os.path.join(sys.path[0], os.path.basename(os.path.realpath(sys.argv[0])))
        for file in os.listdir(os.path.dirname(self.file_symlink_resolved)):
            if file.endswith(".png"):
                self.iconfile = os.path.dirname(self.file_symlink_resolved) + "/" + file
                break
        self.disk_image_iconfile = os.path.dirname(self.file_symlink_resolved) + "/diskimage.png"

        self.prepare_progress_window()
        
        if not os.path.exists(self.image):
            self.showFatalError(tr("%s does not exist" % self.image))
            
        self.process = QtCore.QProcess()
        self.process.setProgram("mount_md") # chmod 6755 /sbin/mdconfig so that it runs as root:wheel
        self.process.setArguments([self.image])

        print(self.process.program() + " " + " ".join(self.process.arguments()))
 
        codec = QtCore.QTextCodec.codecForLocale()
        self.process._decoder_stdout = codec.makeDecoder()
        self.process._decoder_stderr = codec.makeDecoder()
        # Parse the output to extract the device name;
        # one of the lines in the output has the format:
        # Attached disk image to /dev/md1
        # We need to extract the /dev/md1 part
        self.process.readyReadStandardOutput.connect(self._ready_read_standard_output)
        self.process.readyReadStandardError.connect(self._ready_read_standard_error)
        self.process.start()

        while True:
            QtWidgets.QApplication.processEvents()  # Important trick so that the app stays responsive without the need for threading!

    def _periodically_check_for_mounted_device(self):
        print("Periodically checking for mounted device")
        for v in QtCore.QStorageInfo.mountedVolumes():
            # QByteArray -> str
            device = v.device().data().decode()
            if device.startswith(self.device + "s") or device.startswith(self.device + "p") or device.startswith(self.device + "."):
                self.timer.stop()
                self.progress_window.hide()
                self.process.waitForFinished()
                sys.exit(0)


    def _wait_for_hide_progress_window(self):
        print("Waiting for hide progress window")
        # Set a timer to periodically check if the device is mounted
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._periodically_check_for_mounted_device)
        self.timer.start(1000) # 1 second

    def _ready_read_standard_output(self):
        text = self.process._decoder_stdout.toUnicode(self.process.readAllStandardOutput())
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            print(line)
            if line.startswith("Attaching"):
                self.progress_window.open()
                self.progress_window.show()
            if line.startswith("Attached"):
                self.device = line.split(" ")[-1]
                print("Device: " + self.device)
                self._wait_for_hide_progress_window()
            if line.startswith("Removed"):
                self.process.waitForFinished()
                sys.exit(0)

    def _ready_read_standard_error(self):
        pass

    def showNonfatalError(self, text):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(text)
            msg.exec_()

    def showFatalError(self, text):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(text)
            msg.exec_()
            sys.exit(1)

    def prepare_progress_window(self):
        label = os.path.basename(self.image)        
        self.progress_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, " ", label, QtWidgets.QMessageBox.NoButton)
        self.progress_window.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False) # Why does KWin still show it, even if unclickable?
        self.progress_window.setStyleSheet("QDialogButtonBox,QTextEdit{min-width: 500px; } QLabel{min-height: 50px;} QProgressBar{min-width: 410px;}") # FIXME: Do this without hardcoding 410px
        self.progress_window.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.progress_window.setIconPixmap(QtGui.QPixmap(self.disk_image_iconfile))
        self.progress_window.layout().setAlignment(QtCore.Qt.AlignTop)
        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximum(0) # Indeterminate
        self.progress.setMinimum(0)

        self.progress.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add the progress bar at the bottom (last row + 1) and first column with column span
        # self.progress_window.layout().addWidget(self.progress, self.progress_window.layout().rowCount(), 0, 1, self.progress_window.layout().columnCount(), QtCore.Qt.AlignCenter)
        self.progress_window.layout().addWidget(self.progress, 1, 1, 1, self.progress_window.layout().columnCount(),
                                  QtCore.Qt.AlignCenter)

        self.progress_window.layout().addWidget(QtWidgets.QLabel(), 1, 1, 1, self.progress_window.layout().columnCount(),
                                  QtCore.Qt.AlignCenter)


    def quit(self):
            sys.exit(0)


if __name__ == "__main__":

    g = GUI()
