"""Read latest messages in a loop."""

from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
from pathlib import Path
import re
import time
from typing import Dict, List

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from cli.cli_send_message import CLI
from utils.logger import request_logger
from trading.parse_InvestorsWizard import Parse_InvestorsWizard
from trading.parse_PipsGainer_v2 import Parse_PipsGainer_v2 as Parse_PipsGainer
from trading.parse_ParamountInfoTech import Parse_ParamountInfoTech
from whatsapp.message import Message
from whatsapp.web_driver import Driver

from configs.settings import (
    WAIT_FOR_SEARCH_BOX,
    WAIT_FOR_QR_CODE_SCAN,
    WAIT_AFTER_EACH_CONTACT,
    NUM_FIRST_COUNTERS_TO_SKIP,
    NUM_LATEST_MESSAGES_TO_READ,
    SAVE_SCREENSHOT,
    SAVE_HTML,
    FILE_ORDERS_LOG,
)


class ReadMessages:
    """Class ReadMessages."""

    def __init__(self) -> None:
        """Initialize."""
        self.driver = Driver().fit()
        self.driver.get("https://web.whatsapp.com")
        request_logger.debug("ReadMessages.init() is done.")

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
        dict_contact_messages: Dict[str, List[Message]] = {}

        # we want a continuous repeating loop, so using a while True
        # but if I close the loop with control+C, we want the driver to quit cleanly
        # using a try-except
        try:
            # check if file where we log the orders exists
            if not Path(FILE_ORDERS_LOG).is_file():
                # file does not exist
                id_order = 0
            else:
                # file exists, let's open and count the lines
                file = open(FILE_ORDERS_LOG, "r")
                lines = file.readlines()
                # print(len(lines))
                last_line = lines[-1].rstrip("\n")
                # print(f"last_line={last_line}")
                padded_str = last_line.split(",")[0].replace("id=", "")
                id_order = int(padded_str.lstrip("0"))
                print(f"id_order={id_order}")
                file.close()
            # now open the file in append mode
            # if file does not exist, it is recreated
            file = open(FILE_ORDERS_LOG, "a")

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
                    if counter % 10 == 0:
                        # pass
                        print(f"... {str(counter).zfill(3)}, {pd.Timestamp.now()}")
                    if counter % 1 == 0:
                        request_logger.debug(
                            f"Start for contact={contact}, counter={counter}, "
                            f"{len(dict_contact_messages[contact])} previous messages, "
                            f"at datetime={pd.Timestamp.now()}"
                        )
                    # we can show the messages that exist so far
                    for i in range(len(dict_contact_messages[contact])):
                        message = dict_contact_messages[contact][i]
                        request_logger.debug(f"Already message i={i}: {message}")
                    request_logger.debug("Start search_box()")
                    self.search_box(contact)
                    request_logger.debug("Start get_contact()")
                    time.sleep(0)
                    self.get_contact(contact)
                    request_logger.debug("Start receive_messages()")
                    time.sleep(0)
                    messages = self.receive_messages(
                        contact, counter, NUM_LATEST_MESSAGES_TO_READ
                    )
                    request_logger.debug(f"Getting back {len(messages)}:")
                    # loop through the messages and find those that are not yet processed
                    # for now using brute force to compare to all previous messages
                    for i in range(len(messages)):
                        message = messages[i]
                        request_logger.debug(f"Received message i={i}: {message}")
                        if message is None or message in dict_contact_messages[contact]:
                            request_logger.debug(
                                "message already in the list, do nothing"
                            )
                            continue
                        # if here, the message is not in the list, so we process it
                        request_logger.info(f"New     message i={i}: {message}")
                        # add to the dictionary of new message
                        dict_contact_messages[contact].append(message)
                        # check if the message can be interpret as a signal to trade
                        # skip the first few, as they refer to trades given before
                        # we started this; why not > 1?
                        # as I see sometimes it sees only 2 messages at first trial
                        if counter <= NUM_FIRST_COUNTERS_TO_SKIP:
                            continue
                        actual_message = message.actual_message
                        request_logger.debug(
                            "Building a list of orders from the actual_message="
                            f"{actual_message}"
                        )
                        if contact == "Meisha Investors Wizard":
                            orders = Parse_InvestorsWizard().fit(actual_message)
                        elif contact == "PipsGainer Research":
                            orders = Parse_PipsGainer().fit(actual_message)
                        elif contact == "Harsh Colleague Vinay":
                            orders = Parse_PipsGainer().fit(actual_message)
                        elif contact == "Vinay Signals PipsGainer":
                            orders = Parse_PipsGainer().fit(actual_message)
                        elif contact == "Akib Alam Paramount InfoSoft Fost InfoTech":
                            orders = Parse_ParamountInfoTech().fit(actual_message)
                        elif contact == "+44 7309 966580":
                            orders = Parse_ParamountInfoTech().fit(actual_message)
                        elif contact == "+44 7465 614471":
                            orders = Parse_PipsGainer().fit(actual_message)
                        elif contact == "+44 7465 660053":
                            orders = Parse_InvestorsWizard().fit(actual_message)
                        else:
                            request_logger.warning(
                                f"contact{contact} not known, " "so can not build orders."
                            )
                        request_logger.debug("Showing orders built")
                        for i, o in enumerate(orders):
                            id_order += 1
                            o.set_id(id_order)
                            print(o)
                            # append to the file
                            file.write(o.__str__() + "\n")
                    request_logger.debug("End receive_messages()")
                    file.flush()  # Flush the buffer to write the data after one contact
                    if counter % 1 == 0:
                        request_logger.debug(
                            f"End for contact={contact}, counter={counter}, "
                            f"{len(dict_contact_messages[contact])} previous messages, "
                            f"at datetime={pd.Timestamp.now()}, "
                            f"will wait {WAIT_AFTER_EACH_CONTACT} before next contact."
                        )
                    time.sleep(WAIT_AFTER_EACH_CONTACT)
        except KeyboardInterrupt:
            request_logger.error("Ctrl+C was pressed, so stopping.")
        finally:
            file.close()
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
        request_logger.debug(f"Start search box: xpath={xpath}")
        # go to the search box
        box = WebDriverWait(self.driver, WAIT_FOR_SEARCH_BOX).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        request_logger.debug(f"box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.debug(f"again1 box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.debug(f"again2 box={box}")
        if box is None:
            box = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            request_logger.debug(f"again3 box={box}")
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
        request_logger.debug(f"contact={contact}, type={type(contact)}")
        # box.send_keys(contact)
        # box.send_keys(Keys.ENTER)
        # box.send_keys(Keys.RETURN)
        # box.send_keys(contact, Keys.RETURN)
        box.send_keys(contact, Keys.SHIFT, Keys.RETURN)
        time.sleep(1)
        request_logger.debug(f"End search box: xpath={xpath}")

    def get_contact(self, contact: str) -> None:
        """Select the contact found.

        It is a span with the title of the contact.
        """
        xpath = "//span" f'[@title="{contact}"]'
        request_logger.debug(f"Start get_contact: xpath={xpath}")
        contact_element = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # click on it
        contact_element.click()
        time.sleep(1)
        request_logger.debug(f"End get_contact: xpath={xpath}")

    def receive_messages(self, contact: str, counter: int, N: int) -> List[Message]:
        """Receive messages."""
        request_logger.debug(
            f"Start receive_messages(contact={contact}, counter={counter})"
        )
        # this returns the latest message in a chat
        xpath = (
            "//div"
            '[@tabindex="-1"]'
            '[@class="n5hs2j7m oq31bsqd gx1rr48f qh5tioqs"]'
            '[@data-tab="8"]'
            '[@role="application"]'
            # '[@aria-label="Message list. Press right arrow key on a message to open message context menu."]' # noqa
        )
        request_logger.debug(f"Search for latest conversation: xpath={xpath}")
        counter_str = str(counter).zfill(3)
        text = ""
        text += "\n\n\n"
        text += f"******** Start {counter_str}, {pd.Timestamp.now()}, {contact} ********\n"  # noqa
        conversation = WebDriverWait(self.driver, WAIT_FOR_QR_CODE_SCAN).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        text += f"counter_str={counter_str}\n"
        request_logger.debug(text)
        # latest message
        t = conversation.text
        request_logger.debug(f"type(t)={type(t)}, len(t)={len(t)}, t={t}")
        # time.sleep(3)
        if SAVE_SCREENSHOT:
            self.driver.save_screenshot(f"./open/screenshot_{counter_str}.png")
        element_html = conversation.get_attribute("innerHTML")  # exact HTML content
        request_logger.debug(f"element_html={element_html}")
        if SAVE_HTML:
            with open(f"./output/source_code_outer_{counter_str}.html", "w") as f:
                f.write(element_html)
        soup = BeautifulSoup(element_html, "html.parser")
        request_logger.debug(f"soup={soup}")
        request_logger.debug(f"soup.prettify()={soup.prettify()}")
        # div1_all
        # div1=soup.find_all(class_="_1-FMR message-in focusable-list-item")[-1]
        div1_all = soup.find_all("div", attrs={"class": re.compile("_1-FMR.*")})
        request_logger.debug(f"len(div1_all)={len(div1_all)}")
        messages = self.get_messages(
            div1_all,
            contact=contact,
            N=N,
        )
        request_logger.debug(f"messages={messages}")
        return messages

    def get_messages(self, div1_all: Tag, contact: str, N: int) -> List[Message]:
        """Return a list of the N last messages from div1.

        Reason we want more is that since last check maybe more messages appear.
        """
        request_logger.debug(
            f"Start get the last {N} messages from div1_all, " f"for contact={contact}"
        )
        messages = []
        N = min(N, len(div1_all))
        for i in range(1, N + 1):
            messages.append(self.get_message(div1_all, index=-i, contact=contact))
        return messages

    def get_message(self, div1_all: Tag, index: int, contact: str) -> Message:
        """Return a message from one div1."""
        request_logger.debug(f"get_messsage(contact={contact}, index={index})")
        # div1
        div1 = div1_all[index]
        request_logger.debug(f"div1.div={div1.div}")
        request_logger.debug(f"div1.text={div1.text}")
        request_logger.debug(f"div1.text={div1.text}")
        # div2_all
        div2_all = div1.find_all(class_="copyable-text")
        request_logger.debug(f"len(div2_all)={len(div2_all)}")
        request_logger.debug(f"div2_all={div2_all}")
        if len(div2_all) == 0:
            # this can happen if the last message is deleted
            request_logger.debug(
                "len(div2_all)=0, "
                "it can happen if last message is deleted, "
                "or if you have been removed from the group, "
                "so sleep a second and continue"
            )
            return None
        # div2
        div2 = div2_all[0]
        request_logger.debug(f"div2.div={div2.div}")
        request_logger.debug(f"div2.text={div2.text}")
        request_logger.debug(f"div2.prettify()={div2.prettify()}")
        # metadata
        metadata = div2["data-pre-plain-text"]
        request_logger.debug(f"metadata={metadata}")
        # e.g. '[2:56 pm, 28/10/2022] Harsh Colleague Vinay: '
        datetime_str = metadata.split("]")[0].split("[")[-1]
        request_logger.debug(f"datetime_str={datetime_str}")
        # e.g. '2:56 pm, 28/10/2022'
        # e.g. 0:24 pm, 10/11/2022 -> this has a problem as 0 must appear as 12
        # for both am and pm, but avoid for 10.
        if datetime_str[0] == "00":
            datetime_str = datetime_str.replace("00:", "12:")
        request_logger.debug(f"datetime_str={datetime_str}")
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        if "am" in datetime_str or "pm" in datetime_str:
            # I has hours from 0 to 12
            my_format = "%I:%M %p, %d/%m/%Y"
        else:
            # H has hours from 0 to 23
            my_format = "%H:%M, %d/%m/%Y"
        request_logger.debug(f"datetime_str={datetime_str}")
        # e.g. build datetime object, e.g. Timestamp('2022-10-28 14:56:00')
        datetime = pd.to_datetime(datetime_str, format=my_format)
        request_logger.debug(f"datetime={datetime}")
        author = metadata.split("]")[1][1:-2]
        # e.g. 'Harsh Colleague Vinay'
        request_logger.debug(f"author={author}")
        text = "\n"
        text += f"datetime={datetime}\n"
        text += f"author={author}\n"
        div3 = div2.find_all(class_="quoted-mention _11JPr")
        if len(div3) == 0:
            quoted_message = ""
        else:
            # .rstrip() to eliminate also all spaces from the end
            quoted_message = div3[0].text.rstrip()
        # eliminate all the enter and tabs, just put spaces in between
        # to be on one line, easier to read and to analyse
        quoted_message = " ".join(quoted_message.split())
        request_logger.debug(f"quoted_message={quoted_message}")
        text += f"quoted_message={quoted_message}\n"
        # div4_all = div2.find_all(class_="_11JPr selectable-text copyable-text")
        # below more generic, as this code _11JPr changes over time
        div4_all = div2.find_all(
            class_=lambda c: c and "selectable-text copyable-text" in c
        )
        if len(div4_all) == 0:
            return None
        div4 = div4_all[0]
        actual_message = div4.text
        # eliminate all the enter and tabs, just put spaces in between
        # to be on one line, easier to read and to analyse
        actual_message = " ".join(actual_message.split())
        request_logger.debug(
            f"actual_message={actual_message}, time={pd.Timestamp.now()}"
        )
        text += f"actual_message={actual_message}\n"
        # print(text)
        message = Message(contact, author, datetime, actual_message, quoted_message)
        request_logger.debug(f"message={message}")
        return message
