from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from dialog_about_ui import Ui_AboutDialog
import os


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.ui.about_logo.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "Activity Monitor.png")))
