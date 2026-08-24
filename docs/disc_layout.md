# Disc Layout

## Status

The source identity is recorded, but the target disc layout has not been documented or
confirmed in this repository.

## Recorded Source Identity

The complete locally supplied source image is available at the ignored path
`local/disc_images/mshvsf_saturn_jp/`. Its CUE descriptor and all twelve BIN tracks
remain local and immutable. The tracked filename, size, and SHA-256 manifest is in
[`references/mshvsf/saturn_jp/README.md`](../references/mshvsf/saturn_jp/README.md).

Do not infer track roles, filesystem structure, sector modes, or offsets from filenames
alone. Record those properties only after inspection of this exact source image.

The platform expectations below come from the official Sega references cataloged in
`docs/references.md`. They constrain later observations but are not observations of
the MSHvSF source image.

## Platform Vocabulary

- A Game-CD program area begins with a Mode 1 track. Permitted Mode 2 Form 1/Form 2
  tracks follow it, and CD-DA tracks follow the data tracks. The format standard
  prohibits multisession Game-CDs.
- A raw sector is 2,352 bytes. Mode 1 and Mode 2 Form 1 contain 2,048 user-data bytes;
  Mode 2 Form 2 contains 2,324. An offset calculation must name which representation
  and which sector payload it uses.
- `LSN` numbers sectors from absolute time `00:02:00`; `FAD` numbers frames from
  `00:00:00`. For the documented Game-CD layout, `LSN = FAD - 150`.
- LSN 0 through 15 are the system area. The system area contains the IP used for
  startup; it is distinct from the ISO 9660 data structures that begin at LSN 16.
- ISO 9660 volume descriptors, path tables, directory records, and file extents
  describe logical files. Directory records provide an extent LSN and byte length,
  but permitted interleaving and container-specific sector storage prevent treating
  those values as universal byte offsets.
- The CD block can read TOC/session metadata, filter sectors by FAD and subheader,
  buffer them, and provide an ISO 9660 file service. This is platform capability, not
  evidence that the target application uses that service.

## Source-Image Observation Checklist

After `ENV-007` records immutable source identities, inspect without modification and
record these independently:

- descriptor/container format and the mapping of every component to tracks;
- session count, track numbers, track types, indexes, pregaps, and sector storage size;
- system-area bytes and parsed IP fields, with exact component and offset;
- ISO 9660 volume descriptors, logical block size, directories, filenames, extent
  LSNs, byte lengths, flags, and any interleave metadata;
- conversion used for each reported FAD, LSN, file extent, and container byte offset;
- gaps, trailing data, subchannel data, error-correction bytes, and other material a
  filesystem-only extraction may omit;
- exact tool version, command, input hashes, output hashes, and any warnings.

Do not call a file `IP.BIN` solely because it occupies the system area: the Sega
documents use IP for the on-disc initial program and use `SYS_IP.BIN` or `IP.BIN` in
particular development workflows. Record the target bytes and naming evidence.

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

## Target Findings

Record filesystems, tracks, files, extents, offsets, sector modes, checksums, and
rebuild constraints only after measurement. Each claim needs the exact tool version,
command, input hash, output, and reproducibility notes. Do not infer the Saturn layout
from another platform or game.
