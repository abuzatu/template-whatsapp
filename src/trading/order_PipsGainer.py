"""Module for Order for PipsGainer (the central broadcast)."""

from typing import List

from trading.order_base import Order
from utils.logger import request_logger


class Order_PipsGainer(Order):
    """Order from PipsGainer (the central broadcast)."""

    def __init__(self) -> None:
        """init."""
        super().__init__()
        self.examples = [
            """
            BASIC FOREX: BUY STOP NZDCAD 0.7985
            TP 0.8015
            SL 0.7945
            CMP 0.7983
            www.PipsGainer.com
            """,
            "BASIC FOREX: BUY STOP NZDCAD 0.7985 TP 0.8015 SL 0.7945 CMP 0.7983 www.PipsGainer.com",  # noqa
            "BASIC FOREX: SELL STOP USDCAD 1.3245 TP 1.3230 SL 1.3290 CMP 1.3251 www.PipsGainer.com",  # noqa
            """
            BASIC FOREX: BUY STOP NZDJPY 85.45
            TP 85.75
            SL 85.00
            CMP 85.43
            www.PipsGainer.com
            """,
            "BASIC COMEX: SELL LIMIT GOLD 1777 TP 1770 SL 1784 CMP 1776.60 www.PipsGainer.com",  # noqa
            "PRIME COMEX: SELL STOP WTI 80.00 TP 79.00 SL 81.00 CMP 80.08 www.PipsGainer.com",  # noqa
            """
            ACTIVATED
            """,
            """
            TP HIT
            """,
            """
            SL HIT
            """,
        ]

    def fit(self, text: str) -> None:
        """Initialize from a text message with rule-based."""
        if text.rstrip() in [
            "ACTIVATED",
            "TP HIT",
            "SL HIT",
        ]:
            # set no trade
            request_logger.warning("Update on a trade. Will ignore.")
            return
        # split the text into words
        request_logger.debug(f"text={text}")
        words = text.split()
        request_logger.debug(f"words={words}")
        if len(words) == 0 or len(words) == 1:
            request_logger.debug(
                "Just empty string or only one word, so can not be a trade, we ignore."
            )
        elif len(words) > 12 and words[12] == "www.PipsGainer.com":
            self.set_call(words)
        else:
            request_logger.debug("Regular message, will ignore.")
            pass

    def set_call(self, words: List[str]) -> None:
        """Fill values for CALL:, usually to open an order."""
        self.segment = words[1][0:-1]
        self.action = "open"
        self.direction = words[2].lower()
        if self.direction not in ["buy", "sell"]:
            request_logger.warning(f"direction={self.direction} should be buy or sell!")
        if words[3] in ["LIMIT", "STOP"]:
            self.type = "entry"
        else:
            request_logger.warning(f"type={words[3]} not known, expect LIMIT, STOP.")
        self.symbol = words[4]
        if self.symbol == "WTI":
            self.symbol = "USOilSpot"
        elif self.symbol == "GOLD":
            self.symbol = "XAUUSD"
        self.EPs = [float(words[5])]  # entry price
        self.TPs.append(float(words[7]))
        self.SL = float(words[9])
        self.CMP = float(words[11])  # current market price
        if words[12] != "www.PipsGainer.com":
            request_logger.warning(
                "Problem in format, as www.PipsGainer.com is not position 12!"
            )
            request_logger.warning(f"words={words}")
        if len(words) > 13:
            request_logger.info("This is an update")
            pass

    def set_update(self, words: List[str]) -> None:
        """Fill values for UPDATE:, usually to close an order if not closed already.

        Not used for now.
        """
        print(words)
        # find position of pipsgainer
        if "BOOKED" in words:
            # we will close the trade at market value
            self.action = "close"
            self.type = "market"
            self.symbol = words[2]
        else:
            request_logger.warning("For UPDATE there that is not to close not coded.")
