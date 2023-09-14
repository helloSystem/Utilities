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

from PyQt5.QtCore import QSysInfo, QFile, QTextStream
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QStorageInfo
import os

"""
On FreeBSD, determining the underlying storage device associated with a FUSE filesystem mount is not a straightforward
task using standard command-line utilities.
FUSE filesystems are managed by user-space programs and may not directly map to traditional block devices
like in regular filesystems.
Hence, the mount command does not show the underlying storage device associated with a FUSE filesystem mount.
This class is used to determine the underlying storage device associated with a FUSE filesystem mount using
the /var/log/automount.log file.
It only works if the sysutils/automount port or package is installed and the /var/log/automount.log file exists.
"""

### TODO: Also make it possible to search for a /dev/... device and then find out the mountpoint(s) associated with it
### TODO: Actually use ii in the application

class FileSystemInfo:
    def __init__(self, mountpoint):
        self.filePath = mountpoint
        self.fileInfo = QFile(mountpoint)

    def get_filesystem_info(self):
        fileSystemType = ""
        device = ""
        mountpoint = ""

        # If it is a mountpoint, show the filesystem type
        mountpoints = []
        for storage in QStorageInfo.mountedVolumes():
            mountpoints.append(storage.rootPath())

        if self.filePath in mountpoints:
            info = QStorageInfo(self.filePath)

            fileSystemType = info.fileSystemType()
            device = info.device()
            mountpoint = info.rootPath()
            # print("fileSystemType:", fileSystemType)

            # If it is "fuse", show the actual filesystem type
            if fileSystemType == "fusefs":
                mountpointToBeFound = self.filePath
                if os.path.islink(mountpointToBeFound):
                    mountpointToBeFound = os.path.realpath(mountpointToBeFound)
                print("It is a fuse filesystem, so we need to find out the actual filesystem type")
                if (QSysInfo.kernelType() == "freebsd" and QFile.exists("/var/log/automount.log")):
                    print("It is FreeBSD and /var/log/automount.log exists, so we use it")
                    # FIXME: Is there a better way to do this?
                    output = ""
                    file = QFile("/var/log/automount.log")
                    if file.open(QFile.ReadOnly | QFile.Text):
                        stream = QTextStream(file)
                        while not stream.atEnd():
                            line = stream.readLine()
                            if mountpointToBeFound in line and "mount OK" in line:
                                output = line
                        file.close()
                    # print("output:", output)
                    if output:
                        # Line format is like this:
                        # 2023-28-28 22:14:34 /dev/da0s1: mount OK: 'mount.exfat -o uid=0 -o gid=0 -o umask=002 -o noatime /dev/da0s1 /media/Ventoy'
                        # Parse the line, get the filesystem type, the device and the mountpoint
                        partEnclosedInSingleQuotes = output.split("'")[1]
                        # print("partEnclosedInSingleQuotes:", partEnclosedInSingleQuotes)
                        fileSystemType = partEnclosedInSingleQuotes.split(" ")[0]
                        # Remove "mount."
                        fileSystemType = fileSystemType.replace("mount.", "")
                        # print("fileSystemType:", fileSystemType)
                        # Device is the second last word
                        device = partEnclosedInSingleQuotes.split(" ")[-2]
                        # print("device:", device)
                        # Mountpoint is the last word
                        mountpoint = partEnclosedInSingleQuotes.split(" ")[-1]
                        # print("mountpoint:", mountpoint)
            return fileSystemType, device, mountpoint
        else:
            print("It is not a mountpoint")
            return fileSystemType, device, mountpoint

if __name__ == "__main__":
    app = QApplication([])
    mountpoint = "/media/Ventoy"
    fileSystemInfo = FileSystemInfo(mountpoint)
    fileSystemType, device, mountpoint = fileSystemInfo.get_filesystem_info()
    if device:
        print("fileSystemType:", fileSystemType)
        print("device:", device)
        print("mountpoint:", mountpoint)
