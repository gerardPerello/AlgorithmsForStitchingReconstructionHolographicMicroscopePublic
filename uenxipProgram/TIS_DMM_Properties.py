# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIS_2_ui.ui'
#
# Created by: Sergio Moreno
#
# Date: 16-03-2020

import os
import time
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TIS_DMM_Sensor:
    def __init__(self, mainwindow, cameraUSB_2_0, modelUSB_3_1, tiscamera):
        self.window = mainwindow
        self.cameraUSB_2_0 = cameraUSB_2_0
        self.tis = tiscamera
        self.modelUSB_3_1 = modelUSB_3_1

    def set_conf(self):
        """ Load conf parameters. """
        # Default Sensor parameters
        if self.cameraUSB_2_0 == True:
            self.window.comboBox_resolution.setItemText(0, "744x480")
            self.window.label_17.setText("16 to 63")
            self.window.label_20.setText("100 us to 0.25 s")
            self.window.spinBox_gain.setMinimum(16)
            self.window.spinBox_gain.setMaximum(63)
            self.window.spinBox_exposure.setMinimum(100)
            self.window.spinBox_exposure.setMaximum(250000)
        elif self.cameraUSB_2_0 == False:
            if self.modelUSB_3_1 == True:
                self.window.comboBox_resolution.setItemText(0, "720x540")
                self.window.label_17.setText("0 to 480")
                self.window.label_20.setText("1 us to 30 s")
                self.window.spinBox_gain.setMinimum(0)
                self.window.spinBox_gain.setMaximum(480)
                self.window.spinBox_exposure.setMinimum(1)
                self.window.spinBox_exposure.setMaximum(30000000)
            else:
                # Set the range of the offset sliders
                self.window.comboBox_resolution.setItemText(0, "3072x2048")
                self.window.comboBox_resolution.setItemText(1, "2048x2048")
                self.window.comboBox_resolution.setItemText(2, "1920x1080")
                self.window.comboBox_resolution.addItem("")
                self.window.comboBox_resolution.setItemText(3, "640x480")
                self.window.label_17.setText("0 to 480")
                self.window.label_20.setText("20 us to 60 s")
                self.window.spinBox_gain.setMinimum(0)
                self.window.spinBox_gain.setMaximum(480)
                self.window.spinBox_exposure.setMinimum(20)
                self.window.spinBox_exposure.setMaximum(60000000)

    def get_format(self, format_index, cam_index):
        """ Change the format of the camera.
        @param format_index: Index of format resolution selected
        @param cam_index: Index of camera model connected
        """
        if cam_index == 0:
            self.window.comboBox_resolution.setItemText(0, "744x480")
            self.window.label_17.setText("16 to 63")
            self.window.label_20.setText("100 us to 0.25 s")
            self.window.spinBox_gain.setMinimum(16)
            self.window.spinBox_gain.setMaximum(63)
            self.window.spinBox_exposure.setMinimum(100)
            self.window.spinBox_exposure.setMaximum(250000)
            if format_index == 0:
                width = 744
                height = 480
            elif format_index == 1:
                width = 640
                height = 480
            elif format_index == 2:
                width = 320
                height = 240
        elif cam_index == 1:
            self.window.comboBox_resolution.setItemText(0, "720x540")
            self.window.label_17.setText("0 to 480")
            self.window.label_20.setText("1 us to 30 s")
            self.window.spinBox_gain.setMinimum(0)
            self.window.spinBox_gain.setMaximum(480)
            self.window.spinBox_exposure.setMinimum(1)
            self.window.spinBox_exposure.setMaximum(30000000)
            if format_index == 0:
                width = 720
                height = 540
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(8):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "539")
                self.window.comboBox_framerate.setItemText(1, "480")
                self.window.comboBox_framerate.setItemText(2, "120")
                self.window.comboBox_framerate.setItemText(3, "60")
                self.window.comboBox_framerate.setItemText(4, "30")
                self.window.comboBox_framerate.setItemText(5, "15")
                self.window.comboBox_framerate.setItemText(6, "5")
                self.window.comboBox_framerate.setItemText(7, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
            elif format_index == 1:
                width = 640
                height = 480
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(8):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "601")
                self.window.comboBox_framerate.setItemText(1, "480")
                self.window.comboBox_framerate.setItemText(2, "120")
                self.window.comboBox_framerate.setItemText(3, "60")
                self.window.comboBox_framerate.setItemText(4, "30")
                self.window.comboBox_framerate.setItemText(5, "15")
                self.window.comboBox_framerate.setItemText(6, "5")
                self.window.comboBox_framerate.setItemText(7, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
        else:
            # Set the range of the offset sliders
            self.window.comboBox_resolution.setItemText(0, "3072x2048")
            self.window.comboBox_resolution.setItemText(1, "2048x2048")
            self.window.comboBox_resolution.setItemText(2, "1920x1080")
            self.window.comboBox_resolution.addItem("")
            self.window.comboBox_resolution.setItemText(3, "640x480")
            self.window.label_17.setText("0 to 480")
            self.window.label_20.setText("20 us to 60 s")
            self.window.spinBox_gain.setMinimum(0)
            self.window.spinBox_gain.setMaximum(480)
            self.window.spinBox_exposure.setMinimum(20)
            self.window.spinBox_exposure.setMaximum(60000000)
            if format_index == 0:
                width = 3072
                height = 2048
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(5):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "60")
                self.window.comboBox_framerate.setItemText(1, "30")
                self.window.comboBox_framerate.setItemText(2, "15")
                self.window.comboBox_framerate.setItemText(3, "5")
                self.window.comboBox_framerate.setItemText(4, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
            elif format_index == 1:
                width = 2048
                height = 2048
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(6):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "70")
                self.window.comboBox_framerate.setItemText(1, "60")
                self.window.comboBox_framerate.setItemText(2, "30")
                self.window.comboBox_framerate.setItemText(3, "15")
                self.window.comboBox_framerate.setItemText(4, "5")
                self.window.comboBox_framerate.setItemText(5, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
            elif format_index == 2:
                width = 1920
                height = 1080
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(7):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "130")
                self.window.comboBox_framerate.setItemText(1, "120")
                self.window.comboBox_framerate.setItemText(2, "60")
                self.window.comboBox_framerate.setItemText(3, "30")
                self.window.comboBox_framerate.setItemText(4, "15")
                self.window.comboBox_framerate.setItemText(5, "5")
                self.window.comboBox_framerate.setItemText(6, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
            elif format_index == 3:
                width = 640
                height = 480
                for i in range(self.window.comboBox_framerate.count()):
                    self.window.comboBox_framerate.removeItem(i)
                for i in range(8):
                    self.window.comboBox_framerate.addItem("")
                self.window.comboBox_framerate.setItemText(0, "280")
                self.window.comboBox_framerate.setItemText(1, "240")
                self.window.comboBox_framerate.setItemText(2, "120")
                self.window.comboBox_framerate.setItemText(3, "60")
                self.window.comboBox_framerate.setItemText(4, "30")
                self.window.comboBox_framerate.setItemText(5, "15")
                self.window.comboBox_framerate.setItemText(6, "5")
                self.window.comboBox_framerate.setItemText(7, "1")
                framerate = self.window.comboBox_framerate.currentText()
                self.tis.setPropertyGst("framerate", framerate)
        return width, height

    def enableGainAutomatic(self, state):
        """Enables(1)/Disables(0) automatic gain mode."""
        if state == 0:
            self.tis.setProperty("Gain Auto", False)
        else:
            self.tis.setProperty("Gain Auto", True)

    def enableExposureAutomatic(self, state):
        """Enables(1)/Disables(0) automatic time exposure mode."""
        if state == 0:
            self.tis.setProperty("Exposure Auto", False)
        else:
            self.tis.setProperty("Exposure Auto", True)

    def getFramerate(self):
        """Get current framerate setting in 1/s."""
        fr_value = self.window.comboBox_framerate.currentText()
        return(fr_value)

    def updateResolution(self, newIndex):
        width, height = self.get_format(newIndex, self.window.comboBox_camera_model.currentIndex())
        self.tis.setPropertyGst("width", width)
        self.tis.setPropertyGst("height", height)
        areaF = QRectF(0,0,width,height)
        self.window.update_cmos_viewer_size(areaF,width,height)

    def updateFramerate(self, newValue):
        """Set current framerate setting in 1/s."""
        framerate = self.getFramerate()
        self.tis.setPropertyGst("framerate", framerate)

    def updateGain(self, newValue):
        """Set current gain setting."""
        self.tis.setProperty("Gain", int(newValue))

    def getGain(self):
        """Get current gain setting."""
        gain = self.tis.Get_value("Gain", 1)
        return int(gain)

    def updateExposure(self, newValue):
        """Set current exposure time setting."""
        if self.cameraUSB_2_0:
            self.tis.setProperty("Exposure", int(newValue))
        else:
            self.tis.setProperty("Exposure Time (us)", int(newValue))

    def getExposure(self):
        """Get current exposure setting."""
        if self.cameraUSB_2_0:
            ExpTime = self.tis.Get_value("Exposure", 1)
        else:
            ExpTime = self.tis.Get_value("Exposure Time (us)", 1)
        return int(ExpTime)

    def updateBrightness(self, newValue):
        """Set current brightness setting."""
        self.tis.setProperty("Brightness", int(newValue))

    def setMaxLimitExposure(self):
        """Set maximum limit of exposure time setting."""
        if self.cameraUSB_2_0 == True:
            self.tis.setProperty("Exposure Max", int(2147483647))
        elif self.cameraUSB_2_0 == False:
            self.tis.setProperty("Exposure Auto Upper Limit", int(1000000))

    def updateAutomaticProperties(self):
        """Refresh gain and exposure time setting when automatic mode is enabled."""
        self.checkExposure()
        self.checkGain()

    def checkGain(self):
        """Get and set current gain setting in automatic mode."""
        if self.window.checkBox_auto_exposure.isChecked():                    
            Gain = self.tis.Get_value("Gain", 1)
            self.window.spinBox_gain.setValue(int(Gain))

    def checkExposure(self):
        """Get and set current exposure time setting in automatic mode."""
        if self.window.checkBox_auto_gain.isChecked():
            if self.cameraUSB_2_0 == True:
                ExpTime = self.tis.Get_value("Exposure", 1)
                self.tis.setProperty("Exposure", int(ExpTime))
            elif self.cameraUSB_2_0 == False:
                ExpTime = self.tis.Get_value("Exposure Time (us)", 1)
                self.tis.setProperty("Exposure Time (us)", int(ExpTime))
            self.window.spinBox_exposure.setValue(int(ExpTime))
