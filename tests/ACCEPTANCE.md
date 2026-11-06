# Windows Demo Acceptance Checklist

## Status

**Not run.** Mark each item only after observing it on the demo laptop. Use a consenting teammate for the camera checks.

## Setup

- [ ] Windows 10/11, Python 3.11/3.12, Tkinter, and the two dependencies work without elevation.
- [ ] Set speaker volume to an appropriate demo level manually. Confirm output device and camera permission.
- [ ] Close conferencing apps that may hold the webcam. Use Windows camera privacy settings if access is denied.

## Core Flow — Critical

- [ ] Launch shows IDLE and an obvious ARM SYSTEM button.
- [ ] Arm: webcam initialization leaves the window responsive.
- [ ] Camera readiness or failure is visible before the three-second countdown.
- [ ] Arming click and keys/clicks during countdown do not trigger.
- [ ] Countdown completes before ARMED is shown and monitoring becomes active.
- [ ] A physical key press triggers once.
- [ ] After reset/rearm, a mouse click triggers once.
- [ ] After reset/rearm, a trackpad click triggers if Windows reports it as a mouse click.
- [ ] After reset/rearm, mouse wheel/trackpad scrolling triggers where supported.
- [ ] Input in another app triggers, proving detection is global.
- [ ] Cursor movement alone does not trigger; resting a finger on the trackpad is not promised detection.
- [ ] Alarm and fullscreen reveal appear promptly; they do not wait for the photo.
- [ ] One fresh photo appears with funny copy and correct aspect ratio.
- [ ] Rapid simultaneous keys/clicks produce one session, one alarm, one photo.

## Recovery — Critical

- [ ] STOP ALARM & RESET silences promptly, clears the photo, and returns to IDLE.
- [ ] Escape resets from ARMING, ARMED, and TRIGGERED when the app has focus.
- [ ] Alt+F4 remains available; no shortcut or input suppression occurs.
- [ ] Reset during camera warmup and countdown prevents late arming or stale photos.
- [ ] Repeated arm/trigger/reset cycles work with fresh listeners.
- [ ] Alarm auto-silences after the chosen duration; the reveal remains resettable.
- [ ] Webcam denied/unavailable still produces a working alarm and camera-failed reveal.
- [ ] Closing the app stops listening/audio and releases the camera when the driver responds.

## Privacy and Presentation

- [ ] No key characters or keyboard history appear in logs, console output, or files.
- [ ] No photos or videos are written to disk; reset removes the retained display image.
- [ ] No runtime network connections, uploads, or API requests are used.
- [ ] Camera indicator is visible normally; nothing hides OS notifications.
- [ ] Fullscreen copy, photo, and stop button fit on the actual demo display.
- [ ] Muted/unavailable audio does not break the visual reveal.

## Demo Sequence

Launch → ARM SYSTEM → wait for System Armed → teammate presses a key → reveal → STOP ALARM & RESET.

Rehearse once on the same laptop, camera, speaker output, and display configuration used on stage. Keep camera-failure mode as the fallback.
