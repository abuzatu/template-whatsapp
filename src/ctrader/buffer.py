"""Module for Buffer."""


class Buffer:
    """Class Buffer."""

    def __init__(self) -> None:
        """Init."""
        self._buffer = bytearray()

    def write(self, data: bytes) -> None:
        """Write."""
        self._buffer.extend(data)

    def read(self, size: int) -> bytearray:
        """Read."""
        data = self._buffer[:size]
        self._buffer[:size] = b""
        return data

    def peek(self, size: int) -> bytearray:
        """Peek."""
        return self._buffer[:size]

    def count(self) -> int:
        """Count."""
        return len(self._buffer)

    def __len__(self) -> int:
        """Length."""
        return len(self._buffer)
