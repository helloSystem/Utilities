# Thanks a lot rakshitarora who provide the template code
# https://www.geeksforgeeks.org/pyqt5-qdateedit-getting-input-date/
# Clock face generate via https://www.oliverboorman.biz/projects/tools/clocks.php

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

from property_time import Time

# creating a clock class
class AnalogClock(QWidget, Time):

    timeChanged = pyqtSignal(QTime)
    timeZoneChanged = pyqtSignal(int)

    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        Time.__init__(self)



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

        self.pen_square = QPen(self.bColor, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.pen_round = QPen(self.bColor, 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        self.setTime(QTime.currentTime())

    # method for paint event
    def paintEvent(self, event):

        # getting minimum of width and height
        # so that clock remain square
        rec = min(self.width(), self.height())

        # getting current time
        # self.time = self.time.addSecs(1)

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
                "clock_face2.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # color for minute and hour hand
            self.bColor = QColor(120, 120, 120, 255)

            # color for second hand
            self.sColor = QColor(160, 160, 160, 255)

            bg = QImage(os.path.join(
                os.path.dirname(__file__),
                "clock_face2_disable.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # painter.drawImage(int(self.width() / 2 - bg.width() / 2) -1,
        #                   int(self.height() / 2 - bg.height() / 2)+12,
        #                   bg
        #                   )


        # drawing background

        # painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))



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

        # Draw the clock face
        painter.setFont(QFont('Nimbus Sans', 20))
        for i in range(0, 60):

            # drawing background lines
            if (i % 5) == 0:
                painter.setPen(self.pen_square)

                painter.drawLine(78, 0, 85, 0)


            elif (i % 1) == 0:
                painter.setPen(self.pen_round)
                painter.drawPoint(80, 0)

            # rotating the painter
            painter.rotate(6)

        # Circle
        painter.setPen(Qt.NoPen)
        painter.setPen(QPen(self.bColor, 2))
        painter.drawEllipse(-97,
                            -97,
                            194, 194)


        # AM / PM
        painter.setPen(Qt.NoPen)
        painter.setPen(QPen(Qt.darkGray, 2, Qt.SolidLine))
        painter.setFont(QFont('Nimbus Sans', 20))
        if self.time.hour() <= 0 <= 12:
            painter.drawText(-20, 50, "AM")
        else:
            painter.drawText(-20, 50, "PM")

        painter.setPen(Qt.NoPen)
        painter.setPen(QPen(self.bColor, 2, Qt.SolidLine))
        painter.setFont(QFont("Nimbus Sans", 13, QFont.Bold))
        painter.drawText(-9, -62, "12")
        painter.drawText(29, -52, "1")
        painter.drawText(55, -29, "2")
        painter.drawText(65, 7, "3")
        painter.drawText(54, 40, "4")
        painter.drawText(30, 63, "5")
        painter.drawText(-5, 73, "6")
        painter.drawText(-38, 64, "7")
        painter.drawText(-64, 40, "8")
        painter.drawText(-73, 6, "9")
        painter.drawText(-66, -25, "10")
        painter.drawText(-42, -50, "11")
        # set current pen as no pen
        painter.setPen(Qt.NoPen)
        # draw each hand
        drawPointer(self.bColor, (30 * (self.time.hour() + self.time.minute() / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (self.time.minute() + self.time.second() / 60)), self.mPointer)
        drawPointer(self.sColor, (6 * self.time.second()), self.sPointer)

        # the small circle for center illusion
        painter.setPen(QPen(self.bColor, 2, Qt.SolidLine))
        painter.setBrush(QBrush(self.bColor, Qt.SolidPattern))
        painter.drawEllipse(-5,
                            -5,
                            10, 10)
        # ending the painter
        painter.end()

    def updateTime(self):
        self.timeChanged.emit(QTime.currentTime())



# Driver code
if __name__ == '__main__':
    def update_time():
        clock.setTime(QTime.currentTime())
        clock.update()

    app = QApplication(sys.argv)

    # creating a clock object
    clock = AnalogClock()

    # creating a timer object
    timer = QTimer()
    # adding action to the timer
    # update the whole code
    timer.timeout.connect(update_time)
    # setting start time of timer i.e 1 second
    timer.start(1000)

    # show
    clock.show()

    exit(app.exec_())
