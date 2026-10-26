# Localization Plan: Character Names Across Text, Art, and Audio

Status: **provisional** (user decisions, 2026-10-25). The final policy is
`LOC-001` (`TASKS.md`). Rationale and history: `research_log.md`, 2026-10-25
entries; `EXP-0049`, `EXP-0050`.

## The Problem

The Saturn release is the Japanese one. Its art and voice use the Japanese
names. The official English we reuse comes from the US arcade, which uses the
US names. Only three roster-relevant names differ:

| Slot | Arcade English name (`0x2236BC`) | Saturn name | Where the Saturn shows it |
| --- | --- | --- | --- |
| 14 | BISON | Vega | VS screen, life bar, win screen, ending speaker labels ("Vega"); voice (user observation) |
| 15 | AKUMA | Gouki | VS screen "GOUKI" (`EXP-0050` frame `f00013144`, `0268cc2d…`), life bar, speaker label |
| 19 (boss) | CYBER-AKUMA | Mech-Gouki | VS screen "MECH-GOUKI" (`EXP-0049` frame `f00009412`, `14d5ba76…`), life bar |

The other 23 arcade English names match the Saturn's Latin names, as far as
seen. Slots 20-25 (secret characters) are excluded and not checked.

Changing text is cheap. Changing art or voice is not:
- the art formats are not decoded;
- the voice sample format and locations are unknown;
- English-name voice clips would need a source.

## Inventory of Name Surfaces (`LOC-002`, `EXP-0054`)

Found by replaying recorded states and matching on-screen sprites to font
codes (`tools/memory/vdp1_commands.py`). The main surprise: **the Saturn disc
already holds most of the US-name art and text.**

| Surface | How it is drawn | US version on the Saturn disc? | Change needed for a US variant | Cost |
| --- | --- | --- | --- | --- |
| Life bars | pre-drawn label cells in the quote font (two styles: bold `0x740`-`0x7AF`, italic `0x7B0`-`0x7FF`; VEGA `0x760`-`0x762`, MECH-GOUKI from `0x568`) | **yes**: BISON (`0x763`-`0x765`), AKUMA, CYBER-AKUMA cells sit beside the JP ones | copy the US cells over the JP cells (`glyph_copies`), or find the per-character label table and repoint it | low; **proven by replay**: BISON shows in the life bar |
| Win banner ("VEGA / RYU / WIN") | spelled from large 2×2 letter glyphs (codes `0x2E0`-`0x35F`) | letters only, so any name can be spelled | find the name string table and change the spelling (the letters exist) | low to medium (the table is not located) |
| Ending speaker labels ("Vega" over a page) | small ASCII glyphs from a table of 16-character fields in `ME.PAC` `0xB164` | **yes**: "Akuma" and "Bison" are already in that table | edit the fields, or repoint the index | low |
| Title menu "MECH-GOUKI NOW!!" | ASCII string in `MM.BIN` `0x24F03` | no, but it is plain text ("CYBER-AKUMA NOW!" fits in 16 characters) | text edit | low |
| Sound-test titles ("18.VEGA", "22.GOUKI") | ASCII fields in `MM.BIN` `0x6341`, `0x639D` | no, but plain text | text edit | low |
| VS screen ("VEGA", "MECH-GOUKI" under the portraits) | part of the VS-screen sprite mosaic, not the quote font | **unknown**. The tiles are not raw or LZSS in any file; probably in the select archives (`SEL.PAC`, `SEL2.PAC`, `SELCMP.PAC`), whose layout is not decoded | locate and decode the source, then edit or redraw | medium to high |
| Voice ("Vega") | spoken by the announcer at character select and in the win announcement (user, 2026-10-25). Sound is mixed in software by the sound program and streamed through three looping SCSP slots (`0x484`, `0x248C`), so clips never get their own slot. Every sound bank on the disc and its ADPCM decoder are decoded (`EXP-0055`, `EXP-0056`: 4-bit, 12,015.5 Hz), and `tools/audio/sound_bank.py` exports them to WAV. `CMNSE.PAC` has no names (user). Name calls (`EXP-0057`, user listening plus the mixer log): the win screen plays `PL0E` #18 (`0x286`, "Vega"). The same bank also holds #1 (`0x04F`, **"Bison"**), never seen played. `PL0F` #1 (`0x048`) says "Gouki". All three are also in the select bank (`SEL.PAC` payload 1) | Bison: **yes**, on the disc. Akuma: **unknown**; candidates `0x25A` and `0x338` | find what chooses `0x286` over `0x04F`, and switch it for the US variant. Check the Gouki candidates for "Akuma"; if there is none, source a clip and write an encoder | high, plus a sourcing question |

### Sourcing: PS1 or arcade (user question, 2026-10-25)

Most surfaces need no import: the Saturn's own font and tables already hold
the US art and text. Only the VS-screen names (if the Saturn has no US
version) and the voice would need outside assets. For those:

- **PS1 US** (`SLUS-00793`, local and hash-matched, `REF-011`) is probably the
  easier art source. PS1 TIM images are linear 4/8 bpp with colour tables,
  close to the Saturn's linear 4 bpp cells; PS1 audio is SPU ADPCM or XA, with
  well-known decoders. Its VS-screen art and voice must be located first.
  Whether it uses US names there is unverified.
- **US arcade** (`mshvsfu`): CPS2 graphics are planar and tile-mapped, and
  QSound samples are raw PCM in ROMs. That means more conversion work for
  art; audio is simple to decode. Whether the US arcade announcer says names
  is unverified.
- Either source needs a provenance decision, like the official English text.

**Recommendation:** try the PS1 first for the VS screen and voice, but only
after confirming the Saturn lacks US VS art (decode `SEL*.PAC`) and finding
which voice clip says the name.

## Current Provisional Decision: the Saturn's Names in Text

The English text follows the Saturn's art and voice. Art and audio are not
changed. Implemented in `tools/text/official_endings.py`:
- `NAME_OVERRIDES = {14: "VEGA", 15: "GOUKI"}`: the inserted names;
- `TEXT_OVERRIDES`: "Cyber Akuma" → "Mech-Gouki", then "Akuma" → "Gouki",
  applied to the ending pages, the dialogue, and the combined image's win
  quotes.

Every place this touches in the roster image (`local/end027/roster_image.json`):

| Where | Text now |
| --- | --- |
| `MM.BIN` name table, slot 14 | VEGA |
| `MM.BIN` name table, slot 15 | GOUKI |
| Gouki's win quote (`MC0F.PAC` records 7 and 15) | "There is no good or evil, / only Gouki!" |
| Wolverine's ending, page 2 (`ME.PAC` `0x2F54`) | "I know you're watching me / Gouki! You know who I am!" |
| Vega's ending, page 1 (`0x3CFC`) | "Ha! I have the technology / behind the Mech-Gouki!!" |
| Gouki's ending, pages 1-2 (`0x3DE0`) | "Gouki! Don't boast of…", "…Get ready Gouki!!" |
| Dan's ending, page 1 (`0x40D8`) | "…made a fool of me, Gouki!" |

**To revert to US names:** empty both override tables, rebuild, re-baseline
`m8_roster` and `end010`, and do one cold-boot check.

## Options for the Final Policy

| Option | Text | Art | Audio | Cost and risk |
| --- | --- | --- | --- | --- |
| A. Saturn names everywhere (current) | Vega, Gouki, Mech-Gouki | unchanged | unchanged | None beyond text. Western players may expect US names. |
| B. US names everywhere | Bison, Akuma, Cyber-Akuma | edited on every screen that shows them | announcer clips replaced | Needs art and audio reverse engineering, plus a source for the clips. |
| C. US names in text only | Bison, Akuma, Cyber-Akuma | unchanged | unchanged | Inconsistent on screen. Rejected for Vega on 2026-10-25. |

## User Direction (2026-10-25)

Offer both conventions as parallel builds, both in English: the Saturn names
(current) and the American names. Tasks:
- `LOC-002`: inventory and scope of the art and voice;
- `LOC-003`: the variant switch and two patches;
- `LOC-004`: art;
- `LOC-005`: voice, if approved;
- `LOC-006`: an in-game option, a stretch goal.

## Questions for the User (`LOC-001`)

1. A or B?
2. If B: is audio in scope, and from which source? Candidates are unverified:
   the US arcade set or a US home release. Whether one exists with these
   clips, and whether using it is acceptable, are open questions.
3. Which names should excluded characters (Norimaro, the secret characters,
   Apocalypse) use, if they ever come into scope?

## Evidence to Collect Before Deciding (smallest experiments)

1. **Art inventory.** From recorded sessions, list every screen that shows a
   regional name: character select, VS screen, life bar, win screen, ending
   speaker labels, and any other. Most frames already exist under `local/`.
2. **Audio inventory.** Listen to the character-select and VS screens for
   spoken names, for each of the three characters, and record which names are
   voiced.
3. **Only if option B:** a census of disc files for art and audio formats.
   This is new reverse engineering, not started.
