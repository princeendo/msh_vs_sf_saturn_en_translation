# UI-006 / EXP-0086: show each official hint's two pages on the Saturn from a play
# state, with the built US image's font transplanted into the state's cart RAM.
set -eo pipefail
IMG=build/regression/m8_roster_gold_us/build/image_a
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
OUT=local/ui006/verify; mkdir -p $OUT
./invenv.sh python - <<'PY'
from pathlib import Path
from tools.disc.make_ssp import entries
from tools.disc.iso9660 import Track
src = Path("build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin")
files = {e.path.split(";")[0]: e for e in entries(src)}
with src.open("rb") as f:
    t = Track(f, src.stat().st_size)
    memfix = t.read(files["MEMFIX.PAC"].lsn, files["MEMFIX.PAC"].size_bytes)
    mm = t.read(files["MM.BIN"].lsn, files["MM.BIN"].size_bytes)
out = Path("local/ui006/verify")
(out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
(out / "hints.bin").write_bytes(mm[0x7C584:0x7C584 + 76 * 16])
for off in (0x96848, 0x9638C):
    assert mm[off:off + 2] == bytes.fromhex("0009"), hex(off)
print("font and hints extracted")
PY
./invenv.sh python -m tools.memory.mcs_patch local/special004/play/rec/states/f00019422.mcs $OUT/state_font.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
HINTS=$(xxd -p -c 100000 $OUT/hints.bin)
for k in 0 1 2 3 4 5 6 7; do
  v=$(printf '%02x' $((2*k)))
  MAP=$(printf "$v%.0s" $(seq 16))
  ./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/state_font.mcs $OUT/hint$k.png \
    --frames 1200 --shot-at 850 --shot-at 1180 \
    --write workramh:95084:$HINTS --write workramh:AF348:0009 \
    --write workramh:AEE8C:0009 --write workramh:AF3A0:$MAP > $OUT/hint$k.json
  echo "hint $k done"
done
