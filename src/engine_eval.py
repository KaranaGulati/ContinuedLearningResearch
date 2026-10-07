"""Centipawn loss for one game, from Stockfish or from Lichess's own [%eval] comments.

Each position is evaluated once. The position after your move is the
position before your opponent's move, so the evaluations form one sequence,
and each move's loss is the drop between two consecutive entries from the
mover's point of view:

    loss(ply j) = sign(mover) * (eval[j-1] - eval[j]),  clipped at 0

with every eval stored from White's point of view, sign +1 for White and -1
for Black. Mate scores become +-MATE_CP and every eval is then capped at
+-cap, so a missed mate counts as a large finite loss instead of zero or
infinity.
"""

import re

import chess
import chess.engine

MATE_CP = 100_000
LICHESS_EVAL_RE = re.compile(r"\[%eval (#?-?[\d.]+)")


def window_plies(first_move, last_move, n_ply):
    """Position indices (plies played) bounding the scored moves.

    Moves first_move..last_move for both sides are plies 2*first_move-1 to
    2*last_move. Scoring ply j needs positions j-1 and j.
    """
    lo = 2 * first_move - 2
    hi = min(2 * last_move, n_ply)
    return lo, hi


def _terminal_white_cp(board):
    if board.is_checkmate():
        return -MATE_CP if board.turn == chess.WHITE else MATE_CP
    if board.is_game_over(claim_draw=False):
        return 0
    return None


def engine_evals(engine, moves, lo, hi, depth, game_key):
    """White-POV centipawns for positions lo..hi (inclusive) of a move list."""
    board = chess.Board()
    for mv in moves[:lo]:
        board.push(mv)
    evals = []
    for k in range(lo, hi + 1):
        if k > lo:
            board.push(moves[k - 1])
        terminal = _terminal_white_cp(board)
        if terminal is not None:
            evals.append(terminal)
            continue
        info = engine.analyse(board, chess.engine.Limit(depth=depth), game=game_key)
        evals.append(info["score"].white().score(mate_score=MATE_CP))
    return evals


def final_eval(engine, moves, depth, game_key):
    """White-POV centipawns of the last position of the game."""
    board = chess.Board()
    for mv in moves:
        board.push(mv)
    terminal = _terminal_white_cp(board)
    if terminal is not None:
        return terminal
    info = engine.analyse(board, chess.engine.Limit(depth=depth), game=game_key)
    return info["score"].white().score(mate_score=MATE_CP)


def lichess_evals(movetext):
    """White-POV centipawns after each ply from [%eval] comments, None where absent.

    Index 0 is the start position, which Lichess never annotates.
    """
    out = [None]
    for comment in re.findall(r"\{([^}]*)\}", movetext):
        m = LICHESS_EVAL_RE.search(comment)
        if not m:
            out.append(None)
            continue
        v = m.group(1)
        if v.startswith("#"):
            out.append(MATE_CP if not v.startswith("#-") else -MATE_CP)
        else:
            out.append(round(float(v) * 100))
    return out


def move_losses(evals, lo, cap):
    """Per-move losses for both sides from a White-POV eval sequence starting at position lo.

    Returns {"white": [...], "black": [...]}; moves next to a missing eval are skipped.
    """
    capped = [None if e is None else max(-cap, min(cap, e)) for e in evals]
    losses = {"white": [], "black": []}
    for i in range(1, len(capped)):
        before, after = capped[i - 1], capped[i]
        if before is None or after is None:
            continue
        ply = lo + i  # 1-based ply number of the move played
        white_moved = ply % 2 == 1
        drop = (before - after) if white_moved else (after - before)
        losses["white" if white_moved else "black"].append(max(0, drop))
    return losses
