try:
    from PyQt6.QtCore import Qt, QRectF, QPoint, QPointF, pyqtSignal, QEvent, QSize
    from PyQt6.QtGui import (
            QImage,
            QPixmap,
            QPainterPath,
            QMouseEvent,
            QPainter,
            QPen,
            QGuiApplication,
            QKeySequence,
            QCloseEvent
        )
    from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QShortcut
except ImportError:
    try:
        from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF, pyqtSignal, QEvent, QSize
        from PyQt5.QtGui import (
            QImage,
            QPixmap,
            QPainterPath,
            QMouseEvent,
            QPainter,
            QPen,
            QGuiApplication,
            QKeySequence,
            QCloseEvent
        )
        from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QShortcut
    except ImportError:
        raise ImportError("Requires PyQt (version 5 or 6)")


import numpy


class TransWindow(QWidget):
    mouse_press = pyqtSignal()
    transparent_window_signal_quit = pyqtSignal()
    transparent_window_signal_release = pyqtSignal()

    def __init__(self, screen_grab=None, selection=None):
        QWidget.__init__(self, None, Qt.Window)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.screen_grab = screen_grab
        self.selection = selection
        self.showMaximized()
        self.activateWindow()
        self.raise_()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)

        screenGeometry = QApplication.desktop().availableGeometry()
        self.setGeometry(screenGeometry)
        self.setStyleSheet("QWidget { background-color: rgba(255,255,255, 5%); }")
        self.setWindowOpacity(0.5)
        self.pos = None
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_transparent_window)

    def closeEvent(self, event: QCloseEvent) -> None:
        super(TransWindow, self).setWindowOpacity(0.0)
        super(TransWindow, self).closeEvent(event)
        QApplication.processEvents()
        event.accept()

    def mousePressEvent(self, event):
        event: QMouseEvent

        if self.selection:
            xd = QApplication.desktop().screenGeometry().x() - QApplication.desktop().availableGeometry().x()
            yd = QApplication.desktop().screenGeometry().y() - QApplication.desktop().availableGeometry().y()
            self.pos = numpy.array([event.pos().x() - xd,
                                    event.pos().y() - yd])
            print(self.pos)

    def mouseReleaseEvent(self, event):
        self.transparent_window_signal_release.emit()
        self.close()

    def cancel_transparent_window(self):
        self.transparent_window_signal_quit.emit()
