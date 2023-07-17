import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ImageDisplay:

    def __init__(self, qlabel):

        self.imageLabel = qlabel
        self.qimage_scaled = QImage()
        self.pixMap = QPixmap()
        self.qimage = ''
        self.zoomX = 1
        self.position = [0,0]
        self.panFlag = True
        self.pressed = False
        self.cntr, self.numImages = -1, -1 #Info de las imagenes que estan.

        self.__connectEvents()


    def __connectEvents(self):
        self.imageLabel.mousePressEvent = self.mousePressAction
        self.imageLabel.mouseMoveEvent = self.mouseMoveAction
        self.imageLabel.mouseReleaseEvent = self.mouseReleaseAction


    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        self.qimage = QImage(imagePath)
        self.pixMap = QPixmap(self.imageLabel.size())
        if not self.qimage.isNull():
            # reset Zoom factor and Pan position
            self.zoomX = 1
            self.position = [0, 0]
            self.qimage_scaled = self.qimage.scaled(self.imageLabel.width(), self.imageLabel.height(), QtCore.Qt.KeepAspectRatio)
            self.update()
        else:
            self.statusbar.showMessage('Cannot open this image! Try another one.', 5000)

    def update(self):
        ''' This function actually draws the scaled image to the imageLabel.
            It will be repeatedly called when zooming or panning.
            So, I tried to include only the necessary operations required just for these tasks. 
        '''
        if not self.qimage_scaled.isNull():
            # check if position is within limits to prevent unbounded panning.
            px, py = self.position
            px = px if (px <= self.qimage_scaled.width() - self.imageLabel.width()) else (self.qimage_scaled.width() - self.imageLabel.width())
            py = py if (py <= self.qimage_scaled.height() - self.imageLabel.height()) else (self.qimage_scaled.height() - self.imageLabel.height())
            px = px if (px >= 0) else 0
            py = py if (py >= 0) else 0
            self.position = (px, py)

            if self.zoomX == 1:
                self.pixMap.fill(QtCore.Qt.white)

            # the act of painting the qpixamp
            painter = QPainter()
            painter.begin(self.pixMap)
            
            painter.drawImage(QtCore.QPoint(0, 0), self.qimage_scaled,
                    QtCore.QRect(round(self.position[0]), round(self.position[1]), round(self.imageLabel.width()), round(self.imageLabel.height())) )
            painter.end()

            self.imageLabel.setPixmap(self.pixMap)
        else:
            pass

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.panFlag:
            self.pressed = QMouseEvent.pos()    # starting point of drag vector
            self.anchor = self.position         # save the pan position when panning starts

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()         # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy    # update pan position using drag vector
            self.update()                                               # show the image with udated pan position

    def mouseReleaseAction(self, QMouseEvent):
        self.pressed = None                                             # clear the starting point of drag vector

    def zoomPlus(self):
        if self.qimage:
            self.zoomX += 1
            px, py = self.position
            px += self.imageLabel.width()/2
            py += self.imageLabel.height()/2
            self.position = (px, py)
            self.qimage_scaled = self.qimage.scaled(self.imageLabel.width() * self.zoomX, self.imageLabel.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def zoomMinus(self):
        if self.qimage:
            if self.zoomX > 1:
                self.zoomX -= 1
                px, py = self.position
                px -= self.imageLabel.width()/2
                py -= self.imageLabel.height()/2
                self.position = (px, py)
                self.qimage_scaled = self.qimage.scaled(self.imageLabel.width() * self.zoomX, self.imageLabel.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
                self.update()

    def resetZoom(self):
        if self.qimage:
            self.zoomX = 1
            self.position = [0, 0]
            self.qimage_scaled = self.qimage.scaled(self.imageLabel.width() * self.zoomX, self.imageLabel.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def nextImg(self):
        if self.cntr < self.numImages -1:
            self.cntr += 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtGui.QMessageBox.warning(self, 'Sorry', 'No more Images!')

    def prevImg(self):
        if self.cntr > 0:
            self.cntr -= 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtGui.QMessageBox.warning(self, 'Sorry', 'No previous Image!')