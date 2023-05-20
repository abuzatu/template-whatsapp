"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger

from cli.cli_read_messages import CLI

from whatsapp.read_messages import ReadMessages

DEBUG = False


def main(debug: bool) -> None:
    """Run the main function."""
    request_logger.info(
        f"Start __main__ for Whatsapp ReadMessages with sys.argv={sys.argv}"
    )
    cli = CLI(sys.argv)
    print(cli)
    rm = ReadMessages()
    if debug:
        # set by hand
        rm.set_inputs_manually(
            contacts=["Harsh Colleague Vinay"],
        )
    else:
        # set from CLI
        rm.set_inputs_from_cli(cli)
    print(rm)
    # rm.fit()
    rm.quit_driver()


if __name__ == "__main__":
    main(DEBUG)
