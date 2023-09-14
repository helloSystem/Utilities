#!/usr/bin/env python3


import psutil
import hashlib
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)

from utility import get_process_application_name, get_process_environ


class IconsCacheWorker(QObject):
    finished = pyqtSignal()
    updated_icons_cache = pyqtSignal(object)

    def __init__(self, cache):
        super().__init__()
        self.cache = cache
        # self.icon_empty = QIcon(os.path.join(os.path.dirname(__file__), "Empty.png"))
        self.icon_empty = QIcon.fromTheme("system-run")
        # self.icon_empty = QIcon.fromTheme("application-x-executable")

    def refresh(self):
        for p in psutil.process_iter():


            application_name = get_process_application_name(p)

            if application_name:
                environ = get_process_environ(p)
                icon = None
                # Try BUNDLE first
                if environ and "LAUNCHED_BUNDLE" in environ:
                    # XDG thumbnails for AppImages; TODO: Test this
                    if environ["LAUNCHED_BUNDLE"].endswith(".AppImage"):
                        for icon_suffix in [".png", ".svg", ".svgx"]:
                            xdg_thumbnail_path = os.path.join(
                                os.path.expanduser("~/.cache/thumbnails/normal"),
                                f"{hashlib.md5(environ['LAUNCHED_BUNDLE'].encode('utf-8')).hexdigest()}{icon_suffix}"
                            )
                            if os.path.exists(xdg_thumbnail_path):
                                icon = QIcon(xdg_thumbnail_path)
                                break

                    if icon is None:
                        # AppDir
                        if os.path.exists(os.path.join(
                                environ["LAUNCHED_BUNDLE"],
                                "DirIcon")
                        ):
                            icon = QIcon(os.path.join(
                                environ["LAUNCHED_BUNDLE"],
                                "DirIcon")
                            )
                    # .app
                    if icon is None:
                        for icon_suffix in [".png", ".svg", ".svgx"]:
                            icon_path = os.path.join(
                                environ["LAUNCHED_BUNDLE"],
                                "Resources",
                                f"{application_name}{icon_suffix.lower()}"
                            )
                            if os.path.exists(icon_path):
                                icon = QIcon(icon_path)
                                break

                # Default case back to X11 theme support for get icon
                if icon is None:
                    # The entire icon cache method look to be wrong, then only one method work
                    # Try 1 - Slow, UI Freeze
                    # if QIcon.hasThemeIcon(application_name.lower()):
                    #     icon = QIcon.fromTheme(application_name.lower())
                    # else:
                    #     icon = QIcon(self.icon_empty)

                    # Try 2 - Slow, UI Freeze
                    # icon = QIcon.fromTheme(application_name.lower(), self.icon_empty)

                    # Try 3 - Ultra Slow, big UI Freeze
                    # icon = QIcon.fromTheme(application_name.lower(), self.icon_empty)
                    # if icon.isNull():
                    #     icon = QIcon(self.icon_empty)

                    # Try 4 - Acceptable speed, no UI Freeze
                    icon = QIcon.fromTheme(application_name.lower())

                # Application by application emit a signal it contain data
                if application_name not in self.cache:
                    self.updated_icons_cache.emit(
                        {
                            application_name: icon
                        }
                    )

        self.finished.emit()
