#!/usr/bin/env python3

from PyQt5.QtCore import pyqtSignal, QObject, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class IpApiWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(object)
    updated_timezone = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.host = "http://ip-api.com"
        self.path = "line?fields=timezone"
        self.nam = None

    def refresh(self):
        def handleResponse(reply):
            er = reply.error()

            if er == QNetworkReply.NoError:
                try:
                    self.updated_timezone.emit(
                        bytes(reply.readAll()).decode("utf-8").strip("\n")
                    )
                except RuntimeError as er:
                    print("RuntimeError: wrapped C/C++ object of type IpApiWorker has been deleted")

            else:
                self.error.emit(f"<html>"
                                f"<head/>"
                                f"<body>"
                                f"<p>"
                                f"<span style=' font-size:14pt; vertical-align:sub;'>"
                                f"{er} - {reply.errorString()}"
                                f"</span>"
                                f"</p>"
                                f"</body>"
                                f"</html>"
                                )

        req = QNetworkRequest(QUrl(f"{self.host}/{self.path}"))

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(handleResponse)
        self.nam.get(req)

        self.finished.emit()
