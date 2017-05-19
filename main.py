import itchat
import random
import logging
import datetime
import pytz
import hashlib

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
                if len(command) <= 0:
                    return
                if msg.Content[1:] in self.slash_handler:
                    return self.slash_handler[command[0]](msg, command[1:])
            if msg.isAt:
                command = str.replace(msg.Content, "@trangent ", "")
                print(command)
                if command in self.at_handler:
                    return self.at_handler[command](msg)

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
        if len(command) > 0:
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


if __name__ == '__main__':
    h = MainHandler()
    RandomHandler(h)
    EatWhatHandler(h)
    h.run()
