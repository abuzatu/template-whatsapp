"""Module to build the web driver via Chrome driver."""

import time

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from utils.logger import request_logger

from configs.settings import (
    CHROME_PROFILE_PATH,
)


class Driver:
    """Class Driver."""

    def __init__(self) -> None:
        """Initialize.

        Set the chrome web driver to read from Whatsapp via selenium.
        """
        # Set up Chrome options
        chrome_options = Options()
        # chrome_options.add_argument('--headless') # Commented out
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(CHROME_PROFILE_PATH)

        # create webdriver of type ChromeDriver
        request_logger.info("Start to create the web driver.")
        start = time.time()
        self.driver = webdriver.Remote(
            command_executor="http://standalone-chromium:4444/wd/hub",
            options=chrome_options,
        )
        end = time.time()
        duration_seconds = end - start
        duration_minutes = duration_seconds / 60.0
        request_logger.info(
            "Driver created. "
            f"duration_seconds={duration_seconds:.1f} seconds, "
            f"duration_minutes={duration_minutes:.1f} minutes."
        )
        self.driver.maximize_window()

    def fit(self) -> None:
        """Fit. Return the driver.."""
        return self.driver
