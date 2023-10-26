import pdb
import re
import json
import time 
import requests.exceptions as exc
import urllib.parse as urlparse
from logs.custom_logging import CustomFormatter as cf
from utils.init_support import CustomProcess 

class Finder:

    def __init__(self, startup, connection, ignore_links=[]) -> None:
        self._startup = startup
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
        self._response_data["url"].append(response.request.url)
        self._response_data["request_headers"].append(response.request.headers)
        self._response_data["status_code"].append(response.status_code)
        self._response_data["reason"].append(response.reason)
        self._response_data["response_headers"].append(response.headers)
        self._response_data["apparent_encoding"].append(response.apparent_encoding)
        self._response_data["cookies"].append(response.cookies)
        self._response_data["content"].append(response.text)
        self._response_data["history"].append(response.history)
        self._response_data["elapsed_time"].append(response.elapsed.total_seconds())


    def _extract_links_from(self, url) -> list:
        try:
            response = self._startup.session.get(
                url, 
                timeout=self._startup.args["request_timeout"])

            response.raise_for_status()
            self._startup.logger.info(cf.GREEN + url + cf.RESET)
            query = urlparse.urlparse(url).query
            print(query)
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
        if url == None:
            url = self._startup.args["target_url"] 
        href_links = self._extract_links_from(url)
        time.sleep(self._startup.args["request_delay"])
        for link in href_links:
            link = urlparse.urljoin(url, link)
            if "#" in link:
                link = link.split("#")[0]
            if self._startup.args["target_url"] in link \
                and link not in self._response_data["url"] \
                and link not in self._links_to_ignore:
                    self._crawl(link)
