import sys
import login_func
import function
from PyQt5 import QtWidgets, QtGui, QtCore
import json
import api

debug = 0

def main():
    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(":/images/demo1.png"))
    splash.showMessage("正在初始化程序...", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
    splash.show()
    QtWidgets.qApp.processEvents()
    if debug:
        ui = function.fun_main({})
        ui.show()
    else:
        splash.showMessage("正在检查登录状态...", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        QtWidgets.qApp.processEvents()
        try:
            with open("config.json", "r") as f:
                login_info = json.loads(f.readline())
            check = api.BD()
            if check.login(**login_info):
                splash.showMessage("登录成功，即将打开主程序...", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
                QtWidgets.qApp.processEvents()
                cookies = check.get_cookies()
                for i in cookies:
                    login_info[i] = cookies[i]
                login_info["access_token"] = check.access_token
                login_info["refresh_token"] = check.refresh_token
                with open("config.json", "w") as f:
                    f.write(json.dumps(login_info))
                ui = function.fun_main(cookies)
                ui.show()
                splash.finish(ui)
            else:
                splash.showMessage("登陆状态失效，请重新登录...", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
                QtWidgets.qApp.processEvents()
                raise Exception("登陆状态失效")
        except Exception as e:
            print(e)
            login_w = login_func.login_UI()
            login_w.show()
            splash.finish(login_w)
    exit_code = app.exec_()
    if exit_code == 101:
        main()
    else:
        sys.exit()

if __name__ == '__main__':
    main()
