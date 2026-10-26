# Mero Terminal for the Xperia

The customized terminal uses a **20-point default font** (upstream: 10) and a high-contrast `>_` launcher icon. It installs as **Mero Terminal**, package `org.mero.xperia.terminal`, alongside the original `jackpal.androidterm` app. Existing terminal data is preserved.

**Verified on the U20a (2026-10-26):** build/signature verification passed; installation succeeded; Android reported the custom activity focused and a child `/system/bin/sh` running under the new app UID. The user confirmed the 20-point size is comfortable and should be retained.

## Where the code lives

- [Pinned upstream source](upstream/): Android Terminal Emulator v1.0.70, commit `f5ecc5a` (Git submodule). Java UI: `upstream/term/src/main/java/jackpal/androidterm/`. Terminal rendering: `upstream/emulatorview/`. Native process execution: `upstream/libtermexec/`.
- [Customization code](customize.py): font, app label, manifest package, private action/permission identifiers, and launcher icon replacement. Java class/JNI names are retained.
- [Icon source](icon.svg): editable SVG, rasterized to the upstream launcher density sizes.
- [Build script](build.sh) and [container tools](Dockerfile).

This build adapts the author's released APK using apktool, retaining its compiled Java implementation and native libraries. It **does not compile the upstream Java/C sources from scratch**; the source checkout is provided for study and tracing. Upstream's historical full-build instructions are in `upstream/docs/Building.md`. Our overlay is the complete code for the current customizations.

The author's APK is downloaded from `https://jackpal.github.io/Android-Terminal-Emulator/downloads/Term.apk` and checked against SHA-256 `4cbf6adb273a6afa01f7d5f4ea97ac22b5a97ce1a34c000f2ef308a6383e8821` before use. Upstream licensing remains in the source checkout and the retained APK notices.

## Build and install

Host requirements: Docker daemon access, Python 3, curl, sha256sum and ImageMagick (`magick`). The container supplies apktool, signing and alignment tools without installing host Java/Android packages.

From the repo root:

```bash
rtk git submodule update --init --recursive
rtk bash apps/terminal/build.sh
rtk adb install -r build/terminal/MeroTerminal.apk
rtk adb shell am start -n org.mero.xperia.terminal/jackpal.androidterm.Term
```

Open **Mero Terminal**, with the green `>_` icon. Its shell commands run under its own app UID. You can use the on-phone **Menu → Preferences → Text → Font size** setting to adjust the size further. The 20-point value is a first-install default: subsequent APK updates preserve a user's chosen preference.

Build output and decoded APK files live in ignored `build/terminal/`. Signing keys/password live in ignored `local/terminal/`, restricted to the local user. Preserve that signing key privately to install future updates over this app; losing it means the app cannot be updated in place. Nothing in those directories is pushed to Git. The signing password is generated locally and is never printed.

Signing uses the v1/JAR scheme needed by Android 1.6. The original app remains available as a fallback. This overlay does not grant root or add missing Linux commands.
