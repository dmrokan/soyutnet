import sys
import asyncio
from pathlib import Path

import pytest

import soyutnet
from soyutnet import SoyutNet
from soyutnet.constants import GENERIC_ID, GENERIC_LABEL
from test_utils import compare_graph, dump_graph, ConnectionTestData


PathType = type(Path())


# NOTE: Inheriting Path not working for python<=3.11
class APath(PathType):
    def __add__(self, other):
        return self.parent / (self.name + other)


DIR = APath(__file__).resolve().parent
ARTIFACT_DIR = DIR / "artifacts"


async def scheduled():
    await asyncio.sleep(0)
    soyutnet.terminate()


def create_pts(net, N=5):
    i = 1
    while i <= N:
        yield net.Place(f"p{i}")
        yield net.Transition(f"t{i}")
        i += 1


@pytest.mark.filterwarnings("ignore::pytest.PytestReturnNotNoneWarning")
class TestSingleBranch:
    PATH = ARTIFACT_DIR / "TestSingleBranch"

    @dump_graph(PATH + "-test_labeled")
    @compare_graph
    def test_labeled(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, *_ = create_pts(net)

            # [[TestSingleBranch-test_labeled-connections-start]]

            a = lambda weight, labels: net.Arc(weight=weight, labels=labels)
            p1 >> a(2, [1, 2]) >> t1 >> a(1, [1]) >> p2
            t1 >> a(1, [2]) >> p1

            # [[TestSingleBranch-test_labeled-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="a44e6c3b144e77dd9e84d561f3b7e122c293ef9128c07279f7035efae1f2db59",
            )

    @dump_graph(PATH + "-test_01_a")
    @compare_graph
    def test_01_a(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, *_ = create_pts(net)

            # [[TestSingleBranch-test_01_a-connections-start]]

            assert t1 == p1 >> t1
            assert t1 == t1 > p1

            # [[TestSingleBranch-test_01_a-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="e347fe876d2e4aaa1f86ceb6aae20c0f38a8f9dee1b38560d3f56504f5603262",
            )

    @dump_graph(PATH + "-test_01_b")
    @compare_graph
    def test_01_b(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, *_ = create_pts(net)

            # [[TestSingleBranch-test_01_b-connections-start]]

            assert p3 == (p1 >> t1 >> p2 >> t2 >> p3)

            # [[TestSingleBranch-test_01_b-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_02")
    @compare_graph
    def test_02(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, *_ = create_pts(net)

            # [[TestSingleBranch-test_02-connections-start]]

            assert p1 == (p1 > (t1 > (p2 > (t2 > p3))))

            # [[TestSingleBranch-test_02-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_03")
    @compare_graph
    def test_03(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, *_ = create_pts(net)

            # [[TestSingleBranch-test_03-connections-start]]

            assert p1 == (p3 << t2 << p2 << t1 << p1)

            # [[TestSingleBranch-test_03-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_04")
    @compare_graph
    def test_04(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_04-connections-start]]

            assert p3 == (p3 < (t2 < (p2 < (t1 < p1))))
            assert p3 == (p3 > (t2 >> p2 >> t1 >> p1 >> t3))

            # [[TestSingleBranch-test_04-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="62cbb0311ade30a91a84767f4ea67f627fd065841488ea6aaafe036442e07f88",
            )

    @dump_graph(PATH + "-test_05")
    @compare_graph
    def test_05(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_05-connections-start]]

            _ = net.Arc()
            assert p3 == (p1 >> _ >> t1 >> _ >> p2 >> t2 >> _ >> p3)

            # [[TestSingleBranch-test_05-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_06")
    @compare_graph
    def test_06(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_06-connections-start]]

            _ = net.Arc()
            assert p1 == (p3 << _ << t2 << _ << p2 << _ << t1 << _ << p1)

            # [[TestSingleBranch-test_06-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_07")
    @compare_graph
    def test_07(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_07-connections-start]]

            _ = net.Arc()
            assert t2 == (p1 > _ > t1 > _ > p2 > _ > t2 > _ > p3)

            # [[TestSingleBranch-test_07-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_08")
    @compare_graph
    def test_08(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_08-connections-start]]

            _ = net.Arc()
            assert t1 == (p3 < _ < t2 < _ < p2 < _ < t1 < _ < p1)

            # [[TestSingleBranch-test_08-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="f6db9e19de3fbe276056f0d210aad8ef2a1566b7f58e363cf8becde4c172b68a",
            )

    @dump_graph(PATH + "-test_09")
    @compare_graph
    def test_09(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # [[TestSingleBranch-test_09-connections-start]]

            _ = net.Arc(weight=3, labels=[1, 2])
            assert t1 == (p3 < _ < t2 < _ < p2 < _ < t1 < _ < p1)

            # [[TestSingleBranch-test_09-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(label_names={1: "◆", 2: "▲"}),
                hash="b64c98b0fe7b1a7b0ab02c05205b124793e04ad8a91ae85528a32278a50aefdc",
            )


@pytest.mark.filterwarnings("ignore::pytest.PytestReturnNotNoneWarning")
class TestSplit:
    PATH = ARTIFACT_DIR / "TestSplit"

    @dump_graph(PATH + "-test_01")
    @compare_graph
    def test_01(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, _, p3, *_ = create_pts(net)

            # [[TestSplit-test_01-connections-start]]

            _ = net.Arc(weight=2)
            assert p2 == (p1 >> _ >> t1 >> p2)
            assert p3 == (t1 >> p3)

            # [[TestSplit-test_01-connections-end]]

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="ae0c247923633faccbbd6e5782b13ea0a8b14fcb8b8c829b5148da13bfaec82c",
            )

    @dump_graph(PATH + "-test_02")
    @compare_graph
    def test_02(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, _, p3, *_ = create_pts(net)

            # fmt: off
            # [[TestSplit-test_02-connections-start]]

            _ = net.Arc(weight=2)
            assert t1 == (p1 >> _ >> t1 > {
                p2,
                p3,
            })

            # [[TestSplit-test_02-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="ae0c247923633faccbbd6e5782b13ea0a8b14fcb8b8c829b5148da13bfaec82c",
            )

    @dump_graph(PATH + "-test_03")
    @compare_graph
    def test_03(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, *_ = create_pts(net)

            # fmt: off
            # [[TestSplit-test_03-connections-start]]

            _ = net.Arc(weight=2)
            assert t1 == (p1 >> _ >> t1 > {
                p3 << t2 << p2,
                p3,
            })

            # [[TestSplit-test_03-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="59077940298e617a3b8bb3a71825526677e4b6b65ece396d36312e3589d20c2e",
            )

    @dump_graph(PATH + "-test_04")
    @compare_graph
    def test_04(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, p4, *_ = create_pts(net)

            # fmt: off
            # [[TestSplit-test_04-connections-start]]

            assert p1 == (((p1 > t1) > t2) > t3)
            assert p2 == (t1 >> p2)
            assert p3 == (t2 >> p3)
            assert p4 == (t3 >> p4)

            # [[TestSplit-test_04-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="acdcb9149e5806d980d546777f7ccf460fbfcc2eecbc4c92199ef22051e26675",
            )

    @dump_graph(PATH + "-test_05")
    @compare_graph
    def test_05(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, p4, *_ = create_pts(net)

            # fmt: off
            # [[TestSplit-test_05-connections-start]]

            assert p1 == (((p1 > {t1 > p2}) > {t2 > p3}) > {t3 > p4})

            # [[TestSplit-test_05-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="acdcb9149e5806d980d546777f7ccf460fbfcc2eecbc4c92199ef22051e26675",
            )

    @dump_graph(PATH + "-test_06")
    @compare_graph
    def test_06(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, p4, t4, *_ = create_pts(net)

            # fmt: off
            # [[TestSplit-test_06-connections-start]]

            _ = net.Arc(weight=2)
            assert t1 == (p1 >> _ >> t1 > {
                p2 > (t2 > (p3 > (t4 > p4))),
                p3,
            })

            # [[TestSplit-test_06-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="7534922d8080ad6cb124769bb89374d4af8505529d1ed289ff8d88bc49a4e73d",
            )

    @dump_graph(PATH + "-test_07")
    @compare_graph
    def test_07(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, p4, t4, p5, t5 = create_pts(net)

            # fmt: off
            # [[TestSplit-test_07-connections-start]]

            a1 = net.Arc(labels=[1])
            a2 = net.Arc(labels=[2])
            a = net.Arc(labels=[1, 2], weight=2)

            assert t1 == (p1 >> a >> {
                t1 > a1 > p2,
                t1 > a2 > p3,
            })

            # [[TestSplit-test_07-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="b2839693780bed48edec1ed94a192dc0b650b04b13eb694d30278c9b94a78c6f",
            )

    @dump_graph(PATH + "-test_08")
    @compare_graph
    def test_08(self):
        with SoyutNet(extra_routines=[scheduled()]) as net:
            p1, t1, p2, t2, p3, t3, p4, t4, p5, t5 = create_pts(net)
            _ = net.Arc(weight=2)

            # fmt: off
            # [[TestSplit-test_08-connections-start]]

            a = lambda x: net.Arc(labels=[x])
            _ = net.Arc(labels=[1, 2, 3], weight=4)

            assert p1 == (p1 >> _ >> {
                t1 > a(1) > {
                    p2 > a(1) > {t2 > a(1) > p4},
                    p3 > a(2) > {t2 > a(2) > p5},
                },
                t1 > a(2) > {
                    p3 > a(1) > {t3 > a(1) > p4},
                },
            }) >> a(3) >> p1

            # [[TestSplit-test_08-connections-end]]
            # fmt: on

            return ConnectionTestData(
                graph=net.registry.generate_graph(),
                hash="83b084bafd86bf650b0c9ea9e0eeb3ae3fc136e6ac77eb0b761828774de1f72b",
            )
