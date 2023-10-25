import os
import json
import signal
import multiprocessing as mp
from components.probe import Probe
from logs.custom_logging import cli_output 
from utils.init_support import CustomProcess


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
        available_cpus = len(os.sched_getaffinity(0))
        probes_pool = mp.Pool(
            processes=available_cpus,
            initializer=self.__probe_pool_init)
        while True:
            if self.__connection.poll():
                link_data = self.__connection.recv_bytes().decode('utf-8')
                link_data = json.loads(link_data)
                probes_pool.apply_async(
                    func=self.run_probe, 
                    args=(link_data,),
                    callback=self.__probe_finish,
                    error_callback=self.__probe_error)
        # probes_pool.close()
        # probes_pool.join()
