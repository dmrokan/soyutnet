import hashlib
from subprocess import Popen, PIPE
from shutil import which
from dataclasses import dataclass

import warnings


@dataclass
class ConnectionTestData:
    graph: str
    hash: str


def call_dot(graph, filename):
    dot = which("dot")
    if dot is None:
        warnings.warn(
            UserWarning("'dot' command not found. Skipping graph image generation...")
        )
        return
    cmd = [dot, "-Gorientation=L", "-Tpng"]
    with Popen(cmd, stdin=PIPE, stdout=PIPE) as proc:
        outs, errs = proc.communicate(graph.encode())
        with open(filename + ".png", "wb") as fh:
            fh.write(outs)

    assert proc.returncode == 0


def compare_graph(func):
    def wrapped(*args, **kwargs):
        test_data = func(*args, **kwargs)
        graph = test_data.graph
        hash = test_data.hash
        real_hash = hashlib.sha256(graph.encode("utf-8")).hexdigest()
        assert real_hash == hash, real_hash
        return test_data

    return wrapped


def dump_graph(path):
    def inner(func):
        def wrapped(*args, **kwargs):
            test_data = func(*args, **kwargs)
            graph = test_data.graph
            if isinstance(graph, str) and graph:
                call_dot(graph, path)
            return test_data

        return wrapped

    return inner
