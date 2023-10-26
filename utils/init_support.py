import pdb
import sys
import signal
from logs.custom_logging import cli_output
import multiprocessing as mp


def signal_handler(sig, frame):
    cli_output.FATAL(f"\n{mp.current_process().name} EXITED w/ {signal.strsignal(sig)}\n")


class SigExc(Exception):
    pass


class CustomProcess(mp.Process):

    def __init__(self, my_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exec_func = my_func


    def _process_handler(self, sig, frame):
        raise SigExc


    def run(self):
        signal.signal(signal.SIGINT, self._process_handler)
        while True:
            try:
                self._exec_func()
            except SigExc:
                break
        cli_output.FATAL(f"\n{mp.current_process().name} EXITED\n")
