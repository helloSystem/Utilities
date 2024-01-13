import os

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_screen_grab_ui import Ui_ScreenGrab


class ScreenGrabDialog(QDialog):
    screen_dialog_signal_quit = pyqtSignal()

    def __init__(self, parent=None):
        super(ScreenGrabDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)
        self.ui = Ui_ScreenGrab()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.cancel_dialog)

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

    def cancel_dialog(self):
        self.screen_dialog_signal_quit.emit()


