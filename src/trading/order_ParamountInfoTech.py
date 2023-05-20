"""Module for Order for ParamountInfoTech (Akib)."""

from typing import List

from trading.order_base import Order
from utils.logger import request_logger


class Order_ParamountInfoTech(Order):
    """Order from ParamountInfoTech (Akib)."""

    def __init__(self) -> None:
        """init."""
        super().__init__()

        # action: open order to trade
        self.examples_open = [
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
            "Buy... US30...... @33565.... Target=33870... StopLoss=33296",
            "BUY US30 33670, TP 33945, SL 33435",
            "SELL US30 33480, TP 33210, SL 33735",
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
            "Sell............Aud/Cad............@0.89428...........Target=0.88787...........StopLoss=0.90021",
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
        ]

        # action: modify trade
        self.examples_modify = [
            "modify traget price at 33580 in us30 now",
            "modify target price at 1968 in gold",
            "Modify target price at 1.0600 in audnzd",
            "Modify target price at 0.8922 in audcad",
            "Modify target price at 1976 in gold",
            """
            modify traget price at 33580 in us30 now

            modify target price at 1968 in gold

            modify target price at 1.6205 in euraud

            modify target price at 1.4507 in eurcad
            """,
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
            Sell.... Chf/Jpy....@151.783...
            Target=150.221... StopLoss=153.135

            Sell.... Eur/Jpy....@148.722...
            Target=146.959... StopLoss=150.330
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
            "BUY GOLD 2006, TP 2016, SL 1997",
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
            self.examples_open
            + self.examples_modify
            + self.examples_close
            + self.examples_announcement
        )
