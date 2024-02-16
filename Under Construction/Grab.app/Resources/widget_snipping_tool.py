from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainter, QCursor, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, qApp, QShortcut

from property_selection_area import SelectionArea


# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QWidget):

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent

        self.begin = None
        self.end = None
        self.onSnippingCompleted = None

        self.qp = None
        self.selection = None
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
        self.selection = SelectionArea()

        self.selection.is_snipping = False
        self.UpdateScreen()
        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.cancel_widget_snapping)

    def cancel_widget_snapping(self):
        self.selection.is_snipping = False
        self.begin = QPoint()
        self.end = QPoint()
        if self.onSnippingCompleted:
            self.onSnippingCompleted(None)
        self.close()

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
        self.selection.is_snipping = True
        # self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.show()

    def paintEvent(self, event):

        if not self.selection.is_snipping:
            self.begin = QPoint()
            self.end = QPoint()
            # self.setWindowOpacity(0.0)
        self.qp.begin(self)

        # self.setWindowOpacity(opacity)
        selection_rect = QRectF(self.begin, self.end)
        if not selection_rect.isNull():
            # Draw the selection
            self.selection.setFromQRectF(selection_rect.normalized())
            self.qp.setPen(self.selection.SelectionPen)
            self.qp.setBrush(self.selection.SelectionColorBackground)
            self.qp.drawRect(selection_rect)

            # Draw text coordinate
            self.qp.setPen(self.selection.coordinate_pen)
            self.qp.drawText(
                self.selection.coordinate_text_x,
                self.selection.coordinate_text_y,
                self.selection.coordinate_text
            )
            self.qp.setBrush(Qt.NoBrush)
            self.qp.drawRect(
                QRectF(
                    self.selection.coordinate_rect_x,
                    self.selection.coordinate_rect_y,
                    self.selection.coordinate_rect_width,
                    self.selection.coordinate_rect_height
                )
            )

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

        self.selection.is_snipping = False
        QApplication.restoreOverrideCursor()
        self.repaint()
        self.setWindowOpacity(0.0)
        QApplication.processEvents()

        img = self.screen.grabWindow(
            self.win_id,

        ).copy(
            self.selection.x,
            self.selection.y,
            self.selection.width,
            self.selection.height,
        )
        # self.setWindowOpacity(1.0)

        if self.onSnippingCompleted:
            self.onSnippingCompleted(img)

        QApplication.restoreOverrideCursor()
        self.close()
