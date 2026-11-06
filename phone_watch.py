"""Short-lived Bluetooth signal watch for the CAUGHT! Android companion."""
import asyncio
import threading
import time

from bleak import BleakScanner


class PhoneWatch:
    """Observe a session-specific advertising UUID; this is not authentication."""

    def __init__(self, code, notify):
        self.uuid = f"{code.lower()}-cabe-4aed-9c0d-0123456789ab"
        self.notify = notify
        self.cancelled = threading.Event()
        self.last_seen = None
        self.near = False
        self.weak_since = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.cancelled.set()

    def _run(self):
        try:
            asyncio.run(self._watch())
        except Exception as error:
            if not self.cancelled.is_set():
                self.notify(self, "error", str(error))

    async def _watch(self):
        def detected(_device, advertisement):
            if self.cancelled.is_set() or self.uuid not in [u.lower() for u in advertisement.service_uuids]:
                return
            now = time.monotonic()
            self.last_seen = now
            signal = advertisement.rssi
            if signal is None:
                return
            if signal >= -76:
                self.weak_since = None
                if not self.near:
                    self.near = True
                    self.notify(self, "near", None)
            elif signal < -82:
                if self.near and self.weak_since is None:
                    self.weak_since = now
            else:
                self.weak_since = None

        async with BleakScanner(detection_callback=detected):
            self.notify(self, "scanning", None)
            while not self.cancelled.is_set():
                now = time.monotonic()
                if self.near and ((self.last_seen is not None and now - self.last_seen >= 12) or
                                  (self.weak_since is not None and now - self.weak_since >= 8)):
                    self.notify(self, "away", None)
                    return
                await asyncio.sleep(0.25)
