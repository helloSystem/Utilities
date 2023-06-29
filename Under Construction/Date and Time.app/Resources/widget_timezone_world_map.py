# Thanks a lot rakshitarora who provide the template code
# https://www.geeksforgeeks.org/pyqt5-qdateedit-getting-input-date/

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
from iso6709 import Location

from decimal import Decimal

# creating a clock class
class TimeZoneWorldMap(QWidget):
    timeChanged = pyqtSignal(QTime)
    timeZoneChanged = pyqtSignal(int)
    TimeZoneSelectionChanged = pyqtSignal()
    TimeZoneClosestCityChanged = pyqtSignal(list)

    # constructor
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # setting window title
        self.setWindowTitle('TimeZone World Map')

        self.setMouseTracking(True)
        self.bg = None
        self.zone_location = None
        self.latitude_location = None
        self.longitude_location = None

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

        self.__timezone_selection = None
        self.TimeZoneSelection = None

        self.zone1970_db = None
        self.prime_meridian = None
        self.equator_location = None
        self.north_location = None
        self.south_location = None
        self.west_location = None
        self.east_location = None
        self.lat_ratio = None
        self.lng_ratio = None


        self.import_zone1970_db()


    def import_zone1970_db(self):
        self.zone1970_db = {}

        with open("/usr/share/zoneinfo/zone1970.tab") as zone1970_file_descriptor:
            imported_data = zone1970_file_descriptor.readlines()

        # codes	coordinates	TZ	comments
        for line in imported_data:
            if line.startswith("#"):
                continue
            data = line.strip("\n").split("\t")
            loc = Location(data[1])
            if len(data[1]) == len("±DDMM±DDDMM"):
                lat = int(f"{data[1][0]}{data[1][1]}{data[1][2]}")
                lng = int(f"{data[1][5]}{data[1][6]}{data[1][7]}")

            elif len(data[1]) == len("±DDMMSS±DDDMMSS"):
                lat = int(f"{data[1][0]}{data[1][1]}{data[1][2]}")
                lng = int(f"{data[1][7]}{data[1][8]}{data[1][9]}{data[1][10]}")

            print(f"lat:{lat} lng:{lng}")
            # ±DDMM±DDDMM or ±DDMMSS±DDDMMSS,
            self.zone1970_db[f"{data[2]}"] = {
                "code": data[0].split(","),
                "latitude": lat,
                "longitude": lng,
            }
            try:
                self.zone1970_db[f"{data[2]}"]["comments"] = data[3]
            except IndexError:
                pass

        # for item in self.zone1970_db.items():
        #     print(item)



    @pyqtProperty(int)
    def TimeZoneSelection(self):
        return self.__timezone_selection

    @TimeZoneSelection.setter
    def TimeZoneSelection(self, value):
        if value is None:
            value = 0
        if self.__timezone_selection != value:
            self.__timezone_selection = value
            self.TimeZoneSelectionChanged.emit()

    def setTimeZoneSelection(self, value):
        self.TimeZoneSelection = value

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

        timezone_grid_size = self.bg.width() / 24
        coodinates_grid_lat_size =  self.bg.width() / 180

        self.zone_location = {}
        self.longitude_location = {}
        self.latitude_location = {}

        self.north_location = int(self.height() / 2 - self.bg.height() / 2)
        self.south_location = self.north_location  + self.bg.width()
        self.west_location = int(self.width() / 2 - self.bg.width() / 2)
        self.east_location = self.west_location + self.bg.width()

        font_size = int(self.bg.height() / 50)
        utc_text_height = self.south_location - font_size
        painter.setFont(QFont('Nimbus Sans', font_size))

        # Trace Greenwich village location
        # That is the width / 2 of the world map

        self.prime_meridian = self.west_location + int(self.bg.width() / 2)
        self.equator_location = self.north_location + int(self.bg.height() / 2)

        self.lat_ratio = 180 / self.bg.height()
        self.lng_ratio = 360 / self.bg.width()

        # Trace UTC
        self.zone_location["utc"] = {}
        self.zone_location["utc"]['left'] = self.prime_meridian - int(timezone_grid_size / 2)
        self.zone_location["utc"]['right'] = self.prime_meridian + int(timezone_grid_size / 2)
        utc_start = self.prime_meridian - int(timezone_grid_size / 2)
        utc_stop = self.prime_meridian + int(timezone_grid_size / 2)

        painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
        painter.drawText(int(utc_start + (timezone_grid_size / 2) - (timezone_grid_size / 3)), utc_text_height, f"UTC")

        # Time Zone Area
        for utc_plus in range(1, 13):
            # Trace UTC + X
            x = int(utc_stop + (timezone_grid_size * utc_plus))
            if utc_plus < 10:
                offset = int(timezone_grid_size / 6)
            else:
                offset = int(timezone_grid_size / 4)
            # painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            # painter.drawLine(x, start_height, x, self.height() - start_height)

            painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            painter.drawText(int(x - (timezone_grid_size / 2) - offset), utc_text_height, f"+{utc_plus}")

            self.zone_location[f"+{utc_plus}"] = {}
            self.zone_location[f"+{utc_plus}"]['left'] = x - timezone_grid_size
            self.zone_location[f"+{utc_plus}"]['right'] = x

        for utc_minus in range(1, 12):
            # Trace UTC - X
            x = int(utc_start - (timezone_grid_size * utc_minus))
            if utc_minus < 10:
                offset = int(timezone_grid_size / 6)
            else:
                offset = int(timezone_grid_size / 4)
            # painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            # painter.drawLine(x, start_height, x, self.height() - start_height)
            painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            painter.drawText(int(x + (timezone_grid_size / 2) - offset), utc_text_height, f"-{utc_minus}")

            self.zone_location[f"-{utc_minus}"] = {}
            self.zone_location[f"-{utc_minus}"]['left'] = x
            self.zone_location[f"-{utc_minus}"]['right'] = x + timezone_grid_size

        for key, value in self.state_over.items():
            if value is True:
                painter.setPen(QPen(QColor(255, 255, 255, 255), 1, Qt.SolidLine))
                painter.setBrush(QColor(255, 255, 255, 150))
                painter.drawRect(self.zone_location[key]['left'] + 1,
                                 self.north_location + 1,
                                 int(timezone_grid_size - 2),
                                 self.bg.height() - 1)
            try:
                if self.TimeZoneSelection == f"{key}":
                    painter.setPen(QPen(QColor(0, 39, 60, 255), 1, Qt.SolidLine))
                    painter.setBrush(QColor(0, 39, 60, 127))
                    painter.drawRect(self.zone_location[key]['left'] + 1,
                                     self.north_location + 1,
                                     int(timezone_grid_size - 2),
                                     self.bg.height() - 1)
            except KeyError:
                pass

        # ending the painter
        painter.end()

    def mousePressEvent(self, event):
        if self.west_location <= event.pos().x() < self.east_location:
            for key, value in self.zone_location.items():
                if self.zone_location[key]['left'] <= event.pos().x() < self.zone_location[key]['right']:
                    self.setTimeZoneSelection(f"{key}")
                    self.update()
        super().mousePressEvent(event)

    #
    def mouseMoveEvent(self, event):
        if self.west_location <= event.pos().x() < self.east_location:
            for key, value in self.zone_location.items():
                if self.zone_location[key]['left'] <= event.pos().x() < self.zone_location[key]['right']:
                    self.state_over[key] = True
                    self.update()
                else:
                    self.state_over[key] = False
                    self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.west_location <= event.pos().x() < self.east_location:
            lng = (event.pos().x() - self.prime_meridian) * self.lng_ratio
            lat = (event.pos().y() - self.equator_location) * self.lat_ratio
            lat = lat * -1
            print(f"lat:{lat} lng:{lng}")

            tol = 5
            found = False
            closest = []
            while found == False:
                for key, item in self.zone1970_db.items():
                    if int(lng) - tol <= item["longitude"] <= int(lng) + tol and\
                       int(lat) - tol <= item["latitude"] <= int(lat) + tol:
                        if key not in closest:
                            closest.append(key)
                if len(closest) > 3:
                    found = True
                else:
                    tol += 1


            if closest and len(closest) >= 1:
                self.TimeZoneClosestCityChanged.emit(closest)


            for key, value in self.zone_location.items():
                if self.zone_location[key]['left'] <= event.pos().x() < self.zone_location[key]['right']:
                    self.setTimeZoneSelection(f"{key}")
                    self.update()

        super().mouseReleaseEvent(event)


# Driver code
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # creating a clock object
    win = TimeZoneWorldMap()

    # show
    win.show()

    exit(app.exec_())
