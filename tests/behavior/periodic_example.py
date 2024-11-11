import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL


def main(w=2, graph_filename=""):
    async def scheduled():
        await asyncio.sleep(0.005 * w)
        soyutnet.terminate()

    net = SoyutNet()

    reg = net.PTRegistry()
    o1 = net.Observer(verbose=True)
    p1 = net.Place("p1", initial_tokens={GENERIC_LABEL: [GENERIC_ID] * w}, observer=o1)
    o2 = net.Observer(verbose=True)
    p2 = net.Place("p2", initial_tokens={GENERIC_LABEL: [GENERIC_ID] * 0}, observer=o2)
    t1 = net.Transition("t1")
    t2 = net.Transition("t2")
    """Define places and transitions (PTs)"""

    p1.connect(t1, weight=w).connect(p2, weight=w).connect(t2).connect(p1)
    """Connect PTs"""

    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    reg.register(t2)
    """Save to a list of PTs"""

    soyutnet.run(reg, extra_routines=[scheduled()])
    print("Simulation is terminated.")

    records = reg.get_merged_records()
    for rec in records:
        net.print(rec)

    if graph_filename:
        with open(graph_filename, "w") as fh:
            fh.write(reg.generate_graph(label_names={GENERIC_LABEL: "@"}))

    return records


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "")
