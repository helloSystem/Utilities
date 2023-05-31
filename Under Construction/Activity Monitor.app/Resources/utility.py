import psutil

import os
import psutil


def get_process_environ(p):
    p: psutil.Process

    try:
        return p.environ()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return None


def get_process_application_name(p):
    p: psutil.Process

    environ = get_process_environ(p)
    if environ and "LAUNCHED_BUNDLE" in environ:
        return os.path.basename(environ["LAUNCHED_BUNDLE"]).rsplit(".", 1)[0]
    else:
        return p.name()


def bytes2human(n, short=True):
    """
    Forked method from psutil with a better suffix management
    """
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.80 KB'
    # >>> bytes2human(100001221)
    # '95.40 MB'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            return f"{round(float(n) / prefix[s], 2):.2f} {s}B"
    if short:
        return f"{int(n)} B"
    else:
        if n >= 1:
            return f"{int(n)} bytes"
        else:
            return f"{int(n)} byte"

