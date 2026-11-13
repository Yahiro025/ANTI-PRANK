"""CAUGHT! A visible, local, one-shot Windows prank demo. No data is saved."""
from __future__ import annotations

import queue
import secrets
import threading
import time
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox
from pathlib import Path


def load_display_font():
    """Register the bundled brand face privately; no installation or elevation."""
    try:
        import ctypes
        font = Path(__file__).resolve().parent / "assets" / "bricolage.ttf"
        if ctypes.windll.gdi32.AddFontResourceExW(str(font), 0x10, 0):
            return "Bricolage Grotesque 14pt"
    except (AttributeError, OSError):
        pass
    return "Segoe UI"


DISPLAY_FONT = load_display_font()

CREAM = "#FFF4DE"
INK = "#251C19"
RED = "#B92D24"
MUTED = "#6B574C"
PAPER = "#FFFBF2"
SAND = "#F3E1C4"
CAMERA_FAILED = "CAMERA FAILED, BUT YOU'RE STILL CAUGHT."


@dataclass
class Session:
    number: int
    sound_enabled: bool = False
    cancelled: threading.Event = field(default_factory=threading.Event)
    camera_stop: threading.Event = field(default_factory=threading.Event)
    capture: threading.Event = field(default_factory=threading.Event)
    alarm_stop: threading.Event = field(default_factory=threading.Event)
    gate: threading.Lock = field(default_factory=threading.Lock)
    accepting: bool = False
    fired: bool = False
    listeners: list = field(default_factory=list)


class Lookout(tk.Canvas):
    """The same small, geometric character used by the Android companion."""

    def __init__(self, parent):
        super().__init__(parent, width=160, height=144, bg=CREAM,
                         highlightthickness=0, takefocus=False)
        self.expression = "IDLE"
        self.bind("<Configure>", lambda _event: self.draw())

    def draw(self):
        self.delete("all")
        size = min(self.winfo_width(), self.winfo_height())
        scale = size / 100
        x = (self.winfo_width() - size) / 2
        def oval(a, b, c, d, color):
            self.create_oval(x+a*scale, b*scale, x+c*scale, d*scale,
                             fill=color, outline="")
        oval(27, 82, 45, 94, "#8A1E17")
        oval(55, 82, 73, 94, "#8A1E17")
        oval(14, 10, 86, 86, RED)
        oval(27, 22, 73, 68, CREAM)
        gaze = 7 if self.expression == "IDLE" else -5 if self.expression == "ARMING" else 0
        radius = 7 if self.expression == "ARMING" else 10
        oval(50+gaze-radius, 45-radius, 50+gaze+radius, 45+radius, INK)
        oval(46+gaze, 38, 51+gaze, 43, PAPER)
        oval(23, 63, 33, 69, "#C9453B")
        oval(67, 63, 77, 69, "#C9453B")


class App:
    def __init__(self, root):
        self.root = root
        self.messages = queue.Queue()
        self.phone_messages = queue.Queue()
        self.phone_watch = None
        self.phone_code = None
        self.phone_found = False
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
        root.geometry("960x760")
        root.minsize(680, 640)
        root.configure(bg=CREAM)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Escape>", lambda _event: self.reset())
        self.build_ui()
        self.show_idle()
        self.poll_id = root.after(25, self.poll)

    def build_ui(self):
        self.shell = tk.Frame(self.root, bg=CREAM, padx=32, pady=24)
        self.shell.pack(fill="both", expand=True)
        self.shell.columnconfigure(0, weight=1)
        self.shell.rowconfigure(1, weight=1)
        self.top = tk.Frame(self.shell, bg=CREAM)
        self.top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.brand = tk.Label(self.top, text="CAUGHT!", font=(DISPLAY_FONT, 20, "bold"),
                              bg=CREAM, fg=INK)
        self.brand.pack(side="left")
        self.state_label = tk.Label(self.top, font=("Segoe UI", 11, "bold"),
                                    padx=12, pady=6, bg=SAND, fg=INK)
        self.state_label.pack(side="right")
        self.stage_host = tk.Frame(self.shell, bg=CREAM)
        self.stage_host.grid(row=1, column=0, sticky="nsew")
        self.viewport = tk.Canvas(self.stage_host, bg=CREAM, highlightthickness=0,
                                  takefocus=True)
        self.viewport.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.stage_host, command=self.viewport.yview,
                                      bg=CREAM, troughcolor=CREAM, width=12)
        self.scrollbar.pack(side="right", fill="y")
        self.viewport.configure(yscrollcommand=self.scrollbar.set)
        self.stage = tk.Frame(self.viewport, bg=CREAM)
        self.stage_window = self.viewport.create_window(0, 0, window=self.stage, anchor="nw")
        self.viewport.bind("<Configure>", lambda event: self.fit_stage(event.width, event.height))
        self.stage.bind("<Configure>", lambda _event: self.fit_stage())
        self.root.bind("<MouseWheel>", lambda event: self.viewport.yview_scroll(
            -int(event.delta / 120), "units"))
        self.viewport.bind("<Up>", lambda _event: self.viewport.yview_scroll(-1, "units"))
        self.viewport.bind("<Down>", lambda _event: self.viewport.yview_scroll(1, "units"))
        self.stage.columnconfigure(0, weight=1)
        self.stage.rowconfigure(3, weight=1)
        self.mascot = Lookout(self.stage)
        self.mascot.grid(row=0, column=0, pady=(0, 8))
        self.heading = tk.Label(self.stage, bg=CREAM, fg=INK,
                                font=(DISPLAY_FONT, 38, "bold"), wraplength=800)
        self.heading.grid(row=1, column=0, pady=(0, 8))
        self.subtitle = tk.Label(self.stage, bg=CREAM, fg=MUTED,
                                 font=("Segoe UI", 13), wraplength=760)
        self.subtitle.grid(row=2, column=0, pady=(0, 12))
        self.photo_label = tk.Label(self.stage, bg=CREAM, fg=RED, padx=16, pady=8,
                                    font=("Segoe UI", 13, "bold"), wraplength=720)
        self.photo_label.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
        self.detail = tk.Label(self.shell, bg=CREAM, fg=MUTED,
                               font=("Segoe UI", 11), wraplength=760)
        self.detail.grid(row=2, column=0, pady=(8, 12))
        self.controls = tk.Frame(self.shell, bg=CREAM)
        self.controls.grid(row=3, column=0)
        self.action = tk.Button(self.controls, font=("Segoe UI", 14, "bold"), bg=RED,
                                fg=CREAM, activebackground=INK, activeforeground=CREAM,
                                highlightcolor=INK, highlightthickness=2, highlightbackground=CREAM,
                                relief="flat", width=26, padx=16, pady=12, cursor="hand2")
        self.action.grid(row=0, column=0, sticky="ew")
        self.phone_button = tk.Button(self.controls, text="PHONE WATCH", command=self.toggle_phone_watch,
                                      font=("Segoe UI", 11, "bold"), bg=CREAM, fg=INK,
                                      activebackground=SAND, relief="flat", pady=10,
                                      highlightcolor=RED, highlightbackground=CREAM,
                                      highlightthickness=2, cursor="hand2")
        self.phone_button.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.code_label = tk.Label(self.controls, bg=CREAM, fg=RED,
                                   font=("Consolas", 23, "bold"))
        self.code_label.grid(row=2, column=0)
        self.code_label.grid_remove()
        self.phone_label = tk.Label(self.controls, text="", font=("Segoe UI", 11), bg=CREAM,
                                    fg=INK, wraplength=720)
        self.phone_label.grid(row=3, column=0, pady=(0, 4))
        self.silent = tk.BooleanVar(value=True)
        self.sound_control = tk.Checkbutton(self.controls, text="Silent mode (no alarm sound)",
                                            variable=self.silent, bg=CREAM, fg=MUTED,
                                            activebackground=CREAM, selectcolor=PAPER,
                                            font=("Segoe UI", 11), pady=6)
        self.sound_control.grid(row=4, column=0)
        self.bottom = tk.Frame(self.shell, bg=CREAM)
        self.bottom.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        self.bottom.columnconfigure(0, weight=1)
        self.privacy = tk.Label(self.bottom, text="No keys recorded  /  Photo stays in memory",
                                font=("Segoe UI", 10), bg=CREAM, fg=MUTED)
        self.privacy.grid(row=0, column=0, sticky="w")
        self.exit_button = tk.Button(self.bottom, text="Exit  /  Alt+F4", command=self.close,
                                      font=("Segoe UI", 10), bg=CREAM, fg=MUTED,
                                      relief="flat", padx=12, pady=8, cursor="hand2")
        self.exit_button.grid(row=0, column=1, sticky="e")
        self.root.bind("<Configure>", self.resize_text)

    def fit_stage(self, width=None, height=None):
        width = width or self.viewport.winfo_width()
        height = height or self.viewport.winfo_height()
        self.viewport.itemconfigure(self.stage_window, width=width,
                                    height=max(height, self.stage.winfo_reqheight()))
        self.viewport.configure(scrollregion=self.viewport.bbox("all"))

    def resize_text(self, event):
        if event.widget is not self.root:
            return
        width = max(300, event.width - 80)
        self.heading.configure(wraplength=width,
                               font=(DISPLAY_FONT, max(28, min(44, event.width // 24)), "bold"))
        for label in (self.subtitle, self.detail, self.photo_label, self.phone_label):
            label.configure(wraplength=width)
        size = 64 if event.height < 700 else 104
        self.mascot.configure(width=size+16, height=size)

    def set_state(self, value):
        self.state = value
        self.state_label.configure(text=f"STATE: {value}")
        self.mascot.expression = value
        self.mascot.draw()
        triggered = value == "TRIGGERED"
        bg, fg = (RED, CREAM) if triggered else (CREAM, INK)
        for widget in (self.root, self.shell, self.top, self.stage_host,
                       self.viewport, self.stage, self.controls, self.bottom):
            widget.configure(bg=bg)
        for label in (self.brand, self.heading, self.subtitle, self.detail, self.privacy):
            label.configure(bg=bg, fg=fg if triggered else MUTED if label in
                            (self.subtitle, self.detail, self.privacy) else INK)
        self.state_label.configure(bg=CREAM if triggered else SAND, fg=INK)
        self.scrollbar.configure(bg=bg, troughcolor=bg)
        self.exit_button.configure(bg=bg, fg=fg)
        self.action.configure(bg=CREAM if triggered else INK if value == "ARMED" else RED,
                              fg=INK if triggered else CREAM, highlightbackground=bg)
        self.photo_label.configure(bg=PAPER if triggered else CREAM, fg=INK if triggered else RED)
        if triggered:
            self.viewport.yview_moveto(0)
            self.mascot.grid_remove()
            self.phone_button.grid_remove()
            self.phone_label.grid_remove()
            self.sound_control.grid_remove()
            self.code_label.grid_remove()
        else:
            self.viewport.yview_moveto(0)
            self.mascot.grid()
            self.phone_button.grid()
            self.phone_label.grid()
            self.sound_control.grid()
        self.sound_control.configure(state="normal" if value == "IDLE" else "disabled")

    def show_idle(self, error=""):
        self.set_state("IDLE")
        self.heading.configure(text="Touch it. Regret it.", fg=INK)
        self.subtitle.configure(text="Your friends brought pranks. You brought consequences.")
        self.photo_label.configure(image="", text="One touch. One alarm. One very awkward photo.")
        self.detail.configure(text=error or "Arming visibly activates the webcam. Use with consenting teammates.")
        self.action.configure(text="ARM SYSTEM", command=self.arm, state="normal")
        self.phone_button.configure(state="normal")
        if self.phone_watch is None:
            self.phone_label.configure(text="")

    def current(self, session):
        return not self.closed and self.session is session and not session.cancelled.is_set()

    def arm(self):
        if self.state != "IDLE":
            return
        if self.phone_watch is not None:
            self.stop_phone_watch()
        self.phone_button.configure(state="disabled")
        self.serial += 1
        session = self.session = Session(self.serial, sound_enabled=not self.silent.get())
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

    def toggle_phone_watch(self):
        if self.phone_watch is not None:
            self.stop_phone_watch()
            return
        if self.state != "IDLE":
            return
        try:
            from phone_watch import PhoneWatch
        except ImportError:
            self.phone_label.configure(text="Bluetooth support missing. Install requirements.txt and try again.")
            return
        self.phone_code = secrets.token_hex(4).upper()
        self.code_label.configure(text=self.phone_code)
        self.code_label.grid()
        self.phone_found = False
        self.phone_watch = PhoneWatch(self.phone_code, lambda watch, kind, data:
                                      self.phone_messages.put((watch, kind, data)))
        self.phone_button.configure(text="STOP PHONE WATCH")
        self.phone_label.configure(text=f"Phone code: {self.phone_code}   ·   Enter it in the Android app, then start lookout.")
        self.phone_watch.start()

    def stop_phone_watch(self):
        watch = self.phone_watch
        self.phone_watch = None
        self.phone_found = False
        if watch is not None:
            watch.stop()
        self.phone_button.configure(text="PHONE WATCH")
        self.phone_label.configure(text="")
        self.code_label.grid_remove()

    def poll_phone(self):
        try:
            while True:
                watch, kind, data = self.phone_messages.get_nowait()
                if watch is not self.phone_watch:
                    continue
                if kind == "near":
                    self.phone_found = True
                    self.phone_label.configure(text=f"Phone nearby · {self.phone_code} · Leave with your phone to arm.")
                elif kind == "scanning" and not self.phone_found:
                    self.phone_label.configure(text=f"Phone code: {self.phone_code} · Waiting for Android lookout nearby.")
                elif kind == "away":
                    self.stop_phone_watch()
                    self.phone_label.configure(text="Phone signal weak or lost. Arming the laptop…")
                    self.arm()
                elif kind == "error":
                    self.stop_phone_watch()
                    self.phone_label.configure(text="Bluetooth scanning failed. Turn on Windows Bluetooth and try again.")
        except queue.Empty:
            pass

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
        if not session.sound_enabled:
            return
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
        self.heading.configure(text="CAUGHT IN 4K", fg=CREAM)
        self.subtitle.configure(text="BRO THOUGHT NOBODY WOULD NOTICE")
        self.action.configure(text="STOP ALARM & RESET", command=self.reset)
        self.detail.configure(text="Silent reveal. No alarm sound. Esc resets." if not session.sound_enabled
                              else "The 4K part is a joke. Alarm stops after 10 seconds. Esc resets.")
        self.photo_label.configure(text="Getting your reaction…" if self.prepared else CAMERA_FAILED)
        threading.Thread(target=self.alarm_worker, args=(session,), daemon=True).start()
        self.root.update_idletasks()
        self.capture_size = (max(1, self.photo_label.winfo_width() - 32),
                             max(1, self.photo_label.winfo_height() - 16))
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
        self.poll_phone()
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
                    self.heading.configure(text="System armed")
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
        self.stop_phone_watch()
        self.cancel_session()
        self.closed = True
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
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
