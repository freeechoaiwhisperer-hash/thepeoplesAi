# ============================================================
# FreedomForge AI — ui/top_bar.py
# Clean top bar with Kill Switch, CPU/GPU usage, single mic toggle
# ============================================================

import customtkinter as ctk
import psutil
import threading

class TopBar(ctk.CTkFrame):
    def __init__(self, master, app, theme: dict):
        super().__init__(master, fg_color=theme["bg_topbar"], height=50)
        self.app = app
        self.theme = theme
        self.pack(fill="x")
        self._build()

    def _build(self):
        T = self.theme

        # Left: App name
        ctk.CTkLabel(self, text="The People's AI", font=("Arial", 16, "bold"), text_color=T["gold"]).pack(side="left", padx=16)

        # CPU / GPU usage
        self.status_label = ctk.CTkLabel(self, text="CPU: --% | GPU: --%", font=("Arial", 11), text_color=T["text_secondary"])
        self.status_label.pack(side="left", padx=20)

        # Kill Switch
        self.kill_btn = ctk.CTkButton(self, text="🔴 Kill Internet", width=140, height=32, fg_color="#6a0000", hover_color="#8a0000", command=self.app.toggle_kill_switch)
        self.kill_btn.pack(side="right", padx=8)

        # Single mic toggle (removed duplicates)
        self.mic_btn = ctk.CTkButton(self, text="🎤 Voice OFF", width=110, height=32, fg_color=T["bg_hover"], command=self.app.toggle_voice)
        self.mic_btn.pack(side="right", padx=8)

        self._update_status()

    def _update_status(self):
        try:
            cpu = psutil.cpu_percent()
            gpu = 0  # placeholder - add real GPU % if you have GPUtil
            self.status_label.configure(text=f"CPU: {cpu}% | GPU: {gpu}%")
        except:
            pass
        self.after(2000, self._update_status)
