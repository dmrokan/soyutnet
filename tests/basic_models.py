import sys
import asyncio

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL, TokenType


def co_begin(action_count):
    token_ids = list(range(1, action_count + 1))

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return [(GENERIC_LABEL, id)]
        except IndexError:
            pass

        return []

    output_token_ids = list(token_ids)

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        output_token_ids.remove(token[1])
        if not output_token_ids:
            await net.sleep(0.01)
            soyutnet.terminate()

    net = SoyutNet()
    o1 = net.ComparativeObserver(expected={1: [((GENERIC_LABEL, action_count),)]})
    o31 = net.ComparativeObserver(
        expected={1: [((GENERIC_LABEL, 0),)] * action_count + [((GENERIC_LABEL, 1),)]}
    )
    reg = net.PTRegistry()
    p1 = net.Place("p1", initial_tokens={GENERIC_LABEL: token_ids})
    p2 = net.Place("p2", observer=o1)
    t1 = net.Transition("t1", record_firing=True)
    t2 = net.Transition("t2", record_firing=True)
    p1.connect(t1).connect(p2).connect(t2, weight=action_count)
    reg.register(p1)
    reg.register(p2)
    reg.register(t1)
    reg.register(t2)
    for i in range(action_count):
        obsv = None
        if i == 0:
            obsv = o31
        p3i = net.SpecialPlace(f"p3_{i}", consumer=consumer, observer=obsv)
        reg.register(p3i)
        t2.connect(p3i)

    total_firings = [0, 0]

    async def firing_test1():
        nonlocal total_firings
        while True:
            await t1.wait_for_firing()
            total_firings[0] += 1

    async def firing_test2():
        nonlocal total_firings
        while True:
            await t2.wait_for_firing()
            total_firings[1] += 1

    soyutnet.run(reg, extra_routines=[firing_test1(), firing_test2()])

    print(total_firings, t2.get_no_of_times_enabled())
    assert total_firings[0] == t1.get_no_of_times_enabled() - 1
    assert total_firings[0] == len(t1.get_firing_records()) - 1
    """t1 notifies before firing_test1 starts waiting misses waiting for the first one."""
    assert total_firings[1] == t2.get_no_of_times_enabled()
    assert total_firings[1] == len(t2.get_firing_records())


def co_end(action_count):
    async def producer(place):
        net.DEBUG(f"{place.ident()}")
        place_id = place.ident().split(",")[0].split("_")[1]
        try:
            return [(GENERIC_LABEL, int(place_id))]
        except IndexError:
            pass

        return []

    output_token_ids = list(range(1, action_count + 1))

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        output_token_ids.remove(token[1])
        net.DEBUG(f"Token '{token}' is removed.")
        if not output_token_ids:
            soyutnet.terminate()

    net = SoyutNet()
    reg = net.PTRegistry()
    p1 = net.SpecialPlace("p0", consumer=consumer)
    t0 = net.Transition("t0")
    t0.connect(p1)
    reg.register(p1)
    reg.register(t0)
    for i in range(action_count):
        p0i = net.SpecialPlace(f"p0_{i+1}", producer=producer)
        reg.register(p0i)
        p0i.connect(t0)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        pass


def sync_by_signal():
    token_ids = list(range(1, 11)) + [GENERIC_ID] * 30

    async def producer(place):
        try:
            id = token_ids.pop(0)
            net.DEBUG(f"Produced '{(GENERIC_LABEL, id)}'")
            return [(GENERIC_LABEL, id)]
        except IndexError:
            pass

        return []

    output_token_ids = token_ids[:10]

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        if token[1] == GENERIC_ID:
            return
        output_token_ids.remove(token[1])
        net.DEBUG(f"Consumed '{token}'")
        if not output_token_ids:
            soyutnet.terminate()

    activate = False

    async def processor(place):
        nonlocal activate
        if place._get_token_count(GENERIC_LABEL) > 3:
            net.DEBUG(f"Activated. 'p4' will start consuming.")
            activate = True

        return activate

    net = SoyutNet()
    p0 = net.SpecialPlace("p0", producer=producer)
    p1 = net.SpecialPlace("p1", consumer=consumer)
    p2 = net.Place("p2", processor=processor)
    p3 = net.SpecialPlace("p3", producer=producer)
    p4 = net.SpecialPlace("p4", consumer=consumer)
    t0 = net.Transition("t0")
    t1 = net.Transition("t1")

    reg = net.PTRegistry()
    reg.register(p0)
    reg.register(p1)
    reg.register(p2)
    reg.register(p3)
    reg.register(p4)
    reg.register(t0)
    reg.register(t1)

    p0.connect(t0, weight=2).connect(p1)
    t0.connect(p2).connect(t1)
    p3.connect(t1).connect(p4)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        pass

    gv = reg.generate_graph()
    return gv


def feedback(N=1):
    token_ids = list(range(1, 5))
    WRITER_LABEL = 1

    async def producer(place):
        try:
            id = token_ids.pop(0)
            label = WRITER_LABEL
        except IndexError:
            id = GENERIC_ID
            label = GENERIC_LABEL
        token = (label, id)
        DEBUG(f"Produced {token}")
        return [token]

    consumed_ids = list(token_ids)

    async def consumer(place):
        nonlocal consumed_ids
        token = place.get_token(WRITER_LABEL)
        if not token:
            return
        try:
            consumed_ids.remove(token[1])
        except ValueError:
            return
        print(f"Consumed {token}")
        if not consumed_ids:
            soyutnet.terminate()

    p0 = SpecialPlace("p0", producer=producer)
    pt0 = Transition("pt0")
    p1 = Place("p1", observer_verbose=False)
    pt1 = Transition("pt1")
    p2 = Place("p2", observer_verbose=False)
    pt2 = Transition("pt2")
    p3 = SpecialPlace("p3", consumer=consumer)

    FEEDBACK_LABEL = 1
    initial_tokens = {
        GENERIC_LABEL: [GENERIC_ID] * (1 + N),
    }
    lock = Place("lock", initial_tokens=initial_tokens)

    reg = PTRegistry()
    reg.register(p0)
    reg.register(p1)
    reg.register(p2)
    reg.register(p3)
    reg.register(pt0)
    reg.register(pt1)
    reg.register(pt2)
    reg.register(lock)

    labels = [WRITER_LABEL, GENERIC_LABEL]
    (
        p0.connect(pt0, labels=labels)
        .connect(p1, labels=labels)
        .connect(pt1, labels=labels)
        .connect(p2, weight=2, labels=labels)
        .connect(pt2, weight=N + 1, labels=labels)
        .connect(p3, labels=labels[:1])
    )

    pt2.connect(lock, weight=N).connect(pt1)

    try:
        asyncio.run(soyutnet.main(reg))
    except asyncio.exceptions.CancelledError:
        pass

    print(pt0.ident(), pt0.get_no_of_times_enabled())
    print(pt1.ident(), pt1.get_no_of_times_enabled())
    print(pt2.ident(), pt2.get_no_of_times_enabled())
