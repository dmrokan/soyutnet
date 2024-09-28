Examples
========

Producer/consumer
-----------------

This example implements the simplest producer/consumer network. One end produces
tokens which enables the transition that transfers the token to the consumer. Both producer
and consumer are instances of :py:class:`soyutnet.place.SpecialPlace` class.

.. figure:: _static/images/producer_consumer_example.png
   :align: center
   :alt: Producer/consumer example

   Producer/consumer example

It is implemented by the code below which can be found at
`SoyutNet repo <https://github.com/dmrokan/soyutnet/blob/main/tests/simple_example.py>`__.

.. literalinclude:: ../../tests/simple_example.py
   :language: python
   :lines: 8-28
   :lineno-start: 8

The main function starts by defining token IDs of produced token. The producer
function is called by :math:`p_1` and the consumer is called by :math:`p_2`.

.. literalinclude:: ../../tests/simple_example.py
   :language: python
   :lines: 29-52
   :lineno-start: 29

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

.. literalinclude:: ../../tests/simple_example.py
   :language: python
   :lines: 53-63
   :lineno-start: 53

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
--------

This example implements an *n-tester* transition which is enabled when input place
has :math:`n` or more tokens.

.. figure:: _static/images/n_tester_example.png
   :align: center
   :alt: n-tester example

   n-tester example

It is implemented by the code below which can be found at
`SoyutNet repo <https://github.com/dmrokan/soyutnet/blob/main/tests/n_tester.py>`__.

.. literalinclude:: ../../tests/n_tester.py
   :language: python

**Usage**

.. code:: bash

    $ python3 tests/n_tester.py 9
    $ dot -Tpng test.gv > n_tester_example.png # Generate image from graphviz dot file


Periodic
--------

This example implements two transitions that fires at adjustable periods.

.. figure:: _static/images/periodic_example.png
   :align: center
   :alt: n-tester example

   Periodic example

It is implemented by the code below which can be found at
`SoyutNet repo <https://github.com/dmrokan/soyutnet/blob/main/tests/periodic_example.py>`__.

.. literalinclude:: ../../tests/periodic_example.py
   :language: python

**Usage**

It can be seen that ``t2`` fires more frequently than ``t1``
which can be adjusted by the second argument of Python script.

.. code:: bash

    $ python3 tests/periodic_example.py 2
    ('p1', (191030.211397, ((0, 2),), 't1'))
    ('p2', (191030.211567, ((0, 2),), 't2'))
    ('p2', (191030.211661, ((0, 1),), 't2'))
    ('p1', (191030.211747, ((0, 2),), 't1'))
    ('p2', (191030.211865, ((0, 2),), 't2'))
    ('p2', (191030.211957, ((0, 1),), 't2'))
    ('p1', (191030.212038, ((0, 2),), 't1'))
    ('p2', (191030.212158, ((0, 2),), 't2'))
    ('p2', (191030.212239, ((0, 1),), 't2'))
    ('p1', (191030.212318, ((0, 2),), 't1'))
    ('p2', (191030.212428, ((0, 2),), 't2'))

    $ python3 tests/periodic_example.py 3 test.gv
    ('p1', (190774.824447, ((0, 3),), 't1'))
    ('p2', (190774.824606, ((0, 3),), 't2'))
    ('p2', (190774.824707, ((0, 2),), 't2'))
    ('p2', (190774.824793, ((0, 1),), 't2'))
    ('p1', (190774.824881, ((0, 3),), 't1'))
    ('p2', (190774.825015, ((0, 3),), 't2'))
    ('p2', (190774.825109, ((0, 2),), 't2'))
    ('p2', (190774.825191, ((0, 1),), 't2'))
    ('p1', (190774.825274, ((0, 3),), 't1'))
    ('p2', (190774.825398, ((0, 3),), 't2'))
    ('p2', (190774.825487, ((0, 2),), 't2'))
    ('p2', (190774.825568, ((0, 1),), 't2'))
    ('p1', (190774.825649, ((0, 3),), 't1'))
    ('p2', (190774.825774, ((0, 3),), 't2'))

    $ dot -Tpng test.gv > periodic_example.png
