import pdb
import os
import time 
import http
import glob
import requests.exceptions as exc
from bs4 import BeautifulSoup
from logs.custom_logging import CustomFormatter as cf
import urllib.parse as urlparse 


class Probe:

    def __init__(self, startup):
        self._startup = startup
        self._xss_payload_list = None
        self._sql_payloads = {}
        self._response_codes = {status.value: status.phrase for status in http.HTTPStatus}

        self._get_xss_payloads()
        self._get_sql_payloads()


    def _get_sql_payloads(self):
        sql_files = glob.glob("payloads/sql_payloads/*.txt")
        for sql_file in sql_files:
            with open(sql_file) as f:
                payload_list = f.read().split("\n")
                payload_list.pop()
                _, file_name = os.path.split(sql_file)
                payload_type = file_name.split(".")[0]
                self._sql_payloads[payload_type] = payload_list


    def _get_xss_payloads(self):
        with open("payloads/xss-payload-list.txt") as f:
            self._xss_payload_list = f.read().split("\n")
            self._xss_payload_list.pop()


    def _extract_forms(self, response):
        parsed_html = BeautifulSoup(response, "html5lib")
        return parsed_html.findAll("form")


    def _submit_form(self, form, value, url):
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

        try:
            if method.upper() == 'POST':
                return self._startup.session.post(post_url, data=post_data)
            return self._startup.session.get(post_url, params=post_data)
        except (
            exc.Timeout,
            exc.HTTPError, 
            exc.ReadTimeout, 
            exc.ConnectionError, 
            exc.TooManyRedirects,
            exc.RequestException) as e:
            self._startup.logger.warning(str(e) + " " + url)
            return None


    def _test_xss_in_link(self, url):
        xss_test_script = "<script>alert('test')</script>"
        url = url.replace("=", "=" + xss_test_script)
        response = self._startup.session.get(url)
        return xss_test_script.encode() in response.content


    def _sql_probe_form(self, form, url) -> bool:
        for payload_type, payload_list in self._sql_payloads.items():
            for sql_payload in payload_list:
                response = self._submit_form(form, sql_payload, url)
                time.sleep(self._startup.args["request_delay"])
                if response is not None:
                    code_ignored = response.status_code in self._startup.args["ignore_codes"]
                    if not code_ignored:
                        response = " ".join(
                            [str(response.status_code), 
                            self._response_codes[response.status_code]])
                        self._startup.logger.info(
                            f"SUCCESSFUL PROBE: {cf.BOLD + url + cf.RESET}", 
                            extra=
                            {
                                "payload": cf.GREEN + sql_payload + cf.RESET,
                                "response": cf.CYAN + response + cf.RESET
                            })
                        return True
                else:
                    return False

        return False


    def _xss_probe_form(self, form, url) -> bool:
        for idx, xss_payload in enumerate(self._xss_payload_list):
            response = self._submit_form(form, xss_payload, url)
            time.sleep(self._startup.args["request_delay"])
            if response is not None:
                code_ignored = response.status_code in self._startup.args["ignore_codes"]
                if code_ignored:
                    pass
                    # self._startup.logger.critical(
                    #     f"CODE {response.status_code} \
                    #     XSS FAILED PROBE WITH: {xss_payload} ON {url} FORM")
                else:
                    response = " ".join(
                        [str(response.status_code), 
                        self._response_codes[response.status_code]])
                    self._startup.logger.info(
                        f"SUCCESSFUL PROBE: {cf.BOLD + url + cf.RESET}", 
                        extra=
                        {
                            "payload": cf.GREEN + xss_payload + cf.RESET,
                            "response": cf.CYAN + response + cf.RESET
                        })
                    return True
            else:
                return False

        return False


    def probe_link(self, link_data):
        link, response = link_data["url"], link_data["response"]
        forms = self._extract_forms(response)
        for form in forms:
            vulnerable_to_xss = self._xss_probe_form(form, link)
            vulnerable_to_sql = self._sql_probe_form(form, link)
            # if is_vulnerable_to_xss:
            #     self.__startup.logger.info("[***] XSS discovered in " + link + " in the following form")
        # self.__startup.logger.info("DONE")

        # if "=" in link:
        #     print("[+] Testing " + link)
        #     is_vulnerable_to_xss = __test_xss_in_link(link)
        #     if is_vulnerable_to_xss:
        #         print("[***] Discovered XSS in " + link)
