# CAUGHT! — A Windows Anti-Prank Laptop Trap

## Context

Leave your laptop unattended. Someone presses a key, clicks, or scrolls. Instead of letting them prank you, the laptop pranks them.

An alarm goes off. A fullscreen warning appears. One webcam photo shows up alongside:

**CAUGHT IN 4K**

**BRO THOUGHT NOBODY WOULD NOTICE**

This is a comedic team project for OpenAI DevDays Exchange. It is not professional security software. “4K” is a joke, not a capture specification.

## Project Status

The native MVP is implemented in `caught.py`: visible arming, a three-second countdown, global physical-input detection, a one-shot fullscreen reveal, an original two-tone alarm, and an in-memory webcam photo with a camera-failure fallback. Escape and the reset button cancel the session; the alarm also stops automatically after ten seconds.

No new automated tests were written, per the hackathon deadline. Syntax, dependency imports, and non-hardware Tk startup were checked. The Android APK was built and its signature verified, but no Android device was available; the phone-to-laptop flow remains unverified. The laptop's Bluetooth radio reported powered off during the scanner check. Camera, speakers, real global input, and the complete physical demo require rehearsal on the demo laptop using the acceptance checklist.

## Technical Requirements

| Component | Choice |
| --- | --- |
| Platform | Windows 10/11; Windows 11 primary |
| Language | Python 3.11 or 3.12 |
| GUI | Tkinter |
| Global input | pynput |
| Phone signal | Android Bluetooth LE advertising; Bleak scanner on Windows |
| Webcam | OpenCV |
| Alarm | winsound |
| Runtime services | None |

Direct dependencies are `pynput`, `opencv-python`, and `bleak`; their supporting packages install automatically. No Pillow, browser, backend, database, account, cloud, or runtime API requests.

## Setup

Install Python 3.11 or 3.12 with Tcl/Tk support if needed. Then, from this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m tkinter
```

The last command should open a small Tk window. Close it after checking.

The local `.venv` contains the pinned dependencies. Launch from the repository root:

```powershell
.\.venv\Scripts\python.exe caught.py
```

## Android phone companion

Download [CAUGHT-companion.apk](mobile/releases/CAUGHT-companion.apk) to an Android 8.0+ phone and open it to install; Android may ask you to allow installations from the app used to open the file. This is a locally signed development build, not a Play Store release.

1. Turn on Bluetooth on the laptop and phone. Open CAUGHT! on the laptop and choose **PHONE WATCH**.
2. Open CAUGHT! Companion on the phone, enter the laptop's eight-character code, grant Nearby devices permission, and tap **START LOOKOUT**. Allow notifications so you can see the lookout is running.
3. Keep the phone close until the laptop says **Phone nearby**. Take the phone away. When its signal stays weak for roughly eight seconds or is missing for twelve seconds, the laptop starts its normal camera warmup and countdown. Input after it is armed triggers the usual reveal. The phone does not receive alerts in this version.
4. Stop monitoring with **STOP PHONE WATCH** on the laptop or **STOP LOOKOUT** on the phone. Once the laptop starts arming, use **CANCEL**, **DISARM**, or Escape on the laptop. Phone return does not automatically disarm it.

Bluetooth strength is affected by walls, the phone model and radio interference; it is not an exact 10-meter measurement. Stopping the Android lookout or losing its signal can arm the laptop. The shared session code appears in Bluetooth advertisements and can be copied; this is a fun proximity trigger, not identity verification or a security lock. The phone must support Bluetooth LE advertising, and Android may stop the foreground service under device-specific power restrictions.

To rebuild the development APK on this machine, run `powershell -ExecutionPolicy Bypass -File mobile/build.ps1`; the new build is written to the ignored `mobile/build` directory. Copy it to `mobile/releases/CAUGHT-companion.apk` before committing a refreshed phone download. The script uses the local Android SDK, Android build-tools 36.0.0, platform android-37.0, and Android Studio's JDK. A development signing key is generated in the ignored `mobile/build` directory; retain it if you want future APKs to update an existing installation.

## Start Building

1. Read [AGENTS.md](AGENTS.md) for the implementation rules.
2. Follow [the 10-minute build plan](docs/BUILD_PLAN.md).
3. Verify against [the acceptance checklist](tests/ACCEPTANCE.md).

[PRODUCT.md](PRODUCT.md) holds the product context. [DESIGN.md](DESIGN.md) records the confirmed visual direction. [The test README](tests/README.md) describes the planned automated checks, deferred for this deadline.

## Privacy and Exit Controls

- Detect input events; never record keys or typed text.
- Keep one photo in memory. Never automatically save or upload it.
- Clear the photo on reset.
- Never suppress input, shortcuts, or normal Windows controls.
- Always provide a visible stop/reset button and Escape to reset.
- Camera failure must still produce the alarm and warning.
- Run a consensual demo. Arming uses a visible camera indicator; nothing attempts to hide it.

## Scope

One local desktop app and an optional Android proximity companion. Four desktop states. One trigger per session. A three-second countdown. A camera fallback. A funny reveal.

Do not add packaging, installers, startup services, face recognition, owner identification, settings panels, or persistence during the demo build.
