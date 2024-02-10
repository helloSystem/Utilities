import os

from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QCloseEvent
from PyQt5.QtWidgets import QDialog, QShortcut, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_screen_grab_ui import Ui_ScreenGrab


class ScreenGrabDialog(QDialog):
    screen_dialog_signal_quit = pyqtSignal()
    screen_dialog_signal_start = pyqtSignal()

    def __init__(self, parent=None):
        super(ScreenGrabDialog, self).__init__(parent)
        # self.setWindowFlags(
        #     Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        # )
        # self.setWindowFlags(
        #     Qt.Window |
        #     Qt.CustomizeWindowHint |
        #     Qt.WindowTitleHint |
        #     Qt.WindowCloseButtonHint
        # )
        #self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.ui = Ui_ScreenGrab()
        self.ui.setupUi(self)
        self.ui.icon.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")))
        self.setFixedSize(self.size())

        self.ui.button_cancel.clicked.connect(self.screen_dialog_quit)
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.screen_dialog_quit)

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        self.setFocus()


    # def focusOutEvent(self, event):
    #     self.screen_dialog_signal_quit.emit()


    def closeEvent(self, event: QCloseEvent) -> None:
        super(ScreenGrabDialog, self).setWindowOpacity(0.0)
        super(ScreenGrabDialog, self).closeEvent(event)
        QApplication.processEvents()
        event.accept()

    def screen_dialog_quit(self):
        self.screen_dialog_signal_quit.emit()

    def screen_dialog_start(self):
        self.screen_dialog_signal_start.emit()

