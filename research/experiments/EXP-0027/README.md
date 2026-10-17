# EXP-0027: Ryu's Captions in Variant Team Contexts

Task: `RE-025`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED (V1, V2); V3 not tested

## Question

Is the `RE-022` disc patch, and the record mechanism confirmed in `EXP-0025` and
`EXP-0026`, shared across team contexts, or does some context use a different
table or behave differently?

The baseline (`EXP-0026`) is arcade mode, Ryu on point, Ken as partner, Ryu
landing the KO.

## Variants

One change each from the baseline.

| ID | Change | Hypothesis | Prediction |
| --- | --- | --- | --- |
| **V1** | Team order reversed: Ken on point, Ryu second; Ryu (tagged in) lands the KO | The game still selects Ryu's `MC09.PAC` table. Its RAM location may differ with team slot. | Marker text appears. The table base (`0x060F9E4A`) is recorded, whether `0x002091AC` or not, and all 16 forced records verify at that base. Record 0's placeholder names Ken (name entry 10). |
| **V2** | Partner other than Ken (Chun-Li suggested), Ryu on point and landing the KO | Same table and base as the baseline. Only the placeholder name changes. | Marker text appears with base `0x002091AC`. All 16 records verify. Record 0's placeholder expands to the partner's katakana name, equal to that partner's name-table entry (not 10). |
| V3 | Versus mode | Deferred | Port 2 has no input bindings (`local/mednafen/mednafen.cfg`), and versus mode needs two players. Recorded as an open unknown, not tested. |

## Procedure

1. Cold boot the marker image (track 01 `fd007d13…`) in the patched Mednafen
   (`fe0edb99…`).
2. One background job runs `ko_capture.py --checkpoint` twice in sequence
   (`runs/re025-v1`, then `runs/re025-v2`). Each capture ends at the first record
   pointer into work RAM low, keeps a rolling post-KO checkpoint, and records the
   table base.
3. **User gameplay** (the only manual part):
   - **V1:** arcade, pick Ken then Ryu, tag in Ryu, KO with Ryu. Wait about 5 s
     on the quote, then press F10 (reset).
   - **V2:** arcade, pick Ryu then the other partner, KO with Ryu.
4. For each variant, force indices 0-15 from its checkpoint, then run
   `verify_records.py` (base read from each state; partner-name entry reported).

**Refuted if:** a variant shows non-marker text for Ryu's KO, or any forced
record fails verification. Such a result would be recorded as a variant behaviour,
with its table base and screenshots.

## Actual Result (2026-10-17)

One cold boot of the marker image (track 01 `fd007d13…`) in the patched Mednafen
(`fe0edb99…`); log `local/mednafen/logs/re025-variants.log`. The user played two
arcade fights, with F10 (reset) in between. Everything after each KO was
automatic.

| Variant | User team | Natural record | Table base (state) | Forced 0-15 verified | Record 0 placeholder | Evidence |
| --- | --- | ---: | --- | --- | --- | --- |
| Baseline (`EXP-0026`) | Ryu, Ken | 10 | `0x002091AC` | 16/16 | ケン (entry 10) | `re024-verify.json` `f703522f…` |
| **V1** | Ken (point), Ryu (second), Ryu KO | 5 | **`0x002191AC`** | **16/16** (+ natural), IoU 1.0 for records 1-15 | ケン (entry 10) | `re025-v1-verify.json` `fc456dc75fed149f…`; checkpoint `b1c4cd6292d66dd1…`; quote `d0625d5232168339…` |
| **V2** | Ryu (point), Gouki, Ryu KO | 2 | `0x002091AC` | **16/16** (+ natural), IoU ≥ 0.9957 | **ゴウキ** (`0866 0858 085F`, entry 15) | `re025-v2-verify.json` `6eaef94e67040dd4…`; checkpoint `52bccac2cfac88fb…`; quote `d06d9b6e89730457…` |

- **V1 (team slot).** Ryu's table is decoded to a **different RAM location** when he
  is the second member: `0x002191AC`, 64 KiB above the slot-1 table at
  `0x002091AC`. In the V1 states, the WRAM-L copy at `0x002191AC` equals the
  marker table, and `0x002091AC` holds other data (Ken's, presumably;
  unverified). The pointer routine uses the base stored in the text structure
  (`0x060F9E4A`), and the disc patch works unchanged. **Variant: RAM location
  only.** M1-style RAM patches must not assume `0x002091AC`.
- **V2 (partner).** Same table and base as the baseline. Only the placeholder
  changes: it expands to the partner's name from the name table (entry 15 =
  ゴウキ, Gouki). That matches the alternate length table's value of 5 for
  entry 15, consistent with "Akuma" (`HYPOTHESIS` for the alternate mode).
- **V3 (versus mode).** Not tested. Port 2 has no bindings.
- **Anomaly (recorded, not explained).** The live read of `0x060F9E4A` that
  `ko_capture` made right after V2's pointer store returned `0x002191AC`. The
  pointer itself (`0x00209244`) and the quote-time state (`0x002091AC`) agree with
  slot 1. The word may briefly hold the other team member's table base
  (`HYPOTHESIS`). The verifier uses state values, not this live read.

## Conclusion

**`CONFIRMED`:**

- **Shared.** The same `MC09.PAC` table data, record format, selection index
  (`060AF282`), pointer routine, font, and pair glyphs serve Ryu's quotes whether
  he is the first or second team member, and with any tested partner.
- **Variant 1.** The table's RAM base depends on team slot (`0x002091AC` / `0x002191AC`).
- **Variant 2.** Record 0's placeholder shows the partner's katakana name from the
  name table.

The disc-level caption pipeline (`RE-022`) is therefore context-independent for the
tested contexts.
