# -*- coding: utf-8 -*-

#
# Created by: Sergio Moreno
#
# Date: 06-11-20


from PyQt5 import QtCore
from PyQt5.QtCore import *

class CmosThread(QThread):

        cmos_frame     = pyqtSignal(object)
        cmos_terminate = pyqtSignal(object)
        cmos_format   = pyqtSignal(object)

        def __init__(self, tiscamera):
                QThread.__init__(self)
                self.tis = tiscamera
                
                self.stp_running = False 
                self.camera_format = True
                self.cmos_format.connect(self.update_format)
                self.cmos_terminate.connect(self.terminate)

        # run method gets called when we start the thread
        def run(self):
            while not self.stp_running:
                frame1D, grayArray = self.tis.cameraFrame(formatFrame=self.cam_format)
                self.cmos_frame.emit(grayArray)

        def update_format(self, new_bool):
            """ Update camera format:
                    True -> 8bit
                    False -> 16bit
            """
            self.cam_format = new_bool

        def terminate(self, new_bool):
            """ Break the run function """
            self.stp_running = new_bool
