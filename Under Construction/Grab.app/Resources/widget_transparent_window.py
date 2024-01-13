try:
    from PyQt6.QtCore import Qt, QRectF, QPoint, QPointF, pyqtSignal, QEvent, QSize
    from PyQt6.QtGui import QImage, QPixmap, QPainterPath, QMouseEvent, QPainter, QPen
    from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
except ImportError:
    try:
        from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF, pyqtSignal, QEvent, QSize
        from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QMouseEvent, QPainter, QPen, QGuiApplication
        from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
    except ImportError:
        raise ImportError("Requires PyQt (version 5 or 6)")

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt5.QtGui import QMouseEvent
import numpy


class TransWindow(QWidget):
    mouse_press = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self, None, Qt.Window)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.showMaximized()
        self.activateWindow()
        self.raise_()
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)

        screenGeometry = QApplication.desktop().availableGeometry()
        self.setGeometry(screenGeometry)
        self.setStyleSheet("QWidget { background-color: rgba(255,255,255, 5%); }")
        self.pos = None

    def mousePressEvent(self, QMouseEvent):
        self.hide()
        xd = QApplication.desktop().screenGeometry().x() - QApplication.desktop().availableGeometry().x()
        yd = QApplication.desktop().screenGeometry().y() - QApplication.desktop().availableGeometry().y()
        self.pos = numpy.array([QMouseEvent.pos().x() - xd,
                                QMouseEvent.pos().y() - yd])
        self.mouse_press.emit("mouse_press()")
