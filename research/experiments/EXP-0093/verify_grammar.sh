# TXT-004 (EXP-0093): build the American-names image with --fix-grammar and show
# the corrected CONTINUE? hint pages on the Saturn. Pages 2k and 2k+1 are hint k;
# the corrected pages are 0, 1, 4, 8 and 12, so hints 0, 2, 4 and 6 are forced, as
# EXP-0086 does (play state, built font in cart RAM, built MM.BIN hint records,
# the two nops, and an index map of sixteen 2k bytes).
set -eo pipefail
SPEC=${SPEC:-local/txt004/spec/m8_roster_gold_us.json}
IMG=build/txt004/image_a
./invenv.sh python -m tools.text.caption_compiler "$SPEC" \
  --source-dir local/disc_images/mshvsf_saturn_jp \
  --candidates data/text/font_candidates.json --out-dir build/txt004 > /dev/null
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
OUT=local/txt004/verify; mkdir -p $OUT
./invenv.sh python - <<'PY'
from pathlib import Path
from tools.disc.make_ssp import entries
from tools.disc.iso9660 import Track
src = Path("build/txt004/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin")
files = {e.path.split(";")[0]: e for e in entries(src)}
with src.open("rb") as f:
    t = Track(f, src.stat().st_size)
    memfix = t.read(files["MEMFIX.PAC"].lsn, files["MEMFIX.PAC"].size_bytes)
    mm = t.read(files["MM.BIN"].lsn, files["MM.BIN"].size_bytes)
out = Path("local/txt004/verify")
(out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
(out / "hints.bin").write_bytes(mm[0x7C584:0x7C584 + 76 * 16])
for off in (0x96848, 0x9638C):
    assert mm[off:off + 2] == bytes.fromhex("0009"), hex(off)
print("font and hints extracted")
PY
./invenv.sh python -m tools.memory.mcs_patch local/special004/play/rec/states/f00019422.mcs \
  $OUT/state_font.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
HINTS=$(xxd -p -c 100000 $OUT/hints.bin)
for k in 0 2 4 6; do
  v=$(printf '%02x' $((2*k)))
  MAP=$(printf "$v%.0s" $(seq 16))
  ./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/state_font.mcs $OUT/hint$k.png \
    --frames 1200 --shot-at 850 --shot-at 1180 \
    --write workramh:95084:$HINTS --write workramh:AF348:0009 \
    --write workramh:AEE8C:0009 --write workramh:AF3A0:$MAP > $OUT/hint$k.json
  echo "hint $k done"
done
