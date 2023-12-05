import pdb
import json
import signal
import asyncio
import websockets
import platform
import requests
import multiprocessing as mp
import logging.config
from utils.cli_args import *
from http.server import HTTPServer, SimpleHTTPRequestHandler
from utils.init_support import signal_handler, CustomProcess
from components.finder import Finder
from components.poller import Poller


def run_http_server():
    HOST_NAME = "192.168.192.131"
    PORT = 8080
    http_server = HTTPServer(
        (HOST_NAME, PORT), 
        FindAndProbeHandler)
    http_server.serve_forever()


async def run_websocket_server():
    HOST_NAME = ""
    PORT = 3000
    async with websockets.serve(echo, HOST_NAME, PORT):
        await asyncio.Future()


connected = set()
async def echo(websocket, path):
    # websocket.debug = True
    try:
        while True:
            link_data = await websocket.recv()
            if link_data == "BROWSER":
                connected.add(websocket)
                # browser_websocket = websocket
            else:
                for conn in connected: 
                    await conn.send(link_data)
            # await asyncio.sleep(2)
            # print(dir(websocket))
            # print(len(websocket.messages))
    except websockets.exceptions.ConnectionClosed:
        print(websocket.close_reason)


class FindAndProbeHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        path = self.path
        if path == "/index.html":
            mimetype = "text/html"
        elif path == "/main_page.css":
            mimetype = "text/css"
        elif path == "/index.js":
            mimetype = "text/javascript"
        else:
            path = "/index.html"
            mimetype = "text/html"

        self.send_response(200, "OK")
        self.send_header("Content-Type", mimetype)
        self.end_headers()
        with open(path[1:], 'rb') as f:
            self.wfile.write(f.read())


class FindAndProbeInit:

    def __init__(self) -> None:
        self.session = requests.Session()

        # initialize CLI argument inputs
        user_input = CLIArgs()
        user_input.collect_arguments()
        self.args = user_input.argument_values

        # initialize logger
        f = open("logs/logging_settings.json")
        logging_configs = json.load(f)
        logging.config.dictConfig(logging_configs)
        self.logger = logging.getLogger()


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

    http_process = CustomProcess(
        run_http_server,
        name="HTTP Server")
    http_process.start()

    websocket_process = CustomProcess(
        run_websocket_server,
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
