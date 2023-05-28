import os
import signal

from PyQt5.QtWidgets import QDialog
from dialog_send_signal_ui import Ui_SendSignalDialog


class SendSignalDialog(QDialog):
    def __init__(self, parent=None, process=None):
        super(SendSignalDialog, self).__init__(parent)
        self.process = process
        self.ui = Ui_SendSignalDialog()
        self.ui.setupUi(self)
        self.ui.Label.setText(self.ui.Label.text() % self.process.name())

        self.ui.CancelButton.clicked.connect(self.cancel_dialog)
        self.ui.SendButton.clicked.connect(self.send_dialog)

    def cancel_dialog(self):
        self.close()

    def send_dialog(self):
        # 0, "Hangup (SIGHUP)"
        # 1, "Interrupt (SIGINT)"
        # 2, "Quit (SIGQUIT)"
        # 3, "Abort (SIGABRT)"
        # 4, "Kill (SIGKILL)"
        # 5, "Alarm (SIGALRM)"
        # 6, "User Defined 1 (SIGUSR1)"
        # 7, "User Defined 2 (SIGUSR2)"

        index = self.ui.SignalListComboBox.currentIndex()
        signal_list = [
            signal.SIGHUP,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGABRT,
            signal.SIGKILL,
            signal.SIGALRM,
            signal.SIGUSR1,
            signal.SIGUSR2,
        ]
        if index is not None:
            try:
                os.kill(self.process.pid, signal_list[index])
            except PermissionError:
                pass
        self.close()
