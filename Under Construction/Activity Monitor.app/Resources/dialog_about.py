import os
import signal

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_about_ui import Ui_AboutDialog


class AboutDialog(QDialog):
    process_signal_quit = pyqtSignal()
    process_signal_kill = pyqtSignal()

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
