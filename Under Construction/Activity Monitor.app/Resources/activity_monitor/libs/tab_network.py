#!/usr/bin/env python3

from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)


class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh(self):
        pass
