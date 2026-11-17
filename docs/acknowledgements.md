# Credits, resources and prior art

The v36 patch originated from a reverse-engineering investigation of the Panasonic DMC-LX5 firmware, iterative offline tests and a successful one-camera physical test. The software in this repository is a purpose-built LX5 patching script, not an official Panasonic release.

Prior work that informed the approach:

- **Panasonic** — original DMC-LX5 firmware v2.0 and official update instructions: https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/LX5/index.html
- **Vitaliy Kiselev / PTool** — established Panasonic firmware-version increment, version-comparison patch and legacy Panasonic firmware format methods. Its support for the LX5 was **not** assumed; the LX5 patch was tested separately.
- **flickering-star / lumix-firmware-research** — documented a working Japanese GM5 language unlock and the advertised-version technique, plus MN103 emulator research. https://github.com/flickering-star/lumix-firmware-research . The GM5 result is precedent, not proof of LX5 compatibility.
- **GM/GX Japanese-to-English community work** — examples of editing existing language restrictions, rather than introducing new language resources.

These references do not imply endorsement or shared licensing. Panasonic owns its proprietary firmware, and this repository deliberately excludes firmware binaries.