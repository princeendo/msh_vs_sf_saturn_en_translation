# EXP-0102: Release 0.1.0 zips, checked from the zips

Task: REL-004
Status: DONE (the zips and their check). Publishing is recorded in `TASKS.md`.
Confidence: CONFIRMED

## Observation

`REL-004` asks for:
- one zip of every xdelta variant and one of every SSP variant, each with a
  readme of expected hashes;
- each patch, applied from the zip to the untouched image, reproducing its
  recorded track hash.

## Procedure and Actual Result

1. **Build:** `make_zips.py 0.1.0 build/release/v0.1.0`:
   - reads the committed records `release/m8_roster_gold*.json` and
     `*.ssp.json`, and checks each patch's size against them;
   - writes `README.txt` and both variants, the American names first;
   - zip members get a fixed timestamp.

   Two builds are byte-identical:

   | Zip | SHA-256 |
   | --- | --- |
   | `mshvsf_saturn_en_0.1.0_xdelta.zip` | `af5c1d6e64d7fe92…` |
   | `mshvsf_saturn_en_0.1.0_ssp.zip` | `6c94e181b17388c8…` |
2. **Check:** `check_zips.sh 0.1.0 build/release/v0.1.0 local/rel004/check`
   unpacks both zips into a new directory. It applies each patch to the
   untouched track 01 (`8274307f…`): xdelta with xdelta3 3.2.2, `.ssp` with
   `make_ssp.apply_ssp`.

   | Patch | Patched track 01 |
   | --- | --- |
   | `mshvsf_saturn_en_m8_gold_us.Track01.xdelta` | `c6f1fbd0…` (recorded) |
   | `mshvsf_saturn_en_m8_gold.Track01.xdelta` | `cdf366b3…` (recorded) |
   | `mshvsf_saturn_en_m8_gold_us.ssp` | `c6f1fbd0…` (recorded) |
   | `mshvsf_saturn_en_m8_gold.ssp` | `cdf366b3…` (recorded) |
3. **Release notes:** `release/notes_v0.1.0.md`.

## Conclusion

**CONFIRMED:** both zips are reproducible, and every patch in them rebuilds
its recorded track 01.

## Reproduction

```bash
./invenv.sh python research/experiments/EXP-0102/make_zips.py 0.1.0 build/release/v0.1.0
bash research/experiments/EXP-0102/check_zips.sh 0.1.0 build/release/v0.1.0 local/rel004/check
```
