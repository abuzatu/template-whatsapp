"""Send message, either with or without attachment."""

import time
from typing import List, Optional

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from cli.cli_send_message import CLI
from utils.logger import request_logger
from whatsapp.web_driver import Driver

from configs.settings import (
    WAIT_FOR_SEARCH_BOX,
    WAIT_FOR_QR_CODE_SCAN,
)


class SendMessage:
    """Class SendMessage."""

    def __init__(self) -> None:
        """Initialize."""
        self.driver = Driver().fit()
        self.driver.get("https://web.whatsapp.com")
        request_logger.info("SendMessage.init() is done.")

    def set_inputs_manually(
        self,
        contacts: List[str],
        message: str,
        attachment_image: Optional[str],
        attachment_text: Optional[str],
    ) -> None:
        """Set inputs manually."""
        self.contacts = contacts
        self.message = message
        self.attachment_image = attachment_image
        self.attachment_text = attachment_text

    def set_inputs_from_cli(
        self,
        cli: CLI,
    ) -> None:
        """Set inputs from cli."""
        self.contacts = cli.contacts
        self.message = cli.message
        self.attachment_image = cli.attachment_image
        self.attachment_text = cli.attachment_text

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

    def quit_driver(self) -> None:
        """Quit driver (closes all windows).

        Without this, the next restart will be very slow to create the driver.
        """
        try:
            title = self.driver.title
            request_logger.info(f"Quitting driver with title={title}")
            self.driver.quit()
        except Exception as e:
            request_logger.debug(f"Driver is already quitted: {e}")

    def fit(self) -> None:
        """Fit. Send the message."""
        for contact in self.contacts:
            request_logger.info(f"Process contact={contact}")
            request_logger.info("Start search_box()")
            time.sleep(3)
            self.search_box(contact)
            request_logger.info("Start get_contact()")
            time.sleep(3)
            self.get_contact(contact)
            request_logger.info("Start send message()")
            time.sleep(3)
            self.send_message()
            request_logger.info("Start send message()")
            time.sleep(3)

        self.quit_driver()

    def search_box(self, contact: str) -> None:
        """Search box.

        Find the search box on top left, clear the content,
        copy/paste the name of our contact (group or individual).

        No need to press enter. This will list all contacts found
        by that search. We aim to give unique names, so only one is found.
        """
        xpath = (
            "//div"
            '[@contenteditable="true"]'
            '[@data-testid="chat-list-search"]'
            '[@title="Search input textbox"]'
            '[@data-tab="3"]'
        )
        request_logger.info(f"Start search box: xpath={xpath}")
        # go to the search box
        box = WebDriverWait(self.driver, WAIT_FOR_SEARCH_BOX).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        request_logger.info(f"box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.info(f"again1 box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.info(f"again2 box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.info(f"again3 box={box}")
        # clear the box if any previous info
        # needed for the further elements in the for loop
        # box.clear()
        # clear does not work, so select all, then delete
        # for linux machine like inside docker use CONTROL
        box.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        # for Mac Machines like outside Docker use COMMAND
        # box.send_keys(Keys.COMMAND + "a", Keys.DELETE)
        # the copy step from copy/paste:
        # to allow to have emojis we will copy in memory
        # pyperclip.copy(contact)
        # the paste step from copy/paste
        # would want to do control+V for Windows, or command+V for Mac
        # but command+V does not work for legacy reasons,
        # so use shift+insert instead
        # box.send_keys(Keys.SHIFT, Keys.INSERT)
        # try to send directly the text, as we do not have special characters (emoji)
        # and doing copy paste all the time does not allow other work on the computer
        # while this script is running, as it does not allow copy paste on the computer
        request_logger.info(f"contact={contact}, type={type(contact)}")
        # box.send_keys(contact)
        # box.send_keys(Keys.ENTER)
        # box.send_keys(Keys.RETURN)
        # box.send_keys(contact, Keys.RETURN)
        box.send_keys(contact, Keys.SHIFT, Keys.RETURN)
        time.sleep(1)
        request_logger.info(f"End search box: xpath={xpath}")

    def get_contact(self, contact: str) -> None:
        """Select the contact found.

        It is a span with the title of the contact.
        """
        xpath = "//span" f'[@title="{contact}"]'
        request_logger.info(f"Start get_contact: xpath={xpath}")
        contact_element = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # click on it
        contact_element.click()
        time.sleep(1)
        request_logger.info(f"End get_contact: xpath={xpath}")

    def send_message(self) -> None:
        """Write and send message."""
        request_logger.info(f"Start send message={self.message}")
        # find the message box
        xpath = (
            "//div"
            '[@title="Type a message"]'
            '[@contenteditable="true"]'
            '[@data-tab="10"]'
        )
        request_logger.info(f"message box: xpath={xpath}")
        message_box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # copy the message in memory
        # pyperclip does not work at the moment in my docker with Linux
        # pyperclip.copy(self.message)
        # paste the message in the box
        # message_box.send_keys(Keys.SHIFT, Keys.INSERT)
        message_box.send_keys(self.message, Keys.SHIFT, Keys.INSERT)
        time.sleep(0)
        # send the message by pressing enter
        message_box.send_keys(Keys.ENTER)
        time.sleep(0)
        request_logger.debug(f"End send message={self.message}")
