import re
import subprocess

def call(command, **kw):
    """
    Similar to ``subprocess.Popen`` with the following changes:
    * returns stdout, stderr, and exit code (vs. just the exit code)
    * logs the full contents of stderr and stdout (separately) to the file log
    By default, no terminal output is given, not even the command that is going
    to run.
    Useful when system calls are needed to act on output, and that same output
    shouldn't get displayed on the terminal.
    Optionally, the command can be displayed on the terminal and the log file,
    and log file output can be turned off. This is useful to prevent sensitive
    output going to stderr/stdout and being captured on a log file.
    :param terminal_verbose: Log command output to terminal, defaults to False, and
                             it is forcefully set to True if a return code is non-zero
    :param logfile_verbose: Log stderr/stdout output to log file. Defaults to True
    :param verbose_on_failure: On a non-zero exit status, it will forcefully set logging ON for
                               the terminal. Defaults to True
    """
    executable = command.pop(0)
    command.insert(0, executable)
    terminal_verbose = kw.pop('terminal_verbose', False)
    logfile_verbose = kw.pop('logfile_verbose', True)
    verbose_on_failure = kw.pop('verbose_on_failure', True)
    show_command = kw.pop('show_command', False)
    command_msg = "Running command: %s" % ' '.join(command)
    stdin = kw.pop('stdin', None)
    print(command_msg)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        close_fds=True,
        **kw
    )

    if stdin:
        stdout_stream, stderr_stream = process.communicate(as_bytes(stdin))
    else:
        stdout_stream = process.stdout.read()
        stderr_stream = process.stderr.read()
    returncode = process.wait()
    if not isinstance(stdout_stream, str):
        stdout_stream = stdout_stream.decode('utf-8')
    if not isinstance(stderr_stream, str):
        stderr_stream = stderr_stream.decode('utf-8')
    stdout = stdout_stream.splitlines()
    stderr = stderr_stream.splitlines()

    if returncode != 0:
        if verbose_on_failure:
            terminal_verbose = True
    return stdout, stderr, returncode


def geom_disk_parser(block):
    pairs = block.split(';')
    parsed = {}
    for pair in pairs:
        if 'Providers' in pair:
            continue
        try:
            column, value = pair.split(':')
        except ValueError:
            continue
        # fixup
        column = re.sub("\s+", "", column)
        column= re.sub("^[0-9]+\.", "", column)
        value = value.strip()
        value = re.sub('\([0-9A-Z]+\)', '', value)
        parsed[column.lower()] = value
    return parsed

def get_disk(diskname):
    """
    Captures all available info from geom
    along with interesting metadata like sectors, size, vendor,
    solid/rotational, etc...

    Returns a dictionary, with all the geom fields as keys.
    """

    command = ['/sbin/geom', 'disk', 'list', re.sub('/dev/', '', diskname)]
    out, err, rc = call(command)
    geom_block = ""
    for line in out:
        line.strip()
        geom_block += ";" + line
    disk = geom_disk_parser(geom_block)
    return disk

def get_zpools():
    """
    Captures information about partitions from 'zpool list'.

    Returns a dictionary, with all the 'gpart show' fields as keys.
    """
    command = ['/sbin/zpool', 'list', '-Hp']
    out, err, rc = call(command)
    zpools = []
    for line in out:
        fields = line.split()
        print(fields)
        zp = Zpool(fields[0])
        zp.size = fields[1]
        zp.alloc = fields[2]
        zp.free = fields[3]
        zp.ckpoint = fields[4]
        zp.expandsz = fields[5]
        zp.frag = fields[6]
        zp.cap = fields[7]
        zp.dedup = fields[8]
        zp.health = fields[9]
        zp.altroot = fields[10]
        zpools.append(zp)
    return(zpools)

def get_datasets(zpool):
    command = ['zfs', 'list', '-H', '-o', 'name',  '-r', zpool]
    out, err, rc = call(command)
    return(out)

def get_partitions(diskname):
    """
    Captures information about partitions from 'gpart show'.

    Returns a dictionary, with all the 'gpart show' fields as keys.
    """
    command = ['/sbin/gpart', 'show', '-lp', re.sub('/dev/', '', diskname)]
    out, err, rc = call(command)
    partitions = []
    for line in out:
        line = line.replace("=>", "").replace("- free -", "free")
        line.strip()
        fields = line.split()
        if len(fields) < 2:
            continue
        if fields[2] == "free":
            fields.insert(2, "")
        partition = {}
        logical_starting_block = fields[0]
        partition_size_in_blocks = fields[1]
        name = fields[2]
        if name == "":
            name = None
        partition_type_or_label = fields[3]
        partition_type_or_label = partition_type_or_label.replace("(null)", "Partition")
        human_readable_partition_size = fields[4]
        p = Partition()
        p.name = name
        p.logical_starting_block = logical_starting_block
        p.size_in_blocks = partition_size_in_blocks
        p.type_or_label = partition_type_or_label
        p.human_readable_size = human_readable_partition_size
        partitions.append(p)
    return(partitions)

def get_disks():
    command = ['/sbin/geom', 'disk', 'status', '-s']
    out, err, rc = call(command)
    disks = {}
    for path in out:
        dsk, rest1, rest2 = path.split()
        disk = get_disk(dsk)
        disks['/dev/'+dsk] = disk
    return disks

class Disks(object):

    def __init__(self, path=None):
        self.disks = {}


class Disk(object):

    def __init__(self, path):
        self.abspath = path
        self.path = path
        self.reject_reasons = []
        self.available = True


class Partition(object):

    def __init__(self):
        self.name = None
        self.logical_starting_block = None
        self.size_in_blocks = None
        self.type_or_label = None
        self.human_readable_size = None

    def __repr__(self):
        return("{'name': '%s', 'logical_starting_block': %s, 'size_in_blocks': %s, 'type_or_label': '%s', 'human_readable_size': '%s'}" % (self.name, self.logical_starting_block, self.size_in_blocks, self.type_or_label, self.human_readable_size))

    def get_volume_label(self):
        command = ["fstyp", "-l", "/dev/" + self.name]
        out, err, rc = call(command)
        if rc != 0:
            return self.name
        parts = out[0].split(" ")
        parts.pop(0)
        result = " ".join(parts)
        if result:
            return(result)
        else:
            return self.name

class Zpool(object):

    def __init__(self, name):
        self.name = name
        self.size = None
        self.alloc = None
        self.free = None
        self.ckpoint = None
        self.expandsz = None
        self.frag = None
        self.cap = None
        self.dedup = None
        self.health = None
        self.altroot = None


if __name__ == "__main__":
    ds = get_disks()
    for d in ds:

        di = get_disk(d)
        print(di)
        if int(di.get("mediasize")) >= 6*1024*1024:
          print(di.get("descr"))
