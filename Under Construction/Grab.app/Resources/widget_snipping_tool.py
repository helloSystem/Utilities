import os

from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QCursor, QKeySequence, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, qApp, QShortcut

from property_selection_area import SelectionArea


# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QWidget):
    snipping_completed = pyqtSignal(object)

    def __init__(self, parent=None, cursor=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent

        self.begin = None
        self.end = None

        self.qp = None
        self.selection = None
        self.selection_rect = None
        self.win_id = None
        self.screen = None
        self.selection_pen_width = None
        self.enable_sound = None
        self.cursor = cursor
        self.cursor_name = {
            Qt.ArrowCursor: "ArrowCursor",
            Qt.BlankCursor: "BlankCursor",
            Qt.ForbiddenCursor: "ForbiddenCursor",
            Qt.IBeamCursor: "IBeamCursor",
            Qt.OpenHandCursor: "OpenHandCursor",
            Qt.PointingHandCursor: "PointingHandCursor",
            Qt.UpArrowCursor: "UpArrowCursor",
            Qt.WhatsThisCursor: "WhatsThisCursor",
        }
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
        self.snipping_completed.emit(None)
        QApplication.restoreOverrideCursor()
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
        self.show()

        if not self.screen:
            return
        try:
            img = self.screen.grabWindow(self.win_id)
        except (Exception, BaseException):
            img = None

        if img and self.cursor != Qt.BlankCursor:
            pm = QPixmap(self.width(), self.height())
            cursor_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), f"{self.cursor_name[self.cursor]}.png"))
            painter = QPainter(pm)
            painter.drawPixmap(0, 0, self.width(), self.height(), img)
            painter.drawPixmap(
                QCursor().pos().x() - (cursor_pixmap.width() / 2),
                QCursor().pos().y() - (cursor_pixmap.height() / 2),
                cursor_pixmap.width(),
                cursor_pixmap.height(),
                cursor_pixmap,
            )
            painter.end()
            img = pm

        self.snipping_completed.emit(img)

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

            # Draw coordinate
            # Draw coordinate text
            self.qp.setPen(self.selection.coordinate_pen)
            self.qp.setBrush(Qt.NoBrush)
            self.qp.drawText(
                self.selection.coordinate_text_x, self.selection.coordinate_text_y, self.selection.coordinate_text
            )
            # Draw coordinate border
            self.qp.drawRect(
                QRectF(
                    self.selection.coordinate_rect_x,
                    self.selection.coordinate_rect_y,
                    self.selection.coordinate_rect_width,
                    self.selection.coordinate_rect_height,
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

        try:
            img = self.screen.grabWindow(
                self.win_id,
                self.selection.x,
                self.selection.y,
                self.selection.width,
                self.selection.height,
            )
        except (Exception, BaseException):
            img = None

        self.setWindowOpacity(1.0)

        self.snipping_completed.emit(img)
        QApplication.restoreOverrideCursor()
        self.close()
