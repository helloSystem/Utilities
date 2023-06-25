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
class AnalogClock(QWidget):
    timeChanged = pyqtSignal(QTime)
    timeZoneChanged = pyqtSignal(int)

    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.timeZoneOffset = 0

        # creating a timer object
        timer = QTimer(self)

        # adding action to the timer
        # update the whole code
        timer.timeout.connect(self.update)
        timer.timeout.connect(self.updateTime)

        # setting start time of timer i.e 1 second
        timer.start(1000)

        # setting window title
        self.setWindowTitle('Clock')

        # setting window geometry
        self.setGeometry(200, 200, 300, 300)

        # creating hour hand
        self.hPointer = QPolygon(QRect(-2, 10, 4, -60))

        # creating minute hand
        self.mPointer = QPolygon(QRect(-1, 10, 3, -96))

        # creating second hand
        self.sPointer = QPolygon(QRect(-1, 20, 2, -115))
        # colors
        # color for minute and hour hand
        self.bColor = QColor(53, 76, 112, 255)

        # color for second hand
        self.sColor = QColor(255, 162, 0, 255)

    # method for paint event
    def paintEvent(self, event):

        # getting minimum of width and height
        # so that clock remain square
        rec = min(self.width(), self.height())

        # getting current time
        tik = QTime.currentTime()

        # creating a painter object
        painter = QPainter(self)

        # load the clock background image
        if self.isEnabled():
            # color for minute and hour hand
            self.bColor = QColor(53, 76, 112, 255)

            # color for second hand
            self.sColor = QColor(255, 162, 0, 255)

            # Face clock background
            bg = QImage(os.path.join(
                os.path.dirname(__file__),
                "clock_face.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # color for minute and hour hand
            self.bColor = QColor(120, 120, 120, 255)

            # color for second hand
            self.sColor = QColor(120, 120, 120, 255)

            bg = QImage(os.path.join(
                os.path.dirname(__file__),
                "clock_face_disable.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawImage(int(self.width() / 2 - bg.width() / 2),
                          int(self.height() / 2 - bg.height() / 2),
                          bg
                          )

        def drawPointer(color, rotation, pointer):

            # setting brush
            painter.setBrush(QBrush(color))

            # saving painter
            painter.save()

            # rotating painter
            painter.rotate(rotation)

            # draw the polygon i.e hand
            painter.drawConvexPolygon(pointer)

            # restore the painter
            painter.restore()

        # tune up painter
        painter.setRenderHint(QPainter.Antialiasing)

        # translating the painter
        painter.translate(self.width() / 2, self.height() / 2)

        # scale the painter
        painter.scale(rec / 200, rec / 200)

        # painter.drawImage(int(rec / 200) - int(rec / 2), int(rec / 200) - int(rec / 2), bg)
        # set current pen as no pen
        painter.setPen(QtCore.Qt.NoPen)

        # draw each hand
        drawPointer(self.bColor, (30 * (tik.hour() + tik.minute() / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (tik.minute() + tik.second() / 60)), self.mPointer)
        drawPointer(self.sColor, (6 * tik.second()), self.sPointer)

        # ending the painter
        painter.setPen(QPen(self.bColor, 2, Qt.SolidLine))
        painter.setBrush(QBrush(self.bColor, Qt.SolidPattern))
        painter.drawEllipse(-5,
                            -5,
                            10, 10)

        painter.setPen(QPen(Qt.darkGray, 2, Qt.SolidLine))
        painter.setFont(QFont('FreeMono', 20))
        if QTime().hour() <= 0 <= 12:
            painter.drawText(-15, 50, "AM")
        else:
            painter.drawText(-15, 50, "PM")
        painter.end()

    def updateTime(self):
        self.timeChanged.emit(QtCore.QTime.currentTime())

    def setTimeZone(self, value):
        if value != self.timeZoneOffset:
            self.timeZoneOffset = value
            self.timeZoneChanged.emit(value)
            self.update()

    def resetTimeZone(self):
        if self.timeZoneOffset != 0:
            self.timeZoneOffset = 0
            self.timeZoneChanged.emit(0)
            self.update()


# Driver code
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # creating a clock object
    win = AnalogClock()

    # show
    win.show()

    exit(app.exec_())
