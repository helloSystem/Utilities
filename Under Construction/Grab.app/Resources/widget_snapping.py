from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRectF


# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QWidget):
    is_snipping = False

    def __init__(self, parent=None, app=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.screen = app.primaryScreen()
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = QPoint()
        self.end = QPoint()
        self.onSnippingCompleted = None

        self.window_background_color = None
        self.window_opacity = None

        self.selection_color_background = None
        self.selection_color_border = None
        self.selection_opacity = None

        self.setUp()

    @property
    def SelectionColorBackground(self):
        if SnippingWidget.is_snipping:
            return QColor(127, 127, 127, 127)
        else:
            return QColor(0, 0, 0, 0)

    @property
    def SelectionPen(self):
        if SnippingWidget.is_snipping:
            return QPen(
                self.SelectionColorBackground,
                1,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            )
        else:
            return QPen(
                QColor(0, 0, 0, 0),
                0,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            )

    def setUp(self):
        # Selection
        # Color
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: rgba(255,255,255, 95%);")
        self.selection_color_background = QColor(127, 127, 127, 127)
        self.selection_color_border = QColor(127, 127, 127, 127)
        # Pen


    def fullscreen(self):
        try:
            img = QPixmap.grabWindow(QApplication.desktop().winId(),
                                     0,
                                     0,
                                     self.screen.size().width(),
                                     self.screen.size().height())
        except:
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

    def start(self):
        SnippingWidget.is_snipping = True
        # self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.show()

    def paintEvent(self, event):
        qp = QPainter(self)
        if SnippingWidget.is_snipping:
            # brush_color = (128, 128, 128, 100)
            lw = 1
            opacity = 1.0
        else:
            self.begin = QPoint()
            self.end = QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0.0
            self.setWindowOpacity(opacity)

        # self.setWindowOpacity(opacity)

        qp.setPen(self.SelectionPen)
        qp.setBrush(self.SelectionColorBackground)

        rect = QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.is_snipping = False
        QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.repaint()
        QApplication.processEvents()

        # img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        QApplication.primaryScreen().grabWindow(0)
        # img = QPixmap.grabWindow(QApplication.desktop().winId(),
        #                          x1,
        #                          y1,
        #                          x2,
        #                          y2)
        img = QApplication.screens()[0].grabWindow(
            QApplication.desktop().winId(), x1,
            y1,
            x2,
            y2)
        # try:
        #     img = QPixmap.grabWindow(QApplication.desktop().winId(),
        #                              x1,
        #                              y1,
        #                              x2,
        #                              y2)
        # except:
        #     img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()
