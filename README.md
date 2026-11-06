# CAUGHT! — A Windows Anti-Prank Laptop Trap

## Context

Leave your laptop unattended. Someone presses a key, clicks, or scrolls. Instead of letting them prank you, the laptop pranks them.

An alarm goes off. A fullscreen warning appears. One webcam photo shows up alongside:

**CAUGHT IN 4K**

**BRO THOUGHT NOBODY WOULD NOTICE**

This is a comedic team project for OpenAI DevDays Exchange. It is not professional security software. “4K” is a joke, not a capture specification.

## Project Status

The native MVP is implemented in `caught.py`: visible arming, a three-second countdown, global physical-input detection, a one-shot fullscreen reveal, an original two-tone alarm, and an in-memory webcam photo with a camera-failure fallback. Escape and the reset button cancel the session; the alarm also stops automatically after ten seconds.

No new automated tests were written, per the hackathon deadline. Syntax, dependency imports, and non-hardware Tk startup were checked. Camera, speakers, real global input, and the complete physical demo require rehearsal on the demo laptop using the acceptance checklist.

## Technical Requirements

| Component | Choice |
| --- | --- |
| Platform | Windows 10/11; Windows 11 primary |
| Language | Python 3.11 or 3.12 |
| GUI | Tkinter |
| Global input | pynput |
| Webcam | OpenCV |
| Alarm | winsound |
| Runtime services | None |

Only two direct dependencies: `pynput` and `opencv-python`. OpenCV also installs its required NumPy dependency. No Pillow, browser, backend, database, authentication, cloud, or runtime API requests.

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

One local desktop app. Four states. One trigger per session. A three-second countdown. A camera fallback. A funny reveal.

Do not add packaging, installers, startup services, face recognition, owner identification, settings panels, or persistence during the demo build.
