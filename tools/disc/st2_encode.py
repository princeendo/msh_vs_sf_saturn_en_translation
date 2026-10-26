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


def lz_encode(data: bytes) -> bytes:
    """Graphics LZ: header (u32 compressed size, u32 size) plus the token stream."""
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


def script_encode(data: bytes, progress: Callable[[int], None] | None = None) -> bytes:
    """Section A's bit-flag LZ, ending with the end marker."""
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
