import os
import signal

from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_about_ui import Ui_AboutDialog


class CPUHistory(QWidget, Ui_AboutDialog):
    process_signal_quit = pyqtSignal()
    process_signal_kill = pyqtSignal()

    def __init__(self, parent=None, process=None):
        super(CPUHistory, self).__init__(parent)
        self.process = process

    def close(self):
        self.hide()
