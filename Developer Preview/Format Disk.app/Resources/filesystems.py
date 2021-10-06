class Filesystem(object):
    def __init__(self, device):
        self.__repr__ = "<Filesystem>"
        self.nice_name = "Filesystem"
        self.device = device
        self.volume_label = "Untitled"
        self.type_fbsd = None

    @property
    def modify_command(self):
        if not "p" in self.device:
            return
        parent_device = self.device.split("p")[0]
        partition_number = self.device.split("p")[1]
        return ["/sbin/gpart", "modify", "-i", partition_number, "-t", self.type_fbsd, parent_device.replace("/dev/", "")]

    @property
    def add_command(self):
        if "p" in self.device:
            parent_device = self.device.split("p")[0]
            # partition_number = self.device.split("p")[1]
            # Is the i parameter neeed?
            return ["/sbin/gpart", "add", "-t", self.type_fbsd, parent_device.replace("/dev/", "")]
        else:
            # We are asked to format a whole drive rather than a partition, but let's create a partition nonetheless?
            return ["/sbin/gpart", "add", "-t", self.type_fbsd, self.device.replace("/dev/", "")]

class ufs2(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "FreeBSD (UFS2)"
        self.type_fbsd = "freebsd-ufs"

    @property
    def format_command(self):
        return ["newfs", "-L", self.volume_label, self.device]


class fat32(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "MS-DOS (FAT32)"
        self.type_fbsd = "fat32"

    @property
    def format_command(self):
        return ["newfs_msdos", "-F", "32", "-L", self.volume_label, self.device]


class fat16(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "MS-DOS (FAT16)"
        self.type_fbsd = "fat16"

    @property
    def format_command(self):
        return ["newfs_msdos", "-F", "16", "-L", self.volume_label, self.device]


class ntfs(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "Windows (NTFS)"
        self.type_fbsd = "ntfs"

    @property
    def format_command(self):
        return ["mkntfs", "-f", "-L", self.volume_label, self.device]


class exfat(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "ExFAT"
        self.type_fbsd = "ntfs"  # Sic!

    @property
    def format_command(self):
        return ["mkexfatfs", "-n", self.volume_label, self.device]


class ext2(Filesystem):
    def __init__(self, device):
        super().__init__(device)
        self.nice_name = "Linux (ext2)"
        self.type_fbsd = "linux-data"  # Sic!

    @property
    def format_command(self):
        return ["mkfs.ext2", "-L", self.volume_label, self.device]
