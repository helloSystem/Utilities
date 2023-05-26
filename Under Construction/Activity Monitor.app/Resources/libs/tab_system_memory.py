#!/usr/bin/env python3

class TabSystemMemory(object):
    def refresh_color_free(self):
        self.label_free_value.setStyleSheet("color: %s;" % self.color_picker_free_value.color())
        self.chart_pie_item_free.setColor(self.color_picker_free_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_active(self):
        self.label_active_value.setStyleSheet("color: %s;" % self.color_picker_active_value.color())
        self.chart_pie_item_active.setColor(self.color_picker_active_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_inactive(self):
        self.label_inactive_value.setStyleSheet("color: %s;" % self.color_picker_inactive_value.color())
        self.chart_pie_item_inactive.setColor(self.color_picker_inactive_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_color_wired(self):
        self.label_wired_value.setStyleSheet("color: %s;" % self.color_picker_wired_value.color())
        self.chart_pie_item_wired.setColor(self.color_picker_wired_value.color())
        self.system_memory_chart_pie.repaint()

    def refresh_free_raw(self, free_raw):
        if self.chart_pie_item_free.data != free_raw:
            self.chart_pie_item_free.setData(free_raw)
            self.system_memory_chart_pie.repaint()

    def refresh_free(self, free):
        if self.label_free_value.text() != free:
            self.label_free_value.setText(free)

    def refresh_wired_raw(self, wired_raw):
        if self.chart_pie_item_wired.data != wired_raw:
            self.chart_pie_item_wired.setData(wired_raw)
            self.system_memory_chart_pie.repaint()

    def refresh_wired(self, wired):
        if self.label_wired_value.text() != wired:
            self.label_wired_value.setText(wired)

    def refresh_active_raw(self, active_raw):
        if self.chart_pie_item_active.data != active_raw:
            self.chart_pie_item_active.setData(active_raw)
            self.system_memory_chart_pie.repaint()

    def refresh_active(self, active):
        if self.label_active_value.text() != active:
            self.label_active_value.setText(active)

    def refresh_inactive_raw(self, inactive_raw):
        if self.chart_pie_item_inactive.data != inactive_raw:
            self.chart_pie_item_inactive.setData(inactive_raw)
            self.system_memory_chart_pie.repaint()

    def refresh_inactive(self, inactive):
        if self.label_inactive_value.text() != inactive:
            self.label_inactive_value.setText(inactive)

    def refresh_used(self, used):
        if self.label_used_value.text() != used:
            self.label_used_value.setText(used)

    def refresh_available(self, available):
        if self.label_available_value.text() != available:
            self.label_available_value.setText(available)

    def refresh_buffers(self, buffers):
        if self.label_buffers_value.text() != buffers:
            self.label_buffers_value.setText(buffers)

    def refresh_cached(self, cached):
        if self.label_cached_value.text() != cached:
            self.label_cached_value.setText(cached)

    def refresh_shared(self, shared):
        if self.label_shared_value.text() != shared:
            self.label_shared_value.setText(shared)

    def refresh_slab(self, slab):
        if self.label_slab_value.text() != slab:
            self.label_slab_value.setText(slab)
