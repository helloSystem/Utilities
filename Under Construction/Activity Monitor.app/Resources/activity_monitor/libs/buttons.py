#!/usr/bin/env python3

from PyQt5.QtGui import QColor, QPaintEvent
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QSize
)
from PyQt5.QtWidgets import (
    QColorDialog,
    QVBoxLayout,
    QLabel,
    QAbstractButton, QFrame
)


class ColorButton(QAbstractButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        self.label = QLabel()
        self.label.setText("■")
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)
        self.setColor(self._default)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        # self.setStyleSheet("border: none;")

    def paintEvent(self, e: QPaintEvent) -> None:
        pass

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(1, 1)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)
        if self._color:
            self.label.setStyleSheet(f"border: 1px solid; border-color: Gray; color: {self._color};")
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)
