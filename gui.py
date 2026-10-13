"""tkinter GUI."""

import tkinter as tk
from tkinter import ttk, messagebox

from generator import (MIN_LENGTH, MAX_LENGTH, RECOMMENDED,
                       generate_password, calculate_entropy, rate_entropy)

BG = "#1e1f26"
FG = "#e8e8ee"
FIELD = "#2c2d38"
ACCENT = "#4f7cff"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DecodeLabs - Secure Password Generator")
        self.geometry("520x560")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.length_var = tk.IntVar(value=RECOMMENDED)
        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.show_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()
        self.info_var = tk.StringVar()

        self._style()
        self._build()

        # auto-regenerate when options change
        for v in (self.lower_var, self.upper_var, self.digits_var, self.symbols_var):
            v.trace_add("write", self._on_option)

        self.generate()

    # ---------------- styling ----------------
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        s.configure("Sub.TLabel", foreground="#9a9ab0")

        s.configure("TCheckbutton", background=BG, foreground=FG,
                    font=("Segoe UI", 10), indicatorbackground=FIELD,
                    indicatorforeground="white", focuscolor=BG)
        s.map("TCheckbutton",
              background=[("active", BG)],
              indicatorbackground=[("selected", ACCENT), ("!selected", FIELD)])

        s.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        s.configure("Accent.TButton", background=ACCENT, foreground="white")
        s.map("Accent.TButton", background=[("active", "#3d65d8")])

        s.configure("Horizontal.TScale", background=BG, troughcolor=FIELD)
        s.configure("Meter.Horizontal.TProgressbar", troughcolor=FIELD,
                    background="#5cb85c", thickness=12)

    # ---------------- layout ----------------
    def _build(self):
        pad = {"padx": 24}

        ttk.Label(self, text="Password Generator", style="Title.TLabel").pack(pady=(20, 0), anchor="w", **pad)
        ttk.Label(self, text="Cryptographically secure  |  secrets + string",
                  style="Sub.TLabel").pack(anchor="w", **pad)

        # password display
        box = ttk.Frame(self)
        box.pack(fill="x", pady=(18, 4), **pad)
        self.entry = tk.Entry(box, textvariable=self.password_var, font=("Consolas", 14),
                              bg=FIELD, fg="#ffffff", relief="flat", justify="center",
                              readonlybackground=FIELD, state="readonly")
        self.entry.pack(fill="x", ipady=12)

        ttk.Checkbutton(self, text="Show password", variable=self.show_var,
                        command=self._toggle_show).pack(anchor="w", pady=(4, 0), **pad)

        # strength meter
        self.meter = ttk.Progressbar(self, style="Meter.Horizontal.TProgressbar", maximum=128)
        self.meter.pack(fill="x", pady=(12, 4), **pad)
        self.strength_lbl = ttk.Label(self, text="")
        self.strength_lbl.pack(anchor="w", **pad)
        ttk.Label(self, textvariable=self.info_var, style="Sub.TLabel").pack(anchor="w", **pad)

        # length
        lf = ttk.Frame(self)
        lf.pack(fill="x", pady=(18, 0), **pad)
        ttk.Label(lf, text="Length:").pack(side="left")
        self.len_lbl = ttk.Label(lf, text=str(RECOMMENDED), font=("Segoe UI", 10, "bold"))
        self.len_lbl.pack(side="right")

        # create labels BEFORE the scale so callbacks never hit missing widgets
        self.nist_lbl = ttk.Label(self, text="", style="Sub.TLabel")

        self.scale = ttk.Scale(self, from_=MIN_LENGTH, to=MAX_LENGTH, orient="horizontal",
                               command=self._on_slide)
        self.scale.pack(fill="x", pady=(4, 0), **pad)
        self.nist_lbl.pack(anchor="w", **pad)
        self.scale.set(RECOMMENDED)

        # options
        of = ttk.Frame(self)
        of.pack(fill="x", pady=(14, 0), **pad)
        ttk.Checkbutton(of, text="Lowercase (a-z)", variable=self.lower_var).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Checkbutton(of, text="Uppercase (A-Z)", variable=self.upper_var).grid(row=0, column=1, sticky="w", padx=30, pady=2)
        ttk.Checkbutton(of, text="Numbers (0-9)", variable=self.digits_var).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Checkbutton(of, text="Symbols (@ # $ ...)", variable=self.symbols_var).grid(row=1, column=1, sticky="w", padx=30, pady=2)

        # buttons
        bf = ttk.Frame(self)
        bf.pack(fill="x", pady=22, **pad)
        ttk.Button(bf, text="Generate", style="Accent.TButton",
                   command=self.generate).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(bf, text="Copy", command=self.copy).pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.bind("<Return>", lambda e: self.generate())

    # ---------------- handlers ----------------
    def _on_slide(self, value):
        n = int(float(value))
        if n == self.length_var.get() and self.password_var.get():
            return  # no change, avoid needless regeneration
        self.length_var.set(n)
        self.len_lbl.config(text=str(n))
        if n < RECOMMENDED:
            self.nist_lbl.config(text=f"Below NIST recommended {RECOMMENDED}+ characters",
                                 foreground="#f0ad4e")
        else:
            self.nist_lbl.config(text="Meets NIST SP 800-63-4 length guidance",
                                 foreground="#5cb85c")
        if self.password_var.get():
            self.generate()

    def _on_option(self, *_):
        # always keep at least one character type ticked
        if not any(v.get() for v in (self.lower_var, self.upper_var,
                                     self.digits_var, self.symbols_var)):
            self.lower_var.set(True)  # re-triggers this callback, which regenerates
            return
        self.generate()

    def _toggle_show(self):
        self.entry.config(show="" if self.show_var.get() else "•")

    def generate(self):
        try:
            pwd, pool = generate_password(
                self.length_var.get(), self.lower_var.get(), self.upper_var.get(),
                self.digits_var.get(), self.symbols_var.get())
        except ValueError as e:
            messagebox.showwarning("Invalid options", str(e))
            return

        bits = calculate_entropy(len(pwd), pool)
        label, color = rate_entropy(bits)

        self.password_var.set(pwd)
        self.meter["value"] = min(bits, 128)
        ttk.Style(self).configure("Meter.Horizontal.TProgressbar", background=color)
        self.strength_lbl.config(text=label, foreground=color, font=("Segoe UI", 10, "bold"))
        self.info_var.set(f"Entropy: {bits:.1f} bits  |  Pool: {pool}  |  Length: {len(pwd)}")

    def copy(self):
        pwd = self.password_var.get()
        if pwd:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.info_var.set("Copied to clipboard")