"""CLI for when we want to read messages."""

from typing import List, Optional
from utils.logger import request_logger


class CLI:
    """class CLI.

    Create an object with the parameters passed.
    """

    def __init__(self, sys_argv: List[str]) -> None:
        """Initialize."""
        self.contacts: Optional[List[str]] = self._get_contacts(sys_argv)

    def __str__(self) -> str:
        """Build a string, to allow to print."""
        result = "From CLI retrieved: " f"contacts='{self.contacts}', "
        return result

    def _get_contacts(self, sys_argv: List[str]) -> Optional[List[str]]:
        """Get the list of contacts, either groups or individuals.

        To which we want to send the same message.
        """
        try:
            if sys_argv[1]:
                input_file_name = sys_argv[1]
                request_logger.debug(f'Reading contacts from file="{input_file_name}"')
                # open the input file in read mode
                # with encoding to be able to read the emojis
                with open(input_file_name, "r", encoding="utf8") as f:
                    contacts = [contact.strip() for contact in f.readlines()]
        except IndexError:
            request_logger.error(
                "Please provide contacts file name as the first argument!"
            )
            return None
        request_logger.info(f"contacts={contacts}")
        return contacts
