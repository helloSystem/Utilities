from PyQt5.QtCore import (
    Qt,
    pyqtSignal as Signal,
)

from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QFileIconProvider,
)

from .buttons import ColorButton
from .chartpie import ChartPie, ChartPieItem


class TabDiskUsage(QWidget):
    mounted_disk_partitions_changed = Signal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.__mounted_disk_partitions = None
        self.mounted_disk_partitions = None
        self.combobox_devices = None
        self.label_space_utilized_value = None
        self.label_space_utilized_value_in_bytes = None
        self.color_button_space_utilized = None
        self.label_space_free_value = None
        self.label_space_free_value_in_bytes = None
        self.color_button_space_free = None
        self.label_space_total_value = None
        self.chartpie = None
        self.chartpie_item_utilized = None
        self.chartpie_item_free = None
        # self.mounted_disk_partitions = self.scan_mounted_disk_partitions()

        self.setupUI()

        self.combobox_devices.currentIndexChanged.connect(self.combobox_index_changed)
        # self.combobox_devices.activated.connect(self.combobox_index_changed)
        # self.combobox_devices.activated.connect(lambda: self.mounted_disk_partitions(self.combobox_refresh))

        self.mounted_disk_partitions_changed.connect(self.combobox_refresh)

    @property
    def mounted_disk_partitions(self):
        return self.__mounted_disk_partitions

    @mounted_disk_partitions.setter
    def mounted_disk_partitions(self, value: dict):
        if value is None:
            value = {}
        if self.mounted_disk_partitions != value:
            self.__mounted_disk_partitions = value

            self.mounted_disk_partitions_changed.emit()

    def setMoutedDiskPartitions(self, value):
        self.mounted_disk_partitions = value

    def combobox_refresh(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
        self.combobox_devices.clear()
        for item_number, data in self.mounted_disk_partitions.items():
            self.combobox_devices.addItem(QFileIconProvider().icon(QFileIconProvider.Drive), data["mountpoint"])
        self.combobox_devices.setCurrentIndex(index)

    def combobox_index_changed(self):
        index = self.combobox_devices.currentIndex()
        if index == -1:
            index = 0
            self.combobox_devices.setCurrentIndex(index)

        self.label_space_utilized_value.setText(
            f"<font color='{self.color_button_space_utilized.color()}'>"
            f"{self.mounted_disk_partitions[index]['used']}"
            f"</font>"
        )
        self.label_space_utilized_value_in_bytes.setText(
            f"<font color='{self.color_button_space_utilized.color()}'>"
            f"{self.mounted_disk_partitions[index]['used_in_bytes']}"
            f"</font>"
        )
        self.label_space_free_value.setText(
            f"<font color='{self.color_button_space_free.color()}'>"
            f"{self.mounted_disk_partitions[index]['free']}"
            f"</font>"
        )
        self.label_space_free_value_in_bytes.setText(
            f"<font color='{self.color_button_space_free.color()}'>"
            f"{self.mounted_disk_partitions[index]['free_in_bytes']}"
            f"</font>"
        )
        self.label_space_total_value.setText(f"{self.mounted_disk_partitions[index]['total']}")

        self.chartpie_item_utilized.color = self.color_button_space_utilized.color()
        self.chartpie_item_utilized.data = self.mounted_disk_partitions[index]["used_raw"]
        self.chartpie_item_free.color = self.color_button_space_free.color()
        self.chartpie_item_free.data = self.mounted_disk_partitions[index]["free_raw"]

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout_grid = QGridLayout()

        self.combobox_devices = QComboBox()
        layout_grid.addWidget(self.combobox_devices, 0, 1, 1, 2)

        label_spacing = QLabel()

        label_space_utilized = QLabel("Space utilized:")
        label_space_utilized.setAlignment(Qt.AlignRight)
        # Used label value
        self.label_space_utilized_value = QLabel("")
        self.label_space_utilized_value.setAlignment(Qt.AlignRight)

        self.label_space_utilized_value_in_bytes = QLabel("")
        self.label_space_utilized_value_in_bytes.setAlignment(Qt.AlignRight)

        self.color_button_space_utilized = ColorButton(color="red")

        layout_grid.addWidget(label_spacing, 1, 0, 1, 1)
        # Insert Space utilized labels on the right position
        layout_grid.addWidget(label_space_utilized, 2, 0, 1, 1)
        layout_grid.addWidget(self.label_space_utilized_value, 2, 1, 1, 1)
        layout_grid.addWidget(self.label_space_utilized_value_in_bytes, 2, 2, 1, 1)
        layout_grid.addWidget(self.color_button_space_utilized, 2, 3, 1, 1)

        label_space_free = QLabel("Space free:")
        label_space_free.setAlignment(Qt.AlignRight)
        # Used label value
        self.label_space_free_value = QLabel("")
        self.label_space_free_value.setAlignment(Qt.AlignRight)

        self.label_space_free_value_in_bytes = QLabel("")
        self.label_space_free_value_in_bytes.setAlignment(Qt.AlignRight)

        self.color_button_space_free = ColorButton(color="green")

        # Insert Space utilized labels on the right position
        layout_grid.addWidget(label_space_free, 3, 0, 1, 1)
        layout_grid.addWidget(self.label_space_free_value, 3, 1, 1, 1)
        layout_grid.addWidget(self.label_space_free_value_in_bytes, 3, 2, 1, 1)
        layout_grid.addWidget(self.color_button_space_free, 3, 3, 1, 1)

        self.label_space_total_value = QLabel("")
        self.label_space_total_value.setAlignment(Qt.AlignLeft)
        # self.label_space_total_value.setContentsMargins(10, 0, 0, 0)

        self.chartpie_item_utilized = ChartPieItem()
        self.chartpie_item_utilized.color = self.color_button_space_utilized.color()
        self.chartpie_item_utilized.data = 0

        self.chartpie_item_free = ChartPieItem()
        self.chartpie_item_free.color = self.color_button_space_free.color()
        self.chartpie_item_free.data = 0

        self.chartpie = ChartPie()
        self.chartpie.addItems(
            [
                self.chartpie_item_utilized,
                self.chartpie_item_free,
            ]
        )
        layout_grid.addWidget(self.chartpie, 0, 4, 4, 1, Qt.AlignCenter)
        layout_grid.addWidget(self.label_space_total_value, 4, 4, 1, 1, Qt.AlignCenter)

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

    def refresh(self):
        pass
