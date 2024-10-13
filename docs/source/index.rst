SoyutNet documentation
======================

SoyutNet is a place/transition net (PT net, Petri net) simulator
that uses Python's asyncio task and synchronization utilities as
backend. (*Soyut means abstract in Turkish.*)

This documents gives a brief information on `PT nets`_, summarizes
its implementation in `SoyutNet`_ and discusses the project's `Goals`_.

`Code repository 🔗 <https://github.com/dmrokan/soyutnet>`_

.. _PT nets:

PT nets
-------

Place/transition net is a formal modeling framework for discrete event
systems (DES). It also provides a graphical modeling framework to visualize
the structure of the model. A graphical example is given below.

.. _first example:

An example
^^^^^^^^^^

.. image:: _static/images/first_example_T0.png
   :width: 480
   :align: center

In the diagram,

* :math:`p_1` and :math:`p_2` are called **places**.
* :math:`t_1` is called a **transition**.
* :math:`a_1` and :math:`a_2` are **arcs** connecting transitions and places to each other.
* :math:`\bullet` is called a **token**.
* :math:`p_1` is an **input place** of :math:`t_1`
* :math:`p_2` is an **output place** of :math:`t_1`

When this model is executed, its flow is

#. :math:`p_1` has a token and its output arc is connected to :math:`t_1`,
#. :math:`t_1` is enabled because :math:`p_1` has 1 or more tokens,
#. :math:`t_1` is fired and it transfers the token from :math:`p_1` to :math:`p_2`.

The final state is:

.. image:: _static/images/first_example_T1.png
   :width: 480
   :align: center

The model reached its final state according to the rules explained below.

PT net definition and rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A PT net consists of 5 components

#. :math:`P=\{p_1, p_2, \dots, p_m\}` finite set of places
#. :math:`T=\{t_1, t_2, \dots, t_n\}` finite set of transitions
#. :math:`A \subseteq (P \times T) \cup (T \times P)` set of arcs from P to T and T to P
#. :math:`W: A \rightarrow \{1, 2, \dots\}` arc weights
#. :math:`M_0: P \rightarrow \{0, 1, 2, \dots\}` initial marking

In the example above,

* :math:`P=\{p_1, p_2\}`
* :math:`T=\{t_1\}`
* :math:`A=\{a_1, a_2\}`
* :math:`W=\{w(p_1, t_1)=1, w(t_1, p_2)=1\}`
* :math:`M_0=\{p_1 = 1, p_2 = 0\}`

Functions :math:`w(p_i, t_j)` and :math:`w(t_i, p_j)` denotes the arc weights between
transitions and places. After :math:`t_1` fires, marking changes and it becomes

.. math::
   M_1=\{p_1 = 0, p_2 = 1\}

according to the rules below.

1. A transition :math:`t_i` is enabled if its all input places have a number of tokens greater than or
   equal to the weight of the connecting arcs.

   .. math::
      M_{in} = \{u_1, u_2, \dots\} ~~~ \textrm{marking of input places of} ~ t_i \\
      M_{out} = \{v_1, v_2, \dots\} ~~~ \textrm{marking of output places of} ~ t_i \\

   .. math::
      w(\bar{p}_j, t_i) \leq u_j, ~~~ \textrm{for all input places} ~ \bar{p}_j

where :math:`j` are the indices of :math:`t_i`'s input places and :math:`M_{in}, M_{out}` are the
current marking of the input and output places (number of tokens in each place).

2. When a transition :math:`t_i` is fired, it removes a number of tokens equal to the weights of arcs
   connecting the input places and transfers a number of tokens equal to the weight of arcs connecting
   to the output places.

   .. math::
      M^{\ast}_{in} = \{u_1-w(\bar{p}_1,t_i), u_2-w(\bar{p}_2, t_i), \dots\} \\
      M^{\ast}_{out} = \{v_1+w(t_i,\tilde{p}_1), v_2+w(t_i, \tilde{p}_2), \dots\} \\

where :math:`M^{\ast}` is the new marking of input and output places after :math:`t_i` is fired.

.. image:: _static/images/io_arc_weights.png
   :align: center

Labeled PT net
^^^^^^^^^^^^^^

An extension of PT nets called **labeled PT nets** which assigns a label to the tokens and arcs.

.. image:: _static/images/first_example_labeled_PT.png
   :width: 720
   :align: center

The transition :math:`t_1` expects a specific type of token (represented by ◆) and transforms
it to a token with another label (▲).

.. _SoyutNet:

SoyutNet
--------

SoyutNet implements a slightly modified version of the labeled PT nets. Each place/transition (PT)
work asynchronously in their dedicated ``asyncio.Task`` and communicates to the other PTs
through ``asyncio.Queue`` instances in their input/output arcs.

Data structures
^^^^^^^^^^^^^^^

**Label**
    An integer value. Its type is ``label_t = int``. It can be the generic label
    (:py:attr:`soyutnet.constants.GENERIC_LABEL`) or any positive integer.

**ID**
    An integer value. Its type is ``id_t = int``. It can be the generic ID
    (:py:attr:`soyutnet.constants.GENERIC_ID`) or any positive integer.

**Token**
    It is defined as a tuple of a label and an ID.

   .. code-block:: python

      token: Tuple[label_t, id_t] = (label, id)

**Token binding**
    Tokens are not pure abstract structures. Each token can be binded to a
    concrete data structure. This can be done via :py:attr:`soyutnet.SoyutNet.TokenRegistry`.

    .. code-block:: python

       an_object = an_instantiator()
       net = SoyutNet()
       treg = net.TokenRegistry()
       actual_token = net.Token(label=label, binding=an_object)
       treg.register(actual_token) # Registry assigns an auto incrementing ID
       id_of_actual_token = actual_token._id

    And, the binded object can be retrived somewhere else in the program as below.

    .. code-block:: python

       binded_object = treg.pop_entry(label, id_of_actual_token).get_binding()

**Place**
    Keeps a Python dictionary of tokens indexed by labels (:py:attr:`soyutnet.pt_common.PTCommon._tokens`).

    .. code-block:: python

        token_dictionary: Dict[label_t, list[id_t]] = {
            label_1: [ id_1, id_2 ],
            label_2: [ id_3 ],
            label_3: [ id_4, id_5 ],
        }

**Arc**
    Arcs have a weight (default is 1) and *one or more labels*. And, they keep references to its
    input and output places/transitions (PTs).

    .. code-block:: python

       start = pt1 # Weak reference to the input place or transition
       end = pt2 # Weak reference to the output place or transition
       weight: int = 1
       labels: list[label_t] = [ label_1, label_2, ... ]

    An arc can accept any token whose label is in its ``labels`` list. End points ``start``
    and ``end`` can not both be places or transitions. If one is a place, the other must
    be a transition.

    Arcs use ``asyncio.Queue`` instances to wait for and transfer tokens. Their queue's maximum size
    is equal the arc's weight.

**Transition**
    A transition is enabled if all input arc (:py:attr:`soyutnet.pt_common.PTCommon._input_arcs`)
    queues (:py:attr:`soyutnet.pt_common.Arc._queue`) are full. Meaning, input arc queues has the
    same number of tokens as arc's weight.

    **SoyutNet's additional rule:** The sum of a transition's input arc weights for each label
    must be equal to the sum of its output arc weights for each label.

    As shown in the image below sum of input and output ◆ and ▲ are the same. If this property is
    not satisfied, SoyutNet model will possibly enter a
    `deadlock <https://en.wikipedia.org/wiki/Deadlock_(computer_science)>`_.

.. image:: _static/images/sum_of_arc_weights.png
   :width: 480
   :align: center

*Note:* SoyutNet's places and transitions accept a callback function named as ``processor``
(:py:attr:`soyutnet.pt_common.PTCommon._processor`). It is called after tokens acquired from input
arcs and before sending them through output arcs. SoyutNet's additional rule can be worked around
by a custom processor callback that duplicates or discards input tokens.

**Observer records**
    If a place has an observer attached, the observer keeps track of tokens when an output
    transition is fired. It records:

    * Time instant (for keeping track of the order of firings)
    * A tuple of token labels and count of tokens just before the firing
    * The identity of transition fired

      .. code:: python

         records = [
             ( time1, ( (label_1, count_11), (label_2, count_12), ... ), "<name of transition>" ),
             ( time2, ( (label_1, count_21), (label_2, count_22), ... ), "<name of transition>" ),
             ...
         ]

     The records (:py:attr:`soyutnet.observer.ObserverHistoryType`) saved in distinct observers can
     be merged by :py:func:`soyutnet.registry.PTRegistry.get_merged_records` at the end of simulation.


Special place
^^^^^^^^^^^^^

SoyutNet implements a special type of place called *SpecialPlace* (:py:class:`soyutnet.place.SpecialPlace`).
Regular places (:py:class:`soyutnet.place.Place`) operates according to the PT net rules. More precisely,
places redirect tokens from input arcs to the output arcs by matching token's and output arc's labels.

On the other hand, *SpecialPlace* class constructor accepts two extra optional arguments.

.. _producer:

1. ``producer``: It is a callback function which is called to acquire tokens after the
   default ``_process_input_arcs`` (:py:func:`soyutnet.pt_common.PTCommon._process_input_arcs`)
   is called. This function can be used to produce custom tokens by generating a label and ID.
   Then, it will be injected into the PT net's flow.

.. _consumer:

2. ``consumer``: This callback function is called before the default ``_process_output_arcs``
   function (:py:func:`soyutnet.pt_common.PTCommon._process_output_arcs`) is called.
   It can be used as an end point of PT net model. The tokens acquired by this function can be
   redirected to other utilities.

Graphviz DOT file generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Version ``0.2.0`` introduces Graphviz DOT file generation from the SoyutNet's net
structure. `DOT language <https://graphviz.org/doc/info/lang.html>`__ is a special
format for defining graph structures that can be parsed by
`dot <https://graphviz.org/doc/info/command.html>`__ command to generate images
in several formats.

Example code
^^^^^^^^^^^^

The code below implements the `first example`_ but arcs have two labels in this case. It means
:math:`t1` and :math:`p2` will accept tokens with both labels.

.. literalinclude:: ../../tests/readme_example.py
   :language: python

.. code:: bash

    $ python3 first_example.py 1 # Generates the Graphviz dot file below.
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

    $ python first_example.py 2>&1 > /dev/null | dot -Tpng > first_example.png

Outputs:

.. image:: _static/images/first_example.png
   :align: center

.. _Goals:

Goals
-----

SoyutNet implements a modified version of labeled PT nets with an additional rule;

    the sum of input arc weights of a transition must be equal to the sum of output arc
    weights for each label.

Because, SoyutNet assumes that tokens represent real entities with an ID and a label assigned.
The ID identifies the token and the label determines how it flows through the network.
It also ensures that a token created by a `producer`_ arrives at a `consumer`_ without
duplication or getting discarded as generally expected in a real life application. Producers
and consumers should decide to duplicate or discard a token.

The main goal of SoyutNet is to investigate that PT net based formal methods can be used to improve
a producer/consumer pipeline.

Docstrings
----------

.. toctree::
   :maxdepth: 3

   soyutnet

Examples
--------

.. toctree::
   :maxdepth: 2

   examples

Simulations
-----------

* `PI-controller <https://soyutnet.readthedocs.io/projects/simulations/en/latest/src.pi_controller.html>`__
* `HTTP balancer <https://soyutnet.readthedocs.io/projects/simulations/en/latest/src.http_balancer.html>`__
* `HTTP server <https://soyutnet.readthedocs.io/projects/simulations/en/latest/src.http_server.html>`__

Modules
-------

.. toctree::
   :maxdepth: 1

   modules

Credits
-------

.. toctree::
   :maxdepth: 2

   credits
