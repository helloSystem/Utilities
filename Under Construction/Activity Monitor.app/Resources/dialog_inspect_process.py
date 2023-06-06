import os
import datetime
import socket
import sys
import grp

import psutil

from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileIconProvider,
)
from PyQt5.QtWidgets import QWidget
from dialog_inspect_process_ui import Ui_InspectProcess

from utility import get_process_application_name
from utility import bytes2human

ACCESS_DENIED = ""
NON_VERBOSE_ITERATIONS = 4
RLIMITS_MAP = {
    "RLIMIT_AS": "virtualmem",
    "RLIMIT_CORE": "coredumpsize",
    "RLIMIT_CPU": "cputime",
    "RLIMIT_DATA": "datasize",
    "RLIMIT_FSIZE": "filesize",
    "RLIMIT_MEMLOCK": "memlock",
    "RLIMIT_MSGQUEUE": "msgqueue",
    "RLIMIT_NICE": "nice",
    "RLIMIT_NOFILE": "openfiles",
    "RLIMIT_NPROC": "maxprocesses",
    "RLIMIT_NPTS": "pseudoterms",
    "RLIMIT_RSS": "rss",
    "RLIMIT_RTPRIO": "realtimeprio",
    "RLIMIT_RTTIME": "rtimesched",
    "RLIMIT_SBSIZE": "sockbufsize",
    "RLIMIT_SIGPENDING": "sigspending",
    "RLIMIT_STACK": "stack",
    "RLIMIT_SWAP": "swapuse",
}


class InspectProcess(QWidget, Ui_InspectProcess):
    def __init__(self, parent=None, process=None):
        super(InspectProcess, self).__init__(parent)
        Ui_InspectProcess.__init__(self)
        self.setupUi(self)
        self.process = process
        self.open_files_model = QStandardItemModel()

        self.buttonQuit.clicked.connect(self.quit)

        self.setWindowTitle(f"{get_process_application_name(self.process)} ({self.process.pid})")

        self.sample_text = ""

    def quit(self):
        self.close()

    def add_to_sample_text(self, a, b):
        if a != "":
            a = f"{a.upper()}:"
        self.sample_text += "%-13s %s\n" % (a, b)

    @staticmethod
    def str_named_tuple(nt, convert_bytes=False):
        if nt == ACCESS_DENIED:
            return ""
        if not convert_bytes:
            return ", ".join(["%s=%s" % (x, getattr(nt, x)) for x in nt._fields])
        else:
            return ", ".join(["%s=%s" % (x, bytes2human(getattr(nt, x))) for x in nt._fields])

    def run(self):
        try:
            proc = self.process
            pinfo = proc.as_dict(ad_value=ACCESS_DENIED)
        except psutil.NoSuchProcess as err:
            sys.exit(str(err))

        # collect other proc info
        with proc.oneshot():
            try:
                parent = proc.parent()
                if parent:
                    parent = parent.name()
                else:
                    parent = ""
            except psutil.Error:
                parent = ""

        # Parent
        self.parent_process_value.setText(f"{parent} ({pinfo['ppid']})")

        # User
        self.add_to_sample_text("user", pinfo["username"])
        if psutil.POSIX:
            self.user_value.setText(f"{pinfo['username']} ({pinfo['uids'].effective})")

        # Group
        if psutil.POSIX:
            self.process_group_id_value.setText(
                f"{grp.getgrgid(pinfo['gids'].effective)[0]} ({pinfo['gids'].effective})"
            )

        # CPU Time
        cpu_tot_time = datetime.timedelta(seconds=sum(pinfo["cpu_times"]))
        cpu_tot_time = "%s:%s.%s" % (
            cpu_tot_time.seconds // 60 % 60,
            str((cpu_tot_time.seconds % 60)).zfill(2),
            str(cpu_tot_time.microseconds)[:2],
        )
        self.cpu_time_value.setText(f"{cpu_tot_time}")

        # Memory Info
        if pinfo["memory_full_info"]:
            if hasattr(pinfo["memory_full_info"], "uss"):
                self.unique_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].uss)}")
            else:
                self.unique_set_size_label.hide()
                self.unique_set_size_value.hide()

            if hasattr(pinfo["memory_full_info"], "vms"):
                self.virtual_memory_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].vms)}")
            else:
                self.virtual_memory_size_value.hide()
                self.virtual_memory_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "rss"):
                self.resident_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].rss)}")
            else:
                self.resident_set_size_value.hide()
                self.resident_set_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "shared"):
                self.shared_memory_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].shared)}")
            else:
                self.shared_memory_size_value.hide()
                self.shared_memory_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "text"):
                self.text_resitent_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].text)}")
            else:
                self.text_resitent_set_size_value.hide()
                self.text_resitent_set_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "data"):
                self.data_resident_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].data)}")
            else:
                self.data_resident_set_size_value.hide()
                self.data_resident_set_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "swap"):
                self.swapped_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].swap)}")
            else:
                self.swapped_size_value.hide()
                self.swapped_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "lib"):
                self.shared_libraries_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].lib)}")
            else:
                self.shared_libraries_size_value.hide()
                self.shared_libraries_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "pss"):
                self.proportional_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].pss)}")
            else:
                self.proportional_set_size_value.hide()
                self.proportional_set_size_label.hide()

            if hasattr(pinfo["memory_full_info"], "stack"):
                self.stack_size_value.setText(f"{pinfo['memory_full_info'].stack}")
            else:
                self.stack_size_label.hide()
                self.stack_size_value.hide()

            if hasattr(pinfo["memory_full_info"], "pfaults"):
                self.fault_value.setText(f"{pinfo['memory_full_info'].pfaults}")
            else:
                self.fault.hide()
                self.fault_value.hide()

            if hasattr(pinfo["memory_full_info"], "pageins"):
                self.fault_value.setText(f"{pinfo['memory_full_info'].pageins}")
            else:
                self.pageins.hide()
                self.pageins_value.hide()

        # CPU %
        self.cpu_percent_value.setText(f"{proc.cpu_percent(interval=1)}")

        # Memory %
        self.memory_percent_value.setText(f"{round(pinfo['memory_percent'], 2)}")

        # Status
        self.status_value.setText(f"{pinfo['status']}")

        # Nice
        self.nice_value.setText(f"{pinfo['nice']}")

        # Threads Number
        self.threads_number_value.setText(f"{pinfo['num_threads']}")

        if psutil.POSIX:
            self.file_descriptors_value.setText(f"{pinfo['num_fds']}")
        else:
            self.file_descriptors_value.hide()
            self.file_descriptors.hide()

        if "io_counters" in pinfo:
            if hasattr(pinfo["io_counters"], "read_count"):
                self.read_count_value.setText(f"{pinfo['io_counters'].read_count}")
            else:
                self.read_count.hide()
                self.read_count_value.hide()

            if hasattr(pinfo["io_counters"], "write_count"):
                self.write_count_value.setText(f"{pinfo['io_counters'].write_count}")
            else:
                self.write_count.hide()
                self.write_count_value.hide()

            if hasattr(pinfo["io_counters"], "read_bytes") and pinfo["io_counters"].read_bytes != -1:
                self.read_bytes_value.setText(f"{bytes2human(pinfo['io_counters'].read_bytes)}")
            else:
                self.read_bytes.hide()
                self.read_bytes_value.hide()

            if hasattr(pinfo["io_counters"], "write_bytes") and pinfo["io_counters"].write_bytes != -1:
                self.write_bytes_value.setText(f"{bytes2human(pinfo['io_counters'].write_bytes)}")
            else:
                self.write_bytes.hide()
                self.write_bytes_value.hide()

            if hasattr(pinfo["io_counters"], "read_chars"):
                self.read_chars_value.setText(f"{pinfo['io_counters'].read_chars}")
            else:
                self.read_chars.hide()
                self.read_chars_value.hide()

            if hasattr(pinfo["io_counters"], "write_chars"):
                self.write_chars_value.setText(f"{pinfo['io_counters'].write_chars}")
            else:
                self.write_chars.hide()
                self.write_chars_value.hide()

            if hasattr(pinfo["io_counters"], "other_count"):
                self.other_count_value.setText(f"{pinfo['io_counters'].other_count}")
            else:
                self.other_count.hide()
                self.other_count_value.hide()

            if hasattr(pinfo["io_counters"], "other_bytes"):
                self.other_bytes_value.setText(f"{bytes2human(pinfo['io_counters'].other_bytes)}")
            else:
                self.other_bytes.hide()
                self.other_bytes_value.hide()

        # CTX Switches
        if "num_ctx_switches" in pinfo:
            self.context_switches_value.setText(f"{pinfo['num_ctx_switches'].voluntary}")

        # Open Files
        if pinfo["open_files"]:
            self.add_to_sample_text("open-files", "PATH")
            self.open_files_model = QStandardItemModel()
            headers = []

            for i, file in enumerate(pinfo["open_files"]):
                row = []
                if hasattr(file, "path"):
                    item = QStandardItem(f"{file.path}")
                    item.setData(f"{file.path}", Qt.UserRole)
                    item.setIcon(QFileIconProvider().icon(QFileInfo(file.path)))
                    row.append(item)
                    if "Path" not in headers:
                        headers.append("Path")

                if hasattr(file, "fd"):
                    item = QStandardItem(f"{file.fd}")
                    item.setData(file.fd, Qt.UserRole)
                    row.append(item)
                    if "Fd" not in headers:
                        headers.append("Fd")

                if hasattr(file, "position"):
                    item = QStandardItem(f"{file.position}")
                    item.setData(f"{file.position}", Qt.UserRole)
                    row.append(item)
                    if "Position" not in headers:
                        headers.append("Position")

                if hasattr(file, "mode"):
                    item = QStandardItem(f"{file.mode}")
                    item.setData(file.mode, Qt.UserRole)
                    if f"{file.mode}" == "r" or f"{file.mode}" == "rt":
                        item.setToolTip("<html><head/><body><p>Open for reading text</p></body></html>\n")
                    elif f"{file.mode}" == "r+" or f"{file.mode}" == "r+b":
                        item.setToolTip("<html><head/><body><p>Open the file with no truncation</p></body></html>\n")
                    elif f"{file.mode}" == "w":
                        item.setToolTip(
                            "<html><head/><body><p>Open for writing, truncating the file " "first</p></body></html>\n"
                        )
                    elif f"{file.mode}" == "w+" or f"{file.mode}" == "w+b":
                        item.setToolTip("<html><head/><body><p>Open and truncate the file</p></body></html>\n")
                    elif f"{file.mode}" == "a":
                        item.setToolTip(
                            "<html><head/><body><p>Open for writing, appending to the end of file if it "
                            "exists</p></body></html>\n"
                        )
                    elif f"{file.mode}" == "b":
                        item.setToolTip("<html><head/><body><p>Binary mode</p></body></html>\n")
                    elif f"{file.mode}" == "t":
                        item.setToolTip("<html><head/><body><p>Text mode</p></body></html>\n")
                    elif f"{file.mode}" == "+":
                        item.setToolTip(
                            "<html><head/><body><p>Open for updating (reading and " "writing)</p></body></html>\n"
                        )

                    row.append(item)
                    if "Mode" not in headers:
                        headers.append("Mode")

                if hasattr(file, "flags"):
                    item = QStandardItem(f"{file.flags}")
                    item.setData(f"{file.flags}", Qt.UserRole)
                    row.append(item)
                    if "Flags" not in headers:
                        headers.append("Flags")

                if row:
                    self.open_files_model.appendRow(row)

                self.open_files_model.setHorizontalHeaderLabels(headers)
                self.open_files_model.setSortRole(Qt.UserRole)
                self.OpenFileTreeView.setSortingEnabled(False)
                self.OpenFileTreeView.setModel(self.open_files_model)
                self.OpenFileTreeView.setSortingEnabled(True)

                for header_pos in range(len(self.OpenFileTreeView.header())):
                    self.OpenFileTreeView.resizeColumnToContents(header_pos)
                self.OpenFileTreeView.sortByColumn(0, Qt.AscendingOrder)

        # Connections
        num_ports = 0
        if pinfo["connections"]:
            connections_model = QStandardItemModel()
            for conn in pinfo["connections"]:
                if conn.type == socket.SOCK_STREAM:
                    prototype = "TCP"
                elif conn.type == socket.SOCK_DGRAM:
                    prototype = "UDP"
                else:
                    prototype = "UNIX"
                lip, lport = conn.laddr
                if not conn.raddr:
                    rip, rport = "*", "*"
                else:
                    rip, rport = conn.raddr
                connections_model.appendRow(
                    [
                        QStandardItem(f"{prototype}"),
                        QStandardItem(f"{lip}:{lport}"),
                        QStandardItem(f"{rip}:{rport}"),
                        QStandardItem(f"{conn.status}"),
                    ]
                )
                # Ports Number
                # if conn.status == psutil.CONN_LISTEN:
                num_ports += 1
            self.ports_value.setText(f"{num_ports}")
            connections_model.setHorizontalHeaderLabels(("Protocol", "Local Address", "Remote Address", "Status"))
            self.ConnectionsTreeView.setModel(connections_model)
            for header_pos in range(len(self.ConnectionsTreeView.header())):
                self.ConnectionsTreeView.resizeColumnToContents(header_pos)
            self.ConnectionsTreeView.sortByColumn(0, Qt.AscendingOrder)

        else:
            self.add_to_sample_text("connections", "")
            self.ports_value.setText(f"{num_ports}")

        if pinfo.get("memory_maps", None):
            environment_model = QStandardItemModel()
            headers = []
            for m in proc.memory_maps(grouped=False):
                row = []
                if hasattr(m, "addr"):
                    map_address = f"{m.addr.split('-')[0].zfill(16)}"
                    item = QStandardItem(map_address)
                    item.setData(map_address, Qt.UserRole)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    row.append(item)
                    if "Address" not in headers:
                        headers.append("Address")

                if hasattr(m, "rss"):
                    item = QStandardItem(bytes2human(m.rss))
                    item.setData(m.rss, Qt.UserRole)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)
                    if "RSS" not in headers:
                        headers.append("RSS")

                if hasattr(m, "private"):
                    item = QStandardItem(bytes2human(m.private))
                    item.setData(m.private, Qt.UserRole)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)
                    if "Private" not in headers:
                        headers.append("Private")

                if hasattr(m, "perms"):
                    item = QStandardItem(f"{m.perms}")
                    item.setData(f"{m.perms}", Qt.UserRole)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    row.append(item)
                    if "Mode" not in headers:
                        headers.append("Mode")

                if hasattr(m, "path"):
                    item = QStandardItem(f"{m.path}")
                    item.setData(f"{m.path}", Qt.UserRole)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item.setIcon(QFileIconProvider().icon(QFileInfo(m.path)))
                    row.append(item)
                    if "Mapping" not in headers:
                        headers.append("Mapping")

                if row:
                    environment_model.appendRow(row)

            environment_model.setHorizontalHeaderLabels(headers)
            environment_model.setSortRole(Qt.UserRole)

            self.MapsTreeView.setSortingEnabled(False)
            self.MapsTreeView.setModel(environment_model)
            self.MapsTreeView.setSortingEnabled(True)

            for header_pos in range(len(self.MapsTreeView.header())):
                self.MapsTreeView.resizeColumnToContents(header_pos)

            self.MapsTreeView.sortByColumn(0, Qt.DescendingOrder)

        if hasattr(proc, "environ") and pinfo["environ"]:
            environment_model = QStandardItemModel()
            for name, value in pinfo["environ"].items():
                environment_model.appendRow([QStandardItem(f"{name}"), QStandardItem(f"{value}")])
            environment_model.setHorizontalHeaderLabels(["Name", "Value"])

            self.treeViewEnvironement.setModel(environment_model)

            for header_pos in range(len(self.treeViewEnvironement.header())):
                self.treeViewEnvironement.resizeColumnToContents(header_pos)
            self.treeViewEnvironement.sortByColumn(0, Qt.AscendingOrder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InspectProcess(process=psutil.Process(os.getpid()))
    win.run()
    win.show()
    sys.exit(app.exec())
