# Making a Release

The procedure 0.1.0 followed (`REL-004`, `EXP-0102`), written for the next
version. The examples use `0.1.1`; put your version wherever it appears.

The agent does steps 1-7. You do steps 8-10 on github.com, because `gh` on
this machine is signed in as the work account, which this project never uses.

## Before You Start

- [ ] Every open task in `TASKS.md` is done, or you have deferred it.
- [ ] The release image has been played on real hardware or in Mednafen.
- [ ] `git status` is clean, on `main`, and up to date with `origin/main`.
- [ ] `git config user.email` prints
      `13876322+princeendo@users.noreply.github.com`.
- [ ] The files in [Files You Need](../README.md#files-you-need) are in
      place, and `xdelta3 --version` reports 3.2.2.

## 1. Rebuild Everything and Check It

```bash
./invenv.sh python -m tools.regression.reference_builds \
  --driver local/mame_src/cps2.cpp --report docs/regression_report.md
```

All nine references must pass. It takes about 30 minutes. The two release
images land in `build/regression/m8_roster_gold_us/build/image_a/`
(American names) and `build/regression/m8_roster_gold/build/image_a/`
(Saturn names).

## 2. Make the Patches and Their Records

The `--record` files in `release/` are what the zips and the docs are
checked against, so they are committed.

```bash
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us \
  --record release/m8_roster_gold_us.json
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --out-dir build/release/m8_gold \
  --record release/m8_roster_gold.json
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --release-version 0.1.1 \
  --description "Official arcade English text; US character names." \
  --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.ssp.json
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --release-version 0.1.1 \
  --description "Official arcade English text; Saturn character names." \
  --out-dir build/release/m8_gold --record release/m8_roster_gold.ssp.json
```

## 3. Make the Zips, Twice

```bash
./invenv.sh python research/experiments/EXP-0102/make_zips.py 0.1.1 build/release/v0.1.1
shasum -a 256 build/release/v0.1.1/*.zip
./invenv.sh python research/experiments/EXP-0102/make_zips.py 0.1.1 build/release/v0.1.1-again
shasum -a 256 build/release/v0.1.1-again/*.zip
```

Both runs must print the same two hashes. Then delete
`build/release/v0.1.1-again`.

## 4. Check the Zips the Way a Player Would

```bash
bash research/experiments/EXP-0102/check_zips.sh 0.1.1 build/release/v0.1.1 local/rel/v0.1.1-check
```

It unpacks both zips and applies all four patches to the untouched track 01.
Each printed hash must equal the patched track 01 in `release/*.json`.

## 5. Update the Documents

- **`release/notes_v0.1.1.md`:** a new file in the shape of
  `release/notes_v0.1.0.md`. Give the new track 01 hashes, list what changed
  since the last release, and carry over the known limits.
- **`README.md`:**
  - Download: the new version, its tag link and both zip links;
  - the Patch Files table: the new patched track 01 hashes;
  - `--release-version` in the build commands;
  - remove the "(after 0.1.0)" notes, and the remark that the warning page
    is still Japanese in 0.1.0;
  - the Build the Release Patches note about 0.1.0 (keep a line on how to
    rebuild older versions from their tags).
- **`release/README.md`:** the track 01 hashes in "Steps" and "Or: Sega
  Saturn Patcher"; the expected spec, track, patch and `.ssp` hashes after
  "Commands"; `--release-version`; the change list.
- **`TASKS.md`:** a `REL-` task for the release, with the zip hashes.
- **`research_log.md`:** an entry with the commands and hashes.

## 6. Commit and Tag

Stage only the files above: never the zips, patches or images (`AGENTS.md`
rule 21).

```bash
git add README.md release/ docs/regression_report.md TASKS.md research_log.md
git commit -m "Prepare release 0.1.1"
git tag -a v0.1.1 -m "Release 0.1.1"
```

## 7. Push the Commit and the Tag

```bash
git push
git push origin v0.1.1
```

## 8. Create the Release on github.com (You)

Signed in as **princeendo**:

| Do this | What you should see |
| --- | --- |
| Open https://github.com/princeendo/msh_vs_sf_saturn_en_translation/releases and click **Draft a new release**. | The new-release form. |
| Under **Choose a tag**, pick `v0.1.1`. | "Existing tag". Do not create a new tag here. |
| Title: `0.1.1`. | |
| Paste the contents of `release/notes_v0.1.1.md` into the description. | The preview shows the hash table. |
| Drag in `build/release/v0.1.1/mshvsf_saturn_en_0.1.1_xdelta.zip` and `mshvsf_saturn_en_0.1.1_ssp.zip`. | Both files listed under the description. |
| Leave **Set as a pre-release** unticked, keep **Set as the latest release** ticked, and click **Publish release**. | The release page with two assets plus the source archives. |

## 9. Check What GitHub Is Serving (Agent)

```bash
curl -s https://api.github.com/repos/princeendo/msh_vs_sf_saturn_en_translation/releases/tags/v0.1.1 \
  | python3 -c "import json,sys; [print(a['name'], a['size'], a.get('digest')) for a in json.load(sys.stdin)['assets']]"
```

Each asset's size and `sha256:` digest must equal the zip built in step 3.

## 10. Record It

Mark the `REL-` task done with the release URL and publication time, and
add the publication to `research_log.md`. Commit and push.
