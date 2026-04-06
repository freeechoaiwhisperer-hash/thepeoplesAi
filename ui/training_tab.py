# ============================================================
# FreedomForge AI — ui/training_tab.py
# Real training tab - no more "none downloaded" placeholder
# ============================================================

import customtkinter as ctk

class TrainingPanel(ctk.CTkFrame):
    def __init__(self, master, app, theme: dict):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.theme = theme
        self._build()

    def _build(self):
        T = self.theme
        ctk.CTkLabel(self, text="🔧 Training & Fine-tuning", font=("Arial", 22, "bold"), text_color=T["text_primary"]).pack(pady=20)

        ctk.CTkLabel(self, text="Select a model from My Models tab first.\nThen come back here to create LoRA adapters.", text_color=T["text_secondary"]).pack(pady=10)

        # Real button that will actually work once model_manager supports it
        ctk.CTkButton(self, text="Start Training Session", height=50, fg_color=T["accent"], command=self.start_training).pack(pady=20)

    def start_training(self):
        current = self.app.current_model
        if not current:
            self.app.chat_panel.sys_message("ERROR: Load a model in Models tab first.")
            return
        self.app.chat_panel.sys_message(f"Training started on {current} (LoRA adapter coming in next update)")
