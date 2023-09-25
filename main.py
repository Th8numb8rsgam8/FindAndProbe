#!/home/kali/anaconda3/bin/python

import os, sys 
import pdb
import json
import time
import signal
import platform
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
        threading.excepthook = self.__thread_error


    def run(self):
        poll_thread = threading.Thread(target=self.poll_targets, daemon=True)
        poll_thread.name = "Probe Inquisitor"
        try:
            poll_thread.start()
        except KeyboardInterrupt:
            poll_thread.join()
            self.__startup_info.logger.critical("POLLER STOPPED")
            sys.exit(1)


    def run_probe(self, link_data):
        probe = Probe(self.__startup_info)
        probe.probe_link(link_data)


    def __thread_error(self, arg):
        self.__startup_info.logger.critical("THREAD ERROR")


    def __observe_error(self, exc):
        self.__startup_info.logger.critical(exc)


    def __observe_finish(self, arg):
        print("FINISHED")


    def __probe_pool_init(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)


    def poll_targets(self):
        try:
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
                        callback=self.__observe_finish,
                        error_callback=self.__observe_error)
            probes_pool.close()
            probes_pool.join()
        except KeyboardInterrupt:
            self.__startup_info.logger.critical("POLLER ERROR")


def signal_handler(sig, frame):
    print("INTERRUPT SIGNAL")
    sys.exit(0)


if __name__ == "__main__":
    
    try:
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

    except KeyboardInterrupt:
        startup_info.logger.critical("USER PREMATURELY ENDED SCRIPT EXECUTION!")
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
