#!/usr/bin/env python3


import psutil
import hashlib
import os
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
            icon = None

            try:
                environ = p.environ()
            except psutil.AccessDenied:
                environ = None

            # Try helloSystem app first
            if environ and "LAUNCHED_BUNDLE" in environ:
                application_name = os.path.basename(environ["LAUNCHED_BUNDLE"]).rsplit(".", 1)[0]
                # XDG thumbnails for AppImages; TODO: Test this
                if environ["LAUNCHED_BUNDLE"].endswith(".AppImage"):
                    for icon_suffix in [".png", ".jpg", ".xpg", ".svg", ".xpm"]:
                        xdg_thumbnail_path = os.path.join(
                            os.path.expanduser("~/.cache/thumbnails/normal"),
                            f"{hashlib.md5(environ['LAUNCHED_BUNDLE'].encode('utf-8')).hexdigest()}{icon_suffix}"
                        )
                        if os.path.exists(xdg_thumbnail_path):
                            icon = QIcon(xdg_thumbnail_path)
                            break

                if icon is None:
                    # AppDir
                    if os.path.exists(os.path.join(environ["LAUNCHED_BUNDLE"], "DirIcon")):
                        icon = QIcon(os.path.join(environ["LAUNCHED_BUNDLE"], "DirIcon"))
                # .app
                if icon is None:
                    for icon_suffix in [".png", ".jpg", ".xpg", ".svg", ".xpm"]:
                        icon_path = os.path.join(
                            environ["LAUNCHED_BUNDLE"],
                            "Resources",
                            f"{application_name}{icon_suffix.lower()}"
                        )
                        if os.path.exists(icon_path):
                            icon = QIcon(icon_path)
                            break
            else:
                application_name = p.name()

            # Default case
            if icon is None:
                icon = QIcon.fromTheme(p.name().lower())
            if application_name not in self.cache:
                self.updated_icons_cache.emit({application_name: icon})

        self.finished.emit()
