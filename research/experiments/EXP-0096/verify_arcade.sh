# RE-048 (EXP-0092): show built win-quote records with descender letters on the
# Saturn. As EXP-0089: the built US image's font goes into the post-boss dialogue
# checkpoint's cart RAM, and a built record replaces box 4's (WRAM-L 0x0022BA40;
# the same 76-byte record format and font as win quotes).
#   MC0B.PAC table 0x9B58 record 7: "I hope I get royalties, / not just a one time fee!"
#   MC02.PAC table 0xD6D8 record 5: "Never stop improving / yourself!"
set -eo pipefail
IMG=build/ref012_m8_roster_gold_us/image_a
CUE="$IMG/Marvel Super Heroes vs. Street Fighter (Japan).cue"
OUT=local/ref012/arcade/verify; mkdir -p $OUT
./invenv.sh python - <<'PY'
from pathlib import Path
from tools.disc.make_ssp import entries
from tools.disc.iso9660 import Track
from tools.disc.pac_lzss import decode_file
src = Path("build/ref012_m8_roster_gold_us/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin")
files = {e.path.split(";")[0]: e for e in entries(src)}
out = Path("local/ref012/arcade/verify")
with src.open("rb") as f:
    t = Track(f, src.stat().st_size)
    memfix = t.read(files["MEMFIX.PAC"].lsn, files["MEMFIX.PAC"].size_bytes)
    (out / "font.bin").write_bytes(memfix[0x6A558:0x6A558 + 0x32740])
    for name, table, record in (("MC0B.PAC", 0x9B58, 7), ("MC02.PAC", 0xD6D8, 5)):
        data = decode_file(t.read(files[name].lsn, files[name].size_bytes))[1]
        start = table + 76 * record
        (out / f"{name[:4]}_r{record}.hex").write_text(data[start:start + 76].hex())
print("font and records extracted")
PY
./invenv.sh python -m tools.memory.mcs_patch local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs \
  $OUT/state_font.mcs --region cart_ram --address 0278CF60 --data $OUT/font.bin
for rec in MC0B_r7 MC02_r5; do
  ./invenv.sh python -m tools.mednafen.write_trial "$CUE" $OUT/state_font.mcs $OUT/$rec.png \
    --frames 1300 --shot-at 1100 --write workraml:2BA40:$(cat $OUT/$rec.hex) > $OUT/$rec.json
done
cat $OUT/MC0B_r7.json $OUT/MC02_r5.json
