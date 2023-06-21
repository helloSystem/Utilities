# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './dialog_about.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(338, 393)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(0, 0))
        AboutDialog.setWindowTitle("")
        AboutDialog.setModal(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setContentsMargins(13, 13, 13, 13)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.about_logo = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_logo.sizePolicy().hasHeightForWidth())
        self.about_logo.setSizePolicy(sizePolicy)
        self.about_logo.setMinimumSize(QtCore.QSize(96, 96))
        self.about_logo.setMaximumSize(QtCore.QSize(96, 96))
        self.about_logo.setBaseSize(QtCore.QSize(0, 0))
        self.about_logo.setText("")
        self.about_logo.setPixmap(QtGui.QPixmap("./Network Utility.png"))
        self.about_logo.setScaledContents(True)
        self.about_logo.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.about_logo.setObjectName("about_logo")
        self.verticalLayout_2.addWidget(self.about_logo, 0, QtCore.Qt.AlignHCenter)
        self.about_app_name = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_app_name.sizePolicy().hasHeightForWidth())
        self.about_app_name.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.about_app_name.setFont(font)
        self.about_app_name.setWordWrap(False)
        self.about_app_name.setObjectName("about_app_name")
        self.verticalLayout_2.addWidget(self.about_app_name)
        self.about_version = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_version.sizePolicy().hasHeightForWidth())
        self.about_version.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.about_version.setFont(font)
        self.about_version.setWordWrap(True)
        self.about_version.setObjectName("about_version")
        self.verticalLayout_2.addWidget(self.about_version)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.about_text = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_text.sizePolicy().hasHeightForWidth())
        self.about_text.setSizePolicy(sizePolicy)
        self.about_text.setTextFormat(QtCore.Qt.AutoText)
        self.about_text.setWordWrap(True)
        self.about_text.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.about_text.setObjectName("about_text")
        self.verticalLayout_2.addWidget(self.about_text, 0, QtCore.Qt.AlignVCenter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.about_footer = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_footer.sizePolicy().hasHeightForWidth())
        self.about_footer.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setKerning(True)
        self.about_footer.setFont(font)
        self.about_footer.setWordWrap(True)
        self.about_footer.setObjectName("about_footer")
        self.verticalLayout_2.addWidget(self.about_footer, 0, QtCore.Qt.AlignBottom)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        self.about_app_name.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\">Network Utility</p></body></html>"))
        self.about_version.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#3d3846; vertical-align:super;\">Version 0.2rc1 </span></p></body></html>"))
        self.about_text.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\">This project is open souce, contributions are welcomed.<br/></p><p align=\"center\">Visit <a href=\"https://github.com/helloSystem/Utilities/\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/helloSystem/Utilities/</span></a> for more information or to report bug and/or suggest a new feature. </p></body></html>"))
        self.about_footer.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; vertical-align:sub;\">Make with love by: Jérôme ORNECH alias Hierosme<br/>Copyright 2023-2024 helloSystem Team. All right reserved. </span></p></body></html>"))
