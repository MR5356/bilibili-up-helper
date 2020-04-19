import time
import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon, QCursor, QMovie
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QApplication, QAction, qApp, QDesktopWidget, QWidget, \
    QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QListWidgetItem
from windows import Ui_MainWindow
from setting_func import setting_UI
import qtawesome
import api
import json
import os
import resources_rc

def pic_cache(url):
    if not os.path.exists("cache"):
        os.mkdir("cache")
    if os.path.exists(f"cache/{url.split('/')[-1]}"):
        pass
    else:
        pic = requests.get(url).content
        try:
            with open(f"cache/{url.split('/')[-1]}", "wb") as f:
                f.write(pic)
        except Exception as e:
            print(e)
            qApp.quit()
    return f"cache/{url.split('/')[-1]}"

class fun_main(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, cookies):
        super(fun_main, self).__init__()

        # 版本控制
        self.version = 1.1

        # self.load_data()
        self.setupUi(self)
        self.setWindowOpacity(1)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 主窗口透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 窗口始终置顶
        # self.setWindowFlag(Qt.Tool)  # 隐藏任务栏图标
        self.setWindowIcon(QIcon(':/images/logo.ico'))
        self.init_systray()
        self.set_win_center()
        self.signal_on_button()
        self.set_icon()
        self.getSettingSignal({})
        self.m_flag = False
        self.notify_flag = False
        self.notify_enable = True
        self.cookies = cookies
        self.video_url = {}
        self.article_url = {}
        self.reply_url = {}
        self.danmaku_url = {}
        self.main_thread()
        self.notify_thread()
        self.video_thread()
        self.article_thread()
        self.reply_thread()
        self.danmaku_thread()
        self.update_thread()

    def Setting(self):
        my = setting_UI()
        my.mySignal.connect(self.getSettingSignal)
        my.exec_()

    def init_UI(self):
        try:
            with open("UI_config.json", "r") as f:
                msm = json.loads(f.readline())
            self.getSettingSignal(msm)
        except:
            pass

    def getSettingSignal(self, msm):
        if not msm:
            try:
                with open("UI_config.json", "r") as f:
                    msm = json.loads(f.readline())
            except Exception as e:
                print(e)
                msm = {'color': ['#4568DC', '#B06AB3'], 'pic': ':/images/demo1.png'}
        else:
            with open("UI_config.json", "w") as f:
                f.write(json.dumps(msm))
        # print(msm)
        self.gif = QMovie(msm.get("pic"))
        self.gif.setScaledSize(QSize(200, 200))
        self.label_left_b1.setMovie(self.gif)
        self.gif.start()
        # self.label_left_b1.setPixmap(QtGui.QPixmap(msm.get("pic")))
        # self.label_left_b1.setScaledContents(True)
        # self.label_left_b1.setPixmap(QtGui.QPixmap("images/22332.png"))
        self.widget_top.setStyleSheet(
            "QWidget#widget_top{background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0" + f" {msm.get('color')[0]},stop:1 {msm.get('color')[1]})" + ";border-top-left-radius:2px;border-top-right-radius:2px;}")
        self.progressBar.setStyleSheet(
            "QProgressBar::chunk{background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0" + f" {msm.get('color')[0]},stop:1 {msm.get('color')[1]})" + ";}")

    def signal_on_button(self):
        self.pushButton_close.clicked.connect(self.win_close)
        self.pushButton_min.clicked.connect(self.showMinimized)
        self.pushButton_feedback.clicked.connect(lambda: self.open_browser("https://www.toodo.fun"))
        self.pushButton_notify.clicked.connect(self.notify_clicked)
        self.listWidget.itemClicked.connect(self.vitem_clicked)
        self.listWidget_article.itemClicked.connect(self.aitem_clicked)
        self.listWidget_reply.itemClicked.connect(self.ritem_clicked)
        self.listWidget_danmaku.itemClicked.connect(self.ditem_clicked)
        self.pushButton_vrenew.clicked.connect(self.video_thread)
        self.pushButton_arenew.clicked.connect(self.article_thread)
        self.pushButton_rrenew.clicked.connect(self.reply_thread)
        self.pushButton_drenew.clicked.connect(self.danmaku_thread)
        self.pushButton_setting.clicked.connect(self.Setting)
        self.pushButton_max.clicked.connect(self.window_max)

    def set_icon(self):
        self.pushButton_notify.setIcon(qtawesome.icon('fa.bell', color="white"))
        self.pushButton_feedback.setIcon(qtawesome.icon('fa.envelope-o', color="white"))
        self.pushButton_min.setIcon(qtawesome.icon('fa.window-minimize', color='white'))
        self.pushButton_close.setIcon(qtawesome.icon('fa.close', color='white'))
        # self.pushButton_coin.setIcon(qtawesome.icon('fa.bold', color='blank'))
        # self.pushButton_balance.setIcon(qtawesome.icon('fa.flash', color='blank'))
        # self.pushButton_reply.setIcon(qtawesome.icon('fa.reply', color='blank'))
        # self.pushButton_like.setIcon(qtawesome.icon('fa.thumbs-up', color='blank'))
        # self.pushButton_sysnotify.setIcon(qtawesome.icon('fa.bell', color='blank'))
        self.pushButton_vrenew.setIcon(qtawesome.icon('fa.refresh', color='blank'))
        self.pushButton_arenew.setIcon(qtawesome.icon('fa.refresh', color='blank'))
        self.pushButton_rrenew.setIcon(qtawesome.icon('fa.refresh', color="blank"))
        self.pushButton_drenew.setIcon(qtawesome.icon('fa.refresh', color="blank"))
        self.pushButton_setting.setIcon(qtawesome.icon('fa.cog', color='white'))
        self.pushButton_max.setIcon(qtawesome.icon('fa.window-maximize', color='white'))

    def init_systray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(':/images/logo.ico'))
        self.tray.setToolTip("哔哩哔哩UP主助手")
        self.tray.activated.connect(self.tray_act)  # 设置托盘点击事件处理函数
        self.tray_menu = QMenu(QApplication.desktop())  # 创建菜单
        self.tray_menu.setWindowFlags(self.tray_menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.tray_menu.setStyleSheet('''QMenu::item {border-radius: 4px;padding: 8px 48px 8px 16px;background-color: transparent;}
                                        QMenu::item:selected { background-color:rgb(240,245,255);}   
        ''')
        self.NicknameAction = QAction('请叫我雯子小姐的小爷', self)
        self.tray_coin = QAction("硬币：0")
        self.tray_balance = QAction("电池：0")
        self.tray_follower = QAction("粉丝：0")
        self.LogoutAction = QAction('退出登录', self)
        self.FeedbackAction = QAction("反馈与建议", self)
        self.RestoreAction = QAction('显示主界面', self)  # 添加一级菜单动作选项(还原主窗口)
        self.UpdateAction = QAction('检查更新', self)
        self.QuitAction = QAction('退出程序', self)  # 添加一级菜单动作选项(退出程序)
        self.RestoreAction.triggered.connect(self.show)
        self.QuitAction.triggered.connect(self.close)
        self.LogoutAction.triggered.connect(self.logout)
        self.FeedbackAction.triggered.connect(lambda: self.open_browser("https://www.toodo.fun"))
        self.UpdateAction.triggered.connect(lambda: self.update_thread(auto=False))
        self.tray_coin.setIcon(qtawesome.icon('fa.btc', color="blank"))
        self.tray_balance.setIcon(qtawesome.icon('fa.flash', color='blank'))
        self.tray_follower.setIcon(qtawesome.icon('fa.user', color='blank'))
        self.LogoutAction.setIcon(qtawesome.icon('fa.sign-out', color="blank"))
        self.FeedbackAction.setIcon(qtawesome.icon('fa.envelope-o', color="blank"))
        self.RestoreAction.setIcon(qtawesome.icon('fa.home', color='blank'))
        self.UpdateAction.setIcon(qtawesome.icon('fa.refresh', color='blank'))
        self.QuitAction.setIcon(qtawesome.icon('fa.sign-out', color='blank'))
        self.tray_menu.addAction(self.NicknameAction)
        self.tray_menu.addAction(self.tray_coin)
        self.tray_menu.addAction(self.tray_balance)
        self.tray_menu.addAction(self.tray_follower)
        self.tray_menu.addAction(self.LogoutAction)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.FeedbackAction)
        self.tray_menu.addAction(self.RestoreAction)  # 为菜单添加动作
        self.tray_menu.addAction(self.UpdateAction)
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu)  # 设置系统托盘菜单
        self.tray.messageClicked.connect(self.notify_clicked)
        self.tray.show()

        # self.tray.showMessage('Hello', '我藏好了', icon=0)  # 参数1：标题 参数2：内容 参数3：图标（0没有图标 1信息图标 2警告图标 3错误图标），0还是有一个小图标

    def tray_act(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.show()

    def window_max(self):
        if self.isMaximized():
            self.showNormal()
            self.pushButton_max.setToolTip("窗口最大化")
        else:
            self.showMaximized()
            self.pushButton_max.setToolTip("恢复默认大小")

    def logout(self):
        with open("config.json", "w") as f:
            f.write("{}")
        QMessageBox.information(self, '小助手提示', '退出登录成功，请重新登录')
        self.tray.hide()
        self.destroy()
        qApp.exit(101)

    def set_win_center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def win_close(self):
        self.hide()
        # self.tray.showMessage('Hello', '我藏好了', icon=0)

    def open_browser(self, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def notify_clicked(self):
        self.notify_flag = False
        self.pushButton_notify.setText("通知：你有 0 条未读消息")
        self.open_browser("https://message.bilibili.com/#/")

    def main_thread(self):
        try:
            self.pushButton_nickname.setText("正在获取信息中...")
            self.main_Thread = Main_Thread(self.cookies)
            self.main_Thread.display_signal.connect(self.change_UI)
            self.main_Thread.start()
        except Exception as e:
            print(e)
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def change_UI(self, msm):
        # print(f"UI: {msm}")
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '登录状态失效',
                                                   "请重新登录",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
        else:
            self.pushButton_nickname.setText(msm["nickname"])
            self.NicknameAction.setText(msm["nickname"])
            try:
                self.pushButton_nickname.clicked.disconnect()
            except Exception as e:
                print(f"clike: {e}")
                pass
            self.pushButton_nickname.clicked.connect(
                lambda: self.open_browser(f"https://space.bilibili.com/{msm['mid']}"))
            face = pic_cache(msm['face'])
            try:
                self.label_face.setPixmap(QPixmap(face))
            except Exception as e:
                print(f"face_Main: {e}")
                img = QImage.fromData(
                         requests.get(msm["face"]).content)
                self.label_face.setPixmap(QPixmap.fromImage(img))
            self.label_face.setScaledContents(True)
            self.label_level.setText(f"等级 {msm['level']}")
            self.label_exp.setText(f'{msm["experience"]["current"]}/{msm["experience"]["next"]}')
            self.progressBar.setValue(int(msm["experience"]["current"] / msm["experience"]["next"] * 100))
            self.pushButton_coin.setText(f"硬币：{msm['coins']}")
            self.pushButton_balance.setText(f"电池：{msm['balance']}")
            self.label_follower.setText(f"粉丝\n{msm['follower']}")
            self.tray_coin.setText(f"硬币：{msm['coins']}")
            self.tray_balance.setText(f"电池：{msm['balance']}")
            self.tray_follower.setText(f"粉丝：{msm['follower']}")
            self.label_like.setText(f"点赞\n{msm['video']['like']}")
            self.label_view.setText(f"播放\n{msm['video']['view']}")
            self.label_reply.setText(f"评论\n{msm['video']['reply']}")
            self.label_danmaku.setText(f"弹幕\n{msm['video']['danmaku']}")
            self.label_share.setText(f"分享\n{msm['video']['share']}")
            self.label_favorite.setText(f"收藏\n{msm['video']['favorite']}")
            self.label_coin.setText(f"投币\n{msm['video']['coin']}")
            self.label_artview.setText(f"阅读量\n{msm['article']['view']}")
            self.label_artlike.setText(f"点赞\n{msm['article']['like']}")
            self.label_artcoin.setText(f"投币\n{msm['article']['coin']}")
            self.label_artreply.setText(f"评论\n{msm['article']['reply']}")
            self.label_artshare.setText(f"分享\n{msm['article']['share']}")
            self.label_artfav.setText(f"收藏\n{msm['article']['favorite']}")
            self.label_creative.setText(f"创作力\n{msm['rating']['creative']}")
            self.label_influence.setText(f"影响力\n{msm['rating']['influence']}")
            self.label_credit.setText(f"信用分\n{msm['rating']['credit']}")
            # self.label_balance.setText(f"充电\n{msm['balance']}")
            print("成功刷新UI")

    def notify_thread(self):
        try:
            self.notify_Thread = Notify_Thread(self.cookies)
            self.notify_Thread.display_signal.connect(self.Notify_UI)
            self.notify_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Notify_UI(self, msm):
        # print(f"notify: {msm}")
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '系统通知线程已经停止',
                                                   "系统通知模块停止了工作(不影响主程序)，是否重启软件尝试恢复",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                pass
        else:
            notify = "通知：你有"
            tray_notify = "哔哩哔哩UP主助手\n"
            if msm.get("at") != 0:
                notify += f" {msm.get('at')} 条@你的消息 "
                tray_notify += f"@你的：{msm.get('at')}\n"
                if not self.notify_flag and self.notify_enable:
                    self.notify_flag = True
                    self.tray.showMessage('新的@消息', f"你收到了 {msm.get('at')} 条@消息", icon=1)
            if msm.get("chat") != 0:
                notify += f" {msm.get('chat')} 条聊天消息 "
                tray_notify += f"私信消息：{msm.get('chat')}\n"
                if not self.notify_flag and self.notify_enable:
                    self.notify_flag = True
                    self.tray.showMessage('新的聊天消息', f"你收到了 {msm.get('chat')} 条新的聊天消息", icon=1)
            if msm.get("reply") != 0:
                notify += f" {msm.get('reply')} 条回复你的消息 "
                tray_notify += f"回复消息：{msm.get('reply')}\n"
                if not self.notify_flag and self.notify_enable:
                    self.notify_flag = True
                    self.tray.showMessage('新的回复', f"你收到了 {msm.get('reply')} 条新的回复", icon=1)
            if msm.get("sys_msg") != 0:
                notify += f" {msm.get('sys_msg')} 条系统通知 "
                tray_notify += f"系统通知：{msm.get('sys_msg')}\n"
                if not self.notify_flag and self.notify_enable:
                    self.notify_flag = True
                    self.tray.showMessage("收到一条系统通知", f"你收到了 {msm.get('sys_msg')} 条新的系统通知", icon=1)
            if msm.get("like") != 0:
                notify += f" {msm.get('like')} 个新收到的赞 "
                tray_notify += f"收到的赞：{msm.get('like')}"
                if not self.notify_flag and self.notify_enable:
                    self.notify_flag = True
                    # self.tray.showMessage('新的点赞', f"你新收到了 {msm.get('like')} 个赞", icon=1)
            if msm.get("at") == msm.get("chat") == msm.get("like") == msm.get("reply") == msm.get("sys_msg") == 0:
                notify += f" 0 条未读消息"
                tray_notify += "没有未读消息"
            self.pushButton_notify.setText(notify)
            self.tray.setToolTip(tray_notify)
            print("成功刷新Notify")

    def video_thread(self):
        try:
            self.pushButton_vrenew.setText(f"获取中...")
            self.video_Thread = Video_Thread(self.cookies)
            self.video_Thread.display_signal.connect(self.Video_UI)
            self.video_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Video_UI(self, msm):
        # print(f"video: {msm}")
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '视频稿件线程出错',
                                                   "视频稿件模块停止了工作(不影响主程序)，是否重启软件尝试恢复",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                pass
        else:
            a = time.time()
            try:
                self.listWidget.clear()
            except Exception as e:
                print(e)
                pass
            if msm["video_url"]:
                self.video_url = msm["video_url"]
                self.label_vtot.setText(f"共有 {len(self.video_url)} 个视频稿件")
                for i in msm["widgets"]:
                    item = QListWidgetItem()  # 创建QListWidgetItem对象
                    item.setSizeHint(QSize(200, 100))  # 设置QListWidgetItem大小
                    QApplication.processEvents()
                    widget = self.get_item_wight(i)  # 调用上面的函数获取对应
                    QApplication.processEvents()
                    self.listWidget.addItem(item)  # 添加item
                    self.listWidget.setItemWidget(item, widget)
            else:
                self.label_vtot.setText(f"暂时没有视频稿件")
            self.pushButton_vrenew.setText("")

    def article_thread(self):
        try:
            self.pushButton_arenew.setText(f"获取中...")
            self.article_Thread = Article_Thread(self.cookies)
            self.article_Thread.display_signal.connect(self.Article_UI)
            self.article_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Article_UI(self, msm):
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '专栏文章线程出错',
                                                   "已经停止使用了专栏文章模块(不影响主程序)，是否重启软件尝试恢复",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                pass
        else:
            try:
                self.listWidget_article.clear()
            except Exception as e:
                print(e)
                pass
            if msm["article_url"]:
                self.article_url = msm["article_url"]
                self.label_atot.setText(f"共有 {len(self.article_url)} 个专栏文章")
                for i in msm["widgets"]:
                    item = QListWidgetItem()  # 创建QListWidgetItem对象
                    item.setSizeHint(QSize(200, 100))  # 设置QListWidgetItem大小
                    QApplication.processEvents()
                    widget = self.get_item_wight(i)  # 调用上面的函数获取对应
                    QApplication.processEvents()
                    self.listWidget_article.addItem(item)  # 添加item
                    self.listWidget_article.setItemWidget(item, widget)
            else:
                self.label_atot.setText(f"暂时没有专栏文章")
            self.pushButton_arenew.setText("")

    def reply_thread(self):
        try:
            self.pushButton_rrenew.setText(f"获取中...")
            self.reply_Thread = Reply_Thread(self.cookies)
            self.reply_Thread.display_signal.connect(self.Reply_UI)
            self.reply_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Reply_UI(self, msm):
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '评论线程出错',
                                                   "已经停止使用评论功能(不影响主程序)，是否重启软件尝试恢复",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                pass
        else:
            try:
                self.listWidget_reply.clear()
            except Exception as e:
                print(e)
                pass
            if msm["reply_url"]:
                self.reply_url = msm["reply_url"]
                self.label_rtot.setText(f"共有 {len(self.reply_url)} 条评论（如果评论数大于100，则只显示最新的100条记录）")
                # self.label_rtot.setText(f"共有 {len(self.reply_url)} 条弹幕（如果评论数大于100，则只显示最新的100条记录）") if len(self.reply_url) > 500 else self.label_rtot.setText(f"共有 {len(self.reply_url)} 条评论")
                for i in msm["widgets"]:
                    item = QListWidgetItem()  # 创建QListWidgetItem对象
                    QApplication.processEvents()
                    widget = self.get_item_wight_reply(i)  # 调用上面的函数获取对应
                    item.setSizeHint(QSize(widget.width(), widget.height()))  # 设置QListWidgetItem大小与widget相同
                    QApplication.processEvents()
                    self.listWidget_reply.addItem(item)  # 添加item
                    self.listWidget_reply.setItemWidget(item, widget)
            else:
                self.label_rtot.setText(f"暂时没有评论")
            self.pushButton_rrenew.setText("")

    def danmaku_thread(self):
        try:
            self.pushButton_drenew.setText(f"获取中...")
            self.danmaku_Thread = Danmaku_Thread(self.cookies)
            self.danmaku_Thread.display_signal.connect(self.Danmaku_UI)
            self.danmaku_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Danmaku_UI(self, msm):
        if msm.get("error", 0) == 1:
            reply = QtWidgets.QMessageBox.question(self,
                                                   '评论线程出错',
                                                   "已经停止使用评论功能(不影响主程序)，是否重启软件尝试恢复",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.tray.hide()
                self.destroy()
                qApp.exit(101)
            else:
                pass
        else:
            try:
                self.listWidget_danmaku.clear()
            except Exception as e:
                print(e)
                pass
            if msm["danmaku_url"]:
                self.danmaku_url = msm["danmaku_url"]
                self.label_dtot.setText(f"共有 {len(self.danmaku_url)} 条评论（如果弹幕数大于500，则只显示最新的500条记录）")
                # self.label_dtot.setText(f"共有 {len(self.danmaku_url)} 条弹幕（如果弹幕数大于500，则只显示最新的500条记录）") if len(self.danmaku_url) > 500 else self.label_dtot.setText(f"共有 {len(self.danmaku_url)} 条弹幕")
                for i in msm["widgets"]:
                    item = QListWidgetItem()  # 创建QListWidgetItem对象
                    QApplication.processEvents()
                    widget = self.get_item_wight_danmaku(i)  # 调用上面的函数获取对应
                    item.setSizeHint(QSize(widget.width(), widget.height()))  # 设置QListWidgetItem大小与widget相同
                    QApplication.processEvents()
                    self.listWidget_danmaku.addItem(item)  # 添加item
                    self.listWidget_danmaku.setItemWidget(item, widget)
            else:
                self.label_dtot.setText(f"暂时没有评论")
            self.pushButton_drenew.setText("")

    def update_thread(self, auto=True):
        try:
            self.update_Thread = Update_Thread(auto)
            self.update_Thread.display_signal.connect(self.Update_UI)
            self.update_Thread.start()
        except:
            QMessageBox.information(self, '小助手提示', '程序运行异常，请确定网络连接是否正常，然后尝试重启客户端，如问题还未解决，请点击反馈按钮留言')

    def Update_UI(self, msm):
        if msm.get("net", 1) == 0:
            if msm["Version"] == False:
                QMessageBox.information(self, '小助手提示', '连接更新服务器失败')
            else:
                pass
        else:
            if msm['Version'] == self.version:
                if msm["auto"] == False:
                    QMessageBox.information(self, '小助手提示', '已经是最新版本')
                else:
                    pass
            else:
                reply = QtWidgets.QMessageBox.question(self,
                                                       '发现新版本，是否立即更新',
                                                       f'发现新版本：V{msm["Version"]}，更新内容如下：\n\n{msm["Update_des"]}\n\n是否立即更新?',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.open_browser(msm["Update_url"])
                else:
                    pass

    # 视频稿件部分
    def get_item_wight(self, msms):
        # 读取属性
        face = msms["face"]
        tag = str(msms["tag"])
        title = str(msms["title"])
        btn_view = str(msms["view"])
        btn_reply = str(msms["reply"])
        btn_danmaku = msms.get("danmaku", -1)  # str(msms["danmaku"])
        btn_coin = str(msms["coin"])
        btn_favorite = str(msms["favorite"])
        btn_like = str(msms["like"])
        btn_share = str(msms["share"])
        create_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msms["create_time"])))
        state_panel = msms.get("state_panel", 0)
        wight = QWidget()

        wight.setObjectName("widget_main")
        wight.setStyleSheet("QWidget#widget_main{background:Transparent;border:0px solid grey;}QWidget#widget_main:hover{background-color:rgba(240,245,255,0.8);}")
        wight.setMinimumSize(QtCore.QSize(0, 100))
        wight.setMaximumSize(QtCore.QSize(16777215, 100))
        layout_main = QHBoxLayout()
        layout_main.setContentsMargins(11, 0, 11, 0)
        layout_main.setSpacing(6)
        label_face = QLabel()
        label_face.setFixedSize(120, 76)
        try:
            img = QImage.fromData(face)
            label_face.setPixmap(QPixmap.fromImage(img))
        except:
            label_face.setPixmap(QPixmap(face))
        label_face.setScaledContents(True)
        layout_right = QVBoxLayout()
        layout_right_down = QHBoxLayout()  # 右下的横向布局
        pushButton_view = QtWidgets.QPushButton()
        pushButton_view.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_view.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_view.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_view.setIcon(qtawesome.icon('fa.play-circle', color='#99A2AA'))
        pushButton_view.setText(btn_view)
        pushButton_reply = QtWidgets.QPushButton()
        pushButton_reply.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_reply.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_reply.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_reply.setIcon(qtawesome.icon('fa.comment', color="#99A2AA"))
        pushButton_reply.setText(btn_reply)
        pushButton_coin = QtWidgets.QPushButton()
        pushButton_coin.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_coin.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_coin.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_coin.setIcon(qtawesome.icon('fa.btc', color='#99A2AA'))
        pushButton_coin.setText(btn_coin)
        pushButton_favorite = QtWidgets.QPushButton()
        pushButton_favorite.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_favorite.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_favorite.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_favorite.setIcon(qtawesome.icon('fa.star', color='#99A2AA'))
        pushButton_favorite.setText(btn_favorite)
        pushButton_like = QtWidgets.QPushButton()
        pushButton_like.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_like.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_like.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_like.setIcon(qtawesome.icon('fa.thumbs-up', color='#99A2AA'))
        pushButton_like.setText(btn_like)
        pushButton_share = QtWidgets.QPushButton()
        pushButton_share.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_share.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_share.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_share.setIcon(qtawesome.icon('fa.share', color='#99A2AA'))
        pushButton_share.setText(btn_share)
        layout_right_down.addWidget(pushButton_view)
        if btn_danmaku != -1:
            pushButton_danmaku = QtWidgets.QPushButton()
            pushButton_danmaku.setMinimumSize(QtCore.QSize(50, 30))
            pushButton_danmaku.setMaximumSize(QtCore.QSize(80, 30))
            pushButton_danmaku.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
            pushButton_danmaku.setIcon(qtawesome.icon('fa.list-alt', color='#99A2AA'))
            pushButton_danmaku.setText(str(btn_danmaku))
            layout_right_down.addWidget(pushButton_danmaku)
        layout_right_down.addWidget(pushButton_reply)
        layout_right_down.addWidget(pushButton_coin)
        layout_right_down.addWidget(pushButton_favorite)
        layout_right_down.addWidget(pushButton_like)
        layout_right_down.addWidget(pushButton_share)
        layout_right_down.addWidget(QLabel(create_time))
        if state_panel == 1:
            label_state_panel = QtWidgets.QLabel()
            label_state_panel.setStyleSheet("QLabel{background:Transparent;border:0px solid grey;color:#5168D7}")
            label_state_panel.setMinimumSize(QtCore.QSize(30, 30))
            label_state_panel.setMaximumSize(QtCore.QSize(50, 30))
            # label_state_panel.setMaximumHeight(20)
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(7)
            label_state_panel.setFont(font)
            label_state_panel.setText("审稿中")
            layout_right_down.addWidget(label_state_panel)
        elif state_panel != 0:
            label_state_panel = QtWidgets.QLabel()
            label_state_panel.setStyleSheet("QLabel{background:Transparent;border:0px solid grey;color:red}")
            label_state_panel.setMinimumSize(QtCore.QSize(30, 30))
            label_state_panel.setMaximumSize(QtCore.QSize(50, 30))
            # label_state_panel.setMaximumHeight(20)
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(9)
            label_state_panel.setFont(font)
            label_state_panel.setText("已锁定")
            layout_right_down.addWidget(label_state_panel)
        layout_right_up = QHBoxLayout()  # 右下的横向布局
        label_tag = QtWidgets.QLabel()
        label_tag.setAlignment(QtCore.Qt.AlignCenter)
        label_tag.setStyleSheet("QLabel{background:Transparent;border:1px solid grey;border-radius:5px;}")
        label_tag.setMaximumHeight(20)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(7)
        label_tag.setFont(font)
        label_tag.setText(tag)
        layout_right_up.addWidget(label_tag)
        label_title = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(50)
        label_title.setFont(font)
        label_title.setText(title)
        layout_right_up.addWidget(label_title)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout_right_up.addItem(spacerItem)
        layout_main.addWidget(label_face)  # 最左边的头像
        layout_right.addLayout(layout_right_up)  # 右边的纵向布局
        layout_right.addLayout(layout_right_down)  # 右下角横向布局
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        return wight  # 返回wight

    def get_item_wight_reply(self, msms):
        title = msms["title"]
        id = msms['id']
        like = msms["like"]
        face = msms["face"]
        floor = msms["floor"]
        replier = msms['replier']
        message = msms['message']
        ctime = msms['ctime']
        # ctime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msms["ctime"])))
        parent = msms['parent']

        wight = QWidget()
        wight.setObjectName("widget_main")
        wight.setStyleSheet("QWidget#widget_main{background:Transparent;border:0px solid grey;}QWidget#widget_main:hover{background-color:rgba(240,245,255,0.8);}")
        layout_main = QHBoxLayout()
        layout_main.setContentsMargins(11, 0, 11, 0)
        layout_main.setSpacing(6)
        label_face = QLabel()
        label_face.setFixedSize(120, 76)
        try:
            img = QImage.fromData(face)
            label_face.setPixmap(QPixmap.fromImage(img))
        except:
            label_face.setPixmap(QPixmap(face))
        label_face.setScaledContents(True)

        layout_right = QVBoxLayout()

        layout_right_down = QHBoxLayout()  # 右下的横向布局
        pushButton_like = QtWidgets.QPushButton()
        pushButton_like.setMinimumSize(QtCore.QSize(50, 30))
        pushButton_like.setMaximumSize(QtCore.QSize(80, 30))
        pushButton_like.setStyleSheet("QPushButton{background:Transparent;border:0px solid grey;}")
        pushButton_like.setIcon(qtawesome.icon('fa.thumbs-up', color='#99A2AA'))
        pushButton_like.setText(f"{like}")
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        label_time = QLabel(f"{ctime}")
        label_time.setFont(font)
        layout_right_down.addWidget(label_time)
        layout_right_down.addWidget(pushButton_like)

        layout_right_middle = QVBoxLayout()  # 右下的横向布局
        if parent == 1:
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(9)
            label_reply = QLabel(f"{message}")
            label_reply.setFont(font)
            label_reply.setStyleSheet("QLabel{color:Gray}")
            layout_right_middle.addWidget(label_reply)
            label_parent = QLabel(f"{msms['parent_name']}的评论: {msms['parent_message']}")
            label_parent.setStyleSheet("QLabel{color:DarkGray}")
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(8)
            label_parent.setFont(font)
            layout_right_middle.addWidget(label_parent)
            count = len(msms['parent_message'].split('\n')) + len(msms['message'].split('\n')) + 2
        else:
            count = len(msms['message'].split('\n')) + 2
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(9)
            label_reply = QLabel(f"{message}")
            label_reply.setFont(font)
            label_reply.setStyleSheet("QLabel{color:Gray}")
            layout_right_middle.addWidget(label_reply)
            # layout_right_middle.addWidget(QLabel(f"{message}"))
        wight.setMinimumSize(QtCore.QSize(0, 10))
        wight.setMaximumSize(QtCore.QSize(16777215, count * 30))

        layout_right_up = QHBoxLayout()  # 右上的横向布局
        label_title = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        label_title.setFont(font)
        if parent == 0:
            label_title.setText(f"{replier} 在 #{floor} 的评论")
        else:
            label_title.setText(f"{replier} 回复 {msms['parent_name']} 在 #{floor} 的评论")
        layout_right_up.addWidget(label_title)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout_right_up.addItem(spacerItem)
        layout_right.addLayout(layout_right_up)  # 右边的纵向布局
        layout_right.addLayout(layout_right_middle)
        layout_right.addLayout(layout_right_down)  # 右下角横向布局
        layout_main.addWidget(label_face)
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        return wight  # 返回wight

    def get_item_wight_danmaku(self, msms):
        title = msms["title"]
        id = msms['id']
        message = msms['message']
        ctime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msms["ctime"])))

        wight = QWidget()
        wight.setObjectName("widget_main")
        wight.setStyleSheet(
            "QWidget#widget_main{background:Transparent;border:0px solid grey;}QWidget#widget_main:hover{background-color:rgba(240,245,255,0.8);}")
        wight.setMinimumSize(QtCore.QSize(0, 10))
        wight.setMaximumSize(QtCore.QSize(16777215, 100))
        layout_main = QHBoxLayout()
        layout_main.setContentsMargins(11, 0, 11, 0)
        layout_main.setSpacing(6)
        layout_right = QVBoxLayout()
        layout_right_up = QHBoxLayout()  # 右下的横向布局
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(7)
        label_title = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(50)
        label_title.setFont(font)
        label_title.setText(f"{ctime}：{message}")
        layout_right_middle = QVBoxLayout()  # 右下的横向布局
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        label_reply = QLabel(f"来自于：{title}")
        label_reply.setFont(font)
        label_reply.setStyleSheet("QLabel{color:Gray}")
        layout_right_middle.addWidget(label_reply)
        layout_right_up.addWidget(label_title)
        layout_right.addLayout(layout_right_up)  # 右边的纵向布局
        layout_right.addLayout(layout_right_middle)  # 右下角横向布局
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        return wight  # 返回wight

    def vitem_clicked(self, item):
        self.open_browser(self.video_url[self.listWidget.currentIndex().row()])

    def aitem_clicked(self, item):
        self.open_browser(self.article_url[self.listWidget_article.currentIndex().row()])

    def ritem_clicked(self, item):
        self.open_browser(self.reply_url[self.listWidget_reply.currentIndex().row()])

    def ditem_clicked(self, item):
        self.open_browser(self.danmaku_url[self.listWidget_danmaku.currentIndex().row()])

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

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self,
                                               '哔哩哔哩UP主助手',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.tray.hide()
            qApp.quit()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:  # 重写Esc键事件
            self.close()


class Main_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                while True:
                    for _ in range(5):
                        if app.get_main_info():
                            self.display_signal.emit(app.main_info)
                            break
                    time.sleep(120)
            else:
                self.display_signal.emit({"error": 1})
        except:
            self.display_signal.emit({"error": 1})


class Notify_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                while True:
                    for _ in range(5):
                        if app.get_notify():
                            self.display_signal.emit(app.notify)
                            break
                    time.sleep(30)
            else:
                self.display_signal.emit({"error": 1})
        except:
            self.display_signal.emit({"error": 1})


class Video_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                for _ in range(5):
                    if app.get_video():
                        msm = app.videos
                        var = ["url", "face", "tag", "title", "view", "danmaku", "reply", "coin", "favorite", "like",
                               "share", "create_time", "state_panel"]
                        video_url = msm["url"]
                        widgets = []
                        for i in range(len(video_url)):
                            msms = {}
                            for j in var:
                                if j == "face":
                                    msms[j] = pic_cache(msm[j][i])
                                    # msms[j] = requests.get(msm[j][i]).content
                                else:
                                    msms[j] = msm[j][i]
                            widgets.append(msms)
                        self.display_signal.emit({"error": 0, "video_url": video_url, "widgets": widgets})
                        break
            else:
                self.display_signal.emit({"error": 1})
        except Exception as e:
            print(e)
            self.display_signal.emit({"error": 1})


class Article_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                for _ in range(5):
                    if app.get_article():
                        msm = app.article
                        var = ["url", "face", "tag", "title", "view", "reply", "coin", "favorite", "like",
                               "share", "create_time"]
                        article_url = msm["url"]
                        widgets = []
                        for i in range(len(article_url)):
                            msms = {}
                            for j in var:
                                if j == "face":
                                    msms[j] = pic_cache(msm[j][i])
                                    # msms[j] = requests.get(msm[j][i]).content
                                else:
                                    msms[j] = msm[j][i]
                            widgets.append(msms)
                        self.display_signal.emit({"error": 0, "article_url": article_url, "widgets": widgets})
                        break
            else:
                self.display_signal.emit({"error": 1})
        except Exception as e:
            print(e)
            self.display_signal.emit({"error": 1})


class Reply_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                for _ in range(5):
                    if app.get_reply():
                        msm = app.reply
                        # print(msm)
                        var = ["title", "id", "floor", "face", "replier", "message", "ctime", "parent", "parent_name", "parent_message", "like"]
                        reply_url = msm["url"]
                        widgets = []
                        for i in range(len(reply_url)):
                            msms = {}
                            for j in var:
                                if j == "face":
                                    msms[j] = pic_cache(msm[j][i])
                                else:
                                    msms[j] = msm[j][i]
                            widgets.append(msms)
                        self.display_signal.emit({"error": 0, "reply_url": reply_url, "widgets": widgets})
                        break
            else:
                self.display_signal.emit({"error": 1})
        except Exception as e:
            print(e)
            self.display_signal.emit({"error": 1})


class Danmaku_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies

    def run(self):
        app = api.BD()
        login_info = {}
        try:
            if app.login(**self.cookies):
                for _ in range(5):
                    if app.get_danmaku():
                        msm = app.danmaku
                        # print(msm)
                        var = ["title", "id", "message", "ctime"]
                        reply_url = msm["url"]
                        widgets = []
                        for i in range(len(reply_url)):
                            msms = {}
                            for j in var:
                                msms[j] = msm[j][i]
                            widgets.append(msms)
                        self.display_signal.emit({"error": 0, "danmaku_url": reply_url, "widgets": widgets})
                        break
            else:
                self.display_signal.emit({"error": 1})
        except Exception as e:
            print(e)
            self.display_signal.emit({"error": 1})


class Update_Thread(QThread):
    display_signal = pyqtSignal(dict)

    def __init__(self, auto):
        super().__init__()
        self.auto = auto

    def run(self):
        try:
            result = json.loads(requests.get('https://www.toodo.fun/funs/bilibili/version.php', timeout=3).text)
        except:
            result = {
                "net": 0,
                "Version": 1.1,
                "Update_des": "1、更新了一\n2、更新了2222\n3、更新了333",
                "Update_url": "https://www.toodo.fun"
            }
        if self.auto:
            result["auto"] = True
        else:
            result["auto"] = False
        self.display_signal.emit(result)

