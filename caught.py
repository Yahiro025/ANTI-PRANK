"""CAUGHT! A visible, local, one-shot Windows prank demo. No data is saved."""
from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox

CREAM = "#FFF4DE"
INK = "#251C19"
RED = "#B92D24"
MUTED = "#6B574C"
CAMERA_FAILED = "CAMERA FAILED, BUT YOU'RE STILL CAUGHT."


@dataclass
class Session:
    number: int
    cancelled: threading.Event = field(default_factory=threading.Event)
    camera_stop: threading.Event = field(default_factory=threading.Event)
    capture: threading.Event = field(default_factory=threading.Event)
    alarm_stop: threading.Event = field(default_factory=threading.Event)
    gate: threading.Lock = field(default_factory=threading.Lock)
    accepting: bool = False
    fired: bool = False
    listeners: list = field(default_factory=list)


class App:
    def __init__(self, root):
        self.root = root
        self.messages = queue.Queue()
        self.camera_guard = threading.Lock()
        self.audio_guard = threading.Lock()
        self.serial = 0
        self.session = None
        self.state = "IDLE"
        self.phase = ""
        self.prepared = False
        self.photo_pending = False
        self.photo = None
        self.closed = False
        root.title("CAUGHT! — The anti-prank prank")
        root.geometry("940x720")
        root.minsize(620, 540)
        root.configure(bg=CREAM)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Escape>", lambda _event: self.reset())
        self.build_ui()
        self.show_idle()
        self.poll_id = root.after(25, self.poll)

    def build_ui(self):
        self.shell = tk.Frame(self.root, bg=CREAM, padx=30, pady=22)
        self.shell.pack(fill="both", expand=True)
        top = tk.Frame(self.shell, bg=CREAM)
        top.pack(fill="x")
        tk.Label(top, text="CAUGHT!", font=("Segoe UI", 19, "bold"), bg=CREAM,
                 fg=INK).pack(side="left")
        self.state_label = tk.Label(top, font=("Segoe UI", 12, "bold"), bg=CREAM,
                                    fg=RED)
        self.state_label.pack(side="right")
        self.heading = tk.Label(self.shell, bg=CREAM, fg=INK,
                                font=("Segoe UI", 40, "bold"), wraplength=850)
        self.heading.pack(pady=(24, 5))
        self.subtitle = tk.Label(self.shell, bg=CREAM, fg=MUTED,
                                 font=("Segoe UI", 15), wraplength=840)
        self.subtitle.pack(pady=(0, 12))
        # Keep the stop/exit controls outside the expanding image area.
        footer = tk.Frame(self.shell, bg=CREAM)
        footer.pack(side="bottom", fill="x", pady=(12, 0))
        self.action = tk.Button(footer, font=("Segoe UI", 17, "bold"), bg=RED,
                                fg=CREAM, activebackground=INK, activeforeground=CREAM,
                                relief="flat", padx=26, pady=13, cursor="hand2")
        self.action.pack()
        self.exit_button = tk.Button(footer, text="EXIT  ·  Alt+F4", command=self.close,
                                      font=("Segoe UI", 11), bg=CREAM, fg=MUTED,
                                      relief="flat", padx=18, pady=7, cursor="hand2")
        self.exit_button.pack()
        tk.Label(footer, text="Esc resets · No keys recorded · Photo stays in memory",
                 font=("Segoe UI", 10), bg=CREAM, fg=MUTED).pack()
        self.photo_label = tk.Label(self.shell, bg=CREAM, fg=RED,
                                    font=("Segoe UI", 17, "bold"), wraplength=760)
        self.photo_label.pack(fill="both", expand=True, pady=6)
        self.detail = tk.Label(self.shell, bg=CREAM, fg=MUTED,
                               font=("Segoe UI", 12), wraplength=820)
        self.detail.pack(side="bottom", pady=5)
        self.root.bind("<Configure>", self.resize_text)

    def resize_text(self, event):
        if event.widget is not self.root:
            return
        width = max(300, event.width - 80)
        self.heading.configure(wraplength=width,
                               font=("Segoe UI", max(26, min(64, event.width // 18)), "bold"))
        self.subtitle.configure(wraplength=width)
        self.detail.configure(wraplength=width)
        self.photo_label.configure(wraplength=width)

    def set_state(self, value):
        self.state = value
        self.state_label.configure(text=f"STATE: {value}")

    def show_idle(self, error=""):
        self.set_state("IDLE")
        self.heading.configure(text="Touch it. Regret it.", fg=INK)
        self.subtitle.configure(text="Your friends brought pranks. You brought consequences.")
        self.photo_label.configure(image="", text="One touch. One alarm. One very awkward photo.")
        self.detail.configure(text=error or "Arming visibly activates the webcam. Use with consenting teammates.")
        self.action.configure(text="ARM SYSTEM", command=self.arm, state="normal")

    def current(self, session):
        return not self.closed and self.session is session and not session.cancelled.is_set()

    def arm(self):
        if self.state != "IDLE":
            return
        self.serial += 1
        session = self.session = Session(self.serial)
        self.prepared = False
        self.photo_pending = False
        self.phase = "camera"
        self.set_state("ARMING")
        self.heading.configure(text="Bait is being prepared.")
        self.subtitle.configure(text="Warming up the camera. Input is ignored for now.")
        self.photo_label.configure(text="Camera light may turn on. No photos are saved.")
        self.detail.configure(text="Camera preparation has a five-second limit.")
        self.action.configure(text="CANCEL", command=self.reset)
        # Prepare short, bounded tones before the countdown; no sound plays yet.
        self.tones = ((880, 140), (660, 140))
        threading.Thread(target=self.camera_worker, args=(session,), daemon=True).start()
        self.root.after(5000, lambda: self.camera_timeout(session))

    def camera_timeout(self, session):
        if self.current(session) and self.phase == "camera":
            session.camera_stop.set()
            self.begin_countdown(session, False)

    def begin_countdown(self, session, available):
        if not self.current(session) or self.phase != "camera":
            return
        self.prepared = available
        self.phase = "countdown"
        self.detail.configure(text="Camera ready. One photo after a trigger." if available
                              else "Camera unavailable. The alarm and reveal still work.")
        self.countdown(session, 3)

    def countdown(self, session, remaining):
        if not self.current(session) or self.phase != "countdown":
            return
        if remaining == 0:
            self.phase = "listeners"
            self.heading.configure(text="Almost watching…")
            self.subtitle.configure(text="Connecting global input listeners.")
            threading.Thread(target=self.input_worker, args=(session,), daemon=True).start()
            self.root.after(3000, lambda: self.listener_timeout(session))
            return
        self.heading.configure(text=f"Hands off in… {remaining}")
        self.subtitle.configure(text="Clicks and keys are ignored during the countdown.")
        self.root.after(1000, lambda: self.countdown(session, remaining - 1))

    def listener_timeout(self, session):
        if self.current(session) and self.phase == "listeners":
            self.reset("Input monitoring did not start. Please try again.")

    def latch(self, session):
        # OS callbacks only latch an event. Never inspect or retain key contents.
        with session.gate:
            if session.cancelled.is_set() or not session.accepting or session.fired:
                return
            session.fired = True
            session.accepting = False
        self.messages.put((session, "trigger", None))

    def input_worker(self, session):
        from pynput import keyboard, mouse
        from pynput._util.win32 import SystemHook

        def key_filter(_message, data):
            return not bool(data.flags & 0x10)  # injected keyboard notification

        def mouse_filter(_message, data):
            return not bool(data.flags & 0x01)  # injected mouse notification

        listeners = []
        try:
            listeners = [
                keyboard.Listener(on_press=lambda *_: self.latch(session),
                                  win32_event_filter=key_filter, suppress=False),
                mouse.Listener(on_click=lambda _x, _y, _button, pressed:
                               self.latch(session) if pressed else None,
                               on_scroll=lambda *_: self.latch(session),
                               win32_event_filter=mouse_filter, suppress=False),
            ]
            with session.gate:
                if session.cancelled.is_set():
                    return
                session.listeners = listeners
            for listener in listeners:
                if session.cancelled.is_set():
                    return
                listener.start()
            # In pinned pynput 1.8.1, wait() signals BEFORE Windows installs hooks.
            # Check actual handles, bounded, rather than reporting a false ARMED.
            ready = False
            deadline = time.monotonic() + 2
            while not session.cancelled.is_set() and time.monotonic() < deadline:
                if not all(item.is_alive() for item in listeners):
                    break
                hooks = [SystemHook._HOOKS.get(item.ident) for item in listeners]
                if all(hook is not None and bool(hook._hook) for hook in hooks):
                    ready = True
                    break
                if session.cancelled.wait(0.02):
                    break
            if ready and not session.cancelled.is_set():
                self.messages.put((session, "listeners_ready", None))
                # Detect a hook that dies after readiness instead of claiming ARMED forever.
                while not session.cancelled.wait(0.1):
                    if session.fired:
                        return
                    if not all(item.is_alive() for item in listeners):
                        self.messages.put((session, "input_failed", None))
                        return
            else:
                self.messages.put((session, "input_failed", None))
        except Exception:
            self.messages.put((session, "input_failed", None))
        finally:
            self.stop_listeners(listeners)

    @staticmethod
    def stop_listeners(listeners):
        for listener in listeners:
            try:
                listener.stop()
            except Exception:
                pass

    def camera_worker(self, session):
        import cv2
        # A timed-out driver may still own the previous handle. Never race it.
        if not self.camera_guard.acquire(blocking=False):
            self.messages.put((session, "camera_ready", False))
            return
        camera = None
        frame = rgb = ppm = None
        try:
            for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF):
                if session.cancelled.is_set() or session.camera_stop.is_set():
                    return
                camera = cv2.VideoCapture(0, backend)
                if camera.isOpened():
                    break
                camera.release()
                camera = None
            if camera is None or not camera.isOpened():
                self.messages.put((session, "camera_ready", False))
                return
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            for _ in range(3):
                if session.cancelled.is_set() or session.camera_stop.is_set():
                    return
                ok, frame = camera.read()
                frame = None
                if not ok:
                    self.messages.put((session, "camera_ready", False))
                    return
            self.messages.put((session, "camera_ready", True))
            while not session.cancelled.is_set() and not session.camera_stop.is_set():
                # Discard ongoing reads; capture starts with a new read after request.
                ok, frame = camera.read()
                frame = None
                if not ok:
                    self.messages.put((session, "camera_failed", None))
                    return
                if session.capture.is_set():
                    ok, frame = camera.read()
                    if not ok or frame is None:
                        self.messages.put((session, "photo", None))
                        return
                    height, width = frame.shape[:2]
                    max_width, max_height = self.capture_size
                    ratio = min(max_width / width, max_height / height, 1)
                    frame = cv2.resize(frame, (max(1, int(width * ratio)),
                                               max(1, int(height * ratio))))
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width = rgb.shape[:2]
                    ppm = f"P6\n{width} {height}\n255\n".encode("ascii") + rgb.tobytes()
                    with session.gate:
                        if not session.cancelled.is_set() and not session.camera_stop.is_set():
                            self.messages.put((session, "photo", ppm))
                    return
                if session.cancelled.wait(0.025):
                    return
        except Exception:
            self.messages.put((session, "camera_failed", None))
        finally:
            frame = rgb = ppm = None
            try:
                if camera is not None:
                    camera.release()
            finally:
                self.camera_guard.release()

    def alarm_worker(self, session):
        import winsound
        # Prevent overlap with a final short tone from a cancelled session.
        while not session.alarm_stop.is_set():
            if self.audio_guard.acquire(timeout=0.05):
                break
        else:
            return
        try:
            deadline = time.monotonic() + 10
            while not session.alarm_stop.is_set() and time.monotonic() < deadline:
                for pitch, duration in self.tones:
                    if session.alarm_stop.is_set() or time.monotonic() >= deadline:
                        return
                    try:
                        winsound.Beep(pitch, duration)
                    except RuntimeError:
                        return  # visual reveal remains usable
                    if session.alarm_stop.wait(0.035):
                        return
        finally:
            self.audio_guard.release()

    def reveal(self, session):
        if not self.current(session) or self.state != "ARMED":
            return
        self.phase = "reveal"
        self.set_state("TRIGGERED")
        self.root.attributes("-fullscreen", True)
        self.root.lift()
        self.root.focus_force()
        self.heading.configure(text="CAUGHT IN 4K", fg=RED)
        self.subtitle.configure(text="BRO THOUGHT NOBODY WOULD NOTICE")
        self.action.configure(text="STOP ALARM & RESET", command=self.reset)
        self.detail.configure(text="The 4K part is a joke. The awkwardness is real. Alarm stops after 10 seconds.")
        self.photo_label.configure(text="Getting your reaction…" if self.prepared else CAMERA_FAILED)
        threading.Thread(target=self.alarm_worker, args=(session,), daemon=True).start()
        self.capture_size = (max(220, min(960, self.root.winfo_screenwidth() - 100)),
                             max(100, min(540, self.root.winfo_screenheight() - 380)))
        if self.prepared:
            self.photo_pending = True
            session.capture.set()
            self.root.after(3000, lambda: self.photo_timeout(session))

    def photo_timeout(self, session):
        if self.current(session) and self.photo_pending:
            self.photo_pending = False
            session.camera_stop.set()
            self.photo_label.configure(image="", text=CAMERA_FAILED)

    def poll(self):
        if self.closed:
            return
        try:
            while True:
                session, kind, data = self.messages.get_nowait()
                if not self.current(session):
                    continue
                if kind == "camera_ready":
                    self.begin_countdown(session, data)
                elif kind == "camera_failed":
                    if self.phase == "camera":
                        self.begin_countdown(session, False)
                    else:
                        self.prepared = False
                        self.detail.configure(text="Camera unavailable. The alarm and reveal still work.")
                        if self.state == "TRIGGERED":
                            self.photo_timeout(session)
                elif kind == "listeners_ready" and self.phase == "listeners":
                    with session.gate:
                        if not session.cancelled.is_set():
                            session.accepting = True
                    self.phase = "watching"
                    self.set_state("ARMED")
                    self.heading.configure(text="System Armed.")
                    self.subtitle.configure(text="This laptop is being watched. Don't touch it.")
                    self.photo_label.configure(text="Go on. Act natural.")
                    self.action.configure(text="DISARM", command=self.reset)
                elif kind == "input_failed" and self.state in ("ARMING", "ARMED"):
                    self.reset("Global input monitoring failed. Please try again.")
                elif kind == "trigger":
                    self.reveal(session)
                elif kind == "photo" and self.state == "TRIGGERED" and self.photo_pending:
                    self.photo_pending = False
                    if data:
                        try:
                            self.photo = tk.PhotoImage(data=data, format="PPM")
                            self.photo_label.configure(image=self.photo, text="")
                        except tk.TclError:
                            self.photo_label.configure(image="", text=CAMERA_FAILED)
                    else:
                        self.photo_label.configure(image="", text=CAMERA_FAILED)
                data = None
        except queue.Empty:
            pass
        self.poll_id = self.root.after(25, self.poll)

    def cancel_session(self):
        session = self.session
        self.session = None
        if session is not None:
            with session.gate:
                session.accepting = False
                session.cancelled.set()
                session.camera_stop.set()
                session.alarm_stop.set()
                listeners = list(session.listeners)
            # pynput stop() can wait for its message-loop startup. Never call on Tk.
            if listeners:
                threading.Thread(target=self.stop_listeners, args=(listeners,),
                                 daemon=True).start()
        self.photo_pending = False
        self.photo_label.configure(image="")
        self.photo = None
        # Drop any queued photo payload rather than retaining it until the next poll.
        try:
            while True:
                self.messages.get_nowait()
        except queue.Empty:
            pass

    def reset(self, error=""):
        if self.closed:
            return
        self.cancel_session()
        self.root.attributes("-fullscreen", False)
        self.phase = ""
        self.show_idle(error)

    def close(self):
        if self.closed:
            return
        self.cancel_session()
        self.closed = True
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def main():
    root = tk.Tk()
    root.withdraw()
    try:
        import cv2  # noqa: F401 -- check installation before enabling the UI
        import pynput  # noqa: F401
        import winsound  # noqa: F401
    except ImportError:
        messagebox.showerror("CAUGHT! — Setup needed",
                             "Install the dependencies first:\npython -m pip install -r requirements.txt",
                             parent=root)
        root.destroy()
        return
    App(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
