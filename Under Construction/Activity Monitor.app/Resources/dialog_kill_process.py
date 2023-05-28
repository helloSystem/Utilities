import os
import signal

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from dialog_kill_process_ui import Ui_KillDialog


class KillProcessDialog(QDialog):
    process_signal_quit = pyqtSignal()
    process_signal_kill = pyqtSignal()

    def __init__(self, parent=None, process=None):
        super(KillProcessDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)
        self.process = process
        self.ui = Ui_KillDialog()
        self.ui.setupUi(self)
        self.ui.Label.setText(self.ui.Label.text() % self.process.name())

        self.ui.button_cancel.clicked.connect(self.cancel_dialog)
        self.ui.button_force_quit.clicked.connect(self.force_kill_process)
        self.ui.button_quit.clicked.connect(self.kill_process)

    def cancel_dialog(self):
        self.close()

    def force_kill_process(self):
        try:
            os.kill(self.process.pid, signal.SIGKILL)
            self.process_signal_kill.emit()
        except PermissionError:
            pass
        self.close()

    def kill_process(self):
        try:
            os.kill(self.process.pid, signal.SIGQUIT)
            self.process_signal_quit.emit()
        except PermissionError:
            pass
        self.close()
