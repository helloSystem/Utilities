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
            if p.name() not in self.cache:
                try:
                    if "LAUNCHED_BUNDLE" in p.environ():
                        # Without the path, only the bundle name, without the last suffix
                        bundle_path = p.environ()["LAUNCHED_BUNDLE"]
                        bundle_name = bundle_path.split("/")[-1].split(".")[0]

                        # Get the application bundle icon
                        # AppDir
                        if os.path.exists(bundle_path + "/DirIcon"):
                            icon = QIcon(bundle_path + "/DirIcon")
                            self.updated_icons_cache.emit({p.name(): icon})
                        else:
                            # .app
                            icon_suffixes = ["png", "jpg", "xpg", "svg", "xpm"]
                            for icon_suffix in icon_suffixes:
                                if os.path.exists(bundle_path + "/Resources/" + bundle_name + "." + icon_suffix):
                                    icon = QIcon(bundle_path + "/Resources/" + bundle_name + "." + icon_suffix)
                                    self.updated_icons_cache.emit({p.name(): icon})
                                    break
                        # XDG thumbnails for AppImages; TODO: Test this
                        if bundle_path.endswith(".AppImage"):
                            # xdg_thumbnail_path = os.path.join(xdg.BaseDirectory.xdg_cache_home, "thumbnails", "normal")
                            xdg_thumbnail_path = os.path.expanduser("~/.cache/thumbnails/normal")
                            print(xdg_thumbnail_path)
                            xdg_thumbnail_path = os.path.join(xdg_thumbnail_path,
                                                              hashlib.md5(bundle_path.encode("utf-8")).hexdigest() + ".png")
                            if os.path.exists(xdg_thumbnail_path):
                                icon = QIcon(xdg_thumbnail_path)
                                self.updated_icons_cache.emit({p.name(): icon})
                    else:
                        self.updated_icons_cache.emit({p.name(): QIcon.fromTheme(p.name().lower())})
                except psutil.AccessDenied:
                    self.updated_icons_cache.emit({p.name(): QIcon.fromTheme(p.name().lower())})
        self.finished.emit()
