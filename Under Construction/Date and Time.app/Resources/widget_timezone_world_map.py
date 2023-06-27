# Thanks a lot rakshitarora who provide the template code
# https://www.geeksforgeeks.org/pyqt5-qdateedit-getting-input-date/

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os


# creating a clock class
class TimeZoneWorldMap(QWidget):
    timeChanged = pyqtSignal(QTime)
    timeZoneChanged = pyqtSignal(int)

    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)






        # setting window title
        self.setWindowTitle('TImeZone Worl Map')

        # setting window geometry
        self.setGeometry(200, 200, 300, 300)


        # color for minute and hour hand
        self.bColor = QColor(53, 76, 112, 255)

        # color for second hand
        self.sColor = QColor(255, 162, 0, 255)

    # method for paint event
    def paintEvent(self, event):

        # getting minimum of width and height
        # so that clock remain square
        rec = max(self.width(), self.height())

        # creating a painter object
        painter = QPainter(self)

        # load the clock background image

        # Face clock background
        if rec >= 1280:
            map_file = "2560px-World_map_with_nations.png"
        elif rec >= 640:
            map_file = "1280px-World_map_with_nations.png"
        elif rec:
            map_file = "640px-World_map_with_nations.png"
        else:
            map_file = "320px-World_map_with_nations.png"
        bg = QImage(os.path.join(
            os.path.dirname(__file__),
            map_file
        )).scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        painter.drawImage(int(self.width() / 2 - bg.width() / 2),
                          int(self.height() / 2 - bg.height() / 2),
                          bg
                          )
        gridSize = self.width() / 24
        x = y = 0
        width = self.width()
        height = self.height()
        while x <= width:
            # draw vertical lines
            painter.drawLine(x, int(self.height() / 2 - bg.height() / 2), x, self.height() - int(self.height() / 2 - bg.height() / 2))
            x += gridSize



        # ending the painter
        painter.end()








# Driver code
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # creating a clock object
    win = TimeZoneWorldMap()

    # show
    win.show()

    exit(app.exec_())
