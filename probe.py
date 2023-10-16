import pdb
import time 
from bs4 import BeautifulSoup
import urllib.parse as urlparse 


class Probe:

    def __init__(self, startup):
        self.__startup = startup
        with open("xss-payload-list.txt") as f:
            self.__xss_payload_list = f.read().split("\n")
            self.__xss_payload_list.pop()


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
        if method.upper() == 'POST':
            return self.__startup.session.post(post_url, data=post_data)
        return self.__startup.session.get(post_url, params=post_data)


    def __test_xss_in_link(self, url):
        xss_test_script = "<script>alert('test')</script>"
        url = url.replace("=", "=" + xss_test_script)
        response = self.__startup.session.get(url)
        return xss_test_script.encode() in response.content


    def __test_xss_in_form(self, form, url):
        for idx, xss_payload in enumerate(self.__xss_payload_list):
            self.__startup.logger.info(
                f"PROBING: PAYLOAD {idx} -> TARGET - {url}",
                extra={"payload": xss_payload})
            response = self.__submit_form(form, xss_payload, url)
            time.sleep(self.__startup.args["request_delay"])
            code_ignored = response.status_code in self.__startup.args["ignore_codes"]
            # if code_ignored:
            #     self.__startup.logger.critical(
            #         f"CODE {response.status_code} \
            #         XSS FAILED PROBE WITH: {xss_payload} ON {url} FORM")
            # else:
            #     self.__startup.logger.info(
            #         f"CODE {response.status_code} \
            #         XSS SUCCESSFUL PROBE WITH: {xss_payload} ON {url} FORM")


    def probe_link(self, link_data):
        link, response = link_data["url"], link_data["response"]
        forms = self.__extract_forms(response)
        for form in forms:
            is_vulnerable_to_xss = self.__test_xss_in_form(form, link)
            # if is_vulnerable_to_xss:
            #     self.__startup.logger.info("[***] XSS discovered in " + link + " in the following form")
        # self.__startup.logger.info("DONE")

        # if "=" in link:
        #     print("[+] Testing " + link)
        #     is_vulnerable_to_xss = __test_xss_in_link(link)
        #     if is_vulnerable_to_xss:
        #         print("[***] Discovered XSS in " + link)
