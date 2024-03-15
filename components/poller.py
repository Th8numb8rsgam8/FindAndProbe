import os
import json
import signal
import multiprocessing as mp
from components.probe import Probe
from logs.custom_logging import cli_output 
from utils.init_support import CustomProcess


class Poller:

    def __init__(self, startup_info, connection, queue):
        self._startup_info = startup_info
        self._connection = connection


    def run(self):
        poll_process = CustomProcess(
            self.poll_targets, 
            name="Probe Inquisitor")
        poll_process.start()


    def run_probe(self, link_data):
        probe = Probe(self._startup_info)
        probe.probe_link(link_data)


    def _probe_error(self, exc):
        self._startup_info.logger.critical(exc)


    def _probe_finish(self, arg):
        cli_output.OK("PROBING COMPLETE")


    def _probe_pool_init(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        mp.current_process().name = "Probe"


    def poll_targets(self):
        available_cpus = len(os.sched_getaffinity(0))
        probes_pool = mp.Pool(
            processes=available_cpus,
            initializer=self._probe_pool_init)
        while True:
            if self._connection.poll():
                link_data = self._connection.recv_bytes().decode('utf-8')
                if link_data != "Finder Complete":
                    link_data = json.loads(link_data)
                    probes_pool.apply_async(
                        func=self.run_probe, 
                        args=(link_data,),
                        callback=self._probe_finish,
                        error_callback=self._probe_error)
                else:
                    break
        probes_pool.close()
        probes_pool.join()
