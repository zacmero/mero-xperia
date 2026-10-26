# Mero Xperia — experiment roadmap

## Verified milestone status — 2026-10-26

- **Connectivity follow-up:** Bluetooth pairing and PNG receipt verified with a byte-for-byte round-trip comparison; text-file receipt was rejected. See [Bluetooth findings](bluetooth.md).
- **Recovery gate:** not satisfied. [Recovery readiness](recovery-and-customization.md) records the U20 tool-support lead, missing bootloader/baseband images, and the untested restore path.

- **XPR-001:** media, the four exposed MTD main-area partitions, four protected system files, and 30 selected protected data files are stored locally and on Google Drive. The main and raw-flash packages passed remote checks. A complete, proven firmware restore remains unavailable.
- **XPR-002:** normal ADB shell and a temporary RAM-only root helper verified; kernel/ABI/memory/storage findings documented. This firmware lacks `uname`; `/proc/version` provides kernel evidence.
- **XPR-003:** first freestanding ARMv6 C executable verified on the phone (greeting, exit 0, transfer round-trip). libc-based C and compatible DEX builds remain future experiments.
- **XPR-004:** local terminal tested by the user; source checkout and font/icon customization build added under `apps/terminal/`. Network client/service integration remains pending.

## Next sequence

1. Rehearse recovery **off the phone**: extract the archives into a scratch directory, inspect the saved databases and apps, and determine how to read the YAFFS2 main-area images. Keep original backups immutable.
2. Find a trustworthy U20a stock firmware package for the exact variant/build, record its origin and hashes, and identify a compatible flash tool and loader. The upstream U20 configuration is only a tooling lead.
3. Test flash-mode entry and host USB detection without issuing a write. Document the exit path, expected wipe effects, and any untested steps before replacing Sony framework resources.
4. Meanwhile, use the installed terminal and temporary root shell for read-only system experiments. Prototype black/grey colors in a separate app or launcher; this will not recolor Sony's stock menus.
5. After the recovery gate is met, make one reversible framework-resource change at a time, with the original APK, permissions, and rollback procedure documented before installing it.


Project target: a **tiny offline-first Linux/Android 1.6 handheld** that teaches embedded system internals and ultimately becomes a keyboard-driven interface to personal lab services. Each milestone has an explicit evidence gate.

## XPR-001 · Preserve the time capsule (P0)

**Steps:** note hardware condition, check battery safely, inspect microSD, back up irreplaceable pictures/files, preserve version information. No reset/flash.

**Done when:** at least one verified private backup of existing user files and a documented software baseline exist.

## XPR-002 · Establish a read-only ADB shell (P0)

**Steps:** Arch Linux `android-tools`, data-capable micro-USB cable, phone-side USB debugging, `adb devices`; gather release/ABI/kernel/memory/fs facts.

**Done when:** a stable, non-root shell runs `getprop`, `uname`, and `cat /proc/meminfo` successfully, with redacted findings in this repository.

**Risk gate:** no destructive commands, no flash/recovery, do not upload raw serial/IMEI-related output.

## XPR-003 · First native C executable (P1)

**Goal:** write `hello-xperia.c` (CPU details or file read) and cross-compile for **old ARM + Android Bionic** (not just a modern glibc Linux/ARM build). Transfer via `adb push` only after preservation.

**Done when:** compiled binary executes with a clean exit in the handset shell, and we have recorded compiler/linker parameters plus ELF inspection.

**Unknowns:** ABI, compatible NDK/toolchain, executable location permissions, C library vintage.

## XPR-004 · Pocket Mero terminal (P1)

**Goal:** tiny QWERTY-controlled UI communicating with a trusted service on the LAN/host, not running large models locally.

**Candidate read-only actions:** view a research task status, view queued messages, browse locally cached notes, show an Oracle VM status string.

**Done when:** the phone can request and render a deliberately tiny response from an isolated desktop service using a documented protocol.

**Safety:** avoid exposing an unauthenticated service to the Internet; avoid main personal credentials on Android 1.6.

## XPR-005 · Character + music interface (P2)

Small pixel sprite/animation, keyboard events, simple notes/rhythm/metronome. Favor low memory use, offline assets, and the real QVGA screen.

**Done when:** a native or early-Android-compatible app responds to input and renders/plays at least one original asset.

## XPR-006 · Embedded forensics (P2, gated)

System process inventory; filesystem layout; kernel modules; available serial/debug access; radio/baseband status (`Unknown` on About phone); historic service/boot tools.

**Done when:** findings are reproduced and recorded without wiping, bricking, or publishing identifiers.

**Do not attempt firmware writes** until a model-correct backup/restore path has been identified, tested where possible, and a risk/recovery plan documented.

---

## Working conventions

- Each milestone should eventually become a small issue/PR once the owner starts implementation; do not create a large issue backlog before first test.
- Keep hardware observations distinct from external model specifications and speculation.
- Prefer **one observable experiment at a time** (command → output → interpretation → next experiment).
- Log hashes of preserved personal files **privately**; no original private media or SIM/device identifiers in public commits.
- Reuse Arch, git, simple shell/C/Python on the host; use Android-compatible Java or C on-device as needed.
