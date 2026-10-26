# mero-xperia

A hardware-archaeology and low-level programming lab for a working **Sony Ericsson Xperia X10 mini pro U20a** (2010).

**Current discovery (2026-10-25):** The actual handset boots and displays **Android 1.6 (Donut)**, **Linux kernel 2.6.29**, and Sony Ericsson build **1.2.A.1.181**. This is **not** the later Android 2.1 firmware described in Sony Ericsson's revised March 2011 white paper.

## Status: verified on the physical handset

| Item | Observation | Provenance |
| --- | --- | --- |
| Device | Sony Ericsson Xperia X10 mini pro | Product box and handset |
| Variant | **U20a** | Android About phone and under-battery label |
| Android ("Firmware version") | **1.6** | About phone screenshot |
| Kernel | **2.6.29** | About phone screenshot |
| Kernel build string | `SEMCUser@SEMCHost #1` | About phone screenshot |
| Sony Ericsson build | **1.2.A.1.181** | About phone screenshot |
| Baseband | **Unknown** (as displayed) | About phone screenshot; significance not diagnosed |
| Condition | Booted successfully, working display, navigating system settings | User test and photos |
| Manufacturer marking | Brazilian-manufactured; batch marking `10W41` (likely 2010 week 41; not independently verified) | Under-battery label |

**Privacy:** The photographed under-battery label contains individually identifying handset numbers. Do not commit full label photographs, IMEI, serial numbers, SIM details, or raw personal archives to this public repository.

## Published model specifications (NOT measured on this handset)

- **SoC/CPU:** Qualcomm MSM7227, ARM11-class, **600 MHz**.
- **Display:** 2.55-inch 240 × 320 QVGA capacitive single-touch screen.
- **Input:** slide-out 4 × 10 QWERTY keyboard; accelerometer.
- **Networking:** Wi-Fi 802.11 b/g (2.4 GHz), Bluetooth 2.0+EDR. U20a cellular: GSM 850/900/1800/1900 and UMTS/HSPA 850/1900/2100 MHz.
- **Imaging/audio:** 5 MP autofocus rear camera, LED light/flash, FM radio, 3.5 mm audio connector.
- **Connection/storage:** micro-USB, USB mass-storage support, microSD. Sony Ericsson's **March 2011** document lists support up to **32 GB** (original 2010 documents sometimes say **16 GB**). Test actual card compatibility before relying on it.
- **Memory:** manufacturer documents *up to 128 MB phone memory*, **not** a confirmed RAM amount. Determine usable RAM and flash partitions from the actual device.
- **Size/weight:** 90 × 52 × 17 mm, 120 g.
- **Battery:** revised manufacturer white paper lists 970 mAh (other period sources cite 930 mAh); verify the installed pack label before documenting its actual capacity.

### Why documentation differs

Sony Ericsson's early **2010 launch specification** described **Android 1.6**, matching this handset. Its **March 2011 revised white paper** describes **Android 2.1**, after the available update. Never treat later release software as what this phone currently runs.

## Lab priorities

1. **Preserve first**: check removable battery, image/copy microSD and personal files, inventory software without reset/flash.
2. **ADB (read-only)**: identify kernel, ABI, available shell commands, memory, filesystem, and mount points.
3. **First native experiment**: cross-compile a tiny ARM/Android C executable for this old environment; run and inspect return value.
4. **Pocket terminal**: physical keyboard + tiny local network client for a controlled host service on desktop or Oracle VM.
5. **Pixel-art/music lab**: tiny custom UI, keyboard interactions, sound cues.
6. **Advanced reverse engineering**: only after we have recorded device identity, current build and feasible restore options.

See [hardware profile](docs/hardware-profile.md), [safe first session](docs/first-session.md), and [roadmap](docs/roadmap.md).

Related reference: [iFixit E10i teardown notes](docs/related-teardown.md). This covers the X10 Mini, **not** this U20a mini pro; its specifications and disassembly steps are not verified for our handset.

### USB connection verified — 2026-10-25

- **USER-OBSERVED:** The original cable only charged the phone. After changing cables, the USB notification appeared; selecting **Mount** exposed a folder on the computer. USB debugging was also enabled.
- **HOST-OBSERVED:** `lsusb` now reports `0fce:2138 Sony Ericsson Mobile Communications AB Xperia X10 mini pro (Debug)`.
- **INTERPRETATION:** Changing the cable resolved the observed connection problem. The original cable may lack working data conductors; its exact fault has not been tested.
- **VERIFIED (2026-10-26):** Standalone ADB installed; non-root shell works. See the [backup session](docs/backup-session.md) for measured memory, partition sizes, preservation results and internal-backup limits.

## Quick start (Arch Linux host)

Install the Android debug bridge:

```bash
sudo pacman -S android-tools
adb version
```

On **this old Android 1.6 release**, look for *Settings → Applications → Development → USB debugging* (the menu can differ). Connect via a **USB data cable**, then:

```bash
adb devices
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.display.id
adb shell cat /proc/version
adb shell cat /proc/meminfo
```

No part of the quick start requires root, a factory reset, network access, or flashing. If `adb devices` does not report a usable device, follow the [first-session checks](docs/first-session.md) rather than forcing drivers or firmware.

**Security:** Android 1.6 is obsolete and unpatched. Avoid primary Google accounts, sensitive services, public networks, and casual exposure to the Internet. For experiments favor offline USB or a dedicated isolated LAN. Old ADB has different host-authorization protections from modern Android; enable USB debugging only when needed.

## Sources

- [Sony Ericsson X10 mini pro U20a/U20i white paper, revised March 2011](https://www-support-downloads.sonymobile.com/u20/whitepaper_EN_u20_x10_mini_pro.pdf)
- [Original 2010 launch specs, archived coverage](https://www.xperiax10.net/2010/02/15/xperia-x10-family-extended-with-mini-mini-pro-handsets/)
- [Android Debug Bridge documentation](https://developer.android.com/tools/adb)

Provenance convention: **OBSERVED** means read from the actual phone; **PUBLISHED** means manufacturer/product documentation; **PLANNED** means untested experiments.

For verified shell commands, filesystem boundaries, CPU/display interfaces and native/Dalvik programming paths, see the [exploration guide](docs/exploration.md).

**Experiments verified (2026-10-26):** A [1,048-byte native ARMv6 C program](experiments/hello-native/README.md) ran from `/data/local/tmp` with exit status 0. A [terminal app on the phone](docs/on-device-terminal.md) was installed and launched with a local shell. The exploration guide also explains why a few MiB of `MemFree` does not mean that is the phone's total usable RAM.

**Terminal code and build instructions:** [apps/terminal/](apps/terminal/README.md), including the pinned upstream source, larger-font customization and `>_` icon.
