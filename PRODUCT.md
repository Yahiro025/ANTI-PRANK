# CAUGHT! — Product Context

## Platform

Windows 10/11 desktop. Windows 11 is the primary demo target.

## Stack

Python 3.11/3.12, Tkinter, pynput, OpenCV, and winsound. These are explicit project requirements. No browser, server, database, account, cloud service, or runtime API request.

## Purpose

An unattended laptop pranks the person who touches it. Arm it, walk away, and let one key press, click, or scroll trigger an alarm, a fullscreen reveal, and one webcam photo.

## Users and Context

A team demonstrating a comedic project at OpenAI DevDays Exchange, within a strict 30-minute development window. This is a funny local demo, not security software. Any monitored interaction counts; the app cannot identify an authorized person.

## Core Flow

IDLE → ARMING → ARMED → TRIGGERED. Initialize the camera off the UI thread, then count down three seconds. Ignore countdown input. Trigger once per session. Reset clears the photo and returns to IDLE.

## Guardrails

- Detect events only. Never retain typed characters or keyboard history.
- Never suppress shortcuts, inject input, lock the desktop, or require elevation.
- Keep the photo in memory; never automatically save or upload it.
- Camera failure must not prevent the alarm or reveal.
- Provide an obvious stop/reset path. Normal Windows controls remain available.
- No startup persistence, background surveillance, or video recording.

## Voice

Direct and structured documentation, using the supplied project brief as the writing reference. Playful reveal copy: “CAUGHT IN 4K” and “BRO THOUGHT NOBODY WOULD NOTICE.” The 4K line is a joke, not a resolution claim.

## Implementation Decisions

The brief ends during the alarm requirement. Use an original two-tone alarm, auto-silenced after ten seconds, Escape to reset, and a visible stop button. These are pragmatic MVP decisions, not additional user requirements. Visual direction is pending the optional UI preference question; no implementation depends on an answer.
