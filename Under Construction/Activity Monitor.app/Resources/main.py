#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QActionGroup,
)
from ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.setupUiGroups()

    def connectSignalsSlots(self):
        pass

    def setupUiGroups(self):
        menu_frequency_group = QActionGroup(self)
        menu_frequency_group.addAction(self.ActionFrequencyTo1Sec)
        menu_frequency_group.addAction(self.ActionFrequencyTo3Secs)
        menu_frequency_group.addAction(self.ActionFrequencyTo5Secs)

        menu_filter_by_group = QActionGroup(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
