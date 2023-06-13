"""Module about assets."""

from typing import Tuple

assets_all = {
    "EURCZK": {"symbol_id": 1024, "symbol_num_digits": 3},
    "EURUSD": {"symbol_id": 1, "symbol_num_digits": 5},
    "NZDSGD": {"symbol_id": 1025, "symbol_num_digits": 4},
    "GBPUSD": {"symbol_id": 2, "symbol_num_digits": 5},
    "USDTHB": {"symbol_id": 1026, "symbol_num_digits": 3},
    "EURJPY": {"symbol_id": 3, "symbol_num_digits": 3},
    "USDJPY": {"symbol_id": 4, "symbol_num_digits": 3},
    "AUDUSD": {"symbol_id": 5, "symbol_num_digits": 5},
    "USDCHF": {"symbol_id": 6, "symbol_num_digits": 5},
    "GBPJPY": {"symbol_id": 7, "symbol_num_digits": 3},
    "USDCAD": {"symbol_id": 8, "symbol_num_digits": 5},
    "EURGBP": {"symbol_id": 9, "symbol_num_digits": 5},
    "EURCHF": {"symbol_id": 10, "symbol_num_digits": 5},
    "AUDJPY": {"symbol_id": 11, "symbol_num_digits": 3},
    "NZDUSD": {"symbol_id": 12, "symbol_num_digits": 5},
    "CHFJPY": {"symbol_id": 13, "symbol_num_digits": 3},
    "EURAUD": {"symbol_id": 14, "symbol_num_digits": 5},
    "CADJPY": {"symbol_id": 15, "symbol_num_digits": 3},
    "GBPAUD": {"symbol_id": 16, "symbol_num_digits": 5},
    "AUS200": {"symbol_id": 10000, "symbol_num_digits": 2},
    "EURCAD": {"symbol_id": 17, "symbol_num_digits": 5},
    "STOXX50": {"symbol_id": 10001, "symbol_num_digits": 2},
    "AUDCAD": {"symbol_id": 18, "symbol_num_digits": 5},
    "F40": {"symbol_id": 10002, "symbol_num_digits": 2},
    "GBPCAD": {"symbol_id": 19, "symbol_num_digits": 5},
    "DE30": {"symbol_id": 10003, "symbol_num_digits": 2},
    "AUDNZD": {"symbol_id": 20, "symbol_num_digits": 5},
    "HK50": {"symbol_id": 10004, "symbol_num_digits": 2},
    "IT40": {"symbol_id": 10005, "symbol_num_digits": 2},
    "NZDJPY": {"symbol_id": 21, "symbol_num_digits": 3},
    "JP225": {"symbol_id": 10006, "symbol_num_digits": 2},
    "USDNOK": {"symbol_id": 22, "symbol_num_digits": 5},
    "AUDCHF": {"symbol_id": 23, "symbol_num_digits": 5},
    "AEX": {"symbol_id": 10007, "symbol_num_digits": 2},
    "WIG20": {"symbol_id": 10008, "symbol_num_digits": 2},
    "USDMXN": {"symbol_id": 24, "symbol_num_digits": 5},
    "GBPNZD": {"symbol_id": 25, "symbol_num_digits": 5},
    "ES35": {"symbol_id": 10009, "symbol_num_digits": 2},
    "EURNZD": {"symbol_id": 26, "symbol_num_digits": 5},
    "SMI": {"symbol_id": 10010, "symbol_num_digits": 2},
    "CADCHF": {"symbol_id": 27, "symbol_num_digits": 5},
    "UK100": {"symbol_id": 10011, "symbol_num_digits": 2},
    "US2000": {"symbol_id": 10012, "symbol_num_digits": 2},
    "USDSGD": {"symbol_id": 28, "symbol_num_digits": 5},
    "US500": {"symbol_id": 10013, "symbol_num_digits": 2},
    "USDSEK": {"symbol_id": 29, "symbol_num_digits": 5},
    "USTEC": {"symbol_id": 10014, "symbol_num_digits": 2},
    "NZDCAD": {"symbol_id": 30, "symbol_num_digits": 5},
    "EURSEK": {"symbol_id": 31, "symbol_num_digits": 5},
    "US30": {"symbol_id": 10015, "symbol_num_digits": 2},
    "XPDUSD": {"symbol_id": 10016, "symbol_num_digits": 2},
    "GBPSGD": {"symbol_id": 32, "symbol_num_digits": 5},
    "XPTUSD": {"symbol_id": 10017, "symbol_num_digits": 2},
    "EURNOK": {"symbol_id": 33, "symbol_num_digits": 5},
    "EURHUF": {"symbol_id": 34, "symbol_num_digits": 3},
    "XBRUSD": {"symbol_id": 10018, "symbol_num_digits": 2},
    "USDPLN": {"symbol_id": 35, "symbol_num_digits": 5},
    "XTIUSD": {"symbol_id": 10019, "symbol_num_digits": 2},
    "XNGUSD": {"symbol_id": 10020, "symbol_num_digits": 3},
    "USDDKK": {"symbol_id": 36, "symbol_num_digits": 5},
    "GBPNOK": {"symbol_id": 37, "symbol_num_digits": 5},
    "BRENT": {"symbol_id": 10021, "symbol_num_digits": 2},
    "AUDDKK": {"symbol_id": 38, "symbol_num_digits": 5},
    "WTI": {"symbol_id": 10022, "symbol_num_digits": 2},
    "NZDCHF": {"symbol_id": 39, "symbol_num_digits": 5},
    "EURUSDt": {"symbol_id": 10023, "symbol_num_digits": 5},
    "GBPCHF": {"symbol_id": 40, "symbol_num_digits": 5},
    "DE30t": {"symbol_id": 10024, "symbol_num_digits": 1},
    "XAUUSD": {"symbol_id": 41, "symbol_num_digits": 2},
    "CHINA50": {"symbol_id": 10025, "symbol_num_digits": 2},
    "XAGUSD": {"symbol_id": 42, "symbol_num_digits": 3},
    "BTCUSD": {"symbol_id": 10026, "symbol_num_digits": 2},
    "XAUEUR": {"symbol_id": 43, "symbol_num_digits": 2},
    "DSHUSD": {"symbol_id": 10027, "symbol_num_digits": 2},
    "XAGEUR": {"symbol_id": 44, "symbol_num_digits": 3},
    "BCHUSD": {"symbol_id": 10028, "symbol_num_digits": 2},
    "ETHUSD": {"symbol_id": 10029, "symbol_num_digits": 2},
    "LTCUSD": {"symbol_id": 10030, "symbol_num_digits": 2},
    "GBPTRY": {"symbol_id": 10031, "symbol_num_digits": 5},
    "XAUAUD": {"symbol_id": 10032, "symbol_num_digits": 2},
    "CA60": {"symbol_id": 10033, "symbol_num_digits": 2},
    "TecDE30": {"symbol_id": 10034, "symbol_num_digits": 2},
    "MidDE60": {"symbol_id": 10035, "symbol_num_digits": 2},
    "NETH25": {"symbol_id": 10036, "symbol_num_digits": 2},
    "SWI20": {"symbol_id": 10037, "symbol_num_digits": 2},
    "SG30": {"symbol_id": 10038, "symbol_num_digits": 2},
    "CHINAH": {"symbol_id": 10039, "symbol_num_digits": 2},
    "NOR25": {"symbol_id": 10040, "symbol_num_digits": 2},
    "SA40": {"symbol_id": 10041, "symbol_num_digits": 2},
    "SE30": {"symbol_id": 10042, "symbol_num_digits": 2},
    "USCrude100": {"symbol_id": 10043, "symbol_num_digits": 2},
    "UKBrent100": {"symbol_id": 10044, "symbol_num_digits": 2},
    "MidDE50": {"symbol_id": 10045, "symbol_num_digits": 2},
    "DE40": {"symbol_id": 10046, "symbol_num_digits": 2},
    "XAUCHF": {"symbol_id": 10047, "symbol_num_digits": 2},
    "XAUGBP": {"symbol_id": 10048, "symbol_num_digits": 2},
    "XAUJPY": {"symbol_id": 10049, "symbol_num_digits": 0},
    "XAGAUD": {"symbol_id": 10050, "symbol_num_digits": 3},
    "IN50": {"symbol_id": 10051, "symbol_num_digits": 2},
    "USDHKD": {"symbol_id": 1000, "symbol_num_digits": 4},
    "AUDSGD": {"symbol_id": 1001, "symbol_num_digits": 5},
    "CHFSGD": {"symbol_id": 1002, "symbol_num_digits": 5},
    "EURDKK": {"symbol_id": 1003, "symbol_num_digits": 5},
    "EURHKD": {"symbol_id": 1004, "symbol_num_digits": 5},
    "EURPLN": {"symbol_id": 1005, "symbol_num_digits": 5},
    "EURSGD": {"symbol_id": 1006, "symbol_num_digits": 5},
    "EURTRY": {"symbol_id": 1007, "symbol_num_digits": 5},
    "EURZAR": {"symbol_id": 1008, "symbol_num_digits": 5},
    "GBPDKK": {"symbol_id": 1009, "symbol_num_digits": 5},
    "GBPSEK": {"symbol_id": 1010, "symbol_num_digits": 5},
    "NOKSEK": {"symbol_id": 1011, "symbol_num_digits": 5},
    "USDTRY": {"symbol_id": 1012, "symbol_num_digits": 5},
    "USDZAR": {"symbol_id": 1013, "symbol_num_digits": 5},
    "NOKJPY": {"symbol_id": 1014, "symbol_num_digits": 3},
    "SEKJPY": {"symbol_id": 1015, "symbol_num_digits": 3},
    "SGDJPY": {"symbol_id": 1016, "symbol_num_digits": 3},
    "USDHUF": {"symbol_id": 1017, "symbol_num_digits": 3},
    "USDCZK": {"symbol_id": 1018, "symbol_num_digits": 4},
    "USDRUB": {"symbol_id": 1019, "symbol_num_digits": 3},
    "USDCNH": {"symbol_id": 1020, "symbol_num_digits": 5},
    "GBPZAR": {"symbol_id": 1021, "symbol_num_digits": 4},
    "EURMXN": {"symbol_id": 1022, "symbol_num_digits": 4},
    "EURRUB": {"symbol_id": 1023, "symbol_num_digits": 3},
}

DICT_SYMBOL_ID_SYMBOL = {assets_all[symbol]["symbol_id"]: symbol for symbol in assets_all}
# sort by keys
DICT_SYMBOL_ID_SYMBOL = dict(sorted(DICT_SYMBOL_ID_SYMBOL.items()))


def get_info_quantity_to_trade(symbol: str) -> Tuple[float, float]:
    """Return the minimum and our allowed quantities to trade for a given asset."""
    if symbol in ["US30", "USTEC", "US500", "US2000", "DE40"]:
        # US indices: 1 lot = 1 unit
        min_quantity_to_trade = 1.0
        our_quantity_to_trade = 1.0
    elif symbol in ["BTCUSD", "ETHUSD"]:
        # crypto: 1 lot = 1 unit
        min_quantity_to_trade = 0.01
        our_quantity_to_trade = 0.05
    elif symbol in ["XAUUSD"]:
        # gold: 1 lot = 100 ounces
        min_quantity_to_trade = 1.0
        our_quantity_to_trade = 5.0
    elif symbol in ["XTIUSD"]:
        # oil: 1 lot = 100 barrels
        min_quantity_to_trade = 50.0
        our_quantity_to_trade = 50.0
    else:
        # forex: 1 lot = 100k units of the base currency
        # EURUSD = trade 100k euros; USDJPY = trade 100k USD
        min_quantity_to_trade = float(1_000)
        our_quantity_to_trade = float(10_000)

    return (min_quantity_to_trade, our_quantity_to_trade)
