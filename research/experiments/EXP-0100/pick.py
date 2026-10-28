"""Stack whole shots (352x240) nearest after given frames into one PNG, 3 columns."""

import sys
from pathlib import Path

from tools.common.png import decode_png
from tools.memory.mcs_extract import encode_png

shots = sorted(Path("local/final/play/rec/shots").glob("f*.png"))
frames = [int(p.stem[1:]) for p in shots]
want = [int(a) for a in sys.argv[2:]]
picked = [next(p for p, f in zip(shots, frames, strict=True) if f >= w) for w in want]
w, h, cols = 352, 240, 3
rows = (len(picked) + cols - 1) // cols
W, H = w * cols, h * rows
out = bytearray(W * H * 3)
for n, p in enumerate(picked):
    img = decode_png(p.read_bytes())
    ox, oy = (n % cols) * w, (n // cols) * h
    for y in range(min(h, img.height)):
        for x in range(min(w, img.width)):
            o = ((oy + y) * W + ox + x) * 3
            out[o : o + 3] = bytes(img.pixel(x, y)[:3])
Path(sys.argv[1]).write_bytes(encode_png(W, H, bytes(out)))
print([p.name for p in picked])
