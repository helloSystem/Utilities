from PyQt5.QtWidgets import QDialog
from dialog_about_ui import Ui_AboutDialog


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
