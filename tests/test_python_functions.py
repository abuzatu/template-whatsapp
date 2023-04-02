"""Module for tests."""


def test_sum() -> None:
    """Test sum."""
    assert sum([1, 2, 3]) == 6, "Should be 6"


def test_sum_tuple() -> None:
    """Test sum tuple."""
    assert sum([1, 2, 2]) == 5, "Should be 5"


if __name__ == "__main__":
    test_sum()
    test_sum_tuple()
    print("Everything passed")