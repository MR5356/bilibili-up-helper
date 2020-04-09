from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QCursor, QMovie
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from setting import Ui_Dialog
from PyQt5 import QtWidgets, QtCore, QtGui


class setting_UI(Ui_Dialog, QtWidgets.QDialog):
    mySignal = pyqtSignal(dict)

    def __init__(self):
        super(setting_UI, self).__init__()
        self.setupUi(self)
        self.m_flag = False
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 窗口始终置顶
        self.pushButton_yes.clicked.connect(self.win_close)
        self.pushButton_set.clicked.connect(self.sendChange)
        self.pushButton_no.clicked.connect(self.close)
        self.comboBox_d.currentIndexChanged.connect(self.change_color)
        self.comboBox_z.currentIndexChanged.connect(self.change_pic)
        self.colors = {
            "Can You Feel The Love Tonight": ["#4568DC", "#B06AB3"],
            "Meridian": ["#283c86", "#45a247"],
            "Mello": ["#c0392b", "#8e44ad"],
            "CryStal Clear": ["#159957", "#155799"],
            "Chitty Chitty Bang Bang": ["#007991", "#78ffd6"],
            "Blue Skies": ["#56CCF2", "#2F80ED"],
            "Cinnamint": ["#4AC29A", "#BDFFF3"],
            "Maldives": ["#B2FEFA", "#0ED2F7"],
            "Sha La La": ["#D66D75", "#E29587"],
            "Scooter": ["#36D1DC", "#5B86E5"],
            "Alive": ["#CB356B", "#BD3F32"],
            "Visions of Grandeur": ["#000046", "#1CB5E0"],
            "Sunkist": ["#F2994A", "#F2C94C"],
            "Coal": ["#EB5757", "#000000"],
            "Mini": ["#30E8BF", "#FF8235"],
            "Purplepine": ["#20002c", "#cbb4d4"],
            "Celestial": ["#C33764", "#1D2671"],
            "Pacific Dream": ["#34e89e", "#0f3443"],
            "Venice": ["#6190E8", "#A7BFE8"],
            "Orca": ["#44A08D", "#093637"],
            "Love and Liberty": ["#200122", "#6f0000"],
            "The Blue Lagoon": ["#43C6AC", "#191654"],
            "Under the Lake": ["#093028", "#237A57"],
            "Honey Dew": ["#43C6AC", "#F8FFAE"],
            "Roseanne": ["#FFAFBD", "#ffc3a0"],
            "What lies Beyond": ["#F0F2F0", "#000C40"],
            "Rose Colored Lenses": ["#E8CBC0", "#636FA4"],
            "Cocoaa Ice": ["#c0c0aa", "#1cefff"],
            "Vice City": ["#3494E6", "#EC6EAD"],
            "80's Purple": ["#41295a", "#2F0743"],
            "Cosmic Fusion": ["#ff00cc", "#333399"],
            "Nepal": ["#de6161", "#2657eb"],
        }
        for i in self.colors:
            self.comboBox_d.addItem(i)
        self.pics = {
            "demo1": ":/images/demo1.png",
            "demo2": ":/images/demo2.png",
        }
        for i in self.pics:
            self.comboBox_z.addItem(i)
        self.label_pic.setPixmap(QtGui.QPixmap(":/images/demo1.png"))
        self.label_pic.setScaledContents(True)
        self.radioButton_z.toggled.connect(self.choose_show)
        self.pushButton_choose.hide()
        self.lineEdit_choose.hide()
        self.pushButton_choose.clicked.connect(self.choose_pic)

    def win_close(self):
        self.sendChange()
        self.close()

    def choose_pic(self):
        fileName1, filetype = QFileDialog.getOpenFileName(self,
                                                          "选取文件",
                                                          "C:/",
                                                          "All Pics (*.png *.jpg *.jpeg *.gif)")
        self.lineEdit_choose.setText(fileName1)
        self.gif = QMovie(fileName1)
        self.gif.setScaledSize(QSize(200, 200))
        self.label_pic.setMovie(self.gif)
        self.gif.start()
        # self.label_pic.setPixmap(QtGui.QPixmap(fileName1))
        # self.label_pic.setScaledContents(True)

    def choose_show(self):
        if self.radioButton_z.isChecked():
            self.lineEdit_choose.show()
            self.pushButton_choose.show()

    def change_pic(self):
        if self.radioButton_z.isChecked():
            self.lineEdit_choose.hide()
            self.pushButton_choose.hide()
            self.radioButton_z.toggle()
        pic = self.pics[self.comboBox_z.currentText()]
        self.label_pic.setPixmap(QtGui.QPixmap(pic))
        self.label_pic.setScaledContents(True)

    def change_color(self):
        color = self.colors[self.comboBox_d.currentText()]
        self.widget_main.setStyleSheet(
            "QWidget#widget_main{background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0" + f" {color[0]},stop:1 {color[1]}" + ");border-top-left-radius:2px;border-top-right-radius:2px;}")

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
            pass
            # self.close()
        elif e.key() == Qt.Key_Enter:
            pass

    def sendChange(self):
        color = self.colors[self.comboBox_d.currentText()]
        if self.radioButton_z.isChecked():
            pic = self.lineEdit_choose.text()
            if not pic:
                QMessageBox.information(self, '小助手提示', '图片不能为空')
        else:
            pic = self.pics[self.comboBox_z.currentText()]
        self.mySignal.emit({"color": color, "pic": pic})  # 发射信号