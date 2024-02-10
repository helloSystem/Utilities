import time

from PyQt5.QtCore import QThread, QThreadPool


class SnapShots(QThread):
    def __init__(self, main_window, fps=25):
        QThread.__init__(self)
        self.fps = fps
        self.main_window = main_window
        self.halt = False
        self.queue = Queue.Queue()

    def run(self, fps=None):
        if fps:
            self.fps = fps
        period = 1.0 / self.fps
        while not self.halt:
            st = time.time()
            while not self.queue.empty():
                pass
            self.queue.put("capture")
            self.emit(SIGNAL("capture()"))
            td = time.time() - st
            wait = period - td
            if wait > 0: time.sleep(wait)
        # empty the queue here (thread safe)
        with self.queue.mutex:
            self.queue.queue.clear()
