import os
import signal
import argparse
import datetime
import socket
import sys

import psutil
from utility_bytes2human import bytes2human

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QActionGroup,
    QLabel,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
    QLineEdit,
    QComboBox,
    QShortcut,
)
from PyQt5.QtWidgets import QDialog
from dialog_inspect_process_ui import Ui_InspectProcess

ACCESS_DENIED = ''
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


class InspectProcess(QDialog):
    def __init__(self, parent=None, process=None):
        super(InspectProcess, self).__init__(parent)
        self.process = process
        self.ui = Ui_InspectProcess()
        self.ui.setupUi(self)

    def cancel_dialog(self):
        self.close()

    def print_(self, a, b):
        if sys.stdout.isatty() and psutil.POSIX:
            fmt = '\x1b[1;32m%-13s\x1b[0m %s' % (a, b)
        else:
            fmt = '%-11s %s' % (a, b)
        print(fmt)

    def str_ntuple(self, nt, convert_bytes=False):
        if nt == ACCESS_DENIED:
            return ""
        if not convert_bytes:
            return ", ".join(["%s=%s" % (x, getattr(nt, x)) for x in nt._fields])
        else:
            return ", ".join(["%s=%s" % (x, bytes2human(getattr(nt, x)))
                              for x in nt._fields])

    def run(self, pid, verbose=False):
        try:
            proc = psutil.Process(pid)
            pinfo = proc.as_dict(ad_value=ACCESS_DENIED)
        except psutil.NoSuchProcess as err:
            sys.exit(str(err))

        # collect other proc info
        with proc.oneshot():
            try:
                parent = proc.parent()
                if parent:
                    parent = '(%s)' % parent.name()
                else:
                    parent = ''
            except psutil.Error:
                parent = ''
            try:
                pinfo['children'] = proc.children()
            except psutil.Error:
                pinfo['children'] = []
            if pinfo['create_time']:
                started = datetime.datetime.fromtimestamp(
                    pinfo['create_time']).strftime('%Y-%m-%d %H:%M')
            else:
                started = ACCESS_DENIED

        # here we go
        # Title
        self.print_('pid', pinfo['pid'])
        self.print_('name', pinfo['name'])
        self.setWindowTitle(f"{pinfo['name']} ({pinfo['pid']})")

        # Parent
        self.print_('parent', '%s %s' % (pinfo['ppid'], parent))
        self.ui.parent_process_value.setText('%s %s' % (pinfo['ppid'], parent))

        self.print_('exe', pinfo['exe'])
        self.print_('cwd', pinfo['cwd'])
        self.print_('cmdline', ' '.join(pinfo['cmdline']))
        self.print_('started', started)

        cpu_tot_time = datetime.timedelta(seconds=sum(pinfo['cpu_times']))
        cpu_tot_time = "%s:%s.%s" % (
            cpu_tot_time.seconds // 60 % 60,
            str((cpu_tot_time.seconds % 60)).zfill(2),
            str(cpu_tot_time.microseconds)[:2])
        self.print_('cpu-tspent', cpu_tot_time)
        self.print_('cpu-times', self.str_ntuple(pinfo['cpu_times']))
        if hasattr(proc, "cpu_affinity"):
            self.print_("cpu-affinity", pinfo["cpu_affinity"])
        if hasattr(proc, "cpu_num"):
            self.print_("cpu-num", pinfo["cpu_num"])

        self.print_('memory', self.str_ntuple(pinfo['memory_full_info'], convert_bytes=True))
        self.print_('memory %', round(pinfo['memory_percent'], 2))
        self.ui.unique_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].uss)}")
        self.ui.virtual_memory_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].vms)}")
        self.ui.resident_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].rss)}")
        self.ui.shared_memory_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].shared)}")
        self.ui.text_resitent_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].text)}")
        self.ui.data_resident_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].data)}")
        self.ui.swapped_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].swap)}")
        self.ui.shared_libraries_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].lib)}")
        self.ui.proportional_set_size_value.setText(f"{bytes2human(pinfo['memory_full_info'].pss)}")
        self.ui.dirty_pages_number_value.setText(f"{pinfo['memory_full_info'].dirty}")

        # User
        self.print_('user', pinfo['username'])
        if psutil.POSIX:
            self.print_('uids', self.str_ntuple(pinfo['uids']))
            self.ui.user_value.setText(f"{pinfo['username']} ({pinfo['uids'].effective})")

        # Group
        if psutil.POSIX:
            self.ui.process_group_id_value.setText(f"{pinfo['gids'].effective}")

        # CPU
        self.ui.cpu_percent_value.setText(f"{proc.cpu_percent(interval=1)}")

        # If run in terminal
        if psutil.POSIX:
            self.print_('terminal', pinfo['terminal'] or '')

        self.print_('status', pinfo['status'])
        self.print_('nice', pinfo['nice'])
        if hasattr(proc, "ionice"):
            try:
                ionice = proc.ionice()
            except psutil.Error:
                pass
            else:
                if psutil.WINDOWS:
                    self.print_("ionice", ionice)
                else:
                    self.print_("ionice", "class=%s, value=%s" % (
                        str(ionice.ioclass), ionice.value))

        self.print_('num-threads', pinfo['num_threads'])
        if psutil.POSIX:
            self.print_('num-fds', pinfo['num_fds'])
        if psutil.WINDOWS:
            self.print_('num-handles', pinfo['num_handles'])

        if 'io_counters' in pinfo:
            self.print_('I/O', self.str_ntuple(pinfo['io_counters'], convert_bytes=True))
        if 'num_ctx_switches' in pinfo:
            self.print_("ctx-switches", self.str_ntuple(pinfo['num_ctx_switches']))
        if pinfo['children']:
            template = "%-6s %s"
            self.print_("children", template % ("PID", "NAME"))
            for child in pinfo['children']:
                try:
                    self.print_('', template % (child.pid, child.name()))
                except psutil.AccessDenied:
                    self.print_('', template % (child.pid, ""))
                except psutil.NoSuchProcess:
                    pass

        if pinfo['open_files']:
            self.print_('open-files', 'PATH')
            for i, file in enumerate(pinfo['open_files']):
                if not verbose and i >= NON_VERBOSE_ITERATIONS:
                    self.print_("", "[...]")
                    break
                self.print_('', file.path)
        else:
            self.print_('open-files', '')

        if pinfo['connections']:
            template = '%-5s %-25s %-25s %s'
            self.print_('connections',
                        template % ('PROTO', 'LOCAL ADDR', 'REMOTE ADDR', 'STATUS'))
            for conn in pinfo['connections']:
                if conn.type == socket.SOCK_STREAM:
                    type = 'TCP'
                elif conn.type == socket.SOCK_DGRAM:
                    type = 'UDP'
                else:
                    type = 'UNIX'
                lip, lport = conn.laddr
                if not conn.raddr:
                    rip, rport = '*', '*'
                else:
                    rip, rport = conn.raddr
                self.print_('', template % (
                    type,
                    "%s:%s" % (lip, lport),
                    "%s:%s" % (rip, rport),
                    conn.status))
        else:
            self.print_('connections', '')

        if pinfo['threads'] and len(pinfo['threads']) > 1:
            template = "%-5s %12s %12s"
            self.print_('threads', template % ("TID", "USER", "SYSTEM"))
            for i, thread in enumerate(pinfo['threads']):
                if not verbose and i >= NON_VERBOSE_ITERATIONS:
                    self.print_("", "[...]")
                    break
                self.print_('', template % thread)
            self.print_('', "total=%s" % len(pinfo['threads']))
        else:
            self.print_('threads', '')

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
                template = "%-12s %15s %15s"
                self.print_("res-limits", template % ("RLIMIT", "SOFT", "HARD"))
                for res_name, soft, hard in resources:
                    if soft == psutil.RLIM_INFINITY:
                        soft = "infinity"
                    if hard == psutil.RLIM_INFINITY:
                        hard = "infinity"
                    self.print_('', template % (
                        RLIMITS_MAP.get(res_name, res_name), soft, hard))

        if hasattr(proc, "environ") and pinfo['environ']:
            template = "%-25s %s"
            self.print_("environ", template % ("NAME", "VALUE"))
            for i, k in enumerate(sorted(pinfo['environ'])):
                if not verbose and i >= NON_VERBOSE_ITERATIONS:
                    self.print_("", "[...]")
                    break
                self.print_("", template % (k, pinfo['environ'][k]))

        if pinfo.get('memory_maps', None):
            template = "%-8s %s"
            self.print_("mem-maps", template % ("RSS", "PATH"))
            maps = sorted(pinfo['memory_maps'], key=lambda x: x.rss, reverse=True)
            for i, region in enumerate(maps):
                if not verbose and i >= NON_VERBOSE_ITERATIONS:
                    self.print_("", "[...]")
                    break
                self.print_("", template % (bytes2human(region.rss), region.path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InspectProcess(process=os.getpid())
    win.run(os.getpid(), verbose=True)
    win.show()
    sys.exit(app.exec())
