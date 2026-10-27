# EXP-0084: Sega Saturn Patcher (.ssp) release patches

Task: REL-002
Status: DONE
Confidence: CONFIRMED (in-place applier; the official patcher's own code on macOS)

## Observation

Other Saturn translations ship `.ssp` patches next to xdelta. The `.ssp`
format was not documented in this repository. Two appliers exist:

- the official Sega Saturn Patcher (Knight0fDragon), Windows-only (.NET 5,
  WPF);
- `saturn-patcher-egui` (GPL-3.0), a cross-platform re-implementation of
  the apply path.

Every file this project patches keeps its size and position
(`file_size_unchanged`).

## Hypothesis

An `.ssp` is a ZIP of per-file BSDIFF40 patches plus a few text entries. A
generator that writes the entries the official patcher requires can rebuild
each release track 01 exactly when an in-place applier applies it to the
untouched image.

## Controlled Change

New `tools/disc/make_ssp.py`. It produces one `.ssp` per name variant from
the same built images as `make_patch`. The game data is unchanged.

## Prediction

Applying each `.ssp` with `saturn-patcher-egui` to a copy of the untouched
track 01 gives the release hash: `e820f6e1…` for Saturn names and
`a6572495…` for American names.

## Inputs and Provenance

- **Untouched track 01:** `8274307f…` (manifest).
- **Built images:** regression references `m8_roster_gold` and
  `m8_roster_gold_us`.
- **Sample `.ssp` made by the official tool, downloaded with the user's
  permission (2026-10-27):**
  - from `https://segaxtreme.net/resources/doom-fix-patch.287/download`,
    saved as `doom_fix_v0.3.zip`;
  - zip: 5,645,341 bytes, `1a7f26e737ec13ee4b6c82875b6c507946367df6f27d412baeb9ab8559911d70`;
  - inside: `Doom (Japan) fix patch v0.3.SSP`, 493,475 bytes,
    `98c9ffdc24ddd65d30be27b65859c5fd16b54b10ad0ad2af92cb8c9c4161041e`;
  - its README says it was made with Sega Saturn Patcher v1.3 and is applied
    with the bundled v1.95.
- **Official patcher v1.95:** `SegaSaturnPatcher.exe`, 13,759,786 bytes,
  `9b739d18637bfbe50318d30793fd384d8b7f3ce5101d468b212974f31e31085b`, from
  the same zip. It was decompiled (with the user's permission), never run:
  - `SSPStandard.dll` 2.0.8052.1922: `fc6ce5e6…`;
  - `SegaSaturnPatcherCore.dll` 1.95.8052.1922: `a33eb122…`;
  - `SegaSaturnPatcherUI.dll`: `2e5cdefe…`;
  - `DeltaQ.BsDiff.dll`: `ce1d3d82…`.
- **saturn-patcher-egui:** `https://github.com/ralfguth/saturn-patcher-egui`,
  commit `20837e065881eaa6e02a0fe568a568bab0f34ecb` (2026-06-22).

All downloads and extracted files are in the session scratchpad only, not
committed.

## Tools and Environment

- macOS 26 (Darwin 25.6.0); Python 3.12.13, zlib 1.2.12.
- cargo/rustc 1.99.1 (Homebrew `rust`): built saturn-patcher-egui with
  `cargo build --release --bin saturn-patcher`.
- .NET SDK 10.0.403 (Homebrew `dotnet`) and `ilspycmd` 11.2.0.10050.
- `/usr/bin/bspatch` (macOS system).
- `unbundle_dotnet.py` (this folder): extracts assemblies from a .NET
  single-file bundle.

## Procedure

1. **Read the sample `.ssp`:** Python `zipfile`, entry names, sizes and the
   text entries.
2. **Read the official patcher's code:**
   1. extract its assemblies:
      `python3 -I unbundle_dotnet.py SegaSaturnPatcher.exe OUT SSPStandard SegaSaturnPatcherCore SegaSaturnPatcherUI DeltaQ ISO9660 Helper`;
   2. decompile each with `ilspycmd -p -o OUT/src_NAME OUT/NAME.dll`;
   3. read `SSPStandard/SSP.cs` (load, save, apply), `BuildDisc.cs`,
      `SelectedCDInfo.cs`, `MainPage.cs` and `DeltaQ.BsDiff/Patch.cs`.
3. **Read the open applier:** `saturn-patcher-egui` `src/lib.rs`, the
   `load_ssp` and `apply_ssp` behaviour (no code copied).
4. **Map the release changes** (`changed_files`). Only whole sectors of 34
   root files differ, with no change outside files. The originals' last
   sectors are zero past the end of the file. Every original sector's EDC/ECC
   regenerates exactly.
5. **Build:** `make_ssp` for both variants (commands under Reproduction).
6. **Apply and compare hashes:**
   1. `saturn-patcher <ssp> <copy of untouched track 01>`, then `shasum -a 256`;
   2. each `._DFR` with `/usr/bin/bspatch` against the original file, then
      compare with the record's `target_sha256`.

## Actual Result

### Format (from the sample and the decompiled v1.95)

The ZIP entries:

| Entry | Content | Needed by |
| --- | --- | --- |
| `NAME._DFR` | BSDIFF40 (bzip2) patch of file `NAME` (sub-folders `DIR\NAME`) | both appliers |
| `version.txt` | assembly version; the first two parts are compared (`1.0` = old text format) | official: no entry → "Not a valid patch"; null read during build |
| `driveOrder.txt` | `PATH,INDEX,XAMODE` per ISO entry, by extent | official: read without a null check during build |
| `changes.md5` | `NAME:MD5` (upper-case hex) of each original file with a `._DFR` | egui (looked up by exact name); official v1.95 writes it, never reads it |
| `ip.bin` | 32 KiB system area | optional; the official UI replaces the image's IP.BIN with it (and checks the product number) |
| `readme.txt`, `meta.txt` | shown in the official UI | optional |

- **Other kinds:**
  - `._NEW` (new file), `._DEL` (delete), `._RPL` (whole file);
  - optional variants `._OPT`, `._OPL`, `._OEW`, `._ADD`, `._ODD`;
  - `._TRK` (audio track).
- **Sample:** the v1.3 sample uses `CHANGES._MD5` and two-field
  `driveOrder.txt` lines. Its `version.txt` is `1.3.7760.32512\r\n`.
- **Official rebuild:** the official patcher extracts the image's files and
  applies the entries. It then rebuilds the ISO in `driveOrder.txt` order,
  with the image's PVD fields and IP.BIN.
- **Official bspatch:** DeltaQ reads the standard BSDIFF40 header and three
  SharpZipLib bzip2 streams.
- **egui:** it reads only `changes.md5` and `._DFR`, and patches root files
  in place: it checks each source MD5, then writes the sectors and
  regenerates Mode 1 EDC/ECC.

### What `make_ssp` writes

- **Entries:**
  - `._DFR` for the 34 changed files;
  - `version.txt` (`1.3.7760.32512`);
  - `readme.txt`;
  - `driveOrder.txt` with all 414 entries, XA mode 0;
  - `changes.md5`;
  - `meta.txt`.
- **XA mode:** the disc's directory records carry no system-use data, so the
  XA mode is 0.
- **No `ip.bin`:** the image keeps its own, and no boot code is shipped.
- **Determinism:** fixed ZIP times; the output is byte-identical over two
  builds.
- **bsdiff:** `bsdiff40` follows Colin Percival's bsdiff 4 scan. It finds
  matches through an index of 8-byte strings (plus the current and
  same-position alignments) instead of a suffix array, and caps the backward
  extension at 4,096 bytes.
  - A first version with one whole-file add per file made a 1,577,860-byte
    patch; MEMFIX.PAC alone was 191 KB.
  - With matching: MEMFIX.PAC 10.7 KB, MVSOP0.ST2 51 KB. xdelta3 gives
    16 KB and 58 KB for those files.

### Patches

| Variant | `.ssp` | Size (bytes) | SHA-256 | egui result |
| --- | --- | --- | --- | --- |
| Saturn names | `mshvsf_saturn_en_m8_gold.ssp` | 560,868 | `eb809034c1adc21ccfc6f192d93f9fa9df3cb8c6b720ee26830971ca50ec7a61` | `e820f6e12fb54d71…` = release |
| American names | `mshvsf_saturn_en_m8_gold_us.ssp` | 560,981 | `1a7f0f32be32c81914d3b1190f17829f2411bb6f82b88f3ce2dbb87f772fd185` | `a6572495338f2d49…` = release |

- `/usr/bin/bspatch` reproduced 34 of 34 files in each variant.
- `make_ssp`'s own applier also reproduced each track.
- Both `.ssp` files are smaller than the xdelta patches (642,747 / 644,202).
  bsdiff matches against the whole original file, so moved data is stored
  as a copy.

### The official patcher's own code (follow-up, user request 2026-10-27)

The official patcher's core libraries target plain .NET 5. Only its window
needs Windows. So they were run on macOS under .NET 10.0.403 with a small
console harness (`official_build/`, `official_apply/`).
`unbundle_dotnet.py` extracts its libraries into `local/rel002/ssplib/`.

**Test A, completely unmodified code** (`official_apply`):
- **Steps:** `SelectGame` on a scratch copy of the untouched CUE, then
  `Extract`, then `new SSP(file, version, device)`; then
  `ssp.ApplyPatch(name, path, methods)` for every extracted file, with the
  names Windows would compute.
- **Results, both variants:**
  - the patch is valid, with version 1.3.7760.32512;
  - `ContainsContent` is true;
  - 414 drive-order entries are read;
  - exactly 34 files change, each from the recorded source MD5 to the
    recorded target SHA-256 (34 of 34).

**Test B, the GUI's build path** (`official_build`):
- **Steps:**
  1. `SelectedCDInfo.SelectGame("CD Image", null, cue)`;
  2. set `PatchName`;
  3. `OutputType = BIN`;
  4. `await BuildDisc.Build(out, multiFiles: true, methods)`.
- **Two macOS-only problems, found first:**
  1. **Command line:** the patcher's own command line (`BuildDisc.Parse`)
     reads absolute macOS paths as `/` switches. Given relative paths, it
     spun for over ten minutes and was stopped. Its command line also
     replaces the volume descriptor with blank, current-date values, unlike
     the GUI, so it was not used.
  2. **Path separators:** `BuildDisc` strips its work folder with
     `path.Replace(folder + "\\", "")` (four places). With the unmodified
     core, `ApplyPatch` left `MM.BIN` unchanged, and the build spun.
- **The fix:** `posix_sep.py` changes the core's single `"\\"` string
  literal to `"/"`, one byte (`#US` entry at file offset `0xA8DE`, `0x5C` to
  `0x2F`).
  - original `SegaSaturnPatcherCore.dll`: `a33eb122…`;
  - modified copy: `1607a3d40d25624cf2087133a2c28d31af4110065b30f16f86a753f8ebfb00aa`.
  - On Windows the original literal is already right.
- **Output CUE:** it was rewritten with bare file names, as
  `Split('\\').Last()` gives on Windows; Mednafen refuses absolute paths.

**Test B results** (`compare_layout.py`, against the original or the release
track 01):

| Build | Track 01 SHA-256 | Files moved / resized / different | Raw sectors different |
| --- | --- | --- | --- |
| no patch (control) | `0768faaa86c80ce0aba7d07785a5df1240f882047f1da8d5c0fbc479a8201f63` | 0 / 0 / 0 (vs. original) | 1: LSN 16 |
| Saturn-name `.ssp` | `93b46b4ee700771f47119f94db4be1e50451279e9e5fccbb501a4e2d623ad7af` | 0 / 0 / 0 (vs. `e820f6e1…`) | 1: LSN 16 |
| American-name `.ssp` | `44dea132153f4469ca67b1a8fa851360ac48bb8bbece4fa086719797f3b5bbe5` | 0 / 0 / 0 (vs. `a6572495…`) | 1: LSN 16 |

- **Track 01:** the rebuild keeps every file at its original LSN with
  identical bytes; the size is the same (452,397,792 bytes).
- **LSN 16:** the only change is the volume descriptor's volume space size,
  216,839 → 218,484 (bytes `0x50`-`0x57`). That is the rebuilt disc's total
  length with the re-laid audio.
- **Audio tracks:** the patcher re-lays them in the no-patch control as
  well, so this is its own behaviour, not the patch's.
  - each track file starts with about 145-146 more sectors before the
    original audio;
  - track 03's pregap becomes 2:00 (Redump: 1:74);
  - the files no longer equal the originals byte for byte.

**Cold boot:** `tools.mednafen.frame_capture`, silent, frames 600-7,200
every 300.
- **Saturn-name rebuild** (`local/rel002/boot_official_gold/`):
  - CAPCOM logo (`f00001200.png`);
  - "LEGENDARY / HEROES / UNITE AGAIN!!" (`f00002700.png`);
  - "AMAZING / TEAM BATTLES!" (`f00006300.png`);
  - the demo fight (`f00004800.png`);
  - the title screen (`f00007200.png`).
- **American-name rebuild** (`local/rel002/boot_official_gold_us/`): the
  same frames as the Saturn-name rebuild, byte for byte:
  - `f00002700.png` `dc3c865c…`;
  - `f00004800.png` `071fd4bf…`;
  - `f00006300.png` `ff536381…`;
  - `f00007200.png` `9277ee35…`.
  `f00006300.png` also equals the release image's cold-boot capture of the
  same caption in `EXP-0083` (`ff536381e827fa72…`).
- **Audio:** sound was muted, so CD audio from the re-laid tracks was not
  heard.

## Conclusion

**CONFIRMED:**
- applying the generated `.ssp` with the independent `saturn-patcher-egui`
  gives each release track 01 exactly;
- the macOS `bspatch` reproduces every file diff;
- the official patcher's own unmodified loader and bsdiff apply all 34 file
  patches exactly;
- its own rebuild, with one path-separator byte changed for macOS, writes
  every file at its original position with the release contents, and the
  image boots into the English attract sequence and the title screen.

## Uncertainty and Alternatives

- **Not run on Windows.** The GUI was not used, and the rebuild ran on macOS
  with the one-byte separator change. Windows behaviour is inferred from the
  same code.
- **Audio:** the official rebuild re-lays the CD audio tracks; they were not
  listened to.
- `version.txt` 1.3 is chosen so that v1.3 and later accept the patch; only
  v1.95's code was read.

## Reproduction

```bash
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --release-version 0.1.0 \
  --description "Official arcade English text; Saturn character names." \
  --out-dir build/release/m8_gold --record release/m8_roster_gold.ssp.json
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --release-version 0.1.0 \
  --description "Official arcade English text; US character names." \
  --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.ssp.json

# independent applier (patches the copy in place)
cp "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" t01.bin
saturn-patcher build/release/m8_gold/mshvsf_saturn_en_m8_gold.ssp t01.bin
shasum -a 256 t01.bin   # e820f6e12fb54d71f19c83477399e91159de2a1856e0983df93e76cec452a1c2
```

Official patcher's code on macOS (needs the .NET SDK; the libraries are
extracted from the patcher's bundle, which is not in the repository):

```bash
E=research/experiments/EXP-0084
mkdir -p local/rel002/ssplib
python3 -I $E/unbundle_dotnet.py SegaSaturnPatcher.exe local/rel002/ssplib \
  SegaSaturnPatcherCore SSPStandard ISO9660 Helper DeltaQ ICSharpCode Microsoft NAudio
# Test A (unmodified libraries)
dotnet build $E/official_apply/official_apply.csproj -c Release -o local/rel002/apply
(cd "$WORK" && dotnet "$OLDPWD/local/rel002/apply/official_apply.dll" COPY.cue \
  "$OLDPWD/build/release/m8_gold/mshvsf_saturn_en_m8_gold.ssp" "$WORK/files")
# Test B (separator byte changed in a copy of the core)
mkdir -p local/rel002/ssplib_posix && cp local/rel002/ssplib/*.dll local/rel002/ssplib_posix/
python3 -I $E/posix_sep.py local/rel002/ssplib/SegaSaturnPatcherCore.dll \
  local/rel002/ssplib_posix/SegaSaturnPatcherCore.dll
dotnet build $E/official_build/official_build.csproj -c Release -o local/rel002/build \
  -p:SspLib=$PWD/local/rel002/ssplib_posix
dotnet local/rel002/build/official_build.dll "$WORK/COPY.cue" \
  "$PWD/build/release/m8_gold/mshvsf_saturn_en_m8_gold.ssp" "$WORK/out/m8_gold.bin" multi
./invenv.sh python $E/compare_layout.py \
  "build/regression/m8_roster_gold/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  "$WORK/out/m8_gold_Track_1.bin"
```
