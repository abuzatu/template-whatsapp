"""Module to run FixAPI only with socket and asyncio, inspired from Hishal."""

# python
import asyncio
from asyncio.events import AbstractEventLoop
import time
import yaml

# our modules
from ctrader_fix_asyncio.broker import Broker

# our modules
from configs.assets import get_info_quantity_to_trade
from configs.settings import work_dir

# get one account from the config
CONFIG_FILE_NAME = f"{work_dir()}/src/configs/config_accounts.yaml"
ACCOUNT_NAME = (
    "Hishal"
    # "Vinay"
    # "PMT"
)
account_names = ["Hishal", "Vinay", "PMT"]

# Open the YAML file
with open(CONFIG_FILE_NAME, "r") as file:
    # Load the YAML content
    yaml_data = yaml.load(file, Loader=yaml.FullLoader)
credentials = [c for c in yaml_data["accounts"] if c["name"] == ACCOUNT_NAME][0]


class App:
    """App class for main gui event loop.

    Except we do have have the Window for now.
    """

    async def exec(self) -> None:
        """This runs the for loop."""
        window = Window(asyncio.get_event_loop())
        await window.show()


class Window:
    """Class Window. Though so far no window, but text-based."""

    def __init__(self, loop: AbstractEventLoop) -> None:
        """Init."""
        # the async event loop
        self.loop = loop
        # create the connection to several accounts
        self.accounts = {}
        for account_name in account_names:
            credentials = [c for c in yaml_data["accounts"] if c["name"] == account_name][
                0
            ]
            self.accounts[account_name] = Broker(
                credentials=credentials,
                price_sendersubid=None,
                trade_sendersubid=None,
                price_msgseqnum=1,
                trade_msgseqnum=1,
                bid=0.0,
                ask=0.0,
                positions=[],
                num_opened_positions=0,
                orders=[],
                num_opened_orders=0,
            )
            # for now we receive the prices for just one symbol
            self.accounts[account_name].set_asset(symbol="EURUSD")
        print("Demo FIX API Application - 2023")
        time.sleep(1)
        print("Create task for self.login()")
        self.loop.create_task(self.login())
        time.sleep(1)
        print("End init of Window()")

    async def login(self) -> None:
        """For each of the accounts login to price and trade streams.

        The prices will come back every time there is a change.
        TO DO: not clear yet how. subscribe to several assets at the same time.
        Or how can I stop a subscription to start later a new one with other assets?

        The requests for positions and orders are sent at every heartbeat,
        then the ansewrs can come right away.
        """
        if True:
            # login to the price streams for all brokers
            for account_name in self.accounts:
                asyncio.create_task(self.accounts[account_name].price_login())
        if True:
            # login to the trade streams for all brokers
            for account_name in self.accounts:
                asyncio.create_task(self.accounts[account_name].trade_login())
        await asyncio.sleep(0)

    async def show(self) -> None:
        """The main while loop that keeps repeating.

        Originally it was the show window when created in the event loop.

        But no window for now. So we just wait.
        """
        await asyncio.sleep(5)
        counter = 0
        while True:
            counter += 1
            # print("I am in show() - the for loop, refresh every 3 seconds.")
            print()
            print("************************************")
            print(f"******* COUNTER ={counter} ********")
            print("************************************")

            for account_name in self.accounts:
                # prices
                if True:
                    print(
                        f"ACCOUNT={account_name}, prices: "
                        f"asset={self.accounts[account_name].symbol}, "
                        f"bid={self.accounts[account_name].bid}, "
                        f"ask={self.accounts[account_name].ask}"
                    )
                # positions
                if True:
                    print(
                        f"ACCOUNT={account_name}, positions: "
                        f"num_opened_positions = "
                        f"{self.accounts[account_name].num_opened_positions}, "
                        f"len(positions) = {len(self.accounts[account_name].positions)}"
                    )
                    # print(f"positions = {self.accounts[account_name].positions}")
                    for position in self.accounts[account_name].positions:
                        print(f"position = {position}")
                # orders
                if True:
                    print(
                        f"ACCOUNT={account_name}, orders: "
                        f"num_opened_orders = "
                        f"{self.accounts[account_name].num_opened_orders}, "
                        f"len(orders) = {len(self.accounts[account_name].orders)}"
                    )
                    # print(f"positions = {self.accounts[account_name].positions}")
                    for order in self.accounts[account_name].orders:
                        print(f"order = {order}")

                if True and counter == 2:
                    await self.accounts[account_name].set_order_examples(
                        symbol="AUDUSD",
                        price_low=0.6700,
                        price_high=0.6800,
                        num_repeats=1,
                    )

                if True and counter == 3:
                    position_ids = await self.accounts[account_name].close_all_positions()
                    print(f"Closed all positions: position_ids={position_ids}")

                if True and counter == 4:
                    order_ids = await self.accounts[account_name].cancel_all_orders()
                    print(f"Closed all orders: order_ids={order_ids}")

                continue

                if True and counter == 2:
                    symbols = [
                        "XTIUSD",
                    ]
                    position_ids = await self.accounts[
                        account_name
                    ].close_all_positions_for_several_symbols(symbols)
                    print(
                        f"Closed all positions for symbols={symbols}: "
                        f"position_ids={position_ids}"
                    )

                if True and counter == 2:
                    symbol = "BTCUSD"
                    (
                        min_quantity_to_trade,
                        our_quantity_to_trade,
                    ) = get_info_quantity_to_trade(symbol)
                    # set TP for a given position buy position
                    await self.accounts[account_name].set_order(
                        symbol=symbol,
                        direction="sell",
                        order_type="limit",
                        quantity_to_trade=min_quantity_to_trade,
                        price=30000,
                        position_id="339874985",
                    )
                    # set SL for a given buy position
                    await self.accounts[account_name].set_order(
                        symbol=symbol,
                        direction="sell",
                        order_type="stop",
                        quantity_to_trade=min_quantity_to_trade,
                        price=24000,
                        position_id="339874985",
                    )

                if True and counter == 10:
                    # this will also close all orders associated with that position
                    await self.accounts[account_name].close_position(
                        position_id="339874985"
                    )

                if True and counter == 5:
                    symbol = "AUDUSD"
                    position_ids = await self.accounts[
                        account_name
                    ].close_all_positions_for_one_symbol(symbol)
                    print(
                        f"Closed positions for symbol={symbol}: "
                        f"position_ids={position_ids}"
                    )

                if True and counter == 6:
                    symbols = ["EURUSD", "EURAUD"]
                    position_ids = await self.accounts[
                        account_name
                    ].close_all_positions_for_several_symbols(symbols)
                    print(
                        f"Closed all positions for symbols={symbols}: "
                        f"position_ids={position_ids}"
                    )

                if True and counter == 6:
                    # close all orders for one position
                    order_ids = await self.accounts[
                        account_name
                    ].cancel_all_orders_for_one_position(
                        position_id="339826567",
                    )
                    print(
                        f"Closed all orders for position_id={339826567}, "
                        f"order_ids={order_ids}"
                    )

                if True and counter == 2:
                    await self.accounts[account_name].cancel_order(
                        order_id="543142033",
                    )

                if True and counter == 10:
                    order_ids = await self.accounts[
                        account_name
                    ].cancel_all_orders_for_one_symbol(
                        symbol="US500",
                    )
                    print(
                        f"Closed all orders for symbol={symbol}, "
                        f"order_ids={order_ids}"
                    )

                if True and counter == 12:
                    order_ids = await self.accounts[
                        account_name
                    ].cancel_all_orders_for_several_symbols(
                        symbols=["BTCUSD", "US30", "XAUUSD"]
                    )
                    print(
                        f"Closed all orders for symbols={symbols}, "
                        f"order_ids={order_ids}"
                    )

                if True and counter == 20:
                    order_ids = await self.accounts[account_name].cancel_all_orders()
                    print(f"Closed all orders: order_ids={order_ids}")

            # wait 5 seconds for the current counter
            await asyncio.sleep(3)

    async def buy(self) -> None:
        """Create a buy function here as an example, but not really needed."""
        for account_name in self.accounts:
            asyncio.create_task(
                self.accounts[account_name].set_order(
                    symbol="XAUUSD",
                    direction="buy",
                    order_type="limit",
                    quantity_to_trade=get_info_quantity_to_trade(symbol="XAUUSD")[0],
                    price=1900.0,
                    position_id=None,
                )
            )
            asyncio.create_task(
                self.accounts[account_name].async_set_order(
                    symbol="XAUUSD",
                    direction="buy",
                    order_type="stop",
                    quantity_to_trade=get_info_quantity_to_trade(symbol="XAUUSD")[1],
                    price=2000.0,
                    position_id=None,
                )
            )


def main() -> None:
    """Run the main function."""
    print("Start main")
    # runs the application
    asyncio.run(App().exec())


if __name__ == "__main__":
    main()
