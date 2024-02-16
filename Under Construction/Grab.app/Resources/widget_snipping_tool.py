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
        self.enable_sound = None
        self.cursor = Qt.BlankCursor

        self.initialState()

    def initialState(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint)

        self.begin = QPoint()
        self.end = QPoint()
        self.qp = QPainter()
        self.selection_info = SelectionArea()

        self.is_snipping = False
        self.UpdateScreen()
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_widget_snapping)
        self.selection_pen_width = 2

    def cancel_widget_snapping(self):
        self.is_snipping = False
        self.begin = QPoint()
        self.end = QPoint()
        if self.onSnippingCompleted:
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
        # Be sure the screen is the Parent of the Desktop
        self.screen = qApp.primaryScreen()
        self.win_id = QApplication.desktop().winId()

        # Impose the screen size of the snipping widget
        self.resize(self.screen.grabWindow(self.win_id).size())

        # Back to normal situation where screen is the parent of the MainWindow
        if self.windowHandle():
            self.screen = self.windowHandle().screen()

    def fullscreen(self):
        self.UpdateScreen()
        if not self.screen:
            return
        QApplication.setOverrideCursor(self.cursor)
        try:
            img = self.screen.grabWindow(self.win_id)
        except (Exception, BaseException):
            img = None

        QApplication.restoreOverrideCursor()
        if self.onSnippingCompleted:
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

        # Draw the selection
        self.qp.setPen(self.SelectionPen)
        self.qp.setBrush(self.SelectionColorBackground)



        selection_rect = QRectF(self.begin, self.end)
        self.qp.drawRect(selection_rect)

        # Draw text coordinate
        coordinate_spacing = 5
        coordinate_font = QFont()
        coordinate_font_metrics = QFontMetrics(coordinate_font)
        coordinate_x = max(self.end.x(), self.begin.x())
        coordinate_y = max(self.end.y(), self.begin.y())
        coordinate_text = f"{int(abs(selection_rect.width()))}, {int(abs(selection_rect.height()))}"
        coordinate_text_height = coordinate_font_metrics.height()
        coordinate_text_width = coordinate_font_metrics.width(coordinate_text)
        coordinate_text_x = coordinate_x - coordinate_text_width - coordinate_spacing
        coordinate_text_y = coordinate_y - coordinate_spacing + coordinate_text_height
        coordinate_rect_x = coordinate_x - coordinate_text_width - (coordinate_spacing * 2)
        coordinate_rect_y = coordinate_y + (coordinate_spacing / 2)
        coordinate_rect_width = coordinate_text_width + (coordinate_spacing * 2)
        coordinate_rect_height = coordinate_text_height - (self.selection_pen_width * 2)

        self.qp.setPen(QPen(
                QColor(0, 0, 0, 255),
                1,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            ))
        self.qp.drawText(
            coordinate_text_x,
            coordinate_text_y,
            coordinate_text
        )
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawRect(
            QRectF(
                coordinate_rect_x,
                coordinate_rect_y,
                coordinate_rect_width,
                coordinate_rect_height
                   )
        )
        if not selection_rect.isNull():
            self.selection_info.setFromQRectF(selection_rect.normalized())

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
        self.setWindowOpacity(0.0)
        QApplication.processEvents()

        img = self.screen.grabWindow(
            self.win_id,

        ).copy(
            self.selection_info.x,
            self.selection_info.y,
            self.selection_info.width,
            self.selection_info.height,
        )
        # self.setWindowOpacity(1.0)

        if self.onSnippingCompleted:
            self.onSnippingCompleted(img)

        QApplication.restoreOverrideCursor()
        self.close()
