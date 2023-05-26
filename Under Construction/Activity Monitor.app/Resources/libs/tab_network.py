#!/usr/bin/env python3

from .bytes2human import bytes2human


class TabNetwork(object):
    def __init__(self, parent=None):
        super().__init__()

        self.packets_in_old_value = None
        self.packets_out_old_value = None
        self.data_received_old_value = None
        self.data_sent_old_value = None

    def refresh_packets_in(self, packets_in):
        if self.packets_in_old_value:
            self.packets_in_old_value = self.packets_in_value
            self.packets_in_value = packets_in
            self.label_packets_in_sec_value.setText(
                "%d" % ((self.packets_in_value - self.packets_in_old_value) / self.timer_value)
            )
        else:
            self.packets_in_value = packets_in
            self.packets_in_old_value = self.packets_in_value

        self.label_packets_in_value.setText("%s" % self.packets_in_value)

    def refresh_packets_out(self, packets_out):
        if self.packets_out_old_value:
            self.packets_out_old_value = self.packets_out_value
            self.packets_out_value = packets_out
            self.label_packets_out_sec_value.setText(
                "%d" % ((self.packets_out_value - self.packets_out_old_value) / self.timer_value)
            )
        else:
            self.packets_out_value = packets_out
            self.packets_out_old_value = self.packets_out_value

        self.label_packets_out_value.setText("%s" % self.packets_out_value)

    def refresh_data_received(self, data_received):
        if self.data_received_old_value:
            self.data_received_old_value = self.data_received_value
            self.data_received_value = data_received
            self.label_data_received_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_received_sec_value.color(),
                    bytes2human((self.data_received_value - self.data_received_old_value) / self.timer_value)
                )
            )
        else:
            self.data_received_value = data_received
            self.data_received_old_value = self.data_received_value

        self.label_data_received_value.setText("%s" % bytes2human(self.data_received_value))

    def refresh_data_sent(self, data_sent):
        if self.data_sent_old_value:
            self.data_sent_old_value = self.data_sent_value
            self.data_sent_value = data_sent
            self.label_data_sent_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_sent_sec_value.color(),
                    bytes2human((self.data_sent_value - self.data_sent_old_value) / self.timer_value)
                )
            )
        else:
            self.data_sent_value = data_sent
            self.data_sent_old_value = self.data_sent_value

        self.label_data_sent_value.setText("%s" % bytes2human(self.data_sent_value))
        self.refresh_bandwidth()

    def refresh_bandwidth(self):
        delta1 = (
                (self.data_sent_value - self.data_sent_old_value) / self.timer_value
        )
        delta2 = (
                (self.data_received_value - self.data_received_old_value) / self.timer_value
        )
        self.label_bandwidth_value.setText("%s" % bytes2human(delta1 + delta2))
