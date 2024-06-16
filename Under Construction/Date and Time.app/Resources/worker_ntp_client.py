#!/usr/bin/env python3

from datetime import datetime
from socket import gaierror
from PyQt5.QtCore import pyqtSignal, QObject, QDate, QDateTime
from ntplib import NTPClient
from ntplib import NTPException, NTPRolloverException


class NtpClientWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(object)
    updated_datetime = pyqtSignal(object)
    updated_date = pyqtSignal(object)

    def __init__(self, host, version=2, port=123, timeout=5):
        super().__init__()
        self.host = host
        self.version = version
        self.port = port
        self.timeout = timeout

        self.ntp_client = NTPClient()

    def refresh(self):
        try:
            response = self.ntp_client.request(
                host=self.host,
                version=self.version,
                port=self.port,
                timeout=self.timeout
            )

            imported_timestamp = datetime.fromtimestamp(response.tx_time)

            self.updated_date.emit(
                QDate(
                    imported_timestamp.year,
                    imported_timestamp.month,
                    imported_timestamp.day,
                )
            )
            self.updated_datetime.emit(
                QDateTime(
                    imported_timestamp.year,
                    imported_timestamp.month,
                    imported_timestamp.day,
                    imported_timestamp.hour,
                    imported_timestamp.minute,
                    imported_timestamp.second,
                )
            )
            self.error.emit("")
        except (gaierror, NTPException, NTPRolloverException) as error:
            self.error.emit(f"<html>"
                            f"<head/>"
                            f"<body>"
                            f"<p>"
                            f"<span style=' font-size:14pt; vertical-align:sub;'>"
                            f"{str(error)}"
                            f"</span>"
                            f"</p>"
                            f"</body>"
                            f"</html>"
                            )

        self.finished.emit()
