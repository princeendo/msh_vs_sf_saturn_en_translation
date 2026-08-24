# Mednafen Agent Interface

## Status

**Deferred.** No custom Mednafen agent interface is specified or authorized.

Complete `EMU-012` first. Only if `EMU-020` then documents a concrete insufficiency
in stock Mednafen may an interface be designed or implemented.

## Future Design Inputs

If the gate is satisfied, record:

- the exact blocked workflow and stock behavior;
- the minimum operations required by a controlled experiment;
- synchronization and deterministic-checkpoint requirements;
- command, response, error, timeout, and versioning semantics;
- security and filesystem boundaries;
- a reproducible test using synthetic or legally distributable inputs.

Do not invent protocol commands, memory addresses, transport details, or emulator
hooks before those requirements are observed.
