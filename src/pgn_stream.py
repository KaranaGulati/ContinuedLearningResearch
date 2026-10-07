"""Fast splitter for Lichess PGN streams.

python-chess's PGN reader builds a full move tree per game and manages a few
thousand games a second, too slow for a 90-million-game month. Lichess dumps
are regular: a block of [Tag "value"] lines, a blank line, the movetext on
one line, and a blank line. This reads that layout directly.
"""

import io
import re

TAG_RE = re.compile(r'^\[(\w+) "(.*)"\]$')


def iter_games(binary_stream):
    """Yield (headers, movetext, raw_pgn_text) for each game in the stream."""
    text = io.TextIOWrapper(binary_stream, encoding="utf-8", errors="replace")
    headers, header_lines, move_lines = {}, [], []

    def emit():
        movetext = " ".join(move_lines)
        raw = "\n".join(header_lines) + "\n\n" + "\n".join(move_lines) + "\n"
        return headers, movetext, raw

    for line in text:
        line = line.rstrip("\n").rstrip("\r")
        if line.startswith("["):
            if move_lines:
                yield emit()
                headers, header_lines, move_lines = {}, [], []
            m = TAG_RE.match(line)
            if m:
                headers[m.group(1)] = m.group(2)
                header_lines.append(line)
        elif line.strip():
            move_lines.append(line)
        elif move_lines and headers:
            yield emit()
            headers, header_lines, move_lines = {}, [], []
    if headers and move_lines:
        yield emit()
