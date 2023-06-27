#!/usr/bin/env python3

# FIXME: The spinner is not shown; we need to fix this by using threading? Is there a better way?
# TODO: Implement manual time zone setting in the time zone tab
# TODO: Implement manual date and time setting in the date and time tab

import subprocess
import sys
import os
import time
from PyQt5.QtCore import Qt, QDateTime, QTimer, QDate
from PyQt5.QtWidgets import (QApplication, QDateTimeEdit, QGridLayout,
                             QGroupBox, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QTabWidget, QVBoxLayout, QWidget)
from PyQt5.QtGui import QMovie, QKeyEvent, QPixmap
from PyQt5.QtCore import QEvent

from date_and_time_ui import Ui_MainWindow
from property_date_time_auto import DateTimeAutomatically


class DateTimeWindow(QMainWindow, Ui_MainWindow, DateTimeAutomatically):
    def __init__(self):
        super().__init__()
        DateTimeAutomatically.__init__(self)
        self.setupUi(self)
        self.analog_clock_widget.show()
        self.timer = QTimer()
        self.timer.start(1000)

        self.initial_state()
        self.signalsConnect()

    def signalsConnect(self):
        self.timer.timeout.connect(self.refresh)
        self.actionHelpAbout.triggered.connect(self.show_about)
        self.DateTimeAutomaticallyChanged.connect(self.__date_and_time_automatically_changed)
        self.date_and_time_auto_checkbox.toggled.connect(self.__date_and_time_automatically_changed)
        self.dt_set_date_time_manual.dateTimeChanged.connect(
            lambda: self.timer.stop() if self.dt_set_date_time_manual.dateTime().toString(
                'H:mm:ss AP') != self.get_current_datetime().toString('H:mm:ss AP') else None)

    def initial_state(self):
        self.dt_set_date_time_manual.setDateTime(self.get_current_datetime())
        self.setDateTimeAutomatically(False)
        self.tz_time_zone_label.setText(self.get_current_time_zone())

    def refresh(self):
        self.dt_set_date_time_manual.setDateTime(self.get_current_datetime())
        self.dt_set_date_manual.setDate(self.get_current_date())
        #
        # # Undo, cut, copy, paste, and delete actions. Undo is disabled.
        # # They have the default shortcuts. When invoked, the corresponding
        # # shortcut is sent to the currently focused widget.
        # undo_action = self.edit_menu.addAction("Undo")
        # undo_action.setShortcut("Ctrl+Z")
        # undo_action.setEnabled(False)
        # self.edit_menu.addSeparator()
        # cut_action = self.edit_menu.addAction("Cut")
        # cut_action.setShortcut("Ctrl+X")
        # cut_action.triggered.connect(lambda: self.send_shortcut(
        #     Qt.Key_X, Qt.ControlModifier))
        # copy_action = self.edit_menu.addAction("Copy")
        # copy_action.setShortcut("Ctrl+C")
        # copy_action.triggered.connect(lambda: self.send_shortcut(
        #     Qt.Key_C, Qt.ControlModifier))
        # paste_action = self.edit_menu.addAction("Paste")
        # paste_action.setShortcut("Ctrl+V")
        # paste_action.triggered.connect(lambda: self.send_shortcut(
        #     Qt.Key_V, Qt.ControlModifier))
        # delete_action = self.edit_menu.addAction("Delete")
        # delete_action.setShortcut("Del")
        # delete_action.triggered.connect(lambda: self.send_shortcut(
        #     Qt.Key_Delete, Qt.NoModifier))
        # self.edit_menu.addSeparator()
        #
        # self.edit_menu.addAction("Set Date and Time automatically",
        #                          self.set_date_time_auto)
        # self.edit_menu.addAction("Set time zone automatically",
        #                          self.set_time_zone_auto)
        #
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

    def get_current_datetime(self):
        # try:
        #     # Get the current date and time
        #     result = subprocess.run(["date", "+%Y-%m-%d %H:%M:%S"],
        #                             capture_output=True, text=True, check=True)
        #     return QDateTime.fromString(result.stdout.strip(), "yyyy-MM-dd hh:mm:ss")
        # except subprocess.CalledProcessError as e:
        #     self.show_error_dialog("Error getting current Date and Time",
        #                            f"An error occurred while getting the current Date and Time: {e.stderr}")
        return QDateTime.currentDateTime()

    def get_current_date(self):
        return QDate.currentDate()

    def set_date_time_manual(self):
        self.spinner.show()
        # 202304151224.10 = Sa. 15 Apr. 2023 12:24:10 CEST
        new_date_time = self.dt_set_date_time_manual.dateTime().toString(
            "yyyyMMddhhmm.ss")
        print(new_date_time)
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
        self.spinner.show()
        # Wait one second before setting the date and time automatically
        time.sleep(1)
        try:
            # Set the date and time automatically using NTP
            subprocess.run(["sudo", "ntpdate", "-v", "-b",
                            "-u", "pool.ntp.org"], check=True)
            self.dt_set_date_time_manual.setDateTime(
                self.get_current_datetime())
        except subprocess.CalledProcessError as e:
            self.show_error_dialog("Error setting Date and Time automatically",
                                   f"An error occurred while setting the Date and Time automatically: {e.stderr}")
        # Restart the timer if it is not running
        if not self.timer.isActive():
            self.timer.start()
        self.spinner.hide()

    def set_time_zone_auto(self):
        try:
            # Set the time zone automatically using NTP
            subprocess.run(["sudo", "ntpdate", "-v", "-b",
                            "-u", "pool.ntp.org"], check=True)
        except subprocess.CalledProcessError as e:
            self.show_error_dialog("Error setting time zone automatically",
                                   f"An error occurred while setting the time zone automatically: {e.stderr}")

    def get_current_time_zone(self):
        with open('/etc/timezone') as file:
            data = file.readlines()

        for line in data:
            if line.startswith("#"):
                pass
            else:
                return line.strip("\n")

    def show_error_dialog(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
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

    def __date_and_time_automatically_changed(self):
        if self.date_and_time_auto_checkbox.isChecked():
            self.ntp_servers_comboBox.setEnabled(True)

            self.dt_set_date_time_manual.setEnabled(False)
            self.dt_use_24h_clock.setEnabled(False)
            self.analog_clock_widget.setEnabled(False)

            self.dt_set_date_manual.setEnabled(False)
            self.calendarWidget.setEnabled(False)
        else:
            self.ntp_servers_comboBox.setEnabled(False)

            self.dt_set_date_time_manual.setEnabled(True)
            self.dt_use_24h_clock.setEnabled(True)
            self.analog_clock_widget.setEnabled(True)

            self.dt_set_date_manual.setEnabled(True)
            self.calendarWidget.setEnabled(True)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DateTimeWindow()
    window.show()
    sys.exit(app.exec_())
