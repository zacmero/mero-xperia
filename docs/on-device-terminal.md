# Terminal on the phone — installed and launched

The user subsequently confirmed the terminal works on the handset. The repo now includes the [source checkout, font/icon customizations and build/install instructions](../apps/terminal/README.md). **Mero Terminal** is the customized app; the original terminal described below is retained as a fallback.

The customized app was installed and launched on 2026-10-26, with its child shell verified under `app_91`. The user confirmed the new 20-point font is comfortable. Its launcher icon is the green `>_` terminal glyph; use **Mero Terminal** to open this customized version.

On 2026-10-26 we installed **Terminal Emulator for Android**, package `jackpal.androidterm`, and launched `jackpal.androidterm/.Term`. Android reported it as the focused activity. The process table showed both the app and its child `/system/bin/sh` running as `app_81` (package UID 10081). This verifies that a local shell can run without the USB connection; actual unplugged interaction remains for the user to try.

## Source and compatibility

- [Author's project](https://github.com/jackpal/Android-Terminal-Emulator): development has ended.
- [Author's download page](https://jackpal.github.io/Android-Terminal-Emulator/) links to the [APK used](https://jackpal.github.io/Android-Terminal-Emulator/downloads/Term.apk).
- [Source build configuration](https://github.com/jackpal/Android-Terminal-Emulator/blob/master/term/build.gradle) declares minimum SDK 4, matching Android 1.6. The actual APK installed successfully on this U20a, contains ARM `armeabi` libraries, and launched its shell.
- Downloaded APK: 564,672 bytes; SHA-256 `4cbf6adb273a6afa01f7d5f4ea97ac22b5a97ce1a34c000f2ef308a6383e8821`.

The download came directly from the author's HTTPS site. A local hash records the bytes obtained; it is not an independently verified publisher fingerprint. The APK is kept privately in ignored `local/apks/Term.apk`. Installation, package and launch captures are under ignored `captures/experiment-2026-10-26/`. The package reports Internet, wake-lock and external-storage permissions; no network service was configured in this session.

## Try it

Open the terminal app from the phone's launcher and use the slide-out keyboard. Inside that app, type `id`, `pwd`, `ls`, or `cat /proc/meminfo`. These commands run locally on the handset. RTK belongs to the host computer, so do not prefix commands typed into the phone's terminal with `rtk`. Type `exit` to end a shell session.

The terminal app's shell runs under its app UID, **not** ADB's UID 2000. Permissions differ; neither is root. The app does not add missing command-line tools, so `whoami`, `uname`, desktop GNU utilities and a compiler do not become available just by installing it.

The native experiment currently has mode `700` and belongs to the ADB shell user, so the terminal app cannot execute that file as installed. Sharing the experiment with the app would require deliberately adjusting that experiment's directory/file permissions or copying it into app-owned storage; no protected-directory permissions were changed.
