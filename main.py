import pdb
import signal, platform
import multiprocessing as mp
from utils.cli_args import *
from utils.init_support import * 
from components import finder, poller
from components.servers import FindAndProbeHTTPServer, WebSocketServer


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    host_system = platform.system()
    if host_system == "Linux":
        mp.set_start_method("fork")
    else:
        mp.set_start_method("spawn")
    startup_info = FindAndProbeInit()

    HOST_NAME = "192.168.192.131"
    PORT = 8080

    http_server = FindAndProbeHTTPServer(HOST_NAME, PORT)
    http_server.run()
    websocket_server = WebSocketServer()
    websocket_server.run()

    finder_pipe, poller_pipe = mp.Pipe(duplex=True)
    finder = finder.Finder(startup_info, finder_pipe)
    poller = poller.Poller(startup_info, poller_pipe)
    finder.run()
    poller.run()
