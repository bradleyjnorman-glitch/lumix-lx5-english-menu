#!/usr/bin/env python3
"""Reproducible offline patcher for one verified Panasonic DMC-LX5 v2.0 image.

Does not contain Panasonic firmware and never communicates with a camera.
Only accepts a stock image with the exact SHA-256 used for the 2026-11-17
successful Japanese LX5 -> English menu conversion.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

STOCK_SHA256 = 'e59e88ac3a7ecce50a49a2c4775bf73410bfa523b0304188c00d27d86420b2a6'
ENGLISH_SHA256 = 'adf084b47e101387eee571caf8644f687b9ad717cdbd9323c0af24de2b90fb6b'
ROLLBACK_SHA256 = '8e15db5e3cc5d85d1c356910070622a8588c2003418a544ce962d3a575b92bfa'
SIZE = 16_254_464
HEADER = 0x200
SEED = bytes.fromhex('0c9ef8efe6cd114f1f441e3e6735c285')
LANGUAGE_MASK_OFFSET = 0x3B4050
VERSION_OUTER_OFFSET = 0x1C
VERSION_INNER_OFFSET = 0x210
OLD_VERSION_BYTES = bytes.fromhex('01020102')
NEW_VERSION_BYTES = bytes.fromhex('02020202')
PROGRAM_VERSION = slice(0x4E00, 0x4E14)
SETTINGS_START = 0x55C600
DIGEST = slice(0x40, 0x50)
PARITY16 = bytes((i.bit_count() & 1 for i in range(65536)))


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def init_mt19937_by_array(key: tuple[int, ...]) -> list[int]:
    """MT19937 init_by_array used by Panasonic's parity-clocked stream."""
    mt = [0] * 624
    mt[0] = 19650218
    for k in range(1, 624):
        mt[k] = (1812433253 * (mt[k - 1] ^ (mt[k - 1] >> 30)) + k) & 0xFFFFFFFF
    i, j = 1, 0
    for _ in range(max(624, len(key))):
        mt[i] = ((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525)) + key[j] + j) & 0xFFFFFFFF
        i += 1
        j += 1
        if i >= 624:
            mt[0] = mt[623]
            i = 1
        if j >= len(key):
            j = 0
    for _ in range(623):
        mt[i] = ((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941)) - i) & 0xFFFFFFFF
        i += 1
        if i >= 624:
            mt[0] = mt[623]
            i = 1
    mt[0] = 0x80000000
    return mt


def mt19937_stream(key: tuple[int, ...]):
    mt = init_mt19937_by_array(key)
    mag = (0, 0x9908B0DF)
    while True:
        for k in range(227):
            y = (mt[k] & 0x80000000) | (mt[k + 1] & 0x7FFFFFFF)
            mt[k] = mt[k + 397] ^ (y >> 1) ^ mag[y & 1]
        for k in range(227, 623):
            y = (mt[k] & 0x80000000) | (mt[k + 1] & 0x7FFFFFFF)
            mt[k] = mt[k - 227] ^ (y >> 1) ^ mag[y & 1]
        y = (mt[623] & 0x80000000) | (mt[0] & 0x7FFFFFFF)
        mt[623] = mt[396] ^ (y >> 1) ^ mag[y & 1]
        for y in mt:
            y ^= y >> 11
            y ^= (y << 7) & 0x9D2C5680
            y ^= (y << 15) & 0xEFC60000
            y ^= y >> 18
            yield y & 0xFFFFFFFF


def transform(source: bytes, *, decode: bool) -> bytes:
    if len(source) != SIZE or source[:4] != b'UPD\x00':
        raise ValueError('Not the exact-size LX5 UPD image')
    words = array.array('I')
    words.frombytes(source[HEADER:])
    if sys.byteorder != 'little':
        words.byteswap()
    result = array.array('I', [0]) * len(words)
    next_word = mt19937_stream(struct.unpack('<4I', SEED)).__next__
    prev = 0
    for index, value in enumerate(words):
        if PARITY16[(prev & 0xFFFF) ^ (prev >> 16)]:
            next_word()
        updated = value ^ next_word()
        result[index] = updated
        prev = updated if decode else value
    if sys.byteorder != 'little':
        result.byteswap()
    return source[:HEADER] + result.tobytes()


def decode(source: bytes) -> bytes:
    return transform(source, decode=True)


def encode(plain: bytes) -> bytes:
    updated = bytearray(plain)
    updated[DIGEST] = hashlib.md5(updated[HEADER:]).digest()
    return transform(bytes(updated), decode=False)


def load_stock(path: Path) -> bytes:
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as archive:
            matches = [n for n in archive.namelist() if n.lower().endswith('lx5__v20.bin')]
            if len(matches) != 1:
                raise ValueError('ZIP must contain exactly one LX5__V20.BIN')
            original = archive.read(matches[0])
    elif path.suffix.lower() == '.bin':
        original = path.read_bytes()
    else:
        raise ValueError('Provide Panasonic official LX5__V20.zip or extracted .BIN (not .EXE)')
    if sha256(original) != STOCK_SHA256:
        raise ValueError('Original firmware SHA-256 not recognised. Refusing to patch.')
    return original


def build(stock_encoded: bytes, original_plain: bytes, *, english: bool) -> bytes:
    patched = bytearray(original_plain)
    if patched[VERSION_OUTER_OFFSET:VERSION_OUTER_OFFSET+4] != OLD_VERSION_BYTES:
        raise ValueError('Unexpected outer version metadata')
    if patched[VERSION_INNER_OFFSET:VERSION_INNER_OFFSET+4] != OLD_VERSION_BYTES:
        raise ValueError('Unexpected inner version metadata')
    if patched[LANGUAGE_MASK_OFFSET:LANGUAGE_MASK_OFFSET+4] != b'\0\0\0\0':
        raise ValueError('Unexpected original Japanese language policy')
    patched[VERSION_OUTER_OFFSET:VERSION_OUTER_OFFSET+4] = NEW_VERSION_BYTES
    patched[VERSION_INNER_OFFSET:VERSION_INNER_OFFSET+4] = NEW_VERSION_BYTES
    if english:
        patched[LANGUAGE_MASK_OFFSET] = 1
    result = encode(bytes(patched))
    output_plain = decode(result)
    if output_plain[:0x40] != patched[:0x40] or output_plain[0x50:] != patched[0x50:]:
        raise AssertionError('Unexpected decoded output differences')
    if output_plain[DIGEST] != hashlib.md5(output_plain[HEADER:]).digest():
        raise AssertionError('MD5 mismatch')
    if output_plain[0x0C:0x2C] != output_plain[0x200:0x220]:
        raise AssertionError('Duplicate metadata mismatch')
    if output_plain[PROGRAM_VERSION] != original_plain[PROGRAM_VERSION]:
        raise AssertionError('Installed firmware program version changed')
    if output_plain[SETTINGS_START:] != original_plain[SETTINGS_START:]:
        raise AssertionError('Packaged settings or calibration changed')
    expected_hash = ENGLISH_SHA256 if english else ROLLBACK_SHA256
    if sha256(result) != expected_hash:
        raise AssertionError('Output differs from the original v36 test image')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('official', type=Path, help='Official Panasonic LX5__V20.ZIP or LX5__V20.BIN')
    parser.add_argument('--out', type=Path, default=Path('output'), help='Output directory')
    args = parser.parse_args()
    stock = load_stock(args.official)
    original_plain = decode(stock)
    if original_plain[DIGEST] != hashlib.md5(original_plain[HEADER:]).digest():
        raise ValueError('Original decoded-body MD5 is invalid')
    if encode(original_plain) != stock:
        raise ValueError('Original image did not re-encode byte-for-byte')
    assert original_plain[0x0C:0x2C] == original_plain[0x200:0x220]
    targets = {
        'english': build(stock, original_plain, english=True),
        'stock_code_rollback': build(stock, original_plain, english=False),
    }
    manifest = {'original_sha256': STOCK_SHA256,
                'warning': 'Only one Japanese LX5 physically tested. Flashing is at your risk; no proven emergency recovery.',
                'outputs': {name: sha256(data) for name, data in targets.items()}}
    for name, data in targets.items():
        p = args.out / name / 'LX5__V20.BIN'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        assert sha256(p.read_bytes()) == manifest['outputs'][name]
        print(f'{p}: {manifest["outputs"][name]}')
    (args.out / 'checksums.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Generated exact v36 images. No camera or SD card was modified.')


if __name__ == '__main__':
    main()