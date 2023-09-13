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
            self.refresh_packets_in_sec_value()
        else:
            self.packets_in_value = packets_in
            self.packets_in_old_value = self.packets_in_value

        self.refresh_packets_in_value()

    def refresh_packets_in_sec_value(self):
        packets_in_sec_value = (
            f"{int(round(((self.packets_in_value - self.packets_in_old_value) / self.timer_value)))}"
        )
        if (
                self.network_packets_in_sec_value.isVisible()
                and self.network_packets_in_sec_value.text() != packets_in_sec_value
        ):
            self.network_packets_in_sec_value.setText(packets_in_sec_value)

    def refresh_packets_in_value(self):
        if (
            self.network_packets_in_value.isVisible()
            and self.network_packets_in_value.text() != f"{self.packets_in_value}"
        ):
            self.network_packets_in_value.setText(f"{self.packets_in_value}")

    def refresh_packets_out(self, packets_out):
        if self.packets_out_old_value:
            self.packets_out_old_value = self.packets_out_value
            self.packets_out_value = packets_out

            packets_out_sec_value = (
                f"{int(round(((self.packets_out_value - self.packets_out_old_value) / self.timer_value)))}"
            )
            if (
                self.network_packets_out_sec_value.isVisible()
                and self.network_packets_out_sec_value.text() != packets_out_sec_value
            ):
                self.network_packets_out_sec_value.setText(packets_out_sec_value)
        else:
            self.packets_out_value = packets_out
            self.packets_out_old_value = self.packets_out_value

        if (
            self.network_packets_out_value.isVisible()
            and self.network_packets_out_value.text() != f"{self.packets_out_value}"
        ):
            self.network_packets_out_value.setText(f"{self.packets_out_value}")

    def refresh_data_received(self, data_received):
        if self.data_received_old_value:
            self.data_received_old_value = self.data_received_value
            self.data_received_value = data_received

            data_received_sec_value = (
                f"{bytes2human((self.data_received_value - self.data_received_old_value) / self.timer_value)}"
            )
            if (
                self.network_data_received_sec_value.isVisible()
                and self.network_data_received_sec_value.text() != data_received_sec_value
            ):
                self.network_data_received_sec_value.setText(data_received_sec_value)
        else:
            self.data_received_value = data_received
            self.data_received_old_value = self.data_received_value

        data_received_value = f"{bytes2human(self.data_received_value)}"
        if (
            self.network_data_received_value.isVisible()
            and self.network_data_received_value.text() != data_received_value
        ):
            self.network_data_received_value.setText(data_received_value)

    def refresh_data_sent(self, data_sent):
        if self.data_sent_old_value:
            self.data_sent_old_value = self.data_sent_value
            self.data_sent_value = data_sent

            data_sent_sec_value = (
                f"{bytes2human((self.data_sent_value - self.data_sent_old_value) / self.timer_value)}"
            )
            if (
                self.network_data_sent_sec_value.isVisible()
                and self.network_data_sent_sec_value.text() != data_sent_sec_value
            ):
                self.network_data_sent_sec_value.setText(data_sent_sec_value)
        else:
            self.data_sent_value = data_sent
            self.data_sent_old_value = self.data_sent_value

        data_sent_value = f"{bytes2human(self.data_sent_value)}"
        if (
            self.network_data_sent_value.isVisible()
            and self.network_data_sent_value.text() != data_sent_value
        ):
            self.network_data_sent_value.setText(data_sent_value)

        self.refresh_network_bandwidth()

    def refresh_network_bandwidth(self):
        if self.network_data_radiobutton.isChecked():
            delta1 = (self.data_sent_value - self.data_sent_old_value) / self.timer_value
            delta2 = (self.data_received_value - self.data_received_old_value) / self.timer_value
            bandwidth_value = f"{bytes2human(delta1 + delta2)}"
        else:
            delta1 = (self.packets_out_value - self.packets_out_old_value) / self.timer_value
            delta2 = (self.packets_in_value - self.packets_in_old_value) / self.timer_value
            bandwidth_value = int(round(delta1 + delta2))

        if (
            self.network_bandwidth_value.isVisible()
            and self.network_bandwidth_value != f"{bandwidth_value} "
        ):
            self.network_bandwidth_value.setText(f"{bandwidth_value} ")

    def refresh_color_data_received_sec(self):
        self.network_data_received_sec_value.setStyleSheet(
            "color: %s;" % self.color_picker_data_received_sec_value.color()
        )

    def refresh_color_data_sent_sec(self):
        self.network_data_sent_sec_value.setStyleSheet("color: %s;" % self.color_picker_data_sent_sec_value.color())
