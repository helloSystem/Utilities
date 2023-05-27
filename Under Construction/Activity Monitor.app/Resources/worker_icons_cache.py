#!/usr/bin/env python3


import psutil
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal as Signal,
    QObject,
)


class IconsCacheWorker(QObject):
    finished = Signal()

    # Icon Cache
    updated_icons_cache = Signal(object)

    def __init__(self, cache):
        super().__init__()
        self.cache = cache

    def refresh(self):
        none_icon = QIcon(":/None")
        for p in psutil.process_iter():
            if p.name() not in self.cache:
                # Set icon as speed of possible
                self.updated_icons_cache.emit({p.name(): QIcon.fromTheme(p.name().lower())})

                # # Ultra slow code
                # if QIcon.hasThemeIcon(p.name().lower()):
                #     self.updated_icons_cache.emit({p.name(): QIcon.fromTheme(p.name().lower())})
                # else:
                #     self.updated_icons_cache.emit({p.name(): none_icon})

        self.finished.emit()
