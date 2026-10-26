# Exploring the stock Android 1.6 system

Observed through the U20a's non-root ADB shell on 2026-10-26. Raw captures remain private under `captures/exploration-2026-10-26/`. This session read device information; it did not install an app, change firmware or write an experimental program to the phone.

## Where commands run

From the computer, `rtk adb shell` opens an interactive shell **on the phone**, initially at `/`. `exit` returns to the computer. `rtk adb shell id` runs one command on the phone and returns. RTK runs on the computer; it is not installed on the handset.

The phone reports UID/GID `2000` (`shell`), with supplementary groups including `input`, `log` and `sdcard_rw`. This is not root. Seeing a path in `ls /` does not establish permission to read it: `/init.rc` is visible, but reading it returned permission denied.

`whoami` and `uname` are absent from `/system/bin` and `/system/xbin`. Their short-name invocation produces a misleading permission-denied error. Use `id` for identity and `cat /proc/version` for the kernel. The exact cause of that shell error wording has not been traced.

## A map of the filesystem

| Path | Role and observation |
| --- | --- |
| `/` | Root directory; mounted read-only as `rootfs`. |
| `/system` | Stock OS binaries, libraries, framework and system apps; YAFFS2, read-only. |
| `/system/bin` | Shell, toolbox commands, Android utilities and native services. |
| `/system/framework` | Android runtime/framework archives, including `core.jar`. |
| `/data` | Application data and installed applications; YAFFS2, writable mount with per-directory access controls. |
| `/data/local/tmp` | Candidate experiment directory: its parent listing shows owner `shell`, mode `drwxrwx--x`. Actual file writing/execution here has not been tested. |
| `/cache` | Writable YAFFS2 cache partition. |
| `/sdcard` | Removable card mount location. It was absent from `/proc/mounts` during this session while USB mass storage exposed it to the host. |
| `/proc` | Kernel-generated information, such as CPU, memory and mounts; not ordinary disk files. |
| `/sys` | Kernel device/driver attributes; some are writable controls. Only selected read operations were used. |
| `/dev` | Device interfaces, including input event devices; not ordinary media files. |
| `/sqlite_stmt_journals` | A 4 MiB temporary filesystem at observation time. |

## Shell and tools

`/system/bin/sh` supports basic scripts and arithmetic: `echo $((2+3))` returned `5`. Its PATH is `/sbin:/system/sbin:/system/bin:/system/xbin`.

Many commands are symlinks to Android's `toolbox`, including `id`, `ls`, `cat`, `df`, `ps`, `top`, `getprop` and `getevent`. Listed commands also include `pm`, `am`, `dalvikvm`, `app_process` and `sendevent`. Presence does not make every operation usable by the shell user.

The inspected command directories do not list `whoami`, `uname`, `grep`, `find`, `tar`, `busybox`, `python`, `gcc`, `cc`, `javac`, `java`, `su` or `run-as`. This inventory does not prove no copy exists elsewhere.

Modern shell assumptions fail here: `ls -ld` was treated as a filename, and `[` produced permission denied. An attempted `[ -w /data/local/tmp ]` check therefore did **not** establish whether that path is writable. Do filtering on the host when a utility is missing.

## Hardware interfaces measured

- CPU: ARMv6-compatible, architecture `6TEJ`; ABI `armeabi`.
- CPU frequency attributes: minimum `122880`, maximum `600000`, sampled current `245760` (kHz: 122.88, 600 and 245.76 MHz). Governor: `ondemand`. Listed governors: `conservative`, `ondemand`, `userspace`, `powersave`, `performance`. These readings do not establish sustained performance.
- Display: framebuffer mode `U:240x320p-0`, virtual size `240,640`, 16 bits per pixel. The virtual buffer is larger than the reported screen mode; double buffering is a plausible explanation, not verified here.
- Battery at sampling: status `Full`, capacity `100`. The standard-looking `temp` and `voltage_now` paths were absent; those readings do not establish battery health or original capacity.
- Input drivers: `mimmi_keypad` → `event0`, `compass` → `event1`, `7k_handset` → `event2`, `Cypress cy8ctma300 touch driver` → `event3`, `systemconnector` → `event4`. No live key capture or event injection was performed.

## What this means for programs

The phone reports Android SDK/API **4**, `ro.debuggable=0`, `ro.secure=1`. Dalvik and `app_process` exist. `dalvikvm -help` printed its options and then an initialization-failure message; this establishes command availability, not successful execution of our own code.

The backed-up `core.jar` contains `classes.dex`. The stock `pm` and `am` scripts set `CLASSPATH` to their framework JAR and execute `app_process` with `com.android.commands.pm.Pm` or `com.android.commands.am.Am`. These are examples of Android Java-derived code launched from a shell. A desktop Java `.class` or ordinary JAR is not automatically a compatible Dalvik program; a compatible DEX build path remains to be established.

Host inspection of the backed-up `sh` and `dalvikvm` finds **32-bit little-endian ARM EABI4 ELF executables**, dynamically linked through `/system/bin/linker`. The linker itself is statically linked. A native experiment must match this old ARM/Bionic environment; an arbitrary modern ARM Linux binary is not enough.

## Commands to repeat from the computer

Run these individually and inspect each result:

```bash
rtk adb shell id
rtk adb shell pwd
rtk adb shell getprop ro.build.version.sdk
rtk adb shell cat /proc/version
rtk adb shell cat /proc/meminfo
rtk adb shell cat /proc/mtd
rtk adb shell cat /proc/mounts
rtk adb shell ls /system/bin
rtk adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
rtk adb shell cat /sys/class/graphics/fb0/modes
```

Keep raw outputs private; some other properties and `/proc` files contain device identifiers. To explore the SD card on the phone again, first finish host transfers and safely eject its host mount, then disable USB storage sharing on the phone. ADB and storage sharing are separate interfaces.

Follow-up: the [first native program](../experiments/hello-native/README.md) subsequently proved writing and execution in `/data/local/tmp/mero-xperia-hello-20261026`, printing a greeting and returning 0. A Dalvik hello-world remains pending selection of a compatible DEX toolchain. The earlier exploration above was read-only; the follow-up added only the named native experiment.

## Understanding RAM usage

The user's sample reported `MemTotal: 169672 kB` and `MemFree: 3036 kB`: approximately **165.7 MiB kernel-visible RAM** and **2.96 MiB completely unused RAM**, respectively. Linux's historical `kB` labels here represent units of 1024 bytes. `MemTotal` is not a measurement of every physical RAM chip or GPU/modem-reserved memory.

A subsequent sample during the native experiment reported `MemFree: 2952 kB`, `Cached: 24784 kB`, `Buffers: 0 kB`, `SReclaimable: 1276 kB`, and `SwapTotal: 0 kB`. Thus about **2.88 MiB** was completely free and **24.20 MiB** was cached. Some clean cache can be reclaimed, but these categories are not a promise that all those bytes can immediately go to a new program.

This kernel provides no `MemAvailable` estimate. Do not interpret 3 MiB free as either a hard 3 MiB application limit or evidence that arbitrary large apps will fit. Application limits, kernel overhead, reclaimability and Android's process-management behavior also matter. The tiny native program successfully ran under these conditions. No swap was configured in that sample.
