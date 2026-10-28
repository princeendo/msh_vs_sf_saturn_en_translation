# TXT-005 (EXP-0091): show the two corrected digit lines on the Saturn from the
# built US image.
# 1. CONTINUE? hint 2, as EXP-0086 does: the play state with the built font in cart
#    RAM, the built MM.BIN hint records, the two nops, and a map forcing hint 2.
# 2. MC16 table 0x984C record 1 (slot 22, "before 8 am..."), as EXP-0089 does: the
#    record written over box 4 of the post-boss dialogue checkpoint (same 76-byte
#    record format and font).
set -eo pipefail
IMG=build/regression/m8_roster_gold_us/build/image_a
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
OUT=local/txt005/verify; mkdir -p $OUT
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
    mm = t.read(files["MM.BIN"].lsn, files["MM.BIN"].size_bytes)
    mc16 = decode_file(t.read(files["MC16.PAC"].lsn, files["MC16.PAC"].size_bytes))[1]
out = Path("local/txt005/verify")
(out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
(out / "hints.bin").write_bytes(mm[0x7C584:0x7C584 + 76 * 16])
for off in (0x96848, 0x9638C):
    assert mm[off:off + 2] == bytes.fromhex("0009"), hex(off)
record = mc16[0x984C + 76:0x984C + 76 * 2]
(out / "r1.hex").write_text(record.hex())
print("record 1:", record.hex())
PY
./invenv.sh python -m tools.memory.mcs_patch local/special004/play/rec/states/f00019422.mcs \
  $OUT/hint_state.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
HINTS=$(xxd -p -c 100000 $OUT/hints.bin)
MAP=$(printf "04%.0s" $(seq 16))
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/hint_state.mcs $OUT/hint2.png \
  --frames 1200 --shot-at 850 --shot-at 1180 \
  --write workramh:95084:$HINTS --write workramh:AF348:0009 \
  --write workramh:AEE8C:0009 --write workramh:AF3A0:$MAP > $OUT/hint2.json
./invenv.sh python -m tools.memory.mcs_patch local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs \
  $OUT/box_state.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/box_state.mcs $OUT/am.png \
  --frames 1300 --shot-at 1100 --write workraml:2BA40:$(cat $OUT/r1.hex) > $OUT/am.json
cat $OUT/hint2.json $OUT/am.json
