import asyncio
from pathlib import Path

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_LABEL


def main():
    token_ids = list(range(1, 7))

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            token = (GENERIC_LABEL, id)
            print("Produced:", token)
            return [token]
        except IndexError:
            pass

        return []

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

    net = SoyutNet()
    net.DEBUG_ENABLED = True
    net.VERBOSE_ENABLED = True
    net.ERROR(
        [
            {
                0: "ABCD",
                1: [
                    1,
                    2,
                    3,
                ],
            },
            (0, "ABCD", [1, 3, 3.0, b"ABCD"]),
        ]
    )
    log_file = Path(__file__).resolve().parent / "log.tmp"
    log_filename = str(log_file)
    net.LOG_FILE = log_filename
    assert net.LOG_FILE == log_filename
    net.SLOW_MOTION = True
    net.LOOP_DELAY = 0
    net.ERROR(
        [
            {
                0: "ABCD",
                1: [
                    1,
                    2,
                    3,
                ],
            },
            (0, "ABCD", [1, 3, 3.0, b"ABCD"]),
            tuple(),
            list(),
            dict(),
        ]
    )

    assert net.VERBOSE_ENABLED

    o1 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, 1),)] * 5},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    o2 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, i),) for i in range(0, 6)]},
        on_comparison_ends=on_comparison_ends,
        verbose=False,
    )
    p1 = net.SpecialPlace("p1", producer=producer, observer=o1)
    p2 = net.SpecialPlace("p2", consumer=consumer, observer=o2)
    t1 = net.Transition("t1")

    reg = net.PTRegistry()

    reg.register(p1)
    reg.register(p2)
    reg.register(t1)

    p1.connect(t1).connect(p2)

    soyutnet.run(reg)
    print("Simulation is terminated.")

    log_file.unlink()

    records = reg.get_merged_records()
    for r in records:
        print(r)

    vg = reg.generate_graph()
    return vg


if __name__ == "__main__":
    vg = main()
    with open("test.dot", "w") as fh:
        fh.write(vg)
