import os
import sys

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFocusEvent
from PyQt5.QtWidgets import QDialog, QShortcut

from dialog_screen_grab_ui import Ui_ScreenGrabDialog


class ScreenGrabDialog(QDialog):
    screen_dialog_signal_quit = pyqtSignal()
    screen_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(ScreenGrabDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.ui = Ui_ScreenGrabDialog()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.screen_dialog_quit)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.screen_dialog_quit)

        self.setFocus()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if self.hasFocus() or self.ui.button_cancel.hasFocus():
            event.accept()
        else:
            event.accept()
            self.screen_dialog_signal_start.emit()
            self.close()

    def screen_dialog_quit(self):
        self.screen_dialog_signal_quit.emit()
        self.close()
