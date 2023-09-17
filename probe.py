import pdb
import json
import time 
import threading
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib.parse as urlparse 

class Probe:

    def __init__(self, startup, connection):
        self.startup = startup 
        self.__connection = connection

        poller = threading.Thread(target=self.__probe_targets, daemon=True)
        poller.name = "Probe Inquisitor"
        poller.start()


    def __probe_targets(self):
        print("PROBE")
        while True:
            if self.__connection.poll():
                data = self.__connection.recv_bytes().decode('utf-8')
                data = json.loads(data)
                self.startup.logger.warning(data["url"])

            # data = self.startup.queue.get(block=False)
            # data = json.loads(data)
            # print(data)
            # self.finder.startup.logger.warning(data["url"])


    def __extract_forms(self, response):
        parsed_html = BeautifulSoup(response, "html5lib")
        return parsed_html.findAll("form")


    def __submit_form(self, form, value, url):

        action = form.get("action")
        post_url = urlparse.urljoin(url, action)
        method = form.get("method")
        inputs_list = form.findAll("input")
        post_data = {}
        for input_item in inputs_list:
            input_name = input_item.get("name")
            input_type = input_item.get("type")
            input_value = input_item.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if method == 'POST':
            return self.startup.session.post(post_url, data=post_data)
        return self.startup.session.get(post_url, params=post_data)


    def __test_xss_in_link(self, url):
        xss_test_script = "<script>alert('test')</script>"
        url = url.replace("=", "=" + xss_test_script)
        response = self.startup.session.get(url)
        return xss_test_script.encode() in response.content


    def __test_xss_in_form(self, form, url):
        xss_test_script = "<sCript>alert('test')</scriPt>"
        response = self.__submit_form(form, xss_test_script, url)
        time.sleep(self.startup.args["request_delay"])
        return xss_test_script.encode() in response.content


    def __probe_link(self, link, response):
        forms = self.__extract_forms(response)
        for form in forms:
            is_vulnerable_to_xss = self.__test_xss_in_form(form, link)
            pdb.set_trace()
            if is_vulnerable_to_xss:
                self.startup.logger.debug("[***] XSS discovered in " + link + " in the following form")
                # print(form)

        # if "=" in link:
        #     print("[+] Testing " + link)
        #     is_vulnerable_to_xss = self.__test_xss_in_link(link)
        #     if is_vulnerable_to_xss:
        #         print("[***] Discovered XSS in " + link)
