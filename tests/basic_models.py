import sys
import asyncio

import soyutnet
from soyutnet.pt_common import PTRegistry
from soyutnet.token import Token
from soyutnet.place import SpecialPlace, Place
from soyutnet.transition import Transition
from soyutnet.common import GENERIC_ID, GENERIC_LABEL, DEBUG
from soyutnet.observer import ComparativeObserver, Observer


def co_begin(action_count):
    token_ids = list(range(1, action_count + 1))

    async def producer(place):
        try:
            id: id_t = token_ids.pop(0)
            return (GENERIC_LABEL, id)
        except IndexError:
            pass

        return tuple()

    output_token_ids = list(token_ids)

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        output_token_ids.remove(token[1])
        DEBUG(f"Token '{token}' is removed.")
        if not output_token_ids:
            soyutnet.terminate()

    reg = PTRegistry()
    p0 = SpecialPlace("p0", producer=producer)
    t0 = Transition("t0")
    p0.connect(t0, weight=action_count)
    reg.register(p0)
    reg.register(t0)
    for i in range(action_count):
        p1i = SpecialPlace(f"p1_{i}", consumer=consumer)
        reg.register(p1i)
        t0.connect(p1i)

    asyncio.run(soyutnet.main(reg))


def co_end(action_count):
    async def producer(place):
        DEBUG(f"{place.ident()}")
        place_id = place.ident().split(",")[0].split("_")[1]
        try:
            return (GENERIC_LABEL, int(place_id))
        except IndexError:
            pass

        return tuple()

    output_token_ids = list(range(1, action_count + 1))

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        output_token_ids.remove(token[1])
        DEBUG(f"Token '{token}' is removed.")
        if not output_token_ids:
            soyutnet.terminate()

    reg = PTRegistry()
    p1 = SpecialPlace("p0", consumer=consumer)
    t0 = Transition("t0")
    t0.connect(p1)
    reg.register(p1)
    reg.register(t0)
    for i in range(action_count):
        p0i = SpecialPlace(f"p0_{i+1}", producer=producer)
        reg.register(p0i)
        p0i.connect(t0)

    asyncio.run(soyutnet.main(reg))


def sync_by_signal():
    token_ids = list(range(1, 11)) + [GENERIC_ID] * 20

    async def producer(place):
        try:
            id = token_ids.pop(0)
            DEBUG(f"Produced '{(GENERIC_LABEL, id)}'")
            return (GENERIC_LABEL, id)
        except IndexError:
            pass

        return tuple()

    output_token_ids = token_ids[:10]

    async def consumer(place):
        token = place.get_token(GENERIC_LABEL)
        if not token:
            return
        if token[1] == GENERIC_ID:
            return
        output_token_ids.remove(token[1])
        DEBUG(f"Consumed '{token}'")
        if not output_token_ids:
            soyutnet.terminate()

    activate = False

    async def processor(place):
        nonlocal activate
        if place._get_token_count(GENERIC_LABEL) > 3:
            DEBUG(f"Activated. 'p4' will start consuming.")
            activate = True

        return activate

    p0 = SpecialPlace("p0", producer=producer)
    p1 = SpecialPlace("p1", consumer=consumer)
    p2 = Place("p2", processor=processor)
    p3 = SpecialPlace("p3", producer=producer)
    p4 = SpecialPlace("p4", consumer=consumer)
    t0 = Transition("t0")
    t1 = Transition("t1")

    reg = PTRegistry()
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

    asyncio.run(soyutnet.main(reg))


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
        return token

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


def reader_writer(N=1):
    writer_produced_count = 0
    WRITER_LABEL = 1

    async def writer_producer(place):
        nonlocal writer_produced_count
        writer_produced_count += 1
        DEBUG(f"Produced {writer_produced_count}")
        return (WRITER_LABEL, writer_produced_count)

    reader_produced_count = 0
    READER_LABEL = 2

    async def reader_producer(place):
        nonlocal reader_produced_count
        reader_produced_count += 1
        DEBUG(f"Produced {reader_produced_count}")
        return (READER_LABEL, reader_produced_count)

    consumed_count = {WRITER_LABEL: 5, READER_LABEL: 5}

    async def consumer(place):
        nonlocal consumed_count
        token = place.get_token(WRITER_LABEL) or place.get_token(READER_LABEL)
        if not token:
            return
        consumed_count[token[0]] -= 1
        DEBUG(f"Consumed {consumed_count}, {token}")
        if sum(consumed_count.values()) == 0:
            soyutnet.terminate()

    w0 = SpecialPlace("w0", producer=writer_producer)
    wt0 = Transition("wt0")
    w1 = Place("w1", observer_verbose=True)
    wt1 = Transition("wt1")
    w2 = Place("w2", observer_verbose=True)
    wt2 = Transition("wt2")
    w3 = SpecialPlace("w3", consumer=consumer)

    r0 = SpecialPlace("r0", producer=reader_producer)
    rt0 = Transition("rt0")
    r1 = Place("r1", observer_verbose=True)
    rt1 = Transition("rt1")
    r2 = Place("r2", observer_verbose=True)
    rt2 = Transition("rt2")
    r3 = SpecialPlace("r3", consumer=consumer)

    initial_tokens = {
        WRITER_LABEL: [GENERIC_ID] * (1),
        READER_LABEL: [GENERIC_ID] * (1),
    }
    lock = Place("lock", initial_tokens=initial_tokens)

    reg = PTRegistry()
    reg.register(w0)
    reg.register(w1)
    reg.register(w2)
    reg.register(w3)
    reg.register(wt0)
    reg.register(wt1)
    reg.register(wt2)
    # reg.register(r0)
    # reg.register(r1)
    # reg.register(r2)
    # reg.register(r3)
    # reg.register(rt0)
    # reg.register(rt1)
    # reg.register(rt2)
    reg.register(lock)

    (
        w0.connect(wt0, label=WRITER_LABEL)
        .connect(w1, label=WRITER_LABEL)
        .connect(wt1, label=WRITER_LABEL)
        .connect(w2, label=WRITER_LABEL, weight=2)
        .connect(wt2, label=WRITER_LABEL, weight=2)
        .connect(w3, label=WRITER_LABEL)
    )

    # (r0.connect(rt0, label=READER_LABEL)
    # .connect(r1, label=READER_LABEL)
    # .connect(rt1, label=READER_LABEL)
    # .connect(r2, label=READER_LABEL)
    # .connect(rt2, label=READER_LABEL, weight=1)
    # .connect(r3, label=READER_LABEL))

    wt2.connect(lock, label=WRITER_LABEL, weight=N).connect(
        wt1, label=WRITER_LABEL, weight=N
    )
    # rt2.connect(lock, label=READER_LABEL).connect(rt1, label=READER_LABEL)

    asyncio.run(soyutnet.main(reg))


if __name__ == "__main__":
    # co_end(int(sys.argv[1]))
    sync_by_signal()
    # feedback(int(sys.argv[1]))
