import logging
import re

class CustomFormatter(logging.Formatter):

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[37m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0;0m"

    def __init__(self, datefmt, msecfmt):
        logging.Formatter.default_time_format = datefmt
        logging.Formatter.default_msec_format = msecfmt


class ConsoleLogging(CustomFormatter):

    def __init__(self, fmt, datefmt, msecfmt, defaults):
        super().__init__(datefmt, msecfmt)
        self.fmt = fmt
        self.defaults = defaults
        self.FORMATS = {
            logging.DEBUG: self.GREEN + self.fmt + self.RESET,
            logging.INFO:  self.CYAN + self.fmt + self.RESET,
            logging.WARNING: self.YELLOW + self.fmt + self.RESET,
            logging.ERROR: self.RED + self.fmt + self.RESET,
            logging.CRITICAL: self.RED + self.BOLD + self.fmt + self.RESET}


    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, defaults=self.defaults)
        return formatter.format(record)


class FinderLogging(CustomFormatter):

    def __init__(self, fmt, datefmt, msecfmt, defaults):
        super().__init__(datefmt, msecfmt)
        self.fmt = fmt
        self.defaults = defaults


    def format(self, record):
        # record.msg = re.sub('\\x1b\[.*?m', '', record.msg)
        s, ms = divmod(record.relativeCreated, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        record.relativeCreated = f"{round(h)}:{round(m)}:{s + round(ms/1000,3)}"
        formatter = logging.Formatter(self.fmt, defaults=self.defaults)
        return formatter.format(record)


class ProbeLogging(CustomFormatter):

    def __init__(self, fmt, datefmt, msecfmt, defaults):
        super().__init__(datefmt, msecfmt)
        self.fmt = fmt
        self.defaults = defaults


    def format(self, record):
        # record.msg = re.sub('\\x1b\[.*?m', '', record.msg)
        s, ms = divmod(record.relativeCreated, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        record.relativeCreated = f"{round(h)}:{round(m)}:{s + round(ms/1000,3)}"
        formatter = logging.Formatter(self.fmt, defaults=self.defaults)
        return formatter.format(record)


class ConsoleFilter(logging.Filter):

    def filter(self, record):
        return True


class FinderFilter(logging.Filter):

    def filter(self, record):
        if "PROBE" not in record.msg:
            return True


class ProbeFilter(logging.Filter):

    def filter(self, record):
        if "PROBE" in record.msg:
            return True


class cli_output:

    def INFO(text):
        print(f'\033[1;37m {text} \033[0;0')

    
    def OK(text):
        print(f'\033[1;32m {text} \033[0;0')


    def WARNING(text):
        print(f'\033[1;33m {text} \033[0;0')


    def FATAL(text):
        print(f'\033[1;31m {text} \033[0;0')
