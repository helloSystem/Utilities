#!/usr/bin/env python3

import os, sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QCalendarWidget, QMainWindow, QAction, qApp, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap

class Calendar(QWidget):

	def __init__(self):
		super().__init__()
		self.calendar = QCalendarWidget(self)
		# self.calendar.setGridVisible(True)
		self.calendar.setContentsMargins(0,0,0,0)
		self.calendar.setSelectedDate(QDate(datetime.now().year, datetime.now().month, 1))
		self.calendar.clicked.connect(self.printDateInfo)

	def printDateInfo(self, qDate):
		print('{0}/{1}/{2}'.format(qDate.month(), qDate.day(), qDate.year()))
		print(f'Day Number of the year: {qDate.dayOfYear()}')
		print(f'Day Number of the week: {qDate.dayOfWeek()}')

class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Calendar")
		c = Calendar()
		self.c = c
		self.setCentralWidget(c)
		self._showMenu()
		self.setMinimumSize(255, 225)
		self.resizeEvent = self._resizeEvent

	def _resizeEvent(self, event):
		# change the header format depending on the width of the window
		if(event.size().width() < 350):
			self.c.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
		else:
			self.c.calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
		
		# update calendar geometry
		self.c.calendar.setGeometry(0, 0, event.size().width(), event.size().height())

	def _showMenu(self):
		exitAct = QAction('&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAct)
		aboutAct = QAction('&About', self)
		aboutAct.setStatusTip('About this application')
		aboutAct.triggered.connect(self._showAbout)
		helpMenu = menubar.addMenu('&Help')
		helpMenu.addAction(aboutAct)

	def _showAbout(self):
		print("showDialog")
		msg = QMessageBox()
		msg.setWindowTitle("About")
		msg.setIconPixmap(QPixmap(os.path.dirname(__file__) + "/Resources/Calendar.png"))
		candidates = ["COPYRIGHT", "COPYING", "LICENSE"]
		for candidate in candidates:
			if os.path.exists(os.path.dirname(__file__) + "/" + candidate):
				with open(os.path.dirname(__file__) + "/" + candidate, 'r') as file:
					data = file.read()
				msg.setDetailedText(data)
		msg.setText("<h3>Calendar</h3>")
		msg.setInformativeText(
			"A simple calendar application written in PyQt5<br><br><a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
		msg.exec()

def main():
	app = QApplication(sys.argv)
	w = Window()
	w.show()
	sys.exit(app.exec_())

main()
