# Test Plan

## Current Status

The application has not been built. There are no runnable application tests yet, and no test pass is claimed. This folder defines what the builder should verify without inventing an interface or adding placeholder tests that always pass.

## Automated Checks to Add During Implementation

Use Python's standard-library `unittest` and `unittest.mock`. Test the implementation's actual API. Mock camera, audio, listeners, clock/scheduler, and GUI operations as needed.

| Scenario | Expected assertion |
| --- | --- |
| IDLE input | No trigger |
| ARMING input, including the arming click | No trigger |
| Countdown finishes with listeners ready | ARMED exactly once |
| Concurrent input callbacks | One accepted trigger |
| Further input after TRIGGERED | No second alarm or capture |
| Reset before countdown completes | Stale callback cannot arm |
| Reset before camera completes | Late photo cannot appear |
| Camera initialization/capture fails | Alarm and warning still requested |
| Listener startup fails | Never display ARMED |
| Reset or close | Stop requested, photo cleared, listeners stopped |
| New arm after reset | Fresh listeners and a new usable trigger gate |

Pass sentinel key objects that fail if converted to strings or inspected, to catch accidental content logging. Do not write camera images, simulate physical input, or play real audio in automated tests.

Once these tests exist, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Zero discovered tests is not a successful application validation. Hardware acceptance still requires the checklist in [ACCEPTANCE.md](ACCEPTANCE.md).
