import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QSizePolicy,
)

class About(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.icon = None
        self.name = None
        self.version = None
        self.text = None
        self.credit = None

    def show(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(" ")

        if self.icon:
            label_pixmap = QLabel()
            label_pixmap.setPixmap(self.icon)
            label_pixmap.setAlignment(Qt.AlignCenter)
            layout.addWidget(label_pixmap)
        if self.name:
            label_name = QLabel(f"<center><h3>{self.name}</h3></center>")
            label_name.setWordWrap(True)
            layout.addWidget(label_name)
        if self.version:
            label_version = QLabel(f"<center><font size='2'>{self.version}</font></center>")
            label_version.setWordWrap(True)
            layout.addWidget(label_version)
        if self.text:
            label_text = QLabel(f"<center><font size='3'>{self.text}</font></center>")
            label_text.setWordWrap(True)
            layout.addWidget(label_text)
        if self.credit:
            label_credit = QLabel(f"<center><font size='2'>{self.credit}</font></center>")
            label_credit.setWordWrap(True)
            layout.addWidget(label_credit)

        self.exec()
