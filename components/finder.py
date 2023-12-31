import pdb
import re, json, time
import asyncio, websockets
import requests.exceptions as exc
import urllib.parse as urlparse
from logs.custom_logging import CustomFormatter as cf
from utils.init_support import CustomProcess 


class Finder:

    def __init__(self, startup, connection, ignore_links=[]) -> None:
        self._startup = startup
        self._hostname = urlparse.urlparse(self._startup.args["target_url"]).hostname
        self._connection = connection
        self._links_to_ignore = ignore_links
        self._response_data = {
            "method": [],
            "path_url": [],
            "url": [],
            "request_headers": [],
            "status_code": [],
            "reason": [],
            "response_headers": [],
            "apparent_encoding": [],
            "cookies": [],
            "content": [],
            "history": [],
            "elapsed_time": []}


    def run(self) -> None:
        # self._crawl()
        finder_process = CustomProcess(
            self._crawl,
            name="Finder Process")
        finder_process.start()


    def _store_response_info(self, response) -> None:
        self._response_data["method"].append(response.request.method)
        self._response_data["path_url"].append(response.request.path_url)
        self._response_data["request_headers"].append(response.request.headers)
        self._response_data["status_code"].append(response.status_code)
        self._response_data["reason"].append(response.reason)
        self._response_data["response_headers"].append(response.headers)
        self._response_data["apparent_encoding"].append(response.apparent_encoding)
        self._response_data["cookies"].append(response.cookies)
        self._response_data["content"].append(response.text)
        self._response_data["history"].append(response.history)
        self._response_data["elapsed_time"].append(response.elapsed.total_seconds())

        response_record = {
            "sender": "Finder",
            "request_headers":{},
            "response_headers": {},
            "cookies": []
        }
        response_record["method"] = response.request.method
        response_record["path_url"] = response.request.path_url
        for name, val in response.request.headers.items():
            response_record["request_headers"][name] =val
        response_record["status_code"] = response.status_code
        response_record["reason"] = response.reason
        for name, val in response.headers.items():
            response_record["response_headers"][name] = val
        response_record["apparent_encoding"] = response.apparent_encoding
        for cookie in response.cookies:
            response_record["cookies"].append({
                "comment": cookie.comment,
                "comment_url": cookie.comment_url,
                "discard": cookie.discard,
                "domain": cookie.domain,
                "domain_initial_dot": cookie.domain_initial_dot,
                "domain_speficied": cookie.domain_specified,
                "expires": cookie.expires,
                "nonstandard_attr": cookie.get_nonstandard_attr(cookie.name),
                "has_nonstandard_attr": cookie.has_nonstandard_attr(cookie.name),
                "is_expired": cookie.is_expired(),
                "name": cookie.name,
                "path": cookie.path,
                "path_specified": cookie.path_specified,
                "port": cookie.port,
                "port_specified": cookie.port_specified,
                "rfc2109": cookie.rfc2109,
                "secure": cookie.secure,
                "value": cookie.value,
                "version": cookie.version})
        response_record["content"] = response.text
        response_record["elapsed_time"] = response.elapsed.total_seconds()
        asyncio.run(self._send_finder(json.dumps(response_record)))


    async def _send_finder(self, link_data):
        URL = "ws://192.168.192.131:3000"
        async with websockets.connect(URL) as websocket:
            await websocket.send(link_data)


    def _extract_links_from(self, url) -> list:
        try:
            self._response_data["url"].append(url)
            response = self._startup.session.get(
                url, 
                timeout=self._startup.args["request_timeout"])
            response.raise_for_status()
            self._startup.logger.info(cf.GREEN + url + cf.RESET)
            # query = urlparse.urlparse(url).query
            to_probe = json.dumps({
                "url": url, 
                "response": response.text,
                "status_code": response.status_code})
            self._connection.send_bytes(to_probe.encode('utf-8'))
            self._store_response_info(response)
            return re.findall(
                '(?:href=")(.*?)"',
                response.content.decode(errors="ignore"))
        except (
            exc.Timeout,
            exc.HTTPError,
            exc.ReadTimeout,
            exc.ConnectionError,
            exc.TooManyRedirects,
            exc.RequestException) as e:
            self._startup.logger.warning(str(e) + " " + url)
            return []


    def _crawl(self, url=None) -> None:
        tgt_url = url if url is not None else self._startup.args["target_url"]
        href_links = self._extract_links_from(tgt_url)
        time.sleep(self._startup.args["request_delay"])
        for link in href_links:
            link = urlparse.urljoin(tgt_url, link)
            link, _ = urlparse.urldefrag(link)
            if self._hostname in link \
                and link not in self._response_data["url"] \
                and link not in self._links_to_ignore:
                    self._crawl(link)
        if url is None:
            self._connection.send_bytes("Finder Complete".encode('utf-8'))
