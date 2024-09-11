import sys
import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL
from soyutnet.observer import ComparativeObserver, Observer
from soyutnet.common import DEBUG


def main(w1=1, w2=1):
    token_ids = [GENERIC_ID] * (w1 * w2 * 10)

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return (GENERIC_LABEL, id)
        except IndexError:
            pass

        return tuple()

    async def consumer(place):
        return

    place_count = 3

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        if place_count == 0:
            soyutnet.terminate()

    expected1 = {2: [w1] * (len(token_ids) // w1 - 1)}
    expected2 = {2: [w2 * int(i % w1 == 0) for i in range(len(token_ids) - (w1 * w2))]}

    o0 = ComparativeObserver(
        expected={2: [-1] + [1] * (len(token_ids) - 2)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o1 = ComparativeObserver(
        expected=expected1,
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = ComparativeObserver(
        expected=expected2,
        on_comparison_ends=on_comparison_ends,
        verbose=True,
    )
    p0 = SpecialPlace("p0", producer=producer, observer=o0)
    p1 = Place("p1", observer=o1)
    p2 = SpecialPlace("p2", consumer=consumer, observer=o2)
    t1 = Transition("t1")
    t2 = Transition("t2")

    reg = PTRegistry()

    reg.register(p0)
    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    reg.register(t2)

    p0.connect(t1)
    t1.connect(p1)
    p1.connect(t2, weight=w1)
    t2.connect(p2, weight=w2)

    asyncio.run(soyutnet.main(reg))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
