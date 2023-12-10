import websockets, asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler


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


def run_http_server():
    HOST_NAME = "192.168.192.131"
    PORT = 8080
    http_server = HTTPServer(
        (HOST_NAME, PORT), 
        FindAndProbeHandler)
    http_server.serve_forever()


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
