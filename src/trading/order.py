"""Module for transforming the Whatsapp message into an order.

The order can be then placed on different platforms with different APIs.
"""

import datetime
from typing import Optional, List


class Order:
    """Class for Order from a message."""

    def __init__(
        self,
        order_id: Optional[int] = 0,
    ) -> None:
        """Initialize."""
        self.id: Optional[int] = order_id
        self.reset()

    def reset(self) -> None:
        """Reset."""
        self.segment: Optional[str] = None  # FOREX, COMEX, Indices, etc
        self.symbol: Optional[str] = None  # instrument to trade
        self.action: Optional[str] = None  # open or close
        self.type: Optional[str] = None  # market, entry (limit or stop orders)
        self.direction: Optional[str] = None  # buy or sell
        self.CMP: Optional[float] = None  # current market price
        self.EPs: List[
            float
        ] = []  # entry prices (only one for limit, stop, close orders)
        # a list of two values if a range is given for market range
        self.SL: Optional[float] = None  # stop loss (SL)
        self.TPs: List[float] = []  # list of target prices (TPs) if several are given
        self.datetime: datetime.datetime = datetime.datetime.now()
        self.author: Optional[str] = None  # author that gave the signal
        self.text: Optional[str] = None  # the text from which the order was produced

    def set_id(self, id: int) -> None:
        """Set id."""
        self.id = id

    def __str__(self) -> str:
        """String representation."""
        return (
            f"id={str(self.id).zfill(5)}, "
            f'datetime={self.datetime.strftime("%Y-%m-%d %H:%M:%S")}, '
            f'author="{self.author}", '
            f"action={self.action}, "
            f"type={self.type}, "
            f"direction={self.direction}, "
            f"symbol={self.symbol}, "
            f"segment={self.segment}, "
            f"CMP={self.CMP}, "
            f"EPs={self.EPs}, "
            f"SL={self.SL}, "
            f"TPs={self.TPs}, "
            f'text="{self.text}", '
        )

    def print(self) -> None:
        """Print."""
        print(self.__str__())

    """
    TODO: class to inherit from pydantic
    and check that all the fields are in the required format.
    """
