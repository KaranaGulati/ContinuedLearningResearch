import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import resumable  # noqa: E402
from resumable import ResumableReader  # noqa: E402

DATA = bytes(range(256)) * 400  # 102,400 bytes


class FakeProc:
    def __init__(self, chunk):
        self.stdout = io.BytesIO(chunk)

    def wait(self):
        return 0

    def poll(self):
        return 0


def flaky_opener(cut_every):
    """Each connection delivers at most cut_every bytes, then drops."""
    calls = []

    def open_at(url, offset):
        calls.append(offset)
        return FakeProc(DATA[offset:offset + cut_every])
    return open_at, calls


def test_resumes_from_exact_byte(monkeypatch):
    monkeypatch.setattr(resumable.time, "sleep", lambda s: None)
    open_at, calls = flaky_opener(30_000)
    r = ResumableReader("u", total=len(DATA), open_at=open_at, log=io.StringIO())
    out = b"".join(iter(lambda: r.read(4096), b""))
    assert out == DATA
    assert calls == [0, 30_000, 60_000, 90_000]
    assert r.resumes == 3


def test_gives_up_when_server_stops_sending(monkeypatch):
    monkeypatch.setattr(resumable.time, "sleep", lambda s: None)
    r = ResumableReader("u", total=len(DATA), open_at=lambda url, off: FakeProc(b""),
                        max_failures=3, log=io.StringIO())
    with pytest.raises(IOError):
        r.read(4096)
