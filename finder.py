import pdb
import re
import json
import time
import threading
import multiprocessing as mp
import requests.exceptions as exc
import urllib.parse as urlparse 

class Finder:
    startup = None
    connection = None

    @classmethod
    def initialize(cls, startup, connection) -> None:
        cls.startup = startup
        cls.connection = connection


    def __init__(self, ignore_links=[]) -> None:
        self.__links_to_ignore = ignore_links
        self.__response_data = {
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

        search_thread = threading.Thread(target=self.__crawl)
        search_thread.name = "Finder Thread"
        search_thread.start()


    def __store_response_info(self, response):
        self.__response_data["method"].append(response.request.method)
        self.__response_data["path_url"].append(response.request.path_url)
        self.__response_data["url"].append(response.request.url)
        self.__response_data["request_headers"].append(response.request.headers)
        self.__response_data["status_code"].append(response.status_code)
        self.__response_data["reason"].append(response.reason)
        self.__response_data["response_headers"].append(response.headers)
        self.__response_data["apparent_encoding"].append(response.apparent_encoding)
        self.__response_data["cookies"].append(response.cookies)
        self.__response_data["content"].append(response.text)
        self.__response_data["history"].append(response.history)
        self.__response_data["elapsed_time"].append(response.elapsed.total_seconds())


    def __extract_links_from(self, url):
        try:
            response = Finder.startup.session.get(
                url, 
                timeout=Finder.startup.args["request_timeout"])
            response.raise_for_status()
            to_probe = json.dumps({"url": url, "response": response.text})
            # Finder.startup.queue.put(to_probe)
            Finder.connection.send_bytes(to_probe.encode('utf-8'))
            self.__store_response_info(response)
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
            Finder.startup.logger.warning(str(e) + " " + url)
            return [] 


    def __crawl(self, url=None):
        if url == None:
            url = Finder.startup.args["target_url"] 
        href_links = self.__extract_links_from(url)
        time.sleep(Finder.startup.args["request_delay"])
        for link in href_links:
            link = urlparse.urljoin(url, link)
            if "#" in link:
                link = link.split("#")[0]
            if Finder.startup.args["target_url"] in link \
                and link not in self.__response_data["url"] \
                and link not in self.__links_to_ignore:
                    Finder.startup.logger.info(link)
                    self.__crawl(link)
