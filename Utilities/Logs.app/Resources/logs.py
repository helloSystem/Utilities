#!/usr/bin/env python3

# Based on https://stackoverflow.com/a/41751956

import os, sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QProcess, QTextCodec
from PyQt5.QtGui import QTextCursor, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QTextEdit, QAction, QMessageBox, QMainWindow


class ProcessOutputReader(QProcess):
    produce_output = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setProcessChannelMode(QProcess.MergedChannels)
        codec = QTextCodec.codecForLocale()
        self._decoder_stdout = codec.makeDecoder()
        self.readyReadStandardOutput.connect(self._ready_read_standard_output)


    @pyqtSlot()
    def _ready_read_standard_output(self):
        raw_bytes = self.readAllStandardOutput()
        text = self._decoder_stdout.toUnicode(raw_bytes)
        self.produce_output.emit(text)

class MyConsole(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Logs")

        self._showMenu()

        self.setMinimumWidth(1024)
        self.setMinimumHeight(600)

        self.textEdit = QTextEdit()

        font = self.font()
        font.setPointSize(9)
        # font.setFamily("monospace")
        self.textEdit.setFont(font)

        self.textEdit.setReadOnly(True)

        self._cursor_output = self.textEdit.textCursor()

        self.setCentralWidget(self.textEdit)

    @pyqtSlot(str)
    def append_output(self, text):
        lines = text.split("\n")
        for line in lines:
            if line == "":
                continue
            if line.startswith("==>"):
                line = "<br><b>" + line + "</b>"
            red_words = ["error", "fail", "kill", "slow"]
            red = False
            for red_word in red_words:
                if red_word in line.lower():
                    red = True
            if red == True:
                self._cursor_output.insertHtml("<span style='color:red'>" + line + "</span><br>")
                # Also send a notification on red lines
                try:
                    p = QProcess()
                    p.setProgram("notify-send")
                    p.setArguments([line])
                    p.startDetached()
                except:
                    continue
            else:
                self._cursor_output.insertHtml(line + "<br>")
        self.scroll_to_last_line()

    def scroll_to_last_line(self):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.Up if cursor.atBlockStart() else
                            QTextCursor.StartOfLine)
        self.textEdit.setTextCursor(cursor)

    def _showMenu(self):
        exitAct = QAction('&Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.quit)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        aboutAct = QAction('&About', self)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAct)

    def _showAbout(self):
        print("showDialog")
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Logs.png"))
        # msg.setIconPixmap(QIcon.fromTheme("logviewer").pixmap(128))
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
                with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Logs</h3>")
        msg.setInformativeText(
            "A simple utility to view log files<br>in <code>/var/log</code><br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

# Simple singleton:
# Ensure that only one instance of this application is running by trying to kill the other ones
p = QProcess()
p.setProgram("pkill")
p.setArguments(["-f", os.path.abspath(__file__)])
cmd = p.program() + " " + " ".join(p.arguments())
print(cmd)
p.start()
p.waitForFinished()
    
app = QApplication(sys.argv)

reader = ProcessOutputReader()
console = MyConsole()
reader.produce_output.connect(console.append_output)
reader.start('sh', ['-c', "tail -n 10 -f /var/log/*.log"])

console.show()
app.exec_()
