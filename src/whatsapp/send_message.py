"""Send message, either with or without attachment."""

from cli.cli_send_message import CLI
from utils.logger import request_logger
from whatsapp.web_driver import Driver


class SendMessage:
    """Class SendMessage."""

    def __init__(self, cli: CLI) -> None:
        """Initialize."""
        self.cli = cli
        self.driver = Driver().fit()

    def fit(self) -> None:
        """Fit. Send the message."""
        for contact in self.cli.contacts:
            request_logger.info(f"Process contact={contact}")

        # quit the driver (closes all windows)
        self.driver.quit()
