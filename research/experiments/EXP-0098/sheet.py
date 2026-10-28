"""Contact sheet: the quote box (y 176-226) of each forced capture, 2 columns."""

import sys
from pathlib import Path

from tools.common.png import decode_png
from tools.memory.mcs_extract import encode_png

runs = sys.argv[2:]
X0, X1, Y0, Y1 = 16, 336, 176, 226
w, h = X1 - X0, Y1 - Y0
cols = 2
rows = (len(runs) + 1) // 2
W, H = cols * w, rows * h
out = bytearray(W * H * 3)
for n, run in enumerate(runs):
    img = decode_png(Path(run, "quote.png").read_bytes())
    ox, oy = (n % cols) * w, (n // cols) * h
    for y in range(h):
        for x in range(w):
            o = ((oy + y) * W + ox + x) * 3
            out[o : o + 3] = bytes(img.pixel(X0 + x, Y0 + y)[:3])
Path(sys.argv[1]).write_bytes(encode_png(W, H, bytes(out)))
