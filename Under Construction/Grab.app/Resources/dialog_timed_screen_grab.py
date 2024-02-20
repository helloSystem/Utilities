import os
import sys
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QColor
from PyQt5.QtWidgets import QDialog, QShortcut, QGraphicsDropShadowEffect
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_timed_screen_grab_ui import Ui_TimedScreenGrabDialog


class TimedScreenGrabDialog(QDialog):
    timer_dialog_signal_quit = pyqtSignal()
    timer_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None, timer=None):
        super(TimedScreenGrabDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)
        self.sec = int(timer / 1000)
        self.ui = Ui_TimedScreenGrabDialog()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        if self.sec > 1:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} seconds")
        else:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} second")
        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.timed_dialog_quit)
        self.ui.button_start_timer.clicked.connect(self.timed_dialog_start)

        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.timed_dialog_quit)

        self.adjustSize()
        self.setFixedSize(self.size())

    def timed_dialog_quit(self):
        self.timer_dialog_signal_quit.emit()

    def timed_dialog_start(self):
        self.timer_dialog_signal_start.emit()

