"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger

from cli.cli_send_message import CLI
from whatsapp.send_message import SendMessage

DEBUG = False


def main(debug: bool) -> None:
    """Run the main function."""
    request_logger.info(
        f"Start __main__ for Whatsapp SendMessage with sys.argv={sys.argv}"
    )
    cli = CLI(sys.argv)
    print(cli)
    sm = SendMessage()
    if debug:
        # set by hand
        sm.set_inputs_manually(
            contacts=["Harsh Colleague Vinay"],
            message="Hello!",
            attachment_image=None,
            attachment_text=None,
        )
    else:
        # set from CLI
        sm.set_inputs_from_cli(cli)
    print(sm)
    sm.fit()
    sm.quit_driver()


if __name__ == "__main__":
    main(DEBUG)
