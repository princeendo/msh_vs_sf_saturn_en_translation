# Mednafen Research Guide

## Required Order

Use stock Mednafen first. Select and record an upstream release, then document its
URL, version or revision, source hash, host environment, build options, dependencies,
and exact build commands.

Validate the task-required stock capabilities before proposing modifications:

- boot the target using a legally obtained BIOS and source image;
- configure the required 4 MB RAM cartridge;
- verify fightpad input;
- capture screenshots and save states;
- evaluate interactive debugger access.

Record observed behavior and limitations; do not infer capabilities from another
version or platform.

## Local State

Keep runtime configuration, BIOS files, save states, screenshots, memory dumps,
traces, and emulator binaries in ignored local paths. Track only sanitized settings,
provenance, hashes, commands, and factual results.

## Modification Gate

Do not modify Mednafen before `EMU-012` is complete and `EMU-020` documents why stock
Mednafen is insufficient. If modification is authorized, make the smallest useful
change and preserve upstream provenance, rationale, patch, and reproducible build
steps in `vendor/mednafen/`.
