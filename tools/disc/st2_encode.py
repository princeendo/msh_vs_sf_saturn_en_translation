"""Encoders for the attract-stream codecs (UI-003, `EXP-0071`).

Both encoders parse optimally for the codec's fixed token costs, so they compress
at least as well as a greedy encoder; the game's own files leave very little
room (section A of ``MVSOP6`` has 0x18 bytes free).

- ``lz_encode``: the graphics LZ decoded by ``st2_stream.lz_decode``. Tokens: a
  literal costs 9 bits, a copy (3-18 bytes from 1-4096 back) 17 bits.
- ``map_encode``: the word LZ of the map updates (``st2_stream.map_decode``),
  greedy: the longest copy (1-8192 words from 1-65536 back) in its shortest
  form, else a literal word.
- ``script_encode``: section A's bit-flag LZ decoded by
  ``st2_stream.script_decode``. Tokens: literal 9 bits; short copy (2-5 bytes
  from 1-256 back) 12 bits; long copy (3-9 bytes from 1-8191 back) 18 bits;
  extended long copy (2-256 bytes) 26 bits; the end marker 2 flag bits plus
  3 bytes.

The longest match at each position is found with hash chains limited to
``chain`` candidates, so the parse is optimal for the matches found.
"""

from __future__ import annotations

import struct
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass


def longest_matches(
    data: bytes, window: int, max_length: int, min_length: int, chain: int = 96
) -> list[tuple[int, int]]:
    """(length, distance) of a longest match at each position (0 if none)."""
    heads: defaultdict[bytes, list[int]] = defaultdict(list)
    result = [(0, 0)] * len(data)
    for i in range(len(data)):
        key = data[i : i + min_length]
        if len(key) < min_length:
            break
        candidates = heads[key]
        best, best_distance = 0, 0
        limit = min(max_length, len(data) - i)
        for j in reversed(candidates[-chain:]):
            distance = i - j
            if distance > window:
                break
            length = min_length
            while length < limit and data[j + length] == data[i + length]:
                length += 1
            if length > best:
                best, best_distance = length, distance
                if length == limit:
                    break
        result[i] = (best, best_distance)
        candidates.append(i)
    return result


def short_matches(data: bytes, window: int, max_length: int) -> list[tuple[int, int]]:
    """(length, distance) of a longest match of 2-``max_length`` bytes within
    ``window`` (used for the script codec's short copies)."""
    return longest_matches(data, window, max_length, 2, chain=32)


def _lz_parse(
    data: bytes,
) -> tuple[list[int], list[int], list[tuple[int, int]]]:
    """Optimal graphics-LZ parse: (bits from each position to the end, copy
    length chosen there or 0 for a literal, longest matches)."""
    n = len(data)
    matches = longest_matches(data, 4096, 18, 3)
    cost = [0] * (n + 1)
    choice = [0] * (n + 1)  # 0 = literal, else copy length
    for i in range(n - 1, -1, -1):
        cost[i], choice[i] = 9 + cost[i + 1], 0
        length = matches[i][0]
        for take in range(3, length + 1):
            if 17 + cost[i + take] < cost[i]:
                cost[i], choice[i] = 17 + cost[i + take], take
    return cost, choice, matches


def lz_encode(data: bytes) -> bytes:
    """Graphics LZ: header (u32 compressed size, u32 size) plus the token stream."""
    n = len(data)
    _, choice, matches = _lz_parse(data)
    out = bytearray()
    i = 0
    while i < n:
        flag_at = len(out)
        out.append(0)
        for bit in range(8):
            if i >= n:
                break
            take = choice[i]
            if take:
                distance = matches[i][1]
                word = ((0x1000 - distance) << 4) | (take - 3)
                out[flag_at] |= 0x80 >> bit
                out += struct.pack(">H", word)
                i += take
            else:
                out.append(data[i])
                i += 1
    return struct.pack(">II", len(out), n) + bytes(out)


def _script_parse(
    data: bytes, progress: Callable[[int], None] | None = None
) -> tuple[list[int], list[tuple[str, int, int]]]:
    """Optimal section-A parse: (bits from each position to the end, token
    chosen there)."""
    n = len(data)
    shorts = short_matches(data, 256, 5)
    longs = longest_matches(data, 8191, 256, 3)
    inf = 1 << 60
    cost = [inf] * (n + 1)
    cost[n] = 0
    choice: list[tuple[str, int, int]] = [("lit", 1, 0)] * (n + 1)
    for i in range(n - 1, -1, -1):
        best, pick = 9 + cost[i + 1], ("lit", 1, 0)
        length, distance = shorts[i]
        for take in range(2, length + 1):
            if 12 + cost[i + take] < best:
                best, pick = 12 + cost[i + take], ("short", take, distance)
        length, distance = longs[i]
        for take in range(3, length + 1):
            bits = 18 if take <= 9 else 26
            if bits + cost[i + take] < best:
                best, pick = bits + cost[i + take], ("long", take, distance)
        cost[i], choice[i] = best, pick
        if progress and i % 65536 == 0:
            progress(i)
    return cost, choice


def script_encode(data: bytes, progress: Callable[[int], None] | None = None) -> bytes:
    """Section A's bit-flag LZ, ending with the end marker."""
    n = len(data)
    _, choice = _script_parse(data, progress)
    writer = _BitWriter()
    i = 0
    while i < n:
        kind, take, distance = choice[i]
        if kind == "lit":
            writer.bit(1)
            writer.byte(data[i])
        elif kind == "short":
            writer.bit(0)
            writer.bit(0)
            writer.bit((take - 2) >> 1)
            writer.bit((take - 2) & 1)
            writer.byte(0x100 - distance)
        else:
            writer.bit(0)
            writer.bit(1)
            field = (0x2000 - distance) << 3
            if take <= 9:
                writer.byte((field | (take - 2)) >> 8)
                writer.byte((field | (take - 2)) & 0xFF)
            else:
                writer.byte(field >> 8)
                writer.byte(field & 0xFF)
                writer.byte(take - 1)
        i += take
    writer.bit(0)
    writer.bit(1)
    writer.byte(0)
    writer.byte(0)
    writer.byte(0)
    return writer.bytes()


def map_encode(words: Sequence[int]) -> bytes:
    """Word-LZ stream for a 0x2000-word map update (``0xFFFF`` = keep)."""
    if len(words) != 0x2000:
        raise ValueError("a map update is 0x2000 words")
    heads: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    tokens: list[bytes | None] = []  # None = literal (data follows)
    literals: list[int] = []
    i = 0
    while i < len(words):
        best, best_distance = 0, 0
        if i + 1 < len(words):
            for j in reversed(heads[(words[i], words[i + 1])][-64:]):
                distance = i - j
                if distance > 0x10000:
                    break
                length = 0
                limit = min(0x2000, len(words) - i)
                while length < limit and words[j + length] == words[i + length]:
                    length += 1
                if length > best:
                    best, best_distance = length, distance
                    if length == limit:
                        break
        if i and words[i - 1] == words[i]:  # a run: distance 1
            length = 0
            while i + length < len(words) and words[i + length] == words[i - 1]:
                length += 1
            if length > best:
                best, best_distance = min(length, 0x2000), 1
        if best >= 2 or (best == 1 and best_distance <= 16):
            tokens.append(_map_copy(best, best_distance))
            step = best
        else:
            tokens.append(None)
            literals.append(words[i])
            step = 1
        for k in range(i, min(i + step, len(words) - 1)):
            heads[(words[k], words[k + 1])].append(k)
        i += step
    out, literal = bytearray(), iter(literals)
    for start in range(0, len(tokens), 8):
        group = tokens[start : start + 8]
        out.append(sum(1 << n for n, t in enumerate(group) if t is None))
        for token in group:
            out += struct.pack(">H", next(literal)) if token is None else token
    return bytes(out)


def _map_copy(length: int, distance: int) -> bytes:
    """The shortest copy token for ``length`` words from ``distance`` back."""
    if length <= 8 and distance <= 16:
        return bytes([0x80 | (length - 1) << 4 | (distance - 1)])
    if length <= 0x7F and distance <= 0x100:
        return bytes([length, distance - 1])
    if distance <= 0x100:
        return b"\x00" + struct.pack(">HB", 0x2000 | (length - 1), distance - 1)
    if length <= 0x100 and distance <= 0x2000:
        return b"\x00" + struct.pack(">HB", 0x4000 | (distance - 1), length - 1)
    return b"\x00" + struct.pack(">HH", length - 1, distance - 1)


class _BitWriter:
    """Interleaves LSB-first flag bytes with data bytes, as the decoder reads them."""

    def __init__(self) -> None:
        self.out = bytearray()
        self.flag_at = -1
        self.used = 8

    def bit(self, value: int) -> None:
        if self.used == 8:
            self.flag_at = len(self.out)
            self.out.append(0)
            self.used = 0
        if value:
            self.out[self.flag_at] |= 1 << self.used
        self.used += 1

    def byte(self, value: int) -> None:
        self.out.append(value & 0xFF)

    def bytes(self) -> bytes:
        return bytes(self.out)


# Splicing (REL-003): a rebuilt stream that keeps the original's compressed
# bytes wherever its tokens still decode to the new data, so a patch carries
# only the re-encoded stretches instead of a whole new stream.


@dataclass(frozen=True)
class _Token:
    position: int  # output offset
    literal: bool
    length: int
    distance: int


@dataclass(frozen=True)
class _Unit:
    """Original tokens between two points where a fresh flag byte starts."""

    begin: int  # compressed offset (the flag byte)
    end: int
    out_begin: int
    out_end: int
    tokens: tuple[_Token, ...]


def _decodes_to(token: _Token, data: bytes, position: int, original: int) -> bool:
    """Whether ``token``, placed at ``position`` of ``data``, outputs ``data``
    there (``original`` = the literal's byte)."""
    if position + token.length > len(data):
        return False
    if token.literal:
        return data[position] == original
    source = position - token.distance
    if source < 0:
        return False
    return all(data[source + k] == data[position + k] for k in range(token.length))


def _lz_units(block: bytes) -> list[_Unit]:
    """The flag groups of a graphics block (header included), in order."""
    compressed, size = struct.unpack_from(">II", block)
    position, end, out = 8, 8 + compressed, 0
    units = []
    while out < size and position < end:
        begin, out_begin = position, out
        tokens: list[_Token] = []
        flags = block[position]
        position += 1
        for bit in range(8):
            if out >= size:
                break
            if flags & (0x80 >> bit):
                word = (block[position] << 8) | block[position + 1]
                position += 2
                length = (word & 0xF) + 3
                tokens.append(_Token(out, False, length, 0x1000 - (word >> 4)))
            else:
                tokens.append(_Token(out, True, 1, block[position]))
                position += 1
                length = 1
            out += length
        units.append(_Unit(begin, position, out_begin, out, tuple(tokens)))
    return units


def _lz_segment(
    data: bytes,
    start: int,
    stop: int,
    align: bool,
    matches: Sequence[tuple[int, int]],
) -> bytes | None:
    """Optimal graphics-LZ tokens for ``data[start:stop]`` with ``data[:start]``
    as history, starting on a fresh flag byte; with ``align`` the token count is
    a multiple of 8 (None if impossible). ``matches`` are ``data``'s longest
    matches."""
    n, inf = stop - start, 1 << 60
    cost = [[inf] * 8 for _ in range(n + 1)]
    pick: list[list[tuple[int, int]]] = [[(0, 0)] * 8 for _ in range(n + 1)]
    cost[n] = [0] + [inf if align else 0] * 7
    for i in range(n - 1, -1, -1):
        length, distance = matches[start + i]
        for state in range(8):
            flag = 8 if state == 0 else 0
            nxt = (state + 1) % 8
            best, choice = flag + 8 + cost[i + 1][nxt], (1, 0)
            for take in range(3, min(length, n - i) + 1):
                value = flag + 16 + cost[i + take][nxt]
                if value < best:
                    best, choice = value, (take, distance)
            cost[i][state], pick[i][state] = best, choice
    if cost[0][0] >= inf:
        return None
    out, i, state = bytearray(), 0, 0
    while i < n:
        if state == 0:
            flag_at = len(out)
            out.append(0)
        take, distance = pick[i][state]
        if distance:
            out[flag_at] |= 0x80 >> state
            out += struct.pack(">H", ((0x1000 - distance) << 4) | (take - 3))
        else:
            out.append(data[start + i])
        i += take
        state = (state + 1) % 8
    return bytes(out)


def _lz_options(
    matches: Sequence[tuple[int, int]], at: int, room: int, state: int
) -> list[tuple[int, int, int]]:
    """(bytes, take, distance) of the graphics tokens at ``at`` that end within
    ``room`` bytes (distance 0 = literal); a token at state 0 pays the flag."""
    flag = 1 if state == 0 else 0
    length, distance = matches[at]
    found = [(flag + 2, take, distance) for take in range(min(length, room), 2, -1)]
    return [*found, (flag + 1, 1, 0)]


def _lz_reach(
    matches: Sequence[tuple[int, int]], start: int, stop: int
) -> tuple[list[int], list[int]]:
    """Fewest and most bytes that encode ``start``..``start + j`` in whole flag
    groups, for each j (big / -big if impossible)."""
    n, big = stop - start, 1 << 60
    lo = [[big] * 8 for _ in range(n + 1)]
    hi = [[-big] * 8 for _ in range(n + 1)]
    lo[0][0] = hi[0][0] = 0
    for i in range(n):
        for state in range(8):
            if lo[i][state] > hi[i][state]:
                continue
            nxt = (state + 1) % 8
            for cost, take, _ in _lz_options(matches, start + i, n - i, state):
                lo[i + take][nxt] = min(lo[i + take][nxt], lo[i][state] + cost)
                hi[i + take][nxt] = max(hi[i + take][nxt], hi[i][state] + cost)
    return [row[0] for row in lo], [row[0] for row in hi]


def _lz_exact(
    data: bytes,
    start: int,
    stop: int,
    target: int,
    matches: Sequence[tuple[int, int]],
) -> bytes | None:
    """Graphics-LZ tokens for ``data[start:stop]`` (history before it) that
    take exactly ``target`` bytes, start on a fresh flag byte and use a
    multiple of 8 tokens, so the original stream can resume right after them
    unshifted (None if no such encoding is found)."""
    n, big = stop - start, 1 << 60
    lo = [[big] * 8 for _ in range(n + 1)]
    hi = [[-big] * 8 for _ in range(n + 1)]
    lo[n][0] = hi[n][0] = 0
    for i in range(n - 1, -1, -1):
        for state in range(8):
            nxt = (state + 1) % 8
            for cost, take, _ in _lz_options(matches, start + i, n - i, state):
                if lo[i + take][nxt] <= hi[i + take][nxt]:
                    lo[i][state] = min(lo[i][state], cost + lo[i + take][nxt])
                    hi[i][state] = max(hi[i][state], cost + hi[i + take][nxt])
    if not lo[0][0] <= target <= hi[0][0]:
        return None
    out, i, state, left = bytearray(), 0, 0, target
    while i < n:
        nxt = (state + 1) % 8
        option = next(
            (
                o
                for o in _lz_options(matches, start + i, n - i, state)
                if lo[i + o[1]][nxt] <= left - o[0] <= hi[i + o[1]][nxt]
            ),
            None,
        )
        if option is None:
            return None
        cost, take, distance = option
        if state == 0:
            flag_at = len(out)
            out.append(0)
        if distance:
            out[flag_at] |= 0x80 >> state
            out += struct.pack(">H", ((0x1000 - distance) << 4) | (take - 3))
        else:
            out.append(data[start + i])
        i, state, left = i + take, nxt, left - cost
    return bytes(out) if len(out) == target and state == 0 else None


_REACH = 64  # units a re-encoded script gap first tries to grow over (then x4, ...)
_AHEAD = 1024  # graphics groups a re-encoded run may grow over after the change
_BACK = (0, 64, 256, 1024, 4096)  # ... and before it, tried in this order


def _fit(
    build: Callable[[Sequence[bool]], bytes],
    keep: Sequence[bool],
    gains: Sequence[int],
    limit: int,
) -> bytes:
    """Re-encode more of the kept units, those whose optimal re-encoding saves
    the most bits first, until ``build`` fits in ``limit`` bytes."""
    keep = list(keep)
    order = sorted((k for k in range(len(keep)) if keep[k]), key=lambda k: -gains[k])
    step = max(8, len(order) // 64)
    out = build(keep)
    for first in range(0, len(order), step):
        if len(out) <= limit:
            return out
        for k in order[first : first + step]:
            keep[k] = False
        out = build(keep)
    if len(out) > limit:
        raise ValueError(f"needs 0x{len(out):X} bytes; 0x{limit:X} available")
    return out


def lz_splice(original: bytes, data: bytes, limit: int | None = None) -> bytes:
    """A graphics block (header included) for ``data`` that reuses every flag
    group of ``original`` (a block of the same decoded size) still decoding to
    ``data``, and re-encodes only the others.

    Each re-encoded run takes exactly the original bytes it replaces
    (``_lz_exact``), growing over neighbouring groups (up to ``_AHEAD`` after
    and ``_BACK`` before) until that is possible, so the groups after it keep
    their offsets; if it is impossible, the run is encoded as short as it can
    be and later groups shift. If the block is still longer than ``limit``
    bytes (header excluded), the groups whose re-encoding saves the most are
    re-encoded too, without exact runs (``_fit``)."""
    size = struct.unpack_from(">I", original, 4)[0]
    if len(data) != size:
        raise ValueError("a spliced block keeps its decoded size")
    units = _lz_units(original)
    valid = [
        all(_decodes_to(t, data, t.position, t.distance) for t in u.tokens)
        for u in units
    ]
    matches = longest_matches(data, 4096, 18, 3)

    def exact(
        out: bytearray, keep: Sequence[bool], k: int, stop: int, floor: int
    ) -> int | None:
        """Re-encode from a unit at or before ``k`` (not before ``floor``) to a
        kept unit at or after ``stop`` in exactly the original bytes between
        them, so later units keep their offsets; return that kept unit."""
        synced = len(out) == units[k].begin - 8
        tried = -1
        for back in _BACK if synced else (0,):
            b = max(floor, k - back)
            if b == tried:
                break
            tried, start = b, units[b].out_begin
            ends = [e for e in range(stop, min(stop + _AHEAD, len(units))) if keep[e]]
            if not ends:
                return None
            lo, hi = _lz_reach(matches, start, units[ends[-1]].out_begin)
            for e in ends:
                target = (
                    units[e].begin - 8 - (len(out) - (units[k].begin - units[b].begin))
                )
                j = units[e].out_begin - start
                if lo[j] <= target <= hi[j]:
                    segment = _lz_exact(
                        data, start, units[e].out_begin, target, matches
                    )
                    if segment is not None:
                        del out[len(out) - (units[k].begin - units[b].begin) :]
                        out += segment
                        return e
        return None

    def build(keep: Sequence[bool], spliced: bool = True) -> bytes:
        out, k, floor = bytearray(), 0, 0
        while k < len(units):
            if keep[k]:
                out += original[units[k].begin : units[k].end]
                k += 1
                continue
            stop = k
            while stop < len(units) and not keep[stop]:
                stop += 1
            resume = exact(out, keep, k, stop, floor) if spliced else None
            if resume is None:
                segment = None
                while segment is None:
                    end = units[stop].out_begin if stop < len(units) else size
                    segment = _lz_segment(
                        data, units[k].out_begin, end, stop < len(units), matches
                    )
                    if segment is None:
                        stop += 1
                out += segment
                resume = stop
            k = floor = resume
        return bytes(out)

    out = build(valid)
    if limit is not None and len(out) > limit:
        cost = _lz_parse(data)[0]
        gains = [
            8 * (u.end - u.begin) - (cost[u.out_begin] - cost[min(u.out_end, size)])
            for u in units
        ]
        out = _fit(lambda keep: build(keep, False), valid, gains, limit)
    return struct.pack(">II", len(out), size) + out


def _script_units(stream: bytes) -> list[_Unit]:
    """Section A's tokens, cut wherever the flag bits run out, up to and
    including the end marker (its unit has ``out_end`` = the script length)."""
    position, out, flags, left = 0, 0, 0, 0
    units: list[_Unit] = []
    begin, out_begin = 0, 0
    tokens: list[_Token] = []

    def bit() -> int:
        nonlocal position, flags, left
        if left == 0:
            flags, left = stream[position], 8
            position += 1
        value = flags & 1
        flags >>= 1
        left -= 1
        return value

    while True:
        if left == 0 and tokens:
            units.append(_Unit(begin, position, out_begin, out, tuple(tokens)))
            begin, out_begin, tokens = position, out, []
        if bit():
            tokens.append(_Token(out, True, 1, stream[position]))
            position += 1
            out += 1
            continue
        if not bit():
            length = ((bit() << 1) | bit()) + 2
            distance = 0x100 - stream[position]
            position += 1
        else:
            word = (stream[position] << 8) | stream[position + 1]
            position += 2
            distance = -(((word | 0xFFFF0000) - (1 << 32)) >> 3)
            if word & 7:
                length = (word & 7) + 2
            else:
                count = stream[position]
                position += 1
                if count == 0:
                    tokens.append(_Token(out, False, 0, 0))
                    units.append(_Unit(begin, position, out_begin, out, tuple(tokens)))
                    return units
                length = count + 1
        tokens.append(_Token(out, False, length, distance))
        out += length


def _script_segment(
    data: bytes,
    start: int,
    stop: int,
    align: bool,
    end_marker: bool,
    matches: tuple[Sequence[tuple[int, int]], Sequence[tuple[int, int]]],
) -> bytes | None:
    """Optimal section-A tokens for ``data[start:stop]`` (history before it),
    starting on a fresh flag byte; with ``align`` the flag bits fill whole
    bytes; ``end_marker`` appends the end marker. ``matches`` are ``data``'s
    short and long matches."""
    shorts, longs = matches
    n, inf = stop - start, 1 << 60
    tail = 2 + 24 if end_marker else 0  # end marker: 2 flag bits, 3 bytes
    cost = [[inf] * 8 for _ in range(n + 1)]
    pick: list[list[tuple[str, int, int]]] = [[("lit", 1, 0)] * 8 for _ in range(n + 1)]
    for state in range(8):
        final = (state + 2) % 8 if end_marker else state
        cost[n][state] = tail if (final == 0 or not align) else inf
    for i in range(n - 1, -1, -1):
        s_length, s_distance = shorts[start + i]
        l_length, l_distance = longs[start + i]
        for state in range(8):
            best = 9 + cost[i + 1][(state + 1) % 8]
            choice = ("lit", 1, 0)
            for take in range(2, min(s_length, n - i) + 1):
                value = 12 + cost[i + take][(state + 4) % 8]
                if value < best:
                    best, choice = value, ("short", take, s_distance)
            for take in range(3, min(l_length, n - i) + 1):
                bits = 18 if take <= 9 else 26
                value = bits + cost[i + take][(state + 2) % 8]
                if value < best:
                    best, choice = value, ("long", take, l_distance)
            cost[i][state], pick[i][state] = best, choice
    if cost[0][0] >= inf:
        return None
    writer = _BitWriter()
    i, state = 0, 0
    while i < n:
        kind, take, distance = pick[i][state]
        _write_script_token(writer, data[start + i], kind, take, distance)
        state = (state + {"lit": 1, "short": 4, "long": 2}[kind]) % 8
        i += take
    if end_marker:
        writer.bit(0)
        writer.bit(1)
        writer.byte(0)
        writer.byte(0)
        writer.byte(0)
    return writer.bytes()


def _script_options(
    matches: tuple[Sequence[tuple[int, int]], Sequence[tuple[int, int]]],
    at: int,
    room: int,
) -> list[tuple[int, int, str, int, int]]:
    """(bits, flag bits, kind, take, distance) of the section-A tokens at
    ``at`` that end within ``room`` bytes. Long copies are tried at 3-9 bytes
    and at their full length only, which keeps the searches fast."""
    shorts, longs = matches
    found: list[tuple[int, int, str, int, int]] = []
    length, distance = longs[at]
    length = min(length, room)
    takes = [*([length] if length > 9 else []), *range(min(length, 9), 2, -1)]
    found += [(18 if t <= 9 else 26, 2, "long", t, distance) for t in takes]
    length, distance = shorts[at]
    found += [(12, 4, "short", t, distance) for t in range(min(length, room), 1, -1)]
    return [*found, (9, 1, "lit", 1, 0)]


def _script_reach(
    matches: tuple[Sequence[tuple[int, int]], Sequence[tuple[int, int]]],
    start: int,
    stop: int,
) -> tuple[list[int], list[int]]:
    """Fewest and most bits that encode ``start``..``start + j`` with whole flag
    bytes, for each j (big / -big if impossible)."""
    n, big = stop - start, 1 << 60
    lo = [[big] * 8 for _ in range(n + 1)]
    hi = [[-big] * 8 for _ in range(n + 1)]
    lo[0][0] = hi[0][0] = 0
    for i in range(n):
        choices = _script_options(matches, start + i, n - i)
        for state in range(8):
            if lo[i][state] > hi[i][state]:
                continue
            for cost, flags, _, take, _ in choices:
                nxt = (state + flags) % 8
                lo[i + take][nxt] = min(lo[i + take][nxt], lo[i][state] + cost)
                hi[i + take][nxt] = max(hi[i + take][nxt], hi[i][state] + cost)
    return [row[0] for row in lo], [row[0] for row in hi]


def _script_exact(
    data: bytes,
    start: int,
    stop: int,
    target: int,
    matches: tuple[Sequence[tuple[int, int]], Sequence[tuple[int, int]]],
) -> bytes | None:
    """Section-A tokens for ``data[start:stop]`` (history before it) that take
    exactly ``target`` bytes, starting on a fresh flag byte and filling their
    last flag byte, so the original stream resumes right after them unshifted
    (None if no such encoding is found)."""
    n, big = stop - start, 1 << 60
    lo = [[big] * 8 for _ in range(n + 1)]  # bits: data bytes x 8 + flag bits
    hi = [[-big] * 8 for _ in range(n + 1)]
    lo[n][0] = hi[n][0] = 0
    for i in range(n - 1, -1, -1):
        choices = _script_options(matches, start + i, n - i)
        for state in range(8):
            for cost, flags, _, take, _ in choices:
                nxt = (state + flags) % 8
                if lo[i + take][nxt] <= hi[i + take][nxt]:
                    lo[i][state] = min(lo[i][state], cost + lo[i + take][nxt])
                    hi[i][state] = max(hi[i][state], cost + hi[i + take][nxt])
    left = 8 * target
    if not lo[0][0] <= left <= hi[0][0]:
        return None
    writer = _BitWriter()
    i, state = 0, 0
    while i < n:
        found = next(
            (
                o
                for o in _script_options(matches, start + i, n - i)
                if lo[i + o[3]][(state + o[1]) % 8]
                <= left - o[0]
                <= hi[i + o[3]][(state + o[1]) % 8]
            ),
            None,
        )
        if found is None:
            return None
        cost, flags, kind, take, distance = found
        _write_script_token(writer, data[start + i], kind, take, distance)
        i, state, left = i + take, (state + flags) % 8, left - cost
    out = writer.bytes()
    return out if len(out) == target and state == 0 else None


def _write_script_token(
    writer: _BitWriter, literal: int, kind: str, take: int, distance: int
) -> None:
    if kind == "lit":
        writer.bit(1)
        writer.byte(literal)
    elif kind == "short":
        writer.bit(0)
        writer.bit(0)
        writer.bit((take - 2) >> 1)
        writer.bit((take - 2) & 1)
        writer.byte(0x100 - distance)
    else:
        writer.bit(0)
        writer.bit(1)
        field = (0x2000 - distance) << 3
        if take <= 9:
            writer.byte((field | (take - 2)) >> 8)
            writer.byte((field | (take - 2)) & 0xFF)
        else:
            writer.byte(field >> 8)
            writer.byte(field & 0xFF)
            writer.byte(take - 1)


def script_splice(
    stream: bytes,
    new: bytes,
    runs: Sequence[tuple[int, int, int]],
    limit: int | None = None,
) -> bytes:
    """Section A for the script ``new`` that reuses ``stream``'s compressed
    bytes (the original section) wherever they still decode to it.

    ``runs`` are (old start, old end, new start) of script stretches that are
    unchanged between the original script and ``new``; a unit is reused only
    inside one run, and only if every token decodes to ``new`` there. Each
    re-encoded gap ends where the next kept unit starts in the original
    (``_script_exact``, growing over up to ``_REACH`` more units), so kept
    units keep their offsets where possible. If the result is
    longer than ``limit``, more units are re-encoded (``_fit``).
    """
    units = _script_units(stream)

    def mapped(unit: _Unit) -> int | None:
        for old_start, old_end, new_start in runs:
            if old_start <= unit.out_begin and unit.out_end <= old_end:
                if unit.tokens[-1].length == 0 and unit.out_end != old_end:
                    return None  # the end marker must close the last run
                return unit.out_begin - old_start + new_start
        return None

    places = [mapped(u) for u in units]
    valid = [
        p is not None
        and all(
            t.length == 0
            or _decodes_to(t, new, p + t.position - u.out_begin, t.distance)
            for t in u.tokens
        )
        and (u.tokens[-1].length != 0 or p + u.out_end - u.out_begin == len(new))
        for u, p in zip(units, places, strict=True)
    ]
    matches = (short_matches(new, 256, 5), longest_matches(new, 8191, 256, 3))

    def build(keep: Sequence[bool]) -> bytes:
        out, k, at = bytearray(), 0, 0
        while k < len(units):
            if keep[k] and places[k] == at:
                out += stream[units[k].begin : units[k].end]
                at += units[k].out_end - units[k].out_begin
                k += 1
                continue
            stop = k + 1
            while stop < len(units) and not keep[stop]:
                stop += 1
            segment, end, reach, first = None, at, _REACH, stop
            while segment is None and first < len(units):
                last = min(stop + reach, len(units))
                ends = [
                    (e, place)
                    for e in range(first, last)
                    if keep[e] and (place := places[e]) is not None and place >= at
                ]
                if ends:
                    lo, hi = _script_reach(matches, at, ends[-1][1])
                for e, place in ends:
                    target = units[e].begin - len(out)
                    if lo[place - at] <= 8 * target <= hi[place - at]:
                        segment = _script_exact(new, at, place, target, matches)
                        if segment is not None:
                            stop, end = e, place
                            break
                first, reach = last, reach * 4
            while segment is None:
                last = stop >= len(units)
                place = len(new) if last else places[stop]
                if place is not None and place >= at:
                    segment = _script_segment(new, at, place, not last, last, matches)
                    end = place
                if segment is None:
                    stop += 1
            out += segment
            at = end
            k = stop
        return bytes(out)

    out = build(valid)
    if limit is not None and len(out) > limit:
        cost = _script_parse(new)[0]
        gains = [
            8 * (u.end - u.begin)
            - (cost[p] - cost[p + u.out_end - u.out_begin] if p is not None else 0)
            for u, p in zip(units, places, strict=True)
        ]
        out = _fit(build, valid, gains, limit)
    return out
