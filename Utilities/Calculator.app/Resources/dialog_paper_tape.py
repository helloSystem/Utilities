from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from dialog_paper_tape_ui import Ui_PaperTape


class PaperTape(QWidget, Ui_PaperTape):

    def __init__(self, parent=None, process=None):
        super(PaperTape, self).__init__(parent)
        self.setupUi(self)
        self.process = process

        # When you want to destroy the dialog set this to True
        self.have_to_close = False
        self.setFocusPolicy(Qt.ClickFocus)



    def closeEvent(self, evnt):
        # That widget is call as a window, and should be close with the main app
        # Else ---> The widget is hide then continue to store CPU data
        if self.have_to_close:
            super(PaperTape, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.hide()




    # def focusOutEvent(self, event):
    #     self.setFocus()
    #     self.activateWindow()
    #     self.raise_()
    #     self.show()
