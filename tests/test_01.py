import pytest
import asyncio
import random

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import (
    GENERIC_LABEL,
    GENERIC_ID,
    INVALID_ID,
    INITIAL_ID,
    INVALID_LABEL,
)


@pytest.mark.asyncio
async def test_01():
    net = SoyutNet()
    registry = net.TokenRegistry()
    token1 = net.Token()
    token2 = net.Token()

    assert (INVALID_ID, None) == registry.get_first_entry(token1.get_label())
    registry.register(token1)
    registry.register(token2)
    assert token1.get_id() == INITIAL_ID + 1
    assert token1.get_label() == GENERIC_LABEL
    assert (token1.get_id(), token1) == registry.get_first_entry(token1.get_label())

    assert registry.get_entry_count() == 1
    assert registry.get_entry_count(INVALID_LABEL) == 0
    assert registry.pop_entry(GENERIC_LABEL, token1._id) == token1
    assert registry.pop_entry(INVALID_LABEL, random.randint(10, 1000)) == None
    assert registry.pop_entry(GENERIC_LABEL) == token2
    assert registry.pop_entry(INVALID_LABEL) == None


@pytest.mark.asyncio
async def test_02():
    net = SoyutNet()
    place = net.Place()

    assert place.get_id() == GENERIC_ID
    assert place.get_binding() is None


@pytest.mark.asyncio
async def test_03():
    net = SoyutNet()
    transition = net.Transition()

    assert transition.get_id() == GENERIC_ID
    assert transition.get_binding() is None


def test_04():
    import simple_example as e

    e.main()


def test_05():
    import simple_example_different_weight as e

    e.main_01(3, 2)


def test_06():
    import simple_example_two_input_places as e

    for i in range(100, 10000, 1000):
        e.main(i)


def test_07():
    import simple_example_two_input_places_but_different_weights as e

    e.main(w1=3, w2=2)


def test_08():
    from basic_models import co_begin

    for i in range(2, 100):
        co_begin(i)


def test_09():
    from basic_models import co_end

    for i in range(2, 100):
        co_end(i)


def test_10():
    from basic_models import sync_by_signal

    sync_by_signal()


def test_11():
    from n_tester import n_tester

    n_tester()


def test_12():
    import hashlib
    from readme_example import main

    records, graph = main()
    assert (
        hashlib.sha256(graph.encode("utf-8")).hexdigest()
        == "f66957886ed63ee512bbcfad0666501313fcd0e09f6b6a632b4def2b6675037e"
    )
    assert len(records) == 3
    assert records[0][0] == "p1"
    assert records[0][1][1:] == (((0, 1), (1, 2)), "t1")
    assert records[1][0] == "p1"
    assert records[1][1][1:] == (((0, 0), (1, 2)), "t1")
    assert records[2][0] == "p1"
    assert records[2][1][1:] == (((0, 0), (1, 1)), "t1")


def test_13():
    import hashlib
    from periodic_example import main

    for i in range(1, 100, 4):
        records = main(i)
        j = 0
        for rec in records:
            n = rec[0]
            assert (j % (i + 1) == 0 and n == "p1") or (j % (i + 1) != 0 and n == "p2")
            j += 1
