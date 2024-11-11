PT connection syntax
====================

Starting from v0.4.0, SoyutNet supports a simpler syntax for connecting
places and transitions by overloading operators ``>>, <<, >, <``.

* :py:meth:`soyutnet.pt_common.PTCommon.__rshift__`
* :py:meth:`soyutnet.pt_common.PTCommon.__lshift__`
* :py:meth:`soyutnet.pt_common.PTCommon.__gt__`
* :py:meth:`soyutnet.pt_common.PTCommon.__lt__`

Graph format
------------

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_labeled.png
   :align: center

* Places are represented by circles with labels :math:`p_i`.
* Transitions are represented by boxes with labels :math:`t_i`.
* Arcs are arrows with labels in the form of ':math:`w ~ \{l_1, l_2, \dots \}`'.
    * :math:`w` is the weight of arc.
    * :math:`\{l_i\}` is the arc labels meaning that a particular arc
      accepts :ref:`tokens <token-def>` with a label in the set :math:`\{l_i\}`.
    * If arc has no label, then it has the default label ':math:`1 \{0\}`'.

Single branch examples
----------------------

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_01_a-connections-start
   :end-before: TestSingleBranch-test_01_a-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_01_a.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_01_b-connections-start
   :end-before: TestSingleBranch-test_01_b-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_01_b.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_02-connections-start
   :end-before: TestSingleBranch-test_02-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_02.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_03-connections-start
   :end-before: TestSingleBranch-test_03-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_03.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_04-connections-start
   :end-before: TestSingleBranch-test_04-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_04.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_05-connections-start
   :end-before: TestSingleBranch-test_05-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_05.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_06-connections-start
   :end-before: TestSingleBranch-test_06-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_06.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_07-connections-start
   :end-before: TestSingleBranch-test_07-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_07.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_08-connections-start
   :end-before: TestSingleBranch-test_08-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_08.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSingleBranch-test_09-connections-start
   :end-before: TestSingleBranch-test_09-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSingleBranch-test_09.png
   :align: center

Multiple branch examples
------------------------

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_01-connections-start
   :end-before: TestSplit-test_01-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_01.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_02-connections-start
   :end-before: TestSplit-test_02-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_02.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_03-connections-start
   :end-before: TestSplit-test_03-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_03.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_04-connections-start
   :end-before: TestSplit-test_04-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_04.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_05-connections-start
   :end-before: TestSplit-test_05-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_05.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_06-connections-start
   :end-before: TestSplit-test_06-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_06.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_07-connections-start
   :end-before: TestSplit-test_07-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_07.png
   :align: center

.. literalinclude:: ../../tests/pt_connection/test_A.py
   :language: python
   :start-after: TestSplit-test_08-connections-start
   :end-before: TestSplit-test_08-connections-end

.. figure:: ../../tests/pt_connection/artifacts/TestSplit-test_08.png
   :align: center
