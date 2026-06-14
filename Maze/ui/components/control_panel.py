import tkinter as tk
from tkinter import ttk

class ControlPanel(tk.Frame):
    def __init__(self, parent, callbacks, levels, algorithms, width=265, *args, **kwargs):
        super().__init__(parent, bg="#313244", width=width, *args, **kwargs)
        self.pack_propagate(False)
        self.callbacks = callbacks  # Dữ liệu dạng dict chứa các hàm callback như on_reset, on_run, on_pause, on_algo_change
        self.levels = levels
        self.algorithms = algorithms
        
        # Biến trạng thái
        self.selected_level = tk.StringVar(value=list(self.levels.keys())[0])
        self.selected_algo = tk.StringVar(value="Breadth-First Search (BFS)")
        
        # Tham số SA
        self.sa_T0    = tk.DoubleVar(value=100.0)
        self.sa_Tmin  = tk.DoubleVar(value=0.1)
        self.sa_alpha = tk.DoubleVar(value=0.99)
        
        # Tốc độ animation
        self.speed_var = tk.IntVar(value=150)
        
        self.setup_ui()

    def setup_ui(self):
        # CANVAS SCOLL CHO PANEL TRÁI
        self.canvas = tk.Canvas(self, bg="#313244", highlightthickness=0)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="#313244")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        tk.Label(
            self.inner_frame,
            text="Bảng điều khiển",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=15)

        # 1. CHỌN MÀN CHƠI
        tk.Label(
            self.inner_frame, text="1. Chọn màn chơi:", bg="#313244", fg="#a6e3a1", font=("Segoe UI", 11, "bold"),
        ).pack(pady=(5, 0), anchor="w", padx=15)
        self.level_combo = ttk.Combobox(
            self.inner_frame, textvariable=self.selected_level, values=list(self.levels.keys()), state="readonly", width=22,
        )
        self.level_combo.pack(pady=5, padx=15, fill="x")
        self.level_combo.bind("<<ComboboxSelected>>", lambda e: self.callbacks.get("on_reset", lambda: None)())

        # 2. CHỌN THUẬT TOÁN
        tk.Label(
            self.inner_frame, text="2. Chọn thuật toán:", bg="#313244", fg="#89b4fa", font=("Segoe UI", 11, "bold"),
        ).pack(pady=(15, 0), anchor="w", padx=15)
        self.algo_combo = ttk.Combobox(
            self.inner_frame, textvariable=self.selected_algo, values=list(self.algorithms.keys()), state="readonly", width=22,
        )
        self.algo_combo.pack(pady=5, padx=15, fill="x")
        self.algo_combo.bind("<<ComboboxSelected>>", lambda e: self._on_algo_change())

        # 3. GỢI Ý CHIẾN THUẬT
        tk.Label(
            self.inner_frame, text="3. Gợi ý chiến thuật:", bg="#313244", fg="#f9e2af", font=("Segoe UI", 11, "bold"),
        ).pack(pady=(15, 0), anchor="w", padx=15)
        self.hint_label = tk.Label(
            self.inner_frame, text="", bg="#181825", fg="#cdd6f4", font=("Segoe UI", 10, "italic"),
            wraplength=220, justify="left", padx=10, pady=10,
        )
        self.hint_label.pack(pady=5, padx=15, fill="x")

        # CÁC NÚT BẤM
        self.run_btn = ttk.Button(self.inner_frame, text="▶ BẮT ĐẦU", command=self.callbacks.get("on_run"))
        self.run_btn.pack(pady=(20, 10), padx=15, fill="x")
        
        self.reset_btn = ttk.Button(self.inner_frame, text="⟳ TẢI LẠI", command=self.callbacks.get("on_reset"))
        self.reset_btn.pack(pady=5, padx=15, fill="x")
        
        self.pause_btn = ttk.Button(self.inner_frame, text="⏸ DỪNG", command=self.callbacks.get("on_pause"))
        self.pause_btn.pack(pady=5, padx=15, fill="x")

        # THAM SỐ SA
        self.sa_frame = tk.Frame(self.inner_frame, bg="#313244")
        self.sa_frame.pack(fill="x", padx=15, pady=(10, 0))

        tk.Label(
            self.sa_frame, text="⚙ Tham số Simulated Annealing", bg="#313244", fg="#fab387", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self._create_sa_param_row("T₀  (nhiệt ban đầu)", self.sa_T0, 10, 500, 10, "#fab387")
        self._create_sa_param_row("T_min (nhiệt tối thiểu)", self.sa_Tmin, 0.01, 5, 0.01, "#f38ba8")
        self._create_sa_param_row("α  (hệ số làm lạnh)", self.sa_alpha, 0.80, 0.999, 0.001, "#94e2d5")

        self.sa_frame.pack_forget() # Ẩn mặc định

        # 4. TỐC ĐỘ ANIMATION
        tk.Label(
            self.inner_frame, text="4. Tốc độ Animation", bg="#313244", fg="#fab387", font=("Segoe UI", 11, "bold"),
        ).pack(pady=(20, 0), anchor="w", padx=15)
        speed_frame = tk.Frame(self.inner_frame, bg="#313244")
        speed_frame.pack(fill="x", padx=15)
        self.speed_slider = tk.Scale(
            speed_frame, from_=20, to=500, orient="horizontal", variable=self.speed_var,
            bg="#313244", fg="white", troughcolor="#181825", highlightthickness=0,
        )
        self.speed_slider.pack(fill="x")

    def _create_sa_param_row(self, label, var, from_, to, resolution, color):
        row = tk.Frame(self.sa_frame, bg="#313244")
        row.pack(fill="x", pady=1)
        tk.Label(row, text=label, bg="#313244", fg=color, font=("Segoe UI", 9), width=18, anchor="w").pack(side="left")
        tk.Label(row, textvariable=var, bg="#313244", fg="#f9e2af", font=("Consolas", 9, "bold"), width=6).pack(side="right")
        tk.Scale(self.sa_frame, variable=var, from_=from_, to=to, resolution=resolution, orient="horizontal",
                 bg="#313244", fg="white", troughcolor="#181825", highlightthickness=0, showvalue=False).pack(fill="x")

    def _on_algo_change(self):
        if self.selected_algo.get() == "Simulated Annealing (SA)":
            self.sa_frame.pack(fill="x", padx=15, pady=(10, 0), before=self.speed_slider.master)
        else:
            self.sa_frame.pack_forget()
        self.callbacks.get("on_reset", lambda: None)()
