from unittest.mock import Mock

import pytest

from shop.cart import Cart


def test_empty_cart_count() -> None:
    cart = Cart()
    assert cart.items_count() == 0


def test_add_one_item() -> None:
    cart = Cart()
    cart.add("book", price=200.0)
    assert cart.items_count() == 1


def test_add_multiple_items(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_add_negative_price_raises() -> None:
    cart = Cart()
    with pytest.raises(ValueError, match="price"):
        cart.add("book", price=-1.0)


def test_add_zero_quantity_raises() -> None:
    cart = Cart()
    with pytest.raises(ValueError, match="qty"):
        cart.add("book", price=100.0, qty=0)


def test_remove_existing_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("book")
    assert cart_with_items.items_count() == 4


def test_remove_nonexistent_item_raises() -> None:
    cart = Cart()
    with pytest.raises(KeyError):
        cart.remove("unknown")


def test_empty_cart_total() -> None:
    cart = Cart()
    assert cart.total() == 0.0


def test_cart_total(cart_with_items: Cart) -> None:
    assert cart_with_items.total() == 460.0


def test_cart_total_with_discount(cart_with_items: Cart) -> None:
    assert cart_with_items.total(discount_percent=10) == 414.0


@pytest.mark.parametrize(
    "discount, expected",
    [
        (0, 460.0),
        (10, 414.0),
        (25, 345.0),
        (50, 230.0),
        (100, 0.0),
    ],
)
def test_total_parametrized(cart_with_items: Cart, discount: float, expected: float) -> None:
    assert cart_with_items.total(discount_percent=discount) == expected


@pytest.mark.parametrize("discount", [-10, -1, 101, 150])
def test_invalid_discount_raises(cart_with_items: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart_with_items.total(discount_percent=discount)


def test_total_in_with_mock(cart_with_items: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    result = cart_with_items.total_in("USD", rates)

    assert result == 11.5
    rates.get_rate.assert_called_once_with("USD")


@pytest.mark.parametrize("rate", [0.0, -10.0])
def test_total_in_invalid_rate_raises(cart_with_items: Cart, rate: float) -> None:
    rates = Mock()
    rates.get_rate.return_value = rate

    with pytest.raises(ValueError, match="rate"):
        cart_with_items.total_in("USD", rates)


def test_add_same_item_different_price() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=1)
    cart.add("book", price=300.0, qty=2)

    assert cart.items_count() == 3
    assert cart.total() == 600.0


def test_most_expensive_empty_cart() -> None:
    cart = Cart()
    assert cart.most_expensive() is None


def test_most_expensive_with_items(cart_with_items: Cart) -> None:
    item = cart_with_items.most_expensive()

    assert item is not None
    assert item.name == "book"
    assert item.price == 200.0
