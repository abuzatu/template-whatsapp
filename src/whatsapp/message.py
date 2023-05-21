"""Module for messages (author, date, text).

Even if we read again and again the past 10 messages, put only unique messages
to the list, and only for new ones take actions.

Sometimes messages come fast, and we may spend time looping over several groups,
so it is important to capture all previous messages (say up to 10),
and not just the latest one.
"""

import pandas as pd
from typing import Any


class Message:
    """Class for one message."""

    def __init__(
        self,
        contact: str,
        author: str,
        datetime: pd.Timestamp,
        actual_message: str,
        quoted_message: str,
    ) -> None:
        """Initialize."""
        self.contact = contact
        self.author = author
        self.datetime = datetime
        self.actual_message = actual_message
        self.quoted_message = quoted_message

    def __str__(self) -> str:
        """String representation."""
        return (
            f"actual_message='{self.actual_message}', "
            f"quoted_message='{self.quoted_message}', "
            f"datetime={self.datetime}, "
            f"author='{self.author}', "
            f"contact='{self.contact}'."
        )

    def __eq__(self, other: Any) -> bool:
        """Compare two messages to see if they are identical.

        Useful as we get always each few messages and we want to see
        if we have it already.
        """
        if not isinstance(other, Message):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            (self.contact == other.contact)
            and (self.author == other.author)
            and (self.datetime == other.datetime)
            and (self.actual_message == other.actual_message)
            and (self.quoted_message == other.quoted_message)
        )
