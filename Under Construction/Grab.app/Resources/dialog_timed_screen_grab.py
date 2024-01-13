import os

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_timed_screen_grab_ui import Ui_TimedScreenGrab


class TimedScreenGrabDialog(QDialog):
    timer_dialog_signal_quit = pyqtSignal()
    timer_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None, timer=None):
        super(TimedScreenGrabDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)
        self.sec = int(timer / 1000)
        self.ui = Ui_TimedScreenGrab()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        if self.sec > 1:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} seconds")
        else:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} second")
        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.cancel_dialog)
        self.ui.button_start_timer.clicked.connect(self.start_timer_dialog)

    def cancel_dialog(self):
        self.timer_dialog_signal_quit.emit()

    def start_timer_dialog(self):
        self.timer_dialog_signal_start.emit()

