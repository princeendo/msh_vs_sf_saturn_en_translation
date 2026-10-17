# EXP-0027: Ryu's Captions in Variant Team Contexts

Task: `RE-025`
Date: 2026-10-17
Status: IN_PROGRESS (pre-registered)
Confidence: HYPOTHESIS

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
