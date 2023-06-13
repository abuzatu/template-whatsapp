"""Module for Broker for Fix API."""

# python
import asyncio
import json
import random
import re
import socket
import time
from typing import Any, Dict, List, Optional, Set, Union

# our modules
from configs.assets import assets_all, DICT_SYMBOL_ID_SYMBOL, get_info_quantity_to_trade
from configs.settings import work_dir

# Open the JSON file
filename = f"{work_dir()}/src/configs/assets.json"
with open(filename, "r") as file:
    # Load JSON data into a dictionary
    assets = json.load(file)
# print(f"assets={assets}")


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


def tcp_ping(host: str, port: int) -> bool:
    """Check internet connection via ping."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # set timeout to 2 seconds
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False


def get_time() -> str:
    """Get current time in UTC.

    Alternatively, you could use return datetime.utcnow().strftime("%Y%m%d-%H:%M:%S").
    """
    return time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())


class Broker:
    """Broker class to create instances of brokers with cTrader.

    e.g. IC Markets, ICM Capital, etc.

    This does only one asset for now.
    """

    def __init__(
        self,
        credentials: Dict[str, str],
    ):
        """Init."""
        # credentials
        self.broker = credentials["broker"]
        self.hostname = credentials["hostname"]
        self.account = credentials["account"]
        self.password = credentials["password"]
        self.type = credentials["type"]
        self.sendercompid = f"{self.type}.{self.broker}.{self.account}"
        #
        self.price_reader = None
        self.price_writer = None
        self.trade_reader = None
        self.trade_writer = None
        self.price_msgseqnum = 1
        self.trade_msgseqnum = 1
        self.price_sendersubid = ""
        self.trade_sendersubid = ""
        self.bid = 0.0
        self.ask = 0.0

        self.positions: List[Dict[str, Union[str, int, float]]] = []
        self.position_ids: Set[str] = set()
        self.num_opened_positions = 0
        self.orders: List[Dict[str, Union[str, int, float]]] = []
        self.num_opened_orders: int = 0

    def set_asset(self, symbol: str) -> None:
        """Set Asset with name and ID as specific for cTrader."""
        self.symbol = symbol
        self.symbol_id = assets[symbol]["symbol_id"]
        self.symbol_num_digits = assets[symbol]["symbol_num_digits"]
        print(
            f"symbol={self.symbol}, "
            f"symbol_id={self.symbol_id}, "
            f"symbol_num_digits={self.symbol_num_digits}"
        )

    """FIX message constructors."""

    def fix_login_to_a_stream(self, stream_name: str) -> str:
        """Login to a stream.

        Two choices: price (QUOTE) and trade (TRADE).
        """
        stream_msgseqnum = (
            self.price_msgseqnum if stream_name == "QUOTE" else self.price_msgseqnum
        )
        stream_sendersubid = (
            self.price_sendersubid if stream_name == "QUOTE" else self.trade_sendersubid
        )
        bl = (
            "35=A"
            f"|34={stream_msgseqnum}"
            f"|49={self.sendercompid}"
            "|56=cServer"
            f"|57={stream_name}"
            f"|50={stream_sendersubid}"
            f"|52={get_time()}"
            "|98=0"
            "|108=1"
            "|141=Y"
            f"|553={self.account}"
            f"|554={self.password}"
            "|"
        )
        if stream_name == "QUOTE":
            self.price_msgseqnum += 1
        else:
            self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_heartbeat_to_a_stream(self, stream_name: str) -> str:
        """Heartbeat to stream.

        Two choises: price (QUOTE) and trade (TRADE).
        """
        stream_msgseqnum = (
            self.price_msgseqnum if stream_name == "QUOTE" else self.trade_msgseqnum
        )
        stream_sendersubid = (
            self.price_sendersubid if stream_name == "QUOTE" else self.trade_sendersubid
        )
        bl = (
            "35=0"
            f"|34={stream_msgseqnum}"
            f"|49={self.sendercompid}"
            "|56=cServer"
            f"|57={stream_name}"
            f"|50={stream_sendersubid}"
            f"|52={get_time()}"
            "|"
        )
        if stream_name == "QUOTE":
            self.price_msgseqnum += 1
        else:
            self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_security_request(self) -> str:
        """Security request to learn the list of symbols and their IDs."""
        bl = (
            f"35=x|34={self.price_msgseqnum}|49={self.sendercompid}|56=cServer|57=TRADE"
            f"|50={self.price_sendersubid}"
            f"|52={get_time()}"
            f"|320=Sxo2Xlb1jzJC|559=0|"
        )
        self.price_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_market_data_request(self, symbol: str, symbol_id: int) -> str:
        """Request to market data using the price stream."""
        bl = (
            "35=V"
            f"|34={self.price_msgseqnum}"
            f"|49={self.sendercompid}"
            "|56=cServer"
            "|57=QUOTE"
            f"|50={self.price_sendersubid}"
            f"|52={get_time()}"
            f"|262={symbol}"
            "|263=1"
            "|264=1"
            "|265=1"
            "|146=1"
            f"|55={symbol_id}"
            "|267=2"
            "|269=0"
            "|269=1"
            "|"
        )
        self.price_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_request_positions(self) -> str:
        """Request positions using the trade stream."""
        bl = (
            "35=AN"  # was AF
            f"|34={self.trade_msgseqnum}"
            f"|49={self.sendercompid}"
            "|56=cServer"
            "|57=TRADE"
            f"|50={self.trade_sendersubid}"
            f"|52={get_time()}"
            f"|710={self.trade_msgseqnum}"
            "|"
        )
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_request_orders(self) -> str:
        """Request orders using the trade stream."""
        bl = (
            "35=AF"  # was AN
            f"|34={self.trade_msgseqnum}"
            f"|49={self.sendercompid}"
            "|56=cServer"
            "|57=TRADE"
            f"|50={self.trade_sendersubid}"
            f"|52={get_time()}"
            f"|584={self.trade_msgseqnum}"
            "|585=7"
            f"|225={get_time()}"  # only orders before this datetime
            "|"
        )
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_set_order(
        self,
        symbol: str,
        direction: str,
        order_type: str,
        quantity_to_trade: int,
        price: Optional[float],
        position_id: Optional[str] = None,
    ) -> str:
        """Code to create a general order.

        Field 55 corresponds to the symbol_id.
        Field 54: direction (1 = buy, 2 = sell)
        Field 38 to the quantity in unit not lots.
        Field 40: order type (1 = market order, 2 = limit order; 3 = stop order)
        Field 44: limit price only for the limit order
        Field 99: stop price only for the stop order

        If position_id specified, the order is attached to a current position.
        This is used to close the position (opposite direction, same volume),
        or a partial close (opposite direction, part of the volume),
        or to set a TP or SL.
        """
        # for each asset you need to have the id as a number
        symbol_id = assets_all[symbol]["symbol_id"]

        if direction == "buy":
            direction_id = 1
        elif direction == "sell":
            direction_id = 2
        else:
            raise ValueError

        if order_type == "market":
            order_type_id = 1
            price_info = ""
        elif order_type == "limit":
            order_type_id = 2
            # limit price
            price_info = f"|44={price}"
        elif order_type == "stop":
            order_type_id = 3
            # stop price
            price_info = f"|99={price}"
        else:
            raise ValueError

        # assign the position to a parent if given
        position_info = "" if position_id is None else f"|721={position_id}"

        bl = (
            "35=D"
            f"|49={self.sendercompid}"
            "|56=cServer"
            f"|34={self.trade_msgseqnum}"
            f"|52={get_time()}"
            f"|50={self.trade_sendersubid}"
            "|57=TRADE"
            f"|11={self.trade_msgseqnum}"
            f"|55={symbol_id}"
            f"|54={direction_id}"
            f"|60={get_time()}"
            f"|40={order_type_id}"
            f"|38={quantity_to_trade}"
            f"{price_info}"
            f"{position_info}"
        )
        bl += "|"
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def fix_cancel_order(
        self,
        order_id: str,
        order_request_id: Optional[str] = None,
    ) -> str:
        """Code to cancel an order by its order_id, and order_request_id.

        It seems that it works with any value for the order_request_id,
        but it is required to be given.
        """
        if order_request_id is None:
            order_request_id = f"VAL{self.trade_msgseqnum}"
        bl = (
            "35=F"
            f"|49={self.sendercompid}"
            "|56=cServer"
            f"|34={self.trade_msgseqnum}"
            f"|52={get_time()}"
            f"|50={self.trade_sendersubid}"
            "|57=TRADE"
            f"|11={self.trade_msgseqnum}"
            f"|37={order_id}"
            f"|41={order_request_id}"
            "|"
        )
        self.trade_msgseqnum += 1
        message = f"8=FIX.4.4|9={str(len(bl))}|{bl}".replace("|", "\u0001")
        return message + f"10={checksum(message)}\u0001"

    def print_fix_message(self, name: str, fix_message: str) -> None:
        """Print fix message in a human readable format."""
        readable_fix_message = fix_message.replace("\u0001", "|")
        print(f"{name}={readable_fix_message}")

    def parse_one_position_message(self, full_message: str) -> Dict[str, Any]:
        """Parse one position message."""
        # print(f"full_message for position={full_message}")
        d = None
        if match := re.search("721=(\\d+)", full_message):
            d = {}
            d["position_id"] = match.group(1)
            #
            if match := re.search("55=(\\d+)", full_message):
                symbol_id = int(match.group(1))
            else:
                symbol_id = 0
            # quantity can be float for BTCUSD and ETHUSD as min is 0.01
            if match := re.search("704=([\d.]+)\|", full_message):  # noqa
                quantity_buy = float(match.group(1))
            else:
                quantity_buy = 0.0
            if match := re.search("705=([\d.]+)\|", full_message):  # noqa
                quantity_sell = float(match.group(1))
            else:
                quantity_sell = 0.0
            if quantity_buy > 0.0 and quantity_sell == 0.0:
                direction = "buy"
                quantity = quantity_buy
            elif quantity_buy == 0.0 and quantity_sell > 0.0:
                direction = "sell"
                quantity = quantity_sell
            else:
                raise ValueError
            #
            if match := re.search("730=([\d.]+)\|", full_message):  # noqa
                cost_price = float(match.group(1))
            else:
                cost_price = 0.0
            #
            if match := re.search("727=(\\d+)", full_message):
                num_opened_positions = int(match.group(1))
            else:
                num_opened_positions = 0
            # build dictionary
            d["symbol"] = DICT_SYMBOL_ID_SYMBOL[symbol_id]
            d["symbol_id"] = symbol_id
            d["direction"] = direction
            d["quantity"] = quantity
            d["cost_price"] = cost_price
            d["num_opened_positions"] = num_opened_positions
        # print(f"d={d}")
        return d

    def parse_one_order_message(self, full_message: str) -> Dict[str, Any]:
        """Parse one order message."""
        # print(f"full_message for order={full_message}")
        d = None
        if match := re.search("37=(\\d+)", full_message):
            d = {}
            d["order_id"] = match.group(1)
            #
            if match := re.search("11=(\\d+)", full_message):
                order_request_id = match.group(1)
            else:
                order_request_id = None
            #
            if match := re.search("721=(\\d+)", full_message):
                position_id = match.group(1)
            else:
                position_id = None
            #
            if match := re.search("55=(\\d+)", full_message):
                symbol_id = int(match.group(1))
            else:
                symbol_id = 0
            #
            if match := re.search("38=([\d.]+)\|", full_message):  # noqa
                quantity_ordered = float(match.group(1))
            else:
                quantity_ordered = 0.0
            #
            if match := re.search("14=([\d.]+)\|", full_message):  # noqa
                quantity_filled = float(match.group(1))
            else:
                quantity_filled = 0.0
            #
            if match := re.search("151=([\d.]+)\|", full_message):  # noqa
                quantity_not_filled = float(match.group(1))
            else:
                quantity_not_filled = 0.0
            #
            if match := re.search("39=(\\d+)", full_message):
                value = match.group(1)
                order_status = (
                    "new"
                    if value == "0"
                    else "partially_filled"
                    if value == "1"
                    else "filled"
                    if value == "2"
                    else "rejected"
                    if value == "8"
                    else "cancelled"
                    if value == "4"
                    else "expired"
                    if value == "C"
                    else None
                )  # noqa
            else:
                order_status = None
            #
            if match := re.search("54=(\\d+)", full_message):
                value = match.group(1)
                order_direction = (
                    "buy" if value == "1" else "sell" if value == "2" else None
                )  # noqa
            else:
                order_direction = None
            #
            if match := re.search("40=(\\d+)", full_message):
                value = match.group(1)
                order_type = (
                    "market"
                    if value == "1"
                    else "limit"
                    if value == "2"
                    else "stop"
                    if value == "3"
                    else None
                )  # noqa
            else:
                order_type = None
            #
            if match := re.search("44=([\d.]+)\|", full_message):  # noqa
                price_limit = float(match.group(1))
            else:
                price_limit = None
            #
            if match := re.search("99=([\d.]+)\|", full_message):  # noqa
                price_stop = float(match.group(1))
            else:
                price_stop = None
            #
            if match := re.search("59=(\\d+)", full_message):
                value = match.group(1)
                time_in_force = (
                    "GTC"
                    if value == "1"
                    else "IOC"
                    if value == "3"
                    else "GTD"
                    if value == 6
                    else None
                )  # noqa
            else:
                symbol_id = 0
            #
            # this to allow any character, numbers or letters from 150= to the first |
            if match := re.search(r"150=([^|]+)", full_message):
                value = match.group(1)
                execution_type = (
                    "new"
                    if value == "0"
                    else "canceled"
                    if value == "4"
                    else "replaced"
                    if value == "5"
                    else "rejected"
                    if value == "8"
                    else "expired"
                    if value == "C"
                    else "trade"
                    if value == "F"
                    else "order_status"
                    if value == "I"
                    else None
                )  # noqa
            #
            if match := re.search(r"60=([^|]+)", full_message):
                datetime = match.group(1)
            else:
                datetime = None
            #
            if match := re.search("911=(\\d+)", full_message):
                num_opened_orders = int(match.group(1))
            else:
                num_opened_orders = 0
            # build dictionary
            d["position_id"] = position_id
            d["datetime"] = datetime
            d["symbol"] = DICT_SYMBOL_ID_SYMBOL[symbol_id]
            d["symbol_id"] = symbol_id
            d["order_direction"] = order_direction
            d["order_type"] = order_type
            d["price_limit"] = price_limit
            d["price_stop"] = price_stop
            d["quantity_ordered"] = quantity_ordered
            d["quantity_filled"] = quantity_filled
            d["quantity_not_filled"] = quantity_not_filled
            d["order_status"] = order_status
            d["time_in_force"] = time_in_force
            d["execution_type"] = execution_type
            d["order_request_id"] = order_request_id
            d["num_opened_orders"] = num_opened_orders
        # print(f"d={d}")
        return d

    def get_all_position_ids(
        self, positions: Set[Dict[str, Union[str, int, float]]]
    ) -> List[str]:
        """Get a list of the position_ids that we have from positions."""
        return [position["position_id"] for position in positions]

    def get_all_order_ids(
        self, orders: Set[Dict[str, Union[str, int, float]]]
    ) -> List[str]:
        """Get a list of the order_ids that we have from orders."""
        return [order["order_id"] for order in orders]

    """Login to price and trade streams."""

    async def price_login(self) -> None:
        """Login to price stream on port 5201.

        So far supporting only one asset.
        """
        try:
            print(f"INFO: Logging into broker='{self.broker}' for PRICE stream...")
            self.price_reader, self.price_writer = await asyncio.open_connection(
                self.hostname, 5201
            )
            # print("Price A")
            self.price_sendersubid = random_string()
            # print("Price B")
            #
            fix_price_login = self.fix_login_to_a_stream("QUOTE")
            self.print_fix_message("fix_price_login", fix_price_login)
            #
            fix_market_data_request = self.fix_market_data_request(
                self.symbol, self.symbol_id
            )
            self.print_fix_message("fix_market_data_request", fix_market_data_request)
            #
            fix_message = ""
            fix_message += fix_price_login
            fix_message += fix_market_data_request
            self.price_writer.write(bytes(fix_message, "UTF-8"))
            # print("Price C")
            asyncio.create_task(self.send_price_heartbeat())
            # print("Price D")
            await self.read_price_data()
            # print("Price E")
        except Exception as e:
            await asyncio.sleep(1)
            print(f"ERROR PRICE connection refused login error! exception={e}.")

    async def trade_login(self) -> None:
        """Login to trade stream on port 5202."""
        try:
            print(f"INFO: Logging into broker='{self.broker}' for TRADE stream...")
            self.trade_reader, self.trade_writer = await asyncio.open_connection(
                self.hostname, 5202
            )
            self.trade_sendersubid = random_string()
            fix_trade_login = self.fix_login_to_a_stream("TRADE")
            self.print_fix_message("fix_trade_login", fix_trade_login)
            #
            fix_message = ""
            fix_message += fix_trade_login
            self.trade_writer.write(bytes(fix_message, "UTF-8"))
            #
            asyncio.create_task(self.send_trade_heartbeat())
            # print("Trade D")
            await self.read_trade_data()
            # print("Trade E")
        except Exception as e:
            await asyncio.sleep(1)
            print(f"ERROR: TRADE connection refused login error! exception={e}.")

    """Heartbeat methods for price and trade streams."""

    async def send_price_heartbeat(self) -> None:
        """Price heartbeat used to send heartbeat to server every 1 second.

        If I send with every heartbeat also the market_data_request()
        I get an error that I am already subscribed.
        """
        while True:
            try:
                #
                fix_price_heartbeat = self.fix_heartbeat_to_a_stream("QUOTE")
                # self.print_fix_message("fix_price_heartbeat", fix_price_heartbeat)
                #
                fix_message = ""
                fix_message += fix_price_heartbeat
                #
                self.price_writer.write(bytes(fix_message, "UTF-8"))
            except Exception as e:
                print(f"ERROR There was a PRICE heartbeat error... {e}")
                break
            await asyncio.sleep(1)

    async def send_trade_heartbeat(self) -> None:
        """Trade heartbeat used to send heartbeat to server every 1 second.

        In adition, also request the positions.
        """
        while True:
            try:
                #
                fix_trade_heartbeat = self.fix_heartbeat_to_a_stream("TRADE")
                # self.print_fix_message("fix_trade_heartbeat", fix_trade_heartbeat)
                fix_request_positions = self.fix_request_positions()
                # self.print_fix_message("fix_request_positions", fix_request_positions)
                # fix_request_orders = self.fix_request_orders()
                # self.print_fix_message("fix_request_orders", fix_request_orders)
                #
                fix_message = ""
                fix_message += fix_trade_heartbeat
                fix_message += fix_request_positions
                # fix_message += fix_request_orders
                #
                # self.positions = []
                # self.orders = []
                #
                self.trade_writer.write(bytes(fix_message, "UTF-8"))
            except Exception as e:
                print(f"ERROR: There was a TRADE heartbeat error... {e}")
                break
            await asyncio.sleep(1)

    """Methods to set orders."""

    async def set_order(
        self,
        symbol: str,
        direction: str,
        order_type: str,
        quantity_to_trade: int,
        price: float,
        position_id: Optional[str] = None,
    ) -> None:
        """Async function to set one order, to be called from the main for loop."""
        set_order = self.fix_set_order(
            symbol,
            direction,
            order_type,
            quantity_to_trade,
            price,
            position_id,
        )
        try:
            print("*************************************")
            self.print_fix_message("set_order", set_order)
            print("*************************************")
            self.trade_writer.write(bytes(set_order, "UTF-8"))
        except Exception as e:
            print(f"ERROR: {self.broker}, async_set_order not working! exception={e}")

    async def set_order_examples(
        self,
        symbol: str,
        price_low: float,
        price_high: float,
        num_repeats: int,
    ) -> None:
        """Set order examples of 6 types, each N times."""
        min_quantity_to_trade, our_quantity_to_trade = get_info_quantity_to_trade(symbol)

        fix_set_orders = ""
        for i in range(num_repeats):
            # buy orders
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="buy",
                order_type="market",
                quantity_to_trade=min_quantity_to_trade,
                price=None,
                position_id=None,
            )
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="buy",
                order_type="limit",
                quantity_to_trade=our_quantity_to_trade,
                price=price_low,
                position_id=None,
            )
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="buy",
                order_type="stop",
                quantity_to_trade=our_quantity_to_trade,
                price=price_high,
                position_id=None,
            )
            # sell orders
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="sell",
                order_type="market",
                quantity_to_trade=min_quantity_to_trade,
                price=None,
                position_id=None,
            )
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="sell",
                order_type="limit",
                quantity_to_trade=our_quantity_to_trade,
                price=price_low,
                position_id=None,
            )
            fix_set_orders += self.fix_set_order(
                symbol=symbol,
                direction="sell",
                order_type="stop",
                quantity_to_trade=our_quantity_to_trade,
                price=price_high,
                position_id=None,
            )
        try:
            self.print_fix_message("fix_set_orders", fix_set_orders)
            self.trade_writer.write(bytes(fix_set_orders, "UTF-8"))
        except Exception as e:
            print(f"ERROR: {self.broker} setting orders not working! {e}")

    async def cancel_order(
        self,
        order_id: str,
        order_request_id: Optional[str] = None,
    ) -> None:
        """Async close order based on order_id."""
        fix_cancel_orders = ""
        fix_cancel_orders += self.fix_cancel_order(order_id, order_request_id)
        try:
            self.print_fix_message("fix_cancel_orders", fix_cancel_orders)
            self.trade_writer.write(bytes(fix_cancel_orders, "UTF-8"))
            self.orders = [d for d in self.orders if d["order_id"] != order_id]
        except Exception as e:
            print(
                f"ERROR: Unable to cancel order of order_id={order_id}, "
                f"on {self.broker}, with exception={e}."
            )
        # remove all the orders that have order_id we want
        # usually it should be only one, but just in case
        # use list comprehension to be faster and more concise
        # self.orders = [d for d in self.orders if d["order_id"] != order_id]
        # self.orders.discard(order_id)

    async def cancel_all_orders_for_one_position(
        self,
        position_id: str,
    ) -> List[str]:
        """Close all orders for one position."""
        order_ids = [
            d["order_id"] for d in self.orders if d["position_id"] == position_id
        ]
        fix_cancel_orders = ""
        for order_id in order_ids:
            fix_cancel_orders += self.fix_cancel_order(order_id)
        try:
            self.print_fix_message("fix_cancel_orders", fix_cancel_orders)
            self.trade_writer.write(bytes(fix_cancel_orders, "UTF-8"))
            self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        except Exception as e:
            print(
                f"Unable to cancel order of order_id={order_id}, "
                f"on {self.broker}, with exception={e}."
            )
        # remove all the orders that have order_id we want
        # usually it should be only one, but just in case
        # use list comprehension to be faster and more concise
        # self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        return order_ids

    async def cancel_all_orders_for_one_symbol(
        self,
        symbol: str,
    ) -> List[str]:
        """Close all orders for one symbol."""
        order_ids = [d["order_id"] for d in self.orders if d["symbol"] == symbol]
        fix_cancel_orders = ""
        for order_id in order_ids:
            fix_cancel_orders += self.fix_cancel_order(order_id)
        try:
            self.print_fix_message("fix_cancel_orders", fix_cancel_orders)
            self.trade_writer.write(bytes(fix_cancel_orders, "UTF-8"))
            # remove all the orders that have order_id we want
            # for order_id in order_ids:
            #    self.orders.discard(order_id)
            self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        except Exception as e:
            print(
                f"Unable to cancel order of order_id={order_id}, "
                f"on {self.broker}, with exception={e}."
            )
        # remove all the orders that have order_id we want
        # usually it should be only one, but just in case
        # use list comprehension to be faster and more concise
        # self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        return order_ids

    async def cancel_all_orders_for_several_symbols(
        self,
        symbols: List[str],
    ) -> List[str]:
        """Close all orders for several symbols."""
        order_ids = [d["order_id"] for d in self.orders if d["symbol"] in symbols]
        fix_cancel_orders = ""
        for order_id in order_ids:
            fix_cancel_orders += self.fix_cancel_order(order_id)
        try:
            self.print_fix_message("fix_cancel_orders", fix_cancel_orders)
            self.trade_writer.write(bytes(fix_cancel_orders, "UTF-8"))
            # remove all the orders that have order_id we want
            for order_id in order_ids:
                self.orders.discard(order_id)
        except Exception as e:
            print(
                f"Unable to cancel order of order_id={order_id}, "
                f"on {self.broker}, with exception={e}."
            )
        # remove all the orders that have order_id we want
        # usually it should be only one, but just in case
        # use list comprehension to be faster and more concise
        # self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        return order_ids

    async def cancel_all_orders(
        self,
    ) -> List[str]:
        """Close all orders."""
        order_ids = [d["order_id"] for d in self.orders]
        fix_cancel_orders = ""
        for order_id in order_ids:
            fix_cancel_orders += self.fix_cancel_order(order_id)
        try:
            self.print_fix_message("fix_cancel_orders", fix_cancel_orders)
            self.trade_writer.write(bytes(fix_cancel_orders, "UTF-8"))
            # remove all the orders that have order_id we want
            for order_id in order_ids:
                self.orders.discard(order_id)
        except Exception as e:
            print(
                f"Unable to cancel order of order_id={order_id}, "
                f"on {self.broker}, with exception={e}."
            )
        # remove all the orders that have order_id we want
        # usually it should be only one, but just in case
        # use list comprehension to be faster and more concise
        # self.orders = [d for d in self.orders if d["order_id"] not in order_ids]
        return order_ids

    async def close_position(
        self,
        position_id: str,
    ) -> None:
        """Close a position by creating a market order of oppoiste sign same quantity."""
        print(f"In close_position, self.positions={self.positions}")
        positions = [d for d in self.positions if d["position_id"] == position_id]
        if len(positions) == 0:
            await asyncio.sleep(0.001)
            positions = [d for d in self.positions if d["position_id"] == position_id]
        if len(positions) == 0:
            await asyncio.sleep(0.001)
            positions = [d for d in self.positions if d["position_id"] == position_id]
        if len(positions) == 0:
            print(
                f"WARNING!!! position_id={position_id} not found, "
                f"so can not close. self.positions={self.positions}"
            )
            return

        position_ids = [d["position_id"] for d in positions]
        fix_close_positions = ""
        for d in positions:
            fix_close_positions += self.fix_set_order(
                symbol=d["symbol"],
                direction="buy" if d["direction"] == "sell" else "sell",
                order_type="market",
                quantity_to_trade=d["quantity"],
                price=None,
                position_id=d["position_id"],
            )
        try:
            self.print_fix_message("fix_close_positions", fix_close_positions)
            self.trade_writer.write(bytes(fix_close_positions, "UTF-8"))
            # remove from the list of positions
            # wait asyncio.sleep(0.1)
            ds = [d for d in self.positions if d["position_id"] in position_ids]
            for d in ds:
                self.positions.remove(d)
            # self.positions = [
            #    d for d in self.positions if d["position_id"] != position_id
            # ]
            # self.position_ids.discard(position_id)
            # also close all orders for that position
            # await self.cancel_all_orders_for_one_position(position_id)
        except Exception as e:
            print(
                f"Unable to close position of position_id={position_id}, "
                f"on {self.broker}, with exception={e}."
            )

    async def close_all_positions_for_one_symbol(
        self,
        symbol: str,
    ) -> None:
        """Close all positions for one symbol."""
        print(f"In close_all_positions_for_one_symbol, self.positions={self.positions}")
        position_ids = [d["position_id"] for d in self.positions if d["symbol"] == symbol]
        for position_id in position_ids:
            print(f"Closing position_id={position_id}")
            asyncio.create_task(self.close_position(position_id))

    async def close_all_positions_for_several_symbols(
        self,
        symbols: List[str],
    ) -> None:
        """Close all positions for several symbols."""
        position_ids = [
            d["position_id"] for d in self.positions if d["symbol"] in symbols
        ]
        for position_id in position_ids:
            asyncio.create_task(self.close_position(position_id))

    async def close_all_positions(
        self,
    ) -> None:
        """Close all positions."""
        position_ids = [d["position_id"] for d in self.positions]
        for position_id in position_ids:
            asyncio.create_task(self.close_position(position_id))

    async def read_price_data(self) -> None:
        """Reads data asynchronously from the price stream."""
        while True:
            # print("Read price data again.")
            # await asyncio.sleep(2)
            try:
                # print("Read price data first 16 bytes that represent the header")
                header_bytes = await self.price_reader.read(16)
                # print(f"header={header}")
                header = header_bytes.decode().replace("\u0001", "|")
                # print(f"header={header}")
                if match := re.search("9=(\\d+)", header):
                    index = int(match.group(1))
                    ti = index - 1 if index < 100 else index
                    # print(f"ti={ti}, then read the following 7 in second")
                    second = await self.price_reader.read(ti + 7)
                    # print(f"second={second}")
                    full_message = header + second.decode().replace("\u0001", "|")
                    # print(f"INFO: Read price data: full_message={full_message}")
                    if "35=W" in full_message:
                        # print("Price stream 35=W was found, "
                        #       "so search for prices the fields with 270"
                        # )
                        prices = re.findall("270=([^|]*)", full_message)
                        # print(f"prices={prices}")
                        self.bid = prices[0]
                        self.ask = prices[1]
                        # print(f"self.bid={self.bid}, self.ask={self.ask}")
                    # print("Print again the full message")
                    # print(full_message)
                    # print("Done read the full message")
            except Exception as e:
                print(
                    f"PRICE Unable to read from server for {self.broker}, "
                    f"for self.price_msgseqnum={self.price_msgseqnum}, "
                    f"with exception='{e}'."
                )
                # if we could not connect to the server
                if tcp_ping("www.google.com", 80):
                    # we check if we have internet by pinging google
                    # and we have internet we sent async task to login again to price
                    asyncio.create_task(self.price_login())
                    break
            await asyncio.sleep(0.001)

    async def read_trade_data(self) -> None:
        """Reads data asynchronously from the trade stream.

        Will positions also be removed when I close them? To check.
        But the code seems only to append or not append.
        Answer: when closing all positions, the list of positions is cleared.
        But we need to add a function to close only one position, or a list of positions,
        and then we need to remove only that position from the list.
        """
        while True:
            try:
                # print("Read trade data: Read first 16 bytes that represent the header")
                header_bytes = await self.trade_reader.read(16)
                header = header_bytes.decode().replace("\u0001", "|")
                # print(f"header={header}")
                if match := re.search("9=(\\d+)", header):
                    index = int(match.group(1))
                    ti = index - 1 if index < 100 else index
                    # print(f"ti={ti}, then read the following 7 in second")
                    second = await self.trade_reader.read(ti + 7)
                    # print(f"second={second}")
                    full_message = header + second.decode().replace("\u0001", "|")
                    # print(f"INFO: trade response: full_message={full_message}")
                    if "35=AP" in full_message:
                        # this is a response to a request for positions
                        print(f"trade response position: full_message={full_message}")
                        d = self.parse_one_position_message(full_message)
                        # print(d)
                        # print(f"len(self.positions)={len(self.positions)}")
                        # print(f"len(positions)={len(self.positions)}")
                        # print(f"len(self.positions)={len(self.positions)}")
                        # print("Z")
                        # print(f"self.get_all_position_ids(self.orders)={self.get_all_position_ids(self.positions)}")  # noqa
                        # print("W")
                        # print(f"len(self.positions)={len(self.positions)}")
                        # print(self.positions)
                        # print("our new position received")
                        # print(f"d={d}")
                        # print("Check if it exists in the set of positions")
                        # if d is not None:
                        # self.positions.add(d)
                        # self.position_ids.add(d["position_id"])

                        # print("BBB")
                        # print(self.positions)
                        # print(self.position_ids)
                        # print(f"d={d}")
                        # print("CCC")
                        if (
                            True
                            and (d is not None)
                            and d["position_id"]
                            not in self.get_all_position_ids(self.positions)
                        ):
                            # ] not in self.position_ids:
                            # print("A")
                            # print("position does not exist in the set of positions")
                            self.positions.append(d)
                            # print("B")
                            # self.position_ids.add(d["position_id"])
                            # print("C")
                            # print("We added it to the set of possitions")
                            self.num_opened_positions = d["num_opened_positions"]
                            # print("D")
                        # print("E")
                        # print(
                        # f"after adding position len(self.positions)={len(self.positions)}, "
                        # f"num_opened_positions={self.num_opened_positions},"
                        # f"position_ids={self.position_ids}"
                        # )
                        # print(self.positions)
                    elif "35=8" in full_message:
                        # this is a response to a request for orders
                        # if "543140337" in full_message:
                        print(
                            f"INFO: trade response order EXECUTION REPORT: full_message={full_message}"
                        )
                        d = self.parse_one_order_message(full_message)
                        # print(d)
                        # print(f"len(self.orders)={len(self.orders)}")
                        # print(f"len(orders)={len(self.orders)}")
                        # print(f"len(self.orders)={len(self.orders)}")
                        # print("Z")
                        # print(f"self.get_all_order_ids(self.orders)={self.get_all_order_ids(self.orders)}")  # noqa
                        # print("W")
                        if (d is not None) and d[
                            "order_id"
                        ] not in self.get_all_order_ids(self.orders):
                            self.orders.append(d)
                            self.num_opened_orders = d["num_opened_orders"]
                    elif "35=j" in full_message:
                        if True:
                            print(
                                f"trade response order SET ORDER NOT EXECUTED: "
                                f"full_message={full_message}"
                            )
                    elif "35=9" in full_message:
                        if True:
                            print(
                                f"trade response order CANCEL ORDER NOT EXECUTED: "
                                f"full_message={full_message}"
                            )
                    elif "35=0" in full_message:
                        if True:
                            print(
                                f"trade response HEARTBEAT: "
                                f"full_message={full_message}"
                            )
                    elif "35=1" in full_message:
                        if True:
                            print(
                                f"trade response FORCED HEARTBEAT: "
                                f"full_message={full_message}"
                            )
                    elif "35=2" in full_message:
                        if True:
                            print(
                                f"trade response RESEND REQUEST: "
                                f"full_message={full_message}"
                            )
                    elif "35=A" in full_message:
                        if True:
                            print(
                                f"trade response LOGON BIRECTIONAL: "
                                f"full_message={full_message}"
                            )
                    elif "35=3" in full_message:
                        # self.trade_msgseqnum += 1
                        if True:
                            print(
                                f"trade response REJECT BIRECTIONAL MUST BE INCREMENTED SEQUENCE NUMBER: "
                                f"full_message={full_message}"
                            )
                    elif "35=4" in full_message:
                        if True:
                            print(
                                f"trade response SEQUENCE RESET: "
                                f"full_message={full_message}"
                            )
                    elif "35=5" in full_message:
                        if True:
                            print(
                                f"trade response LOGOUT message sent: "
                                f"full_message={full_message}"
                            )
                    else:
                        print(
                            f"WARNING: trade response order UNKNOWN CATEGORY: "
                            f"full_message={full_message}"
                        )

                    # print(
                    #    f"len(self.positions)={len(self.positions)}, "
                    #    f"num_opened_positions={self.num_opened_positions}"
                    #    )
                    # print(f"opened_positions={self.opened_positions}")
                    # print(full_message)
            except Exception:
                print(f"TRADE Unable to read from server for {self.broker}")
                # if we could not connect to the server
                if tcp_ping("www.google.com", 80):
                    print("But we have internet, so creating a new trade_login_main()")
                    # we check if we have internet by pinging google
                    # and we have internet we sent async task to login again to trade
                    asyncio.create_task(self.trade_login())
                    print("Done create trade_login_main()")
                    break
            # print("Finish read_trade_data")
            # for position in self.positions:
            #    print(f"position={position}")
            await asyncio.sleep(0.001)
            # print("Finish await 0.001 seconds")
