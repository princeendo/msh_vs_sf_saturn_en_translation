"""Decode the common sound bank ``CMNSE.PAC`` and export its clips to WAV (LOC-005).

Bank layout (EXP-0055):

- ``0x10``: u32 clip count (88 on the Japanese disc);
- ``0x14``: one (u16 tag, u16 length) entry per clip. The clip ID is
  ``tag & 0x3FF`` and ``tag >> 10`` is a flag field whose meaning is unknown;
- the clips follow the table, concatenated in table order.

Clip encoding: 4-bit ADPCM, high nibble first, decoded by the SH-2 routine at
``0x0600D420`` (``decode``). It is not IMA, OKI or Yamaha: the difference is
``step * magnitude >> 2`` with no half-step bias, the step is scaled by a 16.16
multiplier table at ``0x0600D46C`` and clamped to ``0x80``-``0x6000``, and the
predictor is not clamped. A clip starts at predictor 0 and step ``0x80``. Each
sample is written twice into the mix ring buffers, which SCSP slots play at
44,100 x 2^-1 x (1 + 92/1024) = 24,031 Hz (octave -1, FNS 92), so clips play at
12,015.5 Hz.

The WAV files are game-derived data: write them under ``local/`` only
(``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import json
import struct
import wave
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.patch_image import find_entry

TABLE = 0x14
STEP_INIT = 0x80
STEP_MIN = 0x80
STEP_MAX = 0x6000
# 16.16 step multipliers by magnitude, copied from 0x0600D46C.
MULTIPLIERS = (0xE666, 0xE666, 0xE666, 0xE666, 0x13333, 0x1999A, 0x20000, 0x26666)
SAMPLE_RATE = 12016  # 12,015.5 Hz rounded for WAV headers
TRACK = Path(
    "local/disc_images/mshvsf_saturn_jp/"
    "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
)


@dataclass(frozen=True)
class Clip:
    index: int
    clip_id: int
    flags: int
    offset: int
    length: int


def parse(bank: bytes) -> list[Clip]:
    """The bank's clips in table order."""
    count = struct.unpack_from(">I", bank, 0x10)[0]
    offset = TABLE + 4 * count
    clips: list[Clip] = []
    for index in range(count):
        tag, length = struct.unpack_from(">HH", bank, TABLE + 4 * index)
        clips.append(Clip(index, tag & 0x3FF, tag >> 10, offset, length))
        offset += length
    if offset > len(bank):
        raise ValueError(f"clips end at 0x{offset:X}, past the bank (0x{len(bank):X})")
    return clips


def nibbles(data: bytes) -> Iterator[int]:
    for byte in data:
        yield byte >> 4
        yield byte & 0xF


def decode_state(
    data: bytes, predictor: int = 0, step: int = STEP_INIT
) -> tuple[list[int], int, int]:
    """(samples, predictor, step), as the routine at 0x0600D420 computes them."""
    samples: list[int] = []
    for nibble in nibbles(data):
        magnitude = nibble & 7
        difference = (step * magnitude) >> 2
        predictor += -difference if nibble & 8 else difference
        step = min(STEP_MAX, max(STEP_MIN, (step * MULTIPLIERS[magnitude]) >> 16))
        samples.append(predictor)
    return samples, predictor, step


def decode(data: bytes, predictor: int = 0, step: int = STEP_INIT) -> list[int]:
    """One sample per nibble."""
    return decode_state(data, predictor, step)[0]


def to_pcm16(samples: Sequence[int], gain: float) -> bytes:
    """Little-endian 16-bit PCM, scaled by ``gain`` and clamped."""
    return b"".join(
        struct.pack("<h", max(-32768, min(32767, round(s * gain)))) for s in samples
    )


def write_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm)


def export(
    bank: bytes, out_dir: Path, rate: int, peak: float | None
) -> list[dict[str, object]]:
    """Write one WAV per clip.

    ``peak`` scales each clip so its loudest sample is that fraction of full scale.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for clip in parse(bank):
        samples = decode(bank[clip.offset : clip.offset + clip.length])
        loudest = max((abs(s) for s in samples), default=0)
        gain = peak * 32767 / loudest if peak and loudest else 1.0
        name = f"cmnse_{clip.index:02d}_id{clip.clip_id:03x}.wav"
        write_wav(out_dir / name, to_pcm16(samples, gain), rate)
        rows.append(
            {
                "file": name,
                "index": clip.index,
                "id": f"0x{clip.clip_id:03X}",
                "flags": clip.flags,
                "offset": f"0x{clip.offset:X}",
                "length": clip.length,
                "seconds": round(len(samples) / rate, 3),
                "peak": loudest,
                "gain": round(gain, 4),
            }
        )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--track", type=Path, default=TRACK, help="track 01 BIN")
    source.add_argument("--bank", type=Path, help="an extracted CMNSE.PAC")
    parser.add_argument("--out-dir", type=Path, default=Path("local/audio/cmnse"))
    parser.add_argument("--rate", type=int, default=SAMPLE_RATE)
    parser.add_argument(
        "--peak",
        type=float,
        default=0.9,
        help="scale each clip's peak to this fraction of full scale (0: raw levels)",
    )
    args = parser.parse_args(argv)
    if args.bank:
        bank = args.bank.read_bytes()
    else:
        with args.track.open("rb") as stream:
            bank = Track(stream, args.track.stat().st_size).read(
                *find_entry(args.track, "CMNSE.PAC;1")
            )
    rows = export(bank, args.out_dir, args.rate, args.peak or None)
    (args.out_dir / "index.json").write_text(json.dumps(rows, indent=1) + "\n")
    print(json.dumps({"out_dir": str(args.out_dir), "clips": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
