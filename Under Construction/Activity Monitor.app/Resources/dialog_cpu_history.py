from PyQt5.QtWidgets import QWidget
from dialog_cpu_history_ui import Ui_CPUHistory


class CPUHistory(QWidget, Ui_CPUHistory):

    def __init__(self, parent=None, process=None):
        super(CPUHistory, self).__init__(parent)
        self.setupUi(self)
        self.process = process

        # When you want to destroy the dialog set this to True
        self.have_to_close = False

    def closeEvent(self, evnt):
        # That widget is call as a window, and should be close with the main app
        # Else ---> The widget is hide then continue to store CPU data
        if self.have_to_close:
            super(CPUHistory, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.hide()
