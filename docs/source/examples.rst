Producer/consumer
=================

This example implements the simplest producer/consumer network. One end produces
tokens which enables the transition that transfers the token to the consumer. Both producer
and consumer are instances of :py:class:`soyutnet.place.SpecialPlace` class.

.. figure:: _static/images/producer_consumer_example.png
   :align: center
   :alt: Producer/consumer example

   Producer/consumer example

It is implemented by the code below which can be found at
`SoyutNet repo <https://github.com/dmrokan/soyutnet/blob/main/tests/simple_example.py>`__.

.. code:: python

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



The main function starts by defining token IDs of produced token. The producer
function is called by :math:`p_1` and the consumer is called by :math:`p_2`.

.. code:: python

    place_count = 2

    def on_comparison_ends(observer):
        nonlocal place_count
        place_count -= 1
        if place_count == 0:
            soyutnet.terminate()

    net = SoyutNet()

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


SoyutNet implements observers (:py:class:`soyutnet.observer.Observer`) for
keeping the record of PT net markings before each firing of a transition.

Currently, observer records has three columns, the time of firing, label and number of
tokens with the label (:py:attr:`soyutnet.observer.ObserverRecordType`).

``ComparativeObserver`` (:py:class:`soyutnet.observer.ComparativeObserver`) is used
for test purposes. It accepts two additional arguments

* ``expected``: A dictionary of token counts with the structure below

  .. code:: python

     expected = {
         record_column_index: [ recorded_value_1, recorded_value_2, ... ],
     }

* ``on_comparison_ends``: It is called after all entries in ``expected`` is compared.
  In the example above, ``on_comparison_end`` is used to termiate the simulation
  after the test is completed.

The token count in :math:`p_1` is observed before each firing of :math:`t_1`
and compared to the list. If a value does not match, it raises a ``RuntimeError``.

.. code:: python

    reg = net.PTRegistry()

    reg.register(p1)
    reg.register(p2)
    reg.register(t1)

    p1.connect(t1).connect(p2)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        print("Simulation is terminated.")


:math:`p_1`'s output is connected to :math:`t_1` and :math:`t_1`'s output is
connected to :math:`p_2`.

The registry keeps a list of places and transitions and it is provided to the
:py:func:`soyutnet.main` function which starts asyncio task loops of PTs.

.. code::

   $ python tests/simple_example.py
   Produced: (0, 1)
   No token in consumer
   Produced: (0, 2)
   Consumed: (0, 1)
   Produced: (0, 3)
   Consumed: (0, 2)
   Produced: (0, 4)
   Consumed: (0, 3)
   Produced: (0, 5)
   Consumed: (0, 4)
   Produced: (0, 6)
   Consumed: (0, 5)
   Consumed: (0, 6)
   Simulation is terminated.


n-tester
========

This example implements an *n-tester* transition which is enabled when input place
has :math:`n` or more tokens.

.. figure:: _static/images/n_tester_example.png
   :align: center
   :alt: n-tester example

   n-tester example

It is implemented by the code below which can be found at
`SoyutNet repo <https://github.com/dmrokan/soyutnet/blob/main/tests/n_tester.py>`__.

.. code:: python

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

        # Generate graphviz dot file.
        gv = reg.generate_graph()
        return gv

    if __name__ == "__main__":
        gv = n_tester(int(sys.argv[1]) + 1)
        with open("test.gv", "w") as fh:
            fh.write(gv)



**Usage**

.. code:: bash

    $ python3 tests/n_tester.py 9
    $ dot -Tpng test.gv > n_tester_example.png # Generate image from graphviz dot file
