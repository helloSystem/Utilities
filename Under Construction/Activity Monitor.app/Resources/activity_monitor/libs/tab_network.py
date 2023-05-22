#!/usr/bin/env python3

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
)

from .widget_color_pickup import ColorButton
from .utils import bytes2human


class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.packets_in_value = None
        self.packets_out_value = None
        self.data_received_value = None
        self.data_sent_value = None

        self.packets_in_old_value = None
        self.packets_out_old_value = None
        self.data_received_old_value = None
        self.data_sent_old_value = None

        self.label_packets_in_value = None
        self.label_packets_out_value = None
        self.label_data_received_value = None
        self.label_data_sent_value = None

        self.label_packets_in_sec_value = None
        self.label_packets_out_sec_value = None
        self.label_data_received_sec_value = None
        self.label_data_sent_sec_value = None

        self.color_picker_data_received_sec_value = None
        self.color_picker_data_sent_sec_value = None

        self.label_bandwidth_value = None

        self.timer_value = 3

        self.setupUI()

    def setupUI(self):
        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.label_packets_in_value = QLabel()
        self.label_packets_in_value.setAlignment(Qt.AlignRight)
        self.label_packets_out_value = QLabel()
        self.label_packets_out_value.setAlignment(Qt.AlignRight)
        self.label_packets_in_sec_value = QLabel()
        self.label_packets_in_sec_value.setAlignment(Qt.AlignRight)
        self.label_packets_out_sec_value = QLabel()
        self.label_packets_out_sec_value.setAlignment(Qt.AlignRight)

        self.label_data_received_value = QLabel()
        self.label_data_received_value.setAlignment(Qt.AlignRight)
        self.label_data_sent_value = QLabel()
        self.label_data_sent_value.setAlignment(Qt.AlignRight)
        self.label_data_received_sec_value = QLabel()
        self.label_data_received_sec_value.setAlignment(Qt.AlignRight)
        self.label_data_sent_sec_value = QLabel()
        self.label_data_sent_sec_value.setAlignment(Qt.AlignRight)

        self.color_picker_data_received_sec_value = ColorButton(color="green")
        self.color_picker_data_sent_sec_value = ColorButton(color="red")

        self.label_bandwidth_value = QLabel()
        self.label_bandwidth_value.setAlignment(Qt.AlignCenter)

        label_packets_in = QLabel("Packets in:")
        label_packets_in.setAlignment(Qt.AlignRight)
        label_packets_out = QLabel("Packets out:")
        label_packets_out.setAlignment(Qt.AlignRight)
        label_packets_in_sec = QLabel("Packets in/sec:")
        label_packets_in_sec.setAlignment(Qt.AlignRight)
        label_packets_out_sec = QLabel("Packets out/sec:")
        label_packets_out_sec.setAlignment(Qt.AlignRight)

        label_data_received = QLabel("Data received:")
        label_data_received.setAlignment(Qt.AlignRight)
        label_data_sent = QLabel("Data sent:")
        label_data_sent.setAlignment(Qt.AlignRight)
        label_data_received_sec = QLabel("Data received/sec:")
        label_data_received_sec.setAlignment(Qt.AlignRight)
        label_data_sent_sec = QLabel("Data sent/sec:")
        label_data_sent_sec.setAlignment(Qt.AlignRight)

        layout_grid = QGridLayout()

        layout_grid.addWidget(label_packets_in, 1, 1, 1, 1)
        layout_grid.addWidget(self.label_packets_in_value, 1, 2, 1, 1)
        layout_grid.addWidget(label_packets_out, 2, 1, 1, 1)
        layout_grid.addWidget(self.label_packets_out_value, 2, 2, 1, 1)
        layout_grid.addWidget(label_packets_in_sec, 3, 1, 1, 1)
        layout_grid.addWidget(self.label_packets_in_sec_value, 3, 2, 1, 1)
        layout_grid.addWidget(label_packets_out_sec, 4, 1, 1, 1)
        layout_grid.addWidget(self.label_packets_out_sec_value, 4, 2, 1, 1)

        layout_grid.addWidget(label_data_received, 1, 3, 1, 1)
        layout_grid.addWidget(self.label_data_received_value, 1, 4, 1, 1)
        layout_grid.addWidget(label_data_sent, 2, 3, 1, 1)
        layout_grid.addWidget(self.label_data_sent_value, 2, 4, 1, 1)
        layout_grid.addWidget(label_data_received_sec, 3, 3, 1, 1)
        layout_grid.addWidget(self.label_data_received_sec_value, 3, 4, 1, 1)
        layout_grid.addWidget(self.color_picker_data_received_sec_value, 3, 5, 1, 1)
        layout_grid.addWidget(label_data_sent_sec, 4, 3, 1, 1)
        layout_grid.addWidget(self.label_data_sent_sec_value, 4, 4, 1, 1)
        layout_grid.addWidget(self.color_picker_data_sent_sec_value, 4, 5, 1, 1)

        layout_grid.addWidget(self.label_bandwidth_value, 0, 6, 1, 1)

        # Force position
        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(20, 0, 20, 0)

        self.setLayout(layout_vbox)

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
