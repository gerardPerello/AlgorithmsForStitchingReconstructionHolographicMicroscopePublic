# -*- coding: utf-8 -*-

# This class allows to configurate and manage the E727_Driver.
#
# Created by: Sergio Moreno
#
# Date: 10-03-2020

import os
import gi
import sys
import time
from datetime import datetime
import numpy as np
import scipy as sy
from collections import namedtuple

gi.require_version("Gst", "1.0")
gi.require_version("Tcam", "0.1")

from gi.repository import Tcam, Gst, GLib, GObject


DeviceInfo = namedtuple("DeviceInfo", "status name identifier connection_type")
CameraProperty = namedtuple("CameraProperty", "status value min max default step type flags category group")

class TIS_Chipscope:
        'The Imaging Source Camera'

        def __init__(self):
                self.cameraUSB2_0 = True
                self.position = None

        def initCamera(self, serial, width, height, framerate, color):
                ''' Constructor
                :param serial: Serial number of the camera to be used.
                :param width: Width of the wanted video format
                :param height: Height of the wanted video format
                :param framerate: Numerator of the frame rate. /1 is added automatically
                :param color: True = 8 bit color, False = 8 bit mono. ToDo: Y16
                :return: none
                '''
                Gst.init(sys.argv)
                self.height = height
                self.width = width
                self.sample = None
                self.samplelocked = False
                self.newsample = False
                self.img_mat = None
                self.ImageCallback = None

                pixelformat = "BGRx"
                if color is False:
                        pixelformat="GRAY16_LE"

                p = "tcambin serial= %s name=source ! queue ! video/x-raw,format=%s,width=%d,height=%d,framerate=%d/1 ! videoconvert ! appsink name=sink" % (serial,pixelformat,width,height,framerate,)
                print(p)
                try:
                        self.pipeline = Gst.parse_launch(p)
                except GLib.Error as error:
                        print("Error creating pipeline: {0}".format(error))
                        raise


                self.pipeline.set_state(Gst.State.READY) 
                self.pipeline.get_state(Gst.CLOCK_TIME_NONE) # Query a pointer to our source, so we can set properties.cd
                self.source = self.pipeline.get_by_name("source")
                self.source.set_property("serial", serial)


                # Query a pointer to the appsink, so we can assign the callback function.
                self.appsink = self.pipeline.get_by_name("sink")
                self.appsink.set_property("max-buffers", 5)              # Unlimited buffers
                self.appsink.set_property("drop",True)                  # Drop old buffers when the buffer queue is filled
                self.appsink.set_property("emit-signals",True)          # Emit new-preroll and new-sample signals
                self.appsink.connect('new-sample', self.on_new_buffer)


        def on_new_buffer(self, appsink):
                self.newsample = True
                if self.samplelocked is False:
                        try:
                                self.sample = appsink.get_property('last-sample')
                                if self.ImageCallback is not None:
                                        self.__convert_sample_to_numpy()
                                        self.ImageCallback(self, *self.ImageCallbackData);

                        except GLib.Error as error:
                                print("Error on_new_buffer pipeline: {0}".format(error))
                                raise
                return False


        def __convert_sample_to_numpy(self):
                ''' Convert a GStreamer sample to a numpy array
                        Sample code from https://gist.github.com/cbenhagen/76b24573fa63e7492fb6#file-gst-appsink-opencv-py-L34
                        The result is in self.img_mat.
                :return:
                '''
                self.samplelocked = True
                buf = self.sample.get_buffer()
                caps = self.sample.get_caps()
                bpp = 4
                dtype = np.uint8
                bla = caps.get_structure(0).get_value('height')
                if( caps.get_structure(0).get_value('format') == "BGRx" ):
                        bpp = 4

                if(caps.get_structure(0).get_value('format') == "GRAY8" ):
                        bpp = 1

                if(caps.get_structure(0).get_value('format') == "GRAY16_LE" ):
                        bpp = 1
                        dtype = np.uint16

                self.img_mat = np.ndarray(
                        (caps.get_structure(0).get_value('height'),
                         caps.get_structure(0).get_value('width'),
                         bpp),
                        buffer=buf.extract_dup(0, buf.get_size()),
                        dtype=dtype)
                self.newsample = False
                self.samplelocked = False

        def Start_pipeline(self):
                try:
                        self.pipeline.set_state(Gst.State.PLAYING)
                        self.pipeline.get_state(Gst.CLOCK_TIME_NONE)

                except GLib.Error as error:
                        print("Error starting pipeline: {0}".format(error))
                        raise

        def Get_image(self):
                return(self.img_mat)

        def Stop_pipeline(self):
                self.pipeline.set_state(Gst.State.PAUSED)
                self.pipeline.set_state(Gst.State.READY)
                self.pipeline.set_state(Gst.State.NULL)

        def getCenterLEDs(self):
                return self.centerLED_NoGlass

        def getCameraModel(self):
                Gst.init([])
                source = Gst.ElementFactory.make('tcambin')
                serials = source.get_device_serials()
                for single_serial in serials:
                    (return_value, model, identifier, connection_type) = source.get_device_info(single_serial)
                    print('Model: {} Serial: {}'.format(model, single_serial))
                return(model, single_serial)

        def getSerial(self):
                Gst.init([])
                pipeline = Gst.parse_launch("tcambin")
                serial = pipeline.get_device_serials()
                print(serial[0])
                return serial[0]

        def Get_value(self, name, atribute):
                (self.ret, self.value,
                 self.min_value, self.max_value,
                 self.default_value, self.step_size,
                 self.value_type, self.flags,
                 self.category, self.group) = self.source.get_tcam_property(name) 
                if atribute == 0: 
                        return(format(self.ret))
                elif atribute == 1:
                        return(format(self.value))
                elif atribute == 2:
                        return(format(self.min_value))
                elif atribute == 3:
                        return(format(self.max_value))
                elif atribute == 4: 
                        return(format(self.default_value))
                elif atribute == 5:
                        return(format(self.step_size))
                elif atribute == 6:
                        return(format(self.value_type))
                elif atribute == 7:
                        return(format(self.flags))
                elif atribute == 8:
                        return(format(self.category))
                elif atribute == 9:
                        return(format(self.group))


        def disAutoExp(self):
                self.source.set_tcam_property('Exposure Auto', False)

        def setProperty(self, propertieString, propertieValue):
                self.source.set_tcam_property(propertieString, propertieValue)

        def setPropertyGst(self, propertieString, propertieValue):
                structure = Gst.Structure.new_from_string("video/x-raw")
                structure.set_value(propertieString, propertieValue)

        def listProperties(self):
                property_names = self.source.get_tcam_property_names() 
                for name in property_names:
                                print("{} has value: {}".format(name,self.Get_value(name, 1)))

        def Save_frames(self, location_file):
                Gst.init([])  # init gstreamer

                serial = None

                pipeline = Gst.parse_launch("tcambin name=source"
#                                     " ! video/x-raw,format=BGRx,width=320,height=240,framerate=60/1"
                                                                        " ! tee name=t"
                                                                        " ! queue"
                                                                        " ! ximagesink"
                                                                        " t."
                                                                        " ! queue"
                                                                        " ! videorate"
                                                                        " ! video/x-raw,format=BGRx,width=320,height=240,framerate=1/1"
                                                                        " ! jpegenc"
                                                                        " ! multifilesink location = {}".format(location_file))
                        # serial is defined, thus make the source open that device
                if serial is not None:
                        camera = self.pipeline.get_by_name("source")
                        camera.set_property("serial", serial)

                pipeline.set_state(Gst.State.PLAYING)

        def wait_for_image(self,timeout):
                ''' Wait for a new image with timeout
                :param timeout: wait time in second, should be a float number
                :return:
                '''
                tries = 10
                while tries > 0 and not self.newsample:
                        tries -= 1
                        time.sleep(float(timeout) / 10.0)

        def Snap_image(self, timeout):
                '''
                Snap an image from stream using a timeout.
                :param timeout: wait time in second, should be a float number. Not used
                :return: bool: True, if we got a new image, otherwise false.
                '''
                if self.ImageCallback is not None:
                        print("Snap_image can not be called, if a callback is set.")
                        return False

                self.wait_for_image(timeout)
                if( self.sample != None and self.newsample == True):
                        self.__convert_sample_to_numpy()
                        return True

                return False

        def Image(self):
                ''' Wait for a new image with timeout
                :param:
                :return: a numpy ndarray with the height and weight of the image
                '''
#                  time.sleep(0.0015)
                while not self.Snap_image(0.0):
                        pass
                capture = self.Get_image()
                return capture

        def captureImage(self, delay):
                if self.Snap_image(delay) is True:
                        frame = self.Get_image()
                        frame_sum = np.sum(frame)
                        return frame_sum

        def grayConversion(self, dataArray, normalized, percentage, area, formatFrame):
                ''' Sets the color limit values of the image reconstructed
                :param dataArray: the 1-D array obtained after chipscope scanning
                :param normalized: selects if the pixels are normalized between fixed limits (False) or it minimum and maximum values (True)
                :param percentage: sets the percentage of the maximum value normalization regarding to the maximum value of the array
                :param area: number to sets the dimension of the array NxN
                :return: the 1-D array in 8-bit format
                '''
                if normalized:
                        vmin=np.amin(dataArray)             # The minimum value of the hole array is set to lower limit
                        normArray = dataArray-vmin
                        vmax=np.amax(normArray)             # The maximum value of the hole array is set to upper limit
                        if vmax == 0:
                                newArray = normArray
                        else:
                                if formatFrame == True:
                                        newArray = (normArray/vmax)*255
                                else:
                                        newArray = (normArray/vmax)*65535
                        if formatFrame == True:
                                qArray8Bit = np.array(newArray, dtype=np.uint8)
                        else:
                                qArray8Bit = np.array(newArray, dtype=np.uint16)
                        return qArray8Bit
                else:
                        if formatFrame == True:
                                vmax = area*area*255*percentage         # The maximum value will be the hole area integrated per the 70% max value of the 8-bit mode (255)
                                dataArray = (dataArray/vmax)*255
                                qArray8Bit = np.array(dataArray, dtype=np.uint8)
                        else:
                                vmax = area*area*65535*percentage       # The maximum value will be the hole area integrated per the 70% max value of the 8-bit mode (255)
                                dataArray = (dataArray/vmax)*65535
                                qArray8Bit = np.array(dataArray, dtype=np.uint16)
                        return qArray8Bit

        def cameraFrame(self, formatFrame):
                ''' Sets the color limit values of the image reconstructed
                :return: the 1-D numpy array in 8-bit format and the 1-D numpy array normalized between its maximum and minimum value  
                '''
                frame = self.Image()

                frame1D = frame[:,:,0]
                if formatFrame:
                        grayFrame = np.array(frame1D, dtype=np.uint8)
                else:
                        grayFrame = np.array(frame1D, dtype=np.uint16)
                return frame1D, grayFrame

        def areaIntegration(self, area):
                ''' Sets the limit values of the area to be integrated
                :param area: number to sets the dimension of the array NxN
                :return: the limit values since the center LED
                '''
                if area%2 == 0:
                        result = area/2
                        roundResult = np.round(result)
                        resMax = roundResult
                        resMin = roundResult
                else:
                        result = area/2
                        roundResult = np.round(result)
                        if roundResult>result:
                                resMax = roundResult
                                resMin = roundResult - 1
                        else:
                                resMax = roundResult + 1
                                resMin = roundResult
                return resMin, resMax

        def getIntensityArea(self, areaIntensity, area, pos_X, pos_Y):
                dataFrame = areaIntensity[pos_Y:pos_Y+area,pos_X:pos_X+area] # Seleccionamos el numero de pixeles a integrar
                sumArea = np.sum(dataFrame)
                return sumArea

        def get_coords_rect(self, area):
                rMin, rMax = self.areaIntegration(area)
                return rMin, rMax

        def set_dynamic_range(self, data_array, high_contrast, pctge, sens_area, cmos_format):
            """ Set the dynamic range of the acquisition.
                @param high_contrast: False  -> Default dynamic range (0 to 255)
                                      True   -> Adjusted dynamic range (min to max values)
            """
            nim_gray = self.grayConversion(dataArray=data_array,
                                                   normalized=high_contrast,
                                                   percentage=pctge,
                                                   area=sens_area,
                                                   formatFrame=cmos_format)
            return (nim_gray)