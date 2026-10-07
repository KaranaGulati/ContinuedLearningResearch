"""A file-like reader over HTTP that resumes after a dropped connection.

A monthly dump is ~30 GB and takes over an hour to stream, so a single
dropped connection is likely. When the transfer stops early, this reopens it
with an HTTP Range request from the exact byte already received. The caller
(a zstd decompressor) keeps its state and never sees the gap.
"""

import subprocess
import sys
import time


def content_length(url):
    out = subprocess.run(["curl", "-sSfIL", url], capture_output=True, text=True, check=True).stdout
    lengths = [int(line.split(":", 1)[1]) for line in out.splitlines()
               if line.lower().startswith("content-length:")]
    if not lengths:
        raise IOError(f"no Content-Length for {url}")
    return lengths[-1]


def curl_from(url, offset):
    args = ["curl", "-sSfL", url] if offset == 0 else ["curl", "-sSfL", "-r", f"{offset}-", url]
    return subprocess.Popen(args, stdout=subprocess.PIPE)


class ResumableReader:
    def __init__(self, url, total=None, open_at=curl_from, max_failures=20, log=sys.stderr):
        self.url = url
        self.total = content_length(url) if total is None else total
        self.open_at = open_at
        self.max_failures = max_failures
        self.log = log
        self.offset = 0
        self.resumes = 0
        self._failures = 0
        self._proc = open_at(url, 0)

    def readable(self):
        return True

    def read(self, n=-1):
        while True:
            data = self._proc.stdout.read(n)
            if data:
                self.offset += len(data)
                self._failures = 0
                return data
            self._proc.wait()
            if self.offset >= self.total:
                return b""
            self._failures += 1
            if self._failures > self.max_failures:
                raise IOError(f"gave up at byte {self.offset:,} of {self.total:,} after "
                              f"{self.max_failures} failed reconnects")
            delay = min(60, 2 ** self._failures)
            print(f"connection dropped at byte {self.offset:,} of {self.total:,}; "
                  f"resuming in {delay}s", file=self.log, flush=True)
            time.sleep(delay)
            self.resumes += 1
            self._proc = self.open_at(self.url, self.offset)

    def close(self):
        if self._proc.poll() is None:
            self._proc.kill()
