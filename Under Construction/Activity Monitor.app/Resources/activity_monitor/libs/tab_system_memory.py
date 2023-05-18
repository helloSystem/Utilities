#!/usr/bin/env python3

import psutil
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtProperty,
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
from .chartpie import ChartPieItem, ChartPie


class TabSystemMemory(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Internal class settings
        self.__virtual_memory = psutil.virtual_memory()
        self.memory_os_capability = {
            "total": hasattr(self.__virtual_memory, "total"),
            "available": hasattr(self.__virtual_memory, "available"),
            "percent": hasattr(self.__virtual_memory, "percent"),
            "used": hasattr(self.__virtual_memory, "used"),
            "free": hasattr(self.__virtual_memory, "free"),
            "active": hasattr(self.__virtual_memory, "active"),
            "inactive": hasattr(self.__virtual_memory, "inactive"),
            "buffers": hasattr(self.__virtual_memory, "buffers"),
            "cached": hasattr(self.__virtual_memory, "cached"),
            "shared": hasattr(self.__virtual_memory, "shared"),
            "slab": hasattr(self.__virtual_memory, "slab"),
            "wired": hasattr(self.__virtual_memory, "wired"),
        }
        self.lbl_free_value = None
        self.color_button_free = None
        self.lbl_buffers_value = None
        self.lbl_wired_value = None
        self.lbl_active_value = None
        self.color_button_wired = None
        self.color_button_active = None
        self.lbl_cached_value = None
        self.lbl_inactive_value = None
        self.color_button_inactive = None
        self.lbl_used_value = None
        self.lbl_available_value = None
        self.lbl_shared_value = None
        self.lbl_slab_value = None
        self.lbl_total_value = None

        # System Memory Chart Pie
        self.chart_pie = None
        self.chart_pie_item_free = None
        self.chart_pie_item_wired = None
        self.chart_pie_item_active = None
        self.chart_pie_item_inactive = None

        self.setupUI()

    def setupUI(self):
        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout_grid = QGridLayout()
        self.chart_pie = ChartPie()

        # layout_grid.setRowStretch(0 | 1 | 2 | 3 | 4, 1)
        # #
        # layout_grid.setColumnStretch(0 | 1 | 2, 20)
        # layout_grid.setColumnStretch(3 | 4, 0)
        # layout_grid.setColumnStretch(5, 40)

        # widget Position management
        grid_col = 0
        grid_row = 0

        if self.memory_os_capability["free"]:
            # Free label
            lbl_free = QLabel("Free:")
            lbl_free.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_free_value = QLabel("")
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setToolTip(
                "Memory not being used at all (zeroed) that is readily available<br>Note that this doesn't reflect the "
                "actual memory available (use available instead). total - used does not necessarily match free. "
            )
            # Free Color button
            self.color_button_free = ColorButton(color="green")
            self.color_button_free.setToolTip("Change Free color display")

            # Insert Free labels on the right position
            layout_grid.addWidget(lbl_free, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_free_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_free, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_free = ChartPieItem()
            self.chart_pie_item_free.setColor(self.color_button_free.color())
            self.chart_pie_item_free.data = 0

            self.chart_pie.addItem(self.chart_pie_item_free)

            grid_row += 1

        if self.memory_os_capability["wired"]:
            # Wired label
            lbl_wired = QLabel("Wired:")
            lbl_wired.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_wired_value = QLabel("")
            self.lbl_wired_value.setAlignment(Qt.AlignRight)
            self.lbl_wired_value.setToolTip("Memory that is marked to always stay in RAM. It is never moved to disk.")
            # Free Color button
            self.color_button_wired = ColorButton(color="red")
            # Insert Free labels on the right position
            layout_grid.addWidget(lbl_wired, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_wired_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_wired, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_wired = ChartPieItem()
            self.chart_pie_item_wired.setColor(self.color_button_wired.color())
            self.chart_pie_item_wired.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_wired)

            grid_row += 1

        # PSUtil can return active
        if self.memory_os_capability["active"]:
            # Active label
            lbl_active = QLabel("Active:")
            lbl_active.setAlignment(Qt.AlignRight)
            # Active label value
            self.lbl_active_value = QLabel("")
            self.lbl_active_value.setAlignment(Qt.AlignRight)
            self.lbl_active_value.setToolTip("Memory currently in use or very recently used, and so it is in RAM.")
            # Active Color button
            self.color_button_active = ColorButton(color="orange")
            # Insert Active labels on the right position
            layout_grid.addWidget(lbl_active, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_active_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_active, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_active = ChartPieItem()
            self.chart_pie_item_active.setColor(self.color_button_active.color())
            self.chart_pie_item_active.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_active)

            grid_row += 1

        # PSUtil can return inactive
        if self.memory_os_capability["inactive"]:
            # Inactive label
            lbl_inactive = QLabel("Inactive:")
            lbl_inactive.setAlignment(Qt.AlignRight)
            # Inactive label value
            self.lbl_inactive_value = QLabel("")
            self.lbl_inactive_value.setAlignment(Qt.AlignRight)
            self.lbl_inactive_value.setToolTip("Memory that is marked as not used.")
            # Inactive Color button
            self.color_button_inactive = ColorButton(color="blue")
            # Insert Inactive labels on the right position
            layout_grid.addWidget(lbl_inactive, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_inactive_value, grid_row, grid_col + 1, 1, 1)
            layout_grid.addWidget(self.color_button_inactive, grid_row, grid_col + 2, 1, 1)

            self.chart_pie_item_inactive = ChartPieItem()
            self.chart_pie_item_inactive.setColor(self.color_button_inactive.color())
            self.chart_pie_item_inactive.setData(0)

            self.chart_pie.addItem(self.chart_pie_item_inactive)

            grid_row += 1

        # PSUtil can return used
        if self.memory_os_capability["used"]:
            # Used label
            lbl_used = QLabel("Used:")
            lbl_used.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_used_value = QLabel("")
            self.lbl_used_value.setAlignment(Qt.AlignRight)
            self.lbl_used_value.setToolTip(
                "Memory used, calculated differently depending on the platform and designed for informational "
                "purposes only. <b>total - free</b> does not necessarily match <b>used</b>. "
            )
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_used, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_used_value, grid_row, grid_col + 1, 1, 1)

        # Position management
        # Set col and row to the second widget Position
        grid_row = 0
        grid_col += 3

        # PSUtil can return available
        if self.memory_os_capability["available"]:
            # Used label
            lbl_available = QLabel("Available:")
            lbl_available.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_available_value = QLabel("")
            self.lbl_available_value.setAlignment(Qt.AlignRight)
            self.lbl_available_value.setToolTip(
                "The memory that can be given instantly to processes without the system going into swap. <br>"
            )
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_available, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_available_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return buffers
        if self.memory_os_capability["buffers"]:
            # Used label
            lbl_buffers = QLabel("Buffers:")
            lbl_buffers.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_buffers_value = QLabel("")
            self.lbl_buffers_value.setAlignment(Qt.AlignRight)
            self.lbl_buffers_value.setToolTip("Cache for things like file system metadata.<br>")
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_buffers, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_buffers_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return cached
        if self.memory_os_capability["cached"]:
            # Used label
            lbl_cached = QLabel("Cached:")
            lbl_cached.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_cached_value = QLabel()
            self.lbl_cached_value.setAlignment(Qt.AlignRight)
            self.lbl_cached_value.setToolTip("Cache for various things.")
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_cached, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_cached_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return shared
        if self.memory_os_capability["shared"]:
            # Used label
            lbl_shared = QLabel("Shared:")
            lbl_shared.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_shared_value = QLabel()
            self.lbl_shared_value.setAlignment(Qt.AlignRight)
            self.lbl_shared_value.setToolTip("Memory that may be simultaneously accessed by multiple processes.")
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_shared, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_shared_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return lab
        if self.memory_os_capability["slab"]:
            # Used label
            lbl_slab = QLabel("Slab:")
            lbl_slab.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_slab_value = QLabel()
            self.lbl_slab_value.setAlignment(Qt.AlignRight)
            self.lbl_slab_value.setToolTip("in-kernel data structures cache.")
            # Insert Used labels on the right position
            layout_grid.addWidget(lbl_slab, grid_row, grid_col, 1, 1)
            layout_grid.addWidget(self.lbl_slab_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        grid_col = 5

        self.lbl_total_value = QLabel("%s" % bytes2human(self.__virtual_memory.total))
        self.lbl_total_value.setAlignment(Qt.AlignLeft)

        layout_grid.addWidget(self.chart_pie, 0, grid_col, grid_col, 1, Qt.AlignCenter)
        layout_grid.addWidget(self.lbl_total_value, 5, grid_col, 1, 1, Qt.AlignCenter)
        grid_row += 1

        layout_grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        widget_grid.setLayout(layout_grid)

        space_label = QLabel()
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh_free_raw(self, free_raw):
        self.chart_pie_item_free.setData(free_raw)
        self.chart_pie_item_free.setColor(self.color_button_free.color())
        self.chart_pie.repaint()

    def refresh_free(self, free):
        self.lbl_free_value.setText(
            "<font color='%s'>%s</font>" % (self.color_button_free.color(), free)
        )

    def refresh_wired_raw(self, wired_raw):
        self.chart_pie_item_wired.setData(wired_raw)
        self.chart_pie_item_wired.setColor(self.color_button_wired.color())
        self.chart_pie.repaint()

    def refresh_wired(self, wired):
        self.lbl_wired_value.setText(
            "<font color='%s'>%s</font>" % (self.color_button_wired.color(), wired)
        )

    def refresh_active_raw(self, active_raw):
        self.chart_pie_item_active.setData(active_raw)
        self.chart_pie_item_active.setColor(self.color_button_active.color())
        self.chart_pie.repaint()

    def refresh_active(self, active):
        self.lbl_active_value.setText(
            "<font color='%s'>%s</font>" % (self.color_button_active.color(), active)
        )

    def refresh_inactive_raw(self, inactive_raw):
        self.chart_pie_item_inactive.setData(inactive_raw)
        self.chart_pie_item_inactive.setColor(self.color_button_inactive.color())
        self.chart_pie.repaint()

    def refresh_inactive(self, inactive):
        self.lbl_inactive_value.setText(
            "<font color='%s'>%s</font>" % (self.color_button_inactive.color(), inactive)
        )

    def refresh_used(self, used):
        self.lbl_used_value.setText(used)

    def refresh_available(self, available):
        self.lbl_available_value.setText(available)

    def refresh_buffers(self, buffers):
        self.lbl_buffers_value.setText(buffers)

    def refresh_cached(self, cached):
        self.lbl_cached_value.setText(cached)

    def refresh_shared(self, shared):
        self.lbl_shared_value.setText(shared)

    def refresh_slab(self, slab):
        self.lbl_slab_value.setText(slab)
