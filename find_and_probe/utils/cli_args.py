import typing
import argparse
import http


class ArgumentDict(typing.TypedDict):
    target_url: str
    request_timeout: float
    request_delay: float
    ignore_codes: typing.List[int]
    show_browser: bool


class CLIArgs:

    def __init__(self) -> None:

        # default CLI argument values
        self._default_req_timeout: float = 5.0
        self._default_req_delay: float = 3.0
        http_status_list = list(http.HTTPStatus)
        self._http_status_vals: typing.List[int] = [status.value for status in http_status_list]

        # collect argument values
        self._argument_values: ArgumentDict
        self._collect_arguments()


    @property
    def argument_values(self) -> ArgumentDict:
        return self._argument_values


    def _collect_arguments(self) -> None:
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
            default=self._default_req_timeout,
            help="Time for client to wait between sending request & receiving response.")
        cli_parser.add_argument(
            "-d", "--request-delay",
            dest="request_delay",
            type=float, 
            default=self._default_req_delay,
            help="Time (in seconds) for client to wait before sending another request.")
        cli_parser.add_argument(
            "-c", "--ignore-codes",
            metavar="404 405",
            dest="ignore_codes",
            type=int, 
            nargs="*",
            choices=self._http_status_vals,
            help="HTTP response codes to ignore from probing target links.")
        cli_parser.add_argument(
            "-b", "--browser",
            dest="show_browser",
            action="store_true",
            help="Flag to pull up the browser to view target results")
        cli_parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
        self._argument_values = vars(cli_parser.parse_args())
