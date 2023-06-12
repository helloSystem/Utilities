#!/usr/bin/env python3

from utility import bytes2human
from PyQt5.QtWidgets import QLabel, QRadioButton
from widget_color_pickup import ColorButton
from property_disk_io_counters import DiskIOCounters
from PyQt5.QtGui import QColor


class TabDiskActivity(DiskIOCounters):
    disk_io_counters_read_count = int
    disk_io_counters_write_count = int
    disk_io_counters_read_bytes = int
    disk_io_counters_write_bytes = int
    disk_io_counters_read_time = int
    disk_io_counters_write_time = int
    disk_io_counters_busy_time = int
    disk_io_counters_read_merged_count = int
    disk_io_counters_write_merged_count = int

    disk_io_counters_read_count_color = QColor
    disk_io_counters_write_count_color = QColor
    disk_io_counters_read_bytes_color = QColor
    disk_io_counters_write_bytes_color = QColor
    disk_io_counters_read_time_color = QColor
    disk_io_counters_write_time_color = QColor
    disk_io_counters_busy_time_color = QColor
    disk_io_counters_read_merged_count_color = QColor
    disk_io_counters_write_merged_count_color = QColor

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

    def __init__(self, *args, **kwargs):
        super(TabDiskActivity, self).__init__()
        DiskIOCounters.__init__(self)

        self.disk_io_counters_read_count_old_value = None
        self.disk_io_counters_write_count_old_value = None
        self.disk_io_counters_read_bytes_old_value = None
        self.disk_io_counters_write_bytes_old_value = None

        self.timer_value = 3

        self.disk_io_counters_read_count_changed.connect(self.refresh_disk_io_counters_read_count)
        self.disk_io_counters_write_count_changed.connect(self.refresh_disk_io_counters_write_count)
        self.disk_io_counters_read_bytes_changed.connect(self.refresh_disk_io_counters_read_bytes)
        self.disk_io_counters_write_bytes_changed.connect(self.refresh_disk_io_counters_write_bytes)
        self.disk_io_counters_read_time_changed.connect(self.refresh_disk_io_counters_read_time)
        self.disk_io_counters_write_time_changed.connect(self.refresh_disk_io_counters_write_time)
        self.disk_io_counters_busy_time_changed.connect(self.refresh_disk_io_counters_busy_time)
        self.disk_io_counters_read_merged_count_changed.connect(self.refresh_disk_io_counters_read_merged_count)
        self.disk_io_counters_write_merged_count_changed.connect(self.refresh_disk_io_counters_write_merged_count)

    def refresh_disk_io_counters_read_count(self):
        self.disk_io_counters_read_count_old_value = self.disk_io_counters_read_count
        self.disk_activity_reads_in_value.setText(f"{self.disk_io_counters_read_count}")
        # if self.reads_in_old_value is not None:
        #     self.disk_io_counters_read_count_old_value = self.disk_io_counters_read_count
        #     self.disk_io_counters_read_count_old_value = reads_in
        #     reads_in_sec_value = f"{int(round(((self.disk_io_counters_read_count_old_value - self.reads_in_old_value) / self.timer_value)))}"
        #     if (
        #             self.disk_activity_reads_in_sec_value.isVisible()
        #             and self.disk_activity_reads_in_sec_value.text() != reads_in_sec_value
        #     ):
        #         self.disk_activity_reads_in_sec_value.setText(reads_in_sec_value)
        # else:
        #     self.disk_io_counters_read_count_old_value = reads_in
        #     self.reads_in_old_value = self.disk_io_counters_read_count_old_value
        #
        # if (
        #         self.disk_activity_reads_in_value.isVisible()
        #         and self.disk_activity_reads_in_value.text() != f"{self.disk_io_counters_read_count_old_value}"
        # ):
        #     self.disk_activity_reads_in_value.setText(f"{self.disk_io_counters_read_count_old_value}")

    def refresh_disk_io_counters_write_count(self):
        pass

    def refresh_disk_io_counters_read_bytes(self):
        pass

    def refresh_disk_io_counters_write_bytes(self):
        pass

    def refresh_disk_io_counters_read_time(self):
        pass

    def refresh_disk_io_counters_write_time(self):
        pass

    def refresh_disk_io_counters_busy_time(self):
        pass

    def refresh_disk_io_counters_read_merged_count(self):
        pass

    def refresh_disk_io_counters_write_merged_count(self):
        pass

    def refresh_reads_in(self, reads_in):
        pass
        # if self.reads_in_old_value is not None:
        #     self.reads_in_old_value = self.disk_io_counters_read_count_old_value
        #     self.disk_io_counters_read_count_old_value = reads_in
        #     reads_in_sec_value = f"{int(round(((self.disk_io_counters_read_count_old_value - self.reads_in_old_value) / self.timer_value)))}"
        #     if (
        #         self.disk_activity_reads_in_sec_value.isVisible()
        #         and self.disk_activity_reads_in_sec_value.text() != reads_in_sec_value
        #     ):
        #         self.disk_activity_reads_in_sec_value.setText(reads_in_sec_value)
        # else:
        #     self.disk_io_counters_read_count_old_value = reads_in
        #     self.reads_in_old_value = self.disk_io_counters_read_count_old_value
        #
        # if (
        #     self.disk_activity_reads_in_value.isVisible()
        #     and self.disk_activity_reads_in_value.text() != f"{self.disk_io_counters_read_count_old_value}"
        # ):
        #     self.disk_activity_reads_in_value.setText(f"{self.disk_io_counters_read_count_old_value}")

    def refresh_writes_out(self, writes_out):
        pass
        # if self.writes_out_old_value is not None:
        #     self.writes_out_old_value = self.disk_io_counters_write_count_old_value
        #     self.disk_io_counters_write_count_old_value = writes_out
        #
        #     writes_out_sec_value = (
        #         f"{int(round(((self.disk_io_counters_write_count_old_value - self.writes_out_old_value) / self.timer_value)))}"
        #     )
        #     if (
        #         self.disk_activity_writes_out_sec_value.isVisible()
        #         and self.disk_activity_writes_out_sec_value.text() != writes_out_sec_value
        #     ):
        #         self.disk_activity_writes_out_sec_value.setText(writes_out_sec_value)
        # else:
        #     self.disk_io_counters_write_count_old_value = writes_out
        #     self.writes_out_old_value = self.disk_io_counters_write_count_old_value
        #
        # if (
        #     self.disk_activity_writes_out_value.isVisible()
        #     and self.disk_activity_writes_out_value.text() != f"{self.disk_io_counters_write_count_old_value}"
        # ):
        #     self.disk_activity_writes_out_value.setText(f"{self.disk_io_counters_write_count_old_value}")

    def refresh_data_read(self, data_read):
        pass
        # if self.data_read_old_value is not None:
        #     self.data_read_old_value = self.disk_io_counters_read_bytes_old_value
        #     self.disk_io_counters_read_bytes_old_value = data_read
        #
        #     data_read_sec = f"{bytes2human((self.disk_io_counters_read_bytes_old_value - self.data_read_old_value) / self.timer_value)}"
        #     if (
        #         self.disk_activity_data_read_sec_value.isVisible()
        #         and self.disk_activity_data_read_sec_value != data_read_sec
        #     ):
        #         self.disk_activity_data_read_sec_value.setText(data_read_sec)
        # else:
        #     self.disk_io_counters_read_bytes_old_value = data_read
        #     self.data_read_old_value = self.disk_io_counters_read_bytes_old_value
        #
        # data_read_value = f"{bytes2human(self.disk_io_counters_read_bytes_old_value)}"
        # if (
        #     self.disk_activity_data_read_value.isVisible()
        #     and self.disk_activity_data_read_value.text() != data_read_value
        # ):
        #     self.disk_activity_data_read_value.setText(data_read_value)

    def refresh_data_written(self, data_written):
        pass
        # if self.data_written_old_value is not None:
        #     self.data_written_old_value = self.disk_io_counters_write_bytes_old_value
        #     self.disk_io_counters_write_bytes_old_value = data_written
        #
        #     data_written_sec_value = (
        #         f"{bytes2human((self.disk_io_counters_write_bytes_old_value - self.data_written_old_value) / self.timer_value)}"
        #     )
        #     if (
        #         self.disk_activity_data_written_sec_value.isVisible()
        #         and self.disk_activity_data_written_sec_value.text() != data_written_sec_value
        #     ):
        #         self.disk_activity_data_written_sec_value.setText(data_written_sec_value)
        # else:
        #     self.disk_io_counters_write_bytes_old_value = data_written
        #     self.data_written_old_value = self.disk_io_counters_write_bytes_old_value
        #
        # data_written_value = f"{bytes2human(self.disk_io_counters_write_bytes_old_value)}"
        # if (
        #     self.disk_activity_data_written_value.isVisible()
        #     and self.disk_activity_data_written_value.text() != data_written_value
        # ):
        #     self.disk_activity_data_written_value.setText(data_written_value)
        #
        # self.refresh_disk_activity_bandwidth()

    def refresh_disk_activity_bandwidth(self):
        if self.disk_activity_data_radiobutton.isVisible():
            if self.disk_activity_data_radiobutton.isChecked():
                delta1 = (self.disk_io_counters_write_bytes_old_value - self.data_written_old_value) / self.timer_value
                delta2 = (self.disk_io_counters_read_bytes_old_value - self.data_read_old_value) / self.timer_value
                bandwidth_value = bytes2human(delta1 + delta2)
            else:
                delta1 = (self.disk_io_counters_write_count_old_value - self.writes_out_old_value) / self.timer_value
                delta2 = (self.disk_io_counters_read_count_old_value - self.reads_in_old_value) / self.timer_value
                bandwidth_value = int(round(delta1 + delta2))
            if (
                self.disk_activity_bandwidth_value.isVisible()
                and self.disk_activity_bandwidth_value != f"{bandwidth_value} "
            ):
                self.disk_activity_bandwidth_value.setText(f"{bandwidth_value} ")

    def refresh_color_data_read_sec(self):
        self.disk_activity_data_read_sec_value.setStyleSheet(
            "color: %s;" % self.color_picker_data_read_sec_value.color()
        )

    def refresh_color_data_written_sec(self):
        self.disk_activity_data_written_sec_value.setStyleSheet(
            "color: %s;" % self.color_picker_data_written_sec_value.color()
        )
