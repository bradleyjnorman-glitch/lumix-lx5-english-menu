# Panasonic Lumix DMC-LX5: Japanese-to-English menu unlock

A **tested, minimal firmware patch** that enables English menus on a Japanese-market Panasonic Lumix **DMC-LX5** running Panasonic firmware **v2.0**.

**Confirmed on one physical Japanese-market LX5 on 17 November 2026:** the modified update installed, the camera displayed English menus, English survived power-off/power-on, and the camera operated with its normal SD card afterwards.

**Not a Panasonic release. Not guaranteed on other units. A failed firmware flash may permanently disable your camera. There is no verified LX5 emergency recovery method.**

## What changes

The patch starts with the official Panasonic LX5 v2.0 firmware. It does **not add new executable code**. It:

1. Enables English (`1`) alongside Japanese in the existing Japanese-region language allow-list: decoded offset `0x3B4050`, `00` → `01`.
2. Changes two existing **advertised version** metadata halfwords from `0x0201` to `0x0202`, in both the outer and matching decoded inner headers. This allowed a camera already running v2.0 to offer the update. The camera still displays program version **2.0**.
3. Regenerates the update-header MD5 and re-encodes the package using the original Panasonic format.

All original executable instructions, packaged factory-calibration data, user-settings templates and installed program-version bytes remain unchanged. This does **not** remove the LX5's normal language validation: it permits English under the original validator.

## Why this repository has no firmware `.BIN`

Panasonic's original firmware is proprietary. This project distributes only an **offline patching script** and documentation. Download your own original image directly from Panasonic:

- [Official Panasonic Global LX5 firmware page](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/LX5/index.html)
- [Official Panasonic LX5 download and update instructions](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/LX5/index2.html)

The **Mac ZIP** download contains `LX5__V20.BIN` and can be used on Windows too. The script accepts either that ZIP or its extracted `.BIN`. It deliberately does not execute downloaded `.EXE` files.

**Required original BIN SHA-256:**

```text
e59e88ac3a7ecce50a49a2c4775bf73410bfa523b0304188c00d27d86420b2a6
```

If your original firmware does not match, the script refuses to patch it.

## Build the tested firmware

Requirements: **Python 3.10 or newer**, no third-party packages. Windows, macOS or Linux.

```sh
python tools/lx5_patch.py LX5__V20.zip --out output
```

Or use the extracted official BIN:

```sh
python tools/lx5_patch.py LX5__V20.BIN --out output
```

Two separate files will be generated:

| File | Intended use | SHA-256 |
| --- | --- | --- |
| `output/english/LX5__V20.BIN` | **English unlock**, exact v36 image successfully installed on one Japanese LX5 | `adf084b47e101387eee571caf8644f687b9ad717cdbd9323c0af24de2b90fb6b` |
| `output/stock_code_rollback/LX5__V20.BIN` | Stock *program code*, preserving higher advertised version; **not physically tested** | `8e15db5e3cc5d85d1c356910070622a8588c2003418a544ce962d3a575b92bfa` |

The patcher verifies the result byte-for-byte against the tested v36 output, including the SHA-256, before writing it. Do not mix these files up. Keep each in a different directory. Only the English file has been physically flashed.

## Installing on a Japanese LX5 — at your own risk

1. Confirm the camera is a **Panasonic DMC-LX5**, not an LX3, LX7 or another model. This project has been physically verified only on **one Japanese LX5 previously running v2.0**.
2. Fully charge the camera battery. Back up your photos.
3. Use a camera-formatted SD card and copy **only** `output/english/LX5__V20.BIN` to the **root** of that card.
4. Turn the camera off, insert the card, turn it on and press **Playback (▶)**.
5. On the tested Japanese LX5, the camera displayed the Japanese **firmware-update confirmation screen** and version **2.0**, despite already running v2.0. **The confirmation screen by itself does not prove flashing will succeed.**
6. If you knowingly accept the risk of permanently disabling the camera, follow [Panasonic's official update instructions](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/LX5/index2.html). Never interrupt the update, remove the battery or card, or switch the camera off during writing.
7. After a successful update, use the newly available English menu setting if needed. Check that English survives a complete power-off/power-on and test normal photography and video functions.

On the tested camera, English menus worked, survived restart and were still available after switching back to the normal SD card. **Photograph/video regression and factory-service calibration were not independently verified on that camera.**

**Rollback warning:** `stock_code_rollback` was validated only in offline tests. It depends on the camera still running its normal updater and is **not** a way to recover a camera that will not boot. It has **not** been physically installed.

## Reproducibility and evidence

- [Physical result and scope](docs/physical-test.md)
- [Technical offsets, encoding and version gate](docs/technical-notes.md)
- [Provenance and prior research](docs/acknowledgements.md)

This is an independently reproducible **single-camera proof of concept**, not a universally certified firmware update. Please record the camera's original firmware version and report both successes and failures if you test it.

## License and ownership

The original patching script and project documentation are available under the [MIT License](LICENSE). The **Panasonic firmware remains Panasonic's property** and is not included or licensed by this repository. External projects linked in the acknowledgements retain their own licenses and ownership.