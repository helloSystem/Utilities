from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QFontMetrics, QColor, QPen, QPalette


class SelectionArea(object):

    def __init__(self):
        self.__x = None
        self.__y = None
        self.__width = None
        self.__height = None
        self.__is_snipping = None

        self.coordinate_spacing = None
        self.coordinate_font = None
        self.coordinate_font_metrics = None
        self.coordinate_pen = None
        self.coordinate_pen_width = 1
        self.coordinate_pen_color = QColor(0, 0, 0, 255)

        self.coordinate_spacing = 5
        self.coordinate_font = QFont()
        self.coordinate_font_metrics = QFontMetrics(self.coordinate_font)
        self.coordinate_pen = QPen(
            self.coordinate_pen_color,
            self.coordinate_pen_width,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )
        self.selection_pen_width = 2


    @property
    def is_snipping(self):
        return self.__is_snipping

    @is_snipping.setter
    def is_snipping(self, value: bool):
        if value != self.is_snipping:
            self.__is_snipping = value

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x: float):
        if x != self.x:
            self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y: float):
        if y != self.y:
            self.__y = y

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width: float):
        if width != self.width:
            self.__width = width

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height: float):
        if height != self.height:
            self.__height = height

    @property
    def coordinate_text(self):
        return f"{int(abs(self.width))}, {int(abs(self.height))}"

    @property
    def coordinate_text_width(self):
        return self.coordinate_font_metrics.width(self.coordinate_text)

    @property
    def coordinate_text_x(self):
        return self.x + self.width - self.coordinate_text_width - self.coordinate_spacing

    @property
    def coordinate_text_y(self):
        return self.y + self.height - self.coordinate_spacing + self.coordinate_font_metrics.height()

    @property
    def coordinate_rect_x(self):
        return self.x + self.width - self.coordinate_text_width - (self.coordinate_spacing * 2)

    @property
    def coordinate_rect_y(self):
        return self.y + self.height + (self.coordinate_spacing / 2)

    @property
    def coordinate_rect_width(self):
        return self.coordinate_text_width + (self.coordinate_spacing * 2)

    @property
    def coordinate_rect_height(self):
        return self.coordinate_font_metrics.height() - (self.selection_pen_width * 2)

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

    def setFromQRectF(self, req: QRectF):
        self.x = req.x()
        self.y = req.y()
        self.width = req.width()
        self.height = req.height()
