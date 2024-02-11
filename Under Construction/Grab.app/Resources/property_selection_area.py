
from PyQt5.QtCore import Qt, QPoint, QRectF, QRect

class SelectionArea(object):

    def __init__(self):
        self.__x = None
        self.__y = None
        self.__width = None
        self.__height = None

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

    def setFromQRectF(self, req: QRectF):
        self.x = req.x()
        self.y = req.y()
        self.width = req.width()
        self.height = req.height()
