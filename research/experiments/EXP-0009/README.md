# EXP-0009: Observe Win-Quote Selection

Task: `REF-007`
Date: 2026-10-15
Status: DONE
Confidence: DISPROVEN

## Observation

The approved plan needs two different post-fight win quotes from the same winner in
otherwise similar scenes (C1 and C2), plus a same-quote control (C1′). What selects
the quote is unknown. It could be random, timing-dependent, opponent-dependent,
dependent on the winning teammate, or fixed.

## Hypothesis

For a fixed pre-KO checkpoint, the win quote is already determined. Changing only the
KO timing or finishing move on replay does not change which quote appears.

## Controlled Change

Part A: from a single pre-KO save state (slot 3), the only variable across replays
is the KO timing and finishing move. The point character is kept the same, and no
tag/switch is performed.

Part B (secondary, not single-variable): a later fight against a different opponent
(and possibly stage), recorded the same way.

## Prediction

If the hypothesis holds, all Part A replays show the same quote text and portrait.
If quotes differ across Part A replays, the hypothesis is `DISPROVEN`, and selection
depends on something that changes after the checkpoint (timing, RNG advance, or
finisher). That would also mean C1 and C2 can be produced from one checkpoint.

## Inputs and Provenance

- Source image: the 13-component manifest in `references/mshvsf/saturn_jp/README.md`
  (verified before and after the run).
- Emulator: stock Mednafen 1.32.1, SHA-256
  `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.
- BIOS aliases as recorded in `docs/mednafen.md`.
- Team: Ryu and Ken (player 1), M30 pad in wired macOS mode.

## Tools and Environment

- Runtime root `MEDNAFEN_HOME="$PWD/local/mednafen"`, launched from the repository
  root, with the log at ignored `local/mednafen/logs/ref007-exp0009.log`.
- Screenshots (`F9`) go to ignored `local/mednafen/snaps/`. The last pre-existing
  numbered snapshot was `-0017.png`.
- State slots 0-2 hold earlier experiment states and are not overwritten. This
  experiment uses slots 3 and 4.

## Procedure

Part A:

1. Start a fight as the Ryu/Ken team and bring the opponent to one hit from losing
   the match.
2. `Option+A` to freeze, `3` to select slot 3, `F5` to save, `F9` to screenshot,
   then `Option+R` to resume.
3. Finish the fight and press `F9` once the quote text is fully drawn. This is
   replay 0.
4. Replays 1-5: press `F7` (normal running, debugger closed), KO the opponent with a
   different timing or move each time, and press `F9` on the fully drawn quote.
   Record the finisher, the point character, and the portrait shown.

Part B:

5. Continue to the next fight against a different opponent. Repeat steps 1-3 using
   slot 4, and record the opponent and stage.

## Actual Result

The user played the session and supplied the per-replay record (fight, slot,
replay, fighter, kill move, opponent, snapshot number). Ryu was on point for every
KO, and no tag was used. The pre-KO screenshots in step 2 were not taken; the saved
states identify the checkpoints.

| State | Size | SHA-256 |
| --- | ---: | --- |
| `local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc3` (fight 1, vs Vega) | 5,386,752 | `dd08030853d0b4fa1ee1ea7973ab27aebb71f3bc1ef37d90b6e68f4c70d3b5e7` |
| `local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc4` (fight 2, vs Sakura) | 5,496,386 | `f3fd6e5a116c9cd2a167e146acad087a8bbef39b5bca4e563ec8308205fafa3d` |

Each quote screenshot is an ignored 352x240 RGB PNG named
`local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-00NN.png`. Quote IDs were assigned by visually comparing
the two-line Japanese text. To keep copyrighted text out of the repository, only
the opening characters are recorded here. Full transcription is `REF-003` work and
needs independent review.

| Fight | Slot | Replay | Kill move | Opponent | Quote | Snapshot | Size | SHA-256 |
| ---: | ---: | ---: | --- | --- | --- | --- | ---: | --- |
| 1 | 3 | 0 | Jumping Fierce | Vega | Q1 | `-0018.png` | 20,477 | `1f1a03425237d0ce5799da59c2dc770a65aa909779d597506d6bd05efdd92f02` |
| 1 | 3 | 1 | Light Punch | Vega | Q1 | `-0019.png` | 19,922 | `db27fec300daa3a09e916b4281c56ba876299d3e68cd601f401d1eeae1cb61bc` |
| 1 | 3 | 2 | Roundhouse | Vega | Q2 | `-0020.png` | 20,060 | `a6c82264ae797449df16bd75af16959612433da523274a8572f96f49396de2a2` |
| 1 | 3 | 3 | Hadouken | Vega | Q3 | `-0021.png` | 19,385 | `848dcca626df3f8f2e73f246acda32a78162d95aef3c41b8c781fc5aee61927e` |
| 1 | 3 | 4 | Crouching Medium Kick | Vega | Q4 | `-0022.png` | 19,686 | `b93758b47d1cbcb21a1fbe95a91b6d196385415e361db7ef92d537edfd55785b` |
| 1 | 3 | 5 | Shinkuu Hadouken | Vega | Q5 | `-0023.png` | 20,423 | `8e4ee132cf5b77c544fad15938a75c219fa943ff905e9d4e2a3402080e431632` |
| 2 | 4 | 0 | Air Throw | Sakura | Q3 | `-0024.png` | 20,084 | `68605cd695f1d0a409fef0171e163945048458c3b833b1e80b5c7d211157fdd3` |
| 2 | 4 | 1 | Light Punch | Sakura | Q6 | `-0025.png` | 20,527 | `92d25488904f661bf7d645b605c15d28ad94e97347cd768a4521bf22e31caed6` |
| 2 | 4 | 2 | Roundhouse | Sakura | Q2 | `-0026.png` | 20,080 | `5d4036f0676230b718fc19630b238e537be18d7ba9c5ce96d7e47215062ede25` |
| 2 | 4 | 3 | Hadouken | Sakura | Q7 | `-0027.png` | 19,857 | `c256f82263b548ad849bc0f5e667c1ab56a4c9400699307303e9407edbc660f4` |
| 2 | 4 | 4 | Crouching Medium Kick | Sakura | Q8 | `-0028.png` | 19,542 | `b78e1a4ffe025c338f6ce271774eaf4fed694242db7f03021e1a64fbb6e01e91` |
| 2 | 4 | 5 | Shinkuu Hadouken | Sakura | Q9 | `-0029.png` | 20,244 | `ccddfcf5d4f0fcf12c531ebda953b356279bf9b2e23459a6699752e4111602f6` |

Quote IDs, by opening characters: Q1 `なぜ、`, Q2 `くはっ。`, Q3 `この勝負、`,
Q4 `闘ってみて`, Q5 `もっと闘え！`, Q6 `どうした、`, Q7 `まだまだ！お前も`,
Q8 `まだまだお前達は`, Q9 `お前達と闘えて`.

Every win screen showed the same joint Ryu-and-Ken portrait and layout. A
`PRESS START` prompt was visible in some captures and not others, so it blinks. The
user observed 9 distinct quotes across 12 screens:

- Within fight 1, slot 3 produced Q1, Q1, Q2, Q3, Q4, and Q5.
- Within fight 2, slot 4 produced Q3, Q6, Q2, Q7, Q8, and Q9.
- Q2 and Q3 appeared against both opponents.
- Hadouken produced Q3 in fight 1 and Q7 in fight 2. Light Punch, Crouching Medium
  Kick, and Shinkuu Hadouken also produced different quotes across the fights.
  Roundhouse produced Q2 in both.

The launch log is ignored `local/mednafen/logs/ref007-exp0009.log`, 4,248 bytes,
reporting `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`. Source-image identity
matched the manifest before launch and again after the session, with Mednafen still
running.

## Conclusion

The hypothesis that the quote is fixed at a pre-KO checkpoint is `DISPROVEN`. One
checkpoint yielded up to six different quotes when only the KO timing and move
changed.

`SUPPORTED`: the selection depends on something that varies after the checkpoint.
Neither the kill move alone nor the opponent alone determines it: the same move gave
different quotes, and the same quotes appeared against different opponents.
Timing- or RNG-based selection is consistent with this, but is not confirmed.

Per the user's correction, every quote here is a Ryu quote, because Ryu landed every
KO.

Practical consequence: the C1 (quote A) and C2 (quote B) states can be produced
from one pre-KO checkpoint, with an identical portrait and scene. A same-quote,
different-history pair already exists across fights (Q2: snapshots 20 and 26; Q3:
21 and 24). That pairing can serve as the C1′-style control if states are saved at
those screens.

## Uncertainty and Alternatives

- Quote identity was judged visually by the agent from screenshots. It is not an
  independently reviewed transcription.
- Each replay changed both timing and move, so timing and move effects are not
  separated. No exact-input replay was attempted, so whether an identical replay
  reproduces the same quote is untested. That matters for an identical-replay C1′.
- The win screen shows a joint Ryu/Ken portrait. An earlier draft of this record
  inferred "team-voiced" quotes from that portrait and the word `俺達`. The user
  corrected this: there are no team quotes, and the quote is always delivered by
  the team member who landed the KO. Ryu landed every KO here, and Q4's `俺は`
  ("I") reads as a single speaker, so all twelve quotes are treated as Ryu's.
  Whether a Ken KO yields Ken quotes under the same portrait is user-reported but
  untested here.
- Background animation and the blinking `PRESS START` are expected noise sources in
  quote-screen state comparisons.

## Reproduction

Launch as in `EXP-0007` with log `local/mednafen/logs/ref007-exp0009.log`. Load slot
3 (or 4) with `F7`, KO the opponent with Ryu, and press `F9` on the fully drawn quote.
Compare the quote text across replays.
