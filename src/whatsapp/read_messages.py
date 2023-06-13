"""Read latest messages in a loop."""

# python
import asyncio
from asyncio.events import AbstractEventLoop
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
from pathlib import Path
from pprint import pformat
import time
from typing import Dict, List
import yaml

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# our modules
from cli.cli_send_message import CLI
from configs.settings import work_dir
from configs.assets import get_info_quantity_to_trade
from ctrader.ctrader import CTrader, get_volume_symbol
from ctrader_fix_asyncio.broker import Broker
from utils.logger import request_logger
from trading.order import Order
from trading.parse_InvestorsWizard import Parse_InvestorsWizard
from trading.parse_General import Parse_General
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

# configuration for trading with CTrader: be careful to include from demo for now
from configs.ctrader_demo import (
    HOST,
    SENDER_COMP_ID_1,
    PASSWORD_1,
    SENDER_COMP_ID_2,
    PASSWORD_2,
    CURRENCY,
    CLIENT_ID,
    DEBUG,
)

DO_CTRADER = True

# get one account from the config
CONFIG_FILE_NAME = f"{work_dir()}/src/configs/config_accounts.yaml"

# account_names = ["PGR", "Vinay", "PMT-1", "PMT-2"]
account_names = ["PGR", "Vinay", "PMT-1"]


# Open the YAML file
with open(CONFIG_FILE_NAME, "r") as file:
    # Load the YAML content
    yaml_data = yaml.load(file, Loader=yaml.FullLoader)


class ReadMessages:
    """Class ReadMessages."""

    def __init__(self, loop: AbstractEventLoop) -> None:
        """Initialize."""
        # the async event loop
        self.loop = loop
        # create the connection to several accounts
        self.accounts = {}
        for account_name in account_names:
            credentials = [c for c in yaml_data["accounts"] if c["name"] == account_name][
                0
            ]
            self.accounts[account_name] = Broker(
                credentials=credentials,
                price_sendersubid=None,
                trade_sendersubid=None,
                price_msgseqnum=1,
                trade_msgseqnum=1,
                bid=0.0,
                ask=0.0,
                positions=[],
                num_opened_positions=0,
                orders=[],
                num_opened_orders=0,
            )
            # for now we receive the prices for just one symbol
            self.accounts[account_name].set_asset(symbol="EURUSD")
        print("Demo FIX API Application - 2023")
        time.sleep(1)
        print("Create task for self.login()")
        self.loop.create_task(self.login())
        time.sleep(1)
        print("End init of Window()")

    async def set_driver(self) -> None:
        """Set driver."""
        # chrome driver
        print("Start the Chrome Driver")
        self.driver = Driver().fit()
        # self.driver = await asyncio.to_thread(Driver().fit())
        print("A")
        self.driver.get("https://web.whatsapp.com")
        print("B")
        request_logger.debug("ReadMessages.init() is done.")
        print("C")

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

    async def login(self) -> None:
        """For each of the accounts login to price and trade streams.

        The prices will come back every time there is a change.
        TO DO: not clear yet how. subscribe to several assets at the same time.
        Or how can I stop a subscription to start later a new one with other assets?

        The requests for positions and orders are sent at every heartbeat,
        then the ansewrs can come right away.
        """
        if DO_CTRADER and True:
            print("A")
            # login to the price streams for all brokers
            for account_name in self.accounts:
                print("B")
                asyncio.create_task(self.accounts[account_name].price_login())
        if DO_CTRADER and True:
            # login to the trade streams for all brokers
            for account_name in self.accounts:
                asyncio.create_task(self.accounts[account_name].trade_login())
        await asyncio.sleep(0)

    async def show(self) -> None:
        """The main while loop that keeps repeating.

        Originally it was the show window when created in the event loop.

        But no window for now. So we just wait.
        """
        # await asyncio.sleep(500)
        counter = 0
        while True:
            counter += 1
            # print("I am in show() - the for loop, refresh every 3 seconds.")
            print()
            print("************************************")
            print(f"******* COUNTER ={counter} ********")
            print("************************************")

            for account_name in self.accounts:
                # prices
                if True:
                    print(
                        f"ACCOUNT={account_name}, prices: "
                        f"asset={self.accounts[account_name].symbol}, "
                        f"bid={self.accounts[account_name].bid}, "
                        f"ask={self.accounts[account_name].ask}"
                    )
                # positions
                if True:
                    print(
                        f"ACCOUNT={account_name}, positions: "
                        f"num_opened_positions = "
                        f"{self.accounts[account_name].num_opened_positions}, "
                        f"len(positions) = {len(self.accounts[account_name].positions)}"
                    )
                    # print(f"positions = {self.accounts[account_name].positions}")
                    for position in self.accounts[account_name].positions:
                        print(f"position = {position}")
                # orders
                if True:
                    print(
                        f"ACCOUNT={account_name}, orders: "
                        f"num_opened_orders = "
                        f"{self.accounts[account_name].num_opened_orders}, "
                        f"len(orders) = {len(self.accounts[account_name].orders)}"
                    )
                    # print(f"positions = {self.accounts[account_name].positions}")
                    for order in self.accounts[account_name].orders:
                        print(f"order = {order}")

                if True and counter == 2:
                    await self.accounts[account_name].set_order_examples(
                        symbol="AUDUSD",
                        price_low=0.6700,
                        price_high=0.6800,
                        num_repeats=1,
                    )

                if True and counter == 5:
                    position_ids = await self.accounts[account_name].close_all_positions()
                    print(f"Closed all positions: position_ids={position_ids}")

                if True and counter == 6:
                    order_ids = await self.accounts[account_name].cancel_all_orders()
                    print(f"Closed all orders: order_ids={order_ids}")

                continue
            # wait 5 seconds for the current counter
            await asyncio.sleep(5)

    async def quit_driver(self) -> None:
        """Quit driver (closes all windows).

        Without this, the next restart will be very slow to create the driver.
        """
        try:
            title = self.driver.title
            request_logger.info(f"Quitting driver with title={title}")
            self.driver.quit()
        except Exception as e:
            request_logger.debug(f"Driver is already quitted: {e}")

    async def fit(self) -> None:
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

        await asyncio.sleep(0)
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
                print()
                print("************************************")
                print(f"******* COUNTER ={counter} ********")
                print("************************************")
                if counter < 10 or counter % 2 == 0:
                    # pass
                    print(f"... {str(counter).zfill(3)}, {pd.Timestamp.now()}")
                # read the messages for each contact in this loop
                for contact in self.contacts:
                    # if the first loop, then create an empty list
                    # then we can append messages to it
                    print(f"counter={counter}, contact={contact}")
                    if counter == 1:
                        dict_contact_messages[contact] = []
                    # we can choose to print a . for each loop, to let us know
                    # how fast the loops are progressing
                    if counter % 1 == 0:
                        # pass
                        print(f"... {str(counter).zfill(3)}, {pd.Timestamp.now()}")
                        for account_name in self.accounts:
                            # prices
                            if DO_CTRADER and False:
                                print(
                                    f"ACCOUNT={account_name}, prices: "
                                    f"asset={self.accounts[account_name].symbol}, "
                                    f"bid={self.accounts[account_name].bid}, "
                                    f"ask={self.accounts[account_name].ask}"
                                )
                            # positions
                            if DO_CTRADER and False:
                                print(
                                    f"ACCOUNT={account_name}, positions: "
                                    f"num_opened_positions = "
                                    f"{self.accounts[account_name].num_opened_positions}, "
                                    f"len(positions) = {len(self.accounts[account_name].positions)}"
                                )
                                # print(f"positions = {self.accounts[account_name].positions}")
                                for position in self.accounts[account_name].positions:
                                    print(f"position = {position}")
                            # orders
                            if DO_CTRADER and False:
                                print(
                                    f"ACCOUNT={account_name}, orders: "
                                    f"num_opened_orders = "
                                    f"{self.accounts[account_name].num_opened_orders}, "
                                    f"len(orders) = {len(self.accounts[account_name].orders)}"
                                )
                                # print(f"positions = {self.accounts[account_name].positions}")
                                for order in self.accounts[account_name].orders:
                                    print(f"order = {order}")

                            if DO_CTRADER and False and counter == 2:
                                await self.accounts[account_name].set_order_examples(
                                    symbol="AUDUSD",
                                    price_low=0.6700,
                                    price_high=0.6800,
                                    num_repeats=1,
                                )

                            if DO_CTRADER and False and counter == 5:
                                position_ids = await self.accounts[
                                    account_name
                                ].close_all_positions()
                                print(
                                    f"Closed all positions: position_ids={position_ids}"
                                )

                            if DO_CTRADER and False and counter == 6:
                                order_ids = await self.accounts[
                                    account_name
                                ].cancel_all_orders()
                                print(f"Closed all orders: order_ids={order_ids}")

                    # await asyncio.sleep(3)
                    # continue

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
                    # await asyncio.sleep(3)
                    # continue
                    request_logger.debug("Start search_box()")
                    await self.search_box(contact)
                    request_logger.debug("Start get_contact()")
                    await asyncio.sleep(0)
                    await self.get_contact(contact)
                    request_logger.debug("Start receive_messages()")
                    await asyncio.sleep(0)
                    messages = self.receive_messages(
                        contact, counter, NUM_LATEST_MESSAGES_TO_READ
                    )
                    request_logger.debug(f"Getting back {len(messages)}:")

                    # await asyncio.sleep(3)
                    # continue
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
                        print("******************************************************")
                        request_logger.info(f"New     message i={i}: {message}")
                        print("******************************************************")
                        # continue
                        # add to the dictionary of new message
                        dict_contact_messages[contact].append(message)
                        # check if the message can be interpret as a signal to trade
                        # skip the first few, as they refer to trades given before
                        # we started this; why not > 1?
                        # as I see sometimes it sees only 2 messages at first trial
                        if counter <= NUM_FIRST_COUNTERS_TO_SKIP:
                            continue
                        actual_message = message.actual_message
                        request_logger.info(
                            "Building a list of orders from the actual_message="
                            f"{actual_message}, and in raw format {repr(actual_message)}."
                        )
                        print(
                            "Building a list of orders from the actual_message="
                            f"{actual_message}, and in raw format {repr(actual_message)}."
                        )
                        if contact == "Meisha Investors Wizard":
                            orders = Parse_InvestorsWizard().fit(actual_message)
                        elif contact == "PipsGainer Research Signals":
                            orders = Parse_General(author="PGR").fit(actual_message)
                        elif contact == "Harsh Colleague Vinay":
                            orders = Parse_General(author="PGH").fit(actual_message)
                        elif contact == "Vinay Signals PipsGainer":
                            orders = Parse_General(author="PGV").fit(actual_message)
                        elif contact == "Akib Alam Paramount InfoSoft Fost InfoTech":
                            orders = Parse_General(author="PMT").fit(actual_message)
                        elif contact == "+44 7309 966580":
                            orders = Parse_General(author="ME1").fit(actual_message)
                        elif contact == "+44 7465 614471":
                            orders = Parse_General(author="ME2").fit(actual_message)
                        elif contact == "+44 7465 660053":
                            orders = Parse_General(author="ME3").fit(actual_message)
                        else:
                            request_logger.warning(
                                f"contact{contact} not known, " "so can not build orders."
                            )
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        request_logger.info("Showing orders built")
                        for i, o in enumerate(orders):
                            id_order += 1
                            o.set_id(id_order)
                            print(o)
                            # append to the file
                            file.write(o.__str__() + "\n")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        print("************************************************")
                        if DO_CTRADER:
                            request_logger.info("Trading orders built")
                            for i, o in enumerate(orders):
                                # continue
                                # act on the order
                                try:
                                    await self.trade_async(o)
                                except RuntimeError:
                                    print(f"WARNING! Not able to trade for order o={o}")
                    request_logger.debug("End receive_messages()")
                    file.flush()  # Flush the buffer to write the data after one contact
                    if counter % 1 == 0:
                        request_logger.debug(
                            f"End for contact={contact}, counter={counter}, "
                            f"{len(dict_contact_messages[contact])} previous messages, "
                            f"at datetime={pd.Timestamp.now()}, "
                            f"will wait {WAIT_AFTER_EACH_CONTACT} before next contact."
                        )
                    await asyncio.sleep(WAIT_AFTER_EACH_CONTACT)
        except KeyboardInterrupt:
            request_logger.error("Ctrl+C was pressed, so stopping.")
            print("Control-C")
        finally:
            print("Closing")
            file.close()
            await self.quit_driver()

    async def search_box(self, contact: str) -> None:
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
        await asyncio.sleep(1)
        request_logger.debug(f"End search box: xpath={xpath}")

    async def get_contact(self, contact: str) -> None:
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
        await asyncio.sleep(1)
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
        # await asyncio.sleep(3)
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
        # div1_all=soup.find_all(class_="_1-FMR message-in focusable-list-item")
        # div1_all = soup.find_all("div", attrs={"class": re.compile("_1-FMR.*")})
        # div1_all = soup.find_all(
        #    class_="_3sxvM message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"
        # )
        # below more generic, as this code _11JPr changes over time
        div1_all = soup.find_all(class_=lambda c: c and "focusable-list-item " in c)
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

    async def trade(self, o: Order) -> None:
        """Trade based on the order received."""
        print("Start trade")
        if o.author == "PGV" or o.author == "PGH" or o.author == "ME2":
            # Pigs Gainer Vinay
            account = SENDER_COMP_ID_2
            password = PASSWORD_2
        else:
            # Akib and everyone else
            account = SENDER_COMP_ID_1
            password = PASSWORD_1

        print("Start CTrader")
        # build trader object
        api = CTrader(
            server=HOST,
            account=account,
            password=password,
            currency=CURRENCY,
            client_id=CLIENT_ID,
            debug=DEBUG,
        )
        print("logged in")
        await asyncio.sleep(1)
        positions = api.positions()
        print(pformat(positions))
        # do the trade
        symbol = o.symbol
        # set volumes in lots
        volume = get_volume_symbol(symbol)
        datetime = o.datetime
        text = f"for {symbol} of volume={volume} lot at {datetime}"
        if o.action == "open":
            if o.direction == "buy":
                print(f"Opening trade buy {text}.")
                api.buy(symbol, volume)
            elif o.direction == "sell":
                print(f"Opening trade sell {text}.")
                api.sell(symbol, volume)
            else:
                print(f"for Open direction={o.direction} is not known for {text}.")
        elif o.action == "close":
            print(f"Closing all positions for {symbol}.")
            api.close(symbol)
        else:
            print(f"Action {o.action} not known, need open or close, for {text}.")
        await asyncio.sleep(1)
        # close the connection
        api.logout()
        await asyncio.sleep(2)
        # to be safe delete the api object
        # del api

    async def trade_async(self, o: Order) -> None:
        """Trade based on the order received."""
        print("Start trade")
        if o.author == "PGV":
            # Pips Gainer Vinay
            account_names = ["Vinay"]
        elif o.author == "PGH" or o.author == "PGR" or o.author == "ME2":
            # Pips Gainer Research. Harsh or ME2
            account_names = ["PGR"]
        elif o.author == "PMT" or o.author == "ME1":
            # Paramount Info Tech or ME1
            # account_names = ["PMT-1", "PMT-2"]
            account_names = ["PMT-1"]
        else:
            account_names = ["Vinay"]

        # do the trade
        if o.action == "open":
            for account_name in account_names:
                print(
                    f"****  Opening in account={account_name} an order "
                    f"for symbol={o.symbol} with order o={o} ******"
                )
                asyncio.create_task(
                    self.accounts[account_name].set_order(
                        symbol=o.symbol,
                        direction=o.direction,
                        order_type=o.type,
                        quantity_to_trade=get_info_quantity_to_trade(o.symbol)[1],
                        price=None if o.type == "market" else o.EPs[0],
                        position_id=None,
                    )
                )
                print(
                    f"****  Opened in account={account_name} and order "
                    f"for symbol={o.symbol} with order o={o} ******"
                )
        elif o.action == "close":
            for account_name in account_names:
                print(
                    f"****  Closing in account={account_name} the positions "
                    f"for symbol={o.symbol} with order o={o} ******"
                )
                position_ids = await self.accounts[
                    account_name
                ].close_all_positions_for_one_symbol(o.symbol)
                print(
                    f"***** Closed in account={account_name} the positions "
                    f"for symbol={o.symbol}: "
                    f"position_ids={position_ids} ****"
                )
            print(f"Action {o.action} not known, need open or close, for order = {o}")
        await asyncio.sleep(0.01)
