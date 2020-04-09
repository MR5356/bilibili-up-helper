import base64
import hashlib
import json
import requests
import time
from urllib import parse
import rsa


class BD:
    def __init__(self):
        self.app_key = "1d8b6e7d45233436"
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': "Mozilla/5.0 BiliDroid/5.51.1 (bbcallen@gmail.com)"})
        self.get_cookies = lambda: self._session.cookies.get_dict(domain=".bilibili.com")
        self.get_uid = lambda: self.get_cookies().get("DedeUserID", "")
        self.main_info = {
            "nickname": "",
            "face": "",
            "coins": 0,
            "mid": "",
            'level': 0,
            'balance': 0,
            "follower": 0,
            'experience': {
                'current': 0,
                'next': 0,
            },
            'video': {
                "coin": 0,
                "favorite": 0,
                "like": 0,
                "view": 0,
                "danmaku": 0,
                "reply": 0,
                "share": 0,
            },
            "article": {
                "view": 0,
                "reply": 0,
                "like": 0,
                "favorite": 0,
                "coin": 0,
                "share": 0,
            },
            "rating": {
                "creative": 0,
                "influence": 0,
                "credit": 0,
            }
        }
        self.notify = {
            "at": 0,
            "chat": 0,
            "like": 0,
            "reply": 0,
            "sys_msg": 0,
        }
        self.videos = {
            "url": [],
            "face": [],
            "tag": [],
            "title": [],
            "view": [],
            "danmaku": [],
            "reply": [],
            "coin": [],
            "favorite": [],
            "like": [],
            "share": [],
            "create_time": [],
            "state_panel": [],
        }
        self.article = {
            "url": [],
            "face": [],
            "tag": [],
            "title": [],
            "view": [],
            "reply": [],
            "coin": [],
            "favorite": [],
            "like": [],
            "share": [],
            "create_time": [],
        }
        self.reply = {
            "title": [],
            "bvid": [],
            "url": [],
            "face": [],
            "id": [],
            "floor": [],
            "replier": [],
            "message": [],
            "ctime": [],
            "parent": [],
            "parent_name": [],
            "parent_message": [],
            "like": [],
        }

    def _requests(self, method, url, decode_level=2, retry=10, timeout=15, **kwargs):
        if method in ["get", "post"]:
            for _ in range(retry + 1):
                try:
                    response = getattr(self._session, method)(url, timeout=timeout, **kwargs)
                    return response.json() if decode_level == 2 else response.content if decode_level == 1 else response
                except:
                    pass
        return None

    # 验证码识别
    def _solve_captcha(self, image):
        url = "https://bili.dev:2233/captcha"
        payload = {'image': base64.b64encode(image).decode("utf-8")}
        response = self._requests("post", url, json=payload)
        return response['message'] if response and response.get("code") == 0 else None

    @staticmethod
    def calc_sign(param):
        salt = "560c52ccd288fed045859ed18bffd973"
        sign_hash = hashlib.md5()
        sign_hash.update(f"{param}{salt}".encode())
        return sign_hash.hexdigest()

    def login(self, **kwargs):
        def by_cookies():
            url = f"https://api.bilibili.com/x/space/myinfo"
            headers = {'Host': "api.bilibili.com"}
            response = self._requests("get", url, headers=headers)
            if response and response.get("code") != -101:
                return True
            else:
                return False

        def by_token():
            param = f"access_key={self.access_token}&appkey={self.app_key}&ts={int(time.time())}"
            url = f"https://passport.bilibili.com/api/v2/oauth2/info?{param}&sign={self.calc_sign(param)}"
            response = self._requests("get", url)
            if response and response.get("code") == 0:
                self._session.cookies.set('DedeUserID', str(response['data']['mid']), domain=".bilibili.com")
                param = f"access_key={self.access_token}&appkey={self.app_key}&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome&ts={int(time.time())}"
                url = f"https://passport.bilibili.com/api/login/sso?{param}&sign={self.calc_sign(param)}"
                self._requests("get", url, decode_level=0)
                if all(key in self.get_cookies() for key in
                       ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]):
                    return True
                else:
                    pass
            url = f"https://passport.bilibili.com/api/v2/oauth2/refresh_token"
            param = f"access_key={self.access_token}&appkey={self.app_key}&refresh_token={self.refresh_token}&ts={int(time.time())}"
            payload = f"{param}&sign={self.calc_sign(param)}"
            headers = {'Content-type': "application/x-www-form-urlencoded"}
            response = self._requests("post", url, data=payload, headers=headers)
            if response and response.get("code") == 0:
                for cookie in response['data']['cookie_info']['cookies']:
                    self._session.cookies.set(cookie['name'], cookie['value'], domain=".bilibili.com")
                self.access_token = response['data']['token_info']['access_token']
                self.refresh_token = response['data']['token_info']['refresh_token']
                return True
            else:
                self.access_token = ""
                self.refresh_token = ""
                return False

        def by_passwd():
            def get_key():
                url = f"https://passport.bilibili.com/api/oauth2/getKey"
                payload = {
                    'appkey': self.app_key,
                    'sign': self.calc_sign(f"appkey={self.app_key}"),
                }
                while True:
                    response = self._requests("post", url, data=payload)
                    if response and response.get("code") == 0:
                        return {
                            'key_hash': response['data']['hash'],
                            'pub_key': rsa.PublicKey.load_pkcs1_openssl_pem(response['data']['key'].encode()),
                        }
                    else:
                        time.sleep(1)

            while True:
                key = get_key()
                key_hash, pub_key = key['key_hash'], key['pub_key']
                url = f"https://passport.bilibili.com/api/v2/oauth2/login"
                param = f"appkey={self.app_key}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{key_hash}{self.password}'.encode(), pub_key)))}&username={parse.quote_plus(self.username)}"
                payload = f"{param}&sign={self.calc_sign(param)}"
                headers = {'Content-type': "application/x-www-form-urlencoded"}
                response = self._requests("post", url, data=payload, headers=headers)
                while True:
                    if response and response.get("code") is not None:
                        if response['code'] == -105:
                            url = f"https://passport.bilibili.com/captcha"
                            headers = {'Host': "passport.bilibili.com"}
                            response = self._requests("get", url, headers=headers, decode_level=1)
                            captcha = self._solve_captcha(response)
                            if captcha:
                                key = get_key()
                                key_hash, pub_key = key['key_hash'], key['pub_key']
                                url = f"https://passport.bilibili.com/api/v2/oauth2/login"
                                param = f"appkey={self.app_key}&captcha={captcha}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{key_hash}{self.password}'.encode(), pub_key)))}&username={parse.quote_plus(self.username)}"
                                payload = f"{param}&sign={self.calc_sign(param)}"
                                headers = {'Content-type': "application/x-www-form-urlencoded"}
                                response = self._requests("post", url, data=payload, headers=headers)
                            else:
                                time.sleep(10)

                        elif response['code'] == -449:
                            time.sleep(1)
                            response = self._requests("post", url, data=payload, headers=headers)
                        elif response['code'] == 0 and response['data']['status'] == 0:
                            for cookie in response['data']['cookie_info']['cookies']:
                                self._session.cookies.set(cookie['name'], cookie['value'], domain=".bilibili.com")
                            self.access_token = response['data']['token_info']['access_token']
                            self.refresh_token = response['data']['token_info']['refresh_token']
                            return True
                        else:
                            return False
                    else:
                        time.sleep(60)

        self._session.cookies.clear()
        for name in ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]:
            value = kwargs.get(name)
            if value:
                self._session.cookies.set(name, value, domain=".bilibili.com")
        self.access_token = kwargs.get("access_token", "")
        self.refresh_token = kwargs.get("refresh_token", "")
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        if (not self.access_token or not self.refresh_token) and all(
                key in self.get_cookies() for key in
                ["bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid", "SESSDATA"]) and by_cookies():
            print("cookies登陆成功")
            return True
        elif self.access_token and self.refresh_token and by_token():
            print("token登录成功")
            return True
        elif self.username and self.password and by_passwd():
            print("密码登陆成功")
            return True
        else:
            self._session.cookies.clear()
            return False

    def get_main_info(self):
        self.main_info = {
            "nickname": "",
            "face": "",
            "coins": 0,
            "mid": "",
            'level': 0,
            'balance': 0,
            "follower": 0,
            'experience': {
                'current': 0,
                'next': 0,
            },
            'video': {
                "coin": 0,
                "favorite": 0,
                "like": 0,
                "view": 0,
                "danmaku": 0,
                "reply": 0,
                "share": 0,
            },
            "article": {
                "view": 0,
                "reply": 0,
                "like": 0,
                "favorite": 0,
                "coin": 0,
                "share": 0,
            },
            "rating": {
                "creative": 0,
                "influence": 0,
                "credit": 0,
            }
        }
        url = f"https://api.bilibili.com/x/space/myinfo?jsonp=jsonp"
        headers = {
            'Host': "api.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        headers2 = {
            'Host': "member.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        response = self._requests("get", url, headers=headers)
        response0 = self._requests("get", "https://api.bilibili.com/studio/growup/web/up/rating/stat", headers=headers)
        if response0 and response0.get("code") == 0:
            self.main_info["rating"]["creative"] = response0['data']['creative']
            self.main_info["rating"]["influence"] = response0['data']['influence']
            self.main_info['rating']["credit"] = response0['data']['credit']
        response2 = self._requests("get", "https://member.bilibili.com/x/web/elec/balance", headers=headers2)
        if response and response.get("code") == 0 and response2 and response2.get("code") == 0:
            self.main_info['experience']['current'] = response['data']['level_exp']['current_exp']
            self.main_info['experience']['next'] = response['data']['level_exp']['next_exp']
            self.main_info['face'] = response['data']['face']
            self.main_info['level'] = response['data']['level']
            self.main_info['nickname'] = response['data']['name']
            self.main_info['mid'] = self.get_uid()
            self.main_info['follower'] = response['data']['follower']
            self.main_info['coins'] = response['data']['coins']
            self.main_info['balance'] = response2['data']["wallet"]["sponsorBalance"]
            response3 = self._requests("get",
                                       f"https://member.bilibili.com/x/web/archives?status=is_pubing%2Cpubed%2Cnot_pubed&pn=1&ps=10&coop=1",
                                       # &interactive=1",
                                       headers=headers2)
            if response3 and response3.get("code") == 0:
                count = response3["data"]["page"]["count"]
                response3 = self._requests("get",
                                           f"https://member.bilibili.com/x/web/archives?status=is_pubing%2Cpubed%2Cnot_pubed&pn=1&ps={count}&coop=1",
                                           # &interactive=1",
                                           headers=headers2)
                if response3 and response3.get("code") == 0:
                    likes, views, reply, danmaku, share, favorite, coin = 0, 0, 0, 0, 0, 0, 0
                    if response3["data"]["arc_audits"]:
                        for i in response3["data"]["arc_audits"]:
                            likes += i["stat"]["like"]
                            views += i["stat"]["view"]
                            reply += i["stat"]["reply"]
                            danmaku += i["stat"]["danmaku"]
                            share += i["stat"]["share"]
                            favorite += i["stat"]["favorite"]
                            coin += i["stat"]["coin"]
                        self.main_info['video']["like"] = likes
                        self.main_info['video']["view"] = views
                        self.main_info['video']["reply"] = reply
                        self.main_info['video']["danmaku"] = danmaku
                        self.main_info['video']["share"] = share
                        self.main_info['video']["favorite"] = favorite
                        self.main_info['video']["coin"] = coin
            response = self._requests("get",
                                      f"https://api.bilibili.com/x/article/creative/article/list?group=0&sort=&pn=1&mobi_app=pc",
                                      headers=headers)
            if response and response.get("code") == 0:
                count = response["artlist"]["page"]["total"]
                if count > 0:
                    for i in response["artlist"]["articles"]:
                        self.main_info["article"]["view"] += i["stats"]["view"]
                        self.main_info["article"]["reply"] += i["stats"]["reply"]
                        self.main_info["article"]["coin"] += i["stats"]["coin"]
                        self.main_info["article"]["favorite"] += i["stats"]["favorite"]
                        self.main_info["article"]["like"] += i["stats"]["like"]
                        self.main_info["article"]["share"] += i["stats"]["share"]
                    if count > 20:
                        if count % 20 == 0:
                            pn = int(count / 20)
                        else:
                            pn = int(count / 20) + 1
                        for i in range(2, pn + 1):
                            response = self._requests("get",
                                                      f"https://api.bilibili.com/x/article/creative/article/list?group=0&sort=&pn={i}&mobi_app=pc",
                                                      headers=headers)
                            if response and response.get("code") == 0:
                                if response["artlist"]["articles"]:
                                    for j in response["artlist"]["articles"]:
                                        self.main_info["article"]["view"] += j["stats"]["view"]
                                        self.main_info["article"]["reply"] += j["stats"]["reply"]
                                        self.main_info["article"]["coin"] += j["stats"]["coin"]
                                        self.main_info["article"]["favorite"] += j["stats"]["favorite"]
                                        self.main_info["article"]["like"] += j["stats"]["like"]
                                        self.main_info["article"]["share"] += j["stats"]["share"]
            return True
        else:
            return False

    def get_notify(self):
        url = f"https://api.bilibili.com/x/msgfeed/unread?build=0&mobi_app=web"
        headers = {
            'Host': "api.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        response = self._requests("get", url, headers=headers)
        if response and response.get("code") == 0:
            self.notify["at"] = response['data']['at']
            self.notify["chat"] = response['data']["chat"]
            self.notify["reply"] = response['data']["reply"]
            self.notify["like"] = response['data']["like"]
            self.notify["sys_msg"] = response['data']["sys_msg"]
            return True
        else:
            return False

    def get_video(self):
        headers2 = {
            'Host': "member.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        response3 = self._requests("get",
                                   f"https://member.bilibili.com/x/web/archives?status=is_pubing%2Cpubed%2Cnot_pubed&pn=1&ps=10&coop=1",
                                   # &interactive=1",
                                   headers=headers2)
        if response3 and response3.get("code") == 0:
            count = response3["data"]["page"]["count"]
            response3 = self._requests("get",
                                       f"https://member.bilibili.com/x/web/archives?status=is_pubing%2Cpubed%2Cnot_pubed&pn=1&ps={count}&coop=1",
                                       # &interactive=1",
                                       headers=headers2)
            if response3 and response3.get("code") == 0:
                if response3["data"]["arc_audits"]:
                    for i in response3["data"]["arc_audits"]:
                        self.videos["face"].append(i["Archive"]["cover"])
                        self.videos["url"].append(f"https://www.bilibili.com/video/{i['Archive']['bvid']}")
                        self.videos["tag"].append(i["typename"])
                        self.videos["title"].append(i["Archive"]["title"])
                        self.videos["view"].append(i["stat"]["view"])
                        self.videos["danmaku"].append(i["stat"]["danmaku"])
                        self.videos["reply"].append(i["stat"]["reply"])
                        self.videos["coin"].append(i["stat"]["coin"])
                        self.videos["favorite"].append(i["stat"]["favorite"])
                        self.videos["like"].append(i["stat"]["like"])
                        self.videos["share"].append(i["stat"]["share"])
                        self.videos["create_time"].append(i["Archive"]["ptime"])
                        self.videos["state_panel"].append(i["state_panel"])
                return True
            else:
                return False
        else:
            return False

    def get_article(self):
        headers = {
            'Host': "api.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        response = self._requests("get",
                                  f"https://api.bilibili.com/x/article/creative/article/list?group=0&sort=&pn=1&mobi_app=pc",
                                  headers=headers)
        if response and response.get("code") == 0:
            count = response["artlist"]["page"]["total"]
            if count > 0:
                for i in response["artlist"]["articles"]:
                    self.article["url"].append(i["view_url"])
                    self.article["face"].append(i["origin_image_urls"][0])
                    self.article["tag"].append(i["category"]["name"])
                    self.article["title"].append(i["title"])
                    self.article["view"].append(i["stats"]["view"])
                    self.article["reply"].append(i["stats"]["reply"])
                    self.article["coin"].append(i["stats"]["coin"])
                    self.article["favorite"].append(i["stats"]["favorite"])
                    self.article["like"].append(i["stats"]["like"])
                    self.article["share"].append(i["stats"]["share"])
                    self.article["create_time"].append(i["publish_time"])
                if count > 20:
                    if count % 20 == 0:
                        pn = int(count / 20)
                    else:
                        pn = int(count / 20) + 1
                    for i in range(2, pn + 1):
                        response = self._requests("get",
                                                  f"https://api.bilibili.com/x/article/creative/article/list?group=0&sort=&pn={i}&mobi_app=pc",
                                                  headers=headers)
                        if response and response.get("code") == 0:
                            if response["artlist"]["articles"]:
                                for j in response["artlist"]["articles"]:
                                    self.article["url"].append(j["view_url"])
                                    self.article["face"].append(j["origin_image_urls"][0])
                                    self.article["tag"].append(j["category"]["name"])
                                    self.article["title"].append(j["title"])
                                    self.article["view"].append(j["stats"]["view"])
                                    self.article["reply"].append(j["stats"]["reply"])
                                    self.article["coin"].append(j["stats"]["coin"])
                                    self.article["favorite"].append(j["stats"]["favorite"])
                                    self.article["like"].append(j["stats"]["like"])
                                    self.article["share"].append(j["stats"]["share"])
                                    self.article["create_time"].append(j["publish_time"])
            return True
        else:
            return False

    def get_reply(self):
        self.reply = {
            "title": [],
            'url': [],
            "bvid": [],
            "id": [],
            "floor": [],
            "face": [],
            "replier": [],
            "message": [],
            "ctime": [],
            "parent": [],
            "parent_name": [],
            "parent_message": [],
            "like": [],
        }
        headers = {
            'Host': "member.bilibili.com",
            'Referer': f"https://space.bilibili.com/{self.get_uid()}/",
        }
        response = self._requests("get",
                                  f"https://member.bilibili.com/x/web/replies?order=ctime&filter=-1&is_hidden=0&type=1&bvid=&pn=1&ps=1",
                                  headers=headers)
        if response and response.get("code") == 0:
            count = response["pager"]["total"]
            response = self._requests("get",
                                      f"https://member.bilibili.com/x/web/replies?order=ctime&filter=-1&is_hidden=0&type=1&bvid=&pn=1&ps={count}",
                                      headers=headers)
            if response and response.get("code") == 0:
                if response["data"]:
                    for i in response["data"]:
                        self.reply['title'].append(i['title'])
                        self.reply['url'].append(f"https://www.bilibili.com/video/{i['bvid']}")
                        self.reply['id'].append(i['id'])
                        self.reply['floor'].append(i['floor'])
                        self.reply['replier'].append(i['replier'])
                        self.reply['message'].append(i['message'])
                        self.reply['ctime'].append(i['ctime'])
                        self.reply['face'].append(i['cover'])
                        self.reply['parent'].append(i['parent'])
                        if i['parent'] == 0:
                            self.reply['parent_name'].append("")
                            self.reply['parent_message'].append("")
                        else:
                            self.reply['parent_name'].append(i['root_info']['member']['uname'])
                            self.reply['parent_message'].append(i['root_info']['content']['message'])
                        self.reply['like'].append(i['like'])
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    app = BD()
    login_info = {}
    try:
        with open("config.json", "r") as f:
            login_info = json.loads(f.readline())
            if app.login(**login_info):
                print("A登录成功")
                cookies = app.get_cookies()
                for i in cookies:
                    login_info[i] = cookies[i]
                login_info["access_token"] = app.access_token
                login_info["refresh_token"] = app.refresh_token
                with open("config.json", "w") as f:
                    f.write(json.dumps(login_info))
                if app.get_main_info():
                    print(app.main_info)
            else:
                print("A登陆失败")
    except:
        pass
