"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger

# from cli.cli_send_message import CLI
from whatsapp.send_message import SendMessage


def main() -> None:
    """Run the main function."""
    request_logger.info(f"Start __main__ for Whatsapp with sys.argv={sys.argv}")
    # cli = CLI(sys.argv)
    # print(cli)
    sm = SendMessage()
    sm.set_inputs(
        contacts=["Meisha Investors Wizard"],
        message="How has trading been going?",
        attachment_image=None,
        attachment_text=None,
    )
    sm.fit()


if __name__ == "__main__":
    main()
