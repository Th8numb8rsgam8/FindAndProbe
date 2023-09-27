import pdb
import sys
import signal
import multiprocessing as mp

def signal_handler(sig, frame):
    sys.exit(1)


def child_process_handler(sig, frame):
    raise SigExc


class SigExc(Exception):
    pass


class CustomProcess(mp.Process):

    def __init__(self, my_func, sig_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__exec_func = my_func
        self.__sig_handler = sig_handler


    def run(self):
        signal.signal(signal.SIGINT, self.__sig_handler)
        while True:
            try:
                self.__exec_func()
            except SigExc:
                break
        print(f"{mp.current_process().name} EXITED")
