# Saturn Memory Map

## Initial Dump Ranges

The project operating contract supplies these initial regions for controlled memory
dumps:

| Label | Inclusive range | Validation |
| --- | --- | --- |
| WRAM-L | `0x00200000-0x002FFFFF` | Source validation pending |
| WRAM-H | `0x06000000-0x060FFFFF` | Source validation pending |

These labels and ranges are starting instructions, not a complete or independently
validated Saturn memory map. Do not add other regions without a cited source or
reproducible project evidence.

## Dump Discipline

Save states are checkpoints, not analyzable RAM snapshots. For comparisons, dump the
same explicit regions from each deterministic checkpoint into stable local raw files.
Record emulator version, source-image identity, checkpoint procedure, range, byte
count, output hash, command, and timestamp. Keep dumps ignored; track their metadata.

Expand the dump scope only when evidence warrants a discriminating experiment.
