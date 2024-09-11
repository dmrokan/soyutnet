import sys
import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL
from soyutnet.observer import ComparativeObserver, Observer


def main(w1=1, w2=1):
    token_ids = [GENERIC_ID] * (10 * (w1 + w2))

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return (GENERIC_LABEL, id)
        except IndexError:
            pass

        return tuple()

    async def consumer(place):
        return

    place_count = 4

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        print(place_count)
        if place_count == 0:
            soyutnet.terminate()

    w3 = w1 + w2
    c1 = w1 + w2

    o00 = ComparativeObserver(
        expected={2: [-1] + [1] * (len(token_ids) // c1 - c1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o01 = ComparativeObserver(
        expected={2: [-1] + [1] * (len(token_ids) // c1 - c1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o10 = ComparativeObserver(
        expected={2: [-1] + [w1] * (len(token_ids) // c1 - c1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o11 = ComparativeObserver(
        expected={2: [-1] + [w2] * (len(token_ids) // c1 - c1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = Observer(verbose=False)
    o3 = Observer(verbose=False)

    p00 = SpecialPlace("p00", producer=producer, observer=o00)
    p01 = SpecialPlace("p01", producer=producer, observer=o01)
    p10 = Place("p10", observer=o10)
    p11 = Place("p11", observer=o11)
    p2 = Place("p2", observer=o2)
    p3 = SpecialPlace("p3", consumer=consumer, observer=o3)

    t00 = Transition("t00")
    t01 = Transition("t01")
    t1 = Transition("t1")
    t2 = Transition("t2")

    reg = PTRegistry()

    reg.register(p00)
    reg.register(p01)
    reg.register(p10)
    reg.register(p11)
    reg.register(p2)
    reg.register(p3)

    reg.register(t00)
    reg.register(t01)
    reg.register(t1)
    reg.register(t2)

    (
        (
            p00.connect(t00).connect(p10).connect(t1, weight=w1),
            p01.connect(t01).connect(p11).connect(t1, weight=w2),
        )[0]
        .connect(p2, weight=w3)
        .connect(t2, weight=w3)
        .connect(p3, weight=w3)
    )

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
