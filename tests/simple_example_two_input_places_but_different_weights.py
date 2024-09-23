import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL


def main(w1=1, w2=1):
    token_ids = [GENERIC_ID] * 35

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
        print(place_count)
        if place_count == 0:
            soyutnet.terminate()

    w3 = w1 + w2

    net = soyutnet.SoyutNet()

    o00 = net.Observer(verbose=False)
    o01 = net.Observer(verbose=False)
    o10 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, 3),)] * 5},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o11 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, i),) for i in range(3, 8)]},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = net.ComparativeObserver(
        expected={
            1: [
                ((GENERIC_LABEL, i),)
                for i in [5, 4, 3, 7, 6, 5, 9, 8, 7, 11, 10, 9, 13, 12, 11]
                + list(range(15, 1, -1))
            ]
        },
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o3 = net.Observer(verbose=False)

    p00 = net.SpecialPlace("p00", producer=producer, observer=o00)
    p01 = net.SpecialPlace("p01", producer=producer, observer=o01)
    p10 = net.Place("p10", observer=o10)
    p11 = net.Place("p11", observer=o11)
    p2 = net.Place("p2", observer=o2)
    p3 = net.SpecialPlace("p3", consumer=consumer, observer=o3)

    t00 = net.Transition("t00")
    t01 = net.Transition("t01")
    t1 = net.Transition("t1")
    t2 = net.Transition("t2")

    reg = net.PTRegistry()

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
        .connect(t2, weight=1)
        .connect(p3, weight=1)
    )

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")

    gv = reg.generate_graph()
    return gv


if __name__ == "__main__":
    gv = main(int(sys.argv[1]), int(sys.argv[2]))
    with open("test.gv", "w") as fh:
        fh.write(gv)
