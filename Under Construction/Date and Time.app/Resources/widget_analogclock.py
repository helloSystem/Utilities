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
import math

from property_time import Time


# creating a clock class
class AnalogClock(QWidget, Time):
    timeChanged = pyqtSignal(QTime)
    timeZoneChanged = pyqtSignal(int)

    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        Time.__init__(self)

        self.qp = None

        # Hands Pointers
        self.hour_pointer = None
        self.minute_pointer = None
        self.second_pointer = None

        # colors
        self.hour_pointer_color = None
        self.hour_pointer_disable_color = None
        self.minute_pointer_color = None
        self.minute_pointer_disable_color = None
        self.second_pointer_color = None
        self.second_pointer_disable_color = None

        # color for number clock face
        self.clock_face_number_color = None
        self.clock_face_number_disable_color = None

        self.clock_face_hour_color = None
        self.clock_face_hour_disable_color = None

        self.ClockFaceHourFont = None

        self.clock_face_minute_color = None
        self.clock_face_minute_disable_color = None

        self.clock_face_am_pm_color = None
        self.clock_face_am_pm_disable_color = None

        self.pen_square = None
        self.pen_round = None

        self.pen_am_pm = None
        self.pen_am_pm_disable = None

        self.pen_square_disable = None
        self.pen_round_disable = None

        self.pen_clock_face_number = None
        self.pen_clock_face_number_disable = None

        self.setupUi()
        self.initialState()

    def setupUi(self):
        # creating hour hand
        self.hour_pointer = QPolygon(QRect(-2, 10, 4, -58))

        # creating minute hand
        self.minute_pointer = QPolygon(QRect(-1, 10, 3, -95))

        # creating second hand
        self.second_pointer = QPolygon(QRect(-1, 20, 2, -107))

        self.ClockFaceHourFont = QFont("Nimbus Sans", 13, QFont.Bold)

    def initialState(self):
        # setting window title
        self.setWindowTitle('Clock')

        # setting window geometry
        self.setGeometry(200, 200, 300, 300)

        # set time one file for the first time (indirect system ask)
        self.setTime(QTime.currentTime())

        self.qp = QPainter()

        # color for minute and hour hand
        self.hour_pointer_color = QColor(53, 76, 112, 255)
        self.hour_pointer_disable_color = QColor(146, 146, 146, 255)

        # color for minute and hour hand
        self.minute_pointer_color = QColor(53, 76, 112, 255)
        self.minute_pointer_disable_color = QColor(146, 146, 146, 255)

        # color for second hand
        self.second_pointer_color = QColor(255, 162, 0, 255)
        self.second_pointer_disable_color = QColor(146, 146, 146, 255)

        self.clock_face_number_color = QColor(0, 124, 202, 255)
        self.clock_face_number_disable_color = QColor(146, 146, 146, 255)

        self.clock_face_hour_color = QColor(29, 103, 188, 255)
        self.clock_face_hour_disable_color = QColor(146, 146, 146, 255)

        self.clock_face_minute_color = QColor(74, 120, 157, 255)
        self.clock_face_minute_disable_color = QColor(146, 146, 146, 255)

        self.clock_face_am_pm_color = Qt.darkGray
        self.clock_face_am_pm_disable_color = Qt.darkGray

        self.pen_am_pm = QPen(self.clock_face_am_pm_color, 2, Qt.SolidLine)
        self.pen_am_pm_disable = QPen(self.clock_face_am_pm_disable_color, 2, Qt.SolidLine)

        self.pen_square = QPen(self.clock_face_hour_color, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.pen_round = QPen(self.clock_face_minute_color, 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        self.pen_square_disable = QPen(Qt.darkGray, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        self.pen_round_disable = QPen(Qt.darkGray, 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        self.pen_clock_face_number = QPen(self.clock_face_number_color, 2, Qt.SolidLine)
        self.pen_clock_face_number_disable = QPen(self.clock_face_number_disable_color, 2, Qt.SolidLine)

    # method for paint event
    def paintEvent(self, event):

        self.qp.begin(self)

        # tune up painter
        self.qp.setRenderHint(QPainter.Antialiasing)

        # drawing background
        self.__draw_background_image()

        # translating the painter
        self.qp.translate(self.width() / 2, self.height() / 2)
        # # scale the painter
        self.qp.scale(min(self.width(), self.height()) / 200, min(self.width(), self.height()) / 200)

        # drawing clock face
        self.__draw_face_clock()

        # AM / PM
        self.__draw_face_clock_am_pm()

        # Clock Face Number in hard for take less CPU
        self.__draw_face_clock_numbers()

        # Pointers
        self.__draw_pointers()

        # the small circle for center illusion
        self.__draw_small_center_illusion()

        # ending the painter
        self.qp.end()

    def __draw_pointers(self):
        # set current pen as no pen
        self.qp.setPen(Qt.NoPen)
        if self.isEnabled():
            self.__draw_pointer(
                self.hour_pointer_color,
                (6 * self.time.second()),
                self.second_pointer
            )
            self.__draw_pointer(
                self.minute_pointer_color,
                (30 * (self.time.hour() + self.time.minute() / 60)),
                self.hour_pointer
            )
            self.__draw_pointer(
                self.second_pointer_color,
                (6 * (self.time.minute() + self.time.second() / 60)),
                self.minute_pointer
            )
        else:
            self.__draw_pointer(
                self.hour_pointer_disable_color,
                (6 * self.time.second()),
                self.second_pointer
            )
            self.__draw_pointer(
                self.minute_pointer_disable_color,
                (30 * (self.time.hour() + self.time.minute() / 60)),
                self.hour_pointer
            )
            self.__draw_pointer(
                self.second_pointer_disable_color,
                (6 * (self.time.minute() + self.time.second() / 60)),
                self.minute_pointer
            )

    def __draw_background_image(self):
        rec = min(self.width(), self.height())
        if self.isEnabled():
            bg = QImage(os.path.join(
                os.path.dirname(__file__),
                "clock_face2.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            bg = QImage(os.path.join(
                os.path.dirname(__file__),
                "clock_face2_disable.png"
            )).scaled(rec, rec, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # drawing background
        self.qp.drawImage(int(self.width() / 2 - bg.width() / 2),
                          int(self.height() / 2 - bg.height() / 2),
                          bg
                          )

    def __draw_pointer(self, color, rotation, pointer):

        # setting brush
        self.qp.setBrush(QBrush(color))

        # saving painter
        self.qp.save()

        # rotating painter
        self.qp.rotate(rotation)

        # draw the polygon i.e hand
        self.qp.drawConvexPolygon(pointer)

        # restore the painter
        self.qp.restore()

    def __draw_face_clock(self):

        if self.isEnabled():
            pen_square = self.pen_square
            pen_round = self.pen_round
        else:
            pen_square = self.pen_square_disable
            pen_round = self.pen_round_disable

        # Draw the clock face
        for i in range(0, 60):
            # drawing background lines
            if (i % 5) == 0:
                self.qp.setPen(pen_square)
                self.qp.drawLine(76, 0, 84, 0)
            elif (i % 1) == 0:
                self.qp.setPen(pen_round)
                self.qp.drawPoint(80, 0)
            # rotating the painter
            self.qp.rotate(6)

    def __draw_face_clock_am_pm(self):
        # AM / PM
        self.qp.setPen(Qt.NoPen)
        self.qp.setPen(self.pen_am_pm)
        self.qp.setFont(QFont('Nimbus Sans', 19))

        if self.time.hour() <= 0 <= 12:
            self.qp.drawText(-15, 45, "AM")
        else:
            self.qp.drawText(-15, 45, "PM")

    def __draw_small_center_illusion(self):
        # the small circle for center illusion
        if self.isEnabled():
            self.qp.setPen(QPen(self.minute_pointer_color, 2, Qt.SolidLine))
            self.qp.setBrush(QBrush(self.minute_pointer_color, Qt.SolidPattern))
        else:
            self.qp.setPen(QPen(self.minute_pointer_disable_color, 2, Qt.SolidLine))
            self.qp.setBrush(QBrush(self.minute_pointer_disable_color, Qt.SolidPattern))
        self.qp.drawEllipse(-3, -3, 6, 6)

    def __draw_face_clock_numbers(self):
        self.qp.setPen(Qt.NoPen)
        if self.isEnabled():
            self.qp.setPen(self.pen_clock_face_number)
        else:
            self.qp.setPen(self.pen_clock_face_number_disable)

        self.qp.setFont(self.ClockFaceHourFont)

        # Clock Face Number location is set in hard for take less CPU (Yes i know, me too ...)
        self.qp.drawText(-9, -62, "12")
        self.qp.drawText(29, -52, "1")
        self.qp.drawText(55, -29, "2")
        self.qp.drawText(65, 7, "3")
        self.qp.drawText(54, 40, "4")
        self.qp.drawText(30, 63, "5")
        self.qp.drawText(-4, 72, "6")
        self.qp.drawText(-38, 64, "7")
        self.qp.drawText(-64, 40, "8")
        self.qp.drawText(-73, 6, "9")
        self.qp.drawText(-66, -25, "10")
        self.qp.drawText(-42, -50, "11")

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
