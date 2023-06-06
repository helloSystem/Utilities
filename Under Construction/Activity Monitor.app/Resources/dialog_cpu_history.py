import os
import signal

from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_cpu_history_ui import Ui_CPUHistory


class CPUHistory(QWidget, Ui_CPUHistory):
    process_signal_quit = pyqtSignal()
    process_signal_kill = pyqtSignal()

    def __init__(self, parent=None, process=None):
        super(CPUHistory, self).__init__(parent)
        self.setupUi(self)
        self.process = process

        # when you want to destroy the dialog set this to True
        self.have_to_close = False

    def closeEvent(self, evnt):
        if self.have_to_close:
            super(CPUHistory, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.hide()
