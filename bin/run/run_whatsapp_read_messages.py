"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger

from cli.cli_read_messages import CLI

# from whatsapp.send_message import SendMessage

DEBUG = False


def main(debug: bool) -> None:
    """Run the main function."""
    request_logger.info(
        f"Start __main__ for Whatsapp ReadMessages with sys.argv={sys.argv}"
    )
    cli = CLI(sys.argv)
    print(cli)


if __name__ == "__main__":
    main(DEBUG)
