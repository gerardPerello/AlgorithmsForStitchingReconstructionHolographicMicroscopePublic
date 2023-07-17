#  -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIS_2_ui.ui'
#
# Created by: Sergio Moreno
#
# Date modification: 06-11-20

# **** LIBRARIES ADDED ****
from doctest import FAIL_FAST
from fileinput import close, filename
import glob
from PIL import Image
import logging
from matplotlib.pyplot import gray
import argparse

parser = argparse.ArgumentParser(description="Manual to this Script")
parser.add_argument('--display', type=int, default=0)
parser.add_argument('--d', type=int, default=0)
args = parser.parse_args()

if args.display == 0:
	viejo = False
elif args.display == 1:
	viejo = True

displayNum = args.display

package = "JBD013_SPI_Communication"
name = "JBD_013_SPI_display"

if viejo:
	package = "JBD_Control"
	name = "JbdDisplay"

display_nuevo = getattr(__import__(package, fromlist=[name]), name)
ROWS = getattr(__import__(package, fromlist=["ROWS"]), "ROWS")
COLUMNS = getattr(__import__(package, fromlist=["COLUMNS"]), "COLUMNS")
#from JBD_Control import JbdDisplay as display_viejo

import os
from os.path import expanduser
import time
import csv
import threading

NUEVO = False

from skimage import io


import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# UB classes
from Main_Control_ui import *
from CMOS_Window_ui import *
from NIM_Window_ui import *
from TIS_IberopticsCameras import TIS_Chipscope as TIS
from Thread_Cmos import CmosThread as ThreadSI
from TIS_DMM_Properties import TIS_DMM_Sensor as DmmTIS

# ****************************

class MyGraphicsScene(QtWidgets.QGraphicsScene):
	mouse_position = QtCore.pyqtSignal(QtCore.QPointF)
	def __init__(self, *args, **kwargs):
		QGraphicsScene.__init__(self)
		# Debug
		self.debug = True
		

	def mouseReleaseEvent(self, event):
		pos = event.scenePos()
		self.mouse_position.emit(pos)
		if self.debug:
			print('\t[DEBUG]-Mouse release position (X,Y)=', pos)

class MainWindow_CMOS(QtWidgets.QMainWindow, Ui_MainWindow_CMOS):
	def __init__(self, *args, **kwargs):
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)

		# Graphic view Shadow Imaging
		self.scene_cmos_viewer = MyGraphicsScene(self)
		self.CS_CameraView.setScene(self.scene_cmos_viewer)

class MainWindow_NIM(QtWidgets.QMainWindow, Ui_MainWindow_NIM):
	def __init__(self, *args, **kwargs):
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)

		# Graphic view Chipscope
		self.scene_nim_viewer = QtWidgets.QGraphicsScene(self)
		self.CS_View.setScene(self.scene_nim_viewer)

class MainWindow(QtWidgets.QMainWindow, Ui_ChipscopeController):
	
	def __init__(self, *args, **kwargs):
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)
		self.setAcceptDrops(True)

		# Variable Paths
		self.csvFileName = 'Leds_list_5x5.csv'
		self.csvPathSelected = path_config + self.csvFileName
		# Debug
		self.debug = False
		self.output_format_selected = 'tiff'
		# Init Params
		self.init_gain = 16
		self.init_exposure = 1600
		# Leds coordinates
		self.camera_connected = False
		self.ledInicial_X = 0
		self.ledInicial_Y = 0
		# Default filenames
		self.filename_pitch = 'Muestras'
		self.displaySelectedLabel.setText(str(displayNum))
		self.displaySizeLabel.setText(str(ROWS) + 'x' + str(COLUMNS))

		# Sensing area #TODO QUITAR? NO SE SI TIENE QUE VER CON LAS FUNCIONES DE ZOOM.
		self.area_top = 3
		self.area_left = 2
		self.width = 744
		self.height = 480
		self.framerate = 60
		self.xpos_sa = int(self.width/2)
		self.ypos_sa = int(self.height/2)
		self.current_coords = (self.xpos_sa, self.ypos_sa)
		self.sensing_area = 5
		self.enab_zoom = False
		self.zoom = False
		self.lensless_save = False
		self.number_of_items = 0

		# High contrast datalist
		self.hc_frame = []
		self.cam_2 = False
		self.cam_3 = True

		# Display Options
		self.leds_luminance = 255
		self.display_BIAS = 63


		""" Init main GUI parameters """
		self.window_cmos = MainWindow_CMOS(self)
		self.window_nim  = MainWindow_NIM(self)

		"""Open CMOS and NIM windows."""
		self.window_cmos.show()
		self.window_nim.show()

		############ THREAD LENSLESS ############
		# Thread of viewer in raw mode
		self.thread_cmos = ThreadSI(Tis)
		self.thread_cmos.cmos_frame.connect(self.cmos_viewer)

		############ WORK / CSV OPTIONS ############
		self.inputCSVPath.setText(self.csvFileName)
		self.lineEdit_pitch_filename.textChanged.connect(self.update_filename)
		self.checkBEditParam.stateChanged.connect(self.enable_edit_pitch_options)
		self.btnSaveCSV.clicked.connect(self.save_csv_file)
		self.btnBrowseCSVpath.clicked.connect(self.browse_csv_file)
		self.btnBrowseSavePath.clicked.connect(self.browse_output_path)
		self.inputCSVPath.textChanged.connect(self.update_csv_filename)
		#### OPEN STITCHER PROGRAM #####
		self.pushButtonOpenStitcher.clicked.connect(self.open_stitcher_program)

		############ Header ############
		self.comboBox_resolution.currentIndexChanged.connect(DmmProp.updateResolution)
		self.comboBox_framerate.currentTextChanged.connect(DmmProp.updateFramerate)
		self.pushButton_reset.clicked.connect(self.reset_scene)
		self.pushButton_camera_connect.clicked.connect(self.connect_camera)

		############ Camera settings ############
		self.checkBox_auto_gain.stateChanged.connect(DmmProp.enableGainAutomatic)
		self.checkBox_auto_exposure.stateChanged.connect(DmmProp.enableExposureAutomatic)
		self.spinBox_gain.valueChanged.connect(DmmProp.updateGain)
		self.spinBox_exposure.valueChanged.connect(DmmProp.updateExposure)
		self.comboBox_format.currentIndexChanged.connect(self.change_camera_format)

		
		# Snapshot and Save frames
		self.pushButton_snap.clicked.connect(self.snap_image)
		
		########## DISPLAY SETTING AND CONNECTION ############
		# Leds intensity
		self.spinBox_leds_intensity.valueChanged.connect(self.set_led_intensity)
		self.spinBox_display_corriente.valueChanged.connect(self.set_display_corriente)
		self.saveDisplayConfigBtn.clicked.connect(self.saveDisplayOptions)
		self.shutDownDisplayBtn.clicked.connect(self.shutDownDisplay)
		self.connectDisplayBtn.clicked.connect(self.connectDisplay)
		self.btnRestartDisplay.clicked.connect(self.RestartDisplay)
		
		######################################################

		# OUTPUT SETTINGS
		self.comboBox_output_file_format.currentIndexChanged.connect(self.change_output_format)
		
		
		# Scan region limits
		self.spinBox_X_inicial_led.valueChanged.connect(self.update_ledInicial_X)
		self.spinBox_Y_inicial_led.valueChanged.connect(self.update_ledInicial_Y)
		
		############ Dynamic acquisition settings ############
		self.pushButton_turn_on_led0.clicked.connect(self.turn_on_led0)
		
		############ Start/Stop acquisition ############
		self.pushButton_start.clicked.connect(self.start_acquisition)
		self.pushButton_stop.clicked.connect(self.send_stop)


		# Generate item for CMOS frames
		self.item_frame_cmos_viewer = QtWidgets.QGraphicsPixmapItem()
		self.window_cmos.scene_cmos_viewer.addItem(self.item_frame_cmos_viewer)
		self.window_cmos.scene_cmos_viewer.setFocusItem(self.item_frame_cmos_viewer)

		self.item_frame_nim_viewer = QtWidgets.QGraphicsPixmapItem()
		self.window_nim.scene_nim_viewer.addItem(self.item_frame_nim_viewer)
		self.window_nim.scene_nim_viewer.setFocusItem(self.item_frame_nim_viewer)

		self.eventStopThread = threading.Event()
		self.updateNimEvent = threading.Event()
		self.lock = threading.Lock()
	
	def set_led_intensity(self, new_value):
		self.leds_luminance = new_value


	def set_display_corriente(self, new_value):
		self.display_BIAS = new_value

	def saveDisplayOptions(self):
		display.saveOptions(self.leds_luminance, self.display_BIAS)
		
	def setStatusBar(self, text):
		self.statusLabel.setText(text)
		logging.info(text)
		app.processEvents()

	def setStatusWorking(self, b):
		if b:
			self.progressBar.setRange(0,0)
		else:
			self.progressBar.setRange(0,100)
		app.processEvents()
	
	#Reseteo del display
	def RestartDisplay(self):
		display.restart()

	#Apaga el display
	def shutDownDisplay(self):
		display.turn_off()

	#Enciende el display
	def connectDisplay(self):
		display.turn_on()

	def open_stitcher_program(self):
		os.popen("/bin/python3 " + stitcher_path)
		self.refreshCMOS()

	########################################
	# Filenames
	########################################

	#Hace el update del nombre de la carpeta donde se guardaran las imagenes de salida.
	def update_filename(self, new_text):
		self.filename_pitch = new_text

	#Hace el update del nombre del fichero CSV.
	def update_csv_filename(self, new_text):
		self.csvFileName = new_text
		self.csvPathSelected = path_config + self.csvFileName
		
	########################################
	#CSV FILE OPTIONS
	########################################
	#Enable change the pitch options, by default they are not enabled.
	def enable_edit_pitch_options(self,state):

		self.spinBox_saltoX.setEnabled(state == 2)
		self.spinBox_saltoY.setEnabled(state == 2)
		self.spinBox_n_leds_X.setEnabled(state == 2)
		self.spinBox_n_leds_Y.setEnabled(state == 2)


	#Guarda la configuracion en un archivo CSV
	def save_csv_file(self):
		#Creamos los datos a guardar,primero el header y luego la data.
		header = ['initx', 'inity', 'pitchx', 'pitchy', 'jumpsx', 'jumpsy']

		data = [str(self.ledInicial_X),str(self.ledInicial_Y),str(self.spinBox_saltoX.value()),
				str(self.spinBox_saltoY.value()),str(self.spinBox_n_leds_X.value()),
				str(self.spinBox_n_leds_Y.value())]

		#En caso de que el nombre de archivo sea nulo, no podemos hacer nada.
		if(self.csvFileName != ""):
			#Si no lo es, usamos QFileINfo para comprobar que existe o no.
			info = QFileInfo(self.csvPathSelected)
			if(info.exists()):
				#Si existe, preguntamos si se quiere sobreescribir.
				reply = QtWidgets.QMessageBox.question(
				self, 'Message', "El archivo ya existe, quieres substituirlo?.",
				QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
				QtWidgets.QMessageBox.No,
				)
				if(reply == QtWidgets.QMessageBox.Yes):
					#En caso afirmativo, lo hacemos.
					with open(info.absoluteFilePath(),"w") as file:
						csvwriter = csv.writer(file)
						csvwriter.writerow(header)
						csvwriter.writerow(data)
						close
					self.checkBEditParam.setChecked(0)
			else:
				#S no existe, lo creamos.
				with open(info.absoluteFilePath(),"x") as file:

					csvwriter = csv.writer(file)
					csvwriter.writerow(header)
					csvwriter.writerow(data)
					close
				self.checkBEditParam.setChecked(0)

	#Carga la configuracion de un CSV.
	def browse_csv_file(self):
		#Dialog for getting the file
		filediag = QFileDialog.getOpenFileName(self, "Open a file", path_config, "*.csv")
		if(filediag[0] != ""):
			info = QFileInfo(filediag[0])
			#Changing our variables with the new file
			self.inputCSVPath.setText(info.fileName())
			#Opening the file with csvRader
			filecsv = open(info.absoluteFilePath())
			csvreader = csv.reader(filecsv)
			#Getting the variables
			header = next(csvreader)
			data = next(csvreader)
			#Changing the variables
			if((header) == ['initx', 'inity', 'pitchx', 'pitchy', 'jumpsx', 'jumpsy']):
				self.spinBox_X_inicial_led.setValue(int(data[0]))
				self.spinBox_Y_inicial_led.setValue(int(data[1]))
				self.spinBox_saltoX.setValue(int(data[2]))
				self.spinBox_saltoY.setValue(int(data[3]))
				self.spinBox_n_leds_X.setValue(int(data[4]))
				self.spinBox_n_leds_Y.setValue(int(data[5]))
				self.checkBEditParam.setChecked(0)
			else:
				reply = QtWidgets.QMessageBox.information(
					self, 'Message', "El formato del CSV es incorrecto.",
					QtWidgets.QMessageBox.OK
					)

			filecsv.close()


	#Selecciona una carpeta para el output
	def browse_output_path(self):
		filediag = QFileDialog.getExistingDirectory(self, 'Select Folder', directory=directory_output_muestras)
		if filediag and filediag[:len(directory_output_muestras)] == directory_output_muestras:
			self.lineEdit_pitch_filename.setText(filediag[len(directory_output_muestras)+1:])
		else:
			reply = QtWidgets.QMessageBox.information(
					self, 'Message', "Solo puede seleccionar carpetas dentro de .../HistorialSets/diadehoy.",
					QtWidgets.QMessageBox.OK
					)

	
	
	########################################
	# Launch/Stop Camera Streaming
	########################################
	def recorrido(self,pixels, brillos=None, fun=lambda pix, val: time.sleep(0.5)):

		if brillos is None:
			brillos = [15 for _ in pixels]#TODO

		display.turn_on()
		cont = 0
		for pix, val in zip(pixels, brillos):
			if not self.eventStopThread.is_set():
				display.turn_on_led(int(pix[0]), int(pix[1]))
				fun(pix,cont,val)
				cont += 1
				display.turn_off_led(int(pix[0]), int(pix[1]))
			else:
				break

		display.turn_off()

		if self.eventStopThread.is_set():
			self.setStatusBar("Capture has been Stopped.")
		else:
			self.setStatusBar('Capture done!')


	def grid(self, pix_start, stride, num_pix, brillo, fun, orientation=0):

		rc = np.array([ROWS, COLUMNS])

		temp = np.floor_divide(rc - pix_start - 1, stride) + 1
		if  ( temp[0] < num_pix[0] ):
			num_pix[0] = temp[0]
			self.spinBox_n_leds_X.setValue(num_pix[0])
			self.setStatusBar("El NX y el NY han cambiado a " + str(num_pix) + "por las dimensiones del display.")
	
		if  ( temp[1] < num_pix[1] ):
			num_pix[1] = temp[1]
			self.spinBox_n_leds_Y.setValue(num_pix[1])
			self.setStatusBar("El NX y el NY han cambiado a " + str(num_pix) + "por las dimensiones del display.")

		self.nx = num_pix[0]
		self.ny = num_pix[1]



		
		brillos = [brillo for _ in range(num_pix[1]) for _ in range(num_pix[0])]
		pixels = [pix_start + np.array([i, j]) * stride for j in range(num_pix[1]) for i in range(num_pix[0])]

		self.recorrido(pixels, brillos, fun)
		self.updateNimEvent.set()


	def start_acquisition(self):

			""" Launch the acquisition algorithm depending on selected mode. """
			if self.camera_connected:
				
				self.setStatusBar('Acquisition Started...')
				self.setStatusWorking(True)

				#En cas de que tinguem algun pixel ences, el tanquem.
				if self.pushButton_turn_on_led0.isChecked():
					self.turn_on_led0()

				
				self.eventStopThread.clear()
				self.updateNimEvent.clear()
				self.window_nim.scene_nim_viewer.setSceneRect(
				0,
				0,
				0,
				0,
				)
				self.images_capture = []
				self.thread_capture = threading.Thread(target=self.grid, args=[
					np.array([self.ledInicial_X, self.ledInicial_Y]),
					np.array([self.spinBox_saltoX.value(), self.spinBox_saltoY.value()]),
					np.array([self.spinBox_n_leds_X.value(), self.spinBox_n_leds_Y.value()]),15,self.snap]
				)
				self.thread_capture.start()
				
				while not self.updateNimEvent.is_set():
					if self.images_capture:
							self.lock.acquire()
							mosaic = self.visNim(self.images_capture, self.nx, 0.1)
							self.lock.release()
							self.frame_transform(mosaic)
							app.processEvents()
							
				
				self.setStatusWorking(False)

				

	#Actualitza el CMOS viewer.
	def refreshCMOS(self):
		app.processEvents()
		
	


	def snap(self,coordPix,indexPicture,_):
		
		time.sleep(0.3)
		#Extraiem la imatge de la camara.
		frame_1d, gray_array = Tis.cameraFrame(
					formatFrame=FORMAT_8_BIT)
		im = Image.fromarray(gray_array)

		#Actualitza el CMOS viewer.
		#self.refreshCMOS(gray_array)

		#Comproba que s'ha de guardar l'arxiu.
		if self.checkBoxSaveFiles.isChecked():
			if not os.path.exists(directory_output_muestras + "/" + self.filename_pitch):
				os.mkdir(directory_output_muestras + "/" + self.filename_pitch)

			#Creem el path.
			savePath = directory_output_muestras + '/{}/{}_Row_{}Col_{}.{}'.format(
						str(self.filename_pitch),
						str(indexPicture),
						str(coordPix[0]),
						str(coordPix[1]),
						self.output_format_selected
						)
			#Guarde,
			im.save(savePath)
		
		#Afegim la imatge dins del set d'imatges capturades per a que es mostri en el visor NIM.
		self.lock.acquire()
		self.images_capture.append(np.array(im))
		self.lock.release()
		
			
			

	#Actaliza la componente X del led inicial
	def update_ledInicial_X(self, new_value):
		""" Define the initial LED position of the scan in X-axis. """
		self.ledInicial_X = new_value

	#Actaliza la componente y del led inicial
	def update_ledInicial_Y(self, new_value):
		""" Define the initial LED position of the scan in Y-axis. """
		self.ledInicial_Y = new_value

	#Enciende 1 solo led.
	def turn_on_led0(self):
		""" Turn on/off the first LED for dynamic acquisition mode. """
		if self.pushButton_turn_on_led0.isChecked():
			display.turn_on()
			display.turn_on_led(int(self.ledInicial_X), int(self.ledInicial_Y))
			self.pushButton_turn_on_led0.setText("Turn OFF")
			if self.debug:
				print('\t[DEBUG_MAIN] - Turned ON: ',
					(self.ledInicial_X, self.ledInicial_Y))
		else:
			display.turn_off_led(int(self.ledInicial_X), int(self.ledInicial_Y))
			display.turn_off()
			self.pushButton_turn_on_led0.setText("Turn ON")
	
	######## FUNCIONES QUE SE TIENEN QUE CAMBIAR TODO

	

	#YES, SE LLAMA EN EL STOP BUTTON.
	def send_stop(self):
		""" Activates stop signal to the current acquisition mode. """
		self.eventStopThread.set()
		

	#YES, SE LLAMA EN EL START ACQISITION.
	def receive_stop(self):
		""" Receive an acknowledge from the stopped thread. """
		if self.tabWidget.currentIndex() == 0:
			self.thread_pitch.stop.emit(False)
		# Enable tab widget
		self.tabWidget.setEnabled(True)
		self.widget.setEnabled(True)
		self.thread_cmos.cmos_terminate.emit(False)
		self.thread_cmos.start()

	#YES, SE USA EN EL START ACQUISITION.
	def get_coords(self, step):
		""" Receive the current row coordinate of the scan. """
		self.current_coords = step

	
	########################################
	# Viewers
	########################################

	#Actualiza la imagen que se visualiza en el CMOS VIEWER
	def cmos_viewer(self, cmos_dataframe):
		""" Print raw image of CMOS camera. """
		DmmProp.updateAutomaticProperties()
		if FORMAT_8_BIT:
			cmos_qimage = QtGui.QImage(
					cmos_dataframe,
					cmos_dataframe.shape[1],
					cmos_dataframe.shape[0],
					QtGui.QImage.Format_Grayscale8,
					)
		else:
			cmos_qimage = QtGui.QImage(
					cmos_dataframe,
					cmos_dataframe.shape[1],
					cmos_dataframe.shape[0],
					QtGui.QImage.Format_Grayscale16,
					)
		image_pixmap = QPixmap.fromImage(cmos_qimage)
		if not self.zoom:
			self.item_frame_cmos_viewer.setPixmap(image_pixmap)
			frame_rect = self.item_frame_cmos_viewer.sceneBoundingRect()
			self.window_cmos.scene_cmos_viewer.setSceneRect(frame_rect)
			self.window_cmos.CS_CameraView.fitInView(
					frame_rect,
					Qt.KeepAspectRatio,
					)
			self.window_cmos.CS_CameraView.ensureVisible(
					frame_rect,
					50,
					50,
					)
		self.window_nim.CS_View.fitInView(self.window_nim.scene_nim_viewer.sceneRect(),
								  Qt.KeepAspectRatio)

	


	#Limpia el NIM, aun no se ha hecho TODO
	def clear_scene(self):
		""" Clear NIM scene during focus mode. """
		for item in  self.window_nim.scene_nim_viewer.items():
			self.window_nim.scene_nim_viewer.removeItem(item)

		self.window_nim.scene_nim_viewer.clear()
	
	#Ayuda a actualizar el NIM
	def frame_transform(self, data_array):
		
		""" Adapt frame to Qt format. """
		item_frame = QtWidgets.QGraphicsPixmapItem()
		h, w = data_array.shape
		bytesPerLine = data_array[0].nbytes

		if FORMAT_8_BIT:
			format = QtGui.QImage.Format_Grayscale8
		else:
			format = QtGui.QImage.Format_Grayscale16

		nim_qimage = QtGui.QImage(data_array, w, h, bytesPerLine, format)
		im_pixmap = QPixmap.fromImage(nim_qimage)

		self.window_nim.scene_nim_viewer.setSceneRect(
				0,
				0,
				0,
				0,
				)
		self.window_nim.scene_nim_viewer.setSceneRect(
				0,
				0,
				nim_qimage.width(),
				nim_qimage.height(),
				)
		self.item_frame_nim_viewer.setPixmap(im_pixmap)
		self.item_frame_nim_viewer.update(self.window_nim.scene_nim_viewer.sceneRect())
		
		self.window_nim.CS_View.ensureVisible(
				0,
				0,
				int(self.window_nim.scene_nim_viewer.width()),
				int(self.window_nim.scene_nim_viewer.height()),
				int(self.window_nim.scene_nim_viewer.width()/2),
				int(self.window_nim.scene_nim_viewer.height()/2),
				)

	def visNim(self, images, nx, padding):
		n = len(images)
		h, w = images[0].shape
		ny = n // nx + (n % nx > 0)
		gap = int(padding * w)

		H = ny * h + (ny - 1) * gap
		W = min(nx, n) * w + (nx - 1) * gap
		
		imageFinal = np.zeros((H, W), dtype=images[0].dtype)

		for k, im in enumerate(images):
			ny = n // nx + (n % nx > 0)
			row = (n - 1) // nx - k // nx
			ncolumns = min(n, nx)
			column = ncolumns - 1 - k % nx
			x0 = column * (gap + w)
			y0 = row * (gap + h)
			imageFinal[y0: y0 + h, x0: x0 + w] = im

		return imageFinal



	#YES se llama cuando cambias la resolucion de la camara TODO.
	def update_cmos_viewer_size(self, qrectf, width_rect, height_rect):
		""" Fit the CMOS viewer to any resolution and zoom mode.
			@param rectf: new resolution rectangle dimensions
			@param width_rect: width of the new resolution
			@param height_rect: height of the new resolution
		"""
		self.zoom = False
		self.window_cmos.scene_cmos_viewer.setSceneRect(qrectf)
		self.window_cmos.CS_CameraView.fitInView(qrectf, Qt.KeepAspectRatio)
		self.window_cmos.CS_CameraView.ensureVisible(
				qrectf,
				50,
				50,
				)
		#  self.window_cmos.CS_CameraView.fitInView(self.window_cmos.scene_cmos_viewer.sceneRect())
		self.xpos_sa = int(width_rect/2)
		self.ypos_sa = int(height_rect/2)
		

	#Reseteo de la escena, cambiarlo entero TODO.
	def reset_scene(self):
		""" Set all the parameters to the default value. """

		self.xpos_sa = int(self.window_cmos.scene_cmos_viewer.width()/2)
		self.ypos_sa = int(self.window_cmos.scene_cmos_viewer.height()/2)
		
		# CMOS settings
		self.spinBox_sensing_area.setValue(5)
		self.spinBox_gain.setValue(16)
		self.spinBox_exposure.setValue(16600)
		# Leds intensity
		self.spinBox_leds_intensity.setValue(255)
		self.spinBox_display_corriente.setValue(63)
		# Dynamic settings
		self.spinBox_X_inicial_led.setValue(0)
		self.spinBox_Y_inicial_led.setValue(0)
		self.pushButton_turn_on_led0.setChecked(False)
		self.pushButton_turn_on_led0.setEnabled(True)
		# Clear display
		#self.jbd.clear_display()
		# Clear NIM scene
		self.window_nim.scene_nim_viewer.clear()
		self.setStatusBar("Reseted Scene.")

	#HACE UN UPDATE DE LOS ICONOS ya que no se ponen automaticamente.
	def upload_icons(self):
		"""Put Icon PNG images on widgets."""
		self.pushButton_snap.setIcon(QtGui.QIcon(path_icons
			+'/snapshot.png'))
		self.pushButton_reset.setIcon(QtGui.QIcon(path_icons
			+'/reset.png'))

	#CAMBIA EL FORMATO DE LA CAMARA.
	def change_camera_format(self):
		if(self.comboBox_format.currentText() == "8-Bit"):
			FORMAT_8_BIT = True
		else:
			FORMAT_8_BIT = False

	def change_output_format(self):
		self.output_format_selected = self.comboBox_output_file_format.currentText()


	########################################
	# Camera connection
	########################################

	#CONNECTA O DESCONNECTA LA CAMARA
	def connect_camera(self, state):
		""" Initialize the camera streaming when it is connected. """
		if state:
			#try:
			# Read camera model and serial number
			devices = Tis.getCameraModel()
			
			# Check if camera model coincides with our cameras
			for position in range(3):
				window.comboBox_camera_model.setCurrentIndex(position)
				cam_model = window.comboBox_camera_model.currentText()
				if cam_model == devices[0]:
					cam_index = window.comboBox_camera_model.currentIndex()
				elif cam_model == devices[0][:-3]:
					cam_index = window.comboBox_camera_model.currentIndex()
				elif cam_model == devices[0][:-4]:
					cam_index = window.comboBox_camera_model.currentIndex()
			window.comboBox_camera_model.setCurrentIndex(cam_index)
			cam_model = window.comboBox_camera_model.currentText()
			self.setStatusBar('Camera selected: ' + cam_model + str(cam_index))
			window.comboBox_camera_model.setEnabled(False)
			if cam_index == 0:
				self.cam_2 = True
				self.cam_3 = True

			self.width, self.height = DmmProp.get_format(0, cam_index)
			self.framerate = DmmProp.getFramerate()
			DmmProp.cameraUSB_2_0 = self.cam_2
			DmmProp.cameraUSB_3_1 = self.cam_3
			DmmProp.set_conf()
			# Inits the pipeline
			Tis.initCamera(
					devices[1],          int(self.width), int(self.height),
					int(self.framerate), FORMAT_8_BIT
					)
			# Disable the automatic properties of the camera
			Tis.setProperty("Gain Auto", False)
			Tis.setProperty("Exposure Auto", False)
			Tis.listProperties()
			# Start the pipeline so the camera streams
			Tis.Start_pipeline()
			self.xpos_sa = int(self.width/2)
			self.ypos_sa = int(self.height/2)
			self.area_top, self.area_left = Tis.get_coords_rect(self.sensing_area)
			
			self.setStatusBar('Config done!')
			self.thread_cmos.cmos_format.emit(FORMAT_8_BIT)
			self.thread_cmos.start()  # Finally starts the thread of camera continous captures.

			if self.cam_2:
				self.init_gain = Tis.Get_value("Gain", 1)
				self.init_exposure = Tis.Get_value("Exposure", 1)
				self.spinBox_gain.setValue(int(self.init_gain))
				self.spinBox_exposure.setValue(int(self.init_exposure))
			else:
				self.init_gain = Tis.Get_value("Gain", 1)
				self.spinBox_gain.setValue(int(self.init_gain))
				self.init_exposure = Tis.Get_value("Exposure Time (us)", 1)
				self.spinBox_exposure.setValue(int(self.init_exposure))
			
			#Especificamos que hemos conseguido conectar la camara.
			self.camera_connected = True
		else:
			#Especificamos que DESCONECTAMOS LA CAMARA.
			self.camera_connected = False

			Tis.Stop_pipeline()
			self.thread_cmos.cmos_terminate.emit(True)
			self.setStatusBar('Camera',window.comboBox_camera_model.currentText(),'has been disconnected')

	########################################
	# Save functions
	########################################

	#SE ACTIVA CUANDO LE DAS AL BOTON DE HACER FOTO.
	#SI LA CAMARA NO ESTA ACTIVADA NO HACE NADA.
	def snap_image(self):
		""" Save current CMOS viewer frame. """
		if(self.camera_connected):
			self.hide_rectangle(state=1)
			file = QFileDialog.getSaveFileName(
					self,
					"Save Image",
					expanduser("~") + "/untitled.png",
					"PNG Files (*.png)",
					)
			areaF = QRectF(
					0,
					0,
					self.window_cmos.scene_cmos_viewer.width(),
					self.window_cmos.scene_cmos_viewer.height(),
					)
			qImgSv = QtGui.QImage(
					self.window_cmos.scene_cmos_viewer.width(),
					self.window_cmos.scene_cmos_viewer.height(),
					QtGui.QImage.Format_ARGB32
					)
			painter = QPainter(qImgSv)
			# Render the region of interest to the QImage.
			self.window_cmos.scene_cmos_viewer.render(painter, areaF)
			painter.end()
			qImgSv.save(file[0])
			# Show the sensing area again
			self.hide_rectangle(state=0)
		else:
			self.setStatusBar("Camera is NOT connected, you can't take an image.")
		
	########################################
	# Exit functions
	########################################

	def quit(self):
		self.close()

	def closeEvent(self, event):
		# default closeEvent when (X) window button is pressed
		reply = QtWidgets.QMessageBox.question(
				self, 'Message', "Are you sure to quit?",
				QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
				QtWidgets.QMessageBox.No,
				)
		if reply == QtWidgets.QMessageBox.Yes:
			if(self.thread_cmos.isRunning):
				self.thread_cmos.cmos_terminate.emit(True)
			if(self.camera_connected):
				Tis.Stop_pipeline()
			#self.jbd.clear_display()
			display.turn_off()
			logging.info("[%s] Exit!" % (time.strftime("%H:%M:%S")))
			logging.info("Cerrando Aplicacion")
			
			QtWidgets.QMainWindow.closeEvent(self, event)
		else:
			event.ignore()
		
	

if __name__ == "__main__":
	display = display_nuevo()
	app = QtWidgets.QApplication([])
	CONTRAST_PCTGE = 1 # From 0 to 1
	
	#############################################################
	#CREATING FOLDERS AND GLOBAL PATHS.
	home = expanduser("~")
	path = os.path.abspath('')

	if path[-1] == 'j':
		path = path + "/uenxipProgram"
		antpath = os.path.abspath('./')

	else:
		antpath = os.path.abspath('../')
	
	pathData = path + '/Data'
	path_config = pathData + '/configs/'
	stitcher_path = antpath + '/StitcherProgram/mainpantalla.py'
	path_icons = pathData + '/icons'
	ftimeFolder = time.strftime("/Test_%Y_%m_%d")
	directory = antpath + '/ImagesLibrary/HistorialSets'
	# Create Data directory
	if not os.path.exists(pathData):
		os.mkdir(pathData)
	# Create main directory
	if not os.path.exists(directory):
		os.mkdir(directory)
	#Create configs directory
	if not os.path.exists(path_config):
		os.mkdir(path_config)
	# Create images directory
	if not os.path.exists(path_icons):
		os.mkdir(path_icons)
	# Create daily subfolder
	directory_output_muestras = directory + ftimeFolder
	if not os.path.exists(directory_output_muestras):
		os.mkdir(directory_output_muestras)
	#############################################################

	
	flogtimeFolder = time.strftime("/log/log_%Y_%m_%d.log")
	path_log = path + flogtimeFolder
	#Init logging
	info = QFileInfo(path_log)
	if not os.path.isdir(path + '/log'):
		os.mkdir(path + '/log')
	if not info.exists():
		f= open(path_log,"w+")
	logging.basicConfig(filename=path_log, level=logging.INFO,)
	logging.info("Nueva Session")

	# Define default global variables

	#Camera
	Tis = TIS()

	#Camera CONFIG (resolution, format, freq, etc.) 
	DmmProp = DmmTIS(None, False, True, Tis)

	#Init main window.
	window = MainWindow()

	#Setup de camera config to main window.(aunque parezca que es al reves)
	DmmProp.window = window
	DmmProp.set_conf()

	#Try to get the camera (then it will setup the config depending to the camera model)
	try:
		devices = Tis.getCameraModel()
	except UnboundLocalError:
		devices = []
	
	
	# If any camera is connected, the GUI charge the default values
	if not devices:
		logging.warning('[Warning] - Any device has been connected.')
	else:
		#Print the devices. 
		logging.info("Devices Connected:")
		for i in devices:
			logging.info(i)

	# Set stream format (Camera format).
	FORMAT_8_BIT = True # True -> 8 bits // False -> 16 bits



	#Init icons.
	window.upload_icons()

	#Init main window and app.
	window.show()
	app.exec_()
