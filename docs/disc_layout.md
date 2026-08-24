# Disc Layout

## Status

The target disc layout has not been documented or confirmed in this repository.

## Source Inventory

Before inspection, record every component of the source image with:

- filename;
- byte size;
- SHA-256;
- release description;
- container or track role only when established by metadata or inspection.

Treat source components as immutable. Do not commit them. Extraction and patch tools
must read from the source and write to distinct ignored paths; derived images belong
under `build/`.

## Future Findings

Record filesystems, tracks, files, extents, offsets, sector modes, checksums, and
rebuild constraints only after measurement. Each claim needs the exact tool version,
command, input hash, output, and reproducibility notes. Do not infer the Saturn layout
from another platform or game.
