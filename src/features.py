"""Per-game features derived from Lichess PGN headers and movetext.

Everything here works on raw text, without replaying moves, so it can run over a
full monthly dump. The checkmate test uses the SAN suffix "#", which Lichess
writes on the mating move. tests/test_features.py checks it against
board.is_checkmate() on the fixtures, and validate_checkmate.py does the same on
a sample of real games.
"""

import re
from datetime import datetime, timezone

COMMENT_RE = re.compile(r"\{[^}]*\}")
CLK_RE = re.compile(r"\[%clk (\d+):(\d\d):(\d\d(?:\.\d+)?)\]")
MOVE_NUMBER_RE = re.compile(r"^\d+\.+$")
RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}
DROPPED_TERMINATIONS = {"Abandoned", "Rules infraction", "Unterminated"}


def speed_class(time_control):
    """Lichess speed category from a TimeControl tag like "600+5".

    Lichess estimates game length as base + 40 * increment and buckets it:
    under 30s ultraBullet, under 180s bullet, under 480s blitz, under 1500s
    rapid, otherwise classical. Correspondence games have TimeControl "-".
    """
    if not time_control or time_control == "-" or "+" not in time_control:
        return "correspondence", None, None
    base, inc = time_control.split("+", 1)
    base, inc = int(base), int(inc)
    estimate = base + 40 * inc
    if estimate < 30:
        speed = "ultraBullet"
    elif estimate < 180:
        speed = "bullet"
    elif estimate < 480:
        speed = "blitz"
    elif estimate < 1500:
        speed = "rapid"
    else:
        speed = "classical"
    return speed, base, inc


def start_timestamp(headers):
    """Unix seconds for the game start, from UTCDate and UTCTime."""
    date, time = headers.get("UTCDate"), headers.get("UTCTime")
    if not date or not time or "?" in date or "?" in time:
        return None
    dt = datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S")
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def san_moves(movetext):
    """SAN tokens in order, with comments, move numbers and the result removed."""
    stripped = COMMENT_RE.sub(" ", movetext)
    return [
        t for t in stripped.split()
        if t not in RESULTS and not MOVE_NUMBER_RE.match(t)
        and not t.startswith("$")
    ]


def clocks(movetext):
    """Clock readings in seconds, one per ply, in move order."""
    return [int(h) * 3600 + int(m) * 60 + float(s) for h, m, s in CLK_RE.findall(movetext)]


def winner(result):
    return {"1-0": "white", "0-1": "black"}.get(result, "")


def classify_win(termination, result, last_san):
    """How a decisive game ended: "time", "checkmate", "resign", "draw" or "drop".

    Termination "Normal" covers both checkmate and resignation, so the mating
    move's "#" suffix is what separates them.
    """
    if termination in DROPPED_TERMINATIONS or result not in ("1-0", "0-1", "1/2-1/2"):
        return "drop"
    if result == "1/2-1/2":
        return "draw"
    if termination == "Time forfeit":
        return "time"
    if termination == "Normal":
        return "checkmate" if last_san and last_san.endswith("#") else "resign"
    return "drop"


def game_features(headers, movetext):
    """Everything later stages need about one rapid game, as a flat dict."""
    moves = san_moves(movetext)
    clk = clocks(movetext)
    speed, base, inc = speed_class(headers.get("TimeControl"))
    white_clk, black_clk = clk[0::2], clk[1::2]

    def used(side_clk):
        # First reading is the clock after the first move, which also catches
        # berserk (started at half the base). Increment is added after each move.
        if len(side_clk) < 2:
            return 0.0
        return max(0.0, side_clk[0] - side_clk[-1] + (inc or 0) * (len(side_clk) - 1))

    has_clk = len(clk) > 0
    return {
        "tc_base": base,
        "tc_inc": inc,
        "white_elo": _int_or_none(headers.get("WhiteElo")),
        "black_elo": _int_or_none(headers.get("BlackElo")),
        "result": headers.get("Result", ""),
        "termination": headers.get("Termination", ""),
        "winner": winner(headers.get("Result", "")),
        "win_type": classify_win(headers.get("Termination", ""), headers.get("Result", ""),
                                 moves[-1] if moves else ""),
        "n_ply": len(moves),
        "duration_s": round(used(white_clk) + used(black_clk), 1) if has_clk else None,
        "white_first_clk": white_clk[0] if white_clk else None,
        "black_first_clk": black_clk[0] if black_clk else None,
        "has_clk": int(has_clk),
        "has_eval": int("[%eval" in movetext),
    }


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
