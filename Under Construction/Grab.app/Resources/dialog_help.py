import os

from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtWidgets import QDialog, QShortcut, qApp
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from dialog_help_ui import Ui_HelpDialog


class HelpDialog(QDialog):
    screen_dialog_signal_quit = pyqtSignal()
    screen_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.ui = Ui_HelpDialog()
        self.ui.setupUi(self)
        self.setup()

    def setup(self):

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.open()
        self.setFocus()

    def open(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as file:
            text = file.read()
        self.ui.textBrowser.setMarkdown(text)



