#!/usr/bin/env python3

from utility import bytes2human
from PyQt5.QtWidgets import QLabel, QRadioButton
from widget_color_pickup import ColorButton


class TabNetwork(object):
    network_packets_in_sec_value: QLabel
    network_packets_in_value: QLabel
    network_packets_out_sec_value: QLabel
    network_packets_out_value: QLabel
    network_data_received_sec_value: QLabel
    network_data_received_value: QLabel
    network_data_sent_sec_value: QLabel
    network_data_sent_value: QLabel
    network_bandwidth_unit: QLabel
    network_bandwidth_value: QLabel
    color_picker_data_received_sec_value: ColorButton
    color_picker_data_sent_sec_value: ColorButton
    network_data_radiobutton: QRadioButton
    network_packets_radiobutton: QRadioButton
    timer_value: int

    def __init__(self):
        self.data_sent_value = None
        self.packets_out_value = None
        self.packets_in_value = None
        self.data_received_value = None
        self.packets_in_old_value = None
        self.packets_out_old_value = None
        self.data_received_old_value = None
        self.data_sent_old_value = None

    def refresh_packets_in(self, packets_in):
        if self.packets_in_old_value:
            self.packets_in_old_value = self.packets_in_value
            self.packets_in_value = packets_in
            self.network_packets_in_sec_value.setText(
                "%d" % ((self.packets_in_value - self.packets_in_old_value) / self.timer_value)
            )
        else:
            self.packets_in_value = packets_in
            self.packets_in_old_value = self.packets_in_value

        self.network_packets_in_value.setText("%s" % self.packets_in_value)

    def refresh_packets_out(self, packets_out):
        if self.packets_out_old_value:
            self.packets_out_old_value = self.packets_out_value
            self.packets_out_value = packets_out
            self.network_packets_out_sec_value.setText(
                "%d" % ((self.packets_out_value - self.packets_out_old_value) / self.timer_value)
            )
        else:
            self.packets_out_value = packets_out
            self.packets_out_old_value = self.packets_out_value

        self.network_packets_out_value.setText("%s" % self.packets_out_value)

    def refresh_data_received(self, data_received):
        if self.data_received_old_value:
            self.data_received_old_value = self.data_received_value
            self.data_received_value = data_received
            self.network_data_received_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_received_sec_value.color(),
                    bytes2human((self.data_received_value - self.data_received_old_value) / self.timer_value)
                )
            )
        else:
            self.data_received_value = data_received
            self.data_received_old_value = self.data_received_value

        self.network_data_received_value.setText("%s" % bytes2human(self.data_received_value))

    def refresh_data_sent(self, data_sent):
        if self.data_sent_old_value:
            self.data_sent_old_value = self.data_sent_value
            self.data_sent_value = data_sent
            self.network_data_sent_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_sent_sec_value.color(),
                    bytes2human((self.data_sent_value - self.data_sent_old_value) / self.timer_value)
                )
            )
        else:
            self.data_sent_value = data_sent
            self.data_sent_old_value = self.data_sent_value

        self.network_data_sent_value.setText("%s" % bytes2human(self.data_sent_value))
        self.refresh_network_bandwidth()

    def refresh_network_bandwidth(self):
        if self.network_data_radiobutton.isChecked():
            delta1 = (
                    (self.data_sent_value - self.data_sent_old_value) / self.timer_value
            )
            delta2 = (
                    (self.data_received_value - self.data_received_old_value) / self.timer_value
            )
            self.network_bandwidth_value.setText(f"{bytes2human(delta1 + delta2)}")
        else:
            delta1 = (
                    (self.packets_out_value - self.packets_out_old_value) / self.timer_value
            )
            delta2 = (
                    (self.packets_in_value - self.packets_in_old_value) / self.timer_value
            )
            packet_number = int(round(delta1 + delta2))

            self.network_bandwidth_value.setText(f"{packet_number} ")


