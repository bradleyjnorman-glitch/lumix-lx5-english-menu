# Confirmed hardware result — 17 November 2026

## Test case

- Camera: Japanese-market Panasonic Lumix DMC-LX5.
- Original on-camera version: Panasonic v2.0.
- Candidate: `ENGLISH_CANDIDATE/LX5__V20.BIN` from the verified v36 build.
- Candidate SHA-256: `adf084b47e101387eee571caf8644f687b9ad717cdbd9323c0af24de2b90fb6b`.

## Observed by camera owner

1. After placing the generated BIN on the SD card, the camera displayed its Japanese firmware-update confirmation dialog (version shown: **2.0**).
2. The owner approved the update; it installed, and the camera remained operational.
3. English menus were available and functioning.
4. English remained active after turning the camera fully off and on again.
5. The owner reinserted their usual SD card; the camera continued to operate in English.

An image of the physical Japanese update confirmation was supplied during the investigation but is **not included here** to avoid publishing the owner's photograph without a separate decision.

## What this does NOT prove

- Other Japanese LX5 units will behave identically.
- The patch works on an LX5 with a different firmware baseline.
- The backup/stock-code image can be flashed as a rollback.
- A camera that stops booting can be recovered.
- Every shooting feature, recording mode and service adjustment was tested after the flash.

Earlier investigation: a restored ROM BACKUP language field `0x30E = 0001` on stock Japanese firmware was accepted temporarily, but the menus remained Japanese, the Language option was absent, and after power cycling the field reverted to `0000`. This was why a region-policy firmware patch was pursued.