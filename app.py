
import sys, os, argparse, uuid
from OCR import OCR
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QCompleter
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QDateTime
import pyautogui

import mss
import numpy as np
from PIL import Image
import ORM as ORM
import csv

UI_MAIN = 'QtDesigner/Main.ui'
DATA_SHIPS = 'database/ships.csv'
DATA_REGIONS = 'database/regions.csv'
DATA_CONSTELLATIONS = 'database/constellations.csv'
DATA_SOLARSYSTEMS = 'database/solarsystems.csv'
DATA_UNKNOWN_PILOT = 'database/unknown_pilot.csv'

Ui_MainWindow, QtBaseClass = uic.loadUiType(UI_MAIN)

class CursorWorker(QThread):
	cursorSignal = pyqtSignal()

	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		while 1:
			self.cursorSignal.emit()
			self.sleep(1)

class AnalyserWorker(QThread):
	analyserSignal = pyqtSignal(list, float)
	saveSignal = pyqtSignal(str, str)

	def __init__(self, delay, NA_area, SA_area, tesseractPath, currentSystem, jumpSystem):
		QThread.__init__(self)
		self.delay = int(delay)
		self.initShapes(NA_area, SA_area)
		self.ocr = OCR()
		self.ocr.setExecPath(tesseractPath)
		self.old_results = []
		self.currentSystem = currentSystem
		self.jumpSystem = jumpSystem


	def initShapes(self, NA_area, SA_area):
		name_width = NA_area[1] - NA_area[0]
		name_height = NA_area[3] - NA_area[2]
		self.nameShape = {"top": NA_area[2], "left": NA_area[0], "width": name_width, "height": name_height}

		ship_width = SA_area[1] - SA_area[0]
		ship_height = SA_area[3] - SA_area[2]
		self.shipsShape = {"top": SA_area[2], "left": SA_area[0], "width": ship_width, "height": ship_height}

	def __del__(self):
		self.wait()

	def saveJump(self, results, names_img):
		for i, row in enumerate(results):
			if not row in self.old_results:
				shipname = row[0]
				pilotname = row[1]
				self.old_results.append(row)
				self.saveSignal.emit(shipname,pilotname);

		# Remove old pilot
		for p in self.old_results:
			if not p in results:
				self.old_results.remove(p)



	def run(self):
		old_names_img = None
		while 1:
			start_time = QDateTime.currentDateTime()
			#grab ships & names
			with mss.mss() as sct:
				# Part of the screen to capture
				ships_img = np.array(sct.grab(self.shipsShape))
				names_img = np.array(sct.grab(self.nameShape))

			# Make OCR only if we have a changement in the screen
			# using var old_names_img and names_img
			if not np.array_equal(names_img, old_names_img):
				# Find ships
				self.ocr.image = ships_img
				ships, ships_image_f = self.ocr.process()

				# Find names
				self.ocr.image = names_img
				names, names_image_f = self.ocr.process()

				#Save jump
				self.saveJump(list(zip(ships, names)),names_image_f)
				old_names_img = names_img

				time = start_time.msecsTo(QDateTime.currentDateTime())/1000
				self.analyserSignal.emit(list(zip(ships, names)),time)

			self.sleep(self.delay)

class MyApp(QtBaseClass, Ui_MainWindow):
	def __init__(self):
		QtBaseClass.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)

		# init connects
		self.makeConnects()

		# mouse worker
		self.cursorWorker = CursorWorker()
		self.isRunningCursorWorker = False
		self.cursorWorker.cursorSignal.connect(self.setCursorLocation)

		# analyser worker
		self.unknown_pilot = []
		NA_area = (int(self.NA_x1.text()), int(self.NA_x2.text()), int(self.NA_y1.text()), int(self.NA_y2.text()))
		SA_area = (int(self.SA_x1.text()), int(self.SA_x2.text()), int(self.SA_y1.text()), int(self.SA_y2.text()))
		self.analyserWorker = AnalyserWorker(self.AnalyserDelay.text(), NA_area, SA_area, self.tesseract_path.text(), self.currentSystem.text(), self.jumpSystem.text())
		self.isRunningAnalyserWorker = False
		self.analyserWorker.analyserSignal.connect(self.updateResults)
		self.analyserWorker.saveSignal.connect(self.saveJump)

		# Style table view
		self.TableViewResults.setColumnCount(2)
		self.TableViewResults.setHorizontalHeaderLabels(['ship','name'])

		# init database
		ORM.loadShips(DATA_SHIPS)
		ORM.loadRegions(DATA_REGIONS)
		ORM.loadConstellations(DATA_CONSTELLATIONS)
		ORM.loadSolarSystems(DATA_SOLARSYSTEMS)

		# init UI
		self.loadCompleterSolarSystems()

		# Meta data
		self.loadUnknownPilot()


	def makeConnects(self):
		self.BTN_tesseract_browse.clicked.connect(self.bowse_OCR)
		self.BTN_CursorDetection.clicked.connect(self.TurnMouseCursorWorker)
		self.BTN_AnalyserWorker.clicked.connect(self.TurnAnalyserWorker)

	def loadUnknownPilot(self):
		self.unknown_pilot = []
		if os.path.exists(DATA_UNKNOWN_PILOT):
			data = np.genfromtxt(DATA_UNKNOWN_PILOT, delimiter=',')
			self.unknown_pilot = list(map( lambda x : x[0], data))

	def saveUnknownPilot(self):
		data = list(map( lambda x : [x], self.unknown_pilot))
		print (self.unknown_pilot)
		print (data)
		np.savetxt(DATA_UNKNOWN_PILOT, data, delimiter=",")

	def loadCompleterSolarSystems(self):
		solarsystems = list(map(lambda x : x[0], ORM.getSolarSystemsName()))
		completer = QCompleter(solarsystems)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		completer.setMaxVisibleItems(6)
		self.currentSystem.setCompleter(completer)
		self.jumpSystem.setCompleter(completer)

	def bowse_OCR(self):
		#'C:/Program Files/Tesseract-OCR/tesseract'
		self.ocr.setExecPath(self.tesseract_path.text())

	def setCursorLocation(self):
		x, y = pyautogui.position()
		self.CursorX.setText(str(x))
		self.CursorY.setText(str(y))

	def updateResults(self,results, exec_time):
		results = results.copy()

		self.TableViewResults.setRowCount((len(results)))
		self.TableViewResults.setColumnCount(2)

		for i, row in enumerate(results):
			ship = QTableWidgetItem(row[0])
			self.TableViewResults.setItem(i, 0, ship)
			name = QTableWidgetItem(row[1])
			self.TableViewResults.setItem(i, 1, name)

		self.L_execution_time.setText("{}s".format(str(round(exec_time, 2))))

	def saveJump(self, shipname, pilotname):
		err, jump, pilot = ORM.saveJump(shipname, pilotname, system_in=self.currentSystem.text(), system_out=self.jumpSystem.text())
		if err:
			if "No pilot" in err:
				if not pilotname in self.unknown_pilot:
					self.unknown_pilot.append(pilotname)
					print ("Error: unknown pilot: " + pilotname)

	def TurnAnalyserWorker(self):
		# Validate data
		if not ORM.valideSystems(self.currentSystem.text(), self.jumpSystem.text()):
			print("Cant start worker: current or jump solarsystem are not valid")
			return

		#Turn worker
		if not self.isRunningAnalyserWorker:
			self.on_analyser_start()
			self.isRunningAnalyserWorker = True
			self.BTN_AnalyserWorker.setText("Stop")
			self.currentSystem.setEnabled(False)
			self.jumpSystem.setEnabled(False)
			self.NA_x1.setEnabled(False)
			self.NA_x2.setEnabled(False)
			self.NA_y1.setEnabled(False)
			self.NA_y2.setEnabled(False)
			self.SA_x1.setEnabled(False)
			self.SA_x2.setEnabled(False)
			self.SA_y1.setEnabled(False)
			self.SA_y2.setEnabled(False)
			self.tesseract_path.setEnabled(False)
		else:
			self.on_analyser_stop()
			self.isRunningAnalyserWorker = False
			self.BTN_AnalyserWorker.setText("Start")
			self.currentSystem.setEnabled(True)
			self.jumpSystem.setEnabled(True)
			self.NA_x1.setEnabled(True)
			self.NA_x2.setEnabled(True)
			self.NA_y1.setEnabled(True)
			self.NA_y2.setEnabled(True)
			self.SA_x1.setEnabled(True)
			self.SA_x2.setEnabled(True)
			self.SA_y1.setEnabled(True)
			self.SA_y2.setEnabled(True)
			self.tesseract_path.setEnabled(True)

	@pyqtSlot()
	def on_analyser_start(self):
		self.analyserWorker.currentSystem = self.currentSystem.text()
		self.analyserWorker.jumpSystem = self.jumpSystem.text()
		self.analyserWorker.start()
		print('Start analyser worker')

	@pyqtSlot()
	def on_analyser_stop(self):
		self.analyserWorker.terminate()
		print('stop analyser worker')

	def TurnMouseCursorWorker(self):
		if not self.isRunningCursorWorker:
			self.on_cursor_start()
			self.isRunningCursorWorker = True
		else:
			self.on_cursor_stop()
			self.isRunningCursorWorker = False

	@pyqtSlot()
	def on_cursor_start(self):
		self.cursorWorker.start()
		print('Start cursor worker')

	@pyqtSlot()
	def on_cursor_stop(self):
		self.cursorWorker.terminate()
		print('stop cursor worker')


if __name__ == "__main__":
	#ap = argparse.ArgumentParser()
	#ap.add_argument("-i", "--image", required=True, help="path to input image")
	#ap.add_argument("-s", "--show", required=False, help="Boolean for draw result")
	#args = vars(ap.parse_args())
	app = QApplication(sys.argv)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())
