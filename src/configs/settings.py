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
