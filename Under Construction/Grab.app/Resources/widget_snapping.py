from PyQt5.QtWidgets import QApplication, QWidget, qApp, QShortcut
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QRectF
from property_selection_area import SelectionArea


# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QWidget):

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent

        self.begin = None
        self.end = None
        self.onSnippingCompleted = None
        self.is_snipping = None
        self.qp = None
        self.selection_info = None
        self.win_id = None
        self.screen = None

        self.initialState()

    def initialState(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)




        self.begin = QPoint()
        self.end = QPoint()
        self.qp = QPainter()
        self.selection_info = SelectionArea()

        self.is_snipping = False
        self.UpdateScreen()
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_widget_snapping)

    def cancel_widget_snapping(self):
        self.is_snipping = False
        self.begin = QPoint()
        self.end = QPoint()
        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(None)
        self.close()

    @property
    def SelectionColorBackground(self):
        if self.is_snipping:
            return QColor(127, 127, 127, 127)
        else:
            return QColor(0, 0, 0, 0)

    @property
    def SelectionPen(self):
        if self.is_snipping:
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

    def UpdateScreen(self):
        self.screen = qApp.primaryScreen()
        self.win_id = QApplication.desktop().winId()

        self.setGeometry(
            0,
            0,
            self.screen.size().width(),
            self.screen.size().height()
        )

        window = self.windowHandle()
        if window:
            self.screen = window.screen()

    def fullscreen(self):
        self.UpdateScreen()
        if not self.screen:
            return

        try:
            img = self.screen.grabWindow(self.win_id,
                                         0,
                                         0,
                                         self.screen.size().width(),
                                         self.screen.size().height()
                                         )
        except (Exception, BaseException):
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

    def start(self):
        self.UpdateScreen()
        self.is_snipping = True
        # self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.showFullScreen()

    def paintEvent(self, event):
        if self.isVisible():
            self.qp.begin(self)
            if not self.is_snipping:
                self.begin = QPoint()
                self.end = QPoint()
                # self.setWindowOpacity(0.0)

            # self.setWindowOpacity(opacity)

            self.qp.setPen(self.SelectionPen)
            self.qp.setBrush(self.SelectionColorBackground)
            rect = QRectF(self.begin, self.end)
            self.qp.drawRect(rect)
            self.qp.end()

            if rect.width() > 0 and rect.height() > 0:
                self.selection_info.setFromQRectF(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.UpdateScreen()
        if not self.screen:
            return

        self.is_snipping = False
        QApplication.restoreOverrideCursor()
        self.repaint()
        QApplication.processEvents()

        try:
            img = self.screen.grabWindow(
                self.win_id,
                self.selection_info.x,
                self.selection_info.y,
                self.selection_info.width,
                self.selection_info.height,
            )
        except (Exception, BaseException):
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()
