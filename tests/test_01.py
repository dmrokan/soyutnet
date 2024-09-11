import pytest
import asyncio

import soyutnet
from soyutnet.token import (
    Token,
    TokenRegistry,
)
from soyutnet.pt_common import PTRegistry
from soyutnet.place import (
    Place,
    SpecialPlace,
)
from soyutnet.transition import (
    Transition,
)
from soyutnet.common import (
    GENERIC_LABEL,
    GENERIC_ID,
    INITIAL_ID,
    INVALID_ID,
)


@pytest.mark.asyncio
async def test_01():
    registry = TokenRegistry()
    token = Token()

    assert (INVALID_ID, None) == registry.get_first_entry(token.get_label())
    registry.register(token)
    assert token.get_id() == INITIAL_ID + 1
    assert token.get_label() == GENERIC_LABEL
    assert (token.get_id(), token) == registry.get_first_entry(token.get_label())

    assert registry.get_entry_count() == 1


@pytest.mark.asyncio
async def test_02():
    place = Place()

    assert place.get_id() == GENERIC_ID
    assert place.get_binding() is None


@pytest.mark.asyncio
async def test_03():
    transition = Transition()

    assert transition.get_id() == GENERIC_ID
    assert transition.get_binding() is None


def test_04():
    import simple_example as e

    e.main()


def test_05():
    import simple_example_different_weight as e

    for i in range(1, 15):
        for j in range(1, i + 1):
            try:
                e.main(i, j)
            except asyncio.exceptions.CancelledError:
                pass


def test_06():
    import simple_example_two_input_places as e

    for i in range(100, 10000, 1000):
        try:
            e.main(i)
        except asyncio.exceptions.CancelledError:
            pass


def test_07():
    import simple_example_two_input_places_but_different_weights as e

    MAX = 10
    for i in range(1, MAX + 1):
        for j in range(1, MAX + 1):
            for k in range(1, MAX + 1):
                e.main(w1=i, w2=j)


def test_08():
    from basic_models import co_begin

    for i in range(2, 100):
        try:
            co_begin(i)
        except asyncio.exceptions.CancelledError:
            pass


def test_09():
    from basic_models import co_end

    for i in range(2, 100):
        try:
            co_end(i)
        except asyncio.exceptions.CancelledError:
            pass


def test_10():
    from basic_models import sync_by_signal

    try:
        sync_by_signal()
    except asyncio.exceptions.CancelledError:
        pass
