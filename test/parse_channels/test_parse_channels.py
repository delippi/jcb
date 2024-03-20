# --------------------------------------------------------------------------------------------------


from jcb import parse_channels, parse_channels_set
import pytest


# --------------------------------------------------------------------------------------------------


def test_parse_single_number():
    """Test parsing a single number."""
    assert parse_channels("10") == [10]


def test_parse_single_number_int():
    """Test parsing a single number."""
    assert parse_channels(10) == [10]


def test_parse_range():
    """Test parsing a range of numbers."""
    assert parse_channels("1-3") == [1, 2, 3]


def test_parse_mixed_input():
    """Test parsing a mixed input with both single numbers and ranges."""
    assert parse_channels("1,2,4-6") == [1, 2, 4, 5, 6]


def test_parse_input_with_spaces():
    """Test parsing input with spaces around commas and dashes."""
    assert parse_channels("1 , 2 , 3-5") == [1, 2, 3, 4, 5]


def test_parse_list_of_numbers():
    """Test parsing when the input is already a list of numbers."""
    assert parse_channels([1, 2, 3]) == [1, 2, 3]


def test_parse_list_of_strings():
    """Test parsing when the input is a list of strings."""
    assert parse_channels(["1", "2", "3"]) == [1, 2, 3]


def test_parse_empty_string():
    """Test parsing an empty string."""
    assert parse_channels("") == []


def test_parse_empty_list():
    """Test parsing an empty list."""
    assert parse_channels([]) == []


def test_parse_invalid_input():
    """Test handling of invalid input."""
    with pytest.raises(ValueError):
        parse_channels("invalid")


def test_parse_as_set():
    """Test parsing a single number as a set."""
    assert parse_channels_set("10") == {10}


# --------------------------------------------------------------------------------------------------


# Main entry point
if __name__ == "__main__":
    pytest.main()


# --------------------------------------------------------------------------------------------------
