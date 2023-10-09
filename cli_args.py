import argparse
import http

class CLIArgs:

    def __init__(self):

        # default CLI argument values
        self.__default_req_timeout = 5.0
        self.__default_req_delay = 3.0
        self.argument_values = None
        http_status_list = list(http.HTTPStatus)
        self.__http_status_vals = [status.value for status in http_status_list]


    def collect_arguments(self):
        cli_parser = argparse.ArgumentParser(
            prog="Find'n Probe",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=
                '''
                The purpose of this application is to find injection 
                points & to probe them w/ specialized payloads.
                ''')
        cli_parser.add_argument(
            "target_url", 
            metavar="http(s)://target.com",
            type=str, 
            help="Target URL for probing.")
        cli_parser.add_argument(
            "-t", "--request-timeout",
            dest="request_timeout",
            type=float, 
            default=self.__default_req_timeout,
            help="Time for client to wait between sending request & receiving response.")
        cli_parser.add_argument(
            "-d", "--request-delay",
            dest="request_delay",
            type=float, 
            default=self.__default_req_delay,
            help="Time (in seconds) for client to wait before sending another request.")
        cli_parser.add_argument(
            "-c", "--ignore-codes",
            metavar="404 405",
            dest="ignore_codes",
            type=int, 
            nargs="*",
            choices=self.__http_status_vals,
            help="HTTP response codes to ignore from probing target links.")
        cli_parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
        self.argument_values = vars(cli_parser.parse_args())
