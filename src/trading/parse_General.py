"""Module to parse universally messages in different formats to place trades.

There is a common pattern once pre-process the models and we try to use it,
so that we can maintain easily to send to a particular account messages
from different providers.

The common cleaning:
o transform to an empty space all symbols: comma, %, = 
o replace new lines with spaces so all is on one line
o remove all the empty spaces
o put all in capital letters

The common processing for BUY or SELL
o assume each order to open starts with BUY or SELL
- allow to be more than than one such order in one Whatsapp message (Akib)
- There can be several TP, depending how they form it
- value is the next word after a particular value
- this format should also allow to start a trade with BUY GOLD only

Then close order
- after that we do close
- we should also close with just CLOSE GOLD
 
Then update or modify, usually for TP or SL
 
Then just information.
 
We would like to identify the categories early on and process them generally.
"""

import re
from typing import List

from trading.order import Order
from utils.logger import request_logger


KEYWORDS_OPEN = [
    "BUY",
    "SELL",
    "BUY_LIMIT",
    "SELL_LIMIT",
    "BUY_STOP",
    "SELL_STOP",
]

KEYWORDS_REMOVE = [
    "AGAIN",
]

KEYWORDS_CLOSE = [
    "CLOSE",
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
    "SMALL",
    "BOOK",
    "PROFIT",
    "AND",
    "ON",
    "COST",
    "OR",
]

KEYWORDS = ["TP", "SL", "CMP"] + KEYWORDS_OPEN


def if_text_starts_with_any_of_prefixes(text: str, prefixes: List[str]) -> bool:
    """Check if a text starts with any of the prefixes."""
    result = False
    for prefix in prefixes:
        result = result or text.startswith(prefix)
    return result


def if_text_contains_any_of_words(text: str, words: List[str]) -> bool:
    """Check if a text starts with any of the prefixes."""
    result = False
    for word in words:
        result = result or word in text
    return result


dict_word_symbol = {
    "GOLD": "XAUUSD",
    "OIL": "XTIUSD",
    "WTI": "XTIUSD",
}


def get_symbol(word: str) -> str:
    """Get symbol."""
    return word if word not in dict_word_symbol.keys() else dict_word_symbol[word]


dict_action_suffix_type = {
    "": "market",
    "_LIMIT": "limit",
    "_STOP": "stop",
}


class Parse_General:
    """Parse one general text message.

    One text message can produce one or several orders.
    .fit() returns List[Order].
    """

    def __init__(self, author: str) -> None:
        """Init."""
        self.author = author

        # action: open order to trade v1 - Akib for gold
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

        # action: open order to trade v2 - Akib for forex
        self.examples_open_v2 = [
            "Sell.... Nzd/Jpy...@85.217....Target=83.910... StopLoss=86.511 Sell..... Aud/Jpy.....@91.193...Target=90.424.... StopLoss=91.950 Sell.... Chf/Jpy.....@153.486..Target=152.674... StopLoss=154.256",  # noqa
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

        # action: open order to trade v3 - PipsGainer Researcher one at a time
        self.examples_open_v3 = [
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
            BOOK AT CMP 1980.50
            """,
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
            """
            BUY STOP XAUUSD @ 1965
            TARGET 1  1970
            TARGET 2  1975
            STOP LOSS 1958
            """,
        ]

        # action: open order to trade v3 - PipsGainer Researcher several at a time
        self.examples_open_v4 = [
            """
            COMEX
            BUY STOP XAUUSD @ 1965
            TARGET 1  1970
            TARGET 2  1975
            STOP LOSS 1958
            CMP 1964.70

            FOREX 
            BUY STOP GBPUSD @ 1.2558
            TARGET 1  1.2578
            TARGET 2  1.2598
            STOP LOSS 1.2532
            CMP 1.2557
            """,
        ]

        # action: open order to trade v4 - PipsGainer Vinay
        self.examples_open_v5 = [
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
            """
            ⚡Gold sell again 1968
            ⚡TP  1966
            ⚡TP  1968
            ⚡TP  1962
            ⚡TP  1960
            ⚡ SL 1975
            """,
            """
            Gold sell  1958 1960 
            TP  1954
            TP  1952
            TP  1950
            SL 1967
            """,
            """
            GOLD BUY 1944 
            Tp  1950 
            Sl 1936
            """,
        ]

        # action: open order to trade v6 - just two words
        self.examples_open_v6 = [
            "GOLD BUY",
            "GOLD SELL",
            "BUY GOLD",
            "SELL GOLD",
            "GOLD SELL NOW",
        ]

        # action: close trade v1 - Akib
        self.examples_close_v1 = [
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

        # action: close trade v1 - just two words
        self.examples_close_v2 = [
            "GOLD CLOSE",
            "CLOSE GOLD",
        ]

        # action: close trade v1 - just two words
        self.examples_regular_v1 = [
            "Now I will say buy gold and you will see that it buys",
            "Now I will say sell gold and you will see that it sells",
            "Now I will say close gold and you will see that it closes",
            "You should use buy or sell market order, but not buy_limit or stop_limit.",
        ]

        self.examples = (
            []
            # + self.examples_open_v1
            # + self.examples_open_v2
            # + self.examples_open_v3
            + self.examples_open_v4
            # + self.examples_open_v5
            # + self.examples_open_v6
            # self.examples_modify
            # + self.examples_close_v1
            # + self.examples_close_v1
            # self.examples_announcement
            # + self.examples_regular_v1
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

        Actually sometimes the \n does not appear, so we build a function to split
        based on starting on BUY or SELL
        """
        print(f"text_original={text}")

        text = self.clean_text(text)
        print(f"text_cleaned ={text}")

        # if there are several orders in one message assume they start by a KEYWORD_OPEN
        # e.g. Akib for forex, so split them
        # splitting by KEYWORD_OPEN and include the delimiter in the result
        #
        # print(f"KEYWORDS_OPEN={KEYWORDS_OPEN}")
        if if_text_starts_with_any_of_prefixes(text, KEYWORDS_OPEN):
            # Akib forex
            # split by "BUY" and "SELL" and including the delimiter in the result
            # "(?:\b(BUY|SELL|BUY_LIMIT|SELL_LIMIT|BUY_STOP|SELL_STOP)\b)"
            # ("Text starts with one of the KEYWORDS_OPEN")
            # but automate as below
            pattern = rf"(?:\b({'|'.join(KEYWORDS_OPEN)})\b)"
            word_list = re.split(pattern, text)
            # remove empty strings and whitespace
            word_list = [word.strip() for word in word_list if word.strip()]
            # print(f"word_list={word_list}")
            # create the text for each order
            order_texts = []
            for word in word_list:
                # print(f"word={word}")
                if word in KEYWORDS_OPEN:
                    # a new word starts
                    # print(f"A new order starts")
                    order_texts.append(word)
                else:
                    # current word continues
                    order_texts[-1] += " " + word

        else:
            # assume there is only one text
            # print("Assume there is only one text = {text}")
            order_texts = [text]

        # for each text build one order
        orders = []
        for text_one in order_texts:
            # print(f"New text_one={text_one}")
            o = self.build_one_order(text_one)
            orders.append(o)
        return orders

    def clean_text(self, text: str) -> str:
        """Clean text."""
        # place all in capital letters
        text = text.upper()

        # reomove ⚡
        text = text.replace("⚡", "")

        # replace special character with spaces
        pattern = r"[,@=]"  # Regular expression pattern matching comma, @, or equal
        text = re.sub(pattern, " ", text)

        # replace any group of two or more dots with empty space
        # needed for the FOREX style for Akib
        pattern = r"\.{2,}"
        text = re.sub(pattern, " ", text)

        # put all in one line, while removing several spaces, tabs, etc
        text = " ".join(text.split())

        # remove a / that is in between letters, e.g. CAD/CHF -> CADCHF
        pattern = r"(?<=[a-zA-Z])/(?=[a-zA-Z])"
        text = re.sub(pattern, "", text)

        # replace various longer words with "SL"
        text = text.replace("STOP LOSS", "SL").replace("STOPLOSS", "SL")

        # replace various longer words with "TP"
        text = text.replace("TARGET", "TP")

        # sometimes there several TPs, and they have names "TP 1 ", or TP 1 "
        # we want to replace their number, as we add them to a list,
        # they usually come in order, but we can sort them anyway
        # usually there are no more than 4 TPs, so we can check for all 9 digits
        # and this should cover all spaces
        for i in range(1, 10):
            text = text.replace(f"TP {i} ", "TP ").replace(f"TP{i} ", "TP ")

        # Pips Gainer Research sometimes give at beginning the segment
        # we want to remove it
        for segment in ["FOREX", "COMEX", "CRYPTO (SPOT)"]:
            text = text.replace(f"{segment} ", "")

        # remove some filling words not relevant, e.g. AGAIN
        for word in KEYWORDS_REMOVE:
            text = text.replace(word, "")

        # some are limit and stop orders, let's group them into one word
        text = text.replace("BUY LIMIT", "BUY_LIMIT")
        text = text.replace("BUY STOP", "BUY_STOP")
        text = text.replace("SELL LIMIT", "SELL_LIMIT")
        text = text.replace("SELL STOP", "SELL_STOP")

        # ready
        return text

    def build_one_order(self, text: str) -> Order:
        """Parse one text to build one Order."""
        # print(f"Build one order from text={text}")
        o = Order()
        # fill already the author
        o.author = self.author
        # fill already the text as passed originally
        o.text = text
        if if_text_contains_any_of_words(text, KEYWORDS_OPEN):
            o = self.parse_for_order_open(o, text)
        elif "MODIFY" in text or "SET" in text:
            o = self.parse_for_order_modify(o, text)
        elif "BOOK PROFIT" in text or "CLOSE" in text:
            o = self.parse_for_order_close(o, text)
        else:
            o = self.parse_for_order_announcement(o, text)
        # return
        return o

    def parse_for_order_announcement(self, o: Order, text: str) -> Order:
        """Parse for order announcement."""
        o.action = "announcement"
        return o

    def parse_for_order_modify(self, o: Order, text: str) -> Order:
        """Parse for order modify."""
        o.action = "modify"
        return o

    def parse_for_order_open(self, o: Order, text: str) -> Order:
        """Parse for order open.

        Read the words one by one and depending what they are, parse them and remove
        That way we can have them in any different order.

        Action and asset can come in either order.
        We should not hard code assets to allow to add later new assets not known now.
        So we check for the keywords, as those are few.
        """
        # print("AAAA for open")
        words = text.split()
        # check if the first word is one of the open keywords
        if words[0] in KEYWORDS_OPEN:
            # if the first element is the action, assume the second element is the asset
            action = words[0]
            symbol = words[1]
        elif words[1] in KEYWORDS_OPEN:
            # if the second element is the action, assume the first element is the asset
            action = words[1]
            symbol = words[0]
        else:
            # case not know if it starts with something else, treat as announcement
            o = self.parse_for_order_announcement(o, text)
            return o
        # print(f"action={action}, symbol={symbol}")
        # check the action
        if "BUY" in action:
            o.action = "open"
            o.direction = "buy"
            action_suffix = action.replace("BUY", "")
            o.type = dict_action_suffix_type[action_suffix]
        elif "SELL" in action:
            o.action = "open"
            o.direction = "sell"
            action_suffix = action.replace("SELL", "")
            o.type = dict_action_suffix_type[action_suffix]
        else:
            # case not known
            o = self.parse_for_order_announcement(o, text)
            return o
        # print(
        #    f"action={action}, symbol={symbol}, direction={o.direction}, "
        #    f"action_suffix={action_suffix}, type={o.type}"
        # )
        # check the symbol
        o.symbol = get_symbol(symbol)
        # print(f"o.symbol={o.symbol}")
        # now the first two words are done, so we can drop them
        words_reduced = words[2:]
        # print(f"words_reduced={words_reduced}")

        # let's convert the strings to numbers where possible
        words = []
        for word in words_reduced:
            try:
                word = float(word)
            except ValueError:
                # remains string
                word = word
            words.append(word)
        # print(f"words={words}")

        # next come one or more float numbers that represent the entry prices
        # find the first numbers and append to the entry prices
        # when first string is found, stop
        numbers = []
        for word in words:
            if isinstance(word, float):
                numbers.append(word)
            else:
                break
        # print(f"numbers={numbers}")
        if o.direction == "buy":
            # for buy, sort in increasing order
            numbers = sorted(numbers, reverse=False)
        else:
            # for sell , ort in decreasing order
            numbers = sorted(numbers, reverse=True)
        # add these in the field of entry prices
        o.EPs = numbers
        # now we can remove these elements
        words = words[len(numbers) :]
        # print(f"words={words}")

        # if "NOW" still present, remove it
        if "NOW" in words:
            words.remove("NOW")

        # next come pairs of strings and number, each string only one number
        # they can be in various orders, so that is why we want ot be generic
        # the strings are TP, SL, CMP
        for i, word in enumerate(words):
            # skip the numbers
            if isinstance(word, float):
                continue
            # we are left only with the strings at position i
            # and we know their value is at position i+1
            value = words[i + 1]
            if not (isinstance(word, str) and isinstance(value, float)):
                # this case is not known
                o = self.parse_for_order_announcement(o, text)
                return o
            # if here we are of correct expected types
            if word == "TP":
                # there can be several values for the target price
                if o.TPs is None:
                    # if no value added so far, create a list with one value
                    o.TPs = [value]
                else:
                    # if there is at least one value, append to it
                    o.TPs.append(value)
            elif word == "SL":
                # there is only one value for stop loss
                o.SL = value
            elif word == "CMP":
                # there is only one value for current market price
                o.CMP = value
            else:
                print(f"WARNING, got an unexpected word={word}")
                o = self.parse_for_order_announcement(o, text)
                return o

            # for TP, sort the values
            if o.direction == "buy":
                # for buy, sort in increasing order
                o.TPs = sorted(o.TPs, reverse=False)
            else:
                # for sell , ort in decreasing order
                o.TPs = sorted(o.TPs, reverse=True)

            # if current market price (CMP) is missing,
            # take it from the first value of entry prices, if this is present
            if o.CMP is None and o.EPs is not None and len(o.EPs) > 0:
                o.CMP = o.EPs[0]

        return o

    def parse_for_order_close(self, o: Order, text: str) -> Order:
        """Parse for order close."""
        o.action = "close"
        words = text.split()
        if len(words) == 2:
            if words[0] == "CLOSE":
                o.symbol = get_symbol(words[1])
            elif words[1] == "CLOSE":
                o.symbol = get_symbol(words[0])
            else:
                # case not know if it starts with something else, treat as announcement
                o = self.parse_for_order_announcement(o, text)

        # let's convert the strings to numbers where possible
        words_all = words[:]
        words = []
        for word in words_all:
            try:
                word = float(word)
            except ValueError:
                # remains string
                word = word
            words.append(word)
        # print(f"words={words}")

        # count the number of floats we have, if only one, assign it as the CMP
        words_all = words[:]
        numbers = []
        words = []
        for word in words_all:
            if isinstance(word, float):
                numbers.append(word)
            else:
                if word not in KEYWORDS_CLOSE:
                    words.append(word)
        # print(f"numbers={numbers}")
        if len(numbers) == 1:
            o.CMP = numbers[0]

        # from the words remove known words so that we remain only with the asset
        # normally here only one should be remaining and that should be the asset
        # print(f"words={words}")
        if len(words) == 1:
            o.symbol = get_symbol(words[0])
        else:
            # case not supported
            o = self.parse_for_order_announcement(o, text)
            return o
        return o
