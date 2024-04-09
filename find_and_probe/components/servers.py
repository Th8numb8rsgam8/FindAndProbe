from . import *
from ..frontend import FRONTEND_DIR
import sass
from http.server import HTTPServer, SimpleHTTPRequestHandler


class WebSocketServer:

    def __init__(self, port: int):
        self._connected = set()
        self._HOST_NAME = ""
        self._PORT = port
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


class FindAndProbeHTTPServer(HTTPServer):

    def __init__(self, websockets_port, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._name = "HTTP Server"
        self.frontend_dir = FRONTEND_DIR
        self.WEBSOCKETS_PORT = websockets_port


    def run(self):
        http_process = CustomProcess(
            super().serve_forever,
            name=self._name)
        http_process.start()


class FindAndProbeHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        path = self.path
        if path == "/index.html":
            mimetype = "text/html"
        elif path == "/table_format.scss":
            mimetype = "text/css"
        elif path == "/index.js":
            mimetype = "text/javascript"
        elif path == "/ws_endpoint":
            mimetype = "application/json"
        else:
            path = "/index.html"
            mimetype = "text/html"

        self.send_response(200, "OK")
        self.send_header("Content-Type", mimetype)
        self.end_headers()

        if path == "/table_format.scss":
            css_string = sass.compile(
                filename=os.path.join(self.server.frontend_dir, path[1:]))
            self.wfile.write(css_string.encode("utf-8"))
        elif path == "/ws_endpoint":
            endpoint = {
                "IP": self.server.server_name, 
                "PORT": self.server.WEBSOCKETS_PORT
            }
            self.wfile.write(json.dumps(endpoint).encode("utf-8"))
        else:
            with open(os.path.join(
                self.server.frontend_dir, path[1:]), 'rb') as f:
                self.wfile.write(f.read())
