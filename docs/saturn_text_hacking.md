# Saturn Text Investigation Guide

Confirmed win-quote storage, font, selection, and disc-source behavior is recorded in
`docs/discoveries.md` and summarized in `docs/text_system.md` and
`docs/agent_briefing.md`. The workflow below is how each was established. Use it
again for any text surface not yet investigated (endings, menus, other characters).

## Initial Workflow

1. Reach a deterministic Ryu post-fight checkpoint.
2. Capture comparable dumps for the supplied initial WRAM ranges.
3. Form one testable hypothesis about the target caption's representation or
   lifecycle.
4. Change one variable and predict an observable result.
5. Record the result with exact addresses or offsets only when measured.
6. Promote a finding only after a controlled reproduction.

Do not assume character encoding, terminators, compression, pointer format, buffer
location, transfer path, font layout, or renderer behavior. Do not transfer such
facts from CPS-II, PlayStation, or XvSF without a specific experiment.

For every memory or binary edit, record original and modified bytes, address or file
offset, purpose, expected behavior, observed behavior, and checkpoint evidence.
