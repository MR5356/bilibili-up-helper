import time
import qtawesome
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox
from login import Ui_Dialog
from PyQt5 import QtWidgets, QtCore
import function
import api
import json


class login_UI(Ui_Dialog, QtWidgets.QDialog):
    def __init__(self):
        super(login_UI, self).__init__()
        self.setupUi(self)
        self.m_flag = False
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 窗口始终置顶
        self.pushButton_close.setIcon(qtawesome.icon('fa.close', color='blank'))
        self.pushButton_close.clicked.connect(self.close)
        self.pushButton_login.clicked.connect(self.login)

    def login(self):
        try:
            user = self.lineEdit_user.text()
            passwd = self.lineEdit_passwd.text()
            if user and passwd:
                self.pushButton_login.setText("登录中...")
                self.main_Thread = Main_Thread(user,passwd)
                self.main_Thread.display_signal.connect(self.change_UI)
                self.main_Thread.start()
            else:
                QMessageBox.information(self, '小助手提示', '账号或者密码不能为空')
        except:
            self.pushButton_login.setText("登录")
            QMessageBox.information(self, '小助手提示', '网络故障，请尝试重启客户端')

    def change_UI(self, msm):
        if msm.get("error", 0) != 1:
            ui = function.fun_main(msm)
            ui.show()
            time.sleep(1)
            self.close()
        else:
            self.pushButton_login.setText("登录")
            QMessageBox.information(self, '登陆失败', '账号或密码错误')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:  # 重写Esc键事件
            self.login()
            # self.close()
        elif e.key() == Qt.Key_Enter:
            self.login()


class Main_Thread(QThread):
    display_signal = pyqtSignal(dict)
    def __init__(self, user, passwd):
        super().__init__()
        self.user = user
        self.passwd = passwd

    def run(self):
        app = api.BD()
        login_info = {}
        if app.login(username=self.user, password=self.passwd):
            cookies = app.get_cookies()
            for i in cookies:
                login_info[i] = cookies[i]
            login_info["access_token"] = app.access_token
            login_info["refresh_token"] = app.refresh_token
            login_info["username"] = self.user
            login_info["password"] = self.passwd
            with open("config.json", "w") as f:
                f.write(json.dumps(login_info))
            self.display_signal.emit(cookies)
        else:
            self.display_signal.emit({"error": 1})