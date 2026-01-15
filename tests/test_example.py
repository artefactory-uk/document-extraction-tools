from your_module.adder import add


def test_example() -> None:
    """A simple test to check CI functionality."""
    assert add(1, 1) == 2
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
