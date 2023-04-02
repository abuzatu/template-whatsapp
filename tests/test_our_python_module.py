"""Hello world of unit test functions, exemplified for a sum.

# https://docs.python.org/3/library/unittest.html

https://realpython.com/python-testing/
"""

import unittest

import utils.sum


class TestSum(unittest.TestCase):
    """Testing the sum."""

    def test_sum_list(self) -> None:
        """Testing sum of elements in a list."""
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self) -> None:
        """Testing sum of elements in a tuple."""
        self.assertEqual(sum((1, 2, 3)), 6, "Should be 6")

    def test_my_sum(self) -> None:
        """Testing my_sum."""
        self.assertEqual(
            utils.sum.my_sum(2, 3),
            5,
            "Should be the value of 5",
        )

    def test_my_sum_three(self) -> None:
        """Testing my_sum_three."""
        self.assertEqual(
            utils.sum.my_sum_three(1, 5, 3),
            9,
            "Should be 9",
        )


if __name__ == "__main__":
    unittest.main()
