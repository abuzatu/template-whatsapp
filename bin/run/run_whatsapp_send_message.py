"""Run to send whatsapp messages with or without attachment to several contacts."""

import sys

from utils.logger import request_logger

from cli.cli_send_message import CLI
from whatsapp.send_message import SendMessage


def main() -> None:
    """Run the main function."""
    request_logger.info(f"Start __main__ for Whatsapp with sys.argv={sys.argv}")
    cli = CLI(sys.argv)
    print(cli)
    sm = SendMessage()
    if True:
        sm.set_inputs_from_cli(cli)
    else:
        sm.set_inputs_manually(
            contacts=["Harsh Colleague Vinay"],
            message="Hello!",
            attachment_image=None,
            attachment_text=None,
        )
    print(sm)
    print(type(sm.contacts), sm.contacts)
    print(type(sm.message), sm.message)
    sm.fit()
    print("A")
    sm.quit_driver()
    print("B")
    sm.quit_driver()


if __name__ == "__main__":
    main()
