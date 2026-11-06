# Implementation Instructions

## Current Task

The repository is prepared for a teammate to implement the MVP in **10 minutes**. There is no application implementation yet. Do not spend the build window reorganizing folders, expanding documentation, choosing frameworks, or creating infrastructure.

## Priorities

1. Functional correctness.
2. Reliability during the live demo.
3. Fast implementation.
4. Minimal dependencies.
5. Simple, maintainable code.
6. A polished comedic reveal.

Follow KISS, DRY, and YAGNI. Start with `caught.py`; split only when a concrete need appears. The user explicitly wants preparation now; do not implement the app until the build is requested.

## Required Stack

Windows 10/11, Python 3.11/3.12, Tkinter, pynput, opencv-python, winsound. Use the standard library for everything else. No Pillow or additional direct dependencies. No runtime network calls, browser, backend, database, accounts, or elevation.

## Behavioral Contract

- States: IDLE → ARMING → ARMED → TRIGGERED. Reset returns to IDLE from any state.
- ARM SYSTEM initializes the camera off the GUI thread and prepares audio, then starts a three-second countdown.
- Ignore countdown input. Activate monitoring only after the countdown. The arming click must never trigger.
- Monitor global key presses, mouse button presses, and supported scroll events. Omit movement detection for the MVP.
- Trigger once per session. Stop listening after the trigger.
- Start alarm and fullscreen warning immediately; capture must not delay them.
- Show one post-trigger photo or the explicit camera-failed fallback.
- Always show the current state.

## Non-Negotiable Guardrails

- Never inspect, print, serialize, or store typed characters or keyboard history.
- Never suppress system shortcuts, block input, inject events, or simulate input in tests.
- Never save identifiable camera frames to disk or upload them.
- Never record video. Live camera reads for warmup/freshness may be discarded in memory.
- Clear the retained photo on reset and exit.
- No background persistence, startup registration, hidden camera behavior, or OS-lock imitation.
- Escape and a visible STOP ALARM & RESET button must work. Keep Alt+F4 available.
- Do not change speaker volume, disable mute, or claim owner identification.

## Threading and Reliability

- All Tk operations belong on the main thread. Worker callbacks put messages into a queue; Tk polls via `after`.
- Camera initialization/read/release and alarm playback must not block Tk.
- Input callbacks do almost nothing: latch one event and queue a notification. Drop event contents.
- Use a lock or equivalent atomic gate for simultaneous events.
- Use session IDs/cancellation so late workers and countdown callbacks cannot affect a reset session.
- One worker owns the camera. Do not release it concurrently from Tk during a read.
- Bound UI waits for camera startup and capture; driver trouble must leave the fallback usable.
- Recreate pynput listeners after stopping them. Never restart stopped listener threads.
- Input-monitor startup failure must return to a clear error state; never display ARMED when hooks failed.

## Testing

Use stdlib `unittest` and mocks for state transitions, races, cancellation, and hardware failure. No new test dependencies. See `tests/README.md`. Do not use a real webcam or trigger the real alarm in automated tests. Use `tests/ACCEPTANCE.md` for the physical-device checks.

## Handoff

Explain what works, what was tested, and what still needs a physical Windows check. Never claim tests passed unless they were executed. Keep the documentation direct, structured, and at the formality level of README.md.
