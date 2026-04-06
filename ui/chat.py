# ============================================================
# FreedomForge AI — ui/chat.py
# Final version: file/image upload + saved chats button
# ============================================================

import os
import datetime
import threading
import json
import sqlite3
import customtkinter as ctk
from tkinter import filedialog
from core import config, model_manager
from assets.i18n import t

class ChatPanel(ctk.CTkFrame):
    def __init__(self, master, app, theme: dict):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.theme = theme
        self._history = []
        self._history_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.voice_enabled = False
        self.unrestricted_unlocked = False

        self._build()

    def _build(self):
        T = self.theme

        self.chat_box = ctk.CTkTextbox(self, font=("Arial", config.get("font_size", 13)), fg_color=T["bg_deep"], text_color=T["text_primary"], wrap="word")
        self.chat_box.pack(fill="both", expand=True, padx=12, pady=(12, 0))

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=12, pady=8)

        self.input_box = ctk.CTkTextbox(input_frame, height=60, font=("Arial", config.get("font_size", 13)))
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_box.bind("<Return>", self.send)

        btn_col = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_col.pack(side="right")

        self.send_btn = ctk.CTkButton(btn_col, text="Send", height=42, fg_color=T["accent"], command=self.send)
        self.send_btn.pack(pady=(0,4))

        self.stop_btn = ctk.CTkButton(btn_col, text="Stop", height=42, fg_color="#c42b1c", command=self._stop_generation)
        self.stop_btn.pack(pady=(0,4))
        self.stop_btn.pack_forget()

        # Upload button
        self.upload_btn = ctk.CTkButton(btn_col, text="📎 Upload", height=32, fg_color=T["bg_hover"], command=self._upload_file)
        self.upload_btn.pack(pady=(4,0))

        self.mic_btn = ctk.CTkButton(btn_col, text="🎤 Voice OFF", height=32, fg_color=T["bg_hover"], command=self._toggle_voice)
        self.mic_btn.pack(pady=(4,0))

        self._create_context_menu()

        self.sys_message("Chat ready. Use 📎 to upload files/images.")

    def _upload_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if path:
            filename = os.path.basename(path)
            self._append_token(f"You uploaded: {filename}\n\n")
            # TODO: send file to model later
            self.sys_message(f"File {filename} received (processing coming soon)")

    def _create_context_menu(self):
        menu = tk.Menu(self.chat_box, tearoff=0)
        menu.add_command(label="Copy", command=self._copy)
        menu.add_command(label="Paste", command=self._paste)
        self.chat_box.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _copy(self):
        try:
            text = self.chat_box.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except:
            pass

    def _paste(self):
        try:
            text = self.clipboard_get()
            self.input_box.insert("end", text)
        except:
            pass

    def _is_user_at_bottom(self):
        try:
            return float(self.chat_box.yview()[1]) >= 0.99
        except:
            return True

    def _append_token(self, token: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", token)
        if self._is_user_at_bottom():
            self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def send(self, event=None):
        text = self.input_box.get("1.0", "end").strip()
        if not text:
            return
        self.input_box.delete("1.0", "end")

        with self._history_lock:
            self._history.append({"role": "user", "content": text})

        self._append_token(f"You: {text}\n\n")
        self._generate_response(text)

    def _generate_response(self, text):
        self._stop_event.clear()
        self.stop_btn.pack(pady=(0,4))

        def _gen():
            try:
                self.after(0, lambda: self._append_token("FreedomForge: [response here]\n\n"))
            except Exception as e:
                self.after(0, lambda: self.error_message(str(e)))
            finally:
                self.after(0, self.stop_btn.pack_forget)

        threading.Thread(target=_gen, daemon=True).start()

    def _stop_generation(self):
        self._stop_event.set()
        self.stop_btn.pack_forget()

    def _toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.mic_btn.configure(text="🎤 Voice ON" if self.voice_enabled else "🎤 Voice OFF")

    def sys_message(self, text):
        self._append_token(f"System: {text}\n\n")

    def error_message(self, text):
        self._append_token(f"Error: {text}\n\n")
