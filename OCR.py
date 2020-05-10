import os, uuid
import cv2
from PIL import Image
import pytesseract
import numpy as np


class OCR():
	def __init__(self):
		self.title = 'APP-Tracker'
		self.exec_path = None
		self.image = None
		self.finalImage = None
		self.isShow = False
		self.text = None
		self.filename = ""

	def setExecPath(self,path):
		pytesseract.pytesseract.tesseract_cmd = path
		print('Set up the tesseract path to ' + path)

	def loadImageFromPIL(self,image):
		self.image = np.array(image.convert('RGB'))
		cv2.imshow("Image", self.image)

	def loadImage(self, path):
		self.image = cv2.imread(path)

	def saveImage(self, filename):
		Image.fromarray(self.finalImage).save('images/_{}_{}.png'.format(uuid.uuid4().hex[:8], filename))

	def process(self):
		# Ajust image
		self.finalImage = cv2.resize(self.image, None, fx=3, fy=3)
		self.finalImage = cv2.cvtColor(self.finalImage, cv2.COLOR_BGR2GRAY)
		#self.finalImage = cv2.medianBlur(self.finalImage, 3)
		self.finalImage = cv2.threshold(self.finalImage, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
	
		#Find text with pytesseract
		# -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_
		script_dir = os.path.dirname(os.path.abspath(__file__))
		self.text = pytesseract.image_to_string(image=Image.fromarray(self.finalImage),
			lang="eng",
			config=" --psm 3 --oem 3 ")

		return list(filter(None, self.toArray())), self.finalImage
		return None, None

	def toArray(self):
		return self.text.split("\n")

	def show(self):
		if self.isShow:
			if self.finalImage is None:
				cv2.imshow("Image", self.image)
			else:
				cv2.imshow("Image", self.finalImage)