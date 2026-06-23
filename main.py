#!/usr/bin/env python3
"""Dark Overlay — chống nhìn trộm với khoá cứng màn hình."""

import tkinter as tk
import json
import os
from AppKit import NSApp
from pynput import keyboard as pynkb

GLOBAL_UNLOCK_HOTKEY = "<ctrl>+<shift>+l"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_CONFIG = {"brightness": 0.85, "contrast": 0, "w": 200, "h": 200, "x": -1, "y": -1}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            return {**DEFAULT_CONFIG, **json.load(open(CONFIG_FILE))}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


class DarkOverlay:
    def __init__(self):
        cfg = load_config()
        self.brightness = cfg["brightness"]
        self.contrast   = cfg["contrast"]
        self.active     = True
        self.locked     = False
        self._ns_win    = None

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        W, H = cfg["w"], cfg["h"]
        x = cfg["x"] if cfg["x"] >= 0 else sw - W - 20
        y = cfg["y"] if cfg["y"] >= 0 else sh - H - 20
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        self.hint = tk.Label(self.root, text="", font=("Arial", 10),
                             fg="white", padx=5, pady=3)

        self._apply()
        self._bind()
        self.root.focus_force()

        # Lấy NSWindow sau khi render xong
        self.root.after(300, self._find_ns_window)

        # Global hotkey để mở khoá khi click-through đang bật
        self._start_global_hotkey()

        self.root.mainloop()

    # ── NSWindow ────────────────────────────────────────────────────────────

    def _find_ns_window(self):
        wins = NSApp.orderedWindows()
        if wins:
            self._ns_win = wins[0]

    def _set_clickthrough(self, enabled: bool):
        if self._ns_win:
            self._ns_win.setIgnoresMouseEvents_(enabled)

    # ── global hotkey ────────────────────────────────────────────────────────

    def _start_global_hotkey(self):
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        hotkey = pynkb.HotKey(
            pynkb.HotKey.parse(GLOBAL_UNLOCK_HOTKEY),
            lambda: self.root.after(0, self._toggle_lock),
        )
        listener = pynkb.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release),
        )
        listener.daemon = True
        listener.start()

    # ── apply ────────────────────────────────────────────────────────────────

    def _apply(self):
        alpha = self.brightness if self.active else 0.0
        c = int(self.contrast)
        color = f"#{c:02x}{c:02x}{c:02x}"
        self.root.configure(bg=color)
        self.hint.configure(bg=color)
        self.root.attributes("-alpha", alpha)

    # ── lock ─────────────────────────────────────────────────────────────────

    def _toggle_lock(self):
        self.locked = not self.locked
        if self.locked:
            self._set_clickthrough(True)   # chuột xuyên qua app
            self._toast("🔒 KHOÁ  |  Ctrl+Shift+L = mở")
        else:
            self._set_clickthrough(False)  # bắt chuột lại
            self.root.focus_force()
            self._toast("🔓 ĐÃ MỞ KHOÁ")

    # ── save config ──────────────────────────────────────────────────────────

    def _save(self):
        g = self.root.geometry()          # "WxH+X+Y"
        parts = g.replace("+", "x").split("x")
        save_config({
            "brightness": self.brightness,
            "contrast":   self.contrast,
            "w": int(parts[0]),
            "h": int(parts[1]),
            "x": int(parts[2]),
            "y": int(parts[3]),
        })

    # ── controls ─────────────────────────────────────────────────────────────

    def _toggle(self):
        self.active = not self.active
        self._apply()
        self._toast("BẬT" if self.active else "TẮT")

    def _brightness(self, d):
        self.brightness = round(max(0.05, min(1.0, self.brightness + d)), 2)
        self._apply()
        self._save()
        self._toast(f"Độ sáng: {int(self.brightness * 100)}%")

    def _contrast(self, d):
        self.contrast = round(max(0, min(128, self.contrast + d)))
        self._apply()
        self._save()
        self._toast(f"Tương phản: {int(self.contrast / 128 * 100)}%")

    def _resize(self, dw, dh):
        if self.locked:
            return
        g = self.root.geometry().split("+")
        wh = g[0].split("x")
        w = max(60, int(wh[0]) + dw)
        h = max(60, int(wh[1]) + dh)
        self.root.geometry(f"{w}x{h}+{g[1]}+{g[2]}")
        self._save()
        self._toast(f"{w} × {h}")

    # ── drag ─────────────────────────────────────────────────────────────────

    def _drag_start(self, e):
        if self.locked:
            return
        self._ox, self._oy = e.x, e.y
        self.root.focus_force()

    def _drag_move(self, e):
        if self.locked:
            return
        x = self.root.winfo_x() + e.x - self._ox
        y = self.root.winfo_y() + e.y - self._oy
        self.root.geometry(f"+{x}+{y}")
        self._save()

    # ── toast ─────────────────────────────────────────────────────────────────

    def _toast(self, text):
        self.hint.configure(text=text)
        self.hint.place(relx=0.5, rely=0.85, anchor="center")
        if hasattr(self, "_job"):
            self.root.after_cancel(self._job)
        self._job = self.root.after(2000, self.hint.place_forget)

    # ── bindings ──────────────────────────────────────────────────────────────

    def _bind(self):
        r = self.root
        r.bind("<Escape>",       lambda e: (self._save(), r.destroy()))
        r.bind("<space>",        lambda e: self._toggle())
        r.bind("<l>",            lambda e: self._toggle_lock())
        r.bind("<L>",            lambda e: self._toggle_lock())

        r.bind("<plus>",         lambda e: self._brightness(+0.05))
        r.bind("<equal>",        lambda e: self._brightness(+0.05))
        r.bind("<minus>",        lambda e: self._brightness(-0.05))

        r.bind("<bracketright>", lambda e: self._contrast(+8))
        r.bind("<bracketleft>",  lambda e: self._contrast(-8))

        r.bind("<Up>",           lambda e: self._resize(0, -20))
        r.bind("<Down>",         lambda e: self._resize(0, +20))
        r.bind("<Right>",        lambda e: self._resize(+20, 0))
        r.bind("<Left>",         lambda e: self._resize(-20, 0))

        r.bind("<ButtonPress-1>", self._drag_start)
        r.bind("<B1-Motion>",     self._drag_move)


if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║             Dark Overlay                 ║")
    print("╠══════════════════════════════════════════╣")
    print("║  L              khoá / mở khoá          ║")
    print("║  Ctrl+Shift+L   mở khoá (global)        ║")
    print("║  Space          bật / tắt               ║")
    print("║  +  /  -        độ sáng tăng / giảm     ║")
    print("║  ]  /  [        tương phản tăng / giảm  ║")
    print("║  ↑↓←→           thay đổi kích thước     ║")
    print("║  Kéo chuột      di chuyển               ║")
    print("║  Escape         thoát                   ║")
    print("╚══════════════════════════════════════════╝")
    DarkOverlay()
