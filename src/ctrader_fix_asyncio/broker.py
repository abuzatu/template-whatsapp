"""Module for Broker for Fix API."""

# python
import asyncio
import random
import re
import socket
import time

# our modules


def checksum(message: str) -> str:
    """Calculates the checksum used for validating fix messages."""
    sum = 0
    message_array = bytes(message, "UTF-8")
    for i in message_array:
        sum += i
    return str((sum % 256)).zfill(3)


def random_string() -> str:
    """Generate random string for sendersubid."""
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    random_s = ""
    for i in range(9):
        random_index = random.randint(0, len(characters) - 1)
        random_s += characters[random_index]
    return random_s


def tcp_ping(host, port):
    """Check internet connection via ping."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # set timeout to 2 seconds
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False


class Broker:
    """Broker class to create instances of brokers with cTrader.

    e.g. IC Markets, ICM Capital, etc.

    This does only one asset for now.
    """

    def __init__(
        self,
        broker,
        hostname,
        price_reader,
        price_writer,
        trade_reader,
        trade_writer,
        sendercompid,
        price_sendersubid,
        trade_sendersubid,
        price_msgseqnum,
        trade_msgseqnum,
        bid,
        ask,
        username,
        password,
        bid_label,
        ask_label,
        price_chk,
        trade_chk,
        positions,
        increment_entry,
        total_lots,
        opened_positions,
    ):
        """Init."""
        self.broker = broker
        self.hostname = hostname
        self.price_reader = price_reader
        self.price_writer = price_writer
        self.trade_reader = trade_reader
        self.trade_writer = trade_writer
        self.sendercompid = sendercompid
        self.price_msgseqnum = price_msgseqnum
        self.trade_msgseqnum = trade_msgseqnum
        self.price_sendersubid = price_sendersubid
        self.trade_sendersubid = trade_sendersubid
        self.bid = bid
        self.ask = ask
        self.username = username
        self.password = password
        self.bid_label = bid_label
        self.ask_label = ask_label
        self.price_chk = price_chk
        self.trade_chk = trade_chk
        self.positions = positions
        self.increment_entry = increment_entry
        self.total_lots = total_lots
        self.opened_positions = opened_positions

    """Fix message constructors"""

    def price_login(self) -> str:
        """Login to price."""
        bl = f'35=A|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|98=0|108=1|141=Y|553={self.username}|554={self.password}|'
        self.price_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def trade_login(self) -> str:
        """Login to trade."""
        bl = f'35=A|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|98=0|108=1|141=Y|553={self.username}|554={self.password}|'
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def price_heartbeat(self) -> str:
        """Heartbeat to price."""
        bl = f'35=0|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|'
        self.price_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def trade_heartbeat(self) -> str:
        """Heartbeat to trade."""
        bl = f'35=0|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|'
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def market_data_request(self) -> str:
        """Request to market data."""
        bl = f'35=V|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=QUOTE|50={self.price_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|262=GBPJPY|263=1|264=1|265=1|146=1|55=7|267=2|269=0|269=1|'
        self.price_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def request_positions(self) -> str:
        """Request positions."""
        bl = f'35=AN|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|710={self.trade_msgseqnum}|'
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def buy_market_order(self) -> str:
        """Buy market order."""
        bl = f'35=D|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|11={self.trade_msgseqnum}|55=2|54=1|60={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|38={self.increment_entry.get()}|40=1|'
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def sell_market_order(self, posid: int) -> str:
        """Sell market order to close the position int which was created via a buy."""
        bl = f'35=D|34={self.trade_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE|50={self.trade_sendersubid}|52={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|11={self.trade_msgseqnum}|55=2|54=2|60={time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())}|38={self.increment_entry.get()}|40=1|721={posid}|'
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    """Login to price and trade streams."""

    async def price_login_main(self):
        """Login to price stream on port 5201."""
        try:
            print(f"Logging into {self.broker} PRICE stream...")
            self.price_reader, self.price_writer = await asyncio.open_connection(
                self.hostname, 5201
            )
            self.price_sendersubid = random_string()
            self.price_writer.write(
                bytes(self.price_login() + self.market_data_request(), "UTF-8")
            )
            asyncio.create_task(self.send_price_heartbeat())
            await self.read_price_data()
        except Exception as e:
            await asyncio.sleep(1)
            print(f"there was a connection refused error! {e}")

    async def trade_login_main(self):
        """Login to trade stream on port 5202."""
        try:
            print(f"Logging into {self.broker} TRADE stream...")
            self.trade_reader, self.trade_writer = await asyncio.open_connection(
                self.hostname, 5202
            )
            self.trade_sendersubid = random_string()
            self.trade_writer.write(bytes(self.trade_login(), "UTF-8"))
            asyncio.create_task(self.send_trade_heartbeat())
            await self.read_trade_data()
        except Exception as e:
            await asyncio.sleep(1)
            print(f"TRADE connection refused login error! {e}")

    """Heartbeat methods for price and trade streams."""

    async def send_price_heartbeat(self) -> None:
        """Price heartbeat used to send heartbeat to server every 1 second."""
        while True:
            try:
                self.price_writer.write(bytes(self.price_heartbeat(), "UTF-8"))
            except Exception as e:
                print(f"There was a PRICE heartbeat error... {e}")
                break
            await asyncio.sleep(1)

    async def send_trade_heartbeat(self) -> None:
        """Trade heartbeat used to send heartbeat to server every 1 second.

        In adition, also request the positions.
        """
        while True:
            try:
                self.trade_writer.write(
                    bytes(self.trade_heartbeat() + self.request_positions(), "UTF-8")
                )
            except Exception as e:
                print(f"There was a TRADE heartbeat error... {e}")
                break
            await asyncio.sleep(1)

    """Button click methods."""

    async def buy(self) -> None:
        """Buy button action that executes the buy orders."""
        bo = ""
        for i in range(int(self.total_lots.get())):
            bo += self.buy_market_order()
        try:
            self.trade_writer.write(bytes(bo, "UTF-8"))
        except Exception as e:
            print(f"{self.broker} buying not working! {e}")

    async def closeall(self) -> None:
        """Closes all positions related to the symbol (that is in the app)."""
        ca = ""
        for p in self.positions:
            ca += self.sell_market_order(p)
        try:
            self.trade_writer.write(bytes(ca, "UTF-8"))
        except Exception as e:
            print(f"Unable to close all positions {self.broker}! {e}")
        self.positions.clear()

    async def read_price_data(self) -> None:
        """Reads data asynchronously from the price stream."""
        while True:
            try:
                header = await self.price_reader.read(16)
                header = header.decode().replace("\u0001", "|")
                if index := re.search("9=(\\d+)", header):
                    index = int(index.group(1))
                    ti = index - 1 if index < 100 else index
                    second = await self.price_reader.read(ti + 7)
                    full_message = header + second.decode().replace("\u0001", "|")
                    if "35=W" in full_message:
                        prices = re.findall("270=([^|]*)", full_message)
                        self.bid = self.bid_label["text"] = prices[0]
                        self.ask = self.ask_label["text"] = prices[1]
                    print(full_message)
            except Exception as e:
                print(
                    f"PRICE Unable to read from server for {self.broker} "
                    f"{e} {self.price_msgseqnum}"
                )
                if tcp_ping("www.google.com", 80):
                    asyncio.create_task(self.price_login_main())
                    break
            await asyncio.sleep(0.001)

    async def read_trade_data(self) -> None:
        """Reads data asynchronously from the trade stream."""
        while True:
            try:
                header = await self.trade_reader.read(16)
                header = header.decode().replace("\u0001", "|")
                if index := re.search("9=(\\d+)", header):
                    index = int(index.group(1))
                    ti = index - 1 if index < 100 else index
                    second = await self.trade_reader.read(ti + 7)
                    full_message = header + second.decode().replace("\u0001", "|")
                    if "704=" in full_message:
                        self.increment_entry.delete(0, "end")
                        self.increment_entry.insert(
                            0, str(re.search("704=(\d+)", full_message).group(1))
                        )
                    if "35=AP" in full_message:
                        if match := re.search("721=(\\d+)", full_message):
                            pid = match.group(1)
                            self.positions.append(
                                pid
                            ) if pid not in self.positions else None
                            if match2 := re.search("727=(\\d+)", full_message):
                                self.opened_positions["text"] = (
                                    str(match2.group(1)) + "  Positions"
                                )
                        else:
                            self.opened_positions["text"] = "0  Positions"
                    # if '35=AP' not in full_message:
                    print(full_message)
            except Exception:
                print(f"TRADE Unable to read from server for {self.broker}")
                if tcp_ping("www.google.com", 80):
                    asyncio.create_task(self.trade_login_main())
                    break
            await asyncio.sleep(0.001)
