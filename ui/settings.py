# ============================================================
# FreedomForge AI — ui/settings.py
# Cleaned duplicate voice toggles + 18+ password = adultonly420
# ============================================================

import os
import threading
import customtkinter as ctk
from core import config
from assets.i18n import t, language_options, display_name_to_code, get_language
from assets.themes import get as get_theme, display_names, name_from_display


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, master, app, theme: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.theme = theme
        self._build()

    def apply_theme(self, theme: dict):
        self.theme = theme
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        T = self.theme

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text=f"⚙️  {t('settings_title')}", font=("Arial", 22, "bold"), text_color=T["text_primary"]).pack(pady=(24, 2), padx=24, anchor="w")
        ctk.CTkLabel(scroll, text=t("settings_subtitle"), font=("Arial", 12), text_color=T["text_secondary"]).pack(padx=24, anchor="w", pady=(0, 14))

        # Appearance
        self._section(scroll, t("settings_appearance"))
        card = self._card(scroll)

        r1 = self._row(card, t("settings_dark_mode"), t("settings_dark_desc"))
        self.dark_var = ctk.BooleanVar(value=config.get("dark_mode", True))
        ctk.CTkSwitch(r1, text="", variable=self.dark_var, command=self._toggle_dark).pack(side="right")

        r2 = self._row(card, t("settings_theme"), t("settings_theme_desc"))
        current = get_theme(config.get("theme", "Midnight"))["display"]
        self.theme_var = ctk.StringVar(value=current)
        ctk.CTkOptionMenu(r2, variable=self.theme_var, values=display_names(), command=self._change_theme, width=180, fg_color=T["bg_hover"]).pack(side="right")

        # Language
        self._section(scroll, t("settings_language"))
        card2 = self._card(scroll)
        r4 = self._row(card2, t("settings_language"), t("settings_lang_desc"))
        lang_opts = language_options()
        current_disp = next((d for c, d in lang_opts if c == get_language()), lang_opts[0][1])
        self.lang_var = ctk.StringVar(value=current_disp)
        ctk.CTkOptionMenu(r4, variable=self.lang_var, values=[d for _, d in lang_opts], command=self._change_language, width=220, fg_color=T["bg_hover"]).pack(side="right")

        # Voice (only ONE toggle now)
        self._section(scroll, t("settings_voice"))
        card3 = self._card(scroll)
        r5 = self._row(card3, "Voice Input", t("settings_voice_in_desc"))
        self.voice_in_var = ctk.BooleanVar(value=config.get("voice_in", False))
        ctk.CTkSwitch(r5, text="", variable=self.voice_in_var, command=lambda: config.set("voice_in", self.voice_in_var.get())).pack(side="right")

        r6 = self._row(card3, "Voice Output", t("settings_voice_out_desc"))
        self.voice_out_var = ctk.BooleanVar(value=config.get("voice_out", False))
        ctk.CTkSwitch(r6, text="", variable=self.voice_out_var, command=lambda: config.set("voice_out", self.voice_out_var.get())).pack(side="right")

        # AI Settings + 18+ unlock
        self._section(scroll, t("settings_special"))
        card5 = self._card(scroll)
        self._build_unlock_section(card5)

        # Reset
        self._section(scroll, t("settings_reset_section"))
        card6 = self._card(scroll)
        r_last = self._row(card6, t("settings_reset"), t("settings_reset_desc"))
        ctk.CTkButton(r_last, text=t("settings_reset"), width=96, height=32, fg_color="#3a1212", command=self._reset).pack(side="right")

    def _build_unlock_section(self, parent):
        T = self.theme
        unlocked = config.get("unlocked", False)

        r = self._row(parent, t("settings_unlock"), t("settings_unlock_desc"))
        self._unlock_lbl = ctk.CTkLabel(r, text=t("settings_unlocked") if unlocked else t("settings_locked"), text_color=T["green"] if unlocked else T["text_secondary"])
        self._unlock_lbl.pack(side="right", padx=8)

        if not unlocked:
            ctk.CTkButton(r, text="Enter Code", width=116, height=30, fg_color=T["bg_hover"], command=self._show_unlock).pack(side="right")

        if unlocked:
            self._build_personality(parent)

    def _show_unlock(self):
        T = self.theme
        dialog = ctk.CTkInputDialog(text="Enter code to unlock 18+ mode:", title="18+ Mode")
        code = dialog.get_input()
        if code and code.strip() == "adultonly420":
            config.set("unlocked", True)
            self._unlock_lbl.configure(text=t("settings_unlocked"), text_color=T["green"])
            self.app.chat_panel.sys_message("18+ unrestricted mode unlocked.")
            self._rebuild()
        elif code:
            self._unlock_lbl.configure(text="❌ Wrong code", text_color=T["red"])
            self.after(2000, lambda: self._unlock_lbl.configure(text=t("settings_locked"), text_color=T["text_secondary"]))

    # ... rest of personality, adapter, reset methods remain the same as your current file ...
    # (keep your existing _build_personality, _reset, etc. — only the unlock part was changed)

    def _toggle_dark(self):
        val = self.dark_var.get()
        config.set("dark_mode", val)
        ctk.set_appearance_mode("dark" if val else "light")

    def _change_theme(self, display: str):
        name = name_from_display(display)
        config.set("theme", name)
        self.app.apply_theme(name)

    def _change_language(self, display: str):
        code = display_name_to_code(display)
        config.set("language", code)
        set_language(code)

    def _change_personality(self, value: str, keys: list, vals: list):
        idx = vals.index(value)
        key = keys[idx]
        config.set("personality", key)
        self.app.update_mode_badge()

    def _reset(self):
        # your existing reset code
        pass

    def _section(self, parent, title):
        T = self.theme
        ctk.CTkLabel(parent, text=title, font=("Arial", 13, "bold"), text_color=T["text_secondary"]).pack(anchor="w", padx=24, pady=(16,4))

    def _card(self, parent):
        T = self.theme
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=T["bg_card"])
        card.pack(fill="x", padx=20, pady=(0,4))
        return card

    def _row(self, parent, label, desc=""):
        T = self.theme
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=10)
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left, text=label, font=("Arial", 14), text_color=T["text_primary"], anchor="w").pack(anchor="w")
        if desc:
            ctk.CTkLabel(left, text=desc, font=("Arial", 11), text_color=T["text_secondary"], anchor="w").pack(anchor="w")
        return row
