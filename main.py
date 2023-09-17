#!/home/kali/anaconda3/bin/python

import pdb
import os, sys
import time
import json
import requests
import threading
import multiprocessing as mp
import logging.config
from cli_args import CLIArgs
from finder import Finder
from probe import Probe

class FindAndProbeInit:

    def __init__(self):
        self.queue = mp.Queue()
        self.session = requests.Session()

        # initialize CLI argument inputs
        cli_args = CLIArgs()
        cli_args.collect_arguments()
        self.args = cli_args.argument_values

        # initialize logger
        f = open("finder_logging.json")
        logging_configs = json.load(f)
        f.close()
        logging.config.dictConfig(logging_configs)
        self.logger = logging.getLogger(__name__)


if __name__ == "__main__":
    
    try:
        available_cpus = len(os.sched_getaffinity(0))
        # process_pool = mp.Pool(processes=available_cpus)
        finder_pipe, probe_pipe = mp.Pipe(duplex=True)
        startup_info = FindAndProbeInit()
        finder = Finder(startup_info, finder_pipe)
        probe = Probe(startup_info, probe_pipe)
        # process_pool.apply_async(finder.crawl())
        # finder_thread = threading.Thread(finder.crawl())
        # finder_thread.name = "Finder Thread"
        # finder_thread.start()

        # probe.probe_targets()
        # probe_thread = threading.Thread(probe.probe_targets())
        # probe_thread.name = "Probe Thread"
        # probe_thread.start()
    except KeyboardInterrupt:
        logger.critical("USER PREMATURELY ENDED SCRIPT EXECUTION!")
        sys.exit(1)

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
