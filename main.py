import pdb
import subprocess
import signal, platform
import multiprocessing as mp
from utils.cli_args import *
from utils.init_support import * 
from logs.custom_logging import cli_output
from components import finder, poller
from components.servers import *


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    host_system = platform.system()
    HOST_NAME, HTTP_PORT = ("", 8080)

    try:
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

        startup_info = FindAndProbeInit()
        http_server = FindAndProbeHTTPServer(
            startup_info.WEBSOCKETS_PORT,
            (HOST_NAME, HTTP_PORT), 
            FindAndProbeHandler)
        http_server.run()
        websocket_server = WebSocketServer(startup_info.WEBSOCKETS_PORT)
        websocket_server.run()

        finder_pipe, poller_pipe = mp.Pipe(duplex=True)
        finder = finder.Finder(startup_info, finder_pipe)
        poller = poller.Poller(startup_info, poller_pipe)
        finder.run()
        poller.run()

    except KeyboardInterrupt as e:
        cli_output.FATAL(e)
