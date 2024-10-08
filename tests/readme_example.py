import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL


def main():
    async def scheduled():
        await asyncio.sleep(1)
        soyutnet.terminate()

    net = SoyutNet()
    net.DEBUG_ENABLED = True

    LABEL = 1
    initial_tokens = {
        GENERIC_LABEL: [GENERIC_ID],
        LABEL: [1000, 990],
    }
    reg = net.PTRegistry()
    o1 = net.Observer(verbose=True)
    p1 = net.Place("p1", initial_tokens=initial_tokens, observer=o1)
    o2 = net.Observer(verbose=True)
    p2 = net.Place("p2", observer=o2)
    t1 = net.Transition("t1")
    """Define places and transitions (PTs)"""

    p1.connect(t1, labels=[GENERIC_LABEL, LABEL]).connect(
        p2, labels=[GENERIC_LABEL, LABEL]
    )
    """Connect PTs"""

    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    """Save to a list of PTs"""

    soyutnet.run(reg, extra_routines=[scheduled()])
    print("Simulation is terminated.")

    records = reg.get_merged_records()
    graph = reg.generate_graph(
        indent="  ", label_names={LABEL: "🤔", GENERIC_LABEL: "🤌"}
    )

    print("\nRecorded events:")
    {None: net.print(rec) for rec in records}
    print("\nNet graph:")
    print(graph, file=sys.stderr)

    return records, graph


if __name__ == "__main__":
    main()
