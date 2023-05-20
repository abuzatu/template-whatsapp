"""Read latest messages in a loop."""

import pandas as pd
import time
from typing import Dict, List

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


class ReadMessages:
    """Class ReadMessages."""

    def __init__(self) -> None:
        """Initialize."""
        self.driver = Driver().fit()
        self.driver.get("https://web.whatsapp.com")
        request_logger.info("ReadMessages.init() is done.")

    def set_inputs_manually(
        self,
        contacts: List[str],
    ) -> None:
        """Set inputs manually."""
        self.contacts = contacts

    def set_inputs_from_cli(
        self,
        cli: CLI,
    ) -> None:
        """Set inputs from cli."""
        self.contacts = cli.contacts

    def __str__(self) -> str:
        """Build a string, to allow to print."""
        result = "From CLI retrieved: " f"contacts='{self.contacts}', "
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
        """Fit. Read the messages of all contacts in a loop.

        Read once to each contact, and see if there is a new message.
        After that start over again. That way we can catch any new message,
        from several contacts, within less than one minute.

        Until we come back to the original contact, several messages may have been
        received, so we need to not only read the last message, but the latest N
        messages, with N configurable, say at 10. We need to store all messages
        processed so that we can compare all latest N messages read to what we stored
        already and see if they are there, and only if new messages to process them
        and then store then back.
        """
        # counting the number of loops we did across all contacts since script started
        counter = 0
        # storing the list of messages for each contact
        dict_contact_messages: Dict[str, List[str]] = {}

        # we want a continuous repeating loop, so using a while True
        # but if I close the loop with control+C, we want the driver to quit cleanly
        # using a try-except
        try:
            while True:
                # increase the counter of the loop to keep track
                counter += 1
                # read the messages for each contact in this loop
                for contact in self.contacts:
                    # if the first loop, then create an empty list
                    # then we can append messages to it
                    if counter == 1:
                        dict_contact_messages[contact] = []
                    # we can choose to print a . for each loop, to let us know
                    # how fast the loops are progressing
                    if counter % 1 == 0:
                        print(".")
                    if counter % 1 == 0:
                        request_logger.info(
                            f"\nStart for contact={contact}, counter={counter}, "
                            f"{len(dict_contact_messages[contact])} previous messages, "
                            f"at datetime={pd.Timestamp.now()}"
                        )
                    # we can show the messages that exist so far
                    for i in range(len(dict_contact_messages[contact])):
                        message = dict_contact_messages[contact][i]
                        request_logger.info(f"Already message i={i}: {message}")
                    request_logger.info("Start search_box()")
                    self.search_box(contact)
                    request_logger.info("Start get_contact()")
                    time.sleep(0)
                    self.get_contact(contact)
                    request_logger.info("Start receive_messages()")
                    time.sleep(1)
                    request_logger.info("End receive_messages()")
        except KeyboardInterrupt:
            request_logger.error("Ctrl+C was pressed, execute cleanup actions.")
            self.quit_driver()

dfdfd

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

    def receive_messages_once(self, contact: str) -> None:
        """Receive messages."""
        request_logger.info(f"Start receive_messages(contact={contact})")
        # either of these two xpath below seems to work to return
        # the latest message in the chat
        xpath1 = "//div" '[@class="_2gzeB"]' '[@data-testid="conversation-panel-body"]'
        xpath2 = (
            "//div"
            '[@tabindex="-1"]'
            '[@class="n5hs2j7m oq31bsqd gx1rr48f qh5tioqs"]'
            '[@data-tab="8"]'
            '[@role="application"]'
            '[@aria-label="Message list. Press right arrow key on a message to open message context menu."]'  # noqa
        )  # noqa
        request_logger.info(f"Search latest message with xpath={xpath1}")
        conversation = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
            EC.presence_of_element_located((By.XPATH, xpath1))
        )
        # latest message
        t = conversation.text
        print(f"type(t)={type(t)}")
        print(f"len(t)={len(t)}")
        print(f"t={t}")
        request_logger.info("End receive_messages()")
