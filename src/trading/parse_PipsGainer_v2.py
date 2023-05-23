"""Module to parse one message for PipsGainer_v2 (from Harsh).

From Harsh, braodcast from researchesr, from May 2023.
It has a different format as the earliner one from fall 2022.
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


class Parse_PipsGainer_v2:
    """Parse a text message from PipsGainer (the central broadcast).

    One text message produces one order.
    .fit() returns Order.
    """

    def __init__(self) -> None:
        """Init."""
        self.author = "PGR"

        self.examples = [
            """
            FOREX
            BUY STOP CADCHF @ 0.6658
            TARGET 1  0.6678
            TARGET 2  0.6698
            STOP LOSS 0.6633
            CMP 0.6657
            """,
            """
            FOREX
            SELL STOP AUDNZD @ 1.0579
            TARGET 1  1.0559
            TARGET 2  1.0539
            STOP LOSS 1.0604
            CMP 1.0580
            """,
            """
            FOREX
            SELL STOP GBPCAD @ 1.6765
            TARGET 1  1.6745
            TARGET 2  1.6725
            STOP LOSS 1.6790
            CMP 1.6767
            """,
            """
            COMEX
            SELL STOP XAUUSD @ 1961
            TARGET 1  1956
            TARGET 2  1951
            STOP LOSS 1968
            CMP 1961.05
            """,
            """
            CRYPTO (SPOT)
            BUY STOP XRPUSDT @ 0.4671
            TARGET 1  0.4682
            TARGET 2  0.4699
            STOP LOSS 0.4650
            CMP 0.4661
            """,
            """
            FOREX
            BUY STOP GBPUSD @ 1.2460
            TARGET 1  1.2480
            TARGET 2  1.2500
            STOP LOSS 1.2435
            CMP 1.2460
            """,
            """
            FOREX
            BUY STOP EURUSD @ 1.0822
            TARGET 1  1.0842
            TARGET 2  1.0862
            STOP LOSS 1.0797
            CMP 1.0820
            """,
            """
            COMEX
            BUY STOP XAUUSD @ 1976
            TARGET 1  1981
            TARGET 2  1986
            STOP LOSS 1969
            CMP 1975.90
            """,
            """
            Target 1 hit
            """,
            """
            BOOK AT CMP 1980.50
            """,
            """
            Target 1 hit in gold
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

        Sometimes there are two lines for the same order, split by \n.
        And also there are several orders in the same text message, also separted by \n.
        That means that two of \n separate texts for one order.
        We split by that and then create a function that parses for one order.
        """
        text = text.upper()
        # print("initial text")
        # print(text)

        orders = []
        for text_one in text.split("\n\n"):
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
        if "BUY" in text or "SELL" in text:
            o = self.parse_for_order_open(o, text)
        # elif "MODIFY" in text or "SET" in text:
        #    o = self.parse_for_order_modify(o, text)
        # elif "BOOK PROFIT" in text or "CLOSE" in text:
        #     o = self.parse_for_order_close(o, text)
        else:
            o = self.parse_for_order_announcement(o, text)
        return o

    def parse_for_order_open(self, o: Order, text: str) -> Order:
        """Parse for order open.

        FOREX SELL STOP AUDNZD @ 1.0579 TARGET 1 1.0559 TARGET 2 1.0539 STOP LOSS 1.0604 CMP 1.0580 # noqa
        COMEX SELL STOP XAUUSD @ 1961 TARGET 1 1956 TARGET 2 1951 STOP LOSS 1968 CMP 1961.05 # noqa
        CRYPTO (SPOT) BUY STOP XRPUSDT @ 0.4671 TARGET 1 0.4682 TARGET 2 0.4699 STOP LOSS 0.4650 CMP 0.4661 # noqa
        """
        print("text new")
        print(text)
        text = text.replace("CRYPTO (SPOT)", "CRYPTO")
        elements = text.split()
        o.segment = elements[0]
        o.action = "open"
        o.symbol = elements[3]
        # for now treat as market orders, as CMP very close to the entry price
        # in future we can tune if worth to have stop orders
        if elements[1] == "BUY":
            o.type = "entry"
            o.direction = "buy"
        elif elements[1] == "SELL":
            o.type = "entry"
            o.direction = "sell"
        else:
            print("WARNING! Neither BUY nor SELL!")
            o.action = "error"
            return o

        # entry price is at sixth position
        try:
            o.EPs.append(float(elements[5]))
        except ValueError:
            o.action = "error"
            return o

        # TP1 is at ninth position
        try:
            o.TPs.append(float(elements[8]))
        except ValueError:
            o.action = "error"
            return o

        # TP2 is at 12th position
        try:
            o.TPs.append(float(elements[11]))
        except ValueError:
            o.action = "error"
            return o

        # SL is at 15th position
        try:
            o.SL = float(elements[14])
        except ValueError:
            o.action = "error"
            return o

        # CMP is at 17th position
        try:
            o.CMP = float(elements[16])
        except ValueError:
            o.action = "error"
            return o

        return o

    def parse_for_order_announcement(self, o: Order, text: str) -> Order:
        """Parse for order announcement."""
        o.action = "announcement"
        return o
