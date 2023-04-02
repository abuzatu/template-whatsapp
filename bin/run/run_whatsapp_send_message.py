"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger
from cli.cli_send_message import CLI


def main() -> None:
    """Run the main function."""
    request_logger.info(f"Start __main__ for Whatsapp with sys.argv={sys.argv}")
    cli = CLI(sys.argv)
    print(cli)


if __name__ == "__main__":
    main()
