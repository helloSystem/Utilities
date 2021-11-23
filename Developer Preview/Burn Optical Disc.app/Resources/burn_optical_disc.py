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
        
        self.process = QtCore.QProcess()
        
        if not os.path.exists("/dev/cd0"):
            self.showFatalError(tr("Optical disc drive not found.")) # TODO: Be more elaborate and check for burning capabilities
            
        if len(sys.argv) < 2:
            filedialog = QtWidgets.QFileDialog()
            filedialog.setDefaultSuffix("iso")
            filedialog.setNameFilter(tr("Optical disc images (*.iso *.img *.raw);;All files (*.*)"))
            filename = None
            if filedialog.exec_():
                filename = filedialog.selectedFiles()[0]
            if not filename:
                exit(0)
            else:
                self.image = filename
        else:
            self.image = sys.argv[1]
        print("self.image: %s" % self.image)
        self.iconfile = None
        self.file_symlink_resolved = os.path.join(sys.path[0], os.path.basename(os.path.realpath(sys.argv[0])))
        for file in os.listdir(os.path.dirname(self.file_symlink_resolved)):
            if file.endswith(".png"):
                self.iconfile = os.path.dirname(self.file_symlink_resolved) + "/" + file
                break
        self.disk_image_iconfile = self.iconfile # os.path.dirname(self.file_symlink_resolved) + "/discimage.png"

        self.prepare_progress_window()
        
        if not os.path.exists(self.image):
            self.showFatalError(tr("%s does not exist" % self.image))
        
        self.burn(self.image)
        
    def burn(self, image_file):          
        # Useful during development:
        # self.process.setProgram(os.path.dirname(__file__) + "/" + "mock_growisofs")
        self.process.setProgram("growisofs")
        
        self.process.setArguments(["-dvd-compat", "-Z", "/dev/cd0=" + image_file])

        print(self.process.program() + " " + " ".join(self.process.arguments()))

        codec = QtCore.QTextCodec.codecForLocale()
        self.process._decoder_stdout = codec.makeDecoder()
        self.process._decoder_stderr = codec.makeDecoder()
        self.process.readyReadStandardOutput.connect(self._ready_read_standard_output)
        self.process.readyReadStandardError.connect(self._ready_read_standard_error)
        self.process.start()

        while True:
            QtWidgets.QApplication.processEvents()  # Important trick so that the app stays responsive without the need for threading!
            time.sleep(0.001)

    def _ready_read_standard_output(self):
        text = self.process._decoder_stdout.toUnicode(self.process.readAllStandardOutput())
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            print(line)
            self.details_textedit.append(line)
            # Only begin showing the progress bar once the writing has actually started
            # so that if errors occur, only the error message is shown and not a
            # progress bar and an error message
            if line.startswith("Executing"):
                # Burning is starting
                self.progress_window.open()
                self.progress.setMaximum(0) # Indeterminate
            elif "%)" in line:
                # Progress reported from burning
                self.progress_window.open()
                total = int(line.split(" ")[0].split("/")[1])
                written = int(line.split("/")[0])
                self.progress.setMaximum(total)
                self.progress.setValue(written)
            elif line.endswith("closing disc"):
                # Burning complete
                self.progress_window.hide()
                timer = QtCore.QTimer()
                timer.singleShot(1500, self.progress_window.hide)
                # TODO: Verify that the checksum of the disc matches the checksum of the ISO
                self.eject()
                self.showInfo(tr("The disc has been written successfully."))
                sys.exit(0)
            elif "(100.0%) " in line:
                # Burning almost complete
                self.progress.setMaximum(0) # Indeterminate

    def _ready_read_standard_error(self):
        text = self.process._decoder_stdout.toUnicode(self.process.readAllStandardError())
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line:
                print(line)
                # print(self.process.ProcessState())
                try:
                    self.details_textedit.append(line)
                except:
                    pass
                    
                if "Resource temporarily unavailable" in line or "unable to stat" in line:
                    self.showFatalError(tr("Device not ready. Please try again later."))
                if "already carries" in line:
                    self.process.terminate()
                    if(self.showQuestion(tr("The disc in the drive is not blank. Do you want to erase it?"))):  
                        self.blank()
                    else:
                        sys.exit(0)           
                elif self.process.ProcessState == 0:
                    # The process is not running, so show an error
                    self.showFatalError(line)
                elif ":-[" in line or ":-(" in line:
                    self.showFatalError(line)
                elif "remaining" not in line and line.endswith("%"):
                    # Progress reported from blanking
                    self.progress_window.open()
                    total = 100
                    try:
                        # There are weird special characters in the output; filter them out
                        # FIXME: This is not quite working yet, why?
                        filtered_line = ""
                        for character in line:
                            if character.isnumeric():
                                filtered_line = filtered_line + character
                        blanked = int(filtered_line.split(".")[0] * 100)
                        self.progress.setMaximum(total)
                        self.progress.setValue(blanked)
                    except:
                        print("Blanking...")
                        self.progress.setMaximum(0) # Indeterminate
                if "blanking" in line:
                    self.progress_window.open()
                if "remaining" not in line and line.endswith("100.0%"):
                    # Blanking complete
                    print("Blanking complete")
                    # The following does not work; FIXME: Why?
                    # self.progress.setMaximum(0) # Indeterminate
                    # timer = QtCore.QTimer()
                    # timer.singleShot(500, lambda: self.burn(self.image))
                    # So do this instead:
                    self.progress_window.hide()
                    timer = QtCore.QTimer()
                    timer.singleShot(500, lambda: self.eject())
                    self.showInfo(tr("The disc has been erased successfully."))
                    sys.exit(0)
               
    def blank(self):
        self.process.setProgram("sudo")
        self.process.setArguments(["-A", "-E", "dvd+rw-format", "-blank", "/dev/cd0"])
        codec = QtCore.QTextCodec.codecForLocale()
        self.process._decoder_stdout = codec.makeDecoder()
        self.process._decoder_stderr = codec.makeDecoder()
        self.process.readyReadStandardOutput.connect(self._ready_read_standard_output)
        self.process.readyReadStandardError.connect(self._ready_read_standard_error)
        self.process.start()
        self.process.waitForStarted()
        print("Blanking disc...")
        self.label.setText(tr("Erasing disc..."))
        while True:
            QtWidgets.QApplication.processEvents()  # Important trick so that the app stays responsive without the need for threading!
            time.sleep(0.001)
            
    def eject(self):
        p = QtCore.QProcess()
        p.setProgram("eject")
        p.setArguments(["/dev/cd0"])
        p.startDetached()

    def showQuestion(self, text):
        result = QtWidgets.QMessageBox.question(None, " ", text)
        if result == QtWidgets.QMessageBox.Yes:
            return(True)
        else:
            return(False)

        return(answer)

    def showInfo(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(" ")
        msg.setText(text)
        msg.exec_()
            
    def showNonfatalError(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle(" ")
        msg.setText(text)
        msg.exec_()

    def showFatalError(self, text):
        try:
            self.process.terminate()
            self.eject()
            self.progress_window.hide()
        except:
            pass
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle(" ")
        msg.setText(text)
        msg.exec_()
        sys.exit(1)

    def prepare_progress_window(self):
        label = tr("Writing %s...") % os.path.basename(self.image)
        self.progress_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, " ", label, QtWidgets.QMessageBox.NoButton)
        self.progress_window.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False) # Why does KWin still show it, even if unclickable?
        self.progress_window.setStyleSheet("QDialogButtonBox,QTextEdit{min-width: 500px; } QLabel{min-height: 50px;} QProgressBar{min-width: 410px;}") # FIXME: Do this without hardcoding 410px
        self.progress_window.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.progress_window.setIconPixmap(QtGui.QPixmap(self.disk_image_iconfile))
        self.progress_window.layout().setAlignment(QtCore.Qt.AlignTop)
        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximum(0) # Indeterminate
        self.progress.setMinimum(0)

        self.progress_window.setDetailedText(" ") # Brings it into existence
        self.label = self.progress_window.findChildren(QtWidgets.QLabel)[1]
        self.details_textedit = self.progress_window.findChild(QtWidgets.QTextEdit)
        
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
