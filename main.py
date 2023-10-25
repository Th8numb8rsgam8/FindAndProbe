import pdb
import json
import signal
import platform
import requests
import multiprocessing as mp
import logging.config
from utils.cli_args import *
from utils.init_support import signal_handler
from components.finder import Finder
from components.poller import Poller


class FindAndProbeInit:

    def __init__(self) -> None:
        self.session = requests.Session()

        # initialize CLI argument inputs
        user_input = CLIArgs()
        user_input.collect_arguments()
        self.args = user_input.argument_values

        # initialize logger
        f = open("logs/logging_settings.json")
        logging_configs = json.load(f)
        logging.config.dictConfig(logging_configs)
        self.logger = logging.getLogger()


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    host_system = platform.system()
    if host_system == "Linux":
        mp.set_start_method("fork")
    else:
        mp.set_start_method("spawn")
    startup_info = FindAndProbeInit()

    finder_pipe, poller_pipe = mp.Pipe(duplex=True)
    finder = Finder(startup_info, finder_pipe)
    poller = Poller(startup_info, poller_pipe)
    finder.run()
    poller.run()


#     try:
#         with open(wordlist) as file:
#             for line in file:
#                 word = line.strip()
#                 test_url = target_url + "/" + word
#                 response = request(test_url)
#                 time.sleep(1/3)
#                 if response:
#                     print("\033[1;32;40m [+] Discovered directory --> " + test_url + "\033[0;0m")
#                 else:
#                     print("\033[0;31;40m [-] Not valid endpoint --> " + test_url + "\033[0;0m")
# 
#     except KeyboardInterrupt:
# 
#         print("Program ended")
