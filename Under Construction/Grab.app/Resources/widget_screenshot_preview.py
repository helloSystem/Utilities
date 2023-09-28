# importing libraries
from PyQt5.QtWidgets import (
    QWidget, QApplication
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QTime, QTimer, QRect, QTime
)
from PyQt5.QtGui import (
    QPolygon, QColor, QPainter, QImage, QBrush, QPen, QFont
)
import sys
import os

class ImagePreview(QWidget):
    pixmapChanged = pyqtSignal(bool)


    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.qp = None

        self.setupUi()
        self.setup()

    def setupUi(self):
        # setting window title
        self.setWindowTitle('Clock')

        # setting window geometry
        self.setGeometry(200, 200, 300, 300)

    def setup(self):
        self.qp = QPainter()

    # method for paint event
    def paintEvent(self, event):

        self.qp.begin(self)

        # tune up painter
        self.qp.setRenderHint(QPainter.Antialiasing)

        # # drawing background
        self.__draw_background_image()

        # translating the painter
        self.qp.translate(self.width() / 2, self.height() / 2)
        # # scale the painter
        self.qp.scale(min(self.width(), self.height()) / 200, min(self.width(), self.height()) / 200)

    # method for paint event
    def __draw_background_image(self):
        rec = min(self.width(), self.height())

        if self.isEnabled():
            bg = self.background_image.scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            bg = self.background_image_disable.scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # drawing background
        self.qp.drawImage(int((self.width() - bg.width()) / 2),
                          int((self.height() - bg.height()) / 2),
                          bg
                          )
        # ending the painter
        self.qp.end()