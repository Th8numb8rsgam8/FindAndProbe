import logging
import pdb

class CustomFormatter(logging.Formatter):

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[37m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0;0m"


    def __init__(self, fmt, datefmt, msecfmt):
        super().__init__()
        logging.Formatter.default_time_format = datefmt
        logging.Formatter.default_msec_format = msecfmt 
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.GREEN + self.fmt + self.RESET,
            logging.INFO:  self.CYAN + self.fmt + self.RESET,
            logging.WARNING: self.YELLOW + self.fmt + self.RESET,
            logging.ERROR: self.RED + self.fmt + self.RESET,
            logging.CRITICAL: self.RED + self.BOLD + self.fmt + self.RESET}


    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class cli_output:

    def INFO(text):
        print(f'\033[1;37m {text} \033[0;0')

    
    def OK(text):
        print(f'\033[1;32m {text} \033[0;0')


    def WARNING(text):
        print(f'\033[1;33m {text} \033[0;0')


    def FATAL(text):
        print(f'\033[1;31m {text} \033[0;0')
