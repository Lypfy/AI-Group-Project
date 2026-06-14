import tkinter as tk
from tkinter import ttk

class LogPanel(tk.Frame):
    def __init__(self, parent, width=250, *args, **kwargs):
        super().__init__(parent, bg="#313244", width=width, *args, **kwargs)
        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        tk.Label(
            self,
            text="Nhật ký (Log)",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=10)

        self.log_text = tk.Text(
            self, bg="#181825", fg="white", font=("Consolas", 10)
        )
        self.log_scroll = ttk.Scrollbar(self, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll.set)
        
        self.log_scroll.pack(side="right", fill="y", pady=10, padx=(0, 10))
        self.log_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        
        # Cấu hình màu cho log
        self.log_text.tag_config("success", foreground="#a6e3a1")
        self.log_text.tag_config("error", foreground="#f38ba8")
        self.log_text.tag_config("info", foreground="#89b4fa")
        self.log_text.tag_config("warning", foreground="#f9e2af")

    def log(self, message, tag="info"):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

    def clear(self):
        self.log_text.delete("1.0", tk.END)
