# Mero Xperia — experiment roadmap

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
