import sys
import os
import signal
import psutil

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QWidget,
    QSizePolicy,
    QSpacerItem,
    QApplication,
    QComboBox,
)


class SendSignal(QWidget):
    process_send_signal = pyqtSignal(object)

    def __init__(self, process=None, size=None):
        super(SendSignal, self).__init__()

        self.process = process
        self.size = size

        self.combobox = None
        self.button_cancel = None
        self.button_send = None

        self.setupUI()
        self.setupConnection()

    def setupUI(self):
        self.setWindowFlags(
            Qt.Dialog
        )
        self.setWindowTitle(" ")

        self.button_cancel = QPushButton(self.tr("Cancel"))
        self.button_cancel.setDefault(False)

        self.button_send = QPushButton(self.tr("Send"))
        self.button_send.setDefault(True)

        self.combobox = QComboBox()
        self.combobox.addItems([
            "Hangup (SIGHUP)",
            "Interrupt (SIGINT)",
            "Quit (SIGQUIT)",
            "Abort (SIGABRT)",
            "Kill (SIGKILL)",
            "Alarm (SIGALRM)",
            "User Defined 1 (SIGUSR1)",
            "User Defined 2 (SIGUSR2)",
        ])
        buttonBoxGrid = QGridLayout()
        buttonBoxGrid.setContentsMargins(0, 0, 0, 0)

        if self.process:
            label_text = QLabel("Please select a signal to send to the process '%s'" % self.process.name())
            buttonBoxGrid.addWidget(label_text, 0, 0, 1, 3, Qt.AlignLeft | Qt.AlignTop)
        buttonBoxGrid.addWidget(self.combobox, 1, 0, 1, 3, Qt.AlignLeft | Qt.AlignTop)
        buttonBoxGrid.addItem(QSpacerItem(3, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding))
        buttonBoxGrid.addWidget(self.button_cancel, 3, 1, 1, 1, Qt.AlignCenter | Qt.AlignBottom)
        buttonBoxGrid.addWidget(self.button_send, 3, 2, 1, 1, Qt.AlignCenter | Qt.AlignBottom)

        buttonBox = QWidget()
        buttonBox.setLayout(buttonBoxGrid)

        layout = QVBoxLayout()

        textArea = QHBoxLayout()
        textArea.setSpacing(0)
        textArea.setContentsMargins(0, 0, 0, 0)
        textAreaBox = QWidget()
        textAreaBox.setLayout(textArea)

        textVBox = QVBoxLayout()
        textBox = QWidget()
        textBox.setLayout(textVBox)

        if self.size:
            self.setFixedSize(self.size[0], self.size[1])

            textVBox.addWidget(label_text)

        textVBox.addStretch()
        textVBox.addWidget(buttonBox)
        textArea.addWidget(textBox)

        layout.addWidget(textAreaBox)

        self.setLayout(layout)

    def setupConnection(self):
        self.button_send.clicked.connect(self.button_send_clicked)
        self.button_cancel.clicked.connect(self.button_cancel_clicked)

    def button_send_clicked(self):
        index = self.combobox.currentIndex()

        # 0 "Hangup (SIGHUP)",
        # 1 "Interrupt (SIGINT)",
        # 2 "Quit (SIGQUIT)",
        # 3 "Abort (SIGABRT)",
        # 4 "Kill (SIGKILL)",
        # 5 "Alarm (SIGALRM)",
        # 6 "User Defined 1 (SIGUSR1)",
        # 7 "User Defined 2 (SIGUSR2)",
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

    def button_cancel_clicked(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SendSignal(
        process=psutil.Process(1)
    )
    win.show()
    sys.exit(app.exec_())
