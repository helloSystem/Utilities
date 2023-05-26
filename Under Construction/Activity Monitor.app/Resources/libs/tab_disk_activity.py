#!/usr/bin/env python3

from .bytes2human import bytes2human


class TabDiskActivity(object):
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
            self.label_reads_in_sec_value.setText(
                "%d" % ((self.reads_in_value - self.reads_in_old_value) / self.timer_value)
            )
        else:
            self.reads_in_value = reads_in
            self.reads_in_old_value = self.reads_in_value

        self.label_reads_in_value.setText("%s" % self.reads_in_value)

    def refresh_writes_out(self, writes_out):
        if self.writes_out_old_value is not None:
            self.writes_out_old_value = self.writes_out_value
            self.writes_out_value = writes_out
            self.label_writes_out_sec_value.setText(
                "%d" % ((self.writes_out_value - self.writes_out_old_value) / self.timer_value)
            )
        else:
            self.writes_out_value = writes_out
            self.writes_out_old_value = self.writes_out_value

        self.label_writes_out_value.setText("%s" % self.writes_out_value)

    def refresh_data_read(self, data_read):
        if self.data_read_old_value is not None:
            self.data_read_old_value = self.data_read_value
            self.data_read_value = data_read
            self.label_data_read_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_read_sec_value.color(),
                    bytes2human((self.data_read_value - self.data_read_old_value) / self.timer_value)
                )
            )
        else:
            self.data_read_value = data_read
            self.data_read_old_value = self.data_read_value

        self.label_data_read_value.setText("%s" % bytes2human(self.data_read_value))

    def refresh_data_written(self, data_written):
        if self.data_written_old_value is not None:
            self.data_written_old_value = self.data_written_value
            self.data_written_value = data_written
            self.label_data_written_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_written_sec_value.color(),
                    bytes2human((self.data_written_value - self.data_written_old_value) / self.timer_value)
                )
            )
        else:
            self.data_written_value = data_written
            self.data_written_old_value = self.data_written_value

        self.label_data_written_value.setText("%s" % bytes2human(self.data_written_value))
        self.refresh_bandwidth()

    def refresh_bandwidth(self):
        delta1 = (
                (self.data_written_value - self.data_written_old_value) / self.timer_value
        )
        delta2 = (
                (self.data_read_value - self.data_read_old_value) / self.timer_value
        )
        self.label_bandwidth_value.setText("%s" % bytes2human(delta1 + delta2))
