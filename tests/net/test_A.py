import pytest

from soyutnet import SoyutNet
from soyutnet.validate import ModelError


def test_01():
    net = SoyutNet()

    p = net.Place()
    t = net.Transition()

    p.connect(t).connect(p)


def test_01_01():
    net = SoyutNet()

    p = net.Place()
    t = net.Transition()

    with pytest.raises(ModelError):
        p.connect(p).connect(t)


def test_01_02():
    net = SoyutNet()

    p = net.Place()
    t = net.Transition()

    from soyutnet.pt_common import PTCommon

    pt = PTCommon(net=net)

    with pytest.raises(ModelError):
        p.connect(pt).connect(t)


def test_01_03():
    net = SoyutNet()
    net2 = SoyutNet()

    p = net.Place()
    t = net2.Transition()

    with pytest.raises(ModelError):
        p.connect(t).connect(p)


if __name__ == "__main__":
    test_01()
