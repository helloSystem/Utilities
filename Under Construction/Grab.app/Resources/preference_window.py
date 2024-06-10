import os
import sys

from PyQt5.QtGui import QPixmap, QKeySequence, QCursor, QIcon
from PyQt5.QtWidgets import QDialog, QShortcut, QWidget
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from preference_window_ui import Ui_PreferenceWindow


class PreferenceWindow(QWidget):
    checkbox_enable_sound_changed = pyqtSignal(object)
    buttongroup_changed = pyqtSignal(object)
    cursor_changed = pyqtSignal(object)

    def __init__(self, parent=None, pointer: int = None, play_sound: bool = None):
        super(PreferenceWindow, self).__init__(parent)

        self.cursor_id = {
            "ArrowCursor": Qt.ArrowCursor,
            "BlankCursor": Qt.BlankCursor,
            "ForbiddenCursor": Qt.ForbiddenCursor,
            "IBeamCursor": Qt.IBeamCursor,
            "OpenHandCursor": Qt.OpenHandCursor,
            "PointingHandCursor": Qt.PointingHandCursor,
            "UpArrowCursor": Qt.UpArrowCursor,
            "WhatsThisCursor": Qt.WhatsThisCursor,
        }

        self.cursor_name = {
            Qt.ArrowCursor: "ArrowCursor",
            Qt.BlankCursor: "BlankCursor",
            Qt.ForbiddenCursor: "ForbiddenCursor",
            Qt.IBeamCursor: "IBeamCursor",
            Qt.OpenHandCursor: "OpenHandCursor",
            Qt.PointingHandCursor: "PointingHandCursor",
            Qt.UpArrowCursor: "UpArrowCursor",
            Qt.WhatsThisCursor: "WhatsThisCursor",
        }

        self.ui = Ui_PreferenceWindow()
        self.ui.setupUi(self)
        self.setup()
        self.setupCustomUI()

        self.ui.checkbox_enable_sound.setChecked(play_sound)
        self.select_cursor(pointer)
        self.__play_sound = None
        self.play_sound = play_sound
        self.pointer = pointer

    def select_cursor(self, cursor_id):
        for button in self.ui.buttonGroup.buttons():
            if self.get_qt_cname_by_id(cursor_id) == button.objectName():
                button.setChecked(True)

    def setupCustomUI(self):
        for button in self.ui.buttonGroup.buttons():
            if os.path.exists(os.path.join(os.path.dirname(__file__), f"preference_{button.objectName()}.png")):
                button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), f"preference_{button.objectName()}.png")))

    def setup(self):

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setFocus()
        self.ui.checkbox_enable_sound.toggled.connect(self.enable_sound_changed)
        self.ui.buttonGroup.buttonClicked.connect(self.pointer_changed)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.preference_window_cancel)

    def preference_window_cancel(self) -> None:
        self.close()

    def pointer_changed(self):
        cursor_id = self.get_qt_cursor_id_by_name(self.ui.buttonGroup.checkedButton().objectName())
        self.buttongroup_changed.emit(cursor_id)

    def enable_sound_changed(self):
        self.checkbox_enable_sound_changed.emit(self.ui.checkbox_enable_sound.isChecked())

    def get_qt_cursor_id_by_name(self, name: str) -> int:
        try:
            return self.cursor_id[name]
        except KeyError:
            return Qt.BlankCursor

    def get_qt_cname_by_id(self, cursor_id: int) -> str:
        try:
            return self.cursor_name[cursor_id]
        except KeyError:
            return "BlankCursor"

