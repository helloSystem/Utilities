import os

from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFocusEvent
from PyQt5.QtWidgets import QDialog, QShortcut
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_selection_grab_ui import Ui_SelectionGrabDialog


class SelectionGrabDialog(QDialog):
    selection_dialog_signal_quit = pyqtSignal()
    selection_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(SelectionGrabDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)

        self.ui = Ui_SelectionGrabDialog()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.cancel_dialog)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_dialog)

    def cancel_dialog(self):
        self.selection_dialog_signal_quit.emit()

    def focusOutEvent(self, a0: QFocusEvent) -> None:
        self.selection_dialog_signal_start.emit()


