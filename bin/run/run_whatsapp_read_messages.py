"""Run to send whatsapp messages with or without attachment to several contacts."""

# python
import asyncio
import sys

# our modules
from utils.logger import request_logger
from cli.cli_read_messages import CLI
from whatsapp.read_messages import ReadMessages

DEBUG = False


class App:
    """App class that runs async.

    Except we do have have the Window for now.
    """

    async def exec(self, debug: bool) -> None:
        """This runs the for loop."""
        request_logger.info(
            f"Start App.exec() for Whatsapp ReadMessages async with sys.argv={sys.argv}"
        )
        print(f"debug={debug}")
        cli = CLI(sys.argv)
        # print(cli)
        rm = ReadMessages(asyncio.get_event_loop())
        if debug:
            # set by hand
            rm.set_inputs_manually(
                contacts=["+44 7309 966580"],
            )
        else:
            # set from CLI
            rm.set_inputs_from_cli(cli)
        print(rm)
        await rm.set_driver()

        await rm.fit()
        # await rm.quit_driver()
        # await rm.show()


def main(debug: bool) -> None:
    """Run the main function."""
    print("Start main")
    # runs the application
    asyncio.run(App().exec(debug))


if __name__ == "__main__":
    main(DEBUG)
