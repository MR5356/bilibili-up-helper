# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_top = QtWidgets.QWidget(self.widget)
        self.widget_top.setStyleSheet("QWidget#widget_top{border-image:url(:/images/22332.png);border-top-left-radius:2px;border-top-right-radius:2px;}")
        self.widget_top.setObjectName("widget_top")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_top)
        self.verticalLayout_3.setContentsMargins(5, 0, 5, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.widget_2 = QtWidgets.QWidget(self.widget_top)
        self.widget_2.setMinimumSize(QtCore.QSize(0, 30))
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setMinimumSize(QtCore.QSize(0, 30))
        self.label.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("QLabel{color:white}")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(181, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_close = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_close.setMinimumSize(QtCore.QSize(30, 30))
        self.pushButton_close.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_close.setStyleSheet("QPushButton{background:Transparent;text-align: left;color:white;border:0px solid grey;}QPushButton:hover{background-color:rgba(255,255,255, 0.8);}")
        self.pushButton_close.setText("")
        self.pushButton_close.setObjectName("pushButton_close")
        self.horizontalLayout.addWidget(self.pushButton_close)
        self.verticalLayout_3.addWidget(self.widget_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.widget_top)
        self.widget_down = QtWidgets.QWidget(self.widget)
        self.widget_down.setStyleSheet("QWidget#widget_down{background:#F0F5FF;border-bottom-left-radius:2px;border-bottom-right-radius:2px}")
        self.widget_down.setObjectName("widget_down")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_down)
        self.gridLayout.setContentsMargins(80, 20, 80, 20)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.widget_down)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.lineEdit_user = QtWidgets.QLineEdit(self.widget_down)
        self.lineEdit_user.setStyleSheet("QLineEdit{background:Transparent;border-width:1px;border-radius:0px;font-size:12px;color:black;border-bottom:1px solid gray;}\n"
"       QLineEdit:hover{border-width:1px;border-radius:0px;font-size:12px;color:black;border-bottom:1px solid rgb(70,200,50);}")
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.gridLayout.addWidget(self.lineEdit_user, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget_down)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.lineEdit_passwd = QtWidgets.QLineEdit(self.widget_down)
        self.lineEdit_passwd.setStyleSheet("QLineEdit{background:Transparent;border-width:1px;border-radius:0px;font-size:12px;color:black;border-bottom:1px solid gray;}\n"
"       QLineEdit:hover{border-width:1px;border-radius:0px;font-size:12px;color:black;border-bottom:1px solid rgb(70,200,50);}")
        self.lineEdit_passwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_passwd.setObjectName("lineEdit_passwd")
        self.gridLayout.addWidget(self.lineEdit_passwd, 1, 1, 1, 1)
        self.pushButton_login = QtWidgets.QPushButton(self.widget_down)
        self.pushButton_login.setStyleSheet("QPushButton{background-color:#4D5E92;color:white;}\n"
"QPushButton:hover{background-color:rgba(84,129,189, 0.8);}")
        self.pushButton_login.setObjectName("pushButton_login")
        self.gridLayout.addWidget(self.pushButton_login, 2, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.widget_down)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "哔哩哔哩UP主助手登录"))
        self.pushButton_close.setToolTip(_translate("Dialog", "<html><head/><body><p>关闭</p></body></html>"))
        self.label_2.setText(_translate("Dialog", "账号："))
        self.lineEdit_user.setPlaceholderText(_translate("Dialog", "请输入密码"))
        self.label_3.setText(_translate("Dialog", "密码："))
        self.lineEdit_passwd.setPlaceholderText(_translate("Dialog", "请输入密码"))
        self.pushButton_login.setText(_translate("Dialog", "登录"))
import resources_rc
