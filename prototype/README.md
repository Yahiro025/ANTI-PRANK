> Historical concept: NICE TRY. This browser demo includes simulated locking flows that are not implemented by CAUGHT! Use the native desktop and Android apps described in the root README for the current product.

# NICE TRY.

Go get coffee. Keep your dignity.

Open **index.html** directly in a browser. No installation, build, server or network connection required. The font is bundled locally.

The interactive prototype includes Overview, My phone, Activity, Settings, pairing setup, a compact brand kit and a downloadable SVG logo. Use the bottom demo controls: Walk away → Simulate input → Return nearby → Simulate OS authentication. Try Lose signal, pause monitoring, or disconnect and re-pair the demo phone. Preferences and activity are session-only; reload resets everything.

This is a design prototype. It does **not** connect Bluetooth devices, monitor real input, lock your OS, identify people, or send notifications. A native desktop agent and phone companion would be needed for those integrations. Sensitivity is a demonstrated preference only.

Behavior: leaving or signal loss locks when monitoring is on; input while away creates an event; returning never unlocks; pausing, disconnecting and pairing never remove an existing lock. Unlocking always requires a separate simulated authentication action. No photographs or keystroke contents are collected.

Run focused behavior checks with `npm test` (Node.js only; no dependencies).

## Feasibility sources

- [Windows Dynamic Lock](https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/hello-feature-dynamic-lock) already uses paired-phone Bluetooth signal strength to trigger locking.
- [Bluetooth Core 6.0 overview](https://www.bluetooth.com/core-specification-6-feature-overview/) describes signal strength as a rough distance proxy. Nearby / away is more honest than an exact 10 m guarantee.
- Activity while away suggests possible tampering; it does not identify who is using the machine. OS-specific locked-screen input support needs validation during native development.

Brand name is a working concept; trademark/domain availability has not been researched. Typeface: Bricolage Grotesque, SIL Open Font License; source and license in assets.
