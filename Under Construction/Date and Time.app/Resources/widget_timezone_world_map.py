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

        self.setMouseTracking(True)
        self.bg = None
        self.zone_location = None

        self.state_over = {
            "-12": False,
            "-11": False,
            "-10": False,
            "-9": False,
            "-8": False,
            "-7": False,
            "-6": False,
            "-5": False,
            "-4": False,
            "-3": False,
            "-2": False,
            "-1": False,
            "utc": False,
            "+1": False,
            "+2": False,
            "+3": False,
            "+4": False,
            "+5": False,
            "+6": False,
            "+7": False,
            "+8": False,
            "+9": False,
            "+10": False,
            "+11": False,
            "+12": False,
        }
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
        self.bg = QImage(os.path.join(
            os.path.dirname(__file__),
            map_file
        )).scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        painter.drawImage(int(self.width() / 2 - self.bg.width() / 2),
                          int(self.height() / 2 - self.bg.height() / 2),
                          self.bg
                          )
        gridSize = self.bg.width() / 24
        self.zone_location = {}
        start_width = int(self.width() / 2 - self.bg.width() / 2)
        stop_width = start_width + self.bg.width()
        start_height = int(self.height() / 2 - self.bg.height() / 2)
        stop_height = start_height + self.bg.height()
        font_size = int(self.bg.height() / 50)
        utc_text_height = stop_height - font_size
        painter.setFont(QFont('Nimbus Sans', font_size))

        # Trace Greenwich village location
        # That is the width / 2 of the world map
        greenwich_location = start_width + int(self.bg.width() / 2)

        # Trace UTC
        self.zone_location["utc"] = {}
        self.zone_location["utc"]['left'] = greenwich_location - int(gridSize / 2)
        self.zone_location["utc"]['right'] = greenwich_location + int(gridSize / 2)
        utc_start = greenwich_location - int(gridSize / 2)
        utc_stop = greenwich_location + int(gridSize / 2)

        painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
        x = utc_start
        painter.drawLine(x, start_height, x, self.height() - start_height)

        painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
        x = utc_stop
        painter.drawLine(x, start_height, x, self.height() - start_height)

        painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
        painter.drawText(int(utc_start + (gridSize / 2) - (gridSize / 3)), utc_text_height, f"UTC")

        for utc_plus in range(1, 13):
            # Trace UTC + X
            x = int(utc_stop + (gridSize * utc_plus))
            if utc_plus < 10:
                offset = int(gridSize / 6)
            else:
                offset = int(gridSize / 4)
            painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            painter.drawLine(x, start_height, x, self.height() - start_height)

            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.drawText(int(x - (gridSize / 2) - offset), utc_text_height, f"+{utc_plus}")

            self.zone_location[f"+{utc_plus}"] = {}
            self.zone_location[f"+{utc_plus}"]['left'] = x - gridSize
            self.zone_location[f"+{utc_plus}"]['right'] = x

        for utc_minus in range(1, 12):
            # Trace UTC - X
            x = int(utc_start - (gridSize * utc_minus))
            if utc_minus < 10:
                offset = int(gridSize / 6)
            else:
                offset = int(gridSize / 4)
            painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            painter.drawLine(x, start_height, x, self.height() - start_height)
            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.drawText(int(x + (gridSize / 2) - offset), utc_text_height, f"-{utc_minus}")

            self.zone_location[f"-{utc_minus}"] = {}
            self.zone_location[f"-{utc_minus}"]['left'] = x
            self.zone_location[f"-{utc_minus}"]['right'] = x + gridSize

        for key, value in self.state_over.items():
            if value is True:

                painter.setPen(QPen(QColor(255, 255, 255, 255), 1, Qt.SolidLine))
                painter.setBrush(QColor(255, 255, 255, 150))
                painter.drawRect(self.zone_location[key]['left'] + 1,
                                 start_height + 1,
                                 int(gridSize - 2),
                                 self.bg.height() - 1)


        # ending the painter
        painter.end()

    # def eventFilter(self, obj, event):
    #     if QWidget is obj:
    #         if event.type() == QtCore.QEvent.MouseButtonPress:
    #             print(self, "press")
    #         elif event.type() == QtCore.QEvent.MouseButtonRelease:
    #             print(self, "release")
    #     return super(TimeZoneWorldMap, self).eventFilter(obj, event)
    def mousePressEvent(self, event):
        # self.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        # self._initial_pos = event.pos()
        print("PRess")
        super().mousePressEvent(event)
    #
    def mouseMoveEvent(self, event):
        # x, y = event.pos()[0]
        # print(self.zone_location)
        # print(event.pos())
        for key, value in self.zone_location.items():
            if self.zone_location[key]['left'] <= event.pos().x() < self.zone_location[key]['right']:
                self.state_over[key] = True
                self.update()
            else:
                self.state_over[key] = False
                self.update()

        # try:
        #     if self.zone_location[0]['left'] <= event.pos().x() <= self.zone_location[0]['right']:
        #         print(f"UTC is over")
        # except KeyError:
        #     pass
        # delta = event.pos() - int(self.width() / 2 - self.bg.width() / 2)
        # self._path.translate(delta)
        # self._rect.translate(delta)
        # self.update()
        # self._initial_pos = event.pos()
        super().mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     QtWidgets.QApplication.restoreOverrideCursor()
    #     super().mouseReleaseEvent(event)
# Driver code
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # creating a clock object
    win = TimeZoneWorldMap()

    # show
    win.show()

    exit(app.exec_())
