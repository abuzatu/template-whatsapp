"""Module for transforming the Whatsapp message into an order.

The order can be then placed on different platforms with different APIs.
"""

from typing import Optional, List
import logging


class Order:
    """Class for Order from a message."""

    def __init__(
        self,
    ) -> None:
        """Initialize."""
        self.reset()

    def reset(self) -> None:
        """Reset."""
        self.segment: Optional[str] = None  # FOREX, COMEX, Indices, etc
        self.symbol: Optional[str] = None  # instrument to trade
        self.action: Optional[str] = None  # open or close
        self.type: Optional[str] = None  # market, entry (limit or stop orders)
        self.direction: Optional[str] = None  # buy or sell
        self.CMP: Optional[float] = None  # current market price
        self.EPs: List[float] = []  # entry prices (only one for limit or stop orders)
        # a list of two values if a range is given for market range
        self.SL: Optional[float] = None  # stop loss (SL)
        self.TPs: List[float] = []  # list of target prices (TPs) if several are given
        self.examples: List[str] = []  # list of examples

    def __str__(self) -> str:
        """String representation."""
        return (
            f"segment={self.segment}, "
            f"action={self.action}, "
            f"type={self.type}, "
            f"direction={self.direction}, "
            f"symbol={self.symbol}, "
            f"CMP={self.CMP}, "
            f"EPs={self.EPs}, "
            f"SL={self.SL}, "
            f"TPs={self.TPs}, "
        )

    def fit(self, text: str) -> None:
        """Fit (to be defined for each inherited class)."""
        pass

    def print(self) -> None:
        """Print."""
        print(self.__str__())

    def fit_examples(self) -> None:
        """fit_examples."""
        logging.info("Will start to fit examples.")
        for example in self.examples:
            print()
            self.fit(example)
            self.print()
            self.reset()
