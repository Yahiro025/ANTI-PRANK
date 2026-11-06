# 10-Minute MVP Build Plan

## Goal

Build the smallest working Windows demo from the prepared brief. Use one entry point: `caught.py`. This document is a plan, not an implementation claim.

## Time Budget

| Time | Deliverable |
| --- | --- |
| 0–2 minutes | Tk window, four states, ARM SYSTEM, reset/exit controls |
| 2–4 minutes | Global pynput listeners, three-second countdown, one-trigger latch |
| 4–6 minutes | Background camera warmup, one photo, Tk display, camera fallback |
| 6–7 minutes | winsound alarm worker, stop event, automatic silence |
| 7–8 minutes | Red-and-cream fullscreen reveal and oversized copy |
| 8–10 minutes | Critical automated checks and physical demo rehearsal |

## Suggested Structure

Keep the state, UI, and queue dispatch in a small App class. Use helpers for the camera, alarm, and input monitoring only if they make cleanup clearer. No generic event bus, framework, plugin system, or configuration layer.

```text
Tk main thread
  ARM SYSTEM → ARMING → worker initializes camera
  camera ready or unavailable → 3-second countdown
  countdown ends → start listeners → confirm ready → ARMED

pynput callback → one-trigger gate → queue notification
Tk queue poll → TRIGGERED → fullscreen reveal + start alarm worker
camera worker → one post-trigger image → queue → display in Tk

RESET / ESC / EXIT → invalidate session, stop workers/listeners,
                    clear photo, leave fullscreen, return to IDLE or close
```

## Practical Choices

- Try webcam index 0 using OpenCV DirectShow; optionally try Media Foundation if opening fails.
- Warm up the camera while ARMING. Discard frames; do not retain a stream. Read fresh frames while armed if needed to avoid an old buffered image.
- Use a five-second UI timeout for camera preparation and three seconds for capture. These are proposed defaults, not requirements from the original brief. A stuck driver must not freeze Tk.
- Convert resized BGR to RGB, then pass binary PPM data to Tk `PhotoImage`. Keep a reference to the image. Pillow is unnecessary.
- Generate a short original two-tone alarm with `winsound.Beep` in a worker. Keep each beep short so stop responds quickly. Proposed default: automatically silence after ten seconds; keep the reveal until reset.
- The physical-input requirement can use pynput's Windows event filters to ignore injected-event flags. Filtering a listener notification must not suppress the event system-wide.
- No mouse movement detection. Trackpad resting is outside scope.
- Escape is an app-local reset shortcut. If the app lacks focus while armed, an Escape key press may first trigger the prank; Escape on the revealed window then resets it. A global disarm hotkey is outside this MVP.

## Failure Behavior

| Failure | Required outcome |
| --- | --- |
| Camera missing, denied, busy, or slow | Countdown continues after fallback; alarm and warning work |
| Capture fails after successful warmup | Show the camera-failed message |
| Sound muted or output unavailable | Visual warning still works; do not change system volume |
| Global listener startup fails | Show an error and return to IDLE; never claim ARMED |
| Reset during warmup/countdown | Old callbacks cannot arm or trigger the new session |
| Several simultaneous inputs | One reveal, one alarm, one retained photo |

## Definition of Done

Run the critical checks in `tests/ACCEPTANCE.md`, report actual results, and leave any hardware limitation explicit. Skip installers, packaging, movement detection, persistent settings, saved photos, extra animations, and CI infrastructure.

## Reference Details

Pynput warns that Windows input callbacks run on operating-system threads and must remain brief; stopped listeners cannot be restarted. See [pynput keyboard documentation](https://pynput.readthedocs.io/en/latest/keyboard.html).

`winsound.Beep` is blocking, so keep it on a worker; memory-backed asynchronous `PlaySound` is unsupported. See [Python winsound documentation](https://docs.python.org/3/library/winsound.html).
