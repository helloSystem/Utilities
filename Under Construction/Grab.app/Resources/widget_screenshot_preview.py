# importing libraries
from PyQt5.QtWidgets import (
    QWidget, QApplication, QLabel
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QTime, QTimer, QRect, QTime
)
from PyQt5.QtGui import (
    QPolygon, QColor, QPainter, QImage, QBrush, QPen, QPalette, QPixmap
)
import sys
import os

class ScreenShotPreview(QLabel):
    pixmapChanged = pyqtSignal()


    # constructor
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

        self.__pixmap = None
        self.qp = None

    #     self.setupUi()
    #     self.setup()
    #
    #
    # def setupUi(self):
    #     # setting window title
    #     self.setWindowTitle('ScreenShotViewer')
    #
    #     # setting window geometry
    #     # self.setGeometry(200, 200, 300, 300)
    #
    # def setup(self):
    #     # self.qp = QPainter()
    #     self.show()
    #
    # def setPixmap(self, pixmap):
    #     if pixmap != self.__pixmap:
    #         self.__pixmap = pixmap
    #         self.pixmapChanged.emit()
    #
    # def pixmap(self):
    #     return self.__pixmap

    # method for paint event
    # def paintEvent(self, event):
    #
    #     self.qp.begin(self)
    #
    #     self.qp.setBrush(Qt.darkGray)
    #     self.qp.drawRect(0, 0, self.width(), self.height())
    #
    #     # tune up painter
    #     self.qp.setRenderHint(QPainter.Antialiasing)
    #
    #     # # drawing background
    #     if isinstance(self.__pixmap, QPixmap):
    #         bg = self.pixmap().scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #
    #         # drawing background
    #         self.qp.drawImage(int((self.width() - bg.width()) / 2),
    #                           int((self.height() - bg.height()) / 2),
    #                           bg.toImage()
    #                           )
    #
    #     # ending the painter
    #     self.qp.end()
