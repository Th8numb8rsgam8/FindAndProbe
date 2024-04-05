from . import *
import sqlite3
import re, time
import requests.exceptions as exc
import urllib.parse as urlparse


class Finder:

    def __init__(self, startup, connection, queue) -> None:
        self._startup = startup
        self.db_con = sqlite3.connect(startup.db_path)
        self._connection = connection
        self._queue = queue

        res = self.db_con.execute(f'''
            SELECT Endpoint FROM main_table 
            WHERE Hostname = "{self._startup.hostname}";''')
        self._links_to_ignore = [url[0] for url in res.fetchall()]


    def run(self) -> None:
        # self._crawl()
        finder_process = CustomProcess(
            self._crawl,
            name="Finder Process")
        finder_process.start()


    def _store_response_info(self, response) -> None:

        if response.url not in self._links_to_ignore:

            # store data in main_table
            query_string = urlparse.urlparse(response.url).query
            query_dict = urlparse.parse_qs(query_string, keep_blank_values=True)
            query_parameters = " ".join(query_dict.keys())

            self._links_to_ignore.append(response.url)
            self.db_con.execute(f'''
                INSERT INTO {self._startup.database_tables["Main"]}
                    (Hostname, Endpoint, method, path_url, 
                    reason, apparent_encoding, elapsed_time, query_parameters)
                VALUES
                    ("{self._startup.hostname}", "{response.url}", 
                    "{response.request.method}", "{response.request.path_url}", 
                    "{response.reason}", "{response.apparent_encoding}", 
                    {response.elapsed.total_seconds()}, "{query_parameters}");
                ''')
            self.db_con.commit()

            # store HTTP headers data in two different tables
            http_headers = {
                "Requests": response.request.headers,
                "Responses": response.headers}
            for table, headers in http_headers.items():
                columns = [col[1] for col in self.db_con.execute(f'''
                    PRAGMA table_info({self._startup.database_tables[table]})
                    ''')]

                names = []
                values = []
                names.extend(["Hostname", "Endpoint"])
                values.extend([self._startup.hostname, response.url])

                for name, val in headers.items():
                    if name not in columns:
                        self.db_con.execute(f'''
                            ALTER TABLE {self._startup.database_tables[table]}
                            ADD COLUMN "{name}" TEXT;
                        ''')
                        self.db_con.commit()
                    names.append(name)
                    values.append(val)

                names = "('" + "', '".join(names) + "')"
                values = "('" + "', '".join(values) + "')"
                self.db_con.execute(f'''
                    INSERT INTO {self._startup.database_tables[table]}
                    {names} VALUES {values}; 
                ''')
                self.db_con.commit()

            # store cookie data in its own table
            for cookie in response.cookies:
                cookie_data = {
                    "Hostname": self._startup.hostname,
                    "Endpoint": response.url,
                    "comment": cookie.comment,
                    "comment_url": cookie.comment_url,
                    "discard": cookie.discard,
                    "domain": cookie.domain,
                    "domain_initial_dot": cookie.domain_initial_dot,
                    "domain_specified": cookie.domain_specified,
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
                    "version": cookie.version
                }

                remove_empty = []
                [remove_empty.append(name) for name, val in cookie_data.items() if val is None]
                [cookie_data.pop(i) for i in remove_empty]
                cookie_data = {key: str(val) for key, val in cookie_data.items()}

                names = "('" + "', '".join(cookie_data.keys()) + "')"
                values = "('" + "', '".join(cookie_data.values()) + "')"
                self.db_con.execute(f'''
                    INSERT INTO {self._startup.database_tables["Cookies"]}
                    {names} VALUES {values}; 
                ''')
                self.db_con.commit()


    def _send_response_to_websocket(self, response) -> None:

        response_record = {
            "sender": "Finder",
            "request_headers":{},
            "response_headers": {},
            "cookies": []
        }

        response_record["url"] = response.url
        response_record["method"] = response.request.method
        response_record["path_url"] = response.request.path_url
        response_record["status_code"] = response.status_code
        response_record["reason"] = response.reason
        response_record["apparent_encoding"] = response.apparent_encoding
        response_record["elapsed_time"] = response.elapsed.total_seconds()

        query_string = urlparse.urlparse(response.url).query
        query_dict = urlparse.parse_qs(query_string, keep_blank_values=True)
        response_record["query_parameters"] = query_dict

        for name, val in response.request.headers.items():
            response_record["request_headers"][name] = val
        for name, val in response.headers.items():
            response_record["response_headers"][name] = val
        for cookie in response.cookies:
            response_record["cookies"].append({
                "comment": cookie.comment,
                "comment_url": cookie.comment_url,
                "discard": cookie.discard,
                "domain": cookie.domain,
                "domain_initial_dot": cookie.domain_initial_dot,
                "domain_specified": cookie.domain_specified,
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
        asyncio.run(self._send_finder(json.dumps(response_record)))


    async def _send_finder(self, link_data):
        URL = f"ws://{self._startup.WEBSOCKETS_IP}:{self._startup.WEBSOCKETS_PORT}"
        async with websockets.connect(URL) as websocket:
            await websocket.send(link_data)


    def _extract_links_from(self, url) -> list:
        try:
            response = self._startup.session.get(
                url, 
                timeout=self._startup.args["request_timeout"])
            response.raise_for_status()
            self._startup.logger.info(cf.GREEN + url + cf.RESET)
            to_probe = json.dumps({
                "url": url, 
                "response": response.text,
                "status_code": response.status_code})
            self._connection.send_bytes(to_probe.encode('utf-8'))
            self._send_response_to_websocket(response)
            self._store_response_info(response)
            return re.findall(
                '(?:href=")(.*?)"',
                response.content.decode(errors="ignore"))
        except (
            exc.Timeout,
            exc.HTTPError,
            exc.ReadTimeout,
            exc.ConnectionError,
            exc.TooManyRedirects) as e:
            self._startup.logger.warning(str(e) + " " + url)
            return []
        except exc.MissingSchema as e:
            self._startup.logger.critical(str(e))
            self._queue.put("Fatal Exception")


    def _crawl(self, url=None) -> None:
        tgt_url = url if url is not None else self._startup.args["target_url"]
        href_links = self._extract_links_from(tgt_url)
        time.sleep(self._startup.args["request_delay"])
        for link in href_links:
            link = urlparse.urljoin(tgt_url, link)
            link, _ = urlparse.urldefrag(link)
            if self._startup.hostname in link \
                and link not in self._links_to_ignore:
                    self._crawl(link)
        if url is None:
            self._connection.send_bytes("Finder Complete".encode('utf-8'))
