import pdb
import os, json
import requests
from utils.cli_args import CLIArgs as CLI
import sys, signal, asyncio
import logging.config
from logs.custom_logging import cli_output
import multiprocessing as mp


def signal_handler(sig, frame):
    cli_output.FATAL(
        f"\n{mp.current_process().name} EXITED w/ {signal.strsignal(sig)}\n")


class SigExc(Exception):
    pass


class FindAndProbeInit:

    def __init__(self) -> None:
        self.session = requests.Session()
        self.WEBSOCKETS_IP, self.WEBSOCKETS_PORT = ("localhost", 3000)

        # initialize CLI argument inputs
        user_input = CLI()
        user_input.collect_arguments()
        self.args = user_input.argument_values

        # initialize logger
        f = open(os.path.join(
            "..",
            os.getcwd(),
            "logs",
            "logging_settings.json"))
        logging_configs = json.load(f)
        logging.config.dictConfig(logging_configs)
        self.logger = logging.getLogger()


class CustomProcess(mp.Process):

    def __init__(self, my_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exec_func = my_func
        self._is_async = asyncio.iscoroutinefunction(my_func)


    def _process_handler(self, sig, frame):
        raise SigExc


    def run(self):
        signal.signal(signal.SIGINT, self._process_handler)
        try:
            asyncio.run(self._exec_func()) if self._is_async else self._exec_func()
        except SigExc:
            cli_output.FATAL(f"\n{mp.current_process().name} EXITED\n")
