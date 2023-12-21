import websockets, asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
from utils.init_support import CustomProcess


class WebSocketServer:

    def __init__(self):
        self._connected = set()
        self._HOST_NAME = ""
        self._PORT = 3000
        self._name = "WebSocket Server"


    def run(self):
        websocket_process = CustomProcess(
            self._run_websocket_server,
            name=self._name)
        websocket_process.start()
    

    async def _run_websocket_server(self):
        async with websockets.serve(
            self._echo, 
            self._HOST_NAME, self._PORT):
            await asyncio.Future()


    async def _echo(self, websocket, path):
        # websocket.debug = True
        try:
            while True:
                link_data = await websocket.recv()
                if link_data == "BROWSER":
                    self._connected.add(websocket)
                    # browser_websocket = websocket
                else:
                    for conn in self._connected: 
                        await conn.send(link_data)
                # await asyncio.sleep(2)
                # print(dir(websocket))
                # print(len(websocket.messages))
        except websockets.exceptions.ConnectionClosed:
            print(websocket.close_reason)


class FindAndProbeHTTPServer:

    def __init__(self, host, port):
        self._host_port = (host, port)
        self._name = "HTTP Server"


    def run(self):
        http_process = CustomProcess(
            self._run_http_server,
            name=self._name)
        http_process.start()


    def _run_http_server(self):
        http_server = HTTPServer(
            self._host_port,
            FindAndProbeHandler)
        http_server.serve_forever()


class FindAndProbeHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        path = self.path
        if path == "/index.html":
            mimetype = "text/html"
        elif path == "/table_format.scss":
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
