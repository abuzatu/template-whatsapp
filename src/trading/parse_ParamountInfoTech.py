"""Module to parse one text message from ParamountInfoTech (Akib)."""

import re
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


class Parse_ParamountInfoTech:
    """Parse one text message from ParamountInfoTech (Akib).

    One text message can produce one or several orders.
    .fit() returns List[Order].
    """

    def __init__(self) -> None:
        """Init."""
        self.author = "PMT"

        # action: open order to trade v1
        self.examples_open_v1 = [
            "BUY GOLD @ 1974 TP 1990 SL 1960",
            "BUY GOLD 1986, TP 2009, SL 1970",
            "BUY GOLD 1966, TP 1989, SL 1947",
            "BUY GOLD 2011, TP 2026, SL 1998",
            "SELL GOLD 2016, TP 2001, SL 2029",
            "BUY GOLD 2014, TP 2031, SL 1998",
            "SELL GOLD 2007, TP 1982, SL 2029",
            "BUY GOLD 2011, TP 2028, SL 1998",
            "Sell Gold 2027, TP 2013, SL 2039",
            "GOLD BUY 2028, TP 2042, SL 2015",
            "Sell Gold 2030, TP 2009, SL 2048",
            "Buy Gold 2024, TP 2051, SL 2003",
            "Sell Gold 2026, TP 2009, SL 2039",
            "Sell gold 2049, TP 2032, SL 2065",
            "BUY GOLD 2035, TP 2055, SL 2018",
            "BUY GOLD 2006, TP 2016, SL 1997",
            "BUY US30 33670, TP 33945, SL 33435",
            "SELL US30 33480, TP 33210, SL 33735",
        ]

        # action: open order to trade v2
        self.examples_open_v2 = [
            "Buy... US30...... @33565.... Target=33870... StopLoss=33296",
            """
            Sell..... Gbp/Aud...@1.86840..
            Target=1.86041... StopLoss=1.87612
            """,
            """
            Sell... Eur/Aud.....@1.62203..
            Target=1.61450...StopLoss=1.62940

            Sell... Eur/Cad...@1.45219...
            Target=1.44295...stopLoss=1.46137

            Sell..... Gbp/Aud...@1.86840..
            Target=1.86041... StopLoss=1.87612
            """,
            "Sell............Aud/Cad............@0.89428...........Target=0.88787...........StopLoss=0.90021",  # noqa
            "Sell.... Aud/Nzd....@1.06193..Target=1.05505... STOPLOSS=1.06868",
            """
            Sell.... Aud/Nzd....@1.06193..
            Target=1.05505... STOPLOSS=1.06868
            """,
            """
            Buy.... Wti.... @72.647....
            Target=74.595.... StopLoss=70.749
            """,
            """
            Buy... Nzd/Cad...@0.84153....
            Target=0.84687.... StopLoss=0.83633
            """,
            """
            Sell... Wti.... @70.328....
            Target=68.612.... StopLoss=71.874
            """,
            """
            Buy... Chf/Jpy...@152.380...
            Target=153.214... StopLoss=151.554
            """,
            """
            Buy.... Nzd/Jpy...@85.288...
            Target=86.005.... StopLoss=84.582
            """,
            """
            Sell..... Usd/Chf....@0.89393..
            Target=0.88924... StopLoss=0.89854
            """,
            """
            Buy.... Gbp/Usd....@1.24943..
            Target=1.25449... StopLoss=1.24296
            """,
            """
            Sell... Aud/Usd...@0.66705..
            Target=0.66354... StopLoss=0.67006

            Sell.... Aud/Chf...@0.59736...
            Target=0.59280... StopLoss=0.60170
            """,
            """
            Buy.... Aud/Cad....@0.90296..
            Target=0.90671... StopLoss=0.90113
            """,
            """
            Buy.... Chf/Jpy...@151.660...
            Target=152.625.... StopLoss=150.708

            Buy..... Usd/Jpy....@136.148..
            Target=137.158... StopLoss=135.163

            Buy..... Eur/Jpy....@147.880...
            Target=148.844.... StopLoss=146.975
            """,
            """
            Buy.... Gbp/Nzd....@2.00019..
            Target=2.01486... StopLoss=1.98589

            Sell... Nzd/Usd...@0.626039..
            Target=0.61782.... StopLoss=0.63346

            Buy.... Eur/Nzd....@1.74493..
            Target=1.76515... StopLoss=1.72495
            """,
            """
            Sell... Cad/Jpy....@100.181...
            Target=99.425... StopLoss=100.927

            Sell.... Chf/Jpy.....@150.745...
            Target=149.647... StopLoss=151.804

            Sell.... Gbp/Jpy.....@169.385..
            Target=168.230... StopLoss=170.484

            Sell..... Usd/Jpy....@134.215..
            Target=133.116... StopLoss=135.314
            """,
            """
            Sell... Eur/Chf....@0.97581...
            Target=0.97229... StopLoss=0.98004
            """,
            """
            Buy.... Chf/Jpy..@152.206..
            Target=153.487... StopLoss=151.172
            """,
            """
            Sell....Aud/Chf....@0.60301...
            Target=0.59798... StopLoss=0.60603

            Sell.... Nzd/Jpy....@85.339....
            Target=84.712.... StopLoss=85.930
            """,
            """
            Buy.... Aud/Usd...@0.67746..
            Target=0.68360.. StopLoss=0.67149
            """,
            """
            Sell.. Gold.... @2022.97....
            Target=1997.40... StopLoss=2048.29
            """,
            """
            Sell... Gbp/Cad....@1.69131...
            Target=1.68330... StopLoss=1.69907

            Buy..... Aud/Nzd...@1.07293..
            Target=1.08141... StopLoss=1.06465
            """,
            """
            Sell.... US30...... @33211.....
            Target=32939.... StopLoss=33411
            """,
            """
            Sell.... Usd/Jpy....@133.931...
            Target=133.010... StopLoss=134.818

            Sell.... Eur/Aud...@1.63949...
            Target=1.63182... StopLoss=1.64711

            Sell.... Gbp/Aud....@1.87174..
            Target=1.86253... StopLoss=1.88072

            Sell.... Eur/Jpy....@147.909...
            Target=146.824.... StopLoss=, 148.802
            """,
            """
            Buy.... Eur/Cad...@1.50634..
            Target=1.51399... StopLoss=1.49930
            """,
            """
            Sell.... Chf/Jpy....@151.783...
            Target=150.221... StopLoss=153.135

            Sell.... Eur/Jpy....@148.722...
            Target=146.959... StopLoss=150.330
            """,
        ]

        # action: modify trade
        self.examples_modify = [
            "modify traget price at 33580 in us30 now",
            "modify target price at 1968 in gold",
            "Modify target price at 1.0600 in audnzd",
            "Modify target price at 0.8922 in audcad",
            "Modify target price at 1976 in gold",
            "Modify target price at 70.12 in WTI",
            "modify stop loss to 1996 in gold",
            "Set target price at 0.9045 in audcad",
            "SET TARGET PRICE AT 85.13 in Nzdjpy",
            "Set target price at 0.6010 in AUDCHF",
            "Set target price at 1.0749 in audnzd",
            "set target price at 1.0709 in AUDNZD",
            "Set target price at 1.6900 in GBPCAD",
            "Set target price at 33180 in us30",
            """
            Set target price at 133.75 in usdjpy


            Set target price at 1.8700 in gbpaud
            """,
            """
            modify traget price at 33580 in us30 now

            modify target price at 1968 in gold

            modify target price at 1.6205 in euraud

            modify target price at 1.4507 in eurcad
            """,
        ]

        # action: close trade
        self.examples_close = [
            "Book profit and close gold now",
            "Book profit and close gbpaud now at 1.8660",
            "Book profit and close oil now",
            "Close audnzd on cost",
            "Close gold now in small profit at 1988.15",
            "Book profit and close nzdcad now at 0.8436",
            "Book profit and close chfjpy now at 152.51",
            "Book profit and close nzdjpy now at 85.44",
            "Book profit and close gold now at 2008",
            "Close AUDUSD now in small loss 0.6673",
            "Close gold now at loss at 2009.81",
            "Book profit and close usdchf now at 0.8929",
            "Book profit and close gbpusd now at 1.2511",
            "Close audchf now at cost or small loss",
            "Book profit and close gold now at 2013.60",
            "Book profit and close USDJPY now at 136.27",
            "Book profit and close EURJPY now at 148.03",
            "Book profit and close CHFJPY now at 151.76",
            "Book profit and close gold now at 2016.80",
            "Close gold in profit",
            "Book profit and close gold now at 2003.75",
            "Book profit and close nzdusd  now at 0.6244",
            "Book profit and close gold now at 2012.50",
            "Book profit and close eurchf now at 0.9733",
            "Book profit and close Eurnzd now at 1.7475",
            "Book profit and close gbpnzd now at 2.0029",
            "Book profit and close usdjpy now at 133.87",
            "Book profit and close gbpjpy now at 169.14",
            "Book profit and close CHFJPY now at 150.32",
            "Book profit and close cadjpy now at 100.01",
            "Close gold now at 2027.90",
            "Close audchf in Profit now at 0.6009",
            "Book profit and close gold now at 2028",
            "Book profit and close gold now at 2026",
            "Book profit and close gold now at 2024.70",
            "book profit and close gbpcad now at 1.6890",
            "Book profit and close us30 now at 33698",
            "Book profit and close us30 now at 337698",
            "Book profit and close gold now",
            "Close eurjpy in Profit now",
            "Book profit and close euraud",
            "Book profit and close gold now",
            "Book profit and close eurjpy",
            "Book profit and close CHFJPY",
            "Book profit and close eurcad now in small profit",
            "Book profit and close gold now at 2037",
            "Book profit and close nzdjpy",
            "Book profit and close audjpy",
            "Book profit and close us30 now at 33441",
            "Book profit and close gold now at 2045",
        ]

        # no action to do, just announcement about trade result
        self.examples_announcement = [
            "Tp hit in us30",
            "Stop loss hit in gold kindly wait for the recovery trade",
            "Stop loss hit in oil",
            "Kindly wait for recovery trades",
            "I am going for a meeting will be back after 1 hour",
            "SL hit in gold please wait for fresh recovery trades",
            """
            I am leaving for today due to some personal reason now

            Will comeback tomorrow
            """,
            "SL hit us30",
            "SL hit usdjpy",
            "I will be in meeting for next one hour",
            "Stop loss hit in gbpchf",
        ]

        # add them all
        self.examples = (
            self.examples_open_v1
            + self.examples_open_v2
            + self.examples_modify
            + self.examples_close
            + self.examples_announcement
        )

        self.examples = (
            # self.examples_open_v1
            self.examples_open_v2
            # self.examples_modify
            # self.examples_close
            # self.examples_announcement
        )

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
        elif "MODIFY" in text or "SET" in text:
            o = self.parse_for_order_modify(o, text)
        elif "BOOK PROFIT" in text or "CLOSE" in text:
            o = self.parse_for_order_close(o, text)
        else:
            o = self.parse_for_order_announcement(o, text)
        return o

    def parse_for_order_open(self, o: Order, text: str) -> Order:
        """Parse for order open.

        There are two styles, maybe coming from different researchers.
        1) usually in gold
        "BUY GOLD @ 1974 TP 1990 SL 1960",
        2) usually in forex
        "Sell... Gbp/Cad....@1.69131... Target=1.68330... StopLoss=1.69907"

        Let's treat them separately.
        """
        if "TP" in text and "SL" in text:
            o = self.parse_for_order_open_v1(o, text)
        elif "TARGET" in text and "STOPLOSS" in text:
            o = self.parse_for_order_open_v2(o, text)
        else:
            print("WARNING: Parse for order open but ca not find version")
            o = Order()
        return o

    def parse_for_order_open_v1(self, o: Order, text: str) -> Order:
        """Parse for order open v1.

        usually in gold:
        BUY GOLD @ 1974 TP 1990 SL 1960
        BUY GOLD 1986, TP 2009, SL 1970
        GOLD BUY 2028, TP 2042, SL 2015

        We will remove @ and ,
        Then values come in the right order.
        Note the first two can sometimes be exchanged.
        """
        text = text.replace("@", " ").replace(",", " ")
        # print(text)
        elements = text.split()
        request_logger.debug(f"elements={elements}.")
        if elements[0] == "BUY" or elements[1] == "BUY":
            o.action = "open"
            o.type = "entry"
            o.direction = "buy"
            if elements[0] == "BUY":
                o.symbol = get_symbol(elements[1])
            elif elements[1] == "BUY":
                o.symbol = get_symbol(elements[0])
        elif elements[0] == "SELL" or elements[1] == "SELL":
            o.action = "open"
            o.type = "entry"
            o.direction = "sell"
            if elements[0] == "SELL":
                o.symbol = get_symbol(elements[1])
            elif elements[1] == "SELL":
                o.symbol = get_symbol(elements[0])
        else:
            print("WARNING! Neither BUY nor SELL!")
            o.action = "error"
            return o

        # CMP
        try:
            o.CMP = float(elements[2])
        except ValueError:
            o.action = "error"
            return o

        # TP
        try:
            o.TPs = [float(elements[4])]
        except ValueError:
            o.action = "error"
            return o

        # SL
        try:
            o.SL = float(elements[6])
        except ValueError:
            o.action = "error"
            return o

        return o

    def parse_for_order_open_v2(self, o: Order, text: str) -> Order:
        """Parse for order open v2.

        usually in forex, very irregular in number of dots and spaces:
        "Sell... Gbp/Cad....@1.69131... Target=1.68330... StopLoss=1.69907"
        """
        # replace any group of two or more dots with empty space
        text = re.sub(r"\.{2,}", " ", text)
        # print(text)
        elements = text.split()
        if elements[0] == "BUY":
            o.action = "open"
            o.type = "entry"
            o.direction = "buy"
        elif elements[0] == "SELL":
            o.action = "open"
            o.type = "entry"
            o.direction = "sell"
        else:
            print("WARNING! Neither BUY nor SELL!")
            o.action = "error"
            return o

        # symbol is at second position, but remove the / which exists for forex
        o.symbol = get_symbol(elements[1].replace("/", ""))

        # CMP is at third position, but remove the @ in front
        try:
            o.CMP = float(elements[2].replace("@", ""))
        except ValueError:
            o.action = "error"
            return o

        # TP is at fourth position, but remove the TARGET= in front
        try:
            o.TPs = [float(elements[3].replace("TARGET=", ""))]
        except ValueError:
            o.action = "error"
            return o

        # SL is at fifth position, but remove the STOPLOSS= in front
        try:
            o.SL = float(elements[4].replace("STOPLOSS=", ""))
        except ValueError:
            o.action = "error"
            return o

        return o

    def parse_for_order_modify(self, o: Order, text: str) -> Order:
        """Parse for order modify."""
        # correct for typos as they happen sometimes
        text = text.replace("TRAGET", "TARGET")

        symbol_candidates = []
        for word in text.split():
            if word.replace(".", "1").isnumeric():
                if "TARGET PRICE" in text:
                    o.TPs = [float(word)]
                elif "STOP LOSS" in text:
                    o.SL = float(word)
                else:
                    print("WARNING! Neither TARGET PRICE, nor STOP LOSS.")
            elif word in [
                "MODIFY",
                "SET",
                "TARGET",
                "PRICE",
                "STOP",
                "LOSS",
                "AT",
                "IN",
                "TO",
                "NOW",
            ]:
                pass
            else:
                print(f"word is likely the asset={word}")
                symbol_candidates.append(word)
        if len(symbol_candidates) == 0:
            print("WARNING! There is no candidate remaining for symbol.")
        elif len(symbol_candidates) > 1:
            print("WARNING! There are several candidates remaining for symbol.")
        else:
            # good, there is only one candidate remaining for symbol
            word = symbol_candidates[0]
            o.symbol = get_symbol(word)
        return o

    def parse_for_order_close(self, o: Order, text: str) -> Order:
        """Parse for order close.

        Close is to be followed immediately at market price.
        """
        o.action = "close"
        o.type = "market"
        # let's try to find the symbol of the asset to close
        # since words can come in any order, we will eliminate all the words one by one
        # that are known to be not be the asset, and will eliminate the price too
        # and what remains should be the asset
        symbol_candidates = []
        for word in text.split():
            if word.replace(".", "1").isnumeric():
                o.CMP = float(word)
            elif word in [
                "BOOK",
                "PROFIT",
                "AND",
                "CLOSE",
                "NOW",
                "AT",
                "IN",
                "SMALL",
                "LARGE",
                "BIG",
                "LOSS",
                "COST",
                "OR",
            ]:
                pass
            else:
                print(f"word is likely the asset={word}")
                symbol_candidates.append(word)
        if len(symbol_candidates) == 0:
            print("WARNING! There is no candidate remaining for symbol.")
        elif len(symbol_candidates) > 1:
            print("WARNING! There are several candidates remaining for symbol.")
        else:
            # good, there is only one candidate remaining for symbol
            word = symbol_candidates[0]
            o.symbol = (
                word if word not in dict_word_symbol.keys() else dict_word_symbol[word]
            )
        return o

    def parse_for_order_announcement(self, o: Order, text: str) -> Order:
        """Parse for order announcement."""
        o.action = "announcement"
        return o
