#!/usr/bin/env python3

import sys
import os
import psutil
import socket

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, pyqtSlot, QThreadPool, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from network_utility_ui import Ui_MainWindow

from dialog_about import AboutDialog
from psutil._common import bytes2human


class DialogNetworkUtility(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.netstat_process = None
        self.lookup_process = None
        self.ping_process = None
        self.traceroute_process = None
        self.whois_process = None
        self.finger_process = None
        self.port_scan_process = None

        self.nic_info = None
        self.af_map = {
            socket.AF_INET: "IPv4",
            socket.AF_INET6: "IPv6",
            psutil.AF_LINK: "MAC",
        }

        self.duplex_map = {
            psutil.NIC_DUPLEX_FULL: "Full",
            psutil.NIC_DUPLEX_HALF: "Half",
            psutil.NIC_DUPLEX_UNKNOWN: "Unknown",
        }

        self.setupUi(self)
        # Icon and Pixmap are loaded without qressouces file
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Network Utility.png")))

        self.thread_manager = QThreadPool()
        self.timer = QTimer()
        self.timer.start(3000)

        self.signalsConnect()
        self.info_refresh_info()

    def signalsConnect(self):
        self.timer.timeout.connect(self.info_refresh_info_safely)
        self.info_nic_list_combobox.currentIndexChanged.connect(self.refresh_info)
        self.netstat_button.clicked.connect(self.netstat_start)
        self.lookup_use_server_checkbox.stateChanged.connect(
            self.lookup_use_server_checkbox_has_change
        )
        self.lookup_button.clicked.connect(self.lookup_start)
        self.ping_button.clicked.connect(self.ping_start)
        self.traceroute_button.clicked.connect(self.traceroute_start)
        self.whois_button.clicked.connect(self.whois_start)
        self.finger_button.clicked.connect(self.finger_start)
        self.port_scan_button.clicked.connect(self.port_scan_start)
        self.port_scan_use_port_range_checkbox.stateChanged.connect(
            self.port_scan_use_port_range_checkbox_change
        )

        self.actionViewInfo.triggered.connect(self._show_info)
        self.actionViewNetstat.triggered.connect(self._show_netstat)
        self.actionViewPing.triggered.connect(self._show_ping)
        self.actionViewTraceroute.triggered.connect(self._show_traceroute)
        self.actionViewLookup.triggered.connect(self._show_lookup)
        self.actionViewWhois.triggered.connect(self._show_whois)
        self.actionViewFinger.triggered.connect(self._show_finger)
        self.actionViewPortScan.triggered.connect(self._show_port_scan)

        self.actionShowAbout.triggered.connect(self._showAboutDialog)

    def info_nic_list_combobox_refresh(self):
        index = self.info_nic_list_combobox.currentIndex()
        if index == -1:
            index = 1
        items = []

        for nic_name, data in self.nic_info.items():
            items.append(nic_name)

        if items != [
            self.info_nic_list_combobox.itemText(i)
            for i in range(self.info_nic_list_combobox.count())
        ]:
            self.info_nic_list_combobox.clear()
            self.info_nic_list_combobox.addItems(items)
            self.info_nic_list_combobox.setCurrentIndex(index)

    @pyqtSlot()
    def info_refresh_info(self):
        self.nic_info = {}

        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)

        for nic, addrs in psutil.net_if_addrs().items():
            self.nic_info[nic] = {}

            if nic in stats:
                st = stats[nic]
                self.nic_info[nic]["stats"] = {}
                self.nic_info[nic]["stats"]["speed"] = bytes2human(st.speed)
                self.nic_info[nic]["stats"]["duplex"] = self.duplex_map[st.duplex]
                self.nic_info[nic]["stats"]["mtu"] = st.mtu
                self.nic_info[nic]["stats"]["up"] = st.isup

            if nic in io_counters:
                io = io_counters[nic]
                self.nic_info[nic]["incoming"] = {}
                self.nic_info[nic]["incoming"]["bytes"] = bytes2human(io.bytes_recv)
                self.nic_info[nic]["incoming"]["pkts"] = io.packets_recv
                self.nic_info[nic]["incoming"]["errs"] = io.errin
                self.nic_info[nic]["incoming"]["drops"] = io.dropin
                self.nic_info[nic]["outgoing"] = {}
                self.nic_info[nic]["outgoing"]["bytes"] = bytes2human(io.bytes_sent)
                self.nic_info[nic]["outgoing"]["pkts"] = io.packets_sent
                self.nic_info[nic]["outgoing"]["errs"] = io.errout
                self.nic_info[nic]["outgoing"]["drops"] = io.dropout

            self.nic_info[nic]["addrs"] = ""
            for addr in addrs:
                if self.af_map.get(addr.family, addr.family) == "MAC":
                    self.nic_info[nic]["mac"] = addr.address
                else:
                    self.nic_info[nic]["addrs"] += "%-4s<br>" % self.af_map.get(
                        addr.family, addr.family
                    )
                    self.nic_info[nic]["addrs"] += (
                            "&nbsp;&nbsp;&nbsp;&nbsp;address: %s<br>" % addr.address
                    )

                    if addr.broadcast:
                        self.nic_info[nic]["addrs"] += (
                                "&nbsp;&nbsp;&nbsp;&nbsp;broadcast: %s<br>" % addr.broadcast
                        )
                    if addr.netmask:
                        self.nic_info[nic]["addrs"] += (
                                "&nbsp;&nbsp;&nbsp;&nbsp;netmask: %s<br>" % addr.netmask
                        )
                    if addr.ptp:
                        self.nic_info[nic]["addrs"] += (
                                "&nbsp;&nbsp;&nbsp;&nbsp;p2p: %s<br>" % addr.ptp
                        )

        self.info_nic_list_combobox_refresh()
        self.refresh_info()

    def refresh_info(self):
        selected_nic = self.info_nic_list_combobox.currentText()
        self.info_stats_speed_value.setText(
            f"{self.nic_info[selected_nic]['stats']['speed']}"
        )
        self.info_stats_status_value.setText(
            f"{'Active' if self.nic_info[selected_nic]['stats']['up'] else 'Down'}"
        )
        self.info_stats_mtu_value.setText(
            f"{self.nic_info[selected_nic]['stats']['mtu']}"
        )
        self.info_stats_duplex_value.setText(
            f"{self.nic_info[selected_nic]['stats']['duplex']}"
        )

        self.info_sent_bytes_value.setText(
            f"{self.nic_info[selected_nic]['incoming']['bytes']}"
        )
        self.info_sent_pkts_value.setText(
            f"{self.nic_info[selected_nic]['incoming']['pkts']}"
        )
        self.info_sent_errs_value.setText(
            f"{self.nic_info[selected_nic]['incoming']['errs']}"
        )
        self.info_sent_drops_value.setText(
            f"{self.nic_info[selected_nic]['incoming']['drops']}"
        )
        self.info_recv_bytes_value.setText(
            f"{self.nic_info[selected_nic]['outgoing']['bytes']}"
        )
        self.info_recv_pkts_value.setText(
            f"{self.nic_info[selected_nic]['outgoing']['pkts']}"
        )
        self.info_recv_errs_value.setText(
            f"{self.nic_info[selected_nic]['outgoing']['errs']}"
        )
        self.info_recv_drops_value.setText(
            f"{self.nic_info[selected_nic]['outgoing']['drops']}"
        )

        if "mac" in self.nic_info[selected_nic]:
            self.info_hardware_address_value.setText(
                f"{self.nic_info[selected_nic]['mac']}"
            )
        else:
            self.info_hardware_address_value.setText("None")
        self.info_addrs_value.setText(f"{self.nic_info[selected_nic]['addrs']}")

    @pyqtSlot()
    def info_refresh_info_safely(self):
        self.thread_manager.start(self.info_refresh_info)  # ...since .start() is used!

    # Netstat
    def netstat_start(self):
        if self.which("netstat"):
            if self.netstat_process is None:  # No process running.
                self.netstat_text_browser.setText("")
                self.netstat_button.setText("Stop")
                self.netstat_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.netstat_process.readyReadStandardOutput.connect(
                    self.handle_netstat_stdout
                )
                self.netstat_process.readyReadStandardError.connect(
                    self.handle_netstat_stderr
                )
                self.netstat_process.stateChanged.connect(self.handle_netstat_state)
                self.netstat_process.finished.connect(
                    self.handle_netstat_process_finished
                )  # Clean up once complete.

                arg = []
                if self.netstat_radiobutton_route.isChecked():
                    arg.append("-r")
                elif self.netstat_radiobutton_statistics.isChecked():
                    arg.append("-s")
                elif self.netstat_radiobuttion_listening.isChecked():
                    arg.append("-l")
                elif self.netstat_radiobutton_groups.isChecked():
                    arg.append("-g")

                self.netstat_process.start(
                    "netstat",
                    arg,
                )

            else:
                self.netstat_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.netstat_text_browser.setText("netstat command not found ...")

    def handle_netstat_stderr(self):
        data = self.netstat_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.netstat_text_browser.setText(stderr)

    def handle_netstat_stdout(self):
        data = self.netstat_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.netstat_text_browser.append(stdout)

    def handle_netstat_state(self, state):
        if state == QProcess.Starting:
            self.netstat_text_browser.append("Netstat has started ...\n")
        elif state == QProcess.NormalExit:
            self.netstat_text_browser.append("Netstat has completed ...\n")

    def handle_netstat_process_finished(self):
        self.netstat_process = None
        self.netstat_button.setText("Lookup")

    # Lookup
    def lookup_use_server_checkbox_has_change(self, int):
        if self.lookup_use_server_checkbox.isChecked():
            self.lookup_server_lineedit.setEnabled(True)
        else:
            self.lookup_server_lineedit.setEnabled(False)

    def lookup_start(self):
        if self.which("dig"):
            if self.lookup_process is None:  # No process running.
                self.lookup_text_browser.setText("")
                self.lookup_button.setText("Stop")
                self.lookup_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.lookup_process.readyReadStandardOutput.connect(
                    self.handle_lookup_stdout
                )
                self.lookup_process.readyReadStandardError.connect(
                    self.handle_lookup_stderr
                )
                self.lookup_process.stateChanged.connect(self.handle_lookup_state)
                self.lookup_process.finished.connect(
                    self.handle_lookup_process_finished
                )  # Clean up once complete.

                info = None
                if self.lookup_information_combobox.currentIndex() == 1:
                    info = "ALL"
                elif self.lookup_information_combobox.currentIndex() == 2:
                    info = "A"
                elif self.lookup_information_combobox.currentIndex() == 3:
                    info = "AAAA"
                elif self.lookup_information_combobox.currentIndex() == 4:
                    info = "CNAME"
                elif self.lookup_information_combobox.currentIndex() == 5:
                    info = "MX"
                elif self.lookup_information_combobox.currentIndex() == 6:
                    info = "NS"
                elif self.lookup_information_combobox.currentIndex() == 7:
                    info = "PTR"
                elif self.lookup_information_combobox.currentIndex() == 8:
                    info = "SRV"
                elif self.lookup_information_combobox.currentIndex() == 9:
                    info = "SOA"
                elif self.lookup_information_combobox.currentIndex() == 10:
                    info = "TXT"
                elif self.lookup_information_combobox.currentIndex() == 11:
                    info = "CAA"
                elif self.lookup_information_combobox.currentIndex() == 12:
                    info = "DS"
                elif self.lookup_information_combobox.currentIndex() == 13:
                    info = "DNSKEY"

                arg = []
                if self.lookup_address_lineedit.text():
                    arg.append(self.lookup_address_lineedit.text())
                if info:
                    arg.append(info)
                if (
                        self.lookup_server_lineedit.isEnabled()
                        and self.lookup_server_lineedit.text()
                ):
                    arg.append(f"@{self.lookup_server_lineedit.text()}")

                self.lookup_process.start(
                    "dig",
                    arg,
                )

            else:
                self.lookup_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.lookup_text_browser.setText("dig command not found ...")

    def handle_lookup_stderr(self):
        data = self.lookup_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.lookup_text_browser.setText(stderr)

    def handle_lookup_stdout(self):
        data = self.lookup_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.lookup_text_browser.append(stdout)

    def handle_lookup_state(self, state):
        if state == QProcess.Starting:
            self.lookup_text_browser.append(f"Lookup has started ...")
        elif state == QProcess.NormalExit:
            self.lookup_text_browser.append("Lookup has completed ...\n")

    def handle_lookup_process_finished(self):
        self.lookup_process = None
        self.lookup_button.setText("Lookup")

    # Ping
    def ping_start(self):
        if self.which("ping"):
            if self.ping_process is None:  # No process running.
                self.ping_text_browser.setText("")
                self.ping_button.setText("Stop")
                self.ping_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.ping_process.readyReadStandardOutput.connect(
                    self.handle_ping_stdout
                )
                self.ping_process.readyReadStandardError.connect(
                    self.handle_ping_stderr
                )
                self.ping_process.stateChanged.connect(self.handle_ping_state)
                self.ping_process.finished.connect(
                    self.handle_ping_process_finished
                )  # Clean up once complete.

                if self.ping_ilimited_radionutton.isChecked():
                    self.ping_process.start(
                        "ping",
                        [self.ping_address_lineedit.text()],
                    )
                else:
                    self.ping_process.start(
                        "ping",
                        [
                            "-c",
                            f"{self.ping_number_of_packet_spiner.value()}",
                            self.ping_address_lineedit.text(),
                        ],
                    )
            else:
                self.ping_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.ping_text_browser.setText("ping command not found ...")

    def handle_ping_stderr(self):
        data = self.ping_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.ping_text_browser.setText(stderr)

    def handle_ping_stdout(self):
        data = self.ping_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.ping_text_browser.append(stdout)

    def handle_ping_state(self, state):
        if state == QProcess.Starting:
            self.ping_text_browser.append(f"Ping has started ...\n")
        elif state == QProcess.NormalExit:
            self.ping_text_browser.append("Ping has completed ...\n")

    def handle_ping_process_finished(self):
        self.ping_process = None
        self.ping_button.setText("Ping")

    # Traceroute
    def traceroute_start(self):
        if self.which("traceroute"):
            if self.traceroute_process is None:  # No process running.
                self.traceroute_text_browser.setText("")
                self.traceroute_button.setText("Stop")
                self.traceroute_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.traceroute_process.readyReadStandardOutput.connect(
                    self.handle_traceroute_stdout
                )
                self.traceroute_process.readyReadStandardError.connect(
                    self.handle_traceroute_stderr
                )
                self.traceroute_process.stateChanged.connect(
                    self.handle_traceroute_state
                )
                self.traceroute_process.finished.connect(
                    self.handle_traceroute_process_finished
                )  # Clean up once complete.

                self.traceroute_process.start(
                    "traceroute",
                    [self.traceroute_address_lineedit.text()],
                )

            else:
                self.traceroute_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.traceroute_text_browser.setText("traceroute command not found ...")

    def handle_traceroute_stderr(self):
        data = self.traceroute_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.traceroute_text_browser.setText(
            self.traceroute_text_browser.toPlainText() + stderr
        )

    def handle_traceroute_stdout(self):
        data = self.traceroute_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.traceroute_text_browser.setText(
            self.traceroute_text_browser.toPlainText() + stdout
        )

    def handle_traceroute_state(self, state):
        if state == QProcess.Starting:
            self.traceroute_text_browser.append(f"Traceroute has started ...\n\n")
        elif state == QProcess.NormalExit:
            self.traceroute_text_browser.append("Traceroute has completed ...\n")

    def handle_traceroute_process_finished(self):
        self.traceroute_process = None
        self.traceroute_button.setText("Traceroute")

    # Whois
    def whois_start(self):
        if self.which("whois"):
            if self.whois_process is None:  # No process running.
                self.whois_text_browser.setText("")
                self.whois_button.setText("Stop")
                self.whois_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.whois_process.readyReadStandardOutput.connect(
                    self.handle_whois_stdout
                )
                self.whois_process.readyReadStandardError.connect(
                    self.handle_whois_stderr
                )
                self.whois_process.stateChanged.connect(self.handle_whois_state)
                self.whois_process.finished.connect(
                    self.handle_whois_process_finished
                )  # Clean up once complete.

                if self.whois_combox.currentIndex() == 0:
                    self.whois_process.start(
                        "whois",
                        [self.whois_address_lineedit.text()],
                    )
                elif self.whois_combox.currentIndex() == 1:
                    self.whois_process.start(
                        "whois",
                        ["-I", self.whois_address_lineedit.text()],
                    )

            else:
                self.traceroute_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.whois_text_browser.setText("whois command not found ...")

    def handle_whois_stderr(self):
        data = self.whois_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.whois_text_browser.append(stderr)

    def handle_whois_stdout(self):
        data = self.whois_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.whois_text_browser.append(stdout)

    def handle_whois_state(self, state):
        if state == QProcess.Starting:
            self.whois_text_browser.append(f"Whois has started ...\n")
        elif state == QProcess.NormalExit:
            self.whois_text_browser.append("Whois has completed ...\n")

    def handle_whois_process_finished(self):
        self.whois_process = None
        self.whois_button.setText("Whois")

    # Finger
    def finger_start(self):
        if self.which("finger"):
            if self.finger_process is None:  # No process running.
                self.finger_text_browser.setText("")
                self.finger_button.setText("Stop")
                self.finger_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.finger_process.readyReadStandardOutput.connect(
                    self.handle_finger_stdout
                )
                self.finger_process.readyReadStandardError.connect(
                    self.handle_finger_stderr
                )
                self.finger_process.stateChanged.connect(self.handle_finger_state)
                self.finger_process.finished.connect(
                    self.handle_finger_process_finished
                )  # Clean up once complete.

                if (
                        self.finger_username_lineedit.text()
                        and self.finger_domain_lineedit.text()
                ):
                    self.finger_process.start(
                        "finger",
                        [
                            f"{self.finger_username_lineedit.text()}@{self.finger_domain_lineedit.text()}"
                        ],
                    )
                elif self.finger_username_lineedit.text():
                    self.finger_process.start(
                        "finger",
                        [f"{self.finger_username_lineedit.text()}"],
                    )
                else:
                    self.finger_process.start(
                        "finger",
                    )
            else:
                self.finger_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.finger_text_browser.setText("finger command not found ...")

    def handle_finger_stderr(self):
        data = self.finger_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.finger_text_browser.setText(
            self.finger_text_browser.toPlainText() + stderr
        )

    def handle_finger_stdout(self):
        data = self.finger_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.finger_text_browser.setText(
            self.finger_text_browser.toPlainText() + stdout
        )

    def handle_finger_state(self, state):
        if state == QProcess.Starting:
            self.finger_text_browser.append(f"Finger has started ...\n\n")
        elif state == QProcess.NormalExit:
            self.finger_text_browser.append("Finger has completed ...\n")

    def handle_finger_process_finished(self):
        self.finger_process = None
        self.finger_button.setText("Finger")

    # Port Scan
    def port_scan_start(self):
        if self.which("nmap"):
            if self.port_scan_process is None:  # No process running.
                self.port_scan_text_browser.setText("")
                self.port_scan_button.setText("Stop")
                self.port_scan_process = (
                    QProcess()
                )  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.port_scan_process.readyReadStandardOutput.connect(
                    self.handle_port_scan_stdout
                )
                self.port_scan_process.readyReadStandardError.connect(
                    self.handle_port_scan_stderr
                )
                self.port_scan_process.stateChanged.connect(self.handle_port_scan_state)
                self.port_scan_process.finished.connect(
                    self.handle_port_scan_process_finished
                )  # Clean up once complete.

                arg = []
                if self.port_scan_address_lineedit.text():
                    arg.append(self.port_scan_address_lineedit.text())
                if self.port_scan_use_port_range_checkbox.isChecked():
                    arg.append("-p")
                    arg.append(
                        f"{self.port_scan_port_from.value()}-{self.port_scan_port_to.value()}"
                    )

                self.port_scan_process.start("nmap", arg)
            else:
                self.port_scan_process.finished.emit(0, QProcess.NormalExit)
        else:
            self.port_scan_text_browser.setText("nmap command not found ...")

    def port_scan_use_port_range_checkbox_change(self):
        if self.port_scan_use_port_range_checkbox.isChecked():
            self.port_scan_port_from.setEnabled(True)
            self.port_scan_port_and_label.setEnabled(True)
            self.port_scan_port_to.setEnabled(True)
        else:
            self.port_scan_port_from.setEnabled(False)
            self.port_scan_port_and_label.setEnabled(False)
            self.port_scan_port_to.setEnabled(False)

    def handle_port_scan_stderr(self):
        data = self.port_scan_process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip("\n")
        self.port_scan_text_browser.append(stderr)

    def handle_port_scan_stdout(self):
        data = self.port_scan_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip("\n")
        self.port_scan_text_browser.append(stdout)

    def handle_port_scan_state(self, state):
        if state == QProcess.Starting:
            self.port_scan_text_browser.append(f"Port Scan has started ...\n")
        elif state == QProcess.NormalExit:
            self.port_scan_text_browser.append("Port Scan has completed ...\n")

    def handle_port_scan_process_finished(self):
        self.port_scan_process = None
        self.port_scan_button.setText("Scan")

    @staticmethod
    def which(pgm):
        path = os.getenv("PATH")
        for p in path.split(os.path.pathsep):
            p = os.path.join(p, pgm)
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p

    def _show_info(self):
        self.tabWidget.setCurrentIndex(0)

    def _show_netstat(self):
        self.tabWidget.setCurrentIndex(1)

    def _show_lookup(self):
        self.tabWidget.setCurrentIndex(2)

    def _show_ping(self):
        self.tabWidget.setCurrentIndex(3)

    def _show_traceroute(self):
        self.tabWidget.setCurrentIndex(4)

    def _show_whois(self):
        self.tabWidget.setCurrentIndex(5)

    def _show_finger(self):
        self.tabWidget.setCurrentIndex(6)

    def _show_port_scan(self):
        self.tabWidget.setCurrentIndex(7)

    def _showAboutDialog(self):
        self.AboutDialog = AboutDialog()
        self.AboutDialog.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    network_utility = DialogNetworkUtility()
    network_utility.show()
    sys.exit(app.exec())
