# Saturn Memory Map

## Scope And Source

This is a task-oriented subset of the master SH-2 map, not a complete Saturn memory
map. The ranges below come from Sega's *SCU User's Manual*, Third version,
`ST-97-R5-072694`, Chapter 1 section 1.2, Figures 1.3 and 1.5. Source provenance and
later SCU corrections are recorded in `docs/references.md`.

## Initial Dump Ranges

Figure 1.3 gives each work-RAM region as a one-Mbyte interval bounded by the
listed start address and the next address after the region. Normalizing those
boundaries to inclusive byte ranges gives:

| Label | Inclusive range | Size | Source |
| --- | --- | --- | --- |
| WRAM-L | `0x00200000-0x002FFFFF` | 1 MiB | Figure 1.3 boundaries `00200000H` and `00300000H` |
| WRAM-H | `0x06000000-0x060FFFFF` | 1 MiB | Figure 1.3 boundaries `06000000H` and `06100000H` |

Together these regions account for the 2 MiB main RAM stated in the *Saturn
Overview Manual*, `ST-103-R1-040194`, Chapter 2 section 2.1, Table 2.1.

These addresses are platform mappings only. They do not establish that either
region contains a caption or any other MSHvSF-specific data.

## Cache-Through Aliases

Figure 1.5 maps cache-through aliases for the same physical regions:

| Label | Inclusive alias range | Size |
| --- | --- | --- |
| WRAM-L cache-through | `0x20200000-0x202FFFFF` | 1 MiB |
| WRAM-H cache-through | `0x26000000-0x260FFFFF` | 1 MiB |

The manual warns that cached reads can return a stale value when a non-CPU device
rewrites an area, and directs such access through the cache-through area. This is an
architecture caveat, not yet a tested Mednafen debugger requirement. Do not infer
additional aliases by arithmetic without another source or experiment.

## Access Caveat

Sega's later *SCU Final Specifications: Precautions*, `ST-210-110194`, item 04,
states that SCU-DMA can use WRAM-H but cannot use WRAM-L. This does not prohibit
CPU or debugger reads of WRAM-L; it limits SCU-DMA. The planned initial raw dumps
still cover both regions through whatever stock debugger mechanism is validated
under `EMU-011` and `DBG-006`.

## Dump Discipline

Save states are checkpoints, not analyzable RAM snapshots. For comparisons, dump the
same explicit regions from each deterministic checkpoint into stable local raw files.
Record emulator version, source-image identity, checkpoint procedure, range, byte
count, output hash, command, and timestamp. Keep dumps ignored; track their metadata.

Expand the dump scope only when evidence warrants a discriminating experiment.
