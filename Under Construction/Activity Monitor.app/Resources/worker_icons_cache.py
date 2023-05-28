#!/usr/bin/env python3


import psutil
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)


class IconsCacheWorker(QObject):
    finished = pyqtSignal()
    updated_icons_cache = pyqtSignal(object)

    def __init__(self, cache):
        super().__init__()
        self.cache = cache

    def refresh(self):
        for p in psutil.process_iter():
            if p.name() not in self.cache:
                self.updated_icons_cache.emit({p.name(): QIcon.fromTheme(p.name().lower())})
        self.finished.emit()
