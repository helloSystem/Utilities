# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './dialog_cpu_history.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CPUHistory(object):
    def setupUi(self, CPUHistory):
        CPUHistory.setObjectName("CPUHistory")
        CPUHistory.resize(1047, 701)
        self.horizontalLayout = QtWidgets.QHBoxLayout(CPUHistory)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.CPUHistoryLayout = QtWidgets.QHBoxLayout()
        self.CPUHistoryLayout.setSpacing(0)
        self.CPUHistoryLayout.setObjectName("CPUHistoryLayout")
        self.cpu_history_graph = CPUGraphBar(CPUHistory)
        self.cpu_history_graph.setObjectName("cpu_history_graph")
        self.CPUHistoryLayout.addWidget(self.cpu_history_graph)
        self.horizontalLayout.addLayout(self.CPUHistoryLayout)

        self.retranslateUi(CPUHistory)
        QtCore.QMetaObject.connectSlotsByName(CPUHistory)

    def retranslateUi(self, CPUHistory):
        _translate = QtCore.QCoreApplication.translate
        CPUHistory.setWindowTitle(_translate("CPUHistory", "CPU History"))
from widget_cpugraphbar import CPUGraphBar
