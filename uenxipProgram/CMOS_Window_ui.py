# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\CMOS_Window_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow_CMOS(object):
    def setupUi(self, MainWindow_CMOS):
        MainWindow_CMOS.setObjectName("MainWindow_CMOS")
        MainWindow_CMOS.resize(429, 338)
        self.centralwidget = QtWidgets.QWidget(MainWindow_CMOS)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.CS_CameraView = QtWidgets.QGraphicsView(self.widget)
        self.CS_CameraView.setMinimumSize(QtCore.QSize(300, 200))
        self.CS_CameraView.setMouseTracking(True)
        self.CS_CameraView.setStatusTip("")
        self.CS_CameraView.setObjectName("CS_CameraView")
        self.gridLayout_2.addWidget(self.CS_CameraView, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        MainWindow_CMOS.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow_CMOS)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 429, 21))
        self.menubar.setObjectName("menubar")
        MainWindow_CMOS.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow_CMOS)
        self.statusbar.setObjectName("statusbar")
        MainWindow_CMOS.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow_CMOS)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_CMOS)

    def retranslateUi(self, MainWindow_CMOS):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_CMOS.setWindowTitle(_translate("MainWindow_CMOS", "CMOS Camera"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow_CMOS = QtWidgets.QMainWindow()
    ui = Ui_MainWindow_CMOS()
    ui.setupUi(MainWindow_CMOS)
    MainWindow_CMOS.show()
    sys.exit(app.exec_())
