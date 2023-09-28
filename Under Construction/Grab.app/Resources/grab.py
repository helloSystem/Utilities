from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QGridLayout,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

import sys
import os
# The Main Window
from main_window_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__()
        self.fileName = None
        self.original_screen = None
        self.printerObj = None

        self.setupUi(self)
        self.setWindowTitle("Grab - new document[*]")

        self.setupCustomUi()
        self.connectSignalsSlots()

        self.take_screenshot()

    def setupCustomUi(self):
        # creating an object of the QPrinter class
        self.printerObj = QPrinter()
        self.resize(370, 270)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

    def connectSignalsSlots(self):
        # signals connections
        # Menu
        # File
        self.ActionMenuFileClose.triggered.connect(self.close)
        self.ActionMenuFileSave.triggered.connect(self.save)
        self.ActionMenuFileSaveAs.triggered.connect(self.saveAs)
        self.ActionMenuFilePrint.triggered.connect(self.printImage)
        self.ActionMenuFilePrintSetup.triggered.connect(self.printPreviewImage)
        # Edit
        self.ActionMenuEditCopy.triggered.connect(self.copyToClipboard)


        # Capture
        self.ActionMenuCaptureScreen.triggered.connect(self.new_screenshot)
        # About
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)

        # self.preview_screen..modificationChanged.connect(self.setWindowModified)

    def closeEvent(self, evnt):
        super(Window, self).closeEvent(evnt)

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
        self.img_preview.setPixmap(self.original_screen)

    def new_screenshot(self):
        self.hide()
        QTimer.singleShot(1000, self.take_screenshot)
        # self.setWindowModified(True)

    def take_screenshot(self):
        self.img_preview.setPixmap(QApplication.primaryScreen().grabWindow(0))

        self.show()
        if self.fileName:
            self.setWindowTitle("Grab - %s[*]" % (os.path.basename(self.fileName)))
        else:
            self.setWindowTitle("Grab - new document[*]")
        self.setWindowModified(True)

    # defining the method to print the image
    def printImage(self):
        # creating an object of the QPrintDialog class
        print_dialog = QPrintDialog(self.printerObj, self)
        # if the print action is executed
        if print_dialog.exec_():
            # creating an object of the QPainter class by passing the object of the QPrinter class
            the_painter = QPainter(self.printerObj)
            # creating a rectangle to place the image
            rectangle = the_painter.viewport()
            # defining the size of the image
            the_size = self.img_preview.pixmap().size()
            # scaling the image to the Aspect Ratio
            the_size.scale(rectangle.size(), Qt.KeepAspectRatio)
            # setting the viewport of the image by calling the setViewport() method
            the_painter.setViewport(rectangle.x(), rectangle.y(), the_size.width(), the_size.height())
            # calling the setWindow() method
            the_painter.setWindow(self.img_preview.pixmap().rect())
            # calling the drawPixmap() method
            the_painter.drawPixmap(0, 0, self.img_preview.pixmap())

    def printPreviewImage(self):
        # Initializes the QPainter and draws the pixmap onto it
        def drawImage(printer):
            the_painter = QPainter()
            the_painter.begin(printer)
            # creating a rectangle to place the image
            rectangle = the_painter.viewport()
            # defining the size of the image
            the_size = self.img_preview.pixmap().size()
            # scaling the image to the Aspect Ratio
            the_size.scale(rectangle.size(), Qt.KeepAspectRatio)
            # setting the viewport of the image by calling the setViewport() method
            the_painter.setViewport(rectangle.x(), rectangle.y(), the_size.width(), the_size.height())
            # calling the setWindow() method
            the_painter.setWindow(self.img_preview.pixmap().rect())
            # calling the drawPixmap() method
            the_painter.drawPixmap(0, 0, self.img_preview.pixmap())

            the_painter.setPen(Qt.red)
            the_painter.drawPixmap(0, 0, self.img_preview.pixmap())
            the_painter.end()

        # Shows the preview
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(drawImage)
        dlg.exec_()

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
