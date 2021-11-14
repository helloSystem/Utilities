#!/usr/bin/env python3

# Hardware Probe
# Copyright (c) 2020-21, Simon Peter <probono@puredarwin.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Stethoscope Icon
# https://iconarchive.com/show/pry-system-icons-by-jonas-rask/Stethoscope-icon.html
# Artist: Jonas Rask Design
# Iconset: Pry System Icons (64 icons)
# License: Free for non-commercial use.
# Commercial usage: Not allowed

import sys, os, re, socket
import shutil
from datetime import datetime

from PyQt5 import QtWidgets, QtGui, QtCore # pkg install py37-qt5-widgets

# Plenty of TODOs and FIXMEs are sprinkled across this code.
# These are invitations for new contributors to implement or comment on how to best implement.
# These things are not necessarily hard, just no one had the time to do them so far.


# Translate this application using Qt .ts files without the need for compilation
import tstranslator
# FIXME: Do not import translations from outside of the appliction bundle
# which currently is difficult because we have all translations for all applications
# in the whole repository in the same .ts files
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "")
def tr(input):
    return tstr.tr(input)


#############################################################################
# Helper functions
#############################################################################

def internetCheckConnected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


#############################################################################
# Initialization
# https://doc.qt.io/qt-5/qwizard.html
#############################################################################


app = QtWidgets.QApplication(sys.argv)

class Wizard(QtWidgets.QWizard, object):
    def __init__(self):

        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor)) # It can take some time before we show the initial page, because hw-probe runs there

        print("Preparing wizard")
        super().__init__()

        self.should_show_last_page = False
        self.error_message_nice = tr("An unknown error occured.")

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(os.path.dirname(__file__) + '/Stethoscope-icon.png'))
        self.setOption(QtWidgets.QWizard.ExtendedWatermarkPixmap, True) # Extend WatermarkPixmap all the way down to the window's edge; https://doc.qt.io/qt-5/qwizard.html#wizard-look-and-feel

        self.hw_probe_tool = '/usr/local/bin/hw-probe'
        self.server_probe_url = None
        self.local_probe_path = None

        self.setWindowTitle(tr("Hardware Probe"))
        self.setFixedSize(600, 400)

        self.setSubTitleFormat(QtCore.Qt.RichText) # Allow HTML; Qt 5.14+ also have an option for Markdown

        # Translate the widgets in the UI objects in the Wizard
        self.setWindowTitle(tr(self.windowTitle()))
        for e in self.findChildren(QtCore.QObject, None, QtCore.Qt.FindChildrenRecursively):
            if hasattr(e, 'text') and hasattr(e, 'setText'):
                e.setText(tr(e.text()))

    def showErrorPage(self, message):
        print("Show error page")
        self.addPage(ErrorPage())
        # It is not possible jo directly jump to the last page from here, so we need to take a workaround
        self.should_show_last_page = True
        self.error_message_nice = message
        self.next()

    # When we are about to go to the next page, we need to check whether we have to show the error page instead
    def nextId(self):
        if self.should_show_last_page == True:
            return max(wizard.pageIds())
        else:
            return self.currentId() + 1

    def playSound(self):
        print("Playing sound")
        soundfile = os.path.dirname(__file__) + '/success.ogg' # https://freesound.org/people/Leszek_Szary/sounds/171670/, licensed under CC0

        proc = QtCore.QProcess()
        command = 'ogg123'
        args = ['-q', soundfile]
        print(command, args)
        try:
            proc.startDetached(command, args)
        except:
            pass


wizard = Wizard()

#############################################################################
# Privacy Information
#############################################################################

class PrivacyPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Privacy Information")
        super().__init__()

        self.setTitle(tr('Privacy Information'))
        self.setSubTitle(tr('Uploading a Hardware Probe is subject to the following Pricacy Terms.'))
        license_label = QtWidgets.QTextBrowser()
        license_layout = QtWidgets.QVBoxLayout(self)
        license_text = open(os.path.dirname(__file__) + '/intro.txt', 'r').read()
        license_label.setText(license_text)  # Skip the first 3 lines
        font = wizard.font()
        font.setPointSize(9)
        license_label.setFont(font)

        license_layout.addWidget(license_label)

        additional_licenses_label = QtWidgets.QLabel()
        additional_licenses_label.setWordWrap(True)
        additional_licenses_label.setText(tr('Please see %s for more information.') % '<a href="https://bsd-hardware.info">https://bsd-hardware.info</a>')
        license_layout.addWidget(additional_licenses_label)

#############################################################################
# Intro page
#############################################################################

class IntroPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing IntroPage")
        super().__init__()

        self.setTitle(tr('Hardware Probe'))
        self.setSubTitle(tr("""<p>This utility collects hardware details of your computer and can anonymously upload them to a public database.</p>
        <p>This can help users and operating system developers to collaboratively debug hardware related issues, check for operating system compatibility and find drivers.</p>
        <p>You will get a permanent probe URL to view and share collected information.</p><br><br><br>"""))

        layout = QtWidgets.QVBoxLayout(self)
        # layout.addWidget(center_widget, True) # True = add stretch vertically

        wizard.showHardwareProbeButton = QtWidgets.QPushButton(tr('Show Hardware Probe'), self)
        wizard.showHardwareProbeButton.clicked.connect(self.showHardwareProbeButtonClicked)
        wizard.showHardwareProbeButton.setDisabled(True)
        layout.addWidget(wizard.showHardwareProbeButton)

    def showHardwareProbeButtonClicked(self):
        print("showHardwareProbeButtonClicked")
        print("self.local_probe_path: %s" % self.local_probe_path)
        proc = QtCore.QProcess()
        command = 'launch'
        args = ["Filer", self.local_probe_path]
        try:
            print("Starting %s %s" % (command, args))
            proc.startDetached(command, args)
        except:
            wizard.showErrorPage(tr("Failed to open the hardware probe."))
            return

    def initializePage(self):
        print("Displaying IntroPage")

        # Without this, the window does not get shown before run_probe_locally is done; why?
        workaroundtimer = QtCore.QTimer()
        workaroundtimer.singleShot(200, self.run_probe_locally)

    def run_probe_locally(self):
        proc = QtCore.QProcess()

        command = 'sudo'
        args = ["-A", "-E", self.wizard().hw_probe_tool, "-all"]

        try:
            print("Starting %s %s" % (command, args))
            proc.start(command, args)
        except:
            wizard.showErrorPage(tr("Failed to run the %s tool." % wizard.hw_probe_tool)) # This does not catch most cases of errors; hence see below
            return
        proc.waitForFinished()

        output_lines = proc.readAllStandardOutput().split("\n")
        err_lines = proc.readAllStandardError().split("\n")
        if len(output_lines) > 2:
            self.local_probe_path = str(output_lines[len(output_lines)-2], encoding='utf-8').split(":")[1].strip() # /root/HW_PROBE/LATEST/hw.info
            print("self.local_probe_path: %s" % self.local_probe_path)
        else:
            wizard.showErrorPage(tr("Failed to run the %s tool." % wizard.hw_probe_tool)) # This catches most cases if something goes wrong
            return

        # Make the Hardware Probe owned by user for easy access by the user

        command = 'sudo'
        args = ["-A", "-E", "chown", "-R", os.environ.get('USER'), self.local_probe_path]

        try:
            print("Starting %s %s" % (command, args))
            proc.start(command, args)
        except:
            wizard.showErrorPage(tr(
                "Failed to set the owner to %x.") % os.environ.get('USER'))  # This does not catch most cases of errors; hence see below
            return
        proc.waitForFinished()

        wizard.showHardwareProbeButton.setDisabled(False)
        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

#############################################################################
# Installation page
#############################################################################

class UploadPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing InstallationPage")
        super().__init__()

        self.setTitle(tr('Uploading Hardware Probe'))
        self.setSubTitle(tr('The Hardware Probe is being uploaded to the public database'))

        self.layout = QtWidgets.QVBoxLayout(self)
        wizard.progress = QtWidgets.QProgressBar(self)
        # Set the minimum, maximum and current values to get an indeterminate progress bar
        wizard.progress.setMaximum(0)
        wizard.progress.setMinimum(0)
        wizard.progress.setValue(0)
        self.layout.addWidget(wizard.progress, True)

    def initializePage(self):
        print("Displaying InstallationPage")
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch])

        if internetCheckConnected() == False:
            print("Offline?")
            wizard.showErrorPage(tr("You need an active internet connection in order to upload."))
            return

        # Without this, the progress bar does not get shown at all; why?
        workaroundtimer = QtCore.QTimer()
        workaroundtimer.singleShot(200, self.upload)

    def upload(self):
        print("Starting Upload")

        proc = QtCore.QProcess()
        command =  "sudo"
        args = ["-A", "-E", wizard.hw_probe_tool, "-all", "-upload"]
        try:
            print("Starting %s %s" % (command, args))
            proc.start(command, args)
        except:
            wizard.showErrorPage(tr("Failed to upload using the %s tool." % wizard.hw_probe_tool)) # This does not catch most cases of errors; hence see below
            return
        proc.waitForFinished()
        # DIXME: What can we do so that the progress bar stays animatged without the need for threading?
        output_lines = proc.readAllStandardOutput().split("\n")
        err_lines = proc.readAllStandardError().split("\n")
        if err_lines[0] != "":
            wizard.showErrorPage(str(err_lines[0], encoding='utf-8'))
            return
        elif len(output_lines) > 2:
            for line in output_lines:
                line = str(line, encoding='utf-8')
                print(line)
                if "Probe URL:" in line:
                    wizard.server_probe_url = line.replace("Probe URL:","").strip()  # Probe URL: https://bsd-hardware.info/?probe=...
                    print("wizard.server_probe_url: %s" % wizard.server_probe_url)
        else:
            wizard.showErrorPage(tr("Failed to upload using the %s tool." % wizard.hw_probe_tool)) # This catches most cases if something goes wrong
            return

        wizard.next()

#############################################################################
# Success page
#############################################################################

class SuccessPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing SuccessPage")
        super().__init__()
        self.timer = QtCore.QTimer()  # Used to periodically check the available disks

    def initializePage(self):
        print("Displaying SuccessPage")
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

        # wizard.playSound()

        self.setTitle(tr('Hardware Probe Uploaded'))
        self.setSubTitle(tr('Thank you for uploading your Hardware Probe.'))

        logo_pixmap = QtGui.QPixmap(os.path.dirname(__file__) + '/check.png').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget =  QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(center_widget, True) # True = add stretch vertically

        # label = QtWidgets.QLabel()
        # label.setText("You can view it at <a href='%s'>%s</a>" % (wizard.server_probe_url, wizard.server_probe_url))
        # label.setWordWrap(True)
        # layout.addWidget(label)

        wizard.showUploadedProbeButton = QtWidgets.QPushButton(re('Show uploaded Hardware Probe'), self)
        wizard.showUploadedProbeButton.clicked.connect(self.showUploadedProbeButtonClicked)
        layout.addWidget(wizard.showUploadedProbeButton)

        self.setButtonText(wizard.CancelButton, tr("Quit"))
        wizard.setButtonLayout([QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

    def showUploadedProbeButtonClicked(self):
        print("showHardwareProbeButtonClicked")
        print("wizard.server_probe_url: %s" % wizard.server_probe_url)
        proc = QtCore.QProcess()
        command = 'launch'
        args = ["Falkon", wizard.server_probe_url]
        try:
            print("Starting %s %s" % (command, args))
            proc.startDetached(command, args)
        except:
            wizard.showErrorPage(tr("Failed to open the uploaded hardware probe."))
            return

#############################################################################
# Error page
#############################################################################

class ErrorPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing ErrorPage")
        super().__init__()

        self.setTitle(tr('Error'))
        self.setSubTitle(tr('Hardware Probe was not successful.'))

        logo_pixmap = QtGui.QPixmap(os.path.dirname(__file__) + '/cross.png').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget =  QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(center_widget, True) # True = add stretch vertically

        self.label = QtWidgets.QLabel()  # Putting it in initializePage would add another one each time the page is displayed when going back and forth
        self.layout.addWidget(self.label)

    def initializePage(self):
        print("Displaying ErrorPage")
        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        wizard.showHardwareProbeButton.hide() # FIXME: Why is this needed?
        wizard.progress.hide()  # FIXME: Why is this needed?
        # wizard.playSound()
        self.label.setWordWrap(True)
        self.label.clear()
        self.label.setText(wizard.error_message_nice)
        self.setButtonText(wizard.CancelButton, "Quit")
        wizard.setButtonLayout([QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

#############################################################################
# Pages flow in the wizard
#############################################################################

intro_page = IntroPage()
wizard.addPage(intro_page)

license_page = PrivacyPage()
wizard.addPage(license_page)
installation_page = UploadPage()
wizard.addPage(installation_page)
success_page = SuccessPage()
wizard.addPage(success_page)

wizard.show()
sys.exit(app.exec_())
