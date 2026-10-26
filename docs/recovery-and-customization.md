# Recovery readiness and OS appearance

Assessment: 2026-10-26, stock **U20a / Android 1.6 / 1.2.A.1.181**.

## Recovery is not secured

The verified local/Drive archives preserve media and readable system files. They are **not a complete, restorable phone image**: protected app data, boot/recovery images and raw flash remain unavailable. No custom recovery installation, working restore operation or emergency USB mode has been verified on this handset.

There is a concrete tooling lead: [Flashtool's upstream U20 configuration](https://github.com/Androxyde/devices/blob/master/U20/U20.properties) lists `recognition=U20i,U20a,mimmi,U20`, `canflash=true`, `canfastboot=false`, and `canrecovery=true`. These are tool configuration flags, **not evidence that recovery exists on this phone or that a particular tool build will restore it**. Do not apply generic modern-Xperia fastboot instructions.

Remaining evidence needed before protected OS modifications:

1. Obtain and identify a trustworthy, model-correct U20a stock firmware package and preserve its provenance/hashes. Restoring some bootable firmware and preserving this exact Android 1.6 build are different goals; a later stock image does not preserve this time capsule.
2. Identify a compatible flash-tool version, required loader and host USB support. Verify its exact handling of this variant and firmware without issuing writes.
3. Document and test the correct emergency/flash-mode entry and host enumeration, with a way to return to normal operation. No such mode transition was attempted in this session.
4. Document wipe effects, preservation gaps and failure cases. Raw modem/device-unique data is not interchangeable between handsets.
5. Establish a practical recovery procedure and decide explicitly which changes it can recover. A documented candidate path is not a tested restore.

No rooting, bootloader unlocking, recovery installation, firmware flashing or `/system` writes were performed.

## Removing the blue appearance

| Change | Requires protected OS changes? | Limits |
| --- | --- | --- |
| Wallpaper | Usually no | Does not recolor menus and system controls. |
| Our own application colors/icons | No | Already demonstrated with Mero Terminal. |
| Another launcher or a small custom Home app | Can be installed as an ordinary app | Must support API 4/ARMv6; changes the home screen, not every Sony screen. No replacement launcher has been tested. |
| Sony settings, framework controls, notification/system resources | May require root and replacing protected framework/system-app resources, or a different ROM | Wrong resources/permissions can break apps or boot. A full firmware reflash is not the only mechanism, but this still belongs behind the recovery gate. |

The scope of any stock theme option on this exact firmware remains unverified. A sensible next cosmetic experiment is an app-level home screen while retaining the stock launcher. Global system recoloring remains deferred until recovery readiness improves.

### Stock menu inspection — 2026-10-26

The user requested black/grey system menus. We decoded the backed-up `framework-res.apk`, `Settings.apk`, `SEMCSettings.apk`, `HomeScreen.apk` and `CustomizationProvider.apk` for inspection under ignored `build/theme-inspect/`. No replacement APK was built or installed.

- Framework `Theme` sets `windowBackground` to `@drawable/semc_bg` and `panelBackground` to `@drawable/menu_background`.
- Visual inspection of `res/drawable-ldpi/semc_bg.png` confirms the blue Sony gradient/wave background. Other density/orientation versions also exist. Menu/panel assets include nine-patch PNGs, whose stretch/padding metadata would need preservation in a future modification.
- Framework `Theme.Black` exists and sets a black window background, but it is an app-selectable style, not evidence of a user-facing global theme switch.
- The inspected default strings and activity declarations expose wallpaper selection in HomeScreen, but no theme/appearance selector was found in those packages. This inspection does not prove that no hidden vendor setting exists anywhere.
- The live `/system/framework/framework-res.apk` is owned by root, mode `644`; `/system` remains mounted read-only. ADB is UID 2000 and no `su` executable exists at `/system/bin/su` or `/system/xbin/su`. Mounting the SD card over USB does not grant permission to replace framework files.

**Outcome:** stock menus were not recolored. The identified resources belong to the protected Android framework. A framework modification would require additional privileged access and a verified model-correct recovery route; neither is established. This is different from editing an ordinary app like Mero Terminal.

## Sources and limits

- [Existing backup scope](backup-session.md): measured preservation and access gaps.
- [Flashtool device configuration](https://github.com/Androxyde/devices/blob/master/U20/U20.properties): candidate U20 tool support, not a verified recovery route.
- Sony's current Companion support page could not be retrieved during this session (HTTP 403); compatibility with this legacy handset was not established. No exact stock firmware was downloaded or authenticated.
