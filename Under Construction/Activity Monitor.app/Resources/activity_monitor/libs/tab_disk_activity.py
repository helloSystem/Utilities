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

from .buttons import ColorButton
from .utils import bytes2human
from .utils import to_positive


class TabDiskActivity(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.reads_in_value = None
        self.writes_out_value = None
        self.data_read_value = None
        self.data_written_value = None

        self.reads_in_old_value = None
        self.writes_out_old_value = None
        self.data_read_old_value = None
        self.data_written_old_value = None

        self.label_reads_in_value = None
        self.label_writes_out_value = None
        self.label_data_read_value = None
        self.label_data_written_value = None

        self.label_reads_in_sec_value = None
        self.label_writes_out_sec_value = None
        self.label_data_read_sec_value = None
        self.label_data_written_sec_value = None

        self.color_picker_data_read_sec_value = None
        self.color_picker_data_written_sec_value = None

        self.label_bandwidth_value = None

        self.timer_value = 3

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.label_reads_in_value = QLabel()
        self.label_reads_in_value.setAlignment(Qt.AlignRight)
        self.label_writes_out_value = QLabel()
        self.label_writes_out_value.setAlignment(Qt.AlignRight)
        self.label_reads_in_sec_value = QLabel()
        self.label_reads_in_sec_value.setAlignment(Qt.AlignRight)
        self.label_writes_out_sec_value = QLabel()
        self.label_writes_out_sec_value.setAlignment(Qt.AlignRight)

        self.label_data_read_value = QLabel()
        self.label_data_read_value.setAlignment(Qt.AlignRight)
        self.label_data_written_value = QLabel()
        self.label_data_written_value.setAlignment(Qt.AlignRight)
        self.label_data_read_sec_value = QLabel()
        self.label_data_read_sec_value.setAlignment(Qt.AlignRight)
        self.label_data_written_sec_value = QLabel()
        self.label_data_written_sec_value.setAlignment(Qt.AlignRight)

        self.color_picker_data_read_sec_value = ColorButton(color="green")
        self.color_picker_data_written_sec_value = ColorButton(color="red")

        self.label_bandwidth_value = QLabel()
        self.label_bandwidth_value.setAlignment(Qt.AlignCenter)

        label_reads_in = QLabel("Reads in:")
        label_reads_in.setAlignment(Qt.AlignRight)
        label_writes_out = QLabel("Writes out:")
        label_writes_out.setAlignment(Qt.AlignRight)
        label_reads_in_sec = QLabel("Reads in/sec:")
        label_reads_in_sec.setAlignment(Qt.AlignRight)
        label_writes_out_sec = QLabel("Writes out/sec:")
        label_writes_out_sec.setAlignment(Qt.AlignRight)

        label_data_read = QLabel("Data read:")
        label_data_read.setAlignment(Qt.AlignRight)
        label_data_written = QLabel("Data written:")
        label_data_written.setAlignment(Qt.AlignRight)
        label_data_read_sec = QLabel("Data read/sec:")
        label_data_read_sec.setAlignment(Qt.AlignRight)
        label_data_written_sec = QLabel("Data written/sec:")
        label_data_written_sec.setAlignment(Qt.AlignRight)

        layout_grid = QGridLayout()

        layout_grid.addWidget(label_reads_in, 1, 1, 1, 1)
        layout_grid.addWidget(self.label_reads_in_value, 1, 2, 1, 1)
        layout_grid.addWidget(label_writes_out, 2, 1, 1, 1)
        layout_grid.addWidget(self.label_writes_out_value, 2, 2, 1, 1)
        layout_grid.addWidget(label_reads_in_sec, 3, 1, 1, 1)
        layout_grid.addWidget(self.label_reads_in_sec_value, 3, 2, 1, 1)
        layout_grid.addWidget(label_writes_out_sec, 4, 1, 1, 1)
        layout_grid.addWidget(self.label_writes_out_sec_value, 4, 2, 1, 1)

        layout_grid.addWidget(label_data_read, 1, 3, 1, 1)
        layout_grid.addWidget(self.label_data_read_value, 1, 4, 1, 1)
        layout_grid.addWidget(label_data_written, 2, 3, 1, 1)
        layout_grid.addWidget(self.label_data_written_value, 2, 4, 1, 1)
        layout_grid.addWidget(label_data_read_sec, 3, 3, 1, 1)
        layout_grid.addWidget(self.label_data_read_sec_value, 3, 4, 1, 1)
        layout_grid.addWidget(self.color_picker_data_read_sec_value, 3, 5, 1, 1)
        layout_grid.addWidget(label_data_written_sec, 4, 3, 1, 1)
        layout_grid.addWidget(self.label_data_written_sec_value, 4, 4, 1, 1)
        layout_grid.addWidget(self.color_picker_data_written_sec_value, 4, 5, 1, 1)

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
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh_reads_in(self, reads_in):
        if self.reads_in_old_value:
            self.reads_in_old_value = self.reads_in_value
            self.reads_in_value = to_positive(reads_in)
            delta = int((self.reads_in_value - self.reads_in_old_value) / self.timer_value)
            self.label_reads_in_sec_value.setText("%s" % delta)

        else:
            self.reads_in_value = to_positive(reads_in)
            self.reads_in_old_value = self.reads_in_value

        self.label_reads_in_value.setText("%s" % self.reads_in_value)

    def refresh_writes_out(self, writes_out):
        if self.writes_out_old_value:
            self.writes_out_old_value = self.writes_out_value
            self.writes_out_value = to_positive(writes_out)
            delta = int((self.writes_out_value - self.writes_out_old_value) / self.timer_value)
            self.label_writes_out_sec_value.setText("%s" % delta)

        else:
            self.writes_out_value = to_positive(writes_out)
            self.writes_out_old_value = self.writes_out_value

        self.label_writes_out_value.setText("%s" % self.writes_out_value)

    def refresh_data_read(self, data_read):
        if self.data_read_old_value:
            self.data_read_old_value = self.data_read_value
            self.data_read_value = to_positive(data_read)

            delta = (
                int((self.data_read_value - self.data_read_old_value) / self.timer_value)
            )
            self.label_data_read_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_read_sec_value.color(),
                    bytes2human(delta)
                )
            )
        else:
            self.data_read_value = to_positive(data_read)
            self.data_read_old_value = self.data_read_value

        self.label_data_read_value.setText("%s" % bytes2human(self.data_read_value))

    def refresh_data_written(self, data_written):
        if self.data_written_old_value:
            self.data_written_old_value = self.data_written_value
            self.data_written_value = to_positive(data_written)

            delta = (
                int((self.data_written_value - self.data_written_old_value) / self.timer_value)
            )

            self.label_data_written_sec_value.setText(
                "<font color=%s>%s</font>" % (
                    self.color_picker_data_written_sec_value.color(),
                    bytes2human(delta)
                )
            )
        else:
            self.data_written_value = to_positive(data_written)
            self.data_written_old_value = self.data_written_value

        self.label_data_written_value.setText("%s" % bytes2human(self.data_written_value))

        self.refresh_bandwidth()

    def refresh_bandwidth(self):
        delta1 = (
            int((self.data_written_value - self.data_written_old_value) / self.timer_value)
        )
        delta2 = (
            int((self.data_read_value - self.data_read_old_value) / self.timer_value)
        )

        self.label_bandwidth_value.setText("%s" % bytes2human(delta1 + delta2))
