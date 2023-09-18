import pdb
import os
import json
import time 
import threading
from bs4 import BeautifulSoup
import multiprocessing as mp
import urllib.parse as urlparse 

class Probe:
    startup = None
    connection = None
    probes_pool = None
    poller = None

    @classmethod
    def initialize(cls, startup, connection) -> None:
        available_cpus = len(os.sched_getaffinity(0))
        cls.probes_pool = mp.Pool(processes=available_cpus)
        cls.startup = startup
        cls.connection = connection
        cls.poller = threading.Thread(target=cls.probe_targets)
        cls.poller.name = "Probe Inquisitor"
        cls.poller.start()


    @classmethod
    def probe_targets(cls):
        pdb.set_trace()
        while True:
            if Probe.connection.poll():
                link_data = Probe.connection.recv_bytes().decode('utf-8')
                link_data = json.loads(link_data)
                Probe.startup.logger.warning(link_data["url"])
                # Probe.probes_pool.apply_async(
                #     func=Probe._Probe__probe_link,
                #     args=(link_data,))


    @classmethod
    def __extract_forms(cls, response):
        parsed_html = BeautifulSoup(response, "html5lib")
        return parsed_html.findAll("form")


    @classmethod
    def __submit_form(cls, form, value, url):
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
            return Probe.startup.session.post(post_url, data=post_data)
        return Probe.startup.session.get(post_url, params=post_data)


    @classmethod
    def __test_xss_in_link(cls, url):
        xss_test_script = "<script>alert('test')</script>"
        url = url.replace("=", "=" + xss_test_script)
        response = Probe.startup.session.get(url)
        return xss_test_script.encode() in response.content


    @classmethod
    def __test_xss_in_form(cls, form, url):
        xss_test_script = "<sCript>alert('test')</scriPt>"
        response = cls.__submit_form(form, xss_test_script, url)
        time.sleep(Probe.startup.args["request_delay"])
        return xss_test_script.encode() in response.content


    @classmethod
    def __probe_link(cls, link_info):
        link, respone = link_info["url"], link_info["response"]
        Probe.startup.logger.debug("PROBING LINK" + link)
        forms = cls.__extract_forms(response)
        for form in forms:
            is_vulnerable_to_xss = cls.__test_xss_in_form(form, link)
            if is_vulnerable_to_xss:
                Probe.startup.logger.debug("[***] XSS discovered in " + link + " in the following form")

        # if "=" in link:
        #     print("[+] Testing " + link)
        #     is_vulnerable_to_xss = self.__test_xss_in_link(link)
        #     if is_vulnerable_to_xss:
        #         print("[***] Discovered XSS in " + link)
