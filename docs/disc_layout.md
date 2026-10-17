# Disc Layout

## Status

The source identity is recorded. The track 01 sector format and ISO 9660 directory
are confirmed by `EXP-0016` (see Target Findings). Other properties remain
unmeasured.

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

`EXP-0016` (`CONFIRMED`; tool `tools/disc/iso9660.py`):

- **Sectors.** Track 01 is 192,346 valid Mode 1/2352 sectors. Header FAD 150-192,495
  gives LSN = index. Tracks 02-12 are audio per the CUE (not inspected).
- **Volume.** The ISO 9660 primary volume descriptor at LSN 16 reads system
  `SEGA SEGASATURN`, volume `MSH_VS_STREET_FIGHTER`, block size 2,048, and root at
  LSN 20 (20,480 bytes). The volume space size is 216,839, which exceeds track 01;
  this is unexplained.
- **Files.** The filesystem is flat: 414 files, no subdirectories, no interleave,
  and no overlapping extents. They are listed in
  `references/mshvsf/saturn_jp/iso9660_files.json`.
- **Not yet checked.** EDC/ECC and IP fields are unverified.
- **PAC files** (`EXP-0018`). `MC09.PAC` (LSN 8,246, 25,128 bytes) is a 0x18-byte
  header (word 4 = compressed length, word 5 = decompressed length) followed by an
  LZSS stream, decoded by `tools/disc/pac_lzss.py`. All 23 `MC*.PAC` files decode
  this way; 52 of 79 `.PAC` files do overall. The rest use unknown layouts.
- **Rebuild** (`EXP-0019`, `CONFIRMED`). An in-place same-size replacement of
  `MC09.PAC` with regenerated Mode 1 EDC/ECC (`tools/disc/sector.py`, which
  validates against all source sectors) boots and works in stock Mednafen. The
  game accepted a recomputed PAC header and a 14-byte zero fill.
- **`MEMFIX.PAC`** (`EXP-0022`). Header of `(0, size)` pairs terminated by
  `(0, 0)`, then 12 uncompressed entries. Entry 4 (`0x6A558`, `0x32740` bytes) is
  the quote font, byte-identical to cart RAM `0x0278CF60`. The file occupies 852
  sectors with 796 slack bytes.


Record filesystems, tracks, files, extents, offsets, sector modes, checksums, and
rebuild constraints only after measurement. Each claim needs the exact tool version,
command, input hash, output, and reproducibility notes. Do not infer the Saturn layout
from another platform or game.
