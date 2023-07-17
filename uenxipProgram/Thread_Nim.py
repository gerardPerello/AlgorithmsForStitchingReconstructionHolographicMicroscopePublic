# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIS_2_ui.ui'
#
# Created by: Sergio Moreno
#
# Date: 10-03-2020

import os
import time
import numpy as np
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import *



class PitchThread(QtCore.QThread):
    """ Class for pitch variable acquisition in chipscope mode. """
    ### Signals emitted
    raw = QtCore.pyqtSignal(object)
    stopped = QtCore.pyqtSignal()
    next_areax = QtCore.pyqtSignal(object)
    resetx = QtCore.pyqtSignal(int)
    next_areay = QtCore.pyqtSignal(object)
    resety = QtCore.pyqtSignal(int)
    coord  = QtCore.pyqtSignal(object)
    stom_frame = QtCore.pyqtSignal(object)
    ### Signals received
    pitch_area = QtCore.pyqtSignal(int, bool)
    coordx = QtCore.pyqtSignal(object)
    coordy = QtCore.pyqtSignal(object)
    static = QtCore.pyqtSignal(object)
    mov = QtCore.pyqtSignal(object)
    pitch_steps = QtCore.pyqtSignal(object)
    pitch_path = QtCore.pyqtSignal(object, str)
    file_format_output = QtCore.pyqtSignal(str)
    cam_format = QtCore.pyqtSignal(bool)
    # Initial X-Y coords
    ref_leds = QtCore.pyqtSignal(object, object)
    pitches_var = QtCore.pyqtSignal(object, object, object, object)
    frame_size = QtCore.pyqtSignal(int, int)
    # Stop thread
    stop = QtCore.pyqtSignal(bool)

    def __init__(self, tiscamera, jbd):
        """ Init class attributes. """
        super().__init__()
        self.tis = tiscamera
        self.jbd = jbd
        self.output_file_format = 'tiff'
        self.n_ypos = 5
        self.n_xpos = 5
        self.pos_x = 0
        self.pos_y = 0
        self.move_x = 0
        self.move_y = 0
        self.ipos_x = 0
        self.ipos_y = 0
        self.led_x0 = 0
        self.led_y0 = 0
        self.led_pitchx = 1
        self.led_pitchy = 1
        self.csvleds = None
        self.use_csv = False
        self.area_hide = True
        self.cmos_format = True
        self.stop_thread = False
        self.directory = None
        self.file = "VarPitch_"

        self.pitch_path.connect(self.get_path)
        self.file_format_output.connect(self.get_output_format)
        self.cam_format.connect(self.get_format)
        self.ref_leds.connect(self.get_leds)
        self.pitches_var.connect(self.get_pitches)
        self.stop.connect(self.get_stop)
        self.pitch_area.connect(self.get_area)
        self.static.connect(self.acq_mode)
        self.pitch_steps.connect(self.get_steps)
        self.coordx.connect(self.get_pos_x)
        self.coordy.connect(self.get_pos_y)
        self.mov.connect(self.get_steps)

    def run(self):
        """ Run method for chipscope acquisition. """
        # Create path to save frames
        self.create_directory(self.directory+'/'+str(self.file))
        file_time = time.strftime("_%Y%m%d_%H%M%S")
        if not self.area_hide:

            #AQUI CREA UNA MATRIZ DE NUMPY DE 0 QUE LUEGO SUPONGO QUE IRA LLENANDO CN LA IMAGEN
            empty_frame = np.zeros((int(self.n_ypos * self.area),
                int(self.n_xpos * self.area)), dtype=int)
            #TODO self.are es el area size del cuadrado rojo. Porque? No lo se xdddd.

        else:
            empty_frame = np.zeros((int(self.n_ypos * 480),
                int(self.n_xpos * 744)), dtype=int)

        # Init scan
        t_init = time.time()
        #print(self.n_ypos) ==> NUMERO DE VECES QUE LO HARA PARA X TODO borrar
        #print(self.n_xpos) ==> NUMERO DE VECES QUE LO HARA PARA Y
        for led_row in range(self.n_ypos):
            for led_col in range(self.n_xpos):
                self.jbd.clear_display()
                # Stop For nested
                if self.stop_thread:
                    break
                # Turn ON the selected LED
                #LED PITCHI ES EL SALTO Y LEDY ES EL LED INICIAL TODO borrar
                self.jbd.turn_on_led(
                        self.led_pitchy*led_row + self.led_y0,
                        self.led_pitchx*led_col + self.led_x0)

                #TimeOut foor good service
                time.sleep(0.3) # In seconds

                #########################
                # #######################
                # Creating area to draw CMOS
                
                if not self.area_hide:
                    if not self.static_mode:
                        self.pos_x = self.ipos_x+(self.led_pitchx*(led_col))
                        self.next_areax.emit(
                                [self.pos_x,self.ipos_y+(self.led_pitchy*(led_row))])
                
                ##########################

                # Capture IMAGE WITH CAMERA
                frame_1d, gray_array = self.tis.cameraFrame(
                        formatFrame=self.cmos_format) #el formato de 8 o 16 bits
                gray_raw = gray_array

                #########################
                # #######################
                # Trying to draw to CMOS
                
                if not self.area_hide:
                    gray_array = gray_array[int(self.pos_y):int(self.pos_y+self.area),
                            int(self.pos_x):int(self.pos_x+self.area)]
                    # Creates the new image
                    empty_frame[led_row*self.area:(led_row*self.area)+self.area,
                            led_col*self.area:(led_col*self.area)+self.area] = gray_array
                else:
                    # Creates the new image
                    empty_frame[led_row*480:(led_row*480)+480,
                            led_col*744:(led_col*744)+744] = gray_array

                pix_coords = (led_col, led_row)
                self.coord.emit(pix_coords)
                self.raw.emit(gray_raw)
                self.stom_frame.emit(empty_frame)
                
                ############################

                #Saving image with dif format.
                im = Image.fromarray(gray_raw)
                
                im.save(self.directory
                        +'/{}/Row_{}Col_{}_Nx{}_Ny{}_Px{}_Py{}.{}'.format(
                            str(self.file),
                            str(led_row),
                            str(led_col),
                            str(self.n_xpos),
                            str(self.n_ypos),
                            str(self.led_pitchx),
                            str(self.led_pitchy),
                            self.output_file_format
                            ))
                    
            # Second break loop
            if self.stop_thread:
                if not self.area_hide:
                    if not self.static_mode:
                        self.resetx.emit(self.ipos_x)
                        self.resety.emit(self.ipos_y)
                break
            if not self.area_hide:
                if not self.static_mode:
                    self.resetx.emit(self.ipos_x)
                    self.pos_y = self.ipos_y+(self.led_pitchy*(led_row))
                    self.next_areay.emit(
                            [self.ipos_x,
                                self.ipos_y+(self.led_pitchy*(led_row+1))])
        t_last = time.time()
        if not self.area_hide:
            if not self.static_mode:
                self.resetx.emit(self.ipos_x)
                self.resety.emit(self.ipos_y)
        self.jbd.clear_display()
        self.stopped.emit()
        print('[FRAME TIME]-', self.get_frame_time(t_init, t_last))
        np.savetxt(
                self.directory
                +'/{}/Frame_A{}_R{}_C{}_{}.csv'.format(
                    str(self.file),
                    str(self.area),
                    str(self.n_ypos),
                    str(self.n_xpos),
                    str(file_time),
                    ),
                empty_frame, delimiter=',')

    def get_path(self, new_path, new_fname):
        """ Receive path from signal. """
        self.directory = new_path
        self.file = new_fname

    def get_area(self, new_area, new_bool):
        """ Update the size of the sensing area. """
        self.area = new_area
        self.area_hide = new_bool

    def get_pos_x(self, pos_x_cs):
        """ Get the new X-axis position of the sensing area. """
        self.pos_x = int(pos_x_cs)
        self.ipos_x = pos_x_cs

    def get_pos_y(self, pos_y_cs):
        """ Get the new Y-axis position of the sensing area. """
        self.pos_y = int(pos_y_cs)
        self.ipos_y = pos_y_cs

    def acq_mode(self, new_bool):
        """ Change the acquisition mode.
            True  -> Static
            False -> Dynamic
        """
        self.static_mode = new_bool

    def get_pitches(self, n_turnx, n_turny, new_pitchx, new_pitchy):
        """ Get the pitches dimension. """
        self.n_ypos = n_turny
        self.n_xpos = n_turnx
        self.led_pitchy = new_pitchy
        self.led_pitchx = new_pitchx

    def get_leds(self, new_ledx, new_ledy):
        """ Get the pitches dimension. """
        self.led_x0 = new_ledx
        self.led_y0 = new_ledy

    def get_steps(self, mov):
        """ Get the step distances of sensing area. """
        self.move_x, self.move_y = mov

    def get_format(self, new_value):
        """ Update the format of the cmos camera (8/16 bits). """
        self.cmos_format = new_value

    def get_stop(self, new_bool):
        """ Gets the stop flag of the thread. """
        self.stop_thread = new_bool
    
    def get_output_format(self, new_value):
        self.output_file_format = new_value
        print(self.output_file_format)

    @staticmethod
    def create_directory(new_path):
        """ Check if the path exists. If not, it creates a new one. """
        if not os.path.exists(new_path):
            os.mkdir(new_path)

    @staticmethod
    def get_frame_time(t_init, t_end):
        t_frame = int(t_end-t_init)
        ty_res = time.gmtime(t_frame)
        rtime = time.strftime("%H:%M:%S",ty_res)
        return rtime

