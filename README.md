# SoyutNet

<img align="left" width="128" height="128" src="https://raw.githubusercontent.com/dmrokan/soyutnet/main/docs/source/_static/soyutnet_logo.png">

SoyutNet is a place/transition net (PT net, Petri net) simulator
that uses Python's asyncio task and synchronization utilities as
backend. (*Soyut means abstract in Turkish.*)

Its documentation can be found at [https://soyutnet.readthedocs.io](https://soyutnet.readthedocs.io)

## Building

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Installing

```bash
python3 -m venv venv
source venv/bin/activate
pip install soyutnet
```

## An example

This example simulates the PT net given in the diagram below.

![PT net example](https://raw.githubusercontent.com/dmrokan/soyutnet/main/docs/source/_static/images/first_example_T0.png "PT net example")

```python
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
```

outputs:

```
$ python tests/behavior/readme_example.py

loop(t1, 3): REC: O{(p1, 1)}: (112199.881220, ((0, 1, ), (1, 2, ), ), t1, )
loop(t1, 3): REC: O{(p1, 1)}: (112199.881402, ((0, 0, ), (1, 2, ), ), t1, )
loop(t1, 3): REC: O{(p1, 1)}: (112199.881550, ((0, 0, ), (1, 1, ), ), t1, )

Recorded events:
(p1, (112199.881220, ((0, 1, ), (1, 2, ), ), t1, ), )
(p1, (112199.881402, ((0, 0, ), (1, 2, ), ), t1, ), )
(p1, (112199.881550, ((0, 0, ), (1, 1, ), ), t1, ), )

Net graph:
digraph Net {
  subgraph cluster_0 {
    p1_0 [shape="circle",fontsize="20",style="filled",color="#000000",fillcolor="#dddddd",label="",xlabel="p1",height="1",width="1",penwidth=3];
    p2_0 [shape="circle",fontsize="20",style="filled",color="#000000",fillcolor="#dddddd",label="",xlabel="p2",height="1",width="1",penwidth=3];
    t1_0 [shape="box",fontsize="20",style="filled",color="#cccccc",fillcolor="#000000",label="",xlabel="t1",height="0.25",width="1.25",penwidth=3];
    t1_0 -> p2_0 [fontsize="20",label="{🤌,🤔}",minlen="2",penwidth="3"];
    p1_0 -> t1_0 [fontsize="20",label="{🤌,🤔}",minlen="2",penwidth="3"];
  }
  clusterrank=none;
}
```

**How to interpret events**

```
('p1', (188597.931257369, ((0, 1), (1, 2)), 't1'))

A list of place markings that show token counts for each label recorded just before a transition is fired:
[('<name of the place>', (<event timestamp in seconds>, ((<token label>, <token count>),), '<firing transition>')), ...]
```

**How to generate the graph**

```bash
sudo apt install graphviz # Which provides 'dot'
python tests/behavior/readme_example.py 2>&1 > /dev/null | dot -Tpng > readme_example.png
```

Outputs:

![PT net graph](https://raw.githubusercontent.com/dmrokan/soyutnet/main/docs/source/_static/images/first_example.png "PT net graph")

## [Credits](https://github.com/dmrokan/soyutnet/blob/main/docs/source/credits.rst)
