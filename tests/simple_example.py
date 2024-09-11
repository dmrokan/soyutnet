import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL
from soyutnet.observer import ComparativeObserver, Observer


def main():
    token_ids = list(range(1, 7))

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            token = (GENERIC_LABEL, id)
            print("Produced:", token)
            return token
        except IndexError:
            pass

        return tuple()

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if token:
            print("Consumed:", token)
        else:
            print("No token in consumer")

    place_count = 2

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        if place_count == 0:
            soyutnet.terminate()

    o1 = ComparativeObserver(
        expected={2: [-1] + [1] * 4},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = ComparativeObserver(
        expected={2: [1] * 5},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    p1 = SpecialPlace("p1", producer=producer, observer=o1)
    p2 = SpecialPlace("p2", consumer=consumer, observer=o2)
    t1 = Transition("t1")

    reg = PTRegistry()

    reg.register(p1)
    reg.register(p2)
    reg.register(t1)

    p1.connect(t1).connect(p2)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")


if __name__ == "__main__":
    main()
