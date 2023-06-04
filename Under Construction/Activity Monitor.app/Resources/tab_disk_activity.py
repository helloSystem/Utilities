#!/usr/bin/env python3

from utility import bytes2human
from PyQt5.QtWidgets import QLabel, QRadioButton
from widget_color_pickup import ColorButton


class TabDiskActivity(object):
    disk_activity_reads_in_sec_value: QLabel
    disk_activity_reads_in_value: QLabel
    disk_activity_writes_out_sec_value: QLabel
    disk_activity_writes_out_value: QLabel
    disk_activity_data_read_sec_value: QLabel
    disk_activity_data_read_value: QLabel
    disk_activity_data_written_sec_value: QLabel
    disk_activity_data_written_value: QLabel
    disk_activity_bandwidth_value: QLabel
    color_picker_data_read_sec_value: ColorButton
    color_picker_data_written_sec_value: ColorButton
    disk_activity_data_radiobutton: QRadioButton

    def __init__(self, parent=None):
        self.reads_in_value = None
        self.writes_out_value = None
        self.data_read_value = None
        self.data_written_value = None

        self.reads_in_old_value = None
        self.writes_out_old_value = None
        self.data_read_old_value = None
        self.data_written_old_value = None

        self.timer_value = 3

    def refresh_reads_in(self, reads_in):
        if self.reads_in_old_value is not None:
            self.reads_in_old_value = self.reads_in_value
            self.reads_in_value = reads_in
            self.disk_activity_reads_in_sec_value.setText(
                "%d" % ((self.reads_in_value - self.reads_in_old_value) / self.timer_value)
            )
        else:
            self.reads_in_value = reads_in
            self.reads_in_old_value = self.reads_in_value

        self.disk_activity_reads_in_value.setText("%s" % self.reads_in_value)

    def refresh_writes_out(self, writes_out):
        if self.writes_out_old_value is not None:
            self.writes_out_old_value = self.writes_out_value
            self.writes_out_value = writes_out
            self.disk_activity_writes_out_sec_value.setText(
                "%d" % ((self.writes_out_value - self.writes_out_old_value) / self.timer_value)
            )
        else:
            self.writes_out_value = writes_out
            self.writes_out_old_value = self.writes_out_value

        self.disk_activity_writes_out_value.setText("%s" % self.writes_out_value)

    def refresh_data_read(self, data_read):
        if self.data_read_old_value is not None:
            self.data_read_old_value = self.data_read_value
            self.data_read_value = data_read
            self.disk_activity_data_read_sec_value.setText(
                f"{bytes2human((self.data_read_value - self.data_read_old_value) / self.timer_value)}"
            )
        else:
            self.data_read_value = data_read
            self.data_read_old_value = self.data_read_value

        self.disk_activity_data_read_value.setText("%s" % bytes2human(self.data_read_value))

    def refresh_data_written(self, data_written):
        if self.data_written_old_value is not None:
            self.data_written_old_value = self.data_written_value
            self.data_written_value = data_written
            self.disk_activity_data_written_sec_value.setText(
                f"{bytes2human((self.data_written_value - self.data_written_old_value) / self.timer_value)}"
            )
        else:
            self.data_written_value = data_written
            self.data_written_old_value = self.data_written_value

        self.disk_activity_data_written_value.setText("%s" % bytes2human(self.data_written_value))
        self.refresh_disk_activity_bandwidth()

    def refresh_disk_activity_bandwidth(self):
        if self.disk_activity_data_radiobutton.isVisible():
            if self.disk_activity_data_radiobutton.isChecked():
                delta1 = (
                        (self.data_written_value - self.data_written_old_value) / self.timer_value
                )
                delta2 = (
                        (self.data_read_value - self.data_read_old_value) / self.timer_value
                )
                self.disk_activity_bandwidth_value.setText("%s" % bytes2human(delta1 + delta2))
            else:
                delta1 = (
                        (self.writes_out_value - self.writes_out_old_value) / self.timer_value
                )
                delta2 = (
                        (self.reads_in_value - self.reads_in_old_value) / self.timer_value
                )
                io_number = int(round(delta1 + delta2))

                self.disk_activity_bandwidth_value.setText(f"{io_number} ")

    def refresh_color_data_read_sec(self):
        self.disk_activity_data_read_sec_value.setStyleSheet(
            "color: %s;" % self.color_picker_data_read_sec_value.color()
        )

    def refresh_color_data_written_sec(self):
        self.disk_activity_data_written_sec_value.setStyleSheet(
            "color: %s;" % self.color_picker_data_written_sec_value.color()
        )