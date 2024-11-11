import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_LABEL, GENERIC_ID


def main_01(w1=1, w2=1):
    token_ids = [GENERIC_ID] * (w1 * w2 * 10)

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return [(GENERIC_LABEL, id)]
        except IndexError:
            pass

        return []

    async def consumer(place):
        return

    place_count = 3

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        if place_count == 0:
            soyutnet.terminate()

    net = SoyutNet()

    expected0 = {1: [((GENERIC_LABEL, i),) for i in [1, 2, 3, 1, 2, 3, 1, 2, 3]]}
    expected1 = {1: [((GENERIC_LABEL, i),) for i in [3, 4, 2, 3, 4, 2, 3, 4, 2]]}
    expected2 = {
        1: [((GENERIC_LABEL, i),) for i in [0, 0, 0, 0, 0, 2, 2, 4, 4, 6, 6, 8, 8, 10]]
    }

    o0 = net.ComparativeObserver(
        expected=expected0,
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o1 = net.ComparativeObserver(
        expected=expected1,
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = net.ComparativeObserver(
        expected=expected2,
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )

    p0 = net.SpecialPlace("p0", producer=producer, observer=o0)
    p1 = net.Place("p1", observer=o1)
    p2 = net.SpecialPlace("p2", consumer=consumer, observer=o2)
    t1 = net.Transition("t1")
    t2 = net.Transition("t2")

    reg = net.PTRegistry()

    reg.register(p0)
    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    reg.register(t2)

    p0.connect(t1, weight=w1).connect(p1, weight=w1).connect(t2, weight=w2).connect(
        p2, weight=w2
    )

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")


if __name__ == "__main__":
    main_01(int(sys.argv[1]), int(sys.argv[2]))
