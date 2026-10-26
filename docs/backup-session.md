# Backup session — 2026-10-26

## Scope and private storage

Private backup directory: `backups/xperia-2026-10-26/` inside this checkout. Git ignores `backups/` and `local/`; personal media, raw diagnostics and system binaries must remain outside version control. The directory is private to the local user, but its contents are not encrypted by this workflow.

The mounted microSD contained **10,139 files, 840,861,057 bytes (801.91 MiB)**. `rsync` copied its files, then a checksum-based dry run reported no differences (exit 0, empty verification report). `sdcard-sha256.jsonl` records each copied file's size and SHA-256. `sdcard.tar.gz` packages the copy and its verification records for cloud storage.

The card has 3,965,190,144 bytes of total block capacity (about 3.69 GiB), as reported by the phone. A raw card image would include filesystem metadata and unused space; this session's file copy does not preserve deleted files or constitute a raw image. The host requires elevated permission to read the raw card device.

## ADB and observed system

Google's official [Linux platform-tools archive](https://dl.google.com/android/repository/platform-tools-latest-linux.zip) supplied ADB **37.0.1-15733141**, protocol version **1.0.41**. It runs from `local/tools/platform-tools/adb`; `~/.local/bin/adb` links to it. Moving/deleting this checkout will break that link.

The actual phone accepted a shell connection without root:

- Model `U20a`; ABI `armeabi`; Android `1.6`; build `1.2.A.1.181`.
- Kernel from `/proc/version`: Linux `2.6.29`, built with GCC `4.2.1`, `#1 PREEMPT Fri Jul 2 13:25:20 2010`.
- Shell UID `2000`; `uname` returned permission denied, so `/proc/version` supplied the kernel evidence.
- Usable RAM (`MemTotal`): **169672 kB**, about **165.7 MiB**. This is kernel-visible memory, not a measurement of physically installed RAM.
- `/proc/mtd`: system **206 MiB**, cache **50 MiB**, appslog **256 KiB**, userdata **211.75 MiB**.
- `df`: `/system` used **136292 KiB**; `/data` used **115336 KiB** at observation time.

## System backup limits

The final per-file pass copied **844 of 848 enumerated system paths**. The four failures were `/system/etc/bluez/audio.conf`, `/system/etc/bluez/hcid.conf`, `/system/etc/bluez/input.conf` and `/system/etc/dbus.conf`. Both compressed archives were read back: SHA-256 matched all **10,139 SD file entries** and **852 system/archive-log entries** against their manifests. This verifies archived bytes, not restore bootability or complete metadata preservation.

Compressed sizes: `sdcard.tar.gz` **757,246,902 bytes**; `system-partial.tar.gz` **80,810,419 bytes**. Together with scope notes and checksums, the upload package is **838,058,013 bytes** (about **799.2 MiB**).

`system/` holds private inventory, access-limit observations, a recursive system listing, copy logs and readable `/system` files. A bulk `adb pull /system` stopped at protected `/system/etc/dbus.conf`; the subsequent per-file copy continues past failures and records each result in `pull-results.json`.

**The original system-partial.tar.gz is a partial file archive, not a complete restorable firmware backup.** A later [read-only MTD capture](raw-flash-preservation.md) preserved the main and spare/OOB areas of the four exposed NAND partitions, including protected app data. That capture still does not include bootloader, baseband, unexposed boot partitions, or a tested restore procedure. Stock Android 1.6 predates the later `adb backup` facility.

## Why pacman installation failed

The user's first attempt requested `android-tools-37.0.0-5-x86_64.pkg.tar.zst`; mirrors returned 404. The local package metadata referenced an older package no longer present at those mirrors.

`sudo pacman -Syu android-tools` refreshed metadata but stopped before installing: held `hyprland` required `libaquamarine.so=13-64`, and held `hyprpaper` required `libhyprtoolkit.so=5-64`, conflicting with the proposed library upgrades. This is a desktop package dependency conflict, independent of the phone. Do not force dependencies or remove holds without reviewing that desktop upgrade. Standalone ADB avoids changing those packages.

## Google Drive destination

Remote: `xperia-drive:`. Destination: `mero-xperia/backups/xperia-2026-10-26/`. OAuth credentials live in the user's rclone configuration, outside this repo. Upload and remote verification results are recorded below when completed. Individual-file uploading was interrupted in favor of archives because the card contains more than ten thousand files; any initial remote `sdcard/` folder is an incomplete staging copy.

**VERIFIED:** All four final files uploaded successfully: `sdcard.tar.gz`, `system-partial.tar.gz`, `BACKUP-SCOPE.txt`, and `SHA256SUMS`. `rclone check --one-way` against the local upload package exited 0 and reported **4/4 matching files**, using sizes and the common content hash. The private report is `backups/xperia-2026-10-26/drive-verify.txt`. This checks the final package; it does not validate any incomplete staging folder or demonstrate a successful phone restore.

The remote uses rclone's shared Google Drive OAuth client. This rclone build reports that client is being retired during 2026; current authorization and this upload succeeded. A personal OAuth client may be needed for future access.

## Later protected-data preservation

The four exposed MTD partitions were captured through a temporary RAM-only root helper and read-only MTD character devices. Main-area images, spare/OOB data, and a bad-block map were saved under `raw-flash/` on the same Drive destination. `rclone check --one-way` found **0 differences and 11 matching files** there; the revised main package also had **0 differences and 9 matching files**. The four `/system` configuration files missed by the original ADB pass are in `system-root-only.tar.gz`. A separate `protected-files.tar.gz` contains 30 selected `/data` files, including contacts and SMS databases and installed app packages; this is a supplement to the live raw `userdata` image, not a full file-level `/data` archive. See [raw-flash preservation](raw-flash-preservation.md) for sizes, method, and restoration limits.

