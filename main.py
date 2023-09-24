#!/home/kali/anaconda3/bin/python

import os, sys 
import pdb
import json
import time
import requests
import threading 
import multiprocessing as mp
import logging.config
from cli_args import CLIArgs
from finder import Finder
from probe import Probe


class FindAndProbeInit:

    def __init__(self) -> None:
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


class Poller:

    def __init__(self, startup_info, connection):
        self.__startup_info = startup_info
        self.__connection = connection


    def run_probe(self, link_data):
        probe = Probe(startup_info)
        probe.probe_link(link_data)


    def __observe_error(self, exc):
        print(exc)


    def poll_targets(self):
        available_cpus = len(os.sched_getaffinity(0))
        probes_pool = mp.Pool(processes=available_cpus)
        while True:
            if self.__connection.poll():
                link_data = self.__connection.recv_bytes().decode('utf-8')
                link_data = json.loads(link_data)
                self.__startup_info.logger.warning(link_data["url"])
                probes_pool.apply_async(
                    func=self.run_probe, 
                    args=(link_data,),
                    error_callback=self.__observe_error)
        probes_pool.close()
        probes_pool.join()


if __name__ == "__main__":
    
    try:
        mp.set_start_method("fork")
        startup_info = FindAndProbeInit()
        finder_pipe, probe_pipe = mp.Pipe(duplex=True)
        Finder.initialize(startup_info, finder_pipe)
        finder = Finder()
        poller = Poller(startup_info, probe_pipe)

        poll_thread = threading.Thread(target=poller.poll_targets)
        poll_thread.name = "Probe Inquisitor"
        poll_thread.start()

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
