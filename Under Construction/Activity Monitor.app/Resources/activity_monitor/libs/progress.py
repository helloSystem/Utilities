from PyQt5.QtCore import (
    QTimer,
    Qt,
    QRectF,
    QSize,
    pyqtSignal as Signal,
    QItemSelectionModel,
    QItemSelection,
    QObject,
    QThread

)
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QStandardItemModel, QStandardItem, QColor, QImage, QPainter, QPen, QPainterPath, QConicalGradient, QGradient, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QShortcut,
    QLabel,
    QColorDialog,
    QAction,
    QActionGroup,
    QWidgetAction,
    QMenuBar,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QTreeView,
    QFileIconProvider,

)
class QRoundProgressBar(QWidget):

    StyleDonut = 1
    StylePie = 2
    StyleLine = 3

    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    UF_VALUE = 1
    UF_PERCENT = 2
    UF_MAX = 4

    def __init__(self):
        super().__init__()
        self.min = 0
        self.max = 100
        self.value = 25

        self.nullPosition = self.PositionTop
        self.barStyle = self.StyleDonut
        self.outlinePenWidth =1
        self.dataPenWidth = 1
        self.rebuildBrush = False
        self.format = "%p%"
        self.decimals = 1
        self.updateFlags = self.UF_PERCENT
        self.gradientData = []
        self.donutThicknessRatio = 0.75

    def setRange(self, min, max):
        self.min = min
        self.max = max

        if self.max < self.min:
            self.max, self.min = self.min, self.max

        if self.value < self.min:
            self.value = self.min
        elif self.value > self.max:
            self.value = self.max

        if not self.gradientData:
            self.rebuildBrush = True
        self.update()

    def setMinimun(self, min):
        self.setRange(min, self.max)

    def setMaximun(self, max):
        self.setRange(self.min, max)

    def setValue(self, val):
        if self.value != val:
            if val < self.min:
                self.value = self.min
            elif val > self.max:
                self.value = self.max
            else:
                self.value = val
            self.update()

    def setNullPosition(self, position):
        if position != self.nullPosition:
            self.nullPosition = position
            if not self.gradientData:
                self.rebuildBrush = True
            self.update()

    def setBarStyle(self, style):
        if style != self.barStyle:
            self.barStyle = style
            self.update()

    def setOutlinePenWidth(self, penWidth):
        if penWidth != self.outlinePenWidth:
            self.outlinePenWidth = penWidth
            self.update()

    def setDataPenWidth(self, penWidth):
        if penWidth != self.dataPenWidth:
            self.dataPenWidth = penWidth
            self.update()

    def setDataColors(self, stopPoints):
        if stopPoints != self.gradientData:
            self.gradientData = stopPoints
            self.rebuildBrush = True
            self.update()

    def setFormat(self, format):
        if format != self.format:
            self.format = format
            self.valueFormatChanged()

    def resetFormat(self):
        self.format = ''
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.decimals:
            self.decimals = count
            self.valueFormatChanged()

    def setDonutThicknessRatio(self, val):
        self.donutThicknessRatio = max(0., min(val, 1.))
        self.update()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QRectF(1, 1, outerRadius-2, outerRadius-2)

        buffer = QImage(outerRadius, outerRadius, QImage.Format_ARGB32)
        buffer.fill(0)

        p = QPainter(buffer)
        p.setRenderHint(QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # background
        # self.drawBackground(p, buffer.rect())

        # base circle
        self.drawBase(p, baseRect)

        # data circle
        arcStep = 360.0 / (self.max - self.min) * self.value
        self.drawValue(p, baseRect, self.value, arcStep)

        # center circle
        innerRect, innerRadius = self.calculateInnerRect(baseRect, outerRadius)
        self.drawInnerBackground(p, innerRect)

        # text
        # self.drawText(p, innerRect, innerRadius, self.value)

        # finally draw the bar
        p.end()

        painter = QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, self.palette().background())

    def drawBase(self, p, baseRect):
        bs = self.barStyle
        if bs == self.StyleDonut:
            p.setPen(QPen(self.palette().shadow().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StylePie:
            p.setPen(QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StyleLine:
            p.setPen(QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(Qt.Qt.NoBrush)
            p.drawEllipse(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2))

    def drawValue(self, p, baseRect, value, arcLength):
        # nothing to draw
        if value == self.min:
            return

        # for Line style
        if self.barStyle == self.StyleLine:
            p.setPen(QPen(self.palette().highlight().color(), self.dataPenWidth))
            p.setBrush(Qt.Qt.NoBrush)
            p.drawArc(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2),
                      self.nullPosition * 16,
                      -arcLength * 16)
            return

        # for Pie and Donut styles
        dataPath = QPainterPath()
        dataPath.setFillRule(Qt.WindingFill)

        # pie segment outer
        dataPath.moveTo(baseRect.center())
        dataPath.arcTo(baseRect, self.nullPosition, -arcLength)
        dataPath.lineTo(baseRect.center())

        p.setBrush(self.palette().highlight())
        p.setPen(QPen(self.palette().shadow().color(), self.dataPenWidth))
        p.drawPath(dataPath)

    def calculateInnerRect(self, baseRect, outerRadius):
        # for Line style
        if self.barStyle == self.StyleLine:
            innerRadius = outerRadius - self.outlinePenWidth
        else:    # for Pie and Donut styles
            innerRadius = outerRadius * self.donutThicknessRatio

        delta = (outerRadius - innerRadius) / 2.
        innerRect = QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawInnerBackground(self, p, innerRect):
        if self.barStyle == self.StyleDonut:
            p.setBrush(self.palette().alternateBase())

            cmod = p.compositionMode()
            p.setCompositionMode(QPainter.CompositionMode_Source)

            p.drawEllipse(innerRect)

            p.setCompositionMode(cmod)

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.format:
            return

        text = self.valueToText(value)

        # !!! to revise
        f = self.font()
        # f.setPixelSize(innerRadius * max(0.05, (0.35 - self.decimals * 0.08)))
        f.setPixelSize(innerRadius * 1.8 / len(text))
        p.setFont(f)

        textRect = innerRect
        p.setPen(self.palette().text().color())
        p.drawText(textRect, Qt.Qt.AlignCenter, text)

    def valueToText(self, value):
        textToDraw = self.format

        format_string = '{' + ':.{}f'.format(self.decimals) + '}'

        if self.updateFlags & self.UF_VALUE:
            textToDraw = textToDraw.replace("%v", format_string.format(value))

        if self.updateFlags & self.UF_PERCENT:
            percent = (value - self.min) / (self.max - self.min) * 100.0
            textToDraw = textToDraw.replace("%p", format_string.format(percent))

        if self.updateFlags & self.UF_MAX:
            m = self.max - self.min + 1
            textToDraw = textToDraw.replace("%m", format_string.format(m))

        return textToDraw

    def valueFormatChanged(self):
        self.updateFlags = 0;

        if "%v" in self.format:
            self.updateFlags |= self.UF_VALUE

        if "%p" in self.format:
            self.updateFlags |= self.UF_PERCENT

        if "%m" in self.format:
            self.updateFlags |= self.UF_MAX

        self.update()

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            dataBrush = QConicalGradient()
            dataBrush.setCenter(0.5,0.5)
            dataBrush.setCoordinateMode(QGradient.StretchToDeviceMode)

            for pos, color in self.gradientData:
                dataBrush.setColorAt(1.0 - pos, color)

            # angle
            dataBrush.setAngle(self.nullPosition)

            p = self.palette()
            p.setBrush(QPalette.Highlight, dataBrush)
            self.setPalette(p)