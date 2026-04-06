# ============================================================
# FreedomForge AI — ui/models_tab.py
# PROFESSIONAL-GRADE Model Library — fixed My Models + dropdown
# ============================================================

import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from core import model_manager
from assets.i18n import t

from utils.paths import MODELS_DIR as _MODELS_DIR_PATH
MODELS_DIR = str(_MODELS_DIR_PATH)

class ModelsPanel(ctk.CTkFrame):
    def __init__(self, master, app, theme: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.theme = theme
        self._build()

    def apply_theme(self, theme: dict):
        self.theme = theme
        self._rebuild()

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        T = self.theme

        hdr = ctk.CTkFrame(self, fg_color="transparent", height=56)
        hdr.pack(fill="x", padx=22, pady=(20,0))
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="📦 Model Library", font=("Arial", 22, "bold"), text_color=T["text_primary"]).pack(side="left", anchor="w")
        ctk.CTkLabel(hdr, text="Download once — runs 100% local", font=("Arial", 12), text_color=T["text_secondary"]).pack(side="left", padx=16, anchor="w")

        ctk.CTkButton(hdr, text="↻ Refresh", width=90, height=30, fg_color=T["bg_hover"], command=self.refresh).pack(side="right", padx=4)

        # My Models
        my_card = ctk.CTkFrame(self, corner_radius=10, fg_color=T["bg_card"])
        my_card.pack(fill="x", padx=12, pady=(10,0))

        my_hdr = ctk.CTkFrame(my_card, fg_color="transparent")
        my_hdr.pack(fill="x", padx=14, pady=(10,6))
        ctk.CTkLabel(my_hdr, text="📂 My Models", font=("Arial", 14, "bold"), text_color=T["text_primary"]).pack(side="left")

        ctk.CTkButton(my_hdr, text="🔍 Scan Computer", width=210, height=28, fg_color=T["bg_hover"], command=self._scan_computer).pack(side="right")

        self.my_models_frame = ctk.CTkFrame(my_card, fg_color="transparent")
        self.my_models_frame.pack(fill="x", padx=14, pady=(0,10))
        self._refresh_my_models()

        # Catalog placeholder (add your curated list here later)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=(10,0))

        ctk.CTkLabel(self.scroll, text="Curated models coming in next update", text_color=T["text_dim"]).pack(pady=40)

        threading.Thread(target=self._probe_local, daemon=True).start()

    def _refresh_my_models(self):
        T = self.theme
        for w in self.my_models_frame.winfo_children():
            w.destroy()

        models = model_manager.get_model_list()

        if not models:
            ctk.CTkLabel(self.my_models_frame, text="No models yet — download one below or scan your computer.", font=("Arial", 11), text_color=T["text_dim"]).pack(anchor="w", pady=4)
            return

        for fn in models:
            loaded = model_manager.get_current_model() == fn
            row = ctk.CTkFrame(self.my_models_frame, fg_color=T["bg_input"], corner_radius=6)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=fn, font=("Arial", 12), text_color=T["text_primary"], anchor="w").pack(side="left", padx=10, pady=6, fill="x", expand=True)

            if loaded:
                ctk.CTkLabel(row, text="▶ Active", font=("Arial", 11, "bold"), text_color=T["gold"]).pack(side="right", padx=10)
            else:
                ctk.CTkButton(row, text="▶ Load", width=80, height=26, fg_color=T["accent"], hover_color=T["accent_hover"], text_color="#ffffff", command=lambda f=fn: self._load(f)).pack(side="right", padx=(4,10), pady=4)

    def _probe_local(self):
        try:
            files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
            if files:
                self.after(0, self._refresh_my_models)
        except Exception:
            pass

    def _load(self, filename):
        self.app.load_model(filename)
        self.app.switch_panel("Chat")

    def _scan_computer(self):
        self.refresh()

    def refresh(self):
        self._refresh_my_models()
