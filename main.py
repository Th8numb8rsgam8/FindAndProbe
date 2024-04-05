from find_and_probe import *

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    try:
        host_address = platform_check()
        initialize_processes(host_address)

    except KeyboardInterrupt as e:
        cli_output.FATAL(e)
