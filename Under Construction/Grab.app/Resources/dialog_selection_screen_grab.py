import os
import sys

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFocusEvent
from PyQt5.QtWidgets import QDialog, QShortcut

from dialog_selection_grab_ui import Ui_SelectionGrabDialog


class SelectionGrabDialog(QDialog):
    selection_dialog_signal_quit = pyqtSignal()
    selection_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(SelectionGrabDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.ui = Ui_SelectionGrabDialog()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        self.ui.button_cancel.clicked.connect(self.selection_dialog_quit)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.selection_dialog_quit)

        self.setFocus()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if self.hasFocus() or self.ui.button_cancel.hasFocus():
            event.accept()
        else:
            event.accept()
            self.selection_dialog_signal_start.emit()
            self.close()

    def selection_dialog_quit(self):
        self.selection_dialog_signal_quit.emit()
        self.close()
