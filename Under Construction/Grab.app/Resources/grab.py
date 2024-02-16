#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QActionGroup, qApp, QPushButton
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QShowEvent
from PyQt5.QtCore import Qt, QTimer, QLoggingCategory, QByteArray, QSettings, QUrl
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
import sys
import os

# The Main Window
from main_window_ui import Ui_MainWindow
from dialog_timed_screen_grab import TimedScreenGrabDialog
from dialog_screen_grab import ScreenGrabDialog
from dialog_help import HelpDialog
from dialog_selection_screen_grab import SelectionGrabDialog
from widget_transparent_window import TransWindow
from widget_snipping_tool import SnippingWidget
from preference_window import PreferenceWindow

QLoggingCategory.setFilterRules("*.debug=false\nqt.qpa.*=false")


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__()
        self.parent = parent
        self.screen = qApp
        self.initialized = False
        self.transparent_window_opacity = None
        self.selection_color_background = None
        self.selection_color_border = None
        self.selection_color_opacity = None
        self.selection_wight_border = None

        self.settings = None
        self.fileName = None
        self.printerObj = None
        self.timer_count = None
        self.scale_factor = None

        self.snippingWidget = None
        self._pixmap = None
        self.sound = None

        self.TimedScreenGrabDialog = None
        self.ScreenGrabDialog = None
        self.SelectionGrabDialog = None
        self.TransWindow = None
        self.PreferenceWindow = None
        self.preference_pointer = None
        self.preference_enable_sound = None

        self.setupUi(self)
        self.setupCustomUi()
        self.setupCustomUiGroups()
        self.connectSignalsSlots()
        self.initialized = False
        self.initialState()

    def initialState(self):
        self.ActionMenuFilePrint.setEnabled(False)
        self.ActionMenuFilePrintSetup.setEnabled(False)
        self.ActionMenuViewFitToWindow.setEnabled(False)

        # Image viewer
        # Set viewer's aspect ratio mode.
        self.img_preview.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio
        # Set the viewer's scroll bar behaviour.
        self.img_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.img_preview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.img_preview.regionZoomButton = Qt.MouseButton.LeftButton  # set to None to disable
        # Pop end of zoom stack (double click clears zoom stack).
        self.img_preview.zoomOutButton = Qt.MouseButton.RightButton  # set to None to disable
        # Mouse wheel zooming.
        self.img_preview.wheelZoomFactor = 1.25  # Set to None or 1 to disable
        # Allow panning with the middle mouse button.
        self.img_preview.panButton = Qt.MouseButton.MiddleButton  # set to None to disable

        self.timer_count = 10000
        self.setWindowTitle("Untitled[*]")
        self.resize(370, 270)

        self.settings = QSettings("helloSystem", "Grab.app")
        self.read_settings()

        self.snipFull()
        self.initialized = True

    def setupCustomUi(self):
        # creating an object of the QPrinter class
        self.printerObj = QPrinter()

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Grab.png")))

        self.snippingWidget = SnippingWidget()

        self.sound = QMediaPlayer()
        self.sound.setMedia(
            QMediaContent(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "trigger_of_camera.wav")))
        )

    def setupCustomUiGroups(self):
        menu_frequency_group = QActionGroup(self)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo1Sec)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo2Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo3Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo4Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo5Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo6Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo7Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo8Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo9Secs)
        menu_frequency_group.addAction(self.ActionUpdateTimerTo10Secs)

    def connectSignalsSlots(self):
        # File
        self.ActionMenuFileClose.triggered.connect(self.close)
        self.ActionMenuFileSave.triggered.connect(self.save)
        self.ActionMenuFileSaveAs.triggered.connect(self.save_as)
        self.ActionMenuFilePrint.triggered.connect(self.print_image)
        self.ActionMenuFilePrintSetup.triggered.connect(self.print_preview_image)

        # Edit
        self.ActionMenuEditCopy.triggered.connect(self.copy_to_clipboard)
        self.ActionMenuEditPreference.triggered.connect(self._showPreferenceWindow)

        # View
        self.ActionMenuViewZoomIn.triggered.connect(self.img_preview.zoomIn)
        self.ActionMenuViewZoomOut.triggered.connect(self.img_preview.zoomOut)
        self.ActionMenuViewZoomClear.triggered.connect(self.img_preview.clearZoom)

        # Capture
        self.ActionMenuCaptureScreen.triggered.connect(self._showScreenGrabDialog)
        self.ActionMenuCaptureSelection.triggered.connect(self._showSelectionGrabDialog)
        self.ActionMenuCaptureTimedScreen.triggered.connect(self._showTimedScreenGrabDialog)

        # Capture / Timer
        self.ActionUpdateTimerTo1Sec.triggered.connect(self._timer_change_for_1_sec)
        self.ActionUpdateTimerTo2Secs.triggered.connect(self._timer_change_for_2_secs)
        self.ActionUpdateTimerTo3Secs.triggered.connect(self._timer_change_for_3_secs)
        self.ActionUpdateTimerTo4Secs.triggered.connect(self._timer_change_for_4_secs)
        self.ActionUpdateTimerTo5Secs.triggered.connect(self._timer_change_for_5_secs)
        self.ActionUpdateTimerTo6Secs.triggered.connect(self._timer_change_for_6_secs)
        self.ActionUpdateTimerTo7Secs.triggered.connect(self._timer_change_for_7_secs)
        self.ActionUpdateTimerTo8Secs.triggered.connect(self._timer_change_for_8_secs)
        self.ActionUpdateTimerTo9Secs.triggered.connect(self._timer_change_for_9_secs)
        self.ActionUpdateTimerTo10Secs.triggered.connect(self._timer_change_for_10_secs)

        # Capture / Area

        # self.ui.pushButton_area.clicked.connect(self.snipArea)
        # self.ui.pushButton_full.clicked.connect(self.snipFull)

        # About
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)
        self.ActionMenuHelpDocumentation.triggered.connect(self._showHelpDialog)

        # Snipping widget
        self.snippingWidget.snipping_completed.connect(self.onSnippingCompleted)

    def onSnippingCompleted(self, img):
        self.setWindowState(Qt.WindowActive)

        if img is None:
            return

        if self.preference_enable_sound and self.initialized:
            self.sound.play()

        self.img_preview.setImage(img)
        self.img_preview.clearZoom()

        self.fileName = None
        self.setWindowTitle("Untitled[*]")

        self.setWindowModified(True)

        self.update_actions()

    def snipArea(self):
        self.setWindowState(Qt.WindowMinimized)
        self.snippingWidget.start()

    def snipFull(self):
        self.setWindowState(Qt.WindowMinimized)
        self.snippingWidget.fullscreen()

    def write_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("preference_enable_sound", self.preference_enable_sound)
        self.settings.setValue("preference_pointer", self.preference_pointer)

    def read_settings(self):
        self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        self.restoreState(self.settings.value("windowState", QByteArray()))
        self.preference_enable_sound = self.settings.value("preference_enable_sound", defaultValue=True, type=bool)
        self.preference_pointer = self.settings.value("preference_pointer", defaultValue=10, type=int)
        self.snippingWidget.cursor = self.preference_pointer

    def closeEvent(self, event):
        self.write_settings()
        super(Window, self).closeEvent(event)
        event.accept()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        filename = urls[0].toLocalFile()
        self.loadFile(filename)
        self.decodeFile(filename)
        event.acceptProposedAction()

    def save(self):
        if not self.isWindowModified():
            return
        if not self.fileName:
            self.save_as()
        else:
            if self.fileName[-3:] == "png":
                self.img_preview.pixmap().save(self.fileName, "png")
            elif self.fileName[-3:] == "jpg":
                self.img_preview.pixmap().save(self.fileName, "jpg")
            self.setWindowTitle("%s[*]" % (os.path.basename(self.fileName)))
            self.setWindowModified(False)

    def save_as(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", filter="PNG(*.png);; JPEG(*.jpg)", options=options
        )
        if fileName:
            if fileName[-3:] == "png":
                self.img_preview.pixmap().save(fileName, "png")
            elif fileName[-3:] == "jpg":
                self.img_preview.pixmap().save(fileName, "jpg")
            self.fileName = fileName
            self.setWindowTitle("%s[*]" % (os.path.basename(self.fileName)))
            self.setWindowModified(False)

    def copy_to_clipboard(self):
        if not self.img_preview.pixmap():
            return
        qi = self.img_preview.pixmap().toImage()
        QApplication.clipboard().setImage(qi)

    def new_timed_screenshot(self):
        QTimer.singleShot(self.timer_count, self.snipFull)

    def normal_size(self):
        self.img_preview.clearZoom()

    def fit_to_window(self):
        # retrieving the Boolean value from the "Fit To Window" action
        self.ActionMenuViewFitToWindow.setEnabled(False)
        fitToWindow = self.ActionMenuViewFitToWindow.isChecked()
        # configuring the scroll area to resizable
        # self.scroll_area.setWidgetResizable(fitToWindow)
        # if the retrieved value is False, calling the user-defined normal_size() method
        if not fitToWindow:
            self.normal_size()
            # calling the user-defined update_actions() method
        # self.update_actions()

    # defining the method to update the actions
    def update_actions(self):
        if self.img_preview.pixmap().isNull():
            self.ActionMenuFileSave.setEnabled(False)
            self.ActionMenuFileSaveAs.setEnabled(False)
            self.ActionMenuFilePrint.setEnabled(False)
            self.ActionMenuFilePrintSetup.setEnabled(False)

            self.ActionMenuViewActualSize.setEnabled(False)
            self.ActionMenuViewZoomToFit.setEnabled(False)
            self.ActionMenuViewZoomIn.setEnabled(False)
            self.ActionMenuViewZoomOut.setEnabled(False)
            self.ActionMenuViewZoomToSelection.setEnabled(False)
        else:
            self.ActionMenuFileSave.setEnabled(True)
            self.ActionMenuFileSaveAs.setEnabled(True)
            self.ActionMenuFilePrint.setEnabled(True)
            self.ActionMenuFilePrintSetup.setEnabled(True)

            self.ActionMenuViewActualSize.setEnabled(True)
            self.ActionMenuViewZoomToFit.setEnabled(True)
            self.ActionMenuViewZoomIn.setEnabled(True)
            self.ActionMenuViewZoomOut.setEnabled(True)
            self.ActionMenuViewZoomToSelection.setEnabled(True)

    def print_image(self):
        # creating an object of the QPrintDialog class
        print_dialog = QPrintDialog(self.printerObj, self)
        # if the print action is executed
        if print_dialog.exec_():
            # creating an object of the QPainter class by passing the object of the QPrinter class
            the_painter = QPainter(self.printerObj)
            # creating a rectangle to place the image
            rectangle = the_painter.viewport()
            # defining the size of the image
            the_size = self.img_preview.pixmap().size()
            # scaling the image to the Aspect Ratio
            the_size.scale(rectangle.size(), Qt.KeepAspectRatio)
            # setting the viewport of the image by calling the setViewport() method
            the_painter.setViewport(rectangle.x(), rectangle.y(), the_size.width(), the_size.height())
            # calling the setWindow() method
            the_painter.setWindow(self.img_preview.pixmap().rect())
            # calling the drawPixmap() method
            the_painter.drawPixmap(0, 0, self.img_preview.pixmap())

    def print_preview_image(self):
        # Initializes the QPainter and draws the pixmap onto it
        def drawImage(printer):
            the_painter = QPainter()
            the_painter.begin(printer)
            # creating a rectangle to place the image
            rectangle = the_painter.viewport()
            # defining the size of the image
            the_size = self.img_preview.pixmap().size()
            # scaling the image to the Aspect Ratio
            the_size.scale(rectangle.size(), Qt.KeepAspectRatio)
            # setting the viewport of the image by calling the setViewport() method
            the_painter.setViewport(rectangle.x(), rectangle.y(), the_size.width(), the_size.height())
            # calling the setWindow() method
            the_painter.setWindow(self.img_preview.pixmap().rect())
            # calling the drawPixmap() method
            the_painter.drawPixmap(0, 0, self.img_preview.pixmap())

            the_painter.end()

        # Shows the preview
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(drawImage)
        dlg.exec_()

    def _preference_enable_sound_changed(self, value: bool) -> None:
        self.preference_enable_sound = value
        self.snippingWidget.enable_sound = self.preference_enable_sound

    def _preference_pointer_changed(self, value: int) -> None:
        self.preference_pointer = value
        self.img_preview.cursor = self.preference_pointer
        self.snippingWidget.cursor = self.preference_pointer

    def _showPreferenceWindow(self):
        if self.ActionMenuEditPreference.isEnabled():
            self.PreferenceWindow = PreferenceWindow(
                play_sound=self.preference_enable_sound, pointer=self.preference_pointer
            )
            self.PreferenceWindow.checkbox_enable_sound_changed.connect(self._preference_enable_sound_changed)
            self.PreferenceWindow.buttongroup_changed.connect(self._preference_pointer_changed)
            self.PreferenceWindow.show()

    @staticmethod
    def _showAboutDialog():
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(
            QPixmap(os.path.join(os.path.dirname(__file__), "Grab.png")).scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        msg.addButton(QPushButton("Ok"), QMessageBox.AcceptRole)
        candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
        for candidate in candidates:
            if os.path.exists(os.path.join(os.path.dirname(__file__), candidate)):
                with open(os.path.join(os.path.dirname(__file__), candidate), "r") as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText(f"<h3>{qApp.applicationName()}</h3>")
        msg.setInformativeText(
            f"{qApp.applicationName()} is an application write in pyQt5 that can capture screen shots.<br><br>"
            "<a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>"
        )
        msg.exec()

    def _showScreenGrabDialog(self):
        if self.ActionMenuCaptureTimedScreen.isEnabled():
            self.hide()

            # self.ScreenGrabDialog.setWindowFlags(self.ScreenGrabDialog.windowFlags() & Qt.WindowStaysOnTopHint)

            self.ScreenGrabDialog = ScreenGrabDialog(self)
            self.ScreenGrabDialog.screen_dialog_signal_quit.connect(self._CloseAllDialogs)
            self.ScreenGrabDialog.screen_dialog_signal_start.connect(self._ScreenGrabStart)

            # self.TransWindow = TransWindow(self)
            # self.TransWindow.transparent_window_signal_release.connect(self._ScreenGrabStart)
            # self.TransWindow.transparent_window_signal_quit.connect(self._CloseAllDialogs)

            self.ScreenGrabDialog.hide()
            self.ScreenGrabDialog.show()

            # self.TransWindow.hide()
            # self.TransWindow.show()

            while not self.windowHandle():
                QApplication.processEvents()

    def _showSelectionGrabDialog(self):
        if self.ActionMenuCaptureSelection.isEnabled():
            self.hide()

            # self.ScreenGrabDialog.setWindowFlags(self.ScreenGrabDialog.windowFlags() & Qt.WindowStaysOnTopHint)

            self.SelectionGrabDialog = SelectionGrabDialog(self)
            self.SelectionGrabDialog.selection_dialog_signal_quit.connect(self._CloseAllDialogs)
            self.SelectionGrabDialog.selection_dialog_signal_start.connect(self._SelectionGrabStart)

            self.SelectionGrabDialog.show()

    def hideEvent(self, event: QShowEvent) -> None:
        super(Window, self).setWindowOpacity(0.0)
        super(Window, self).hideEvent(event)
        event.accept()

    def showEvent(self, event: QShowEvent) -> None:
        super(Window, self).setWindowOpacity(1.0)
        super(Window, self).showEvent(event)
        event.accept()

    def _SelectionGrabStart(self):
        self._CloseAllDialogs()
        self.snipArea()

    def _ScreenGrabStart(self):
        self._CloseAllDialogs()
        self.snipFull()
        # self.take_screenshot()

    def _showTimedScreenGrabDialog(self):
        if self.ActionMenuCaptureTimedScreen.isEnabled():
            self.hide()
            if self.TimedScreenGrabDialog is None:
                self.TimedScreenGrabDialog = TimedScreenGrabDialog(timer=self.timer_count)
                self.TimedScreenGrabDialog.timer_dialog_signal_start.connect(self._TimedScreenGrabStart)
                self.TimedScreenGrabDialog.timer_dialog_signal_quit.connect(self._CloseAllDialogs)
                self.TimedScreenGrabDialog.exec_()
            self.show()

    def _TimedScreenGrabStart(self):
        self._CloseAllDialogs()
        self.new_timed_screenshot()

    def _CloseAllDialogs(self):
        if self.TimedScreenGrabDialog and isinstance(self.TimedScreenGrabDialog, TimedScreenGrabDialog):
            self.TimedScreenGrabDialog.close()
            self.TimedScreenGrabDialog = None
        if self.ScreenGrabDialog and isinstance(self.ScreenGrabDialog, ScreenGrabDialog):
            self.ScreenGrabDialog.close()
            self.ScreenGrabDialog = None
        if self.TransWindow and isinstance(self.TransWindow, TransWindow):
            self.TransWindow.close()
            self.TransWindow = None
        if self.SelectionGrabDialog and isinstance(self.SelectionGrabDialog, SelectionGrabDialog):
            self.SelectionGrabDialog.close()
            self.SelectionGrabDialog = None
        if self.isHidden():
            self.show()

        while not self.windowHandle():
            QApplication.processEvents()

        QApplication.flush()

    def _timer_change_for(self, value):
        self.timer_count = value

    def _timer_change_for_1_sec(self):
        self.timer_count = 1000

    def _timer_change_for_2_secs(self):
        self.timer_count = 2000

    def _timer_change_for_3_secs(self):
        self.timer_count = 3000

    def _timer_change_for_4_secs(self):
        self.timer_count = 4000

    def _timer_change_for_5_secs(self):
        self.timer_count = 5000

    def _timer_change_for_6_secs(self):
        self.timer_count = 6000

    def _timer_change_for_7_secs(self):
        self.timer_count = 7000

    def _timer_change_for_8_secs(self):
        self.timer_count = 8000

    def _timer_change_for_9_secs(self):
        self.timer_count = 9000

    def _timer_change_for_10_secs(self):
        self.timer_count = 10000

    def _showHelpDialog(self):
        if self.ActionMenuHelpAbout.isEnabled():
            self.HelpDialog = HelpDialog()
            self.HelpDialog.show()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Grab")
    app.setApplicationDisplayName("Grab")
    app.setApplicationVersion("0.1")
    window = Window()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
