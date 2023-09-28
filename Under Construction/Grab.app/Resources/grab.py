from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QGridLayout,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QIcon, QResizeEvent
from PyQt5.QtCore import Qt, QTimer

import sys
import os
# The Main Window
from main_window_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__()
        self.fileName = None

        self.setupUi(self)
        self.setWindowTitle("Grab - new document[*]")
        self.original_screen = QApplication.primaryScreen().grabWindow(0)
        print(QApplication.screens())
        self.setupCustomUi()
        self.connectSignalsSlots()
        self.create_widgets()

    def setupCustomUi(self):

        self.resize(370, 270)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

    def connectSignalsSlots(self):
        # signals connections
        # Menu
        # File
        self.ActionMenuFileClose.triggered.connect(self.close)
        self.ActionMenuFileSave.triggered.connect(self.save)
        self.ActionMenuFileSaveAs.triggered.connect(self.saveAs)
        # Edit
        self.ActionMenuEditCopy.triggered.connect(self.copyToClipboard)


        # Capture
        self.ActionMenuCaptureScreen.triggered.connect(self.new_screenshot)
        # About
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)

        # self.preview_screen..modificationChanged.connect(self.setWindowModified)


    def create_widgets(self):
        self.img_preview.setPixmap(self.original_screen.scaled(350, 350,
                                                              Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setWindowModified(True)

    def closeEvent(self, evnt):
        super(Window, self).closeEvent(evnt)

    def resizeEvent(self, event):

        # scaledSize = self.original_screen.size()
        # scaledSize.scale(
        #     self.img_preview.size(),
        #     Qt.KeepAspectRatio
        # )
        # if not self.img_preview.pixmap() \
        # or scaledSize != self.img_preview.pixmap().size():
        self.updateScreenshotLabel()

    def save(self):
        if not self.isWindowModified():
            return
        if not self.fileName:
            self.saveAs()
        else:
            if self.fileName[-3:] == "png":
                self.original_screen.save(self.fileName, "png")
            elif self.fileName[-3:] == "jpg":
                self.original_screen.save(self.fileName, "jpg")
            self.setWindowTitle("Grab - %s[*]" % (os.path.basename(self.fileName)))
            self.setWindowModified(False)

    def saveAs(self):
        if not self.isWindowModified():
            return
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  "Save File",
                                                  "",
                                                  filter="PNG(*.png);; JPEG(*.jpg)",
                                                  options=options
                                                  )
        if fileName:
            if fileName[-3:] == "png":
                self.original_screen.save(fileName, "png")
            elif fileName[-3:] == "jpg":
                self.original_screen.save(fileName, "jpg")
            self.fileName = fileName
            self.setWindowTitle("Grab - %s[*]" % (os.path.basename(self.fileName)))
            self.setWindowModified(False)

    def copyToClipboard(self):
        if not self.original_screen:
            return
        qi = self.original_screen.toImage()
        QApplication.clipboard().setImage(qi)

    def updateScreenshotLabel(self):
        self.img_preview.setPixmap(self.original_screen.scaled(self.img_preview.size(),
                                                               Qt.KeepAspectRatio,
                                                               Qt.SmoothTransformation
                                                               ))


    def new_screenshot(self):
        self.hide()
        QTimer.singleShot(1000, self.take_screenshot)
        # self.setWindowModified(True)

    def take_screenshot(self):
        self.original_screen = QApplication.primaryScreen().grabWindow(0)
        self.updateScreenshotLabel()

        self.show()
        if self.fileName:
            self.setWindowTitle("Grab - %s[*]" % (os.path.basename(self.fileName)))
        else:
            self.setWindowTitle("Grab - new document[*]")
        self.setWindowModified(True)

    @staticmethod
    def _showAboutDialog():
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(
            QPixmap(
                os.path.join(
                    os.path.dirname(__file__),
                    "Grab.png"
                )
            ).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.join(os.path.dirname(__file__), candidate)):
                with open(os.path.join(os.path.dirname(__file__), candidate), 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Grab</h3>")
        msg.setInformativeText(
            "Grab is an application that can capture screen shots write in pyQt5.<br><br>"
            "<a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>"
        )
        msg.exec()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
