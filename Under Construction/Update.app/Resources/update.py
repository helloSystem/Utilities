#!/usr/bin/env python3

import os, sys, socket, subprocess, time, logging, datetime

# Translate this application using Qt .ts files without the need for compilation
import tstranslator
tstr = tstranslator.TsTranslator(os.path.dirname(__file__) + "/i18n", "")
def tr(input):
    return tstr.tr(input)

from PyQt5 import QtWidgets, QtGui, QtCore


def isRootZfs():
    for part in psutil.disk_partitions():
   		if part.mountpoint == '/':
   			if part.fstype == "zfs":
   			    return True
   			else:
   			    return False
   			    
def internetCheckConnected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    socket.setdefaulttimeout(timeout)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        return True
    except socket.error as ex:
        logging.info(ex)
        return False
    finally:
        # Always do this, even if the try failed
        s.close()

class LiteInstaller(object):

    def __init__(self):

        self.already_fetched_packages = 0
        self.already_extracted_packages = 0
        self.total_packages_to_be_installed = 0
        self.percentage_was_already_downloaded = 0.0
        self.having_downloaded_means_percent = 0.5  # If we had to download all packages, the progress is this much after the download phase
        self.file_symlink_resolved = os.path.join(sys.path[0], os.path.basename(os.path.realpath(sys.argv[0])))
        self.filename = None
        self.packages = None # If None, then we assume that we are in update mode. In this case, instead of installing an application, update the system
        self.showing_final_info = False # Whether we are already showing a final message (in order to show no more than one)

        self.iconfile = None
        for file in os.listdir(os.path.dirname(self.file_symlink_resolved)):
            if file.endswith(".png"):
                self.iconfile = os.path.dirname(self.file_symlink_resolved) + "/" + file
                break

        self.ext_process = QtCore.QProcess()
        # self.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        codec = QtCore.QTextCodec.codecForLocale()
        self.ext_process._decoder_stdout = codec.makeDecoder()
        self.ext_process._decoder_stderr = codec.makeDecoder()
        self.ext_process.readyReadStandardOutput.connect(self._ready_read_standard_output)
        self.ext_process.readyReadStandardError.connect(self._ready_read_standard_error)

        if os.path.isfile(os.path.dirname(self.file_symlink_resolved) + "/packages"):
            results = self.read_file_contents("executable")
            self.filename = os.path.realpath(results[0])
            self.packages = self.read_file_contents("packages")

        if self.filename:
            executable = os.access(self.filename, os.X_OK)
            logging.info(executable)
            if(executable):
                os.execvp(self.filename, sys.argv)
        else:
            app = QtWidgets.QApplication(sys.argv)

            for e in app.findChildren(QtCore.QObject, None, QtCore.Qt.FindChildrenRecursively):
                if hasattr(e, 'text') and hasattr(e, 'setText'):
                    e.setText(tr(e.text()))

            if internetCheckConnected() == False:
                logging.info("Offline?")
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle(" ")
                msg.setText(tr("This requires an active internet connection."))
                msg.exec_()
                sys.exit(0)

            reply = self.show_message()
            logging.info(reply)
            if reply == QtWidgets.QMessageBox.No:
                sys.exit(0)

            if self.packages:
                logging.info("Proceeding to install %s from the %s packages" %(self.filename, self.packages))
            else:
                logging.info("Proceeding to update all packages")
            self.show_install()


    def show_message(self):

        self.msgBox = QtWidgets.QMessageBox()

        if self.packages:
            if self.iconfile:
                self.msgBox.setIconPixmap(QtGui.QPixmap(self.iconfile).scaledToWidth(64, QtCore.Qt.SmoothTransformation))
            self.msgBox.setWindowTitle(" ")
            self.msgBox.setText(tr("%s needs to be downloaded before it can be used.") % os.path.basename(os.path.dirname(self.file_symlink_resolved)).replace(".app", ""))
            self.msgBox.setInformativeText(tr("Do you want to download it now?"))
            # self.msgBox.setDetailedText(tr("The following packages and their dependencies will be installed:\n") + str(self.packages))
            logging.info("The following packages and their dependencies be installed:" + "\n" + str(self.packages))
            self.msgBox.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            self.msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
            return(self.msgBox.exec())
        else:
            if self.iconfile:
                self.msgBox.setIconPixmap(QtGui.QPixmap(self.iconfile).scaledToWidth(64, QtCore.Qt.SmoothTransformation))
            self.msgBox.setWindowTitle(" ")
            self.msgBox.setText(tr("This will update FreeBSD and all installed packages."))
            self.msgBox.setInformativeText(tr("Do you want to update the system now?"))
            yesBtn = self.msgBox.addButton(tr("Update"), QtWidgets.QMessageBox.AcceptRole)
            noBtn = self.msgBox.addButton(tr("Cancel"), QtWidgets.QMessageBox.RejectRole)
            yesBtn.setDefault(True) # Does not make it blue; why? In boot-environments.py it works in a QDialogButtonBox...
            self.msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
            self.msgBox.exec()
            if self.msgBox.clickedButton() != yesBtn:
                exit(0)

    def startInstallProcess(self, command):

        # self.ext_process.setStandardOutputFile(wizard.logfile) # TODO: Append lines to "Details" box

        self.ext_process.finished.connect(self.onProcessFinished)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("CONSOLE", "cat") # Trick to make interactive programs like freebsd-update non-interactive, thanks @grahamperrin
        self.ext_process.setProcessEnvironment(env)
        self.ext_process.setProgram("sudo")
        args = ["-A", "-E"] + command
        self.ext_process.setArguments(args)
        try:
            self.ext_process.start()
            # logging.info(pid) # This is None for non-detached processes. If we ran detached, we would get the pid back here
            logging.info("Process started")
            logging.info(self.ext_process.program())
            logging.info(self.ext_process.arguments())
            # logging.info(self.ext_process.processEnvironment())
        except:  # FIXME: do not use bare 'except'
            self.showFatalError(tr("%s cannot be started.") % command[0])
            return  # Stop doing anything here
        if "pkg" in command:
            # If we are running pkg, we can already update the process percentage
            self.progress.setMaximum(100)
            self.progress.setMinimum(0)
        else:
            # We haven't written the code to update the progress percentage yet, so just set to undetermined
            self.progress.setMaximum(0)
            self.progress.setMinimum(0)

    def _ready_read_standard_output(self):

        text = self.ext_process._decoder_stdout.toUnicode(self.ext_process.readAllStandardOutput())
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if "still holds the lock" in line:
                self.ext_process.kill()
                self.msgBox.hide()
                self.errBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, " ", tr("Another installation is still running. Please try again after it has completed."))
                self.errBox.exec()
                exit(0)
            if line.endswith("...") and line[0].isupper():
                self.msgBox.setText(line)
            if line.startswith("["):
                self.msgBox.setText(tr("Installing..."))
            if line != "." and line.strip() != "":
                logging.info(line)
            if "Updating FreeBSD repository" in line:
                # Now pkg has actually started working
                self.progress.setMaximum(100)
                self.progress.setMinimum(0)
                self.progress.setValue(1)
            if line != ".":
                self.details_textedit.append(line)
            if line.startswith("[") and "/" in line and "]" in line:
                self.total_packages_to_be_installed = int(line.split("[")[1].split("/")[1].split("]")[0].strip())
                logging.info("total_packages_to_be_installed:", self.total_packages_to_be_installed)
            if "Fetching" in line and self.total_packages_to_be_installed:
                 try:
                    # Wrap in a 'try' statement to prevent from division by zero errors            
                    p = (self.already_fetched_packages / self.total_packages_to_be_installed) * self.having_downloaded_means_percent
                    self.progress.setValue(int(round(p*100)))
                    # logging.info(p)
                    self.already_fetched_packages = self.already_fetched_packages + 1 # Increment at the end, because the relevant line is printed when the action starts, not when it finishes
                 except:
                    pass
            if "Extracting" in line:
                if self.already_fetched_packages < self.total_packages_to_be_installed:
                    # Some or all packages had already been downloaded and were re-used from the cache.
                    # This means that the progress bar should not jump to 50% after the downloading phase
                    # but to less than that
                    self.percentage_was_already_downloaded = self.already_fetched_packages / self.total_packages_to_be_installed
                    self.progress_after_downloading = (1 - self.percentage_was_already_downloaded) * self.having_downloaded_means_percent # Where our percentage indicator should be after the download phase: If everything came from the cache, at 0, If nothing came from the cache, at 0.5.
                self.already_fetched_packages = self.total_packages_to_be_installed # Once we are in the Extracting phase, all packages have been fetched (or have come from the cache)
                if self.total_packages_to_be_installed:
                    p = self.having_downloaded_means_percent + (self.already_extracted_packages / self.total_packages_to_be_installed) * (1-self.having_downloaded_means_percent)
                    self.progress.setValue(int(round(p*100)))
                    # logging.info(p)
                self.already_extracted_packages = self.already_extracted_packages + 1 # Increment at the end, because the relevant line is printed when the action starts, not when it finishes
            if "Your packages are up to date" in line:
                self.showFinalInfoMessage(tr("Your system is up to date."))
                # TODO: Offer to restart if FreeBSD updates were installed. We can find this out by running

    # def scroll_to_last_line(self):
    #     cursor = self.textCursor()
    #     cursor.movePosition(QTextCursor.End)
    #     cursor.movePosition(QTextCursor.Up if cursor.atBStart() else
    #                         QTextCursor.StartOfLine)
    #     self.setTextCursor(cursor)

    def _ready_read_standard_error(self):
        text = self.ext_process._decoder_stderr.toUnicode(self.ext_process.readAllStandardError())
        lines = text.split("\n")
        for line in lines:
            logging.error(line)
            self.details_textedit.append(line)
        if text.strip() != "sudo" and text.strip() != ":":
            if self.ext_process.ProcessState == 2:
                # The process is still running. We have an error but we are still alive
                # self.showNonfatalError(text)
                pass
            else:
                if not "/include/" in text and not "No such file" in text:
                    self.showFatalError(text)

    def showNonfatalError(self, text):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(text)
            msg.exec_()

    def showFatalError(self, text):
            self.msgBox.close()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(" ")
            msg.setText(text)
            msg.exec_()
            sys.exit(1)

    def showFinalInfoMessage(self, text):
            if self.showing_final_info == True:
                return
            self.showing_final_info = True
            self.msgBox.close()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle(" ")
            msg.setText(text)
            msg.exec_()
            sys.exit(0)

    def onProcessFinished(self):
        self.progress.setValue(100)
        logging.info("Process finished")
        # cursor = self.output.textCursor()
        # cursor.movePosition(cursor.End)
        # cursor.insertText(str(self.ext_process.readAllStandardOutput()))
        # self.output.ensureCursorVisible()
        exit_code = self.ext_process.exitCode()

        logging.info("Process exit code: %s" % exit_code)
        if exit_code != 0:
            # An error occurred, so we show the last line of output
            all_output_so_far = self.details_textedit.toPlainText()
            text = os.linesep.join([s for s in all_output_so_far.splitlines() if s])
            last_line_of_output = text.splitlines()[-1]
            self.showFatalError(last_line_of_output)
        if exit_code == 0:
            if "bectl" in self.ext_process.arguments():
                self.msgBox.setText(tr("Updating FreeBSD..."))
                self.startInstallProcess(["freebsd-update", "fetch", "install", "--not-running-from-cron"])
            if "freebsd-update" in self.ext_process.arguments():
                # If we were running freebsd-update so far, we are not done yet and need to proceed to updating packages now
                self.msgBox.setText(tr("Updating FreeBSD Packages..."))
                self.startInstallProcess(["pkg", "upgrade", "--yes"])
            if "upgrade" in self.ext_process.arguments():
                self.showFinalInfoMessage(tr("Your system is up to date.")) # TODO: Offer restart if FreeBSD was updated
            if self.packages:
                time.sleep(1)
                executable = os.access(self.filename, os.X_OK)
                if executable == True:
                    # os.execve(self.filename, sys.argv, os.environ) # What sh exec also uses. Leads to issues when files are referenced in relation to the main binary path
                    self.msgBox.close()
                    os.execvp(self.filename, sys.argv)
                    sys.exit(0)
        # Not doing the following because by that time most likely
        # another error message is already on the screen
        # else:
        #     self.showFatalError("An error has occurred.\nCannot proceed.")


    def show_install(self):
        self.msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, " ", (tr("Downloading %s...") % (os.path.basename(self.file_symlink_resolved))), QtWidgets.QMessageBox.NoButton)
        # self.msgBox.setWindowFlags(QtCore.Qt.CustomizeWindowHint) # Needed for the next line
        self.msgBox.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False) # Remove the Close button frim the window decoration; FIXME: Why does this remove the window decorations altogether?
        # self.msgBox.setStyleSheet("QTextEdit{min-width: 500px;}")
        self.msgBox.setStyleSheet("QDialogButtonBox,QTextEdit{min-width: 500px; } QLabel{min-height: 50px;} QProgressBar{min-width: 410px;}") # FIXME: Do this without hardcoding 410px
        self.msgBox.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        # self.msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        self.msgBox.setDetailedText(" ") # Brings it into existence?
        self.details_textedit = self.msgBox.findChild(QtWidgets.QTextEdit)

        if self.details_textedit is not None:
            logging.info("Found QTextEdit for the details")
            self.details_textedit.setFixedSize(self.details_textedit.sizeHint())

        if self.iconfile:
            self.msgBox.setIconPixmap(QtGui.QPixmap(self.iconfile).scaledToWidth(64, QtCore.Qt.SmoothTransformation))

        self.msgBox.layout().setAlignment(QtCore.Qt.AlignTop)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setMinimum(0)
        # self.progress.setValue(0)

        self.progress.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add the progress bar at the bottom (last row + 1) and first column with column span
        # self.msgBox.layout().addWidget(self.progress, self.msgBox.layout().rowCount(), 0, 1, self.msgBox.layout().columnCount(), QtCore.Qt.AlignCenter)
        self.msgBox.layout().addWidget(self.progress, 1, 1, 1, self.msgBox.layout().columnCount(),
                                  QtCore.Qt.AlignCenter)

        self.msgBox.layout().addWidget(QtWidgets.QLabel(), 1, 1, 1, self.msgBox.layout().columnCount(),
                                  QtCore.Qt.AlignCenter)

        if self.packages:
            self.startInstallProcess(["pkg", "install", "-y"] + self.packages)
        else:
            if isRootZfs == True:
                self.msgBox.setText(tr("Creating Boot Environment..."))
                name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                self.startInstallProcess(["bectl", "create", name])
            else:
                self.msgBox.setText(tr("Updating FreeBSD..."))
                self.startInstallProcess(["freebsd-update", "fetch", "install", "--not-running-from-cron"])

        self.msgBox.exec()


    def read_file_contents(self, filename):
        global results
        file = open(os.path.dirname(self.file_symlink_resolved) + "/Resources/" + filename)
        lines = file.read().split("\n")
        file.close()
        results = []
        for line in lines:
            if "#" in line:
                line = line.split("#")[0]
            line = line.strip()
            if " " in line:
                elements = line.split(" ")
                for element in elements:
                    results.append(element)
            else:
                if line != "":
                    results.append(line)
        return results

if __name__ == "__main__":
    # Logging
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                     datefmt='%m-%d %H:%M',
    #                     filename='/var/log/update.log',
    #                     filemode='w')
    # Console handler for logging
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)

    LI = LiteInstaller()
