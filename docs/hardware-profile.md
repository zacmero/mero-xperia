# Device profile — Xperia X10 mini pro U20a

> Last observed: 2026-10-25. **Keep observations, period documentation, and hypotheses separate.** This file does not include unique serial or IMEI values because this repository is public.

## A. Observed directly from this device

### ADB observations — 2026-10-26

- ADB shell access verified as UID `2000` (`shell`), without root.
- ABI: `armeabi`; `/proc/cpuinfo` reports ARMv6-compatible processor rev 5, architecture `6TEJ`, features `swp half thumb fastmult vfp edsp java`. These are CPU feature flags, not a claim that a standalone Java runtime is installed.
- Kernel-visible RAM: `MemTotal: 169672 kB` (about 165.7 MiB); this does not establish physical RAM capacity.
- `/proc/mtd` exposes system 206 MiB, cache 50 MiB, appslog 256 KiB and userdata 211.75 MiB. Raw devices are root-only.
- `/proc/version` confirms Linux `2.6.29`, GCC `4.2.1`, build `#1 PREEMPT Fri Jul 2 13:25:20 2010`.
- See the [backup session](backup-session.md) for private archive locations, verification and access limits.

| Property | Value | Evidence |
| --- | --- | --- |
| Brand / family | Sony Ericsson Xperia X10 mini pro | Phone and original packaging shown |
| Model variant | **U20a** | About phone page and under-battery label |
| Android version | **1.6 (Donut)**, displayed as “Firmware version 1.6” | About phone screen |
| Linux kernel | **2.6.29** | About phone screen |
| Kernel build suffix | **SEMCUser@SEMCHost #1** | About phone screen |
| OS/build identifier | **1.2.A.1.181** | About phone screen |
| Baseband version | **Unknown** | About phone screen; root cause **not diagnosed** |
| Hardware state | Boots, screen functional, settings UI navigable | On-device demonstration |
| Model/product type label | U20a; “Indústria Brasileira” | Under-battery label |
| Date/batch marking | `10W41`, probably year/week convention | Under-battery label; manufacturing date inference not yet verified |
| External features seen | Physical slider-keyboard product illustrated on original box; USB cable visibly plugged in during photo | Photos; full keyboard functionality not yet individually tested |
| Battery | Removed for photographing the under-battery label | Photos; present electrical health and capacity not measured |

**Never commit:** full under-battery label photos, serial number, IMEI, subscriber IDs, contacts, personal photos, personal backups, or raw crash/system logs that expose these identifiers.

## B. Published hardware specification (model-family, not benchmarked)

| Area | Manufacturer/model-family specification | Notes |
| --- | --- | --- |
| SoC | Qualcomm **MSM7227** | Original and 2011 white papers |
| CPU frequency | **600 MHz** | CPU clock, not modem frequency |
| CPU generation | ARM11 / ARMv6 class | Family information; confirm actual ABI with `getprop` and `/proc/cpuinfo` locally |
| GPU | Usually identified as **Adreno 200** | Third-party model references; verify on actual device if relevant |
| Main screen | **2.55 in**, **240 × 320** QVGA | Capacitive single-touch |
| Physical input | Sliding **4 × 10 QWERTY** keyboard | Includes arrow, function, shift and symbol keys |
| Camera | **5 MP** autofocus rear, LED flash/video light | No verified front-facing camera |
| Motion | Accelerometer | 2011 manufacturer specs |
| Wi-Fi | 802.11 b/g, **2.4 GHz** | Manufacturer specs; WPA/WPA2 Personal is described |
| Bluetooth | **2.0+EDR**, A2DP and other profiles | Manufacturer specs |
| Radio | **FM radio** | Headphone may be required as antenna |
| Wired connections | **Micro-USB**, **3.5 mm** AV/audio port | Mass-storage support for microSD |
| microSD | **Up to 32 GB** in March 2011 white paper | Earlier 2010 document advertised up to 16 GB; installed firmware compatibility untested |
| Internal usable phone storage | **Up to 128 MB** | **Not a verified RAM figure**; inspect partitions and /proc/meminfo |
| Battery rating | **970 mAh** in 2011 manufacturer white paper | Period web listings also cite 930 mAh; installed battery pack not yet read |
| Dimensions | **90 × 52 × 17 mm** | Manufacturer |
| Weight | **120 g** | Manufacturer |
| U20a GSM | 850 / 900 / 1800 / 1900 MHz | Modem bands; not CPU speed |
| U20a UMTS/HSPA | 850 / 1900 / 2100 MHz | Distinguishes U20a from U20i regional variant |
| Theoretical HSPA speeds | Up to ~7.3 Mbps down, 2.0 Mbps up | Radio maximum in product documentation, not a real-world result |

### Firmware-document mismatch

The **February 2010 launch documentation** lists **Android 1.6**, matching the current software shown in the photos. Sony Ericsson's **revised March 2011 white paper** was updated to list **Android 2.1**. It is incorrect to call this *particular* handset an Android 2.1 device without an actual update. The original firmware is valuable to document and should not be overwritten simply for the sake of a newer number.

## C. Open questions to resolve, without changing firmware

- [ ] Check battery model, rated capacity, current condition, and battery life.
- [ ] Confirm keyboard row/function keys and all physical buttons.
- [ ] Read-only `adb devices` / `getprop` connection.
- [ ] `cat /proc/meminfo` for usable RAM, `df` and mount info for storage.
- [ ] CPU ABI, instruction support and graphics driver visible to shell.
- [ ] Check whether microSD is present; capacity, contents, filesystem (after preserving).
- [ ] Check Wi-Fi, Bluetooth and camera individually, preferably offline.
- [ ] Why does the About screen report **Baseband version: Unknown**? Record radio firmware properties read-only before any assumption; missing SIM is not a proven explanation.
- [ ] Verify availability of a safe restore image matching **U20a / 1.2.A.1.181** before any unlocking, rooting, flashing, or partition write.

## Sources

1. [Sony Ericsson — Xperia X10 mini pro U20i/U20a white paper, revision March 2011](https://www-support-downloads.sonymobile.com/u20/whitepaper_EN_u20_x10_mini_pro.pdf) — manufacturer family hardware and **later** Android 2.1 release.
2. [Sony Ericsson launch specs, February 2010 (archived)](https://www.xperiax10.net/2010/02/15/xperia-x10-family-extended-with-mini-mini-pro-handsets/) — original Android 1.6 and initial 16 GB card support claim.
3. Actual handset photographs and About phone screenshot provided by the owner on 2026-10-25; original images retained outside the public repo.
