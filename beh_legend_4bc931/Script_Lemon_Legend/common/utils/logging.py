# -*- coding: utf-8 -*-
import time


class logging(object):
    USE_LOGGER = True
    LOG_LEVEL = "DEBUG"

    @classmethod
    def i(cls, message):
        cls.info(message)

    @classmethod
    def e(cls, message):
        cls.error(message)

    @classmethod
    def w(cls, message):
        cls.warn(message)

    @classmethod
    def d(cls, message):
        cls.debug(message)

    @classmethod
    def info(cls, message):
        if cls.USE_LOGGER and cls.LOG_LEVEL in ["INFO", "DEBUG"]:
            print("[{}]".format(cls._timeFormatter()) + " [INFO] {}".format(message))

    @classmethod
    def error(cls, message):
        if cls.USE_LOGGER:
            print("[{}]".format(cls._timeFormatter()) + " [ERROR] {}".format(message))

    @classmethod
    def warn(cls, message):
        if cls.USE_LOGGER:
            print("[{}]".format(cls._timeFormatter()) + " [WARN] {}".format(message))

    @classmethod
    def debug(cls, message):
        if cls.USE_LOGGER and cls.LOG_LEVEL == "DEBUG":
            print("[{}]".format(cls._timeFormatter()) + " [DEBUG] {}".format(message))

    @classmethod
    def warning(cls, message):
        cls.warn(message)

    @classmethod
    def _timeFormatter(cls):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
