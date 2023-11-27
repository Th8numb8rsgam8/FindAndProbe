import pdb
import signal, platform
import multiprocessing as mp
from utils.cli_args import *
from utils.init_support import * 
from components import finder, poller, servers


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    host_system = platform.system()
    if host_system == "Linux":
        mp.set_start_method("fork")
    else:
        mp.set_start_method("spawn")
    startup_info = FindAndProbeInit()

    finder_pipe, poller_pipe = mp.Pipe(duplex=True)
    finder = finder.Finder(startup_info, finder_pipe)
    poller = poller.Poller(startup_info, poller_pipe)
    finder.run()
    poller.run()

    http_process = CustomProcess(
        servers.run_http_server,
        name="HTTP Server")
    http_process.start()

    websocket_process = CustomProcess(
        servers.run_websocket_server,
        name="WebSocket Server")
    websocket_process.start()


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
