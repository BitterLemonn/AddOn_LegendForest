import time


class logging():

    USE_LOGGER = True
    LOG_LEVEL = "DEBUG"

    @classmethod
    def info(cls, message):
        if cls.USE_LOGGER and cls.LOG_LEVEL in ["INFO", "DEBUG"]:
            print(cls._timeFormatter() + " [INFO] {}".format(message))

    @classmethod
    def error(cls, message):
        if cls.USE_LOGGER:
            print(cls._timeFormatter() + " [ERROR] {}".format(message))

    @classmethod
    def warn(cls, message):
        if cls.USE_LOGGER:
            print(cls._timeFormatter() + " [WARN] {}".format(message))

    @classmethod
    def debug(cls, message):
        if cls.USE_LOGGER and cls.LOG_LEVEL == "DEBUG":
            print(cls._timeFormatter() + " [DEBUG] {}".format(message))

    @classmethod
    def warning(cls, message):
        cls.warn(message)

    @classmethod
    def _timeFormatter(cls):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
