#!/usr/bin/env python3

# Create Live Media
# Copyright (c) 2020-2023, Simon Peter <probono@puredarwin.org>
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

# USB drive image created by vectorpouch - www.freepik.com
# https://www.freepik.com/free-vector/usb-flash-drive-illustration-3d-realistic-memory-stick_3090678.htm
# The full terms of the license are described in section 7 of the Freepik
# terms of use, available online in the following link:
# http://www.freepik.com/terms_of_use

import socket  # Before urllib so that we can set the timeout
import sys
import os
import re
import socket
import shutil
from datetime import datetime, timedelta
import urllib.request
import json
# pkg install py37-qt5-widgets
from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
import disks  # Privately bundled file

import ssl

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
import FileSystemInfo

# FIXME: Do not import translations from outside of the application bundle
# which currently is difficult because we have all translations for all applications
# in the whole repository in the same .ts files
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "")


def tr(input):
    return tstr.tr(input)


# Since we are running the wizard on Live systems which more likely than not may have
# the clock wrong, we cannot verify SSL certificates. Setting the following allows
# content to be fetched from https locations even if the SSL certification cannot be verified.
# This is needed, e.g., for geolocation.
ssl._create_default_https_context = ssl._create_unverified_context

# Plenty of TODOs and FIXMEs are sprinkled across this code.
# These are invitations for new contributors to implement or comment on how to best implement.
# These things are not necessarily hard, just no one had the time to do them so far.
# TODO: Make translatable


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


class InstallWizard(QtWidgets.QWizard, object):
    def __init__(self):

        print("Preparing wizard")
        super().__init__()

        self.selected_disk_device = None
        self.user_agreed_to_erase = False
        self.selected_iso_url = None
        self.geolocation = None
        self.timezone = None
        self.required_mib_on_disk = 0

        # TODO: Make sure it is actually executable

        self.should_show_last_page = False
        self.error_message_nice = "An unknown error occurred."

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(
            os.path.dirname(__file__) + '/bgusb.png'))

        self.setWindowTitle("Create Live Media")
        self.setFixedSize(600, 400)

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
        # https://freesound.org/people/Leszek_Szary/sounds/171670/, licensed under CC0
        soundfile = os.path.dirname(__file__) + '/success.mp3'
        if os.path.exists(soundfile):
            try:
                subprocess.run(["mpg321", soundfile],
                               stdout=subprocess.PIPE, text=True)
            except:
                pass
        else:
            print("No sound available")


wizard = InstallWizard()


#############################################################################
# Intro page
#############################################################################

class IntroPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing IntroPage")
        super().__init__()

        self.setTitle(tr('Create Live Media'))
        self.setSubTitle(
            tr("This will download a Live image and will write it to an attached storage device."))

        self.releases_url = None

        self.disk_vlayout = QtWidgets.QVBoxLayout(self)

        # Repo dropdown

        self.repo_menu = QtWidgets.QComboBox()
        # "https://api.github.com/repos/mszoek/airyx/releases", "https://api.github.com/repos/probonopd/furybsd-livecd/releases", "https://api.github.com/repos/probonopd/ghostbsd-build/releases", "https://api.github.com/repos/andydotxyz/furybsd-livecd/releases"]
        self.available_repos = ["https://api.github.com/repos/helloSystem/ISO/releases",
                                "https://api.github.com/repos/ventoy/Ventoy/releases"]
        for available_repo in self.available_repos:
            self.repo_menu.addItem("/".join(available_repo.split("/")[4:6]))
        self.other_iso = tr("Other...")
        self.repo_menu.addItem(self.other_iso)
        self.available_repos.append(self.other_iso)
        self.local_iso = tr("Local ISO file...")
        self.repo_menu.addItem(self.local_iso)
        self.available_repos.append(self.local_iso)

        self.disk_vlayout.addWidget(self.repo_menu)
        self.repo_menu.currentTextChanged.connect(self.populateImageList)
        # wizard.selected_iso_url = "file:///usr/home/user/Downloads/alpine-standard-3.13.0-x86_64.iso"
        # urllib.request.urlretrieve(wizard.selected_iso_url, self.save_loc, self.handleProgress)

        # Release label
        self.label = QtWidgets.QLabel()
        self.label.setText(tr("Please choose an image:"))
        self.disk_vlayout.addWidget(self.label)

        # Release ListWidget
        self.release_listwidget = QtWidgets.QListWidget()
        self.disk_vlayout.addWidget(self.release_listwidget)
        self.release_listwidget.itemSelectionChanged.connect(
            self.onSelectionChanged)
        self.release_listwidget.setAlternatingRowColors(True)

        # Date label
        self.date_label = QtWidgets.QLabel()
        self.date_label.setText(tr("Date"))
        self.date_label.hide()
        self.disk_vlayout.addWidget(self.date_label)

        # URL label
        self.url_label = QtWidgets.QLabel()
        self.url_label.setText(tr("URL"))
        self.url_label.hide()
        self.disk_vlayout.addWidget(self.url_label)

        # Checkbox for Pre-release and Experimental builds
        self.prerelease_checkbox = QtWidgets.QCheckBox()
        self.prerelease_checkbox.setText(tr("Show Pre-release builds"))
        self.prerelease_checkbox.setChecked(False)
        self.disk_vlayout.addWidget(self.prerelease_checkbox)
        self.prerelease_checkbox.clicked.connect(self.populateImageList)

    def initializePage(self):
        print("Displaying IntroPage")
        self.populateImageList()

    def populateImageList(self):

        self.available_isos = []
        self.release_listwidget.clear()

        if self.available_repos[self.repo_menu.currentIndex()] == self.other_iso:

            text, okPressed = QtWidgets.QInputDialog.getText(self, tr("Other"), tr(
                "URL of the ISO"), QtWidgets.QLineEdit.Normal, "https://")
            if okPressed and text != '':
                print(text)

            item = QtWidgets.QListWidgetItem(os.path.basename(text))
            item.__setattr__("browser_download_url",
                             text)  # __setattr__() is the equivalent to setProperty() in Qt
            item.__setattr__(
                "updated_at", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
            item.__setattr__("size", 2*1024*1024*1024)
            item.__setattr__("prerelease", False)
            # FIXME: Can we at least attempt to get the real size from the URL?
            self.release_listwidget.addItem(item)
            return

        if self.available_repos[self.repo_menu.currentIndex()] == self.local_iso:

            filedialog = QtWidgets.QFileDialog()
            filedialog.setDefaultSuffix("iso")
            filedialog.setNameFilter(
                tr("Disk images (*.iso *.img);;All files (*.*)"))
            filename = None
            if filedialog.exec_():
                filename = filedialog.selectedFiles()[0]
            if not filename:
                return
            item = QtWidgets.QListWidgetItem(os.path.basename(filename))
            item.__setattr__("browser_download_url",
                             "file:///" + filename)  # __setattr__() is the equivalent to setProperty() in Qt
            info = QtCore.QFileInfo(filename)
            item.__setattr__(
                "updated_at", info.lastModified().toString("%Y-%m-%dT%H:%M:%SZ"))
            item.__setattr__("size", info.size())
            item.__setattr__("prerelease", False)
            # FIXME: Can we at least attempt to get the real size from the URL?
            self.release_listwidget.addItem(item)
            self.onSelectionChanged()
            return

        if internetCheckConnected() == False:
            wizard.showErrorPage(
                tr("This requires an active internet connection."))
            self.label.hide()  # FIXME: Why is this needed? Can we do without?
            self.repo_menu.hide()  # FIXME: Why is this needed? Can we do without?
            self.release_listwidget.hide()  # FIXME: Why is this needed? Can we do without?
            return

        url = self.available_repos[self.repo_menu.currentIndex()]
        print("Getting releases from", url)

        self.date_label.hide()
        self.url_label.hide()

        result = None
        try:
            result = urllib.request.urlopen(url)

        except urllib.error.HTTPError as e:
            # Show error dialog box
            dialog = QtWidgets.QMessageBox()
            dialog.setWindowTitle("   ")
            dialog.setText(
                tr("The list of available images could not be retrieved."))
            if "rate limit exceeded" in str(e):
                dialog.setInformativeText(
                    tr("You have exceeded the GitHub rate limit.\nPlease try again later."))
            else:
                dialog.setInformativeText(str(e))
            dialog.setIcon(QtWidgets.QMessageBox.Critical)
            dialog.exec_()
            sys.exit(1)

        data = json.loads(result.read().decode("utf-8"))
        # print(data)
        for release in data:
            if len(release["assets"]) > 0:
                # print(asset)
                for asset in release["assets"]:
                    if asset["browser_download_url"].endswith(".iso"):
                        # display_name = "%s (%s)" % (asset["name"], release["tag_name"])
                        display_name = "%s %s" % (
                            release["tag_name"], asset["name"])
                        self.available_isos.append(asset)
                        item = QtWidgets.QListWidgetItem(display_name)
                        # item.setIcon(QtGui.QIcon.fromTheme("media-optical"))

                        # __setattr__() is the equivalent to setProperty() in Qt
                        item.__setattr__("browser_download_url",
                                         asset["browser_download_url"])
                        item.__setattr__("updated_at", asset["updated_at"])
                        item.__setattr__("size", asset["size"])
                        item.__setattr__("prerelease", release["prerelease"])
                        item.__setattr__("tag_name", release["tag_name"])
                        item.__setattr__("name", asset["name"])
                        item.__setattr__("body", release["body"])
                        item.__setattr__("html_url", release["html_url"])
                        item.__setattr__("release", release)
                        if self.prerelease_checkbox.isChecked() == False:
                            if release["prerelease"] == False:
                                self.release_listwidget.addItem(item)
                        else:
                            if release["prerelease"] == True:
                                # Show only prerelease builds that were updated within the last 6 months
                                if datetime.strptime(asset["updated_at"], "%Y-%m-%dT%H:%M:%SZ") > datetime.now() - timedelta(days=180):
                                    self.release_listwidget.addItem(item)

        # except:
            # pass
            # wizard.showErrorPage("The list of available images could not be retrieved. GitHub rate limit exceeded?")
            # self.label.hide()  # FIXME: Why is this needed? Can we do without?
            # self.repo_menu.hide()  # FIXME: Why is this needed? Can we do without?
            # self.release_listwidget.hide()  # FIXME: Why is this needed? Can we do without?
            # return

        # Invalidate that the user already has selected something and we can proceed
        self.completeChanged.emit()

    def onSelectionChanged(self):
        print("onSelectionChanged")
        # print("selectedIndexes", self.release_listwidget.selectedIndexes())
        items = self.release_listwidget.selectedItems()
        if len(items) < 1:
            return
        # __getattribute__() is the equivalent to property() in Qt
        print("browser_download_url attribute:" +
              items[0].__getattribute__("browser_download_url"))
        wizard.selected_iso_url = items[0].__getattribute__(
            "browser_download_url")
        date = QtCore.QDateTime.fromString(
            items[0].__getattribute__("updated_at"), "yyyy-MM-ddThh:mm:ssZ")
        self.date_label.setText(date.toLocalTime().toString(
            QtCore.Qt.SystemLocaleLongDate))
        self.date_label.show()
        try:
            self.url_label.setText("<a href=\"%s\">%s</a>" % (
                items[0].__getattribute__("html_url"), items[0].__getattribute__("html_url")))
        except:
            self.url_label.setText("")
        self.url_label.show()
        wizard.required_mib_on_disk = round(
            items[0].__getattribute__("size")/1024/1024, 1)
        # self.isComplete()  # Calling it like this does not make its result get used
        # But like this isComplete() gets called and its result gets used
        self.completeChanged.emit()

    def isComplete(self):
        if wizard.selected_iso_url != None and len(self.release_listwidget.selectedItems()) == 1:
            return True
        else:
            return False

#############################################################################
# Destination disk
#############################################################################


class DiskPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing DiskPage")
        super().__init__()

        self.timer = QtCore.QTimer()  # Used to periodically check the available disks
        self.old_ds = None  # The disks we have recognized so far
        self.setTitle(tr('Select Destination Disk'))
        self.setSubTitle(tr('All data on the selected disk will be erased.'))
        self.disk_listwidget = QtWidgets.QListWidget()
        # self.disk_listwidget.setViewMode(QtWidgets.QListView.IconMode)
        self.disk_listwidget.setIconSize(QtCore.QSize(48, 48))
        # self.disk_listwidget.setSpacing(24)
        self.disk_listwidget.itemSelectionChanged.connect(
            self.onSelectionChanged)
        disk_vlayout = QtWidgets.QVBoxLayout(self)
        disk_vlayout.addWidget(self.disk_listwidget)
        self.label = QtWidgets.QLabel()
        disk_vlayout.addWidget(self.label)

    def initializePage(self):
        print("Displaying DiskPage")

        # If the user clicked back and forth, start with nothing selected
        self.disk_listwidget.clearSelection()
        self.periodically_list_disks()

        if wizard.required_mib_on_disk < 5:
            self.timer.stop()
            wizard.showErrorPage(
                tr("Could not determine the required disk space."))
            self.disk_listwidget.hide()  # FIXME: Why is this needed? Can we do without?
            return

        print("Disk space required: %d MiB" % wizard.required_mib_on_disk)
        self.label.setText(tr("Disk space required: %s MiB") %
                           wizard.required_mib_on_disk)

    def cleanupPage(self):
        print("Leaving DiskPage")

    def periodically_list_disks(self):
        print("periodically_list_disks")
        self.list_disks()

        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.list_disks)
        self.timer.start()

    def list_disks(self):

        ds = disks.get_disks()
        # Do not refresh the list of disks if nothing has changed, because it de-selects the selection
        if ds != self.old_ds:
            self.disk_listwidget.clear()
            for d in ds:
                di = disks.get_disk(d)
                # print(di)
                # print(di.get("descr"))
                # print(di.keys())
                # Only show disks that are above minimum_target_disk_size and are writable
                available_bytes = int(di.get("mediasize").split(" ")[0])
                # For now, we don't show cd* but once we add burning capabilities we may want to un-blacklist them
                # TODO: Identify the disk the Live system is running from, and don't offer that
                if (available_bytes >= wizard.required_mib_on_disk) and di.get("geomname").startswith("cd") == False:
                    # item.setTextAlignment()
                    title = "%s on %s (%s GiB)" % (di.get("descr"), di.get(
                        "geomname"), f"{(available_bytes // (2 ** 30)):,}")
                    if di.get("geomname").startswith("cd") == True:
                        # TODO: Add burning powers
                        item = QtWidgets.QListWidgetItem(
                            QtGui.QIcon.fromTheme('drive-optical'), title)
                    elif di.get("geomname").startswith("da") == True:
                        item = QtWidgets.QListWidgetItem(
                            QtGui.QIcon.fromTheme('drive-removable-media'), title)
                    else:
                        item = QtWidgets.QListWidgetItem(
                            QtGui.QIcon.fromTheme('drive-harddisk'), title)
                        # Prevent from selecting non-removable drives; TODO: Maybe allow selecing them with an extra warning?
                        item.setFlags(QtCore.Qt.ItemIsSelectable)

                    if available_bytes < wizard.required_mib_on_disk*1024*1024:
                        # Disk is too small
                        item.setFlags(QtCore.Qt.ItemIsSelectable)
                    self.disk_listwidget.addItem(item)
            self.old_ds = ds

    def onSelectionChanged(self):
        wizard.user_agreed_to_erase = False
        self.show_warning()

    def show_warning(self):
        # After we remove the selection, do not call this again
        if len(self.disk_listwidget.selectedItems()) != 1:
            return
        wizard.user_agreed_to_erase = False
        reply = QtWidgets.QMessageBox.warning(
            wizard,
            tr("Warning"),
            tr("This will erase all contents of this disk and install the live system on it. Continue?"),
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            print("User has agreed to erase all contents of this disk")
            wizard.user_agreed_to_erase = True
        else:
            self.disk_listwidget.clearSelection()
            pass
        # self.isComplete() # Calling it like this does not make its result get used
        # But like this isComplete() gets called and its result gets used
        self.completeChanged.emit()

    def isComplete(self):
        if wizard.user_agreed_to_erase == True:
            ds = disks.get_disks()
            # Given a clear text label, get back the rdX
            # TODO: Use __setattr__() and __getattribute__() instead; see above for an example on how to use those
            for d in self.old_ds:
                di = disks.get_disk(d)
                searchstring = " on " + str(di.get("geomname")) + " "
                print(searchstring)
                if len(self.disk_listwidget.selectedItems()) < 1:
                    return False
                if searchstring in self.disk_listwidget.selectedItems()[0].text():
                    wizard.selected_disk_device = str(di.get("geomname"))
                    self.timer.stop()  # FIXME: This does not belong here, but cleanupPage() gets called only
                    # if the user goes back, not when they go forward...
                    return True

        selected_disk_device = None
        return False

    def cleanupPage(self):
        self.timer.stop()

#############################################################################
# Installation page
#############################################################################


class InstallationPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing InstallationPage")
        super().__init__()

        self.setTitle(tr('Downloading and writing Live medium'))
        self.setSubTitle(
            tr('The Live image is being downloaded and written to the medium.'))

        self.layout = QtWidgets.QVBoxLayout(self)
        self.progress = QtWidgets.QProgressBar(self)
        self.layout.addWidget(self.progress, True)

    def initializePage(self):
        print("Displaying InstallationPage")
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch])

        # If we immediately call self.download(), then the window contents don't get drawn.
        # Hence we use a timer.
        self.save_loc = '/dev/' + wizard.selected_disk_device
        workaroundtimer = QtCore.QTimer()
        workaroundtimer.singleShot(200, self.download)

    def handleProgress(self, blocknum, blocksize, totalsize):

        processed_data = blocknum * blocksize
        # print("processed_data %i" % processed_data)
        if totalsize > 0:
            download_percentage = processed_data * 100 / totalsize
            self.progress.setValue(download_percentage)
            # Important trick so that the app stays responsive without the need for threading!
            QtWidgets.QApplication.processEvents()

    def download(self):
        print("Download started")

        import glob
        partitions = glob.glob(self.save_loc + "*")
        print("Trying to unmount %s*" % partitions)
        # Unmount all partitions on the target disk
        proc = QtCore.QProcess()
        command = '/sbin/umount'
        args = partitions
        print(command, args)
        try:
            proc.startDetached(command, args)
            proc.waitForFinished()
        except:
            wizard.showErrorPage(tr("Could not unmount partitions."))

        # Download and write directly to the device
        print(wizard.selected_iso_url)
        socket.setdefaulttimeout(240)
        print("socket.getdefaulttimeout(): %s" % socket.getdefaulttimeout())
        try:
            urllib.request.urlretrieve(
                wizard.selected_iso_url, self.save_loc, self.handleProgress)
        except BaseException as error:
            print('An error occurred: {}'.format(error))
            wizard.showErrorPage('{}'.format(error) + ".")

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

        wizard.playSound()

        self.setTitle(tr('Live Medium Complete'))
        self.setSubTitle(tr('The Live image has been written to the device.'))

        logo_pixmap = QtGui.QPixmap(os.path.dirname(
            __file__) + '/usbsuccess.png').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget = QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(center_widget, True)  # True = add stretch vertically

        label = QtWidgets.QLabel()
        label.setText(
            tr("You can now start your computer from the Live medium."))
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setButtonText(wizard.CancelButton, tr("Quit"))
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

        self.periodically_list_disks()

    def periodically_list_disks(self):
        print("periodically_list_disks")
        self.list_disks()

        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.list_disks)
        self.timer.start()

    def list_disks(self):
        ds = disks.get_disks()
        if "/dev/" + wizard.selected_disk_device not in ds:
            print(tr("Device was unplugged, exiting"))
            self.timer.stop()
            sys.exit(0)

#############################################################################
# Error page
#############################################################################


class ErrorPage(QtWidgets.QWizardPage, object):
    def __init__(self):

        print("Preparing ErrorPage")
        super().__init__()

        self.setTitle(tr('Error'))
        self.setSubTitle(tr('The installation could not be performed.'))

        logo_pixmap = QtGui.QPixmap(os.path.dirname(
            __file__) + '/failed.png').scaledToHeight(160, QtCore.Qt.SmoothTransformation)
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)

        center_layout = QtWidgets.QHBoxLayout(self)
        center_layout.addStretch()
        center_layout.addWidget(logo_label)
        center_layout.addStretch()

        center_widget = QtWidgets.QWidget()
        center_widget.setLayout(center_layout)
        self.layout = QtWidgets.QVBoxLayout(self)
        # True = add stretch vertically
        self.layout.addWidget(center_widget, True)

        # Putting it in initializePage would add another one each time the page is displayed when going back and forth
        self.label = QtWidgets.QLabel()
        self.layout.addWidget(self.label)

    def initializePage(self):
        print("Displaying ErrorPage")
        wizard.playSound()
        self.label.setWordWrap(True)
        self.label.clear()
        self.label.setText(wizard.error_message_nice)
        self.setButtonText(wizard.CancelButton, tr("Quit"))
        wizard.setButtonLayout(
            [QtWidgets.QWizard.Stretch, QtWidgets.QWizard.CancelButton])

#############################################################################
# Pages flow in the wizard
#############################################################################

# TODO: Go straight to error page if we are not able to run
# the installer shell script as root (e.g., using sudo).
# We do not want to run this GUI as root, only the installer shell script.

# TODO: Check prerequisites and inspect /mnt, go straight to error page if needed


if (len(sys.argv) == 2 and os.path.isfile(sys.argv[1])):
    # A file has been supplied on the command line
    filename = sys.argv[1]
    wizard.selected_iso_url = "file://" + filename  # TODO: Error checking
    # FIXME: get file size from the supplied path
    wizard.required_mib_on_disk = int(os.path.getsize(filename) / 1024 / 1024)
    wizard.setWindowTitle(os.path.basename(filename))
else:
    intro_page = IntroPage()
    wizard.addPage(intro_page)
disk_page = DiskPage()
wizard.addPage(disk_page)
installation_page = InstallationPage()
wizard.addPage(installation_page)
success_page = SuccessPage()
wizard.addPage(success_page)

wizard.show()
sys.exit(app.exec_())
