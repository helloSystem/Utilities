#!/usr/bin/env python3.7


# Simple Keyboard Layout switcher for FreeBSD in PyQt5


# Copyright (c) 2020, Simon Peter <probono@puredarwin.org>
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


import os, sys, subprocess, shutil


config_file = os.path.expanduser('~/.config/hello/keyboard.conf')


if __name__ == "__main__":
    
    user = os.getenv("SUDO_USER")
    if user is None:
        print("This program needs to be invoked through 'sudo'.")
        exit(1)

    # Move the configuration file to its system-wide destination
    conf_file_path = "/usr/local/etc/X11/xorg.conf.d/00-keyboard.conf"
    try:
        shutil.move("/tmp/00-keyboard.conf", conf_file_path)
    except:
        print("Could not move the configuration file to its system-wide destination")
        exit(1)

    print("Done saving")
