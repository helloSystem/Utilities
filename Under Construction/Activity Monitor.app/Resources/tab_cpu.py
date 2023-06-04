#!/usr/bin/env python3


from PyQt5.QtWidgets import (
    QLabel
)
from property_cpu_times_percent import CPUTimesPercent
from widget_cpugraphbar import CPUGraphBar
from widget_color_pickup import ColorButton
from dialog_cpu_history import CPUHistory


class TabCpu(CPUTimesPercent):
    user: float
    system: float
    idle: float
    nice: float
    irq: float

    cpu_widget_graph: CPUGraphBar
    label_user_value: QLabel
    label_system_value: QLabel
    label_idle_value: QLabel
    label_nice_value: QLabel
    label_irq_value: QLabel
    label_processes_value: QLabel
    label_threads_value: QLabel
    label_system_unit: QLabel
    label_user_unit: QLabel
    label_idle_unit: QLabel
    label_nice_unit: QLabel
    label_irq_unit: QLabel

    color_picker_system_value: ColorButton
    color_picker_user_value: ColorButton
    color_picker_idle_value: ColorButton
    color_picker_nice_value: ColorButton
    color_picker_irq_value: ColorButton

    cpu_history_dialog: CPUHistory

    def __init__(self, *args, **kwargs):
        super(TabCpu, self).__init__()
        CPUTimesPercent.__init__(self)

    def refresh_user(self):
        if self.label_user_value.isVisible() and self.label_user_value.text() != f"{self.user}":
            self.label_user_value.setText(f"{self.user}")
        self.cpu_widget_graph.user = self.user
        self.cpu_history_dialog.cpu_history_graph.user = self.user

    def refresh_system(self):
        if self.label_system_value.isVisible() and self.label_system_value.text() != f"{self.system}":
            self.label_system_value.setText(f"{self.system}")
        self.cpu_widget_graph.system = self.system
        self.cpu_history_dialog.cpu_history_graph.system = self.system

    def refresh_idle(self):
        if self.label_idle_value.isVisible() and self.label_idle_value.text() != f"{self.idle}":
            self.label_idle_value.setText(f"{self.idle}")
        # idle color is just the background color, then it is bind to refresh
        self.cpu_widget_graph.slice()
        self.cpu_history_dialog.cpu_history_graph.slice()

    def refresh_nice(self):
        if self.label_nice_value.isVisible() and self.label_nice_value.text() != f"{self.nice}":
            self.label_nice_value.setText(f"{self.nice}")
        self.cpu_widget_graph.nice = self.nice
        self.cpu_history_dialog.cpu_history_graph.nice = self.nice

    def refresh_irq(self):
        if self.label_irq_value.isVisible() and self.label_irq_value.text() != f"{self.irq}":
            self.label_irq_value.setText(f"{self.irq}")
        self.cpu_widget_graph.irq = self.irq
        self.cpu_history_dialog.cpu_history_graph.irq = self.irq

    def refresh_process_number(self, process_number: int):
        if self.label_processes_value.isVisible() and self.label_processes_value.text() != f"{process_number}":
            self.label_processes_value.setText(f"{process_number}")

    def refresh_cumulative_threads(self, cumulative_threads: int):
        if self.label_threads_value.isVisible() and self.label_threads_value.text() != f"{cumulative_threads}":
            self.label_threads_value.setText(f"{cumulative_threads}")

    def refresh_color_system(self):
        self.label_system_value.setStyleSheet("color: %s;" % self.color_picker_system_value.color())
        self.label_system_unit.setStyleSheet("color: %s;" % self.color_picker_system_value.color())
        self.cpu_widget_graph.color_system = self.color_picker_system_value.color()
        self.cpu_history_dialog.cpu_history_graph.color_system = self.color_picker_system_value.color()

    def refresh_color_user(self):
        self.label_user_value.setStyleSheet("color: %s;" % self.color_picker_user_value.color())
        self.label_user_unit.setStyleSheet("color: %s;" % self.color_picker_user_value.color())
        self.cpu_widget_graph.color_user = self.color_picker_user_value.color()
        self.cpu_history_dialog.cpu_history_graph.color_user = self.color_picker_user_value.color()

    def refresh_color_idle(self):
        self.label_idle_value.setStyleSheet("color: %s;" % self.color_picker_idle_value.color())
        self.label_idle_unit.setStyleSheet("color: %s;" % self.color_picker_idle_value.color())
        self.cpu_widget_graph.color_idle = self.color_picker_idle_value.color()
        self.cpu_history_dialog.cpu_history_graph.color_idle = self.color_picker_idle_value.color()

    def refresh_color_nice(self):
        self.label_nice_value.setStyleSheet("color: %s;" % self.color_picker_nice_value.color())
        self.label_nice_unit.setStyleSheet("color: %s;" % self.color_picker_nice_value.color())
        self.cpu_widget_graph.color_nice = self.color_picker_nice_value.color()
        self.cpu_history_dialog.cpu_history_graph.color_nice = self.color_picker_nice_value.color()

    def refresh_color_irq(self):
        self.label_irq_value.setStyleSheet("color: %s;" % self.color_picker_irq_value.color())
        self.label_irq_unit.setStyleSheet("color: %s;" % self.color_picker_irq_value.color())
        self.cpu_widget_graph.color_irq = self.color_picker_irq_value.color()
        self.cpu_history_dialog.cpu_history_graph.color_irq = self.color_picker_irq_value.color()
