# Confirmed Discoveries

## EMU-004: Stock MSHvSF Boot Endpoint

Confidence: **CONFIRMED**

Experiment: `EXP-0001`

Stock Mednafen 1.32.1 reaches a stable, visibly rendered MSHvSF Saturn title
screen from the recorded untouched Japanese source image using the project-local
runtime root and selected BIOS aliases. The observed runtime log identifies
software `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`.

Source identity is the 13-component manifest in
`references/mshvsf/saturn_jp/README.md`; every component hash matched before and
after the run. The stock binary is
`vendor/mednafen/build/src/mednafen`, 21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`. The
canonical Japanese and North American/European BIOS aliases are unchanged from
the hashes recorded in `docs/mednafen.md`.

The ignored endpoint screenshot is
`local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0001.png`,
352x240, 22,616 bytes, SHA-256
`4c19283ec7c84b6b7690fa526e3323a7e0121efa75fa5fa9c6e88bf3c24f0d85`. The
retained ignored launch log is 4,190 bytes, SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`.

Reproduction uses the launch command and host input sequence recorded in
`research/experiments/EXP-0001/README.md`. This confirms the baseline boot
endpoint only; it does not close `EMU-005`, validate every input, or establish
that the source-image CUE warnings are irrelevant to later experiments.

This file contains only durable findings rated **CONFIRMED** by a controlled,
reproducible experiment. Environment setup, observations, hypotheses, supported
claims, visual similarity, and isolated byte matches do not qualify.

## EMU-005: Forced 4 MiB Cartridge Operation

Confidence: **CONFIRMED**

Experiment: `EXP-0002`

With the untouched MSHvSF Saturn source image and stock Mednafen 1.32.1, forcing
`ss.cart=extram4` selects `Cart: 4MiB Extended RAM` for software `T-1238G`. Three
cold launches reproduced the same selection and reached the rendered MSHvSF title
screen with `PRESS START BUTTON` after the recorded input sequence.

The source identity is the 13-component manifest in
`references/mshvsf/saturn_jp/README.md`; all component hashes matched before and
after. The stock binary is the unchanged
`vendor/mednafen/build/src/mednafen`, 21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

The successful runtime log is 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. The ignored
host captures and exact commands are recorded in `EXP-0002`. This finding is
limited to cartridge configuration and operation sufficient for the tested boot
path; it does not establish direct cartridge RAM read/write or address-boundary
behavior.

## EMU-009: Repeated Save/Load Checkpoint

Confidence: **CONFIRMED**

Experiment: `EXP-0006`

Stock Mednafen 1.32.1 saved and restored a documented MSHvSF title/menu checkpoint
in two cold observations. Each run advanced to the mode-selection screen, then
returned to the title scene after `F7`; the second run used a distinct state slot.

The ignored slot-0 state is 3,173,150 bytes with SHA-256
`e54380cfca308b1058f92d2840bde73e4c13d01bd9e4b8c864be82a3730b66db`. The ignored
slot-1 state is 3,244,032 bytes with SHA-256
`88e8945770bf26667e9006aff476b4d5dab7f7eaef93fa471ceced343dc93d80`. State files
are checkpoint artifacts, not RAM dumps, and were not decompressed or diffed.

The source image matched the 13-component manifest before and after both runs. The
stock binary and BIOS aliases were unchanged. Both run logs were 4,248 bytes with
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` and
reported `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`.

The title background and attract mode are time-dependent, so an immediate screenshot
after `F7` is required when the title scene is the checkpoint criterion. The exact
screenshots, temporary host mapping, and reproduction procedure are recorded in
`research/experiments/EXP-0006/README.md`.

## Entry Requirements

Each future entry must include:

- concise finding and scope;
- confidence label;
- experiment identifier;
- source and artifact hashes;
- exact reproduction commands and tool versions;
- predicted and observed results;
- relevant offsets, addresses, and bytes when measured;
- limitations and links to permitted evidence metadata.
