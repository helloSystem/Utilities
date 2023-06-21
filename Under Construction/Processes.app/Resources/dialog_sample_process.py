import os
import datetime
import socket
import sys
import re

import psutil

from PyQt5.QtCore import Qt, QFileInfo, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
)
from PyQt5.QtWidgets import QWidget
from dialog_sample_process_ui import Ui_SampleProcess

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


class SampleProcess(QWidget, Ui_SampleProcess):
    sample_run_processing = pyqtSignal()
    sample_finish_processing = pyqtSignal()

    def __init__(self, parent=None, process=None):
        super(SampleProcess, self).__init__(parent)
        Ui_SampleProcess.__init__(self)
        self.fileName = None
        self.process = process
        self.setupUi(self)
        self.open_files_model = QStandardItemModel()

        self.setWindowTitle(f"{get_process_application_name(self.process)} ({self.process.pid})")
        self.default_filename = f"{self.windowTitle()}.txt"
        self.buttonClose.clicked.connect(self.quit)
        self.buttonRefresh.clicked.connect(self.run)
        self.comboBox.currentIndexChanged.connect(self.combobox_changed)
        self.sample_run_processing.connect(lambda: self.buttonRefresh.setEnabled(False))
        self.sample_finish_processing.connect(lambda: self.buttonRefresh.setEnabled(True))
        self.buttonSave.clicked.connect(self.save)

        self.sample_text = ""
        self.sample_markdown = ""
        self.count = 0
        self.status_text_template = self.StatusText.text()
        self.run()
        self.comboBox.setCurrentIndex(1)
        self.combobox_changed()


    @staticmethod
    def clean_filename(s):

        # Remove all strange characters (everything except numbers, letters or ".-_()" )
        s = re.sub(r"[^\w\s\.\-\_\(\)]", '_', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '_', s)

        return s

    def save(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File",
            self.clean_filename(self.default_filename),
            "All Files(*);;Text Files(*.txt)",
            options=options
        )
        if fileName:
            with open(fileName, "w") as f:
                f.write(self.sample_text)

    def quit(self):
        self.close()

    def combobox_changed(self):
        if self.comboBox.currentIndex() == 0:
            self.textBrowser.setPlainText(self.sample_text)
            self.textBrowser.setFont(QFont("Monospace"))
            self.textBrowser.setWordWrapMode(False)
        elif self.comboBox.currentIndex() == 1:
            self.textBrowser.setMarkdown(self.sample_markdown)
            self.textBrowser.setFont(QFont("Roboto"))
            self.textBrowser.setWordWrapMode(True)

    def add_to_sample_text(self, a, b):
        if a != "":
            a = f"{a.upper()}:"
        if b is None:
            b = f"{None}"
        self.sample_text += "%s %s\n" % (a, b)

    def add_to_sample_markdown(self, a, b):
        if a != "":
            a = f"{a.title()}"
        if b is None or b == "None":
            b = f"``None``"
        self.sample_markdown += "**%s**: %s\n\n" % (a, b)

    def add_to_sample(self, a, b):
        self.add_to_sample_text(a, b)
        self.add_to_sample_markdown(a, b)

    def str_ntuple(self, nt, convert_bytes=False):
        if nt == ACCESS_DENIED:
            return ""
        if not convert_bytes:
            return ", ".join(["%s=%s" % (x, getattr(nt, x)) for x in nt._fields])
        else:
            return ", ".join(["%s=%s" % (x, bytes2human(getattr(nt, x))) for x in nt._fields])

    def run(self):
        try:
            psutil.Process(self.process.pid).is_running()
        except psutil.NoSuchProcess:
            self.buttonRefresh.setEnabled(False)
            self.StatusText.setText(f"NoSuchProcess")
            return

        self.sample_run_processing.emit()
        self.sample_text = ""
        self.sample_markdown = ""
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
                    parent = "(%s)" % parent.name()
                else:
                    parent = ""
            except psutil.Error:
                parent = ""
            try:
                pinfo["children"] = proc.children()
            except psutil.Error:
                pinfo["children"] = []
            if pinfo["create_time"]:
                started = datetime.datetime.fromtimestamp(pinfo["create_time"]).strftime("%Y-%m-%d %H:%M")
            else:
                started = ACCESS_DENIED

        # here we go
        # Title
        self.sample_markdown += "# %s (%s)\n" % (pinfo["name"], pinfo["pid"])
        self.sample_markdown += "## General\n"

        # PID
        self.add_to_sample("pid", pinfo["pid"])

        # PPID
        self.add_to_sample("parent", "%s %s" % (pinfo["ppid"], parent))

        # PNAME
        self.add_to_sample("name", pinfo["name"])

        # EXE
        self.add_to_sample("exe", pinfo["exe"])

        # CMDLINE
        self.add_to_sample("cmdline", " ".join(pinfo["cmdline"]))

        # CREATE TIME
        self.add_to_sample("started", started)

        # STATUS
        self.add_to_sample("status", pinfo["status"])

        # CWD
        self.add_to_sample("cwd", pinfo["cwd"])

        # USERNAME
        self.add_to_sample("user", pinfo["username"])

        # UIDS
        if psutil.POSIX:
            self.add_to_sample("uids", self.str_ntuple(pinfo["uids"]))

        # GIDS
        if psutil.POSIX:
            self.add_to_sample("gids", self.str_ntuple(pinfo["gids"]))

        # RUN IN A TERMINAL
        if psutil.POSIX:
            self.add_to_sample("terminal", pinfo["terminal"] or None)
        else:
            self.add_to_sample("terminal", None)

        # NICE
        self.add_to_sample("nice", pinfo["nice"])

        # IO NICE
        if hasattr(proc, "ionice"):
            try:
                ionice = proc.ionice()
            except psutil.Error:
                pass
            else:
                if psutil.WINDOWS:
                    self.add_to_sample("ionice", ionice)
                else:
                    self.add_to_sample("ionice", "class=%s, value=%s" % (str(ionice.ioclass), ionice.value))


        # CPUTIME
        cpu_tot_time = datetime.timedelta(seconds=sum(pinfo["cpu_times"]))
        cpu_tot_time = "%s:%s.%s" % (
            cpu_tot_time.seconds // 60 % 60,
            str((cpu_tot_time.seconds % 60)).zfill(2),
            str(cpu_tot_time.microseconds)[:2],
        )
        self.add_to_sample("cpu-tspent", cpu_tot_time)
        self.add_to_sample("cpu-times", self.str_ntuple(pinfo["cpu_times"]))

        # CPU AFFINITY
        if hasattr(proc, "cpu_affinity") and len(pinfo["cpu_affinity"]) > 0:
            self.add_to_sample("cpu-affinity", pinfo["cpu_affinity"])
        else:
            self.add_to_sample("cpu-affinity", "None")

        # CPU NUMBER
        if hasattr(proc, "cpu_num"):
            self.add_to_sample("cpu-num", pinfo["cpu_num"])
        else:
            self.add_to_sample("cpu-num", None)

        # CPU
        self.add_to_sample("cpu %", f"{proc.cpu_percent(interval=1)}")

        # MEMORY FULL INFO
        if hasattr(proc, "memory_full_info") and len(pinfo["memory_full_info"]) > 0:
            self.add_to_sample("memory", self.str_ntuple(pinfo["memory_full_info"], convert_bytes=True))
        else:
            self.add_to_sample("memory", "None")

        # MEMORY PERCENT
        self.add_to_sample("memory %", round(pinfo["memory_percent"], 2))

        # THREADS NUMBER
        self.add_to_sample("num-threads", pinfo["num_threads"])

        #  FILE DESCRIPTOR NUMBER
        if psutil.POSIX:
            self.add_to_sample("num-fds", pinfo["num_fds"])
        else:
            self.add_to_sample("num-fds", "None")

        # HANDLES NUMBER
        if psutil.WINDOWS:
            self.add_to_sample("num-handles", pinfo["num_handles"])
        else:
            self.add_to_sample("num-handles", "None")

        # I/O COUNTERS
        if "io_counters" in pinfo:
            self.add_to_sample("I/O", self.str_ntuple(pinfo["io_counters"], convert_bytes=True))
        else:
            self.add_to_sample("I/O", "None")

        # NUMBER CTX SWITCHRS
        if "num_ctx_switches" in pinfo:
            self.add_to_sample("ctx-switches", self.str_ntuple(pinfo["num_ctx_switches"]))
        else:
            self.add_to_sample("ctx-switches", "None")

        # RLIMIT
        if hasattr(proc, "rlimit"):
            res_names = [x for x in dir(psutil) if x.startswith("RLIMIT")]
            resources = []
            for res_name in res_names:
                try:
                    soft, hard = proc.rlimit(getattr(psutil, res_name))
                except psutil.AccessDenied:
                    pass
                else:
                    resources.append((res_name, soft, hard))
            if resources:
                self.sample_markdown += "## rlimit\n"
                self.sample_markdown += "RLIMIT | SOFT | HARD\n"
                self.sample_markdown += "--- | --- | ---\n"
                template = "%-12s %15s %15s"
                self.add_to_sample_text("res-limits", "")
                self.add_to_sample_text("", template % ("RLIMIT", "SOFT", "HARD"))
                for res_name, soft, hard in resources:
                    if soft == psutil.RLIM_INFINITY:
                        soft = "infinity"
                    if hard == psutil.RLIM_INFINITY:
                        hard = "infinity"
                    self.add_to_sample_text("", template % (RLIMITS_MAP.get(res_name, res_name), soft, hard))
                    self.sample_markdown += f"{RLIMITS_MAP.get(res_name, res_name)} | {soft} | {hard}\n"
                self.sample_markdown += "\n"
        else:
            self.sample_markdown += "## rlimit\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample("rlimit", None)

        # CHILDREN
        if pinfo["children"]:
            template = "%-6s %s"
            self.sample_markdown += "## Children\n"
            self.sample_markdown += "PID | NAME\n"
            self.sample_markdown += "--- | ---\n"

            self.add_to_sample_text("children", "")
            self.add_to_sample_text("", template % ("PID", "NAME"))

            for child in pinfo["children"]:
                try:
                    self.add_to_sample_text("", template % (child.pid, child.name()))
                    self.sample_markdown += f"{child.pid} | {child.name()}\n"
                except psutil.AccessDenied:
                    self.add_to_sample_text("", template % (child.pid, ""))
                    self.sample_markdown += f"{child.pid} |  \n"
                except psutil.NoSuchProcess:
                    pass
            self.sample_markdown += "\n"
        else:
            self.sample_markdown += "## Children\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample_text("children", None)

        # Open Files
        if pinfo["open_files"]:
            self.sample_markdown += "## Open files\n"

            self.add_to_sample_text("open-files", "PATH")
            model = []
            headers = []

            for i, file in enumerate(pinfo["open_files"]):
                row = []
                if hasattr(file, "path"):
                    row.append(f"{file.path}")
                    if "Path" not in headers:
                        headers.append("Path")

                if hasattr(file, "fd"):
                    row.append(f"{file.fd}")
                    if "Fd" not in headers:
                        headers.append("Fd")

                if hasattr(file, "position"):
                    row.append(f"{file.position}")
                    if "Position" not in headers:
                        headers.append("Position")

                if hasattr(file, "mode"):
                    row.append(f"{file.mode}")
                    if "Mode" not in headers:
                        headers.append("Mode")

                if hasattr(file, "flags"):
                    row.append(f"{file.flags}")
                    if "Flags" not in headers:
                        headers.append("Flags")

                if row:
                    model.append(row)

            self.sample_markdown += "PID | NAME\n"
            self.sample_markdown += "--- | ---\n"
            self.sample_markdown += " | ".join(headers)
            self.sample_markdown += " | ".join(["---" for i in headers])
            self.add_to_sample_text("open-files", " ".join(headers))
            for file in model:
                self.add_to_sample_text("", " ".join(file))
                self.sample_markdown += " | ".join(file)
            self.sample_markdown += "\n"

        else:
            self.sample_markdown += "## Open Files\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample_text("open-files", None)

        if pinfo["connections"]:
            self.sample_markdown += "## Connections\n"
            self.sample_markdown += "PROTO | LOCAL ADDR | REMOTE ADDR | STATUS\n"
            self.sample_markdown += "--- | --- | --- | ---\n"
            template = "%-5s %-25s %-25s %s"
            self.add_to_sample_text("connections", "")
            self.add_to_sample_text("", template % ("PROTO", "LOCAL ADDR", "REMOTE ADDR", "STATUS"))
            for conn in pinfo["connections"]:
                if conn.type == socket.SOCK_STREAM:
                    type = "TCP"
                elif conn.type == socket.SOCK_DGRAM:
                    type = "UDP"
                else:
                    type = "UNIX"
                lip, lport = conn.laddr
                if not conn.raddr:
                    rip, rport = "*", "*"
                else:
                    rip, rport = conn.raddr
                self.add_to_sample_text(
                    "", template % (type, "%s:%s" % (lip, lport), "%s:%s" % (rip, rport), conn.status)
                )
                if rip == "*":
                    rip = "\\*"
                if rport == "*":
                    rport = "\\*"
                self.sample_markdown += f"{type} | {lip}:{lport} | {rip}:{rport} | {conn.status}\n"
            self.sample_markdown += "\n"

        else:
            self.sample_markdown += "## Connections\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample_text("connections", None)

        if pinfo["threads"] and len(pinfo["threads"]) > 1:
            self.sample_markdown += "## Threads\n"
            self.sample_markdown += "TID | USER | SYSTEM\n"
            self.sample_markdown += "--- | --- | ---\n"

            template = "%-5s %12s %12s"
            self.add_to_sample_text("threads", template % ("TID", "USER", "SYSTEM"))
            for i, thread in enumerate(pinfo["threads"]):
                self.add_to_sample_text("", template % thread)
                self.sample_markdown += f"{thread.id} | {thread.user_time} | {thread.system_time}\n"
            self.sample_markdown += "\n"
            self.add_to_sample_text("", "total=%s" % len(pinfo["threads"]))
        else:
            self.sample_markdown += "## Threads\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample_text("threads", None)

        # Environment
        if hasattr(proc, "environ") and pinfo["environ"]:
            self.sample_markdown += "## Environment\n"
            self.sample_markdown += "NAME | VALUE\n"
            self.sample_markdown += "--- | ---\n"

            template = "%-25s %s"
            self.add_to_sample_text("environ", "")
            self.add_to_sample_text("", template % ("NAME", "VALUE"))

            for name, value in pinfo["environ"].items():
                self.add_to_sample_text("", template % (name, value))
                self.sample_markdown += f"{name} | {value}\n"
            self.sample_markdown += "\n"
        else:
            self.sample_markdown += "## Environment\n"
            self.sample_markdown += "``None``\n"
            self.add_to_sample_text("environ", None)

        # if pinfo.get('memory_maps', None):
        #     environment_model = QStandardItemModel()
        #     headers = []
        #     for m in proc.memory_maps(grouped=False):
        #         row = []
        #         if hasattr(m, "addr"):
        #             item = QStandardItem()
        #             item.setText(f"{m.addr.split('-')[0].zfill(16)}")
        #             item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        #             row.append(item)
        #             if "Address" not in headers:
        #                 headers.append("Address")
        #
        #         if hasattr(m, "rss"):
        #             item = QStandardItem()
        #             item.setText(bytes2human(m.rss))
        #             item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #             row.append(item)
        #             if "RSS" not in headers:
        #                 headers.append("RSS")
        #
        #         if hasattr(m, "private"):
        #             item = QStandardItem()
        #             item.setText(bytes2human(m.private))
        #             item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #             row.append(item)
        #             if "Private" not in headers:
        #                 headers.append("Private")
        #
        #         if hasattr(m, "perms"):
        #             item = QStandardItem()
        #             item.setText(f"{m.perms}")
        #             item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #             row.append(item)
        #             if "Mode" not in headers:
        #                 headers.append("Mode")
        #
        #         if hasattr(m, "path"):
        #             item = QStandardItem()
        #             item.setText(f"{m.path}")
        #             item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        #             item.setIcon(QFileIconProvider().icon(QFileInfo(m.path)))
        #             # if os.path.exists(m.path):
        #             #     item.setIcon(QFileIconProvider().icon(QFileInfo(m.path)))
        #             # else:
        #             #     item.setIcon(QIcon.fromTheme("system-run"))
        #             row.append(item)
        #             if "Mapping" not in headers:
        #                 headers.append("Mapping")
        #
        #         if row:
        #             environment_model.appendRow(row)
        #     environment_model.setHorizontalHeaderLabels(headers)
        #
        #     self.MapsTreeView.setModel(environment_model)
        #
        #     for header_pos in range(len(self.MapsTreeView.header())):
        #         self.MapsTreeView.resizeColumnToContents(header_pos)
        #
        #     self.MapsTreeView.sortByColumn(0, Qt.DescendingOrder)

        self.count += 1
        self.StatusText.setText(self.status_text_template % (pinfo["pid"], self.count))
        self.comboBox.setCurrentIndex(self.comboBox.currentIndex())
        self.sample_finish_processing.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SampleProcess(process=psutil.Process(os.getpid()))
    win.show()
    sys.exit(app.exec())
