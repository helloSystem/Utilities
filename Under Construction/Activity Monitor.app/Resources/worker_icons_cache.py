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
            if environ and "LAUNCHED_BUNDLE" in environ:
                application_name = os.path.basename(environ["LAUNCHED_BUNDLE"]).rsplit(".", 1)[0]
                # XDG thumbnails for AppImages; TODO: Test this
                if environ["LAUNCHED_BUNDLE"].endswith(".AppImage"):

                    # print(xdg_thumbnail_path)
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

            if icon is None:
                icon = QIcon.fromTheme(p.name().lower())

            if application_name not in self.cache:
                self.updated_icons_cache.emit({application_name: icon})

                # Get the application bundle icon
                # AppDir
                # os.path.exists(os.path.join(bundle_path, "DirIcon"))
                # if os.path.exists(os.path.join(bundle_path, "DirIcon")):
                #     # self.updated_icons_cache.emit({p.name(): QIcon(os.path.join(bundle_path, "DirIcon"))})
                #     icon = QIcon(os.path.join(bundle_path, "DirIcon"))
                #     self.updated_icons_cache.emit(
                #         {f"{bundle_name}": QIcon(os.path.join(bundle_path, "DirIcon"))}
                #     )
                # else:
                #     # .app
                #     for icon_suffix in [".png", ".jpg", ".xpg", ".svg", ".xpm"]:
                #         icon_path = os.path.join(bundle_path, "Resources", f"{bundle_name}{icon_suffix.lower()}")
                #         print(f"Try: {icon_path}")
                #         if os.path.exists(icon_path):
                #             print(f"Found: {icon_path}")
                #             self.updated_icons_cache.emit(
                #                 {f"{bundle_name}": QIcon(icon_path)}
                #             )
                #             break
                        # XDG thumbnails for AppImages; TODO: Test this
                        # if bundle_path.endswith(".AppImage"):
                        #     # xdg_thumbnail_path = os.path.join(xdg.BaseDirectory.xdg_cache_home, "thumbnails", "normal")
                        #     xdg_thumbnail_path = os.path.expanduser("~/.cache/thumbnails/normal")
                        #     # print(xdg_thumbnail_path)
                        #     xdg_thumbnail_path = os.path.join(
                        #         xdg_thumbnail_path,
                        #         hashlib.md5(bundle_path.encode("utf-8")).hexdigest() + ".png")
                        #     if os.path.exists(xdg_thumbnail_path):
                        #         icon = QIcon(xdg_thumbnail_path)
                        #         self.updated_icons_cache.emit({p.name(): icon})

                    # else:
                    #     self.updated_icons_cache.emit({f"{p.name()}": QIcon.fromTheme(p.name().lower())})
                # except psutil.AccessDenied:
                #     self.updated_icons_cache.emit({f"{p.name()}": QIcon.fromTheme(p.name().lower())})
        self.finished.emit()
