# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\NIM_Window_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow_NIM(object):
    def setupUi(self, MainWindow_NIM):
        MainWindow_NIM.setObjectName("MainWindow_NIM")
        MainWindow_NIM.resize(429, 308)
        self.centralwidget = QtWidgets.QWidget(MainWindow_NIM)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.CS_View = QtWidgets.QGraphicsView(self.widget)
        self.CS_View.setMinimumSize(QtCore.QSize(300, 200))
        self.CS_View.setObjectName("CS_View")
        self.gridLayout_2.addWidget(self.CS_View, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        MainWindow_NIM.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow_NIM)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 429, 21))
        self.menubar.setObjectName("menubar")
        MainWindow_NIM.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow_NIM)
        self.statusbar.setObjectName("statusbar")
        MainWindow_NIM.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow_NIM)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_NIM)

    def retranslateUi(self, MainWindow_NIM):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_NIM.setWindowTitle(_translate("MainWindow_NIM", "NIM"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow_NIM = QtWidgets.QMainWindow()
    ui = Ui_MainWindow_NIM()
    ui.setupUi(MainWindow_NIM)
    MainWindow_NIM.show()
    sys.exit(app.exec_())
