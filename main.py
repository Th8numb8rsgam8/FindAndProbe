import os, sys 
import pdb
import json
import time
import signal
import platform
import requests
import multiprocessing as mp
from custom_logging import cli_output
import logging.config
from cli_args import CLIArgs
from finder import Finder
from probe import Probe
from init_support import *


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


    def run(self):
        poll_process = CustomProcess(
            self.poll_targets, 
            name="Probe Inquisitor")
        poll_process.start()


    def run_probe(self, link_data):
        probe = Probe(self.__startup_info)
        probe.probe_link(link_data)


    def __probe_error(self, exc):
        self.__startup_info.logger.critical(exc)


    def __probe_finish(self, arg):
        cli_output.OK("FINISHED")


    def __probe_pool_init(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)


    def poll_targets(self):
        self.__startup_info.logger.warning("POLLER")
        available_cpus = len(os.sched_getaffinity(0))
        probes_pool = mp.Pool(
            processes=available_cpus,
            initializer=self.__probe_pool_init)
        while True:
            if self.__connection.poll():
                link_data = self.__connection.recv_bytes().decode('utf-8')
                link_data = json.loads(link_data)
                self.__startup_info.logger.warning(link_data["url"])
                probes_pool.apply_async(
                    func=self.run_probe, 
                    args=(link_data,),
                    callback=self.__probe_finish,
                    error_callback=self.__probe_error)
        # probes_pool.close()
        # probes_pool.join()


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
