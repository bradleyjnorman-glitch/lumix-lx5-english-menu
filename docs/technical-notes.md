# Technical notes — exact v36 modification

This report documents the specific image that succeeded on one physical Japanese LX5. Do **not** extrapolate its offsets to other camera models or firmware versions.

## Baseline

- Format: Panasonic `UPD\0` update image, `0x200`-byte outer header, MT19937/parity-clocked XOR encoded body.
- Binary size: **16,254,464 bytes**.
- Official stock image SHA-256: `e59e88ac3a7ecce50a49a2c4775bf73410bfa523b0304188c00d27d86420b2a6`.
- A byte-for-byte decode/re-encode roundtrip was established before modifying the image.

## Changes

| Decoded image offset | Baseline | v36 candidate | Purpose |
| --- | --- | --- | --- |
| `0x3B4050` | `00` | `01` | Add English to Japan-region additional-language mask |
| `0x001C..0x001F` (outer header) | `01 02 01 02` | `02 02 02 02` | Advertise later version; two LE `0x0201`→`0x0202` values |
| `0x0210..0x0213` (decoded inner metadata) | `01 02 01 02` | `02 02 02 02` | Match the duplicate metadata |
| `0x0040..0x004F` | Old body MD5 | Regenerated body MD5 | Consistency with changed decoded body |

The installed program-version bytes at `0x4E00..0x4E13` are unchanged. The packaged settings/calibration data beginning `0x55C600` are byte-for-byte unchanged.

Two advertised version halfwords were changed in the **physically tested** file. While earlier offline work suggested the lower halfword drives the version gate, do not substitute a different patch and assume the result has been tested on a camera.

### Build outputs

- English SHA-256: `adf084b47e101387eee571caf8644f687b9ad717cdbd9323c0af24de2b90fb6b`.
- Stock-code rollback SHA-256: `8e15db5e3cc5d85d1c356910070622a8588c2003418a544ce962d3a575b92bfa`.

The *encoded* file changes many bytes because of the parity-clocked stream; this is expected. The decoded executable instructions were not changed. The MD5 is an internal format check, **not a guarantee of authentic firmware or safety**.

## Offline results before physical flash

- One-byte region policy change builds a Japanese+English selectable-language list in native-code replay.
- The original validation routine retained English with the changed allow-list and reset it to Japanese without the patch.
- Menu policy native replay showed an existing item 14 change from nonselectable to selectable; the exact static item-14-to-Language handler route was not fully established before flashing.
- The modified version metadata changed replayed updater status `0x30` to `0x33` and reached the installation callsite with simulated confirmation.
- Model, MD5, duplicate metadata and early section-layout checks passed native replay; deliberately invalid controls were rejected.
- A separate synthetic EEPROM-preservation replay retained a supplied language value. It did **not** emulate all physical writes or startup.

**Physical installation subsequently succeeded on one Japanese LX5.** This establishes that the tested path worked on that unit, not that the entire updater was emulated or that interrupted flashing is recoverable.