# CAUGHT! ? Little lookout

Approved direction: Little lookout. Native Windows and Android share an original one-eyed red character, warm cream canvas, ink typography, and a restrained red primary action. No landing page.

## Product loop

Pair the phone ? establish nearby ? leave with the phone ? laptop arms ? input triggers a reveal ? reset. Phone proximity is RSSI, never an exact meter reading. The phone broadcasts; it does not confirm the laptop is connected or receive alerts. The laptop keeps the photo in memory.

## Shared system

- Cream `#FFF4DE`, paper `#FFFBF2`, ink `#251C19`, red `#B92D24`, muted `#6B574C`, sand `#F3E1C4`.
- Bricolage Grotesque for the brand and display text, bundled with its license in `assets/`. Desktop registers it privately for the process, with Segoe UI fallback. Native body fonts remain platform fonts. Code uses a monospace face.
- Spacing: 4, 8, 12, 16, 24, 32. Android fields and buttons use a 12 dp radius and native ripple feedback. Tk uses real, keyboard-focusable native buttons.
- Little lookout geometry: a 72?76 red oval, 46?46 cream eye, offset ink pupil, two feet and two cheek marks within a 100?100 coordinate system. Idle side-eye, nervous arming pupil, centered watching pupil. No mouse tracking or decorative animation loop.
- State is always named in text. Red is reserved for the character, primary action, and the reveal. TRIGGERED inverts to cream text on red, with a paper photo stage.

## Desktop

Header: brand and state. Stage: mascot, current task, supporting copy, photo/fallback. Footer: primary action, phone watch/code/instructions, sound choice, privacy and exit. Stop/reset remains outside the expanding photo area. The content stage scrolls at compact heights; fixed controls stay visible even when pairing instructions are shown. At trigger, hide pairing and sound setup; expand the photo. Escape resets and Alt+F4 exits.

Silent mode starts enabled for the event. The sound choice is frozen into the session at arming, and disabled during that session. A silent session returns before importing or calling the sound API. The visual reveal and camera behavior still work.

## Android

Brand ? character ? pocket lookout title ? labeled laptop code ? Start lookout ? broadcasting status ? Stop lookout while running ? three-step guide ? honest limitations. Code and buttons grow with text size. Scroll content respects system and keyboard insets. The code survives recreation. The screen describes broadcasting rather than claiming a laptop connection.

## References and rejected directions

`docs/design-directions.html` records the three competing desktop/mobile compositions. Little lookout was selected over Night shift and After hours. Duolingo's shape and character consistency informed the system, without copying its mascot or assets: https://blog.duolingo.com/shape-language-duolingos-art-style/

## Audit and evidence

Native baseline: git commit `98c5746b740da9ac2f31d9be39c6e9634e336fa6` (range adjustments were already uncommitted). Before: oversized unstructured copy, two competing controls, buried phone setup, no silent control, fixed-height Android code input, no native button ripple. After: bounded type scale, shared character/type, dedicated pairing code, explicit silent mode, growing field, ripple feedback and insets.

The ai-design-check CLI cannot meaningfully parse these Tkinter/Java layouts (Java is reported unread); zero findings is not evidence of zero native issues. Native geometry checks and visual Windows inspection are used instead. Android APK build/signature can be verified locally; physical-device layout/permissions/BLE remain acceptance checks.

The old `prototype/` is a historical NICE TRY concept with different locking semantics. It is not the native app specification.
