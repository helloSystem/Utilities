#!/usr/bin/env python3.7

# Based on https://stackoverflow.com/a/41751956

import os, sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QProcess, QTextCodec
from PyQt5.QtGui import QTextCursor, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QAction, QMessageBox, QMainWindow


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

        self.setFixedWidth(1024)
        self.setFixedHeight(600)

        self.plainTextEdit = QPlainTextEdit()

        font = self.font()
        font.setPointSize(9)
        # font.setFamily("monospace")
        self.plainTextEdit.setFont(font)

        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setMaximumBlockCount(10000)  # limit console to 10000 lines

        self._cursor_output = self.plainTextEdit.textCursor()

        self.setCentralWidget(self.plainTextEdit)

    @pyqtSlot(str)
    def append_output(self, text):
        self._cursor_output.insertText(text)
        self.scroll_to_last_line()

    def scroll_to_last_line(self):
        cursor = self.plainTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.Up if cursor.atBlockStart() else
                            QTextCursor.StartOfLine)
        self.plainTextEdit.setTextCursor(cursor)

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

app = QApplication(sys.argv)

reader = ProcessOutputReader()
console = MyConsole()
reader.produce_output.connect(console.append_output)
reader.start('sh', ['-c', "tail -n 5 -f /var/log/*.log"])

console.show()
app.exec_()
