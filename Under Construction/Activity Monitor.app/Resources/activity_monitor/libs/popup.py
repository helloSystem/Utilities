from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
    QPushButton,
)


class popup(QWidget):
    def __init__(self, parent=None, widget=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout(self)
        button = QPushButton("Very Interesting Text Popup. Here's an arrow   ^")
        layout.addWidget(button)

        # adjust the margins or you will get an invisible, unintended border
        layout.setContentsMargins(0, 0, 0, 0)

        # need to set the layout
        self.setLayout(layout)
        self.adjustSize()

        # tag this widget as a popup
        self.setWindowFlags(Qt.Popup)

        # calculate the botoom right point from the parents rectangle
        point = widget.rect().bottomRight()

        # map that point as a global position
        global_point = widget.mapToGlobal(point)

        # by default, a widget will be placed from its top-left corner, so
        # we need to move it to the left based on the widgets width
        self.move(global_point - QPoint(self.width(), 0))
