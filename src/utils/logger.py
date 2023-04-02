"""Module for building a logger.

The custom logger allows to add extra info when available,
when you run for particular use cases to be easier to debug.
"""

import coloredlogs
import functools
import logging
import numpy as np
import psutil
import time
from typing import Any, Callable, Optional, Tuple, Union

# our other modules
import configs.settings as settings


class RequestLogger(logging.LoggerAdapter):
    """Custom logging adapter to add name when available."""

    request_id_ = None
    option_name_ = None

    def set_kwargs(self, request_id: str, option_name: str) -> None:
        """Set request_id and name for all logs for this request."""
        self.request_id_ = request_id
        self.option_name_ = option_name

    @property
    def request_id(cls) -> Optional[str]:
        """Get current request ID."""
        return cls.request_id_

    @property
    def option_name(cls) -> Optional[str]:
        """Get current city name."""
        return cls.option_name_

    def process(self, msg: Any, kwargs: Any) -> Tuple[str, Any]:
        """Add request_id, name and code context to logs."""
        if isinstance(msg, dict):
            pass
        # convert str message to dict
        elif isinstance(msg, str):
            msg = {
                "message": msg,
            }
        else:
            raise TypeError("Logging message must be either str or dict.")

        # add request_id and asset_name to every log message
        if self.request_id is not None:
            msg["request_id"] = self.request_id
        if self.name is not None:
            msg["option_name"] = self.option_name

        # parse message to have city_name
        # at the beginning of every log message
        msg = "[%s] %s" % (self.option_name, msg)
        return msg, kwargs


logger = logging.getLogger(__name__)
coloredlogs.install(
    level=settings.LOGGING_LEVEL,
    logger=logger,
    fmt="%(asctime)s %(name)s [%(process)d] %(levelname)s %(message)s",
)
request_logger = RequestLogger(logger, dict())


def time_and_log(
    add_func_args: Union[str, list] = [],
    level: str = settings.LOGGING_LEVEL,
) -> Callable:
    """Decorate any function to time and log start and end.

    Including also the RAM memory usage.
    """

    def _get_args_logged(kwargs: Any, add_func_args: Union[str, list]) -> dict:
        if add_func_args == "all":
            args_logged = kwargs
        elif add_func_args == []:
            args_logged = "removed"
        else:
            args_logged = {kw: val for kw, val in kwargs.items() if kw in add_func_args}
        return args_logged

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            logging_method = getattr(request_logger, level.lower())

            try:
                # process started
                ram_usage_before = psutil.virtual_memory().percent
                logging_method(
                    {
                        "process": func.__qualname__,
                        "message": "Started.",
                        "current_ram_usage": ram_usage_before,
                        "args": _get_args_logged(kwargs, add_func_args),
                    }
                )
                start_time = time.time()
                result = func(*args, **kwargs)

                # process finished
                ram_usage_after = psutil.virtual_memory().percent
                logging_method(
                    {
                        "process": func.__qualname__,
                        "message": "Success.",
                        "elapsed_seconds": np.round(time.time() - start_time, 4),
                        "current_ram_usage": ram_usage_after,
                    }
                )
                return result

            # process error
            except Exception as e:
                request_logger.exception(
                    {"process": func.__qualname__, "error_msg": str(e)}
                )

                raise e

        return wrapper

    return decorator
