import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL
from soyutnet.observer import ComparativeObserver, Observer


def main():
    token_ids = [GENERIC_ID] * 6

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return (GENERIC_LABEL, id)
        except IndexError:
            pass

        return tuple()

    async def consumer(place):
        return

    place_count = 2

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        if place_count == 0:
            soyutnet.terminate()

    o0 = ComparativeObserver(
        to_what={2: [2] + [1] * 4},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o1 = ComparativeObserver(
        to_what={2: [1] * 5},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    p0 = SpecialPlace("p0", producer=producer, observer=o0)
    p1 = SpecialPlace("p1", consumer=consumer, observer=o1)
    t1 = Transition("t1")

    reg = PTRegistry()

    reg.register(p0)
    reg.register(p1)
    reg.register(t1)

    p0.connect(t1)
    t1.connect(p1)

    asyncio.run(soyutnet.main(reg))


if __name__ == "__main__":
    main()
