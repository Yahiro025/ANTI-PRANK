<p align="center">
  <img src="assets/logo.svg" alt="CAUGHT! watchful eyes logo" width="96" height="96">
</p>

<h1 align="center">CAUGHT!</h1>

<p align="center">
  <strong>One touch. One alarm. One very awkward photo.</strong><br>
  A local Windows prank app with a fullscreen reveal.<br>
  Arm it yourself, or let the optional Android companion arm it when your phone moves away.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#android-companion">Android companion</a> ·
  <a href="#development">Development</a> ·
  <a href="#license">License</a>
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Windows-10%20%7C%2011-251C19?style=flat-square&amp;labelColor=3B3330" alt="Windows 10 or 11"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-251C19?style=flat-square&amp;labelColor=3B3330" alt="Python 3.11 or 3.12"></a>
  <a href="#android-companion"><img src="https://img.shields.io/badge/Android-8.0%2B%20companion-251C19?style=flat-square&amp;labelColor=3B3330" alt="Optional Android 8.0+ companion"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-251C19?style=flat-square&amp;labelColor=3B3330" alt="MIT license"></a>
</p>

## Quick Start

Requires **Windows 10/11** and **Python 3.11 or 3.12 with Tcl/Tk support**. From the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe caught.py
```

After setup, you can also double-click [run.cmd](run.cmd). Bluetooth is needed only for the optional phone companion.

## How it works

`IDLE → ARMING → ARMED → TRIGGERED`. The current state stays visible.

1. **Arm.** Click **ARM SYSTEM**. The camera warms up, then a three-second countdown begins. Input is ignored until **ARMED**.
2. **Trigger.** A global key press, mouse button press, or supported scroll triggers once. The alarm and fullscreen warning start without waiting for the photo.
3. **Reveal.** One webcam photo appears with **CAUGHT IN 4K** and **BRO THOUGHT NOBODY WOULD NOTICE**. If capture fails, the warning reads **CAMERA FAILED, BUT YOU'RE STILL CAUGHT.** The alarm stops automatically after ten seconds.
4. **Reset.** **STOP ALARM & RESET** or Escape while the app has focus stops the alarm, clears the photo, and returns to **IDLE**. **CANCEL** and **DISARM** reset during arming and monitoring. Alt+F4 exits.

## Android companion

The optional companion uses Bluetooth LE advertising to let the laptop detect when your phone moves away. It requires **Android 8.0+**, Bluetooth LE advertising support, and Bluetooth enabled on both devices.

1. Download [CAUGHT-companion.apk](mobile/releases/CAUGHT-companion.apk?raw=true) onto the phone and open it to install. Android may ask you to allow installations from the app opening the file. This is a locally signed development build.
2. On the laptop, select **PHONE WATCH**. Enter its eight-character code in CAUGHT! Companion on the phone.
3. Grant Nearby devices permission when requested, allow notifications, and tap **START LOOKOUT**. Keep the phone close until the laptop says **Phone nearby**.
4. Take the phone away. A weak signal for roughly eight seconds, or a missing signal for twelve seconds, starts the laptop's normal camera warmup and countdown.

**STOP PHONE WATCH** stops laptop monitoring; **STOP LOOKOUT** stops phone advertising. Stopping the phone lookout can also cause the laptop to arm because its signal disappears. Once arming begins, use **CANCEL**, **DISARM**, or Escape on the laptop. Returning with the phone does not disarm it, and the phone receives no alerts.

## Tech Stack

| Component | Choice |
| --- | --- |
| Desktop | Python 3.11/3.12, Tkinter, winsound on Windows 10/11 |
| Global input | pynput |
| Webcam | OpenCV |
| Phone signal | Android Java / Bluetooth LE advertising; Bleak scanner on Windows |
| Runtime services | None; no backend, database, accounts, cloud, or internet API calls |

Direct Python dependencies are `pynput`, `opencv-python`, and `bleak`, pinned in [requirements.txt](requirements.txt). The desktop uses the standard library for everything else, without Pillow or elevation.

## Privacy and controls

- Input callbacks detect events without recording typed characters or keyboard history.
- One photo stays in memory and is cleared on reset or exit. No photos are saved or uploaded, and no video is recorded.
- Input and system shortcuts remain available. The app does not lock Windows or change speaker volume or mute settings.
- Camera use stays visible. Run a consenting demo; there is no hidden monitoring or startup persistence.

## Development

[caught.py](caught.py) contains the native app; [phone_watch.py](phone_watch.py) handles the optional Bluetooth watch. Android source is built with [mobile/build.ps1](mobile/build.ps1), using the Android SDK and JDK configuration in that script.

The separate [NICE TRY prototype](prototype/README.md) is a browser design demo with simulated phone and locking behavior. Run its behavior tests from the repository root with Node.js; no packages need installing:

```powershell
node --test prototype/model.test.js
```

These tests cover the browser prototype only. See the [native test plan](tests/README.md) for mocked checks to add and the [Windows acceptance checklist](tests/ACCEPTANCE.md) for physical-device rehearsal.

## Known Limitations

- Camera, sound, real global input, and the Android-to-Windows flow still need physical-device verification. Automated native-app tests have not been added; the browser prototype has its own behavior tests.
- Mouse movement is not monitored. Scroll detection depends on the events Windows reports, including trackpad support.
- Bluetooth strength varies with walls, radios, and phone power restrictions. It is not an exact distance measurement. The advertised session code can be copied and does not verify identity.
- This is a comedic demo, not security software. It cannot identify the owner. “4K” is a joke, not a capture specification.

## License

Project code is licensed under the [MIT License](LICENSE).

The prototype bundles **Bricolage Grotesque** by the Bricolage Grotesque Project Authors under the [SIL Open Font License 1.1](prototype/assets/FONT-LICENSE.txt). That license applies to the font.
