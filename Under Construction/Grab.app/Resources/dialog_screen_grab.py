import os

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFocusEvent
from PyQt5.QtWidgets import QDialog, QShortcut

from dialog_screen_grab_ui import Ui_ScreenGrabDialog


class ScreenGrabDialog(QDialog):
    screen_dialog_signal_quit = pyqtSignal()
    screen_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(ScreenGrabDialog, self).__init__(parent)

        self.ui = Ui_ScreenGrabDialog()
        self.ui.setupUi(self)

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
        self.ui.button_cancel.clicked.connect(self.screen_dialog_quit)

    def initialState(self):
        self.adjustSize()
        self.setFixedSize(self.size())

        self.setFocus()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if self.hasFocus() or self.ui.button_cancel.hasFocus():
            event.accept()
        else:
            event.accept()
            self.screen_dialog_signal_start.emit()
            self.close()

    def screen_dialog_quit(self):
        self.ui.button_cancel.setFocus(True)
        self.screen_dialog_signal_quit.emit()
        self.close()
