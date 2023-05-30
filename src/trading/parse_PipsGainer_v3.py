"""Module to parse one message for PipsGainer_v3 (from Vinay).

From Vinay, from 30 May 2023. It has its own format, plus I want to code also
simple buy, sell, close, as I am not able to place TP and SL yet, so this would
be suitable for scalping strategy like he showed me on 29 May 2023.
"""

from typing import List

from trading.order import Order
from utils.logger import request_logger

dict_word_symbol = {
    "GOLD": "XAUUSD",
    "OIL": "XTIUSD",
    "WTI": "XTIUSD",
}


def get_symbol(word: str) -> str:
    """Get symbol."""
    return word if word not in dict_word_symbol.keys() else dict_word_symbol[word]


class Parse_PipsGainer_v3:
    """Parse a text message from PipsGainer (the central broadcast).

    One text message produces one order.
    .fit() returns Order.
    """

    def __init__(self) -> None:
        """Init."""
        self.author = "PGV"  # PipsGainerVinay

        self.examples = [
            """
            Gold sell 1955 1956

            TP  1950
            TP  1945

            SL 1962
            """,
            """
            Gold sell 1946

            TP  1940
            SL   1953
            """,
            """
            Gold sell 1951 1952

            TP  1948
            TP  1945
            TP  1943
            TP  1940

            SL 1960
            """,
            """
            GOLD BUY  1955

            TP  1962 
            TP  1969 

            Sl 1941
            """,
            "GOLD BUY",
            "GOLD SELL",
            "GOLD CLOSE",
            "BUY GOLD",
            "SELL GOLD",
            "CLOSE GOLD",
            # from research, to ignore for now
            """
            BUY STOP XAUUSD @ 1977
            TARGET 1  1984
            TARGET 2  1991
            STOP LOSS 1967
            """,
            """
            COMEX
            BUY STOP XAUUSD @ 1979
            TARGET 1  1984
            TARGET 2  1989
            STOP LOSS 1972
            """,
        ]

    def fit_examples(self) -> None:
        """Fit several texts as examples."""
        request_logger.info("Will start to fit examples.")
        for example in self.examples:
            print("")
            orders = self.fit(example)
            for o in orders:
                print(o)

    def fit(self, text: str) -> List[Order]:
        r"""Parse a text message with rule-based to build a list of Order.

        Place all in capital letters, as there is not consistent approach.

        Sometimes it is a long order, sometimes to use the few letters one for scalping.
        All at market order.
        """
        text = text.upper()
        # print("initial text")
        # print(text)

        orders = []
        for text_one in text.split("\n\n\n\n"):
            # this is the text used for one order
            # sometimes even this text is split on different lines
            # so we eliminate those
            # text_one = text_one.replace("\n", " ").replace("\t", " ")
            text_one = " ".join(text_one.split())
            # print("new text")
            # print(text_one)
            o = self.build_one_order(text_one)
            orders.append(o)
        return orders

    def build_one_order(self, text: str) -> Order:
        """Parse one text to build one Order."""
        o = Order()
        # fill already the author
        o.author = self.author
        # fill already the text as passed originally
        o.text = text

        # Removing empty strings and whitespace
        word_list = [text.strip() for text in text.split() if text.strip()]
        print(f"word_list={word_list}")
        if "@" in word_list:
            # skip as these are from the research
            o = self.parse_for_order_announcement(o, text)
        elif word_list[0] in ["BUY", "SELL", "CLOSE"]:
            # the asset is in position 1
            o.symbol = word_list[1]
            o.type = "market"
            if word_list[0] == "BUY":
                o.action = "open"
                o.type = "entry"
                o.direction = "buy"
            elif word_list[0] == "SELL":
                o.action = "open"
                o.type = "entry"
                o.direction = "sell"
            elif word_list[0] == "CLOSE":
                o.action = "close"
            else:
                o = self.parse_for_order_announcement(o, text)
        elif word_list[1] in ["BUY", "SELL", "CLOSE"]:
            # the asset is in position 0
            o.symbol = word_list[0]
            if word_list[1] == "BUY":
                o.action = "open"
                o.type = "entry"
                o.direction = "buy"
            elif word_list[1] == "SELL":
                o.action = "open"
                o.type = "entry"
                o.direction = "sell"
            elif word_list[1] == "CLOSE":
                o.action = "close"
            else:
                o = self.parse_for_order_announcement(o, text)
        else:
            # ignore the rest of the cases
            o = self.parse_for_order_announcement(o, text)
        return o

    def parse_for_order_announcement(self, o: Order, text: str) -> Order:
        """Parse for order announcement."""
        o.action = "announcement"
        return o
