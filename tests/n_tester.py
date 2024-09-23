import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL, TokenType


def n_tester(n=2):
    net = SoyutNet()

    consumed_count = n + 1

    async def consumer(place):
        nonlocal consumed_count
        token: TokenType = place.get_token(GENERIC_LABEL)
        if token:
            net.DEBUG("Consumed:", token)
            consumed_count -= 1
            if consumed_count == 0:
                soyutnet.terminate()

    o1 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, i),) for i in range(2 * n, n - 1, -1)]},
        verbose=True,
    )
    p1 = net.Place(
        "p1", initial_tokens={GENERIC_LABEL: [GENERIC_ID] * (2 * n)}, observer=o1
    )
    t1 = net.Transition()
    p2 = net.SpecialPlace("p2", consumer=consumer)

    reg = net.PTRegistry()
    reg.register(p1)
    reg.register(t1)
    reg.register(p2)

    p1.connect(t1, weight=n).connect(p2, weight=1)
    t1.connect(p1, weight=n - 1)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")
        pass

    gv = reg.generate_graph()
    return gv


if __name__ == "__main__":
    gv = n_tester(int(sys.argv[1]) + 1)
    with open("test.gv", "w") as fh:
        fh.write(gv)
