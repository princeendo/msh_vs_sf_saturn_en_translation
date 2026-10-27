from __future__ import annotations

import pytest

from tests.unit.test_mcs_extract import make_state, pattern
from tools.memory.mcs_extract import (
    REGIONS,
    StateFormatError,
    extract_region,
    parse_state,
)
from tools.memory.mcs_patch import patch_region


def cart_state(big_endian: bool = False) -> bytes:
    half = REGIONS["cart_ram"].size // 2
    return make_state(
        {
            "MAIN": {"X": b"\x01\x02"},
            "CART_EXTRAM": {"LO": pattern(half), "HI": bytes(half)},
        },
        big_endian=big_endian,
    )


@pytest.mark.parametrize("big_endian", [False, True])
def test_patch_region_writes_across_variables_and_keeps_the_rest(
    big_endian: bool,
) -> None:
    raw = cart_state(big_endian)
    spec = REGIONS["cart_ram"]
    address = spec.base_address + spec.size // 2 - 4  # spans LO and HI
    data = bytes.fromhex("11223344556677889900")
    patched = parse_state(patch_region(raw, "cart_ram", address, data))
    before = extract_region(parse_state(raw), spec, "saturn")
    after = extract_region(patched, spec, "saturn")
    offset = address - spec.base_address
    assert after[offset : offset + len(data)] == data
    assert after[:offset] == before[:offset]
    assert after[offset + len(data) :] == before[offset + len(data) :]
    assert patched.sections["MAIN"] == {"X": b"\x01\x02"}


def test_patch_region_refuses_unaligned_or_outside_writes() -> None:
    raw = cart_state()
    base = REGIONS["cart_ram"].base_address
    with pytest.raises(StateFormatError, match="aligned"):
        patch_region(raw, "cart_ram", base + 1, b"\x00\x00")
    with pytest.raises(StateFormatError, match="outside"):
        patch_region(raw, "cart_ram", base - 2, b"\x00\x00")
