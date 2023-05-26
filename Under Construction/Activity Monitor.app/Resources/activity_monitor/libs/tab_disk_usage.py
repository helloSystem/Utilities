from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtProperty,
)

from PyQt5.QtWidgets import (
    QWidget,
    QFileIconProvider,
)

from .widget_chartpie import ChartPieItem
from .ui_tab_disk_usage import Ui_TabDiskUsage


class TabDiskUsage(QWidget, Ui_TabDiskUsage):
    mounted_disk_partitions_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()

        self.__mounted_disk_partitions = {}

        self.setupUi(self)
        self.setupConnect()

        # Configure Chart Data
        self.chart_pie_item_utilized = ChartPieItem()
        self.chart_pie_item_utilized.color = Qt.black
        self.chart_pie_item_utilized.data = 0

        self.chart_pie_item_free = ChartPieItem()
        self.chart_pie_item_free.color = Qt.black
        self.chart_pie_item_free.data = 0

        self.chart_pie.addItems(
            [
                self.chart_pie_item_utilized,
                self.chart_pie_item_free,
            ]
        )

        self.color_button_space_free.setColor("green")
        self.color_button_space_utilized.setColor("red")

    @pyqtProperty(dict)
    def mounted_disk_partitions(self):
        return self.__mounted_disk_partitions

    @mounted_disk_partitions.setter
    def mounted_disk_partitions(self, value):
        if value != self.__mounted_disk_partitions:
            self.__mounted_disk_partitions = value
            self.mounted_disk_partitions_changed.emit()

    def setMoutedDiskPartitions(self, value):
        self.mounted_disk_partitions = value

    def combobox_refresh(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
        self.combobox_devices.clear()
        for item_number, data in self.__mounted_disk_partitions.items():
            self.combobox_devices.addItem(QFileIconProvider().icon(QFileIconProvider.Drive), data["mountpoint"])
        self.combobox_devices.setCurrentIndex(index)

    def combobox_index_changed(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
            self.combobox_devices.setCurrentIndex(index)

        if self.label_space_utilized_value.text() != self.mounted_disk_partitions[index]['used']:
            self.label_space_utilized_value.setText(self.mounted_disk_partitions[index]['used'])

        if self.label_space_utilized_value_in_bytes.text() != self.mounted_disk_partitions[index]['used_in_bytes']:
            self.label_space_utilized_value_in_bytes.setText(self.mounted_disk_partitions[index]['used_in_bytes'])

        if self.label_space_free_value.text() != self.mounted_disk_partitions[index]['free']:
            self.label_space_free_value.setText(self.mounted_disk_partitions[index]['free'])

        if self.label_space_free_value_in_bytes.text() != self.mounted_disk_partitions[index]['free_in_bytes']:
            self.label_space_free_value_in_bytes.setText(self.mounted_disk_partitions[index]['free_in_bytes'])

        if self.label_space_total_value.text() != self.mounted_disk_partitions[index]['total']:
            self.label_space_total_value.setText(self.mounted_disk_partitions[index]['total'])

        if self.chart_pie_item_utilized.data != self.mounted_disk_partitions[index]['used_raw']:
            self.chart_pie_item_utilized.data = self.mounted_disk_partitions[index]["used_raw"]

        if self.chart_pie_item_free.data != self.mounted_disk_partitions[index]['free_raw']:
            self.chart_pie_item_free.data = self.mounted_disk_partitions[index]["free_raw"]

    def setupConnect(self):
        self.combobox_devices.currentIndexChanged.connect(self.combobox_index_changed)
        self.mounted_disk_partitions_changed.connect(self.combobox_refresh)
        self.color_button_space_free.colorChanged.connect(self.refresh_color_space_free)
        self.color_button_space_utilized.colorChanged.connect(self.refresh_color_space_utilized)

    def refresh_color_space_free(self):
        self.label_space_free_value.setStyleSheet("color: %s;" % self.color_button_space_free.color())
        self.label_space_free_value_in_bytes.setStyleSheet("color: %s;" % self.color_button_space_free.color())
        self.chart_pie_item_free.color = self.color_button_space_free.color()

    def refresh_color_space_utilized(self):
        self.label_space_utilized_value.setStyleSheet("color: %s;" % self.color_button_space_utilized.color())
        self.label_space_utilized_value_in_bytes.setStyleSheet("color: %s;" % self.color_button_space_utilized.color())
        self.chart_pie_item_utilized.color = self.color_button_space_utilized.color()
