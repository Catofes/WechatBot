import itchat
import random
import logging
import datetime
import pytz
import hashlib
import threading

itchat.set_logging(loggingLevel=logging.DEBUG)


class MainHandler:
    def __init__(self):
        self.at_handler = {}
        self.slash_handler = {}

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
                command = command.split()
                print(command)
                if command[0] in self.at_handler:
                    return self.at_handler[command[0]](msg, command[1:])

    def register_at(self, key, func):
        self.at_handler[key] = func

    def register_slash(self, key, func):
        self.slash_handler[key] = func

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
        main_handler.register_slash("fff.install", self.fff_install_handler)
        main_handler.register_slash("fff.add", self.fff_add_handler)
        main_handler.register_slash("fff.status", self.fff_status_handler)
        main_handler.register_slash("fff.ignite", self.fff_ignite_handler)
        main_handler.register_slash("fff.water", self.fff_water_handler)

    def fff_install_handler(self, msg, command=None):
        if not command:
            return "你要烧谁？"
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
        else:
            self.lock.acquire()
            for v in command:
                self.flavour.append(v)
            text = "你将 %s 加入了火刑架" % " ".join(command)
            self.lock.release()
            return text

    def fff_status_handler(self, msg, command=None):
        if not self.people:
            return "火柱上什么都没有"
        elif self.flavour:
            return "在 %s 的环绕中， %s 熊熊燃烧！" % (" ".join(self.flavour), " ".join(self.people))
        else:
            return "%s 在熊熊燃烧！" % " ".join(self.people)

    def fff_ignite_handler(self, msg, command=None):
        if not self.people:
            return "火刑架上空空如也。"
        else:
            return "%s 烧起来了，此处应该有掌声！" % (" ".join(self.people))

    def fff_water_handler(self, msg, command=None):
        if not self.people:
            return "火刑架上空空如也。"
        else:
            self.lock.acquire()
            text = "火被扑灭了， %s 被救了下来。" % (" ".join(self.people))
            self.people = []
            self.flavour = []
            self.lock.release()
            return text


if __name__ == '__main__':
    h = MainHandler()
    RandomHandler(h)
    EatWhatHandler(h)
    h.run()
