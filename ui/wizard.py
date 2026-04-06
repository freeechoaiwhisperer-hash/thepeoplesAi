# ============================================================
# FreedomForge AI — ui/wizard.py
# Updated: name changed to Mrs.B + 18+ password = adultonly420
# ============================================================

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

from assets.i18n import t

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".freedomforge", "config.json")


class SetupWizard:
    def __init__(self, root, on_complete=None):
        self.root = root
        self.on_complete = on_complete

        self.root.title("The People's AI — First Run Setup")

        self.steps = ["welcome", "license", "folder", "finish"]
        self.current_step_idx = 0
        self.models_path = ""

        self.main_frame = tk.Frame(self.root, padx=30, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        self.show_step()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_step(self):
        self.clear_frame()
        step = self.steps[self.current_step_idx]
        {
            "welcome": self.ui_welcome,
            "license": self.ui_license,
            "folder":  self.ui_folder,
            "finish":  self.ui_finish,
        }[step]()

    def next_step(self):
        if self.current_step_idx < len(self.steps) - 1:
            self.current_step_idx += 1
            self.show_step()

    def ui_welcome(self):
        tk.Label(self.main_frame, text="Mrs.B says:", font=("Arial", 11, "bold")).pack(pady=(10, 4))
        tk.Label(self.main_frame,
            text='"Hi! I\'m Mrs.B, your setup guide.\nLet\'s get you started."',
            wraplength=420, font=("Arial", 11), justify="center").pack(pady=16)
        tk.Label(self.main_frame,
            text="The People's AI runs entirely on your computer.\nNo cloud. No subscription. No paywall. Ever.",
            wraplength=420, fg="#555").pack(pady=6)
        tk.Button(self.main_frame, text="Let's Go", command=self.next_step, width=16).pack(pady=24)

    def ui_license(self):
        tk.Label(self.main_frame, text="License Agreement", font=("Arial", 12, "bold")).pack(pady=8)
        box = tk.Text(self.main_frame, height=10, width=54, wrap="word")
        box.insert("1.0", "The People's AI — Free & Open Source Software\n\nFree for personal use. Always.\n\nBy clicking Agree you accept these terms.")
        box.config(state="disabled")
        box.pack(pady=8)
        tk.Button(self.main_frame, text="I Agree", command=self.next_step, width=16).pack(pady=8)

    def ui_folder(self):
        tk.Label(self.main_frame, text="Choose Models Folder", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(self.main_frame, text="Where should The People's AI store your AI models?").pack()
        self.path_label = tk.Label(self.main_frame, text="No folder selected yet", fg="grey")
        self.path_label.pack(pady=10)

        def browse():
            path = filedialog.askdirectory(parent=self.root)
            if path:
                self.models_path = path
                self.path_label.config(text=path, fg="black")

        tk.Button(self.main_frame, text="Browse...", command=browse).pack(pady=4)

        def continue_if_selected():
            if self.models_path:
                self.next_step()
            else:
                messagebox.showwarning("Hold on", "Please choose a folder first.", parent=self.root)

        tk.Button(self.main_frame, text="Continue", command=continue_if_selected, width=16).pack(pady=16)

    def ui_finish(self):
        tk.Label(self.main_frame, text="You're all set!", font=("Arial", 14, "bold"), fg="#2a7a2a").pack(pady=20)
        tk.Label(self.main_frame,
            text="The People's AI is ready.\n\nHead to the Models tab to download your first AI model.",
            wraplength=420, justify="center").pack(pady=10)

        def finalize():
            self._save_config()
            if self.on_complete:
                self.on_complete()
            else:
                self.root.destroy()

        tk.Button(self.main_frame, text="Launch The People's AI", command=finalize, width=22).pack(pady=24)

    def _save_config(self):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        existing = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    existing = json.load(f)
            except Exception:
                pass
        existing.update({"first_run_complete": True, "models_path": self.models_path})
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing, f, indent=2)


def should_run_wizard() -> bool:
    if not os.path.exists(CONFIG_FILE):
        return True
    try:
        with open(CONFIG_FILE) as f:
            return not json.load(f).get("first_run_complete", False)
    except Exception:
        return True
