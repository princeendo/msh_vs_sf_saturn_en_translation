"""Decode the game's ADPCM sound banks and export their clips to WAV (LOC-005).

Container (EXP-0055, EXP-0056): a ``.PAC`` file starts with (u32 flag, u32 size)
pairs ended by (0, 0). The payloads follow the pairs back to back, in order. A
flag of ``0xFFFFFFFF`` marks an entry with no payload. Banks found so far:

- ``CMNSE.PAC`` payload 0: the common bank (88 clips);
- ``SEL.PAC`` payload 1 and ``SEL2.PAC`` payload 0: the same 66-clip bank;
- ``PLxx.PAC`` payload 1: each fighter's bank.

Bank layout: a u32 clip count, then one (u16 tag, u16 length) entry per clip,
then the clips concatenated in table order. The clip ID is ``tag & 0x3FF``;
``tag >> 10`` is a flag field whose meaning is unknown. A payload is taken as a
bank only if the count, table and lengths add up to its exact size.

Clip encoding: 4-bit ADPCM, high nibble first, decoded by the SH-2 routine at
``0x0600D420`` (``decode``). It is not IMA, OKI or Yamaha:

- the difference is ``step * magnitude >> 2``, with no half-step bias;
- the step is scaled by a 16.16 multiplier table at ``0x0600D46C`` and clamped
  to ``0x80``-``0x6000``;
- the predictor is not clamped;
- a clip starts at predictor 0 and step ``0x80``.

Each sample is written twice into the mix ring buffers. SCSP slots play those
at 44,100 x 2^-1 x (1 + 92/1024) = 24,031 Hz (octave -1, FNS 92), so clips play
at 12,015.5 Hz.

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

from tools.disc.iso9660 import Track, primary_volume, walk

STEP_INIT = 0x80
STEP_MIN = 0x80
STEP_MAX = 0x6000
# 16.16 step multipliers by magnitude, copied from 0x0600D46C.
MULTIPLIERS = (0xE666, 0xE666, 0xE666, 0xE666, 0x13333, 0x1999A, 0x20000, 0x26666)
SAMPLE_RATE = 12016  # 12,015.5 Hz rounded for WAV headers
NO_PAYLOAD = 0xFFFFFFFF
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


def pac_payloads(data: bytes) -> list[tuple[int, int] | None]:
    """(offset, length) of each container entry; None for an entry with none."""
    entries: list[tuple[int, int]] = []
    position = 0
    while True:
        if position + 8 > len(data):
            raise ValueError("no (0, 0) end marker")
        flag, size = struct.unpack_from(">II", data, position)
        position += 8
        if (flag, size) == (0, 0):
            break
        entries.append((flag, size))
    payloads: list[tuple[int, int] | None] = []
    for flag, size in entries:
        if flag == NO_PAYLOAD:
            payloads.append(None)
            continue
        payloads.append((position, size))
        position += size
    if position > len(data):
        raise ValueError(f"payloads end at 0x{position:X}, past the file")
    return payloads


def parse(bank: bytes) -> list[Clip]:
    """The bank's clips in table order (offsets relative to the bank)."""
    count = struct.unpack_from(">I", bank, 0)[0]
    offset = 4 + 4 * count
    if offset > len(bank):
        raise ValueError(f"a table of {count} entries does not fit the bank")
    clips: list[Clip] = []
    for index in range(count):
        tag, length = struct.unpack_from(">HH", bank, 4 + 4 * index)
        clips.append(Clip(index, tag & 0x3FF, tag >> 10, offset, length))
        offset += length
    if offset > len(bank):
        raise ValueError(f"clips end at 0x{offset:X}, past the bank (0x{len(bank):X})")
    return clips


def is_bank(payload: bytes) -> bool:
    """True if the count, table and lengths add up to the payload's exact size."""
    if len(payload) < 4:
        return False
    count: int = struct.unpack_from(">I", payload, 0)[0]
    if not 0 < count < 0x1000 or 4 + 4 * count > len(payload):
        return False
    lengths: tuple[int, ...] = struct.unpack_from(f">{2 * count}H", payload, 4)[1::2]
    return 4 + 4 * count + sum(lengths) == len(payload)


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
    bank: bytes, out_dir: Path, prefix: str, rate: int, peak: float | None
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
        name = f"{prefix}_{clip.index:02d}_id{clip.clip_id:03x}.wav"
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


def write_catalog(
    out_dir: Path, rows: Sequence[dict[str, object]], rate: int, gap: float = 0.5
) -> None:
    """``catalog.wav``: every clip in order with ``gap`` seconds of silence;
    ``catalog.tsv``: each clip's start time in it."""
    silence = bytes(2 * round(rate * gap))
    pcm = bytearray()
    lines = ["start_s\tindex\tid\tseconds"]
    for row in rows:
        with wave.open(str(out_dir / str(row["file"]))) as clip:
            frames = clip.readframes(clip.getnframes())
        lines.append(
            f"{len(pcm) / 2 / rate:.2f}\t{row['index']}\t{row['id']}\t{row['seconds']}"
        )
        pcm += frames + silence
    write_wav(out_dir / "catalog.wav", bytes(pcm), rate)
    (out_dir / "catalog.tsv").write_text("\n".join(lines) + "\n")


def disc_files(track: Path, names: Sequence[str]) -> dict[str, bytes]:
    """Files from track 01 whose names match ``names`` (``*`` for every PAC)."""
    wanted = {n.upper() for n in names}
    files: dict[str, bytes] = {}
    with track.open("rb") as stream:
        disc = Track(stream, track.stat().st_size)
        volume = primary_volume(disc)
        for entry in walk(
            disc, int(str(volume["root_lsn"])), int(str(volume["root_size"]))
        ):
            name = entry.path.split(";")[0]
            pac = name.upper().endswith(".PAC")
            if not entry.is_dir and (name.upper() in wanted or ("*" in wanted and pac)):
                files[name] = disc.read(entry.lsn, entry.size_bytes)
    return files


def export_file(
    name: str, data: bytes, out_root: Path, rate: int, peak: float | None
) -> list[dict[str, object]]:
    """Export every bank payload of one PAC file; one directory per bank."""
    banks: list[dict[str, object]] = []
    try:
        payloads = pac_payloads(data)
    except ValueError:
        return banks  # another container format (e.g. LZSS)
    for number, span in enumerate(payloads):
        if span is None or not is_bank(data[span[0] : span[0] + span[1]]):
            continue
        offset, length = span
        prefix = f"{Path(name).stem.lower()}_{number}"
        rows = export(
            data[offset : offset + length], out_root / prefix, prefix, rate, peak
        )
        (out_root / prefix / "index.json").write_text(json.dumps(rows, indent=1) + "\n")
        write_catalog(out_root / prefix, rows, rate)
        banks.append(
            {
                "file": name,
                "payload": number,
                "offset": f"0x{offset:X}",
                "clips": len(rows),
            }
        )
    return banks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--track", type=Path, default=TRACK, help="track 01 BIN")
    source.add_argument("--pac", type=Path, action="append", help="an extracted PAC")
    parser.add_argument(
        "--file",
        action="append",
        help="PAC file name on the disc; repeatable; '*' scans every PAC "
        "(default: CMNSE.PAC)",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("local/audio"))
    parser.add_argument("--rate", type=int, default=SAMPLE_RATE)
    parser.add_argument(
        "--peak",
        type=float,
        default=0.9,
        help="scale each clip's peak to this fraction of full scale (0: raw levels)",
    )
    args = parser.parse_args(argv)
    if args.pac:
        files = {p.name: p.read_bytes() for p in args.pac}
    else:
        files = disc_files(args.track, args.file or ["CMNSE.PAC"])
    banks = [
        bank
        for name, data in sorted(files.items())
        for bank in export_file(name, data, args.out_dir, args.rate, args.peak or None)
    ]
    print(json.dumps(banks, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
