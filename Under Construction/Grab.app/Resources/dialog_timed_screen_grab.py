import os

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtWidgets import QDialog, QShortcut

from dialog_timed_screen_grab_ui import Ui_TimedScreenGrabDialog


class TimedScreenGrabDialog(QDialog):
    timer_dialog_signal_quit = pyqtSignal()
    timer_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None, timer=None):
        super(TimedScreenGrabDialog, self).__init__(parent)

        self.sec = int(timer / 1000)
        self.ui = Ui_TimedScreenGrabDialog()
        self.ui.setupUi(self)

        if self.sec > 1:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} seconds")
        else:
            self.ui.Label.setText(self.ui.Label.text() % f"{self.sec} second")

        self.setupCustomUi()
        self.connectSignalsSlots()
        self.initialState()

    def setupCustomUi(self):
        self.setWindowFlags(
            Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint
        )
        self.ui.icon.setPixmap(
            QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")).scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

    def connectSignalsSlots(self):
        self.ui.button_cancel.clicked.connect(self.timed_dialog_quit)
        self.ui.button_start_timer.clicked.connect(self.timed_dialog_start)

    def initialState(self):
        self.adjustSize()
        self.setFixedSize(self.size())

        self.setFocus()

    def timed_dialog_quit(self):
        self.timer_dialog_signal_quit.emit()

    def timed_dialog_start(self):
        self.timer_dialog_signal_start.emit()
