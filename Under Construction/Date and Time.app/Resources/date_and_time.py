#!/usr/bin/env python3

# FIXME: The spinner is not shown; we need to fix this by using threading? Is there a better way?
# TODO: Implement manual time zone setting in the time zone tab
# TODO: Implement manual date and time setting in the date and time tab

import subprocess
import sys
import os
from time import ctime
from PyQt5.QtCore import Qt, QDateTime, QTimer, QDate, QUrl, QEvent, QByteArray, QSettings, QThread, QThreadPool
from PyQt5.QtWidgets import QApplication, QDateTimeEdit, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QKeyEvent, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from date_and_time_ui import Ui_MainWindow
from property_date_time_auto import DateTimeAutomatically
from property_timezone import TimeZoneProperty
from ntplib import NTPClient
from worker_ntp_client import NtpClientWorker

class DateTimeWindow(QMainWindow, Ui_MainWindow, DateTimeAutomatically, TimeZoneProperty):

    def __init__(self):
        super().__init__()
        DateTimeAutomatically.__init__(self)
        TimeZoneProperty.__init__(self)

        # Worker
        self.threads = []
        self.threadpool = QThreadPool()

        self.error_dialog = None
        self.timer = None

        self.system_date = None
        self.system_time = None
        self.system_timezone = None

        self.date = None
        self.time = None

        self.timezone_file_path = None
        self.timezone_file = None

        self.settings = None

        self.__ntp_servers = {
            0: "africa.pool.ntp.org",
            1: "antarctica.pool.ntp.org",
            2: "asia.pool.ntp.org",
            3: "europe.pool.ntp.org",
            4: "north-america.pool.ntp.org",
            5: "oceania.pool.ntp.org",
            6: "south-america.pool.ntp.org",
        }

        self.setupUi(self)
        self.initial_state()
        self.signalsConnect()
        self.read_settings()

    def initial_state(self):
        # self.timezone_file_path = "/etc/timezone"
        # self.timezone_file = QFile(self.timezone_file_path)
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer_ntp_client = QTimer()
        self.timer_ntp_client.start(5000)

        self.dat_timeedit_widget.setDateTime(self.get_current_datetime())
        self.dat_dateedit_widget.setDate(self.get_current_date())

        # self.setDateTimeAutomatically(False)
        # self.tz_time_zone_label.setText(self.get_current_time_zone())
        self.__timezone_closest_city_changed([self.get_timezone_file_content()])

        self.settings = QSettings("helloSystem", "Date and Time.app")

    def signalsConnect(self):
        self.timer.timeout.connect(self.refresh)
        self.timer_ntp_client.timeout.connect(self.refresh_ntp_client)

        self.actionHelpAbout.triggered.connect(self.show_about)
        self.DateTimeAutomaticallyChanged.connect(self.__checkbox_set_date_and_time_automatically_changed)
        self.date_and_time_auto_checkbox.toggled.connect(self.__checkbox_set_date_and_time_automatically_changed)

        # Date and Time
        self.dat_calendar_widget.selectionChanged.connect(self.__dat_calendar_widget_changed)
        self.dat_dateedit_widget.dateTimeChanged.connect(self.__dat_dateedit_widget_changed)
        self.dat_timeedit_widget.dateTimeChanged.connect(self.__dat_timeedit_widget_changed)
        self.ntp_servers_comboBox.currentIndexChanged.connect(self.__ntp_servers_comboBox_index_changed)

        # Time Zone
        self.tz_closest_city_combobox.currentIndexChanged.connect(self.__timezone_combobox_index_changed)
        self.tz_time_zone_world_map_widget.TimeZoneClosestCityChanged.connect(self.__timezone_closest_city_changed)
        self.checkbox_set_time_zone_automatically_using_current_location.toggled.connect(
            self.__checkbox_set_time_zone_automatically_using_current_location_changed
        )
        self.TimeZoneChanged.connect(self.__time_zone_changed)

        # Undo, cut, copy, paste, and delete actions. Undo is disabled.
        # They have the default shortcuts. When invoked, the corresponding
        # shortcut is sent to the currently focused widget.
        self.action_cut.triggered.connect(lambda: self.send_shortcut(Qt.Key_X, Qt.ControlModifier))
        self.action_copy.triggered.connect(lambda: self.send_shortcut(Qt.Key_C, Qt.ControlModifier))
        self.action_paste.triggered.connect(lambda: self.send_shortcut(Qt.Key_V, Qt.ControlModifier))
        self.action_delete.triggered.connect(lambda: self.send_shortcut(Qt.Key_Delete, Qt.NoModifier))
        self.action_set_date_and_time_automatically.changed.connect(
            self.__action_set_date_and_time_automatically_changed)
        self.action_set_time_zone_automatically.changed.connect(self.__action_set_time_zone_automatically_changed)

    def createNtpClientThread(self):
        thread = QThread()
        worker = NtpClientWorker(
            host=self.__ntp_servers[self.ntp_servers_comboBox.currentIndex()],
            version=3,
            port=123,
            timeout=5,
        )
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # Icons Cache
        worker.updated_datetime.connect(self.__worker_ntp_client_send_updated_datetime)
        worker.updated_date.connect(self.__worker_ntp_client_send_updated_date)
        worker.error.connect(self.__worker_ntp_client_send_error)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh_ntp_client(self):
        if self.date_and_time_auto_checkbox.isChecked():
            self.threads.clear()
            self.threads = [
                self.createNtpClientThread(),
            ]
            for thread in self.threads:
                thread.start()

    def refresh(self):
        self.dat_timeedit_widget.setDateTime(self.dat_timeedit_widget.dateTime().addSecs(1))
        # self.dat_date_widget.setDate(self.dat_date_widget.date().addSecs(1))
        self.dat_clock_widget.time = self.dat_timeedit_widget.time()

        # # Help menu
        # self.help_menu = self.menuBar().addMenu("Help")
        # about_action = self.help_menu.addAction("About", self.show_about)
        # about_action.setShortcut("Ctrl+?")
        #
        # # Create spinner
        # self.spinner = QLabel(self)
        # # Generated using http://ajaxload.info/
        # self.spinner.setMovie(
        #     QMovie(os.path.dirname(__file__) + "/Resources/spinner.gif"))
        # self.spinner.movie().start()
        # self.spinner.hide()
        # self.spinner.setAlignment(Qt.AlignCenter)
        # # self.spinner.setFixedSize(16, 16)
        # self.spinner.move(0, self.height() - self.spinner.height())
        # # Connect to the resizeEvent of the window to update the position of the spinner
        # self.resizeEvent = lambda event: self.spinner.move(
        #     -20, self.height() - self.spinner.height() - 10)
        if not self.timer.isActive():
            self.timer.start()



    def send_shortcut(self, key_code, modifier):
        # Send shortcut to currently focused widget like Ctrl+C, Ctrl+V, etc.
        widget = self.focusWidget()
        key_event = QKeyEvent(QEvent.KeyPress, key_code, modifier)
        QApplication.postEvent(widget, key_event)

    def update_date_time(self):
        self.dt_set_date_time_manual.setDateTime(self.get_current_datetime())
        self.dt_set_date_manual.setDateTime(self.get_current_date())

    def create_date_time_tab(self):
        # Create widgets
        self.dt_set_date_time_manual = QDateTimeEdit(self)
        self.dt_set_date_time_manual.setDisplayFormat("MMM d yyyy  hh:mm:ss")
        self.dt_set_date_time_manual.setDateTime(self.get_current_datetime())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)
        # When the QDateTimeEdit is manually changed, stop the timer; but do not stop the timer if it was changed by the timer
        self.dt_set_date_time_manual.dateTimeChanged.connect(
            lambda: self.timer.stop() if self.dt_set_date_time_manual.dateTime().toString(
                'yyyy-MM-dd hh:mm:ss') != self.get_current_datetime().toString('yyyy-MM-dd hh:mm:ss') else None)

        self.btn_set_date_time_manual = QPushButton("Set Date and Time", self)

        self.grp_set_date_time = QGroupBox("Set Date and Time", self)
        self.vbox_set_date_time = QVBoxLayout()
        self.vbox_set_date_time.addWidget(self.dt_set_date_time_manual)
        self.vbox_set_date_time.addWidget(self.btn_set_date_time_manual)
        self.grp_set_date_time.setLayout(self.vbox_set_date_time)

        self.btn_set_date_time_auto = QPushButton(
            "Set Date and Time automatically", self)

        self.grp_set_date_time_auto = QGroupBox("Date and Time options", self)
        self.vbox_set_date_time_auto = QVBoxLayout()
        self.vbox_set_date_time_auto.addWidget(self.btn_set_date_time_auto)
        self.grp_set_date_time_auto.setLayout(self.vbox_set_date_time_auto)

        # Connect signals to slots
        self.btn_set_date_time_manual.clicked.connect(
            self.set_date_time_manual)
        self.btn_set_date_time_auto.clicked.connect(self.set_date_time_auto)

        # Create grid layout for date/time tab
        self.grid_layout_date_time = QGridLayout()

        self.grid_layout_date_time.addWidget(
            self.grp_set_date_time, 2, 0, 1, 2)
        self.grid_layout_date_time.addWidget(
            self.grp_set_date_time_auto, 3, 0, 1, 2)
        self.grid_layout_date_time.setRowStretch(4, 1)

        # Create date/time tab and set layout
        self.date_time_tab = QWidget(self)
        self.date_time_tab.setLayout(self.grid_layout_date_time)

    def create_time_zone_tab(self):
        # Create widgets
        self.btn_set_time_zone_auto = QPushButton(
            "Set time zone automatically", self)

        self.grp_set_time_zone = QGroupBox("Set time zone", self)
        self.vbox_set_time_zone = QVBoxLayout()
        self.vbox_set_time_zone.addWidget(self.btn_set_time_zone_auto)
        self.grp_set_time_zone.setLayout(self.vbox_set_time_zone)

        # Connect signals to slots
        self.btn_set_time_zone_auto.clicked.connect(self.set_time_zone_auto)

        # Create grid layout for time zone tab
        self.grid_layout_time_zone = QGridLayout()
        self.grid_layout_time_zone.addWidget(self.grp_set_time_zone, 1, 0)
        self.grid_layout_time_zone.setRowStretch(2, 1)

        # Create time zone tab and set layout
        self.time_zone_tab = QWidget(self)
        self.time_zone_tab.setLayout(self.grid_layout_time_zone)

    @staticmethod
    def get_current_datetime():
        # try:
        #     # Get the current date and time
        #     result = subprocess.run(["date", "+%Y-%m-%d %H:%M:%S"],
        #                             capture_output=True, text=True, check=True)
        #     return QDateTime.fromString(result.stdout.strip(), "yyyy-MM-dd hh:mm:ss")
        # except subprocess.CalledProcessError as e:
        #     self.show_error_dialog("Error getting current Date and Time",
        #                            f"An error occurred while getting the current Date and Time: {e.stderr}")
        return QDateTime.currentDateTime()

    @staticmethod
    def get_current_date():
        return QDate.currentDate()



    def set_date_time_manual(self):
        self.spinner.show()
        # 202304151224.10 = Sa. 15 Apr. 2023 12:24:10 CEST
        new_date_time = self.dt_set_date_time_manual.dateTime().toString(
            "yyyyMMddhhmm.ss")
        try:
            # Set the new date and time
            subprocess.run(["sudo", "date", new_date_time], check=True)
            self.dt_set_date_time_manual.setDateTime(
                self.get_current_datetime())
        except subprocess.CalledProcessError as e:
            self.show_error_dialog("Error setting Date and Time",
                                   f"An error occurred while setting the Date and Time: {e.stderr}")
        self.spinner.hide()

    def set_date_time_auto(self):
        # self.spinner.show()
        # # Wait one second before setting the date and time automatically
        # time.sleep(1)
        # try:
        #     # Set the date and time automatically using NTP
        #     subprocess.run(["sudo", "ntpdate", "-v", "-b",
        #                     "-u", "pool.ntp.org"], check=True)
        #     self.dt_set_date_time_manual.setDateTime(
        #         self.get_current_datetime())
        # except subprocess.CalledProcessError as e:
        #     self.show_error_dialog("Error setting Date and Time automatically",
        #                            f"An error occurred while setting the Date and Time automatically: {e.stderr}")
        # # Restart the timer if it is not running
        # if not self.timer.isActive():
        #     self.timer.start()
        # self.spinner.hide()
        self.refresh()




    def set_time_zone_auto(self):
        # try:
        #     # Set the time zone automatically using NTP
        #     subprocess.run(["sudo", "ntpdate", "-v", "-b",
        #                     "-u", "pool.ntp.org"], check=True)
        # except subprocess.CalledProcessError as e:
        #     self.show_error_dialog("Error setting time zone automatically",
        #                            f"An error occurred while setting the time zone automatically: {e.stderr}")
        def handleResponse(reply):
            er = reply.error()

            if er == QNetworkReply.NoError:
                # tz = bytes(reply.readAll()).decode("utf-8").strip("\n")
                self.setTimeZone(bytes(reply.readAll()).decode("utf-8").strip("\n"))

                self.tz_closest_city_combobox.clear()
                self.tz_closest_city_combobox.addItem(self.TimeZone)
                self.__timezone_combobox_index_changed()

            else:
                self.show_error_dialog(
                    message=f"Error occurred: {er}<br>{'<br>'.join(reply.errorString().split(' - '))}"
                )
                self.set_time_zone_automatically_checkbox.setChecked(False)

        if self.checkbox_set_time_zone_automatically_using_current_location.isChecked():
            req = QNetworkRequest(QUrl("http://ip-api.com/line?fields=timezone"))

            self.nam = QNetworkAccessManager()
            self.nam.finished.connect(handleResponse)
            self.nam.get(req)

            # TODO: Set language, keyboard,, etc. automatically based on geolocation if user allows

    def get_timezone_file_content(self):
        try:
            return self.TimeZone
        except IOError as error:
            self.show_error_dialog("Problem reading file %s" % self.timezone_file_path)

    @staticmethod
    def show_error_dialog(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(" ")
        msg_box.setText(message)
        msg_box.exec_()

    @staticmethod
    def show_about():
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(
            QPixmap(
                os.path.join(
                    os.path.dirname(__file__),
                    "Date and Time.png"
                )
            ).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.join(os.path.dirname(__file__), candidate)):
                with open(os.path.join(os.path.dirname(__file__), candidate), 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Date and Time</h3>")
        msg.setInformativeText(
            "A simple preferences application to set date and time using "
            "<a href='https://www.freebsd.org/cgi/man.cgi?ntpdate'>ntpdate</a> "
            "and <a href='https://www.freebsd.org/cgi/man.cgi?date'>date</a><br><br>"
            "Visit <a href='https://github.com/helloSystem/Utilities/'>"
            "<span style=' text-decoration: underline; color:#0000ff;'>"
            "https://github.com/helloSystem/Utilities/</span></a> "
            "for more information or to report bug and/or suggest a new feature."
            "<p align='center'><span style=' font-size:14pt; vertical-align:sub;'>"
            "Make for you with love by helloSystem team.<br/></span></p>"
        )
        msg.exec()

    def __checkbox_set_date_and_time_automatically_changed(self):
        if self.date_and_time_auto_checkbox.isChecked():
            self.ntp_servers_comboBox.setEnabled(True)

            self.dat_timeedit_widget.setEnabled(False)
            self.dat_clock_widget.setEnabled(False)

            self.dat_dateedit_widget.setEnabled(False)
            self.dat_calendar_widget.setEnabled(False)

            # Prevent loop with the action menu
            if not self.action_set_date_and_time_automatically.isChecked():
                self.action_set_date_and_time_automatically.setChecked(True)

        else:
            self.ntp_servers_comboBox.setEnabled(False)

            self.dat_timeedit_widget.setEnabled(True)
            self.dat_clock_widget.setEnabled(True)

            self.dat_dateedit_widget.setEnabled(True)
            self.dat_calendar_widget.setEnabled(True)

            # Prevent loop with the action menu
            if self.action_set_date_and_time_automatically.isChecked():
                self.action_set_date_and_time_automatically.setChecked(False)

        self.refresh_ntp_client()

    def __action_set_date_and_time_automatically_changed(self):
        if self.action_set_date_and_time_automatically.isChecked():

            # Prevent loop with the action menu
            if not self.date_and_time_auto_checkbox.isChecked():
                self.date_and_time_auto_checkbox.setChecked(True)
        else:

            # Prevent loop with the action menu
            if self.date_and_time_auto_checkbox.isChecked():
                self.date_and_time_auto_checkbox.setChecked(False)

    def __checkbox_set_time_zone_automatically_using_current_location_changed(self):
        if self.checkbox_set_time_zone_automatically_using_current_location.isChecked():
            self.tz_closest_city_label.setEnabled(False)
            self.tz_closest_city_combobox.setEnabled(False)
            self.tz_time_zone_world_map_widget.setEnabled(False)
            self.tz_time_zone_label.setEnabled(False)
            self.tz_time_zone_value.setEnabled(False)

            # Prevent loop with the action menu
            if not self.action_set_time_zone_automatically.isChecked():
                self.action_set_time_zone_automatically.setChecked(True)

        else:
            self.tz_closest_city_label.setEnabled(True)
            self.tz_closest_city_combobox.setEnabled(True)
            self.tz_time_zone_world_map_widget.setEnabled(True)
            self.tz_time_zone_label.setEnabled(True)
            self.tz_time_zone_value.setEnabled(True)

            # Prevent loop with the action menu
            if self.action_set_time_zone_automatically.isChecked():
                self.action_set_time_zone_automatically.setChecked(False)

                found_the_city_in_zone1970_db = False
                lng = 0
                lat = 0
                for key, value in self.tz_time_zone_world_map_widget.zone1970_db.items():
                    if key == self.TimeZone:
                        found_the_city_in_zone1970_db = True
                        lng = float(value["longitude"])
                        lat = float(value["latitude"])

                if found_the_city_in_zone1970_db:
                    tol = 0
                    found = False
                    closest = []
                    while not found:
                        for key, item in self.tz_time_zone_world_map_widget.zone1970_db.items():
                            if lng - tol <= item["longitude"] <= lng + tol and \
                                    lat - tol <= item["latitude"] <= lat + tol:
                                if key not in closest and not len(closest) > 15:
                                    closest.append(key)

                        if len(closest) > 15:
                            found = True
                        else:
                            tol += 0.1

                    if closest and len(closest) >= 1:
                        self.__timezone_closest_city_changed(closest)

    def __action_set_time_zone_automatically_changed(self):
        if self.action_set_time_zone_automatically.isChecked():
            # Prevent loop with the action menu
            if not self.checkbox_set_time_zone_automatically_using_current_location.isChecked():
                self.set_time_zone_automatically_checkbox.setChecked(True)
            self.set_time_zone_auto()
        else:
            # Prevent loop with the action menu
            if self.checkbox_set_time_zone_automatically_using_current_location.isChecked():
                self.set_time_zone_automatically_checkbox.setChecked(False)

        # Store the setting
        self.settings.setValue("checkbox_set_time_zone_automatically_using_current_location",
                               self.checkbox_set_time_zone_automatically_using_current_location.isChecked()
                               )

    def __time_zone_changed(self):
        self.tz_closest_city_combobox.clear()
        self.tz_closest_city_combobox.addItem(self.TimeZone)
        print("TineZone change")

    def __dat_calendar_widget_changed(self):
        self.dat_dateedit_widget.setDate(self.dat_calendar_widget.selectedDate())

    def __dat_dateedit_widget_changed(self):
        self.dat_calendar_widget.setSelectedDate(self.dat_dateedit_widget.date())

    def __dat_timeedit_widget_changed(self):
        pass
        # self.dat_clock_widget.setTime(self.dat_timeedit_widget.time())

    def __ntp_servers_comboBox_index_changed(self):
        pass
        # if self.date_and_time_auto_checkbox.isChecked():
        #     self.set_date_time_auto()

    def __timezone_closest_city_changed(self, value):
        self.tz_closest_city_combobox.clear()
        self.tz_closest_city_combobox.addItems(sorted(value))
        index = self.tz_closest_city_combobox.findText(self.TimeZone, Qt.MatchFixedString)
        if index >= 0:
            self.tz_closest_city_combobox.setCurrentIndex(index)
        self.__timezone_combobox_index_changed()

    def __timezone_combobox_index_changed(self):
        if self.tz_closest_city_combobox.currentText():
            code = ", ".join(
                self.tz_time_zone_world_map_widget.zone1970_db[self.tz_closest_city_combobox.currentText()]["code"])

            if "comments" in self.tz_time_zone_world_map_widget.zone1970_db[
                self.tz_closest_city_combobox.currentText()]:
                comments = self.tz_time_zone_world_map_widget.zone1970_db[self.tz_closest_city_combobox.currentText()][
                    "comments"]
                self.tz_time_zone_value.setText(f"{code} - {comments}")
            else:
                self.tz_time_zone_value.setText(f"{code}")

    def __worker_ntp_client_send_updated_date(self, qdate):
        if isinstance(qdate, QDate):
            self.dat_dateedit_widget.setDate(qdate)

    def __worker_ntp_client_send_updated_datetime(self, qdatetime):
        if isinstance(qdatetime, QDateTime):
            self.dat_timeedit_widget.setDateTime(qdatetime)

    def __worker_ntp_client_send_error(self, error):
        self.error_message_label.setText(error)

    def closeEvent(self, event):
        self.write_settings()
        super(DateTimeWindow, self).closeEvent(event)
        event.accept()

    def write_settings(self):
        # Entire Application Window
        self.settings.setValue("geometry",
                               self.saveGeometry()
                               )
        self.settings.setValue("windowState",
                               self.saveState()
                               )

        # Tab
        self.settings.setValue("tabWidget",
                               self.tabWidget.currentIndex()
                               )

        # Date and Time Tab
        self.settings.setValue("date_and_time_auto",
                               self.date_and_time_auto_checkbox.isChecked()
                               )

        self.settings.setValue("ntp_servers",
                               self.ntp_servers_comboBox.currentIndex()
                               )

        # Time Zone Tab
        self.settings.setValue("checkbox_set_time_zone_automatically_using_current_location",
                               self.checkbox_set_time_zone_automatically_using_current_location.isChecked()
                               )

        self.settings.setValue("tz_closest_city",
                               self.tz_closest_city_combobox.currentText()
                               )

        # Clock Tab
        self.settings.setValue("show_the_date_and_time",
                               self.groupbox_show_the_date_and_time.isChecked()
                               )
        self.settings.setValue("display_the_time_with_seconds",
                               self.checkbox_display_the_time_with_seconds.isChecked()
                               )
        self.settings.setValue("show_the_day_of_the_week",
                               self.checkbox_show_the_day_of_the_week.isChecked()
                               )
        self.settings.setValue("show_am_pm",
                               self.checkbox_show_am_pm.isChecked()
                               )
        self.settings.setValue("show_am_pm",
                               self.checkbox_show_am_pm.isChecked()
                               )
        self.settings.setValue("flash_time_separator",
                               self.checkbox_flash_time_separator.isChecked()
                               )
        self.settings.setValue("use_24h_clock",
                               self.checkbox_use_24h_clock.isChecked()
                               )

    def read_settings(self):
        # Entire Application Window
        self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        self.restoreState(self.settings.value("windowState", QByteArray()))

        # Tab
        self.tabWidget.setCurrentIndex(
            self.settings.value("tabWidget", defaultValue=0, type=int)
        )
        # Date and Time Tab
        self.date_and_time_auto_checkbox.setChecked(
            self.settings.value("date_and_time_auto",
                                defaultValue=False,
                                type=bool
                                )
        )

        self.ntp_servers_comboBox.setCurrentIndex(
            self.settings.value("ntp_servers",
                                defaultValue=3,
                                type=int
                                )
        )

        # Time Zone Tab
        self.checkbox_set_time_zone_automatically_using_current_location.setChecked(
            self.settings.value("checkbox_set_time_zone_automatically_using_current_location",
                                defaultValue=False,
                                type=bool
                                )
        )

        self.checkbox_set_time_zone_automatically_using_current_location.setChecked(
            self.settings.value("checkbox_set_time_zone_automatically_using_current_location",
                                defaultValue=False,
                                type=bool
                                )
        )
        self.tz_closest_city_combobox.clear()
        self.tz_closest_city_combobox.addItem(self.settings.value("tz_closest_city",
                                                                  defaultValue="",
                                                                  type=str
                                                                  )
                                              )

        self.__checkbox_set_time_zone_automatically_using_current_location_changed()

        # Clock Tab
        self.groupbox_show_the_date_and_time.setChecked(
            self.settings.value("show_the_date_and_time", defaultValue=True, type=bool)
        )
        self.checkbox_display_the_time_with_seconds.setChecked(
            self.settings.value("display_the_time_with_seconds", defaultValue=True, type=bool)
        )
        self.checkbox_show_the_day_of_the_week.setChecked(
            self.settings.value("show_the_day_of_the_week", defaultValue=True, type=bool)
        )
        self.checkbox_show_am_pm.setChecked(
            self.settings.value("show_am_pm", defaultValue=True, type=bool)
        )
        self.checkbox_flash_time_separator.setChecked(
            self.settings.value("flash_time_separator", defaultValue=False, type=bool)
        )
        self.checkbox_use_24h_clock.setChecked(
            self.settings.value("use_24h_clock", defaultValue=False, type=bool)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DateTimeWindow()
    window.show()
    sys.exit(app.exec_())
