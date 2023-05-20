"""Module to parse one text message for Investors Wizard (Meisha)."""

from typing import List

from trading.order import Order
from utils.logger import request_logger


class Parse_InvestorsWizard:
    """Parse a text message from InvestorsWizard (Meisha).

    One text message produces one order.
    """

    def __init__(self) -> None:
        """init."""
        super().__init__()
        self.examples = [
            "FOREX CALL: BUY GBPNZD ABOVE 1.9255 TARGET 1.9275 /1.9295 STOPLOSS 1.9235",
            "FOREX CALL: SELL GBPNZD BELOW 1.9545 TARGET 1.9525 /1.9505 STOPLOSS 1.9565",
            "FOREX CALL: BUY GBPNZD ABOVE 1.9452 TARGET 1.9472/1.9492 STOPLOSS 1.9432 (PENDING ORDER)",  # noqa
            "COMEX CALL: BUY XAUUSD ABOVE 1645.50 TARGET 1650.50 STOPLOSS 1640.50",
            "FOREX CALL: BUY GBPJPY ABOVE 165.68 TARGET 165.88/166.08 STOPLOSS 165.48 (Pending Order)",  # noqa
            "TRADERS DELIGHT CALL: SELL XAUUSD BELOW 1766 TARGET 1759 STOPLOSS 1773",
            "FOREX UPDATE: GBPNZD BUY CALL HAS MADE A HIGH OF 1.9308 TARGET 1.9293 ACHIEVED HOPE YOU HAVE BOOKED PROFIT IN IT",  # noqa
            "FOREX UPDATE: GBPNZD BUY CALL HAS MADE A HIGH OF 1.9432 TARGET 1.9427 ACHIEVED HOPE YOU HAVE BOOKED PROFIT",  # noqa
            "TRADERS DELIGHTUPDATE: XAUUSD SELL CALL HAS MADE A LOW OF 1758.23 TARGET 1759 ACHIEVED HOPE YOU HAVE BOOKED PROFIT IN IT"  # noqa
            # imagined example for BTCUSD to allow to set trades on a weekend
            # buy limit
            # "CRYPTO CALL: BUY BTCUSD ABOVE 17000 TARGET 17000/17100 STOPLOSS 15500",
            # buy stop
            # "CRYPTO CALL: BUY BTCUSD ABOVE 18000 TARGET 19000/19100 STOPLOSS 15500",
            # sell limit
            # "CRYPTO CALL: SELL BTCUSD BELOW 19000 TARGET 17000/17100 STOPLOSS 20000",
            # sell stop
            # "CRYPTO CALL: SELL BTCUSD BELOW 16000 TARGET 15100/151000 STOPLOSS 20000",
            # buy market while giving CMP, even if not used
            # "CRYPTO CALL: BUY BTCUSD AT 16500 TARGET 17000/17100 STOPLOSS 15500",
            # buy market without giving CMP, it's OK, as not used
            # "CRYPTO CALL: BUY BTCUSD AT MARKET TARGET 17000/17100 STOPLOSS 15500",
            # sell market with CMP, even if not used
            # "CRYPTO CALL: SELL BTCUSD AT 16500 TARGET 15200/15100 STOPLOSS 17000",
            # sell market without CMP, it's OK, as not used
            # "CRYPTO CALL: SELL BTCUSD AT MARKET TARGET 15200/15100 STOPLOSS 17000",
            # buy market while giving a range
            "CRYPTO CALL: SELL BTCUSD AT 16000-17000 TARGET 15200/15100 STOPLOSS 17000",
        ]

    def fit_examples(self) -> None:
        """Fit several texts as examples."""
        request_logger.info("Will start to fit examples.")
        for example in self.examples:
            print()
            o = self.fit(example)
            print(o)

    def fit(self, text: str) -> None:
        """Initialize from a text message with rule-based."""
        text = self.upper(text)
        text = self.deal_with_slash(text)
        text = self.deal_with_traders_delight(text)
        request_logger.debug(f"Fit order from text={text}")
        is_entry_order = self.get_is_entry_order(text)
        # split the text into words
        words = text.split()
        if len(words) == 0 or len(words) == 1:
            request_logger.debug(
                "Just empty string or only one word, so can not be a trade, we ignore."
            )
        elif words[1] == "CALL:":
            self.segment = words[0]
            order = self.set_call(words, is_entry_order)
        elif words[1] == "UPDATE:":
            self.segment = words[0]
            order = self.set_update(words)
        else:
            request_logger.debug(f"Action={words[1]} not known, choose CALL: or UPDATE:")
            order = Order()
        return order

    def upper(self, text: str) -> str:
        """Put all text in upper cases.

        Sometimes it has info about pending order in capital or lower.
        """
        return text.upper()

    def deal_with_slash(self, text: str) -> str:
        """Deal with /.

        Meisha gives / when there are several TPs in different formats:
        TARGET 1.9275 /1.9295
        TARGET 1.9525 /1.9505
        TARGET 1.9472/1.9492

        Find if there is a / and if so enter a space before and after.
        """
        if "/" not in text:
            return text
        # if before it there is no space, add it
        index = text.index("/")
        if text[index - 1] != " ":
            text = text[:index] + " " + text[index:]
        # if after there is no space, add it
        index = text.index("/")
        if text[index + 1] != " ":
            text = text[: index + 1] + " " + text[index + 1 :]  # noqa
        return text

    def deal_with_traders_delight(self, text: str) -> str:
        """Deal with TRADERS DELIGHT, as two words, and we expect one."""
        if "TRADERS DELIGHT CALL:" in text:
            if "XAUUSD" in text:
                text = text.replace("TRADERS DELIGHT", "COMEX")
            else:
                text = text.replace("TRADERS DELIGHT", "TRADERSDELIGHT")
        elif "TRADERS DELIGHTUPDATE:" in text:
            if "XAUUSD" in text:
                text = text.replace("TRADERS DELIGHTUPDATE", "COMEX UPDATE")
            else:
                text = text.replace("TRADERS DELIGHTUPDATE", "TRADERSDELIGHT UPDATE")
        return text

    def get_is_entry_order(self, text: str) -> bool:
        """Return a bool if entry order, if false it is a market order.

        If at end of text there is (PENDING ORDER).
        """
        return "PENDING ORDER" in text

    def set_call(self, words: List[str], is_entry_order: bool) -> Order:
        """Fill values for CALL:, usually to open an order."""
        o = Order()
        o.action = "open"
        o.direction = words[2].lower()
        if o.direction not in ["buy", "sell"]:
            request_logger.warning(f"direction={o.direction} should be buy or sell!")
        o.symbol = words[3]
        if words[4] in ["ABOVE", "BELOW"]:
            o.type = "entry" if is_entry_order else "market"
            o.EPs = [float(words[5])]
        elif words[4] in ["AT"]:
            if words[5].isnumeric():
                o.type = "market"
                o.CMP = float(words[5])
                print(f"o.CMP={o.CMP}")
            elif "-" in words[5]:
                # then a range of values is given
                str_EP1, str_EP2 = words[5].split("-")
                print(str_EP1, str_EP2)
                if str_EP1.isnumeric() and str_EP2.isnumeric():
                    EP1 = float(str_EP1)
                    EP2 = float(str_EP2)
                    o.type = "marketrange"
                    o.EPs = [EP1, EP2]
                print(EP1, EP2)
            else:
                o.type = "market"
                print("Current Market price not given in text.")
                request_logger.warning("Current Market price not given in text.")
        else:
            request_logger.warning(f"type={words[4]} not known, expect ABOVE, BELOW, AT.")
        o.TPs.append(float(words[7]))
        if words[8] == "/":
            # there is a TP2
            o.TPs.append(float(words[9]))
            o.SL = float(words[11])
        else:
            # there is no TP2
            o.SL = float(words[9])
        return o

    def set_update(self, words: List[str]) -> None:
        """Fill values for UPDATE:, usually to close an order if not closed already.

        TODO: close also order that are not yet trades, if command is given.
        """
        o = Order()
        if "BOOKED" in words:
            # we will close the trade at market value
            o.action = "close"
            o.type = "market"
            o.symbol = words[2]
        else:
            request_logger.warning("For UPDATE there that is not to close not coded.")
        return o
