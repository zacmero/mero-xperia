# Temporary root and internal flash preservation

On 2026-10-26, this **U20a** running Android **1.6**, build **1.2.A.1.181**, accepted a temporary root helper in `/sqlite_stmt_journals`, a 4 MiB tmpfs. The helper used the old init firmware-event flaw to write a temporary path to `/proc/sys/kernel/hotplug`. A Bluetooth hardware event ran the helper as root. It restored `/sbin/hotplug` before making itself setuid for the ADB shell group. We verified `id` returned `uid=0(root) gid=0(root)` through the helper, and `/proc/sys/kernel/hotplug` again contained `/sbin/hotplug`. The phone was not rebooted, rooted persistently, flashed, or remounted read-write.

The source used here is [root-helper.c](../experiments/temporary-root/root-helper.c). It is a device-specific research experiment; the tested helper path includes this session's date. Rebooting clears the tmpfs helper. The stock `/system` remains read-only. The original public [Exploid research](https://c-skills.blogspot.com/2010/07/android-trickery.html) informed the approach, but our helper does not install anything under `/system` or leave the kernel hotplug path changed after activation.

## What was captured

`/proc/mtd` exposed four NAND partitions. [capture-mtd-readonly.py](../scripts/capture-mtd-readonly.py) read their **read-only character devices**, `/dev/mtd/mtdNro`, in 2 MiB chunks. Each chunk was staged in tmpfs, pulled over ADB, checked for the expected byte count, and appended to a private local image. A test pull repeated the same 2 MiB chunk and produced matching SHA-256 hashes. The block devices `/dev/block/mtdblockN` returned `I/O error` on direct reads; the MTD character devices worked.

| Image | `/proc/mtd` name | Bytes |
| --- | --- | ---: |
| `mtd0-system.img` | system | 216,006,656 |
| `mtd1-cache.img` | cache | 52,428,800 |
| `mtd2-appslog.img` | appslog | 262,144 |
| `mtd3-userdata.img` | userdata | 222,035,968 |

### Spare area and bad blocks

The stock kernel reported 2,048-byte NAND pages, 64 spare/OOB bytes per page, and 131,072-byte erase blocks. A second read-only helper, [oob-capture.c](../experiments/temporary-root/oob-capture.c), used `MEMREADOOB` on `/dev/mtd/mtdNro`. [capture-mtd-oob-readonly.py](../scripts/capture-mtd-oob-readonly.py) pulled the result in at most 2 MiB RAM chunks. The four `.oob` files contain 6,750,208, 1,638,400, 8,192, and 6,938,624 bytes, matching the page counts of their respective `.img` files. A repeat of the first 2 MiB of system OOB data matched byte-for-byte. The `.oob.gz` files decompress to identical bytes.

`MEMGETBADBLOCK` reported two bad erase blocks in system (1029, 1031), one in cache (155), none in appslog, and two in userdata (1027, 1029). The private `bad-blocks.txt` records the full map. These kernel-reported locations help interpret the images; they are not instructions to write flash.

Local images and lossless `.gz` copies are in `backups/xperia-2026-10-26/raw-flash/`, which Git ignores. The local `SHA256SUMS` passed for all 18 files: eight images, eight compressed copies, the scope note, and the bad-block map. Decompressing each `.gz` produced the same SHA-256 as its image. The eight `.gz` files, `SHA256SUMS`, `BACKUP-SCOPE.txt`, and `bad-blocks.txt` were uploaded to `xperia-drive:mero-xperia/backups/xperia-2026-10-26/raw-flash/`. `rclone check --one-way` found **0 differences and 11 matching files**; the private report is `backups/xperia-2026-10-26/drive-raw-verify.txt`. The earlier [SD card and readable system file archives](backup-session.md) remain separate. The four protected configuration files missed in the earlier system pass were pulled with root access and uploaded as `system-root-only.tar.gz`.

## File-level protected-data supplement

[capture-protected-files.py](../scripts/capture-protected-files.py) used the same RAM staging method to copy 30 selected `/data` files: eight SQLite databases for contacts, SMS/telephony, calendar, settings, and media; 20 installed app packages; and two system metadata files. The private path list, file hashes, and copied tree are packaged in `protected-files.tar.gz` on the same Drive destination. The archive was read back locally, with hashes matching all 30 source copies. All eight SQLite databases returned `ok` to a host `PRAGMA quick_check`; the contacts database required a stand-in `LOCALIZED` collation on the host, so this is a structural check, not application-level validation. The revised main Drive package passed `rclone check --one-way` with **0 differences and 8 matching files**. This selection does not cover every `/data` file and was taken while Android was running.

## Limits and recovery status

An off-device extraction tool has not yet been validated against these images. The historical [yaffs2utils README](https://github.com/dorigom/yaffs2utils/blob/1edc1688b7f8db140d2b85448dd68f9e6318dc95/README) says its `unyaffs2` extracts images made by its own builder and does not yet support raw NAND dumps. Finding a suitable raw-dump reader and checking extracted files against the separate file archive is the next recovery rehearsal.

The `.img` plus `.oob` pairs preserve the bytes returned by the kernel's read-only MTD interfaces, but they are not a raw electrical dump or validated flash-ready images. The main-area reads may have been corrected by the kernel's ECC layer. `/data` and `/cache` were mounted and active, so their images may include changes made between chunks. The four visible MTD partitions do not expose bootloader, baseband, or a separate boot/recovery partition. No emergency flash mode, stock firmware package, or restore procedure has been tested. **Do not flash these files directly.** They preserve evidence and protected data, but they do not yet provide a complete, verified recovery route for a failed OS modification.

The temporary helper is present only until reboot. While it exists, an ADB shell can run commands as root; the executable is inside a `0700` directory owned by the shell user and has mode `4750` with group `shell`. The phone's normal ADB shell remains UID 2000.
