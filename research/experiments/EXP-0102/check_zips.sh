# REL-004: unpack the release zips into a fresh directory and apply every patch
# to the untouched track 01. Prints each patched track's SHA-256.
set -eo pipefail
VERSION=$1; ZIPS=$2; WORK=$3
SRC="local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
rm -rf "$WORK"; mkdir -p "$WORK/unz"
for kind in xdelta ssp; do unzip -q "$ZIPS/mshvsf_saturn_en_${VERSION}_$kind.zip" -d "$WORK/unz/$kind"; done
shasum -a 256 "$SRC" | cut -c1-64
for p in "$WORK"/unz/xdelta/*.xdelta; do
  xdelta3 -d -f -s "$SRC" "$p" "$WORK/out.bin"
  echo "$(basename "$p") $(shasum -a 256 "$WORK/out.bin" | cut -c1-64)"
done
for p in "$WORK"/unz/ssp/*.ssp; do
  ./invenv.sh python -c "
import sys; from pathlib import Path; from tools.disc.make_ssp import apply_ssp
apply_ssp(Path(sys.argv[1]).read_bytes(), Path(sys.argv[2]), Path(sys.argv[3]))" "$p" "$SRC" "$WORK/out.bin"
  echo "$(basename "$p") $(shasum -a 256 "$WORK/out.bin" | cut -c1-64)"
done
rm -f "$WORK/out.bin"
