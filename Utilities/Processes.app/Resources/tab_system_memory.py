#!/usr/bin/env python3

from PyQt5.QtWidgets import QLabel
from property_virtual_memory import VirtualMemory
from widget_color_pickup import ColorButton
from widget_chartpie import ChartPieItem, ChartPie
from utility import bytes2human


class TabSystemMemory(VirtualMemory):
    virtual_memory_total: int
    virtual_memory_available: int
    virtual_memory_percent: float
    virtual_memory_used: int
    virtual_memory_free: int
    virtual_memory_active: int
    virtual_memory_inactive: int
    virtual_memory_buffers: int
    virtual_memory_cached: int
    virtual_memory_shared: int
    virtual_memory_slab: int
    virtual_memory_wired: int

    system_memory_free_value: QLabel
    system_memory_active_value: QLabel
    system_memory_inactive_value: QLabel
    system_memory_wired_value: QLabel
    system_memory_used_value: QLabel
    system_memory_available_value: QLabel
    system_memory_buffers_value: QLabel
    system_memory_cached_value: QLabel
    system_memory_shared_value: QLabel
    system_memory_slab_value: QLabel
    system_memory_total_value: QLabel
    system_memory_percent_value: QLabel

    chart_pie_item_memory_free: ChartPieItem
    chart_pie_item_memory_active: ChartPieItem
    chart_pie_item_memory_inactive: ChartPieItem
    chart_pie_item_memory_wired: ChartPieItem

    system_memory_chart_pie: ChartPie

    color_picker_free_value: ColorButton
    color_picker_active_value: ColorButton
    color_picker_inactive_value: ColorButton
    color_picker_wired_value: ColorButton

    def __init__(self, *args, **kwargs):
        super(TabSystemMemory, self).__init__()
        VirtualMemory.__init__(self)

        self.virtual_memory_total_changed.connect(self.refresh_virtual_memory_total)
        self.virtual_memory_available_changed.connect(self.refresh_virtual_memory_available)
        self.virtual_memory_percent_changed.connect(self.refresh_virtual_memory_percent)
        self.virtual_memory_used_changed.connect(self.refresh_virtual_memory_used)
        self.virtual_memory_free_changed.connect(self.refresh_virtual_memory_free)
        self.virtual_memory_active_changed.connect(self.refresh_virtual_memory_active)
        self.virtual_memory_inactive_changed.connect(self.refresh_virtual_memory_inactive)
        self.virtual_memory_buffers_changed.connect(self.refresh_virtual_memory_buffers)
        self.virtual_memory_cached_changed.connect(self.refresh_virtual_memory_cached)
        self.virtual_memory_shared_changed.connect(self.refresh_virtual_memory_shared)
        self.virtual_memory_slab_changed.connect(self.refresh_virtual_memory_slab)
        self.virtual_memory_wired_changed.connect(self.refresh_virtual_memory_wired)

    # Prev Refresh
    def refresh_virtual_memory_total(self):
        if hasattr(self, "system_memory_total_value"):
            self.system_memory_total_value.setText(bytes2human(self.virtual_memory_total))

    def refresh_virtual_memory_available(self):
        if hasattr(self, "system_memory_available_value"):
            self.system_memory_available_value.setText(bytes2human(self.virtual_memory_available))

    def refresh_virtual_memory_percent(self):
        if hasattr(self, "system_memory_percent_value"):
            self.system_memory_percent_value.setText(bytes2human(self.virtual_memory_percent))

    def refresh_virtual_memory_used(self):
        if hasattr(self, "system_memory_used_value"):
            self.system_memory_used_value.setText(bytes2human(self.virtual_memory_used))

    def refresh_virtual_memory_free(self):
        if hasattr(self, "system_memory_free_value"):
            self.system_memory_free_value.setText(bytes2human(self.virtual_memory_free))
            self.chart_pie_item_memory_free.setData(self.virtual_memory_free)
            self.system_memory_chart_pie.repaint()

    def refresh_virtual_memory_active(self):
        if hasattr(self, "system_memory_active_value"):
            self.system_memory_active_value.setText(bytes2human(self.virtual_memory_active))
            self.chart_pie_item_memory_active.setData(self.virtual_memory_active)
            self.system_memory_chart_pie.repaint()

    def refresh_virtual_memory_inactive(self):
        if hasattr(self, "system_memory_inactive_value"):
            self.system_memory_inactive_value.setText(bytes2human(self.virtual_memory_inactive))
            self.chart_pie_item_memory_inactive.setData(self.virtual_memory_inactive)
            self.system_memory_chart_pie.repaint()

    def refresh_virtual_memory_buffers(self):
        if hasattr(self, "system_memory_buffers_value"):
            self.system_memory_buffers_value.setText(bytes2human(self.virtual_memory_buffers))

    def refresh_virtual_memory_cached(self):
        if hasattr(self, "system_memory_cached_value"):
            self.system_memory_cached_value.setText(bytes2human(self.virtual_memory_cached))

    def refresh_virtual_memory_shared(self):
        if hasattr(self, "system_memory_shared_value"):
            self.system_memory_shared_value.setText(bytes2human(self.virtual_memory_shared))

    def refresh_virtual_memory_slab(self):
        if hasattr(self, "system_memory_slab_value"):
            self.system_memory_slab_value.setText(bytes2human(self.virtual_memory_slab))

    def refresh_virtual_memory_wired(self):
        if hasattr(self, "system_memory_wired_value"):
            self.system_memory_wired_value.setText(bytes2human(self.virtual_memory_wired))
            self.chart_pie_item_memory_wired.setData(self.virtual_memory_wired)
            self.system_memory_chart_pie.repaint()

    def refresh_color_free(self):
        self.system_memory_free_value.setStyleSheet("color: %s;" % self.color_picker_free_value.color())
        self.chart_pie_item_memory_free.setColor(self.color_picker_free_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_active(self):
        self.system_memory_active_value.setStyleSheet("color: %s;" % self.color_picker_active_value.color())
        self.chart_pie_item_memory_active.setColor(self.color_picker_active_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_inactive(self):
        self.system_memory_inactive_value.setStyleSheet("color: %s;" % self.color_picker_inactive_value.color())
        self.chart_pie_item_memory_inactive.setColor(self.color_picker_inactive_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_wired(self):
        self.system_memory_wired_value.setStyleSheet("color: %s;" % self.color_picker_wired_value.color())
        self.chart_pie_item_memory_wired.setColor(self.color_picker_wired_value.color())
        self.system_memory_chart_pie.repaint()
