#!/usr/bin/env python3


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
