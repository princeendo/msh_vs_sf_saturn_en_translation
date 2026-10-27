# SPECIAL-004 (EXP-0089): show the built MC13 record 107 (Mech-Gouki's post-boss
# line) on the Saturn. From the EXP-0039 checkpoint before Ryu's post-boss
# dialogue, the built US image's font goes into cart RAM and the built record 107
# replaces box 4's record (WRAM-L 0x0022BA40, MC13 decoded 0xBA40 = record 87).
set -eo pipefail
IMG=build/regression/m8_roster_gold_us/build/image_a
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
STATE=local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs
OUT=local/sp004/verify; mkdir -p $OUT
./invenv.sh python - <<'PY'
from pathlib import Path
from tools.disc.make_ssp import entries
from tools.disc.iso9660 import Track
from tools.disc.pac_lzss import decode_file
src = Path("build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin")
files = {e.path.split(";")[0]: e for e in entries(src)}
with src.open("rb") as f:
    t = Track(f, src.stat().st_size)
    memfix = t.read(files["MEMFIX.PAC"].lsn, files["MEMFIX.PAC"].size_bytes)
    mc13 = decode_file(t.read(files["MC13.PAC"].lsn, files["MC13.PAC"].size_bytes))[1]
out = Path("local/sp004/verify")
(out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
record = mc13[0xA06C + 76 * 107:0xA06C + 76 * 108]
(out / "r107.hex").write_text(record.hex())
print("record 107:", record.hex())
PY
./invenv.sh python -m tools.memory.mcs_patch $STATE $OUT/state_font.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/state_font.mcs $OUT/box4.png \
  --frames ${FRAMES:-1500} ${SHOTS:---shot-at 900 --shot-at 1100 --shot-at 1300} \
  --write workraml:2BA40:$(cat $OUT/r107.hex) > $OUT/box4.json
cat $OUT/box4.json
