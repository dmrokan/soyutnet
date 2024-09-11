import sys
import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL
from soyutnet.observer import ComparativeObserver, Observer


def main(token_count=12):
    token_ids = [GENERIC_ID] * token_count

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

    o00 = ComparativeObserver(
        expected={2: [-1] + [1] * (len(token_ids) // 2 - 2)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o01 = ComparativeObserver(
        expected={2: [-1] + [1] * (len(token_ids) // 2 - 2)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o1 = ComparativeObserver(
        expected={2: [1] * (len(token_ids) // 2 - 1)},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    p00 = SpecialPlace("p00", producer=producer, observer=o00)
    p01 = SpecialPlace("p01", producer=producer, observer=o01)
    p1 = SpecialPlace("p1", consumer=consumer, observer=o1)
    t1 = Transition("t1")

    reg = PTRegistry()

    reg.register(p00)
    reg.register(p01)
    reg.register(p1)
    reg.register(t1)

    p00.connect(t1)
    p01.connect(t1)
    t1.connect(p1)

    asyncio.run(soyutnet.main(reg))


if __name__ == "__main__":
    main(int(sys.argv[1]))
