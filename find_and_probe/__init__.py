import subprocess, queue
import signal, platform
import multiprocessing as mp
from .components.finder import Finder
from .components.poller import Poller
from .components.servers import *
from .utils.cli_args import *
from .utils.init_support import * 
from .logs.custom_logging import cli_output


def platform_check():

    host_system = platform.system()
    HOST_NAME, HTTP_PORT = ("", 8080)

    if host_system == "Linux":
        mp.set_start_method("fork")
        hostname_cmd = subprocess.run(
            ["hostname", "-I"], 
            capture_output=True, 
            text=True)
        if hostname_cmd.returncode == 0:
            HOST_NAME = hostname_cmd.stdout.strip()
        else:
            raise KeyboardInterrupt("INVALID HOST NAME")
    else:
        mp.set_start_method("spawn")

    return HOST_NAME, HTTP_PORT


def initialize_processes(host_address):

    HOST_NAME, HTTP_PORT = host_address

    with mp.Manager() as manager:
        shared_queue = manager.Queue()

        startup_info = FindAndProbeInit()
        http_server = FindAndProbeHTTPServer(
            startup_info.WEBSOCKETS_PORT,
            (HOST_NAME, HTTP_PORT), 
            FindAndProbeHandler)
        http_server.run()
        websocket_server = WebSocketServer(startup_info.WEBSOCKETS_PORT)
        websocket_server.run()

        finder_pipe, poller_pipe = mp.Pipe(duplex=True)
        finder_proc = Finder(startup_info, finder_pipe, shared_queue)
        poller_proc = Poller(startup_info, poller_pipe, shared_queue)
        finder_proc.run()
        poller_proc.run()

        while True:
            child_processes = mp.active_children()
            if len(child_processes) > 1:
                try:
                    result = shared_queue.get(block=False)
                    if result == "Fatal Exception":
                        [child.terminate() for child in 
                         child_processes if "SyncManager" not in child.name]
                except queue.Empty as e:
                    pass
            else:
                break


__all__ = [
    "platform_check", 
    "initialize_processes", 
    "signal", 
    "cli_output",
    "signal_handler"]
