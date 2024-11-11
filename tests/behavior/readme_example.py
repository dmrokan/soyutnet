import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL


def main():
    async def scheduled():
        await asyncio.sleep(1)
        soyutnet.terminate()

    with SoyutNet(extra_routines=[scheduled()]) as net:
        net.DEBUG_ENABLED = True

        LABEL = 1
        initial_tokens = {
            GENERIC_LABEL: [GENERIC_ID],
            LABEL: [1000, 990],
        }
        o1 = net.Observer(verbose=True)
        p1 = net.Place("p1", initial_tokens=initial_tokens, observer=o1)
        o2 = net.Observer(verbose=True)
        p2 = net.Place("p2", observer=o2)
        t1 = net.Transition("t1")
        """Define places and transitions (PTs)"""

        _ = net.Arc(labels=(GENERIC_LABEL, LABEL))
        p1 >> _ >> t1 >> _ >> p2
        """Connect PTs"""

    records = net.registry.get_merged_records()
    graph = net.registry.generate_graph(
        indent="  ", label_names={LABEL: "🤔", GENERIC_LABEL: "🤌"}
    )

    print("\nRecorded events:")
    {net.print(rec) for rec in records}
    print("\nNet graph:")
    print(graph, file=sys.stderr)

    return records, graph


if __name__ == "__main__":
    main()
