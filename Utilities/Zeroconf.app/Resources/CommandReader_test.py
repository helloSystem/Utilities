import unittest
from zeroconf import CommandReader
from PyQt5.QtCore import QObject, QProcess

class TestCommandReader(unittest.TestCase):
    def setUp(self):
        self.lines = []
        self.return_code = None
        self.parent = QObject()

    def test_echo1(self):
        cmd = CommandReader(self.parent, "echo", ["foo"])
        output = []
        cmd.lines.connect(output.append)
        cmd.start()
        cmd.wait()
        self.assertEqual(output, [b"foo\n"])

    def test_echo2(self):
        cmd = CommandReader(self.parent, "echo", ["foo\nbar"])
        output = []
        cmd.lines.connect(output.append)
        cmd.start()
        cmd.wait()
        self.assertEqual(output, [b"foo\n", b"bar\n"])

    def test_echo_sleep1(self):
        cmd = CommandReader(self.parent, "sh", ["-c", "echo foo && sleep 1 && echo bar"])
        output = []
        cmd.lines.connect(output.append)
        cmd.start()
        cmd.wait()
        self.assertEqual(output, [b"foo\n", b"bar\n"])

    def test_echo_sleep_false1(self):
        cmd = CommandReader(self.parent, "sh", ["-c", "echo foo && sleep 1 && echo bar && false"])
        output = []
        cmd.lines.connect(output.append)
        cmd.start()
        cmd.wait()
        self.assertEqual(output, [b"foo\n", b"bar\n"])

    def test_kill1(self):
        cmd = CommandReader(self.parent, "sh", ["-c", "echo foo && sleep 1 && echo bar"])
        def handler(line):
            self.assertEqual(line, b"foo\n")
            cmd.kill()
        cmd.lines.connect(handler)
        cmd.start()
        cmd.wait()
        self.assertEqual(cmd.process.state(), QProcess.ProcessState.NotRunning)

if __name__ == "__main__":
    unittest.main()
