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

Local images and lossless `.gz` copies are in `backups/xperia-2026-10-26/raw-flash/`, which Git ignores. The local `SHA256SUMS` passed for all eight files; decompressing each `.gz` produced the same SHA-256 as its image. The four `.gz` files, `SHA256SUMS`, and `BACKUP-SCOPE.txt` were uploaded to `xperia-drive:mero-xperia/backups/xperia-2026-10-26/raw-flash/`. `rclone check --one-way` found **0 differences and 6 matching files**; the private report is `backups/xperia-2026-10-26/drive-raw-verify.txt`. The earlier [SD card and readable system file archives](backup-session.md) remain separate. The four protected configuration files missed in the earlier system pass were pulled with root access and uploaded as `system-root-only.tar.gz`.

## Limits and recovery status

These are **NAND main-area reads**, without spare/OOB bytes or ECC metadata. `/data` and `/cache` were mounted and active, so their images may include changes made between chunks. The four visible MTD partitions do not expose bootloader, baseband, or a separate boot/recovery partition. No emergency flash mode, stock firmware package, or restore procedure has been tested. **Do not flash these images directly.** They preserve evidence and protected data, but they do not yet provide a complete, verified recovery route for a failed OS modification.

The temporary helper is present only until reboot. While it exists, an ADB shell can run commands as root; the executable is inside a `0700` directory owned by the shell user and has mode `4750` with group `shell`. The phone's normal ADB shell remains UID 2000.
