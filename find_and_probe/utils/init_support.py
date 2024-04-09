import os, json 
import sqlite3
import requests
from .cli_args import CLIArgs as CLI
import sys, signal, asyncio
import logging.config
from ..logs.custom_logging import cli_output
from ..logs import LOGGING_SETTINGS
import multiprocessing as mp
import urllib.parse as urlparse 


def signal_handler(sig, frame):
    cli_output.FATAL(
        f"\n{mp.current_process().name} EXITED w/ {signal.strsignal(sig)}\n")


class SigExc(Exception):
    pass


class FindAndProbeInit:

    def __init__(self) -> None:
        self.database_tables = {
            "Main": "main_table",
            "Requests": "request_headers", 
            "Responses": "response_headers", 
            "Cookies": "cookie_details",
            "Probes": "probe_results"}
        self.session = requests.Session()
        self.WEBSOCKETS_IP, self.WEBSOCKETS_PORT = ("localhost", 3000)
        self.db_path = os.path.join(os.getcwd(), "database", "targets_db.db")

        # initialize CLI argument inputs
        user_input = CLI()
        user_input.collect_arguments()
        self.args = user_input.argument_values
        self.hostname = urlparse.urlparse(self.args["target_url"]).hostname

        # initialize logger
        f = open(LOGGING_SETTINGS)
        logging_configs = json.load(f)
        logging.config.dictConfig(logging_configs)
        self.logger = logging.getLogger()

        # initialize & record target name in target database
        self._initialize_db()


    def _initialize_db(self):
        if not os.path.isdir("database"):
            os.mkdir("database")

        con = sqlite3.connect(self.db_path)
        try:
            for key, tbl_name in self.database_tables.items():
                con.execute(f'''
                    CREATE TABLE IF NOT EXISTS {tbl_name}
                    (Hostname TEXT,
                     Endpoint TEXT PRIMARY KEY);
                    ''')
                con.commit()
                if key == "Main":
                    col_names = [
                        {"name": "method", "data_type": "TEXT"},
                        {"name": "path_url", "data_type":  "TEXT"}, 
                        {"name": "reason",  "data_type": "TEXT"}, 
                        {"name": "apparent_encoding", "data_type": " TEXT"},
                        {"name": "elapsed_time", "data_type": "REAL"},
                        {"name": "query_parameters", "data_type": "TEXT"},
                    ]

                    for col_info in col_names:
                        con.execute(f'''
                            ALTER TABLE {tbl_name} 
                            ADD COLUMN {col_info["name"]} {col_info["data_type"]};
                            ''')
                        con.commit()
                elif key == "Cookies":
                    col_names = [
                        {"name": "comment", "data_type": "TEXT"},
                        {"name": "comment_url", "data_type": "TEXT"},
                        {"name": "discard", "data_type": "TEXT"},
                        {"name": "domain", "data_type": "TEXT"},
                        {"name": "domain_initial_dot", "data_type": "TEXT"},
                        {"name": "domain_specified", "data_type": "TEXT"},
                        {"name": "expires", "data_type": "INTEGER"},
                        {"name": "nonstandard_attr", "data_type": "TEXT"},
                        {"name": "has_nonstandard_attr", "data_type": "TEXT"},
                        {"name": "is_expired", "data_type": "TEXT"},
                        {"name": "name", "data_type": "TEXT"},
                        {"name": "path", "data_type": "TEXT"},
                        {"name": "path_specified", "data_type": "TEXT"},
                        {"name": "port", "data_type": "INTEGER"},
                        {"name": "port_specified", "data_type": "TEXT"},
                        {"name": "rfc2109", "data_type": "TEXT"},
                        {"name": "secure", "data_type": "TEXT"},
                        {"name": "value", "data_type": "TEXT"},
                        {"name": "version", "data_type": "REAL"}
                    ]
                    for col_info in col_names:
                        con.execute(f'''
                            ALTER TABLE {tbl_name} 
                            ADD COLUMN {col_info["name"]} {col_info["data_type"]};
                            ''')
                        con.commit()

        except sqlite3.OperationalError as e:
            self.logger.warning(str(e))

        finally:
            con.close()


class CustomProcess(mp.Process):

    def __init__(self, my_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exec_func = my_func
        self._is_async = asyncio.iscoroutinefunction(my_func)


    def _process_handler(self, sig, frame):
        raise SigExc


    def run(self):
        signal.signal(signal.SIGINT, self._process_handler)
        try:
            asyncio.run(self._exec_func()) if self._is_async else self._exec_func()
        except SigExc:
            cli_output.FATAL(f"\n{mp.current_process().name} EXITED\n")
