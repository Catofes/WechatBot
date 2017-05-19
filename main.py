import itchat
import random
import logging
import datetime
import pytz
import hashlib
import threading
import requests

itchat.set_logging(loggingLevel=logging.DEBUG)


class MainHandler:
    def __init__(self):
        self.at_handler = {}
        self.slash_handler = None

    def prepare(self):
        @itchat.msg_register(itchat.content.TEXT, False, True)
        def random_reply(msg):
            if msg.Content and msg.Content[0] == "/":
                command = msg.Content[1:].split()
                print(command)
                if command[0] in self.slash_handler:
                    return self.slash_handler[command[0]](msg, command[1:])
            if msg.isAt:
                command = str.replace(msg.Content, "@trangent ", "")
                print(command)
                if self.slash_handler:
                    self.slash_handler(msg, command)

    def register_at(self, key, func):
        self.at_handler[key] = func

    def register_slash(self, func):
        self.slash_handler = func

    def run(self):
        self.prepare()
        itchat.auto_login(hotReload=True, enableCmdQR=2)
        itchat.run()


class RandomHandler:
    def __init__(self, main_handler: MainHandler):
        main_handler.register_at("random", self.handler)
        main_handler.register_slash("random", self.handler)

    def handler(self, msg, command=None):
        if command:
            return "%s" % random.randint(0, int(command[0]))
        else:
            return "%s" % random.randint(0, 100)


class EatWhatHandler:
    def __init__(self, main_handler: MainHandler):
        self.refectory = {
            "农园": 1,
            "学一": 1,
            "学五": 1,
            "燕南": 1,
            "勺园": 1,
            "凉皮": 1,
            "这么低概率都能抽中的燕南地下": 0.2,
            "耶！ 吃好的！": 1,
            "蓝旗营": 1
        }
        t = 0.0
        for k, v in self.refectory.items():
            t += float(v)
        self.refectory = {k: float(v) / t for k, v in self.refectory.items()}
        main_handler.register_at("eat", self.handler)
        main_handler.register_at("吃啥", self.handler)
        main_handler.register_slash("eat", self.handler)
        main_handler.register_slash("吃啥", self.handler)

    def get_one(self, seed):
        s = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        s = (s % 100000) / 100000.0
        a = 0.0
        for k, v in self.refectory.items():
            a += v
            if a > s:
                return k

    def handler(self, msg, command=None):
        t = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        if 2 < t.hour < 6:
            return "半夜饿了嘛？ 忍住！"
        elif 6 < t.hour < 10:
            return "早饭我不管。"
        elif 10 < t.hour < 14:
            return "我决定了，今天中午吃： %s" % self.get_one("%s-%s-%s %s" % (t.year, t.month, t.day, "午饭"))
        elif 14 < t.hour < 19:
            return "今天晚上吃： %s" % self.get_one("%s-%s-%s %s" % (t.year, t.month, t.day, "晚饭"))
        else:
            return "你想长胖嘛？"


class FFFHandler:
    def __init__(self, main_handler: MainHandler):
        self.lock = threading.RLock()
        self.people = []
        self.flavour = []
        self.on_fire = False
        main_handler.register_slash("fff.install", self.fff_install_handler)
        main_handler.register_slash("fff.add", self.fff_add_handler)
        main_handler.register_slash("fff.status", self.fff_status_handler)
        main_handler.register_slash("fff.ignite", self.fff_ignite_handler)
        main_handler.register_slash("fff.water", self.fff_water_handler)

    def fff_install_handler(self, msg, command=None):
        if not command:
            return "你要烧谁？"
        elif self.on_fire:
            return "火刑架已经烧起来了。"
        else:
            self.lock.acquire()
            for v in command:
                self.people.append(v)
            text = "你将 %s 绑上火刑架" % " ".join(command)
            self.lock.release()
            return text

    def fff_add_handler(self, msg, command=None):
        if not command:
            return "你要添加什么调料？"
        elif self.on_fire:
            return "火刑架已经烧起来了。"
        else:
            self.lock.acquire()
            for v in command:
                self.flavour.append(v)
            text = "你将 %s 加入了火刑架" % " ".join(command)
            self.lock.release()
            return text

    def fff_status_handler(self, msg, command=None):
        if not self.on_fire:
            if not self.people:
                return "火刑架上什么都没有"
            else:
                return "火刑架上的 %s 正在哀嚎。" % " ".join(self.people)
        elif self.flavour:
            return "在 %s 的环绕中， %s 熊熊燃烧！" % (" ".join(self.flavour), " ".join(self.people))
        else:
            return "%s 在熊熊燃烧！" % " ".join(self.people)

    def fff_ignite_handler(self, msg, command=None):
        if self.on_fire:
            return "火刑架已经烧起来了"
        elif not self.people:
            return "火刑架上空空如也。"
        else:
            self.lock.acquire()
            self.on_fire = True
            self.lock.release()
            return "%s 烧起来了，此处应该有掌声！" % (" ".join(self.people))

    def fff_water_handler(self, msg, command=None):
        if not self.on_fire:
            return "火刑架上空空如也。"
        else:
            self.lock.acquire()
            self.on_fire = False
            text = "火被扑灭了， %s 被救了下来。" % (" ".join(self.people))
            self.people = []
            self.flavour = []
            self.lock.release()
            return text


class ZhangZheHanlder:
    def __init__(self, main_handler: MainHandler):
        self.quota = []
        f = open("Zhangzhe.txt", "r")
        for l in f:
            self.quota.append(l)
        f.close()
        main_handler.register_slash("+1s", self.handler)
        main_handler.register_at("+1s", self.handler)

    def handler(self, msg, command=None):
        return random.choice(self.quota)


class TuLingHandler:
    def __init__(self, main_handler: MainHandler):
        self.key = open("tuling.key").read()
        self.api = "http://www.tuling123.com/openapi/api"
        main_handler.register_at(self.handler)

    def handler(self, msg, command=None):
        if not command:
            return
        url = self.api
        d = {
            "key": self.key,
            "info": command,
            "loc": "北京市北京大学",
            "userid": msg.FromUserName
        }
        response = requests.post(url, data=d)
        response = response.json()
        if response.code == 100000:
            return response.text
        elif response.code == 200000:
            return "%s, url: %s" % (response.text, response.url)
        elif response.code == 302000:
            text = response.text + "\n"
            for v in response.list:
                text += '%s: %s \n' % (v['article'], v['detailurl'])
            return text


if __name__ == '__main__':
    h = MainHandler()
    RandomHandler(h)
    EatWhatHandler(h)
    FFFHandler(h)
    ZhangZheHanlder(h)
    TuLingHandler(h)
    h.run()
