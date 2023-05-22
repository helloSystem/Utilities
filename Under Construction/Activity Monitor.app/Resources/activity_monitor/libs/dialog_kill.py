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
)


class Kill(QWidget):
    process_signal_quit = pyqtSignal()
    process_signal_kill = pyqtSignal()

    def __init__(self, title=None, text=None, icon=None, size=None):
        super(Kill, self).__init__()
        # self.resize(400, 300)

        self.icon = icon
        self.title = title
        self.text = text
        self.size = size

        self.button_cancel = None
        self.button_force_quit = None
        self.button_quit = None

        self.setupUI()
        self.setupConnection()

    def setupUI(self):
        self.setWindowFlags(
            Qt.Dialog
        )
        self.setWindowTitle(" ")

        self.button_cancel = QPushButton(self.tr("Cancel"))
        self.button_cancel.setDefault(False)

        self.button_force_quit = QPushButton(self.tr("Force Quit"))
        self.button_force_quit.setDefault(False)

        self.button_quit = QPushButton(self.tr("Quit"))
        self.button_quit.setDefault(True)
        # button_quit.setAutoDefault(True)

        buttonBoxGrid = QGridLayout()
        buttonBoxGrid.setContentsMargins(0, 0, 0, 0)
        buttonBoxGrid.addWidget(self.button_cancel, 0, 0, 1, 1, Qt.AlignLeft)
        buttonBoxGrid.addItem(QSpacerItem(0, 2, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        buttonBoxGrid.addWidget(self.button_force_quit, 0, 3, 1, 1, Qt.AlignCenter)
        buttonBoxGrid.addWidget(self.button_quit, 0, 4, 1, 1, Qt.AlignCenter)

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
        if self.icon:
            label_pixmap = QLabel()
            label_pixmap.setPixmap(self.icon)
            label_pixmap.setAlignment(Qt.AlignHCenter)
            textArea.addWidget(label_pixmap)
        if self.title:
            label_title = QLabel(f"<b>{self.title}</b>")
            # label_title.setWordWrap(True)
            textVBox.addWidget(label_title)
        if self.text:
            label_text = QLabel(f"<font size='3'>{self.text}</font>")
            # label_text.setWordWrap(True)
            textVBox.addWidget(label_text)

        textVBox.addStretch()
        textVBox.addWidget(buttonBox)
        textArea.addWidget(textBox)

        layout.addWidget(textAreaBox)
        # layout.addStretch()
        # layout.addWidget(buttonBox)

        self.setLayout(layout)

    def setupConnection(self):
        self.button_quit.clicked.connect(self.button_quit_clicked)
        self.button_force_quit.clicked.connect(self.button_kill_clicked)
        self.button_cancel.clicked.connect(self.button_cancel_clicked)

    def button_quit_clicked(self):
        self.process_signal_quit.emit()
        self.close()

    def button_kill_clicked(self):
        self.process_signal_kill.emit()
        self.close()

    def button_cancel_clicked(self):
        self.close()
