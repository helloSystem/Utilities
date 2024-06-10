import os

from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QFocusEvent, QKeySequence
from PyQt5.QtWidgets import QDialog, QDesktopWidget, QShortcut

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
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.ui.icon.setPixmap(
            QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")).scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

    def connectSignalsSlots(self):
        self.ui.button_cancel.clicked.connect(self.screen_dialog_quit)
        # QShortcut(QKeySequence("Escape"), self)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.screen_dialog_quit)

        # QShortcut(QKeySequence("Ctrl+C"), activated=self.on_Ctrl_C)

    def initialState(self):
        self.adjustSize()
        self.setFixedSize(self.size())
        self.center()
        self.setFocus()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # def eventFilter(self, source, event):
    #     if event.type() == QEvent.Close and source is self:
    #         self.close()
    #
    #     elif event.type() == QEvent.FocusOut:
    #         print('eventFilter: focus out')
    #         if self.hasFocus() or self.ui.button_cancel.hasFocus():
    #             event.accept()
    #
    #         else:
    #             super(ScreenGrabDialog, self).close()
    #             event.accept()
    #             self.screen_dialog_signal_start.emit()
    #
    #
    #     return super(ScreenGrabDialog, self).eventFilter(source, event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if self.hasFocus() or self.ui.button_cancel.hasFocus():
            event.accept()
        else:
            super(ScreenGrabDialog, self).close()
            event.accept()
            self.screen_dialog_signal_start.emit()

    def screen_dialog_quit(self):
        self.screen_dialog_signal_quit.emit()
        self.close()

    def screen_dialog_cancel(self):
        self.close()
