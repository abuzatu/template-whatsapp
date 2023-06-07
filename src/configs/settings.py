"""Configuration file with settings."""

import os
from pathlib import Path
from typing import List

# for API
TITLE = "An API title"
DESCRIPTION = "An API description."

WORK_DIR = os.getenv("WORKDIR", "")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Default value is empty so we can force it to "test" in the unit tests.
STAGE = os.getenv("STAGE", "")
GIT_COMMIT_HASH = os.getenv("GIT_COMMIT_HASH", "")

""" Connection to other services"""
INPUT_SERVICE_URL = os.getenv("INPUT_SERVICE_URL", default="")
INPUT_SERVICE_API_KEY = os.getenv("INPUT_SERVICE_API_KEY", default="")

DEBUG = os.getenv("DEBUG", False)
TIMEZONE = os.getenv("TIMEZONE", default="UTC")

""" Getters """


def git_commit_hash() -> str:
    """Return git commit hash for alerts."""
    return GIT_COMMIT_HASH


def stage() -> str:
    """Return environment value."""
    return STAGE


def api_keys() -> List[str]:
    """Return list of valid API keys."""
    return [v for k, v in os.environ.items() if k.startswith("API_KEY")]


""" Environment getters """


def is_production() -> bool:
    """Check if production environment."""
    return STAGE == "production"


def is_staging() -> bool:
    """Check if staging environment."""
    return STAGE == "staging"


def is_test() -> bool:
    """Check if test environment."""
    return STAGE == "test"


def is_development() -> bool:
    """Check if test environment."""
    return STAGE == "development"


""" Paths """


def work_dir() -> Path:
    """Get working dir."""
    if WORK_DIR == "":
        return Path(__file__).parent.parent
    else:
        return Path(WORK_DIR)


""" Web driver for Whatsapp """

# used when running from local Docker
# currently we run from the standalone chromium, so it will not be used
EXECUTABLE_PATH = "/usr/local/bin/chromedriver"

# to avoid to scan the Whatsapp query for every script
# we set the chrome profile path to a particular folder
# that will be used every time
# remove Default from below and replace with our new folder called "Whatsapp"
# MacOS: /Users/abuzatu/Library/Application Support/Google/Chrome/Default
# Linux: home/abuzatu/.config/google-chrome/default
CHROME_PROFILE_PATH = (
    "user-data-dir="
    # when running locally on MacOS:
    # "/Users/abuzatu/Library/Application Support/Google/Chrome/Whatsapp"
    # when running in one Docker for Intel processor
    # without standalone chrome image, but where chromedriver installed locally
    # "$HOME/.config/google-chrome/Whatsapp"
    # when running using the standalone chrome image
    # we create by hand this folder there
    "/home/seluser/.config/chromium/google-chrome/Whatsapp"
)

WAIT_FOR_QR_CODE_SCAN = 100  # seconds

WAIT_FOR_SEARCH_BOX = 100  # seconds

WAIT_AFTER_EACH_CONTACT = 0.1  # seconds

# skip the first 2 rounds as you start, as it refers to previous messages
NUM_FIRST_COUNTERS_TO_SKIP = 2  # number

# read last how many messages
NUM_LATEST_MESSAGES_TO_READ = 5

SAVE_SCREENSHOT = False
SAVE_HTML = False

FILE_ORDERS_LOG = "./output/orders/orders_01.log"
