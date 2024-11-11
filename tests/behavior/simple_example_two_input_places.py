import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL


def main(token_count=12):
    token_ids = [GENERIC_ID] * token_count

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

    o00 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, 1),)] * (len(token_ids) // 2 - 1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o01 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, 1),)] * (len(token_ids) // 2 - 1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o1 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, i),) for i in range(0, len(token_ids), 2)]},
        on_comparison_ends=on_comparison_ends,
        verbose=True,
    )

    p00 = net.SpecialPlace("p00", producer=producer, observer=o00)
    p01 = net.SpecialPlace("p01", producer=producer, observer=o01)
    p1 = net.SpecialPlace("p1", consumer=consumer, observer=o1)
    t1 = net.Transition("t1")

    reg = net.PTRegistry()

    reg.register(p00)
    reg.register(p01)
    reg.register(p1)
    reg.register(t1)

    p00.connect(t1)
    p01.connect(t1)
    t1.connect(p1, weight=2)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")


if __name__ == "__main__":
    main(int(sys.argv[1]))
