# TXT-002 / TXT-003 (EXP-0087, EXP-0088): show each story record (MM.BIN 16-43) on the
# Saturn from the EXP-0081 play state, with the built US image's font in cart RAM.
# The branch after the 1-in-64 roll is forced (bf -> nop at 0x060AF228), and the
# story base literal (0x060AF250) is moved so that the winner's slot 0
# (Apocalypse) reads record R.
set -eo pipefail
IMG=build/regression/m8_roster_gold_us/build/image_a
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
OUT=local/txt002/verify; mkdir -p $OUT
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
out = Path("local/txt002/verify")
(out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
(out / "story.bin").write_bytes(mm[0x7CA44:0x7CA44 + 76 * 28])
assert mm[0x96750:0x96754] == bytes.fromhex("06095544"), mm[0x96750:0x96754].hex()
print("font and story records extracted")
PY
./invenv.sh python -m tools.memory.mcs_patch local/special004/play/rec/states/f00019422.mcs $OUT/state_font.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
STORY=$(xxd -p -c 100000 $OUT/story.bin)
for r in ${RECORDS:-$(seq 16 41)}; do
  LIT=$(printf '%08X' $((0x06095544 + (r - 16) * 76)))
  ./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/state_font.mcs $OUT/r$r.png \
    --frames 524 --write workramh:95544:$STORY --write workramh:AF228:0009 \
    --write workramh:AF250:$LIT > $OUT/r$r.json
  echo "record $r done"
done
