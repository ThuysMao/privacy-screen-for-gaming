#!/usr/bin/env python3
"""Dark Overlay — Windows — chống nhìn trộm."""

import sys
import os
import json
import ctypes
import tkinter as tk
from pynput import keyboard as pynkb

# Khi đóng gói bằng PyInstaller, config nằm cạnh file .exe
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE          = os.path.join(BASE_DIR, "config.json")
GLOBAL_UNLOCK_HOTKEY = "<ctrl>+<shift>+l"
DEFAULT_CONFIG       = {"brightness": 0.85, "contrast": 0,
                        "w": 200, "h": 200, "x": -1, "y": -1}

# Windows API — click-through
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
WS_EX_TRANSPARENT = 0x00000020


# ── config ───────────────────────────────────────────────────────────────────

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


# ── app ───────────────────────────────────────────────────────────────────────

class DarkOverlay:
    def __init__(self):
        cfg = load_config()
        self.brightness = cfg["brightness"]
        self.contrast   = cfg["contrast"]
        self.active     = True
        self.locked     = False
        self._hwnd      = None

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        W, H = cfg["w"], cfg["h"]
        x = cfg["x"] if cfg["x"] >= 0 else sw - W - 20
        y = cfg["y"] if cfg["y"] >= 0 else sh - H - 20
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        self.hint = tk.Label(self.root, text="", font=("Segoe UI", 10),
                             fg="white", padx=5, pady=3)

        self._apply()
        self._bind()
        self.root.focus_force()
        self.root.after(300, self._find_hwnd)
        self._start_global_hotkey()
        self.root.mainloop()

    # ── Windows HWND / click-through ─────────────────────────────────────────

    def _find_hwnd(self):
        self.root.update()
        self._hwnd = self.root.winfo_id()

    def _set_clickthrough(self, enabled: bool):
        if not self._hwnd:
            return
        cur = ctypes.windll.user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
        if enabled:
            new = cur | WS_EX_LAYERED | WS_EX_TRANSPARENT
        else:
            new = (cur | WS_EX_LAYERED) & ~WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(self._hwnd, GWL_EXSTYLE, new)

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

    # ── save config ──────────────────────────────────────────────────────────

    def _save(self):
        g = self.root.geometry().replace("+", "x").split("x")
        save_config({
            "brightness": self.brightness,
            "contrast":   self.contrast,
            "w": int(g[0]), "h": int(g[1]),
            "x": int(g[2]), "y": int(g[3]),
        })

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
            self._set_clickthrough(True)
            self._toast("🔒 KHOÁ  |  Ctrl+Shift+L = mở")
        else:
            self._set_clickthrough(False)
            self.root.focus_force()
            self._toast("🔓 ĐÃ MỞ KHOÁ")

    # ── controls ─────────────────────────────────────────────────────────────

    def _toggle(self):
        self.active = not self.active
        self._apply()
        self._toast("BẬT" if self.active else "TẮT")

    def _brightness(self, d):
        self.brightness = round(max(0.05, min(1.0, self.brightness + d)), 2)
        self._apply(); self._save()
        self._toast(f"Độ sáng: {int(self.brightness * 100)}%")

    def _contrast(self, d):
        self.contrast = round(max(0, min(128, self.contrast + d)))
        self._apply(); self._save()
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
    DarkOverlay()
