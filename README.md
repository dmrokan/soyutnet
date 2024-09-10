# SoyutNet

<img align="left" width="128" height="128" src="https://raw.githubusercontent.com/dmrokan/soyutnet/main/docs/source/_static/soyutnet_logo.png">

SoyutNet is a place/transition net (PT net, Petri net) simulator
that uses Python's asyncio task and synchronization utilities as
its backend. (*Soyut means abstract in Turkish.*)

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
import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.place import Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_LABEL, GENERIC_ID

def main():
    p1 = Place("p1", initial_tokens={ GENERIC_LABEL: [GENERIC_ID] })
    p2 = Place("p2")
    t1 = Transition("t1")
    """Define places and transitions (PTs)"""

    p1.connect(t1).connect(p2)
    """Create connections"""

    reg = PTRegistry()
    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    """Save to a list of PTs"""

    asyncio.run(soyutnet.main(reg))
    """Run the simulation"""

if __name__ == "__main__":
    main()
```

## [Credits](https://github.com/dmrokan/soyutnet/blob/main/docs/source/credits.rst)
