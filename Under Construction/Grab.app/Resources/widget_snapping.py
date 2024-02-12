from PyQt5.QtWidgets import QApplication, QWidget, qApp, QShortcut
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QKeySequence, QFontMetrics, QFont, QPalette
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
        self.selection_rect = None
        self.win_id = None
        self.screen = None
        self.selection_pen_width = None

        self.initialState()

    def initialState(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.begin = QPoint()
        self.end = QPoint()
        self.qp = QPainter()
        self.selection_info = SelectionArea()

        self.is_snipping = False
        self.UpdateScreen()
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_widget_snapping)
        self.selection_pen_width = 2

    def get_screen_size(self):
        return self.screen.grabWindow(self.win_id).size()

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
            color = QPalette().color(QPalette.Highlight)
            color.setAlpha(0)
            return color
        else:
            return QColor(0, 0, 0, 0)

    @property
    def SelectionPen(self):
        if self.is_snipping:
            color = QPalette().color(QPalette.Base)
            color.setAlpha(127)
            return QPen(
                color,
                self.selection_pen_width,
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
        # screenRect = QApplication.desktop().screenGeometry()
        # self.setGeometry(
        #     screenRect
        # )
        # self.move(0, 0)
        self.resize(self.get_screen_size())

        window = self.windowHandle()
        if window:
            self.screen = window.screen()

    def fullscreen(self):
        self.UpdateScreen()
        if not self.screen:
            return

        try:
            img = self.screen.grabWindow(self.win_id)
        except (Exception, BaseException):
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

    def start(self):
        self.UpdateScreen()
        self.is_snipping = True
        # self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.show()

    def paintEvent(self, event):

        if not self.is_snipping:
            self.begin = QPoint()
            self.end = QPoint()
            # self.setWindowOpacity(0.0)
        self.qp.begin(self)

        # self.setWindowOpacity(opacity)

        self.qp.setPen(self.SelectionPen)
        self.qp.setBrush(self.SelectionColorBackground)
        rect = QRectF(self.begin, self.end)
        self.qp.drawRect(rect)

        font = QFont()
        fm = QFontMetrics(font)
        text = f"{int(abs(rect.width()))}, {int(abs(rect.height()))}"
        pixelsWide = fm.width(text)
        pixelsHigh = fm.height()
        spacing = 5



        self.qp.setPen(QPen(
                QColor(0, 0, 0, 255),
                1,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            ))
        self.qp.drawText(
            self.end.x() - pixelsWide - spacing,
            self.end.y() - spacing + pixelsHigh,
            text
        )
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawRect(
            QRectF(
                self.end.x() - pixelsWide - (spacing * 2),
                self.end.y() + ( spacing / 2),
                pixelsWide + (spacing * 2),
                pixelsHigh - ( self.selection_pen_width * 2)
                   )
        )
        if not rect.isNull():
            self.selection_rect = rect
            self.selection_info.setFromQRectF(rect)
        self.qp.end()

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
        self.hide()
        print(self.selection_rect)
        img = self.screen.grabWindow(
            self.win_id,

        ).copy(
            self.selection_rect.x(),
            self.selection_rect.y(),
            self.selection_info.width,
            self.selection_info.height,
        )
        self.show()
        # try:
        #     self.hide()
        #     img = self.screen.grabWindow(
        #         self.win_id,
        #         self.selection_info.x,
        #         self.selection_info.y,
        #         self.selection_info.width,
        #         self.selection_info.height,
        #     )
        #     self.show()
        # except (Exception, BaseException):
        #     img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()
