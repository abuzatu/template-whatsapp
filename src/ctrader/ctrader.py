"""Module for CTrader for both quotes and trades."""

import logging
import json
import time
import random
from operator import itemgetter
from .fix import FIX, Side, OrderType

from typing import Any, Dict, List, Optional


class CTrader:
    """Class that controls the CTrader account.

    On one side getting quotes.
    On the order seeing/seeting/modifying/closing orders and positions.
    """

    def __init__(
        self,
        server: str,
        account: str,
        password: str,
        currency: str,
        client_id: int = 1,
        debug: bool = False,
    ):
        """Init.

        Args:
            server ([str]): [an IP given by them]
            account ([str]): [live.icmarkets.1104926 or demo.icmarkets.1104926]
            password ([str]): [example 12345678 need to setup
            when you create api on ctrader platform]
            currency ([str]): "EUR" or "USD"
            client_id ([str]):[example 1 or trader-1 its comment on position label]
            debug ([bool]): if true or false to add more logging info.
        """
        if debug:
            logging.getLogger().setLevel(logging.INFO)
        split_string = account.split(".")
        broker = split_string[0] + "." + split_string[1]
        login = split_string[2]

        self.client = c = {
            "_id": client_id,
            "server": server,
            "broker": broker,
            "login": login,
            "password": password,
            "currency": currency,
            "fix_status": 0,
            "positions": [],
            "orders": [],
        }
        self.fix = FIX(
            c["server"],
            c["broker"],
            c["login"],
            c["password"],
            c["currency"],
            c["_id"],
            self.position_list_callback,
            self.order_list_callback,
        )
        self.market_data_list = {}

    def trade(
        self,
        symbol,
        action,
        type,
        actionType,
        volume,
        stoploss,
        takeprofit,
        price,
        deviation,
        id,
    ) -> str:
        """Trade."""
        v_action = action
        v_symbol = symbol
        v_ticket = (
            id
            if id
            else "{:.7f}".format(time.time()).replace(".", "")
            + str(random.randint(10000, 99999))
        )
        v_type = str(type)
        v_openprice = price
        v_lots = volume
        v_sl = stoploss
        v_tp = takeprofit

        logging.info(
            (
                "Action: %s, Symbol: %s, Lots: %s, Ticket: %s, price: %s, "
                "takeprofit: %s, stoploss: %s, type: %s"
            ),
            v_action,
            v_symbol,
            v_lots,
            v_ticket,
            v_openprice,
            v_sl,
            v_tp,
            v_type,
        )
        otype = actionType
        symbol = v_symbol[:6]
        factor_size = (
            1
            if symbol
            in [
                "US30",
                "US500",
                "USTEC",
            ]
            else 100_000
        )
        size = int(float(v_lots) * factor_size)
        # print(f"otype={otype}, symbol={symbol}, size={size}")
        global ticket
        ticket = None
        client_id = str(self.client["_id"])
        command = ""
        if v_action == "OPEN":
            if int(v_type) > 1:
                # abre ordem pendente
                command = "{0} {1} {2} {3} {4}".format(
                    otype, symbol, size, v_openprice, v_ticket
                )
                # print(
                #    f"OPEN v_type>1={v_type}, command={command}, "
                #    "should be open limit order"
                # )
                self.parse_command(command, client_id)
            else:
                # abre posicao a mercado
                command = "{0} {1} {2} {3}".format(otype, symbol, size, v_ticket)
                # print(
                #    f"OPEN v_type==0={v_type}, command={command}, "
                #    "should be open market order"
                # )
                self.parse_command(command, client_id)

                # print("A")
                # print(f"v_ticket={v_ticket}")
                time.sleep(4)
                # ticket = self.fix.origin_to_pos_id[v_ticket]
                # print("B")

                if v_sl or v_tp:
                    # if False:
                    # print(f"We have SL or TP, SL={v_sl}, TP={v_tp}")
                    while True:
                        try:
                            ticket = self.fix.origin_to_pos_id[v_ticket]
                            # time.sleep(1)
                            if ticket:  # Verifica se a variável ticket não está vazia
                                break
                        except Exception as e:
                            logging.info(e)
                            continue

                # print("B")

                if ticket:
                    # print(f"C, SL={v_sl}, TP={v_tp}")
                    if v_sl and float(v_sl) > 0:
                        # print(f"D, SL={v_sl}")
                        # abre posicao pendente SL
                        otype = "sell stop" if v_type == "0" else "buy stop"
                        command = "{0} {1} {2} {3} {4} {5}".format(
                            otype, symbol, size, v_sl, v_ticket, ticket
                        )
                        # print(f"We have SL command={command}")
                        self.parse_command(command, client_id)
                    if v_tp and float(v_tp) > 0:
                        # print(f"D, TP={v_tp}")
                        # cancela ordens pendentes abertas de TP e SL
                        ticket_orders = self.getOrdersIdByOriginId(v_ticket)
                        # abre posicao pendente TP
                        otype = "sell limit" if v_type == "0" else "buy limit"
                        command = "{0} {1} {2} {3} {4} {5}".format(
                            otype, symbol, size, v_tp, v_ticket, ticket
                        )
                        # print(f"We have TP command={command}")
                        self.parse_command(command, client_id)

        elif v_action in ["CLOSED", "PCLOSED"]:
            # print("closing action")
            if int(v_type) > 1:
                # ORDEM
                # cancela ordens pendentes
                self.fix.cancel_order(v_ticket)
                ticket_orders = self.getOrdersIdByOriginId(v_ticket, client_id)
                self.cancelOrdersByOriginId(ticket_orders, client_id)
                self.parse_command(command, client_id)
                return
            else:
                # POSICAO
                self.fix.close_position(v_ticket, size)
                # cancela ordens pendentes abertas de TP e SL
                ticket_orders = self.getOrdersIdByOriginId(v_ticket, client_id)
                self.cancelOrdersByOriginId(ticket_orders, client_id)
                self.parse_command(command, client_id)
                return

        return v_ticket

    def buyMarket(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for buy.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            stoploss ([float]): [1.18]
            takeprofit ([float]): [1.19]
            price (int, optional): [on the price]. Defaults to 0.

        Returns:
            [int]: [order ID]
        """
        return self.trade(
            symbol,
            "OPEN",
            0,
            "buy",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def sellMarket(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for sell.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            stoploss ([float]): [1.19]
            takeprofit ([float]): [1.18]
            price (int, optional): [on the price]. Defaults to 0.

        Returns:
            [int]: [Order ID]
        """
        return self.trade(
            symbol,
            "OPEN",
            1,
            "sell",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def buyLimit(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for buy Limit.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            price ([float]): [1.8]. Defaults to 0.

        Returns:
            [int]: [order ID]
        """
        return self.trade(
            symbol,
            "OPEN",
            2,
            "buy limit",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def sellLimit(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for sellLimit.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            price (int, optional): [1.22]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        return self.trade(
            symbol,
            "OPEN",
            3,
            "sell limit",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def buyStop(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for buyStop.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            price (int, optional): [1.22]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        return self.trade(
            symbol,
            "OPEN",
            4,
            "buy stop",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def sellStop(
        self,
        symbol: str,
        volume: float,
        stoploss: Optional[float],
        takeprofit: Optional[float],
        price: Optional[float],
    ) -> str:
        """Summary for sellStop.

        Args:
            symbol ([str]): ["EURUSD"]
            volume ([float]): [0.01]
            price (int, optional): [1.22]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        return self.trade(
            symbol,
            "OPEN",
            5,
            "sell stop",
            volume,
            stoploss,
            takeprofit,
            price,
            None,
            None,
        )

    def positionClosePartial(self, id: str, volume: float) -> str:
        """Position close partial.

        What does the 5 argument do? It is not used in the main trade function.
        """
        return self.trade("", "PCLOSED", 0, "", volume, 0, 0, 0, 5, id)

    def positionCloseById(self, id: str, amount: float) -> Optional[str]:
        """Position close by ID.

        What does the 5 argument do? It is not used in the main trade function.
        """
        try:
            action = self.trade("", "CLOSED", 0, "", amount / 100000, 0, 0, 0, 5, id)
        except Exception as e:
            logging.info(e)
            action = None
            pass
        return action

    def orderCancelById(self, id: str) -> Optional[str]:
        """Ordr cancel by ID.

        What does the 5 argument do? It is not used in the main trade function.
        """
        try:
            action = self.trade("", "CLOSED", 2, "", 0, 0, 0, 0, 5, id)
        except Exception as e:
            logging.info(e)
            action = None
            pass
        return action

    def positions(self) -> List[Dict[str, Any]]:
        """Get positions."""
        return json.loads(json.dumps(self.client["positions"]))

    def orders(self) -> List[Dict[str, Any]]:
        """Get orders."""
        return json.loads(json.dumps(self.client["orders"]))

    def parse_command(self, command: str, client_id: str) -> None:
        """Parse command."""
        parts = command.split(" ")
        logging.info(parts)
        logging.info(f"Command: {command} ")

        if not self.fix.logged:
            logging.info("waiting logging...")
            return

        if parts[0] == "sub":
            try:
                subid = int(parts[1])
                self.fix.market_request(subid - 1, parts[2].upper(), self.quote_callback)
            except ValueError:
                logging.error("Invalid subscription ID")
        if parts[0] in ["buy", "sell"]:
            if parts[1] in ["stop", "limit"]:
                self.fix.new_limit_order(
                    parts[2].upper(),
                    Side.Buy if parts[0] == "buy" else Side.Sell,
                    OrderType.Limit if parts[1] == "limit" else OrderType.Stop,
                    float(parts[3]),
                    float(parts[4]),
                    parts[5] if len(parts) >= 6 else None,
                    parts[6] if len(parts) >= 7 else None,
                )
            else:
                self.fix.new_market_order(
                    parts[1].upper(),
                    Side.Buy if parts[0] == "buy" else Side.Sell,
                    float(parts[2]),
                    parts[3] if len(parts) >= 4 else None,
                    parts[4] if len(parts) >= 5 else None,
                )
        if parts[0] == "close":
            if parts[1] == "all":
                self.fix.close_all()
            else:
                if len(parts) == 3:
                    self.fix.close_position(parts[1], parts[2])
                else:
                    self.fix.close_position(parts[1])
        if parts[0] == "cancel":
            if parts[1] == "all":
                self.fix.cancel_all()
            else:
                self.fix.cancel_order(parts[1])

    def float_format(self, fmt: str, num: float, force_sign: bool = True) -> str:
        """Format a float as a string."""
        return max(
            ("{:+}" if force_sign else "{}").format(round(num, 6)),
            fmt.format(num),
            key=len,
        )

    def position_list_callback(
        self, data: dict, price_data: dict, client_id: str
    ) -> None:
        """Position list callback."""
        positions = []
        for i, kv in enumerate(data.items()):
            pos_id = kv[0]
            name = kv[1]["name"]
            side = "Buy" if kv[1]["long"] > 0 else "Sell"
            amount = kv[1]["long"] if kv[1]["long"] > 0 else kv[1]["short"]
            price_str = self.float_format(
                "{:.%df}" % kv[1]["digits"], kv[1]["price"], False
            )
            price = price_data.get(name, None)
            actual_price = ""
            diff_str = ""
            pl_str = ""
            gain_str = ""
            if price:
                if side == "Buy":
                    p = price["bid"]
                else:
                    p = price["ask"]
                actual_price = ("{:.%df}" % kv[1]["digits"]).format(p)
                diff = p - kv[1]["price"]
                if side == "Sell":
                    diff = -diff
                diff_str = self.float_format("{:+.%df}" % kv[1]["digits"], diff)
                pl = amount * diff
                pl_str = self.float_format("{:+.2f}", pl)
                convert = kv[1]["convert"]
                convert_dir = kv[1]["convert_dir"]
                price = price_data.get(convert, None)
                if price:
                    if convert_dir:
                        rate = 1 / price["ask"]
                    else:
                        rate = price["bid"]
                    pl_base = pl * rate
                    gain_str = "{:+.2f}".format(round(pl_base, 2))
            # adiciona informacoes de posicoes no client
            positions.append(
                {
                    "pos_id": pos_id,
                    "name": name,
                    "side": side,
                    "amount": amount,
                    "price": price_str,
                    "actual_price": actual_price,
                    "diff": diff_str,
                    "pl": pl_str,
                    "gain": gain_str,
                }
            )
        self.client.update(positions=positions)
        logging.debug("client_id %s positions: %s", client_id, positions)

    def getPositionIdByOriginId(self, posId: str) -> Optional[str]:
        """Get PositionID by OriginID."""
        if posId in self.fix.origin_to_pos_id:
            return self.fix.position_list[self.fix.origin_to_pos_id[posId]]
        else:
            return None

    def getOrdersIdByOriginId(self, ordId: str) -> Optional[str]:
        """Get OrderID by OriginID."""
        if (
            ordId in self.fix.origin_to_ord_id
        ):  # Verifique se a chave existe antes de acessá-la
            return self.fix.origin_to_ord_id[ordId]
        else:
            return None  # Retorne None ou outro valor padrão quando a chave não existir

    def cancelOrdersByOriginId(self, clIdArr: str) -> None:
        """Cancel order by OriginID."""
        if not clIdArr:
            return
        for clId in clIdArr:
            self.fix.cancel_order(clId)

    def subscribe(self, symbols: List[str]) -> None:
        """Subscribe."""
        # print(f"A, symbols={symbols}")
        for symbol in symbols:
            # print(f"B, symbol={symbol}")
            self.fix.spot_market_request(symbol)

    def quote(self, symbol: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Quote."""
        if symbol and symbol not in self.fix.spot_price_list:
            return f"Symbol {symbol} not Subscribed, so can not get price."
        elif symbol:
            # print(f"A symbol={symbol}")
            return self.fix.spot_price_list[symbol]
        # print("B return entire list")
        # print(type(self.fix.spot_price_list))
        # print(self.fix.spot_price_list)
        return self.fix.spot_price_list

    def order_list_callback(self, data: dict, price_data: dict, client_id: str):
        """Ordr list callback."""
        orders = []
        for i, kv in enumerate(data.items()):
            ord_id = kv[0]
            name = kv[1]["name"]
            side = "Buy" if kv[1]["side"] == Side.Buy else "Sell"
            amount = kv[1]["amount"]
            order_type = kv[1]["type"]
            price_str = ""
            if order_type > 1:
                price_str = self.float_format(
                    "{:.%df}" % kv[1]["digits"], kv[1]["price"], False
                )
            price = price_data.get(name, None)
            actual_price = ""
            if price:
                if side == "Buy":
                    price = price["ask"]
                else:
                    price = price["bid"]
                actual_price = self.float_format(
                    "{:.%df}" % kv[1]["digits"], price, False
                )
            pos_id = kv[1]["pos_id"]
            # adiciona informacoes de ordens no client
            orders.append(
                {
                    "ord_id": ord_id,
                    "name": name,
                    "side": side,
                    "amount": amount,
                    "price": price_str,
                    "actual_price": actual_price,
                    "pos_id": pos_id,
                    "clid": kv[1]["clid"],
                }
            )
        self.client.update(orders=orders)
        logging.debug("client_id %s orders: %s", client_id, orders)

    def quote_callback(self, name: str, digits: int, data: dict):
        """Quote callback."""
        if len(data) == 0:
            return
        ask = []
        bid = []
        for e in data.values():
            if e["type"] == 0:
                bid.append(e)
            else:
                ask.append(e)
        ask.sort(key=itemgetter("price"))
        bid.sort(key=itemgetter("price"), reverse=True)

        bid_str = ("{:.%df}" % digits).format(bid[0]["price"])
        offer_str = ("{:.%df}" % digits).format(ask[0]["price"])
        spread_str = ("{:.%df}" % digits).format(ask[0]["price"] - bid[0]["price"])
        self.market_data_list[name] = {
            "bid": bid_str,
            "ask": offer_str,
            "spread": spread_str,
            "time": time.time(),
        }

    def close_all(self) -> None:
        """Close all."""
        self.fix.close_all()

    def cancel_all(self) -> None:
        """Cancel all."""
        self.fix.cancel_all()

    def logout(self) -> str:
        """Logout."""
        if self.isconnected():
            self.fix.logout()
            logout = "Logged out"
        else:
            logout = "Not logged in"
        return logout

    def isconnected(self) -> bool:
        """Is connected."""
        return self.fix.logged

    """My functions to be really simple.
    
    Buy and sell at market without SL, TP, price.
    And close fully (entire volume) of all positions of one symbol.
    """

    def buy(self, symbol: str, volume: float) -> None:
        """Market order to buy without SL, TP, price."""
        id = self.buyMarket(symbol, volume, stoploss=None, takeprofit=None, price=None)
        logging.info(f"Position: {id} of market buy of {symbol} in {volume} lots.")

    def sell(self, symbol: str, volume: float) -> None:
        """Market order to sell without SL, TP, price."""
        id = self.sellMarket(symbol, volume, stoploss=None, takeprofit=None, price=None)
        logging.info(f"Position: {id} of market sell of {symbol} in {volume} lots.")

    def close(self, symbol: str) -> None:
        """Close fully all the positions of a given symbol."""
        for position in self.positions():
            if position["name"] != symbol:
                continue
            # if here close the entire position
            # Close position by id of all amount
            # by giving it the entire amount the position
            self.positionCloseById(position["pos_id"], position["amount"])
