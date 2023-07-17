from fileinput import close
from skimage import io
import os
from os.path import expanduser
import csv
import logging
import time
import skimage.transform

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from form import Ui_MainPantalla
from imageDisplay import ImageDisplay
import holoUtils


formatos = [".png", ".tiff", ".jpg"]
IMPORT_FORMATS = ('*.tiff', '*.jpg', '*.png')

class MainPantalla(QtWidgets.QMainWindow, Ui_MainPantalla):

    

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setAcceptDrops(True)

        self.ddxx = self.ddxxSpin.value()
        self.ddxy = self.ddxySpin.value()
        self.ddyx = self.ddyxSpin.value()
        self.ddyy = self.ddyySpin.value()

        self.dddx_dx_x = self.dddx_dx_x_Spin.value()
        self.dddx_dx_y = self.dddx_dx_y_Spin.value()
        self.dddx_dy_x = self.dddx_dy_x_Spin.value()
        self.dddx_dy_y = self.dddx_dy_y_Spin.value()

        self.dddy_dx_x = self.dddy_dx_x_Spin.value()
        self.dddy_dx_y = self.dddy_dx_y_Spin.value()
        self.dddy_dy_x = self.dddy_dy_x_Spin.value()
        self.dddy_dy_y = self.dddy_dy_y_Spin.value()
   
        self.nx = self.NxSpin.value()
        self.ny = self.NySpin.value()

        self.lambd = self.lambdaSpin.value()
        self.z = self.ZSpin.value()
        self.z0 = self.z0Spin.value()
        self.sepPixCam = self.sepPixCamSpin.value()
        self.sepPixDisp = self.sepPixDispSpin.value()
        self.pitchCam = self.pitchCamSpin.value()
        self.pitchDisp = self.pitchDispSpin.value()
        self.apodization = self.ApodizatiSpin.value()
        self.pas = self.pasoSpinB.value()

        self.lineNameFiles.setText("fileName")
        self.fileNameExport = self.lineNameFiles.text()
        self.path_rec = ""

        self.csvParamExport = self.checkParam.isChecked()
        self.formatExport = self.cmbFormatos.currentIndex()
        self.sigma = self.sigmaSpin.value()
        self.cropH = self.spinCropH.value()
        self.cropV = self.spinCropV.value()
        self.nfeatures = self.nFeaturesSpin.value()
        self.optSift = self.optSpinB.value()
        self.epsilon = self.epsilonSpin.value()
        self.formatImport = self.formatInputSelector.currentIndex()
        self.wiggle = self.wiggleSpin.value()
        self.factImage = self.factSpin.value()
        self.orderImport = self.sortedImages_selector.currentIndex()

        self.holos = []
        self.holosIFFT = []
        self.inputImage = 0
        self.outputImage = 0
        self.stitchedImage = 0
        self.moment = True
        self.stack = self.StackCheck.isChecked()

        self.modeStitching = self.checkBoxUsarTodos.isChecked()


        self.processing = False
        

        #Variables de control
        self.setCargado = False


        # Init variables
        self.cargarSetBtn.clicked.connect(self.cargarSet)
        self.CargarImageBtn.clicked.connect(self.cargarImageFile)
        self.StitchBtn.clicked.connect(self.Stitch)
        self.RetrocederBtn.clicked.connect(self.RetrocederIFFT)
        self.AdvanceBtn.clicked.connect(self.AvanzarIFFT)
        self.CalculateBtn.clicked.connect(self.CalculateIFFT)
        self.exportBtn.clicked.connect(self.ExportImages)
        self.importBtn.clicked.connect(self.ImportSession)
        self.CalculateValuesDistBtn.clicked.connect(self.CalculateDistValueVectors)
        self.PathExportBtn.clicked.connect(self.SelectPathExport)
        self.RestoreLastSessionBtn.clicked.connect(self.RestoreLastSession)
        

        # Spin box connection
        self.ApodizatiSpin.valueChanged.connect(self.setApodization)

        self.ddxxSpin.valueChanged.connect(self.setddxx)
        self.ddxySpin.valueChanged.connect(self.setddxy)
        self.ddyxSpin.valueChanged.connect(self.setddyx)
        self.ddyySpin.valueChanged.connect(self.setddyy)

        self.dddx_dx_x_Spin.valueChanged.connect(self.setdddx_dx_x)
        self.dddx_dx_y_Spin.valueChanged.connect(self.setdddx_dx_y)
        self.dddx_dy_x_Spin.valueChanged.connect(self.setdddx_dy_x)
        self.dddx_dy_y_Spin.valueChanged.connect(self.setdddx_dy_y)

        self.dddy_dx_x_Spin.valueChanged.connect(self.setdddy_dx_x)
        self.dddy_dx_y_Spin.valueChanged.connect(self.setdddy_dx_y)
        self.dddy_dy_x_Spin.valueChanged.connect(self.setdddy_dy_x)
        self.dddy_dy_y_Spin.valueChanged.connect(self.setdddy_dy_y)


        self.NxSpin.valueChanged.connect(self.setNx)
        self.NySpin.valueChanged.connect(self.setNy)
        self.lambdaSpin.valueChanged.connect(self.setLambda)
        self.ZSpin.valueChanged.connect(self.setz)
        self.z0Spin.valueChanged.connect(self.setz0)
        self.sepPixCamSpin.valueChanged.connect(self.setSepPixCam)
        self.checkParam.stateChanged.connect(self.setCSVParamExported)
        self.checkBoxUsarTodos.stateChanged.connect(self.setModeStitching)
        self.StackCheck.stateChanged.connect(self.setStack)
        self.lineNameFiles.textChanged.connect(self.setFileNameExport)
        self.linePathToExport.textChanged.connect(self.setPathExport)
        self.cmbFormatos.currentIndexChanged.connect(self.setFormato)
        self.formatInputSelector.currentIndexChanged.connect(self.setImportFormat)
        self.sortedImages_selector.currentIndexChanged.connect(self.setImportOrder)
        self.pasoSpinB.valueChanged.connect(self.setPas)
        self.sigmaSpin.valueChanged.connect(self.setSigma)
        self.nFeaturesSpin.valueChanged.connect(self.setNfeatures)
        self.optSpinB.valueChanged.connect(self.setOptSift)
        self.epsilonSpin.valueChanged.connect(self.setEpsilon)
        self.wiggleSpin.valueChanged.connect(self.setWiggle)
        self.factSpin.valueChanged.connect(self.setFactImage)
        self.pitchCamSpin.valueChanged.connect(self.setPitchCam)
        self.pitchDispSpin.valueChanged.connect(self.setPitchDisp)
        self.sepPixDispSpin.valueChanged.connect(self.setSepPixDisp)
        self.spinCropH.valueChanged.connect(self.setCropH)
        self.spinCropV.valueChanged.connect(self.setCropV)
        #self.ZSlider.valueChanged.connect(self.setz)
        #self.z0Slider.valueChanged.connect(self.setz0)
        
        #Inicialize imageDisplays
        self.imageDisplayMosaic = ImageDisplay(self.imageLabel)
        self.imageDisplayIFFT = ImageDisplay(self.imageLabel2)

        
        self.zoominBtn.clicked.connect(self.imageDisplayMosaic.zoomPlus)
        self.zoomOutbrn.clicked.connect(self.imageDisplayMosaic.zoomMinus)
        self.resetZoomBtn.clicked.connect(self.imageDisplayMosaic.resetZoom)
        self.buttonCalcAltura.clicked.connect(self.calcularAltura)
        self.setEnabledCalculZ0(False)

        self.zoominBtn2.clicked.connect(self.imageDisplayIFFT.zoomPlus)
        self.zoomOutbrn2.clicked.connect(self.imageDisplayIFFT.zoomMinus)
        self.resetZoomBtn2.clicked.connect(self.imageDisplayIFFT.resetZoom)
        self.btnCalculaAll.clicked.connect(self.calcularAllIFFT)

        
    #####################################
    #########   SETTERS
    #####################################
    def setddxx(self, new_value):
        self.ddxx = new_value

    def setddxy(self, new_value):
        self.ddxy = new_value

    def setddyx(self, new_value):
        self.ddyx = new_value

    def setddyy(self, new_value):
        self.ddyy = new_value


    def setdddx_dx_x(self, new_value):
        self.dddx_dx_x = new_value

    def setdddx_dx_y(self, new_value):
        self.dddx_dx_y = new_value

    def setdddx_dy_x(self, new_value):
        self.dddx_dy_x = new_value

    def setdddx_dy_y(self, new_value):
        self.dddx_dy_y = new_value

    def setdddy_dx_x(self, new_value):
        self.dddy_dx_x = new_value

    def setdddy_dx_y(self, new_value):
        self.dddy_dx_y = new_value

    def setdddy_dy_x(self, new_value):
        self.dddy_dy_x = new_value

    def setdddy_dy_y(self, new_value):
        self.dddy_dy_y = new_value

    def setNx(self, new_value):
        self.nx = new_value

    def setNy(self, new_value):
        self.ny = new_value

    def setLambda(self, new_value):
        self.lambd = new_value

    def setz(self, new_value):
        self.z = new_value

    def setz0(self, new_value):
        self.z0 = new_value

    def setPas(self, new_value):
        self.pas = new_value

    def setSepPixCam(self, new_value):
        self.sepPixCam = new_value
    
    def setPitchCam(self, new_value):
        self.pitchCam = new_value

    def setPitchDisp(self, new_value):
        self.pitchDisp = new_value

    def setSepPixDisp(self, new_value):
        self.sepPixDisp = new_value

    def setApodization(self, new_value):
        self.apodization = new_value

    def setFormato(self,new_value):
        self.formatExport = new_value

    def setImportFormat(self, new_value):
        self.formatImport = new_value

    def setImportOrder(self, new_value):
        self.orderImport = new_value
    
    def setPathExport(self, new_value):
        self.path_rec = new_value
    
    def setFileNameExport(self, new_value):
        self.fileNameExport = new_value
    
    def setCSVParamExported(self, new_value):
        self.csvParamExport = new_value

    def setModeStitching(self, new_value):
        self.modeStitching = (new_value != 0)
    
    def setSigma(self, new_value):
        self.sigma = new_value

    def setEpsilon(self, new_value):
        self.epsilon = new_value
    
    def setNfeatures(self, new_value):
        self.nfeatures = new_value

    def setOptSift(self, new_value):
        self.optSift = new_value

    def setWiggle(self, new_value):
        self.wiggle = new_value

    def setFactImage(self, new_value):
        self.factImage = new_value
    
    def setCropH(self, new_value):
        self.cropH = new_value
    
    def setCropV(self, new_value):
        self.cropV = new_value
    
    def setStack(self, new_value):
        
        self.stack = (new_value != 0)

    def setStatusBar(self, text):
        self.StatusContent.setText(text)
        logging.info(text)
        app.processEvents()

    def setStatusWorking(self, b):
        if b:
            self.progressBar.setRange(0,0)
        else:
            self.progressBar.setRange(0,100)
        app.processEvents()
    
    def activaStitch(self):
        self.StitchBtn.setEnabled(True)
        self.CalculateValuesDistBtn.setEnabled(True)

    def activaIFFT(self):
        self.CalculateBtn.setEnabled(True)
        self.RetrocederBtn.setEnabled(True)
        self.AdvanceBtn.setEnabled(True)


    def setlinePathToExport(self, new_value):
        self.linePathToExport.setText(new_value)
        self.path_rec = new_value

    def updateZ0SpinB(self):
        self.z0Spin.setValue(self.z0)

        

    #####################################
    #####################################

    """
    Selecciona el Path de exportación.
    """
    def SelectPathExport(self):
        dname = QFileDialog.getExistingDirectory(self, None, "open a directory")
        if dname:
            self.setlinePathToExport(dname)

    """
    Metodo que carga un Set de imagenes y que se inicializa cuando se hace click al botón "Cargar Set".
    """
    def cargarSet(self):
        dname = QFileDialog.getExistingDirectory(self, "open a directory", directory=antpath+"/ImagesLibrary")
        if dname:
            try:
                self.holos = holoUtils.loadAndNormalize(dname, IMPORT_FORMATS[self.formatImport], self.orderImport)

                if len(self.holos) == 0:
                    self.setStatusBar("No se han detectado muestras o fondos. Comprueba las carpetas o el formato.")
                elif len(self.holos) == 1:
                    self.setStatusBar("Solo se ha cargado una imagen. No hace falta stitching.")
                    self.cargarImageArray(self.holos[0])
                else:
                    self.setStatusBar(
                        "Se ha cargado el set de imagenes de " + dname + ". Hay " + str(len(self.holos)) + " muestras.")
                    self.setDefaultParams()
                    self.activaStitch()

            except:
                self.setStatusBar("No se ha podido cargar el set, comprueba el orden o el formato.")

            finally:
                self.setStatusWorking(b=False)

    """
    Metodo de apoyo para cargar 1 sola imagen en el visualizador de Mosaico. Se usa cuando se hace el Stitching o 
    se carga 1 sola imagen. Ademas activa la possibilidad de realizar operaciones IFFT o calculo de altura.
    """
    def cargarImageArray(self, image):

        self.inputImage = image
        self.activaIFFT()
        self.setEnabledCalculZ0(False)

        io.imsave(path_last_session + 'input.png', image)
        self.imageDisplayMosaic.loadImage(path_last_session + 'input.png')

        self.setStatusBar('Se ha guardado la imagen en: ' + path_last_session + 'input.png')

        
    """
    Metodo para cargar 1 sola imagen. Se activa cuando se hace click al botón "Cargar Imagen".
    """
    def cargarImageFile(self):

        try:

            fnameMuestra = QFileDialog.getOpenFileName(self, "Selecciona la MUESTRA", antpath+"/ImagesLibrary", "*.png; *.jpg; *.tiff")

            typeImage = "." + fnameMuestra[0].split('.')[1]

            fnameFondo = QFileDialog.getOpenFileName(self, "Selecciona el FONDO", antpath+"/ImagesLibrary", "*"+typeImage)
            
            if fnameMuestra[0] != '' and fnameFondo[0] != '':
                self.cargarImageArray(holoUtils.loadMuestraAndFondo(fnameMuestra[0], fnameFondo[0],typeImage=typeImage))
                self.setStatusBar("Se ha cargado la imagen " +fnameMuestra[0] + ".")
            else:
                self.setStatusBar("No se ha seleccionado bien una de las dos imagenes.")
        
        except:
            self.setStatusBar("Ha habido un error. Vuelve a intentarlo.")
            


        

    """
    Metodo que se encarga de hacer todos los updates de los ddx,ddy, etc. cuando estos son calculados.
    """
    def updateVectorParam(self, m1, m2, fact):

        self.ddxxSpin.setValue(m1.intercept_[0] / fact)
        self.ddxySpin.setValue(m1.intercept_[1] / fact)

        self.dddx_dx_x_Spin.setValue(m1.coef_[1][0] / fact)
        self.dddx_dx_y_Spin.setValue(m1.coef_[1][1] / fact)
        self.dddx_dy_x_Spin.setValue(m1.coef_[0][0] / fact)
        self.dddx_dy_y_Spin.setValue(m1.coef_[0][1] / fact)

        self.ddyxSpin.setValue(m2.intercept_[0] / fact)
        self.ddyySpin.setValue(m2.intercept_[1] / fact)

        self.dddy_dx_x_Spin.setValue(m2.coef_[1][0] / fact)
        self.dddy_dx_y_Spin.setValue(m2.coef_[1][1] / fact)
        self.dddy_dy_x_Spin.setValue(m2.coef_[0][0] / fact)
        self.dddy_dy_y_Spin.setValue(m2.coef_[0][1] / fact)


        self.pitchCamSpin.setValue(np.linalg.norm(m1.intercept_ / fact))

    """
    Metodo que se encarga de restablecer los valores de los ddx,ddy, etc.
    """
    def setDefaultParams(self):

        self.ddxxSpin.setValue(self.holos[0].shape[1] + 50)
        self.ddxySpin.setValue(0)

        self.dddx_dx_x_Spin.setValue(0)
        self.dddx_dx_y_Spin.setValue(0)
        self.dddx_dy_x_Spin.setValue(0)
        self.dddx_dy_y_Spin.setValue(0)

        self.ddyxSpin.setValue(0)
        self.ddyySpin.setValue(self.holos[0].shape[0] + 50)

        self.dddy_dx_x_Spin.setValue(0)
        self.dddy_dx_y_Spin.setValue(0)
        self.dddy_dy_x_Spin.setValue(0)
        self.dddy_dy_y_Spin.setValue(0)

        self.factSpin.setValue(1)
        self.wiggleSpin.setValue(0)

    """
    Permite el calculo de la altura.
    """
    def setEnabledCalculZ0(self, b=True):
        self.buttonCalcAltura.setEnabled(b)
        self.pitchCamSpin.setEnabled(b)
        self.pitchDispSpin.setEnabled(b)
        self.sepPixDispSpin.setEnabled(b)
        self.btnCalculaAll.setEnabled(b)

    """
    Permite hacer el Stitching con todos 
    """
    def setEnabledChangeStitchingMode(self, b=True):
        self.checkBoxUsarTodos.setEnabled(b)
        self.spinCropH.setEnabled(b)
        self.spinCropV.setEnabled(b)


    """
    Metodo que calcula los valores de ddx, ddy, etc. usando la libreria HoloUtils. Se activa cuando se hace click al botón
    "Calcula Valores".
    """
    def CalculateDistValueVectors(self):

        self.setStatusWorking(True)
        self.setStatusBar("Calculando los vectores de distancia.")

        try:
            if self.modeStitching is False:
                modelX, modelY = holoUtils.totalMedDistanceVectorTest([skimage.transform.rescale(im, 0.25) for im in self.holos], self.nx, self.ny, optSift=self.optSift/100, epsilon=self.epsilon)
            else:
                holosHechosCuttet = [im[self.cropV:im.shape[0]-self.cropV, self.cropH:im.shape[1]-self.cropH] for im in self.holosIFFT]
                modelX, modelY = holoUtils.totalMedDistanceVectorTest([skimage.transform.rescale(im, 0.25) for im in holosHechosCuttet], self.nx, self.ny, optSift=self.optSift/100, epsilon=self.epsilon)
            self.updateVectorParam(modelX, modelY, 0.25)
            self.setStatusBar("Vectores de distancia calculados.")
            self.setStatusWorking(False)

        except Exception as e:
            print(e)
            self.setStatusBar("No se han podido calcular los valores: " + str(e))

        finally:
            self.setStatusWorking(False)

    """
    Metodo que calcula el valor de la altura automaticamente, se activa cuando se hace click al boton "Calcular z0".
    """
    def calcularAltura(self):

        self.setStatusWorking(True)
        self.setStatusBar("Calculando altura automaticamente.")

        try:

            alt = holoUtils.detectaAltura(self.sepPixCam, self.sepPixDisp,
                                        self.pitchCam, self.pitchDisp,
                                        self.z)
            self.z0 = alt
            self.updateZ0SpinB()
            self.setStatusBar("Altura calculada.")
        except:
            self.setStatusWorking(False)            
            self.setStatusBar("No se ha podido calcular la altura. Revisa los parámetros")

        self.setStatusWorking(False)

    """
    Mètodo que hace el Stitch apoyandose en la libreria HoloUtils. Se activa con el botón "Stitch".
    """
    def Stitch(self):


        self.setStatusWorking(True)
        self.setStatusBar("Creando la imagen de mosaico con los valores.")
        if self.modeStitching is False:
            stitchedImage = holoUtils.mosaicModel(self.holos, self.nx, self.ny,
                                                    ddx=np.array([self.ddxx, self.ddxy]),
                                                    ddy=np.array([self.ddyx, self.ddyy]),
                                                    dddx_dx=np.array([self.dddx_dx_x, self.dddx_dx_y]),
                                                    dddx_dy=np.array([self.dddx_dy_x, self.dddx_dy_y]),
                                                    dddy_dx=np.array([self.dddy_dx_x, self.dddy_dx_y]),
                                                    dddy_dy=np.array([self.dddy_dy_x, self.dddy_dy_y]),
                                                    factAugment=self.factImage, wiggle=self.wiggle,
                                                    stack=self.stack, cut=True)
            self.cargarImageArray(stitchedImage)
        else:
            holosHechosCuttet = [im[self.cropV:im.shape[0]-self.cropV, self.cropH:im.shape[1]-self.cropH] for im in self.holosIFFT]
            stitchedImage = holoUtils.mosaicModel(holosHechosCuttet, self.nx, self.ny,
                                                    ddx=np.array([self.ddxx, self.ddxy]),
                                                    ddy=np.array([self.ddyx, self.ddyy]),
                                                    dddx_dx=np.array([self.dddx_dx_x, self.dddx_dx_y]),
                                                    dddx_dy=np.array([self.dddx_dy_x, self.dddx_dy_y]),
                                                    dddy_dx=np.array([self.dddy_dx_x, self.dddy_dx_y]),
                                                    dddy_dy=np.array([self.dddy_dy_x, self.dddy_dy_y]),
                                                    factAugment=self.factImage, wiggle=self.wiggle,
                                                    stack=self.stack, cut=True)
            self.outputImage = stitchedImage
            io.imsave(path_last_session+'rec.png',self.outputImage)
            self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')
        
        self.setEnabledCalculZ0(True)
        self.setStatusWorking(False)
        self.setStatusBar("Mosaico calculado.")

    """
    Metodo que hace el calculo de la reconstruccion por IFFT apoyandose en la libreria HoloUtils. Se activa segun los diversos
    métodos que vienen a continuación.
    """
    def CalculosReconstruccion(self):


        im = self.inputImage - self.inputImage.min()

        if self.apodization > 0:
            im = holoUtils.apodize(im, int(self.apodization))
    
        self.outputImage = holoUtils.reconstructHologramSph(im, self.lambd * 1e-9, self.inputImage.shape[0] * self.sepPixCam * 1e-6 / self.factImage, self.z, self.z0)
        
    """
    Método para realizar un calculo IFFT con los parametros que hay puestos en la interfaz. Se activa con el botón "Calcular".
    """
    def CalculateIFFT(self):
        self.setStatusWorking(True)
        self.setStatusBar("Calculando Holograma de la imagen de input.")

        self.CalculosReconstruccion()

        io.imsave(path_last_session+'rec.png',self.outputImage)
        self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')
        self.exportBtn.setEnabled(True)

        self.setStatusWorking(False)
        self.setStatusBar("Holograma calculado.")
    """
    Método para realizar un calculo IFFT con los parametros que hay puestos en la interfaz RETROCEDIENDO la "Z0" en la cantidad 
    que pone en la variable Paso Z0. Se activa con el botón "Retroceder".
    """
    def RetrocederIFFT(self):
        self.setStatusWorking(True)
        self.setStatusBar("Calculando Holograma de la imagen de input.")

        self.z0 -= self.pas
        self.updateZ0SpinB()
        self.CalculosReconstruccion()
        io.imsave(path_last_session+'rec.png',self.outputImage)
        self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')

        self.setStatusWorking(False)
        self.setStatusBar("Holograma calculado con paso retrocedido " + str(self.pas) + " el nuevo Z0 es " + str(self.z0))
    """
    Método para realizar un calculo IFFT con los parametros que hay puestos en la interfaz AVANZANDO la "Z0" en la cantidad 
    que pone en la variable "Paso Z0". Se activa con el botón "Retroceder".
    """
    def AvanzarIFFT(self):
        self.setStatusWorking(True)
        self.setStatusBar("Calculando Holograma de la imagen de input.")

        self.z0 += self.pas
        self.updateZ0SpinB()
        self.CalculosReconstruccion()
        io.imsave(path_last_session+'rec.png',self.outputImage)
        self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')

        self.setStatusWorking(False)
        self.setStatusBar("Holograma calculado con paso aumentado " + str(self.pas) + " el nuevo Z0 es " + str(self.z0))

    """
    Calcular el IFFT de todos los holograma.
    """
    def calcularAllIFFT(self):
        self.setStatusWorking(True)
        self.setStatusBar("Calculando TODOS los hologramas,este proceso puede tardar unos segundos.")

        self.holosIFFT = [holoUtils.reconstructHologramSph(im-im.min(), self.lambd * 1e-9, self.holos[0].shape[0] * self.sepPixCam * 1e-6 / self.factImage, self.z, self.z0) for im in self.holos]
        self.setEnabledChangeStitchingMode()

        self.setStatusWorking(False)
        self.setStatusBar("Hologramas calculados con Z " + str(self.z) + " y Z0" + str(self.z0))

    """
    Crea un CSV de parametros para poder guardarlos.
    """
    def createCSVParam(self,csvFileName,csvPathSelected,avisar=True):
        #Creamos los datos a guardar,primero el header y luego la data.
        header = ['ddxx', 'ddxy', 'ddyx', 'ddyy',
            'dddx_dx(x)','dddx_dx(y)','dddx_dy(x)','dddx_dy(y)','dddy_dx(x)','dddy_dx(y)','dddy_dy(x)','dddy_dy(y)',
            'nx', 'ny','sigmaSift','nFeatures','epsilon','goodPercentage','wiggle','factReesc',
             'lamb', 'z', 'z0', 'sepPixCam','sepPixDisp', 'pitchCam', 'pitchDisp' , 'apodization']

        data = [str(self.ddxx), str(self.ddxy), str(self.ddyx),str(self.ddyy), 
                str(self.dddx_dx_x), str(self.dddx_dx_y), str(self.dddx_dy_x), str(self.dddx_dy_y),
                 str(self.dddy_dx_x), str(self.dddy_dx_y), str(self.dddy_dy_x), str(self.dddy_dy_y),
                 str(self.nx),str(self.ny),str(self.sigma),str(self.nfeatures),str(self.epsilon),str(self.optSift),str(self.wiggle),str(self.factImage),
                 str(self.lambd), str(self.z), str(self.z0), str(self.sepPixCam),str(self.sepPixDisp),str(self.pitchCam),str(self.pitchDisp), str(self.apodization)]

        #En caso de que el nombre de archivo sea nulo, no podemos hacer nada.
        if(csvFileName != ""):
            #Si no lo es, usamos QFileINfo para comprobar que existe o no.
            info = QFileInfo(csvFileName)
            if(info.exists()):
                #Si existe, preguntamos si se quiere sobreescribir.
                reply = ''
                if avisar:
                    reply = QtWidgets.QMessageBox.question(
                    self, 'Message', "El archivo ya existe, quieres sustituirlo?.",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No,
                    )
                if(reply == QtWidgets.QMessageBox.Yes or avisar):
                    #En caso afirmativo, lo hacemos.
                    with open(info.absoluteFilePath(),"w") as file:
                        csvwriter = csv.writer(file)
                        csvwriter.writerow(header)
                        csvwriter.writerow(data)
                        close
            else:
                #S no existe, lo creamos.
                with open(info.absoluteFilePath(),"x") as file:

                    csvwriter = csv.writer(file)
                    csvwriter.writerow(header)
                    csvwriter.writerow(data)
                    close
    """
    Metodo que se usa para hacer una exportación de las imagenes y de los parametros. Se activa con el botón "EXPORT".
    """
    def ExportImages(self):
        self.setStatusWorking(True)
        self.setStatusBar("Exportando Hologramas")
        formatValue = formatos[self.formatExport]
        
        fullPath = self.path_rec + '/' + self.fileNameExport + '/' + self.fileNameExport + "_Stitched" + formatValue
        fullPathHolograma = self.path_rec + '/' + self.fileNameExport + '/' + self.fileNameExport + "_Holo" + formatValue
        pathCSV = self.path_rec + '/' + self.fileNameExport + '/' + self.fileNameExport + "_Params.csv"

        if not os.path.isdir(self.path_rec + '/' + self.fileNameExport):
            os.mkdir(self.path_rec + '/' + self.fileNameExport)
        
        if self.csvParamExport:
            self.createCSVParam(pathCSV,self.path_rec)

        try:

            if fullPath != "" and fullPathHolograma != '':
                #Si no lo es, usamos QFileINfo para comprobar que existe o no.
                info = QFileInfo(fullPath)
                if(info.exists()):
                    #Si existe, preguntamos si se quiere sobreescribir.
                    reply = QtWidgets.QMessageBox.question(
                    self, 'Message', "El archivo ya existe, quieres substituirlo?.",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No,
                    )
                    if(reply == QtWidgets.QMessageBox.Yes):
                        #En caso afirmativo, lo hacemos.
                        io.imsave(fullPath,self.inputImage)
                        io.imsave(fullPathHolograma,self.outputImage)
                else:
                    #S no existe, lo creamos.
                    io.imsave(fullPath,self.inputImage)
                    io.imsave(fullPathHolograma,self.outputImage)

            self.setStatusWorking(False)
            self.setStatusBar("Imagenes exportadas en " + self.path_rec)
        
        except:
            self.setStatusWorking(False)
            self.setStatusBar("No se han podido exportar las imagenes!")
    
    """
    Metodo que se usa para cargar el archivo CSV que pone los parametros en questión.
    """
    def cargarCSV(self, pathCSV):
        if(pathCSV != ""):
            info = QFileInfo(pathCSV)
            #Changing our variables with the new file
            #Opening the file with csvRader
            filecsv = open(info.absoluteFilePath())
            csvreader = csv.reader(filecsv)
            #Getting the variables
            header = next(csvreader)
            data = next(csvreader)
            #Changing the variables
            if((header) == ['ddxx', 'ddxy', 'ddyx', 'ddyy',
            'dddx_dx(x)','dddx_dx(y)','dddx_dy(x)','dddx_dy(y)','dddy_dx(x)','dddy_dx(y)','dddy_dy(x)','dddy_dy(y)',
            'nx', 'ny','sigmaSift','nFeatures','epsilon','goodPercentage','wiggle','factReesc',
            'lamb', 'z', 'z0', 'sepPixCam','sepPixDisp', 'pitchCam', 'pitchDisp' , 'apodization']):
                self.ddxxSpin.setValue(float(data[0]))
                self.ddxySpin.setValue(float(data[1]))
                self.ddyxSpin.setValue(float(data[2]))
                self.ddyySpin.setValue(float(data[3]))
                self.dddx_dx_x_Spin.setValue(float(data[4]))
                self.dddx_dx_y_Spin.setValue(float(data[5]))
                self.dddx_dy_x_Spin.setValue(float(data[6]))
                self.dddx_dy_y_Spin.setValue(float(data[7]))
                self.dddy_dx_x_Spin.setValue(float(data[8]))
                self.dddy_dx_y_Spin.setValue(float(data[9]))
                self.dddy_dy_x_Spin.setValue(float(data[10]))
                self.dddy_dy_y_Spin.setValue(float(data[11]))
                self.NxSpin.setValue(int(data[12]))
                self.NySpin.setValue(int(data[13]))
                self.sigmaSpin.setValue(float(data[14]))
                self.nFeaturesSpin.setValue(int(data[15]))
                self.epsilonSpin.setValue(int(data[16]))
                self.optSpinB.setValue(int(data[17]))
                self.wiggleSpin.setValue(int(data[18]))
                self.factSpin.setValue(float(data[19]))
                self.lambdaSpin.setValue(float(data[20]))
                self.ZSpin.setValue(float(data[21]))
                self.z0Spin.setValue(float(data[22]))
                self.sepPixCamSpin.setValue(float(data[23]))
                self.sepPixDispSpin.setValue(float(data[24]))
                self.pitchCamSpin.setValue(float(data[25]))
                self.pitchDispSpin.setValue(float(data[26]))
                self.ApodizatiSpin.setValue(float(data[27]))
            else:
                reply = QtWidgets.QMessageBox.information(
                    self, 'Message', "El formato del CSV es incorrecto.",
                    QtWidgets.QMessageBox.OK
                    )

            filecsv.close()

    """
    Metodo que restaura la ultima session.
    """
    def RestoreLastSession(self):
        self.inputImage = holoUtils.loadImage(path_last_session+'mosaic.png')
        self.imageDisplayMosaic.loadImage(path_last_session+'mosaic.png')
        self.outputImage = holoUtils.loadImage(path_last_session+'rec.png')
        self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')
        self.cargarCSV(path_last_session + 'params.csv')
        self.setStatusBar("Se ha restaurado la session" + path_last_session)
        self.activaIFFT()
        self.setEnabledCalculZ0(True)

    """
    Metodo que restaura una Session anterior.
    """
    def ImportSession(self):
        dname = QFileDialog.getExistingDirectory(self, "open a directory",directory=path+"/Data/reconstructions")
        
        if dname:
            content = os.listdir(dname)
            if content:
                try:
                    content.sort()
                    typeImage = "." + content[0].split('.')[1]
                    nameFiles = dname.split('/')[-1]
                    
                    self.cargarImageArray(holoUtils.loadImage(dname + '/' + nameFiles + "_Stitched" + typeImage))

                    self.outputImage = holoUtils.loadImage(dname + '/' + nameFiles + "_Holo" + typeImage)
                    io.imsave(path_last_session+'rec.png',self.outputImage)
                    self.imageDisplayIFFT.loadImage(path_last_session+'rec.png')
                    self.cargarCSV(dname + '/' + nameFiles + "_Params.csv")
                    
                    self.setStatusBar("Se ha restaurado la session" + nameFiles)
                    self.activaIFFT()
                    self.setEnabledCalculZ0(True)
                except:
                    self.setStatusBar("Los archivos necesarios no se encuentran en el directorio.")
            else:
                self.setStatusBar("El directorio esta vacio.")




    def upload_icons(self):
        """Put Icon PNG images on widgets."""
        self.zoominBtn.setIcon(QtGui.QIcon(path_icons
                +'/zoom.png'))
        self.zoomOutbrn.setIcon(QtGui.QIcon(path_icons
                +'/zoomOut.png'))
        self.resetZoomBtn.setIcon(QtGui.QIcon(path_icons
                +'/reset.png'))
        
        self.zoominBtn2.setIcon(QtGui.QIcon(path_icons
                +'/zoom.png'))
        self.zoomOutbrn2.setIcon(QtGui.QIcon(path_icons
                +'/zoomOut.png'))
        self.resetZoomBtn2.setIcon(QtGui.QIcon(path_icons
                +'/reset.png'))


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        pathCSV = path_last_session + 'params.csv'
        self.createCSVParam(pathCSV,path_last_session,avisar=False)

        logging.info("Cerrando Aplicacion")
        return super().closeEvent(a0)



if __name__ == "__main__":

    QT_DEBUG_PLUGINS = 1
    app = QtWidgets.QApplication([])
    CONTRAST_PCTGE = 1 # From 0 to 1

    #Init main window.
    window = MainPantalla()

    #####Aseguramos que el path es el que queremos y creamos las carpetas.
    home = expanduser("~")
    path = os.path.abspath('./')

    if path[-1] == 'j':
        
        path = path + "/StitcherProgram"
        antpath = os.path.abspath('./')

    else:
        antpath = os.path.abspath('../')
    
    path_icons = path + '/Data/icons'
    path_rec = path + '/Data/reconstructions'
    path_last_session = path + '/Data/lastSession/'
    ftimeFolder = time.strftime("/log/log_%Y_%m_%d.log")
    path_log = path + ftimeFolder
    #Init logging
    info = QFileInfo(path_log)
    if not os.path.isdir(path + '/log'):
        os.mkdir(path + '/log')
    if not info.exists():
        
        f= open(path_log,"w+")
    logging.basicConfig(filename=path_log, level=logging.INFO,)
    logging.info("Nueva Session")

    window.upload_icons()
    window.setlinePathToExport(path_rec)
    #Init main window and app.
    window.show()

    app.exec_()

