from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal

class W_Main(QWidget):
	def __init__(self, form, window):
		super().__init__()
		self.title = 'EvE trafic analyser'
		self.left = 100
		self.top = 100
		self.width = 320
		self.height = 200
		self.form = Form()
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		windowLayout = QVBoxLayout()
		self.show()