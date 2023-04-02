"""CLI for when we want to send messages."""

from typing import List, Optional
from utils.logger import request_logger


class CLI:
    """class CLI.

    Create an object with the parameters passed.
    """

    def __init__(self, sys_argv: List[str]) -> None:
        """Initialize."""
        self.contacts: Optional[List[str]] = self._get_contacts(sys_argv)
        self.message: Optional[str] = self._get_message(sys_argv)
        self.attachment_image: Optional[str] = self._get_attachment_image(sys_argv)
        self.attachment_text: Optional[str] = self._get_attachment_message(sys_argv)

    def __str__(self) -> str:
        """Build a string, to allow to print."""
        result = (
            "From CLI retrieved: "
            f"contacts='{self.contacts}', "
            f"message='{self.message}', "
            f"attachment_image='{self.attachment_image}', "
            f"attachment_text='{self.attachment_text}', "
        )
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

    def _get_message(self, sys_argv: List[str]) -> Optional[str]:
        """Return the same message to send to all contacts.

        Assumes only one message per file.
        """
        try:
            if sys_argv[2]:
                input_file_name = sys_argv[2]
                request_logger.debug(f'Reading message file="{input_file_name}"')
                # open the input file in read mode
                # with encoding to be able to read the emojis
                with open(input_file_name, "r", encoding="utf8") as f:
                    message = f.read().rstrip()
        except IndexError:
            request_logger.error(
                "Please provide the message file name as the second argument!"
            )
            return None
        request_logger.info(f"message={message}")
        return message

    def _get_attachment_image(self, sys_argv: List[str]) -> Optional[str]:
        """Return the name of the attachment file.

        Note it must be the full path to work for Whatsapp.
        """
        try:
            if sys_argv[3]:
                attachment_image = sys_argv[3]
                request_logger.debug(f'Using attachment image="{attachment_image}"')
        except IndexError:
            # pass is OK as it means the user does not have to send an attachment
            request_logger.warning(
                "You did not provide an image file name "
                "as the third argument, "
                "so we will not send an image as an attachement!"
            )
            attachment_image = None
        request_logger.info(f"attachment_file_name={attachment_image}")
        return attachment_image

    def _get_attachment_message(self, sys_argv: List[str]) -> Optional[str]:
        """Return the file name of the text to the attachment.

        Assumes only one message per file.
        """
        try:
            if sys_argv[4]:
                input_file_name = sys_argv[4]
                request_logger.debug(
                    f'Reading attachment message file="{input_file_name}"'
                )
                # open the input file in read mode
                # with encoding to be able to read the emojis
                with open(input_file_name, "r", encoding="utf8") as f:
                    attachment_message = f.read().rstrip()
        except IndexError:
            request_logger.error(
                "Please provide the message file name as the second argument!"
            )
            return None
        request_logger.info(f"attachment_message={attachment_message}")
        return attachment_message


# contacts = utils.get_contacts(sys.argv)
# message = utils.get_message(sys.argv)
# attachment_message = utils.get_attachment_message(sys.argv)
# attachment_file_name = utils.get_attachment_file_name(sys.argv)
