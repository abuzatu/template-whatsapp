"""Module to run FixAPI from Hishal."""

# python
import sys

# our modules
from utils.logger import request_logger
from ctrader_fix_asyncio.broker import Broker

DEBUG = False

# INITIAL GLOBAL VARIABLE DECLARATION - used for the graphical user interface
icmarkets = None
ic_bid_label = None
ic_ask_label = None
ic_price_check_state = None
ic_trade_check_state = None
ic_increment_entry = None
ic_total_lots = None
ic_opened_positions = None
ic_opened_orders = None
ic_price_check_state = None
ic_trade_check_state = None
ic_increment_entry = None
ic_total_lots = None
ic_opened_positions = None
ic_opened_orders = None


def main(debug: bool) -> None:
    """Run the main function."""
    request_logger.info(
        f"Start __main__ for Whatsapp ReadMessages with sys.argv={sys.argv}"
    )
    # create an ic market instance of broker class and login to the 2 streams ICmarkets login credentials
    icmarkets = Broker(
        "icmarkets",
        "h35.p.ctrader.com",
        None,
        None,
        None,
        None,
        "demo.icmarkets.8739125",
        None,
        None,
        1,
        1,
        None,
        None,
        "8739125",
        "ghjd685j23",
        ic_bid_label,
        ic_ask_label,
        ic_price_check_state,
        ic_trade_check_state,
        [],
        ic_increment_entry,
        ic_total_lots,
        ic_opened_positions,
    )


if __name__ == "__main__":
    main(DEBUG)
