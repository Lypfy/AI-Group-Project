"""
sa_app.py — Giao diện Tkinter cho thuật toán Simulated Annealing
Mê cung 20x20 · Hiển thị nhiệt độ, ΔE, xác suất chấp nhận theo thời gian thực
"""

import tkinter as tk
from tkinter import ttk
import copy
import time
import math

from map import MAPS
from simulated_annealing import SimulatedAnnealing

# ─────────────────────────────────────────────
# COLOUR PALETTE (Catppuccin Mocha)
# ─────────────────────────────────────────────
BG_BASE    = "#1e1e2e"
BG_SURFACE = "#313244"
BG_DARK    = "#181825"
BG_CRUST   = "#11111b"

COL_TEXT   = "#cdd6f4"
COL_SUB    = "#6c7086"
COL_GREEN  = "#a6e3a1"
COL_BLUE   = "#89b4fa"
COL_YELLOW = "#f9e2af"
COL_ORANGE = "#fab387"
COL_RED    = "#f38ba8"
COL_MAUVE  = "#cba6f7"
COL_TEAL   = "#94e2d5"
COL_PINK   = "#f5c2e7"

# ─────────────────────────────────────────────
# MAP CELL COLOURS
# ─────────────────────────────────────────────
CELL_WALL     = "#313244"
CELL_EMPTY    = "#45475a"
CELL_ROBOT    = "#89b4fa"
CELL_TRAIL    = "#f9e2af"
CELL_GOAL     = "#a6e3a1"

FONT_UI   = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_BIG  = ("Segoe UI", 20, "bold")
FONT_MONO = ("Consolas", 10)
FONT_MONO_BIG = ("Consolas", 13, "bold")


class SAApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌡 Simulated Annealing — Maze Solver")
        self.root.geometry("1280x820")
        self.root.configure(bg=BG_BASE)
        self.root.resizable(False, False)

        # ── state ──
        self.is_running   = False
        self.is_paused    = False
        self.step_idx     = 0
        self.search_history: list[dict] = []
        self.path: list   = []
        self.goal_pos     = (19, 19)
        self.maze_logic   = None

        # ── SA params ──
        self.var_T0    = tk.DoubleVar(value=100.0)
        self.var_Tmin  = tk.DoubleVar(value=0.1)
        self.var_alpha = tk.DoubleVar(value=0.99)
        self.speed_var = tk.IntVar(value=30)

        # ── level select ──
        self.levels = MAPS
        self.selected_level = tk.StringVar(value=list(MAPS.keys())[0])

        # ── build UI ──
        self._setup_style()
        self._build_ui()
        self._reset()

    # ═══════════════════════════════════════════════════
    # STYLE
    # ═══════════════════════════════════════════════════

    def _setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TButton",
                    font=("Segoe UI", 11, "bold"),
                    padding=8,
                    background=BG_SURFACE,
                    foreground=COL_TEXT,
                    relief="flat")
        s.map("TButton",
              background=[("active", COL_BLUE)],
              foreground=[("active", BG_DARK)])
        s.configure("TCombobox",
                    font=("Segoe UI", 10),
                    padding=4,
                    fieldbackground=BG_DARK,
                    foreground=COL_TEXT,
                    selectbackground=BG_SURFACE)
        s.configure("Horizontal.TScale",
                    background=BG_SURFACE,
                    troughcolor=BG_DARK)
        s.configure("TProgressbar",
                    troughcolor=BG_DARK,
                    background=COL_BLUE,
                    thickness=10)

    # ═══════════════════════════════════════════════════
    # BUILD UI
    # ═══════════════════════════════════════════════════

    def _build_ui(self):
        # ── Title bar ──
        title_bar = tk.Frame(self.root, bg=BG_CRUST, height=52)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(title_bar,
                 text="🌡  Simulated Annealing  —  Maze Solver",
                 bg=BG_CRUST, fg=COL_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=10)

        tk.Label(title_bar,
                 text="Nhóm AI · HCMUTE",
                 bg=BG_CRUST, fg=COL_SUB,
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

        # ── Main layout ──
        main = tk.Frame(self.root, bg=BG_BASE)
        main.pack(fill="both", expand=True, padx=10, pady=8)

        # Left panel
        self._build_left(main)
        # Center (canvas + stats)
        self._build_center(main)
        # Right panel (live metrics + log)
        self._build_right(main)

    # ───────────────────────────────────────────────────
    # LEFT PANEL
    # ───────────────────────────────────────────────────

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG_SURFACE, width=230)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        def section_label(text, color=COL_BLUE):
            tk.Label(left, text=text, bg=BG_SURFACE, fg=color,
                     font=("Segoe UI", 10, "bold")).pack(
                anchor="w", padx=14, pady=(14, 2))

        # ── Level select ──
        section_label("📍 Chọn màn chơi:", COL_GREEN)
        self.level_combo = ttk.Combobox(
            left,
            textvariable=self.selected_level,
            values=list(self.levels.keys()),
            state="readonly", width=24)
        self.level_combo.pack(padx=14, fill="x")
        self.level_combo.bind("<<ComboboxSelected>>", lambda _: self._reset())

        # ── SA parameters ──
        section_label("⚙ Tham số SA:", COL_ORANGE)

        def param_row(label, var, from_, to, resolution, color=COL_TEXT):
            row = tk.Frame(left, bg=BG_SURFACE)
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=label, bg=BG_SURFACE, fg=color,
                     font=("Segoe UI", 9), width=14, anchor="w").pack(side="left")
            val_lbl = tk.Label(row, textvariable=var, bg=BG_SURFACE, fg=COL_YELLOW,
                               font=("Consolas", 9, "bold"), width=6)
            val_lbl.pack(side="right")
            sl = tk.Scale(left, variable=var, from_=from_, to=to,
                          resolution=resolution, orient="horizontal",
                          bg=BG_SURFACE, fg=COL_TEXT, troughcolor=BG_DARK,
                          highlightthickness=0, showvalue=False, length=200)
            sl.pack(padx=14, fill="x")
            return sl

        param_row("T₀  (nhiệt ban đầu)",  self.var_T0,    10,   500, 10,   COL_ORANGE)
        param_row("T_min (nhiệt tối thiểu)", self.var_Tmin, 0.01, 5,   0.01, COL_RED)
        param_row("α  (hệ số làm lạnh)",   self.var_alpha, 0.80, 0.999, 0.001, COL_TEAL)

        # ── Speed ──
        section_label("⚡ Tốc độ hiển thị:", COL_MAUVE)
        speed_row = tk.Frame(left, bg=BG_SURFACE)
        speed_row.pack(fill="x", padx=14, pady=2)
        tk.Label(speed_row, text="Nhanh", bg=BG_SURFACE, fg=COL_SUB,
                 font=("Segoe UI", 8)).pack(side="left")
        tk.Label(speed_row, text="Chậm", bg=BG_SURFACE, fg=COL_SUB,
                 font=("Segoe UI", 8)).pack(side="right")
        tk.Scale(left, variable=self.speed_var, from_=5, to=400,
                 orient="horizontal", bg=BG_SURFACE, fg=COL_TEXT,
                 troughcolor=BG_DARK, highlightthickness=0, showvalue=False,
                 length=200).pack(padx=14, fill="x")

        # ── Buttons ──
        tk.Frame(left, bg=COL_SUB, height=1).pack(fill="x", padx=14, pady=14)

        self.run_btn = ttk.Button(left, text="▶  BẮT ĐẦU GIẢI",
                                  command=self._run)
        self.run_btn.pack(padx=14, pady=4, fill="x")

        self.pause_btn = ttk.Button(left, text="⏸  PAUSE",
                                    command=self._toggle_pause)
        self.pause_btn.pack(padx=14, pady=4, fill="x")

        self.reset_btn = ttk.Button(left, text="⟳  ĐẶT LẠI",
                                    command=self._reset)
        self.reset_btn.pack(padx=14, pady=4, fill="x")

        # ── Hint ──
        section_label("💡 Gợi ý:", COL_YELLOW)
        self.hint_lbl = tk.Label(left, text="",
                                  bg=BG_DARK, fg=COL_TEXT,
                                  font=("Segoe UI", 9, "italic"),
                                  wraplength=200, justify="left",
                                  padx=8, pady=8)
        self.hint_lbl.pack(padx=14, pady=4, fill="x")

    # ───────────────────────────────────────────────────
    # CENTER PANEL
    # ───────────────────────────────────────────────────

    def _build_center(self, parent):
        center = tk.Frame(parent, bg=BG_BASE)
        center.pack(side="left", fill="both", expand=True)

        # Canvas
        canvas_wrap = tk.Frame(center, bg=BG_DARK,
                               highlightbackground=COL_SUB,
                               highlightthickness=1)
        canvas_wrap.pack()

        self.canvas = tk.Canvas(canvas_wrap, width=500, height=500,
                                bg=BG_DARK, highlightthickness=0)
        self.canvas.pack()

        # Status label
        self.status_lbl = tk.Label(center, text="Trạng thái: Sẵn sàng",
                                   bg=BG_BASE, fg=COL_GREEN,
                                   font=("Segoe UI", 12, "bold"))
        self.status_lbl.pack(pady=(8, 2))

        # Progress bar
        self.progress = ttk.Progressbar(center, length=500, mode="determinate",
                                        style="TProgressbar")
        self.progress.pack(pady=4)

        # Stats bar
        stats = tk.Frame(center, bg=BG_SURFACE)
        stats.pack(fill="x", padx=0, pady=4)

        def stat_cell(parent, label, init, color, var_name):
            f = tk.Frame(parent, bg=BG_SURFACE)
            f.pack(side="left", expand=True)
            tk.Label(f, text=label, bg=BG_SURFACE, fg=COL_SUB,
                     font=("Segoe UI", 8)).pack()
            lbl = tk.Label(f, text=init, bg=BG_SURFACE, fg=color,
                           font=("Consolas", 12, "bold"))
            lbl.pack()
            setattr(self, var_name, lbl)

        stat_cell(stats, "BƯỚC", "0",    COL_BLUE,   "stat_step")
        stat_cell(stats, "ΔE",   "—",    COL_ORANGE, "stat_de")
        stat_cell(stats, "P(accept)", "—", COL_MAUVE, "stat_prob")
        stat_cell(stats, "HEURISTIC", "—", COL_TEAL,  "stat_h")

        # Solution path strip
        sol_hdr = tk.Frame(center, bg=BG_BASE)
        sol_hdr.pack(fill="x", pady=(6, 0))
        tk.Label(sol_hdr, text="🧭 Đường đi giải pháp",
                 bg=BG_BASE, fg=COL_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.path_count_lbl = tk.Label(sol_hdr, text="—",
                                        bg=BG_BASE, fg=COL_BLUE,
                                        font=("Segoe UI", 10, "bold"))
        self.path_count_lbl.pack(side="right")

        sol_card = tk.Frame(center, bg=BG_SURFACE,
                            highlightbackground=COL_SUB, highlightthickness=1)
        sol_card.pack(fill="x", pady=2)

        self.sol_scroll = tk.Scrollbar(sol_card, orient="horizontal", bg=BG_DARK)
        self.sol_scroll.pack(side="bottom", fill="x")

        self.sol_canvas = tk.Canvas(sol_card, bg=BG_DARK, height=50,
                                    highlightthickness=0,
                                    xscrollcommand=self.sol_scroll.set)
        self.sol_canvas.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.sol_scroll.config(command=self.sol_canvas.xview)

        self.sol_text_id = self.sol_canvas.create_text(
            10, 25, anchor="w", text="Chưa chạy…",
            fill=COL_BLUE, font=("Segoe UI Emoji", 11, "bold"))

    # ───────────────────────────────────────────────────
    # RIGHT PANEL
    # ───────────────────────────────────────────────────

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG_SURFACE, width=260)
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)

        # ── Temperature gauge ──
        tk.Label(right, text="🌡 Nhiệt độ (T)",
                 bg=BG_SURFACE, fg=COL_ORANGE,
                 font=("Segoe UI", 11, "bold")).pack(pady=(14, 2))

        self.temp_canvas = tk.Canvas(right, width=220, height=22,
                                     bg=BG_DARK, highlightthickness=0)
        self.temp_canvas.pack(padx=14, pady=2)

        self.temp_lbl = tk.Label(right, text="T = —",
                                  bg=BG_SURFACE, fg=COL_ORANGE,
                                  font=("Consolas", 14, "bold"))
        self.temp_lbl.pack()

        # ── Accept rate chart (mini bar) ──
        tk.Label(right, text="✅ Chấp nhận / ❌ Từ chối",
                 bg=BG_SURFACE, fg=COL_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(pady=(14, 2))

        self.accept_canvas = tk.Canvas(right, width=220, height=60,
                                        bg=BG_DARK, highlightthickness=0)
        self.accept_canvas.pack(padx=14, pady=2)

        self._accepted_count = 0
        self._rejected_count = 0

        # ── Legend ──
        legend = tk.Frame(right, bg=BG_SURFACE)
        legend.pack(padx=14, fill="x", pady=4)

        def legend_item(parent, color, text):
            f = tk.Frame(parent, bg=BG_SURFACE)
            f.pack(side="left", padx=4)
            tk.Frame(f, bg=color, width=12, height=12).pack(side="left")
            tk.Label(f, text=" " + text, bg=BG_SURFACE, fg=COL_TEXT,
                     font=("Segoe UI", 8)).pack(side="left")

        legend_item(legend, COL_ROBOT if False else CELL_ROBOT, "Robot (🤖)")
        legend_item(legend, CELL_TRAIL, "Đã qua (🐾)")
        legend_item(legend, CELL_GOAL, "Đích (🏁)")

        # ── Log ──
        tk.Frame(right, bg=COL_SUB, height=1).pack(fill="x", padx=14, pady=10)
        tk.Label(right, text="📋 Nhật ký",
                 bg=BG_SURFACE, fg=COL_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14)

        log_frame = tk.Frame(right, bg=BG_SURFACE)
        log_frame.pack(fill="both", expand=True, padx=14, pady=6)

        log_scroll = tk.Scrollbar(log_frame, bg=BG_DARK)
        log_scroll.pack(side="right", fill="y")

        self.log_text = tk.Text(log_frame, bg=BG_DARK, fg=COL_TEXT,
                                font=FONT_MONO, wrap="none",
                                yscrollcommand=log_scroll.set,
                                state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.config(command=self.log_text.yview)

        self.log_text.tag_config("success",  foreground=COL_GREEN)
        self.log_text.tag_config("error",    foreground=COL_RED)
        self.log_text.tag_config("info",     foreground=COL_BLUE)
        self.log_text.tag_config("warning",  foreground=COL_YELLOW)
        self.log_text.tag_config("accepted", foreground=COL_TEAL)
        self.log_text.tag_config("rejected", foreground=COL_ORANGE)

    # ═══════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════

    def _log(self, msg: str, tag="info"):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def _update_temp_bar(self, T: float):
        """Draw a gradient temperature bar."""
        self.temp_canvas.delete("all")
        w, h = 220, 22
        ratio = min(max(T / self.var_T0.get(), 0.0), 1.0)
        fill_w = int(w * ratio)

        # Background
        self.temp_canvas.create_rectangle(0, 0, w, h, fill=BG_CRUST, outline="")

        # Gradient: cold (teal) → hot (red/orange)
        if fill_w > 0:
            # Simplified: just use a colour based on ratio
            r = int(0xf3 * ratio + 0x94 * (1 - ratio))
            g = int(0x8b * ratio + 0xe2 * (1 - ratio))
            b = int(0xa8 * ratio + 0xd5 * (1 - ratio))
            colour = f"#{r:02x}{g:02x}{b:02x}"
            self.temp_canvas.create_rectangle(0, 0, fill_w, h,
                                               fill=colour, outline="")

        # Text overlay
        self.temp_canvas.create_text(w // 2, h // 2,
                                      text=f"{ratio*100:.1f}%",
                                      fill="white",
                                      font=("Consolas", 9, "bold"))

    def _update_accept_chart(self):
        self.accept_canvas.delete("all")
        w, h = 220, 60
        total = self._accepted_count + self._rejected_count
        if total == 0:
            return
        acc_ratio = self._accepted_count / total
        rej_ratio = self._rejected_count / total

        bar_h = 22
        acc_w = int(w * acc_ratio)
        rej_w = int(w * rej_ratio)

        # Accepted bar
        self.accept_canvas.create_rectangle(0, 4, acc_w, 4 + bar_h,
                                             fill=COL_TEAL, outline="")
        self.accept_canvas.create_text(4, 4 + bar_h // 2,
                                        anchor="w",
                                        text=f"✅ {self._accepted_count} ({acc_ratio*100:.1f}%)",
                                        fill=BG_DARK, font=("Consolas", 8, "bold"))

        # Rejected bar
        self.accept_canvas.create_rectangle(0, 34, rej_w, 34 + bar_h,
                                             fill=COL_ORANGE, outline="")
        self.accept_canvas.create_text(4, 34 + bar_h // 2,
                                        anchor="w",
                                        text=f"❌ {self._rejected_count} ({rej_ratio*100:.1f}%)",
                                        fill=BG_DARK, font=("Consolas", 8, "bold"))

    # ═══════════════════════════════════════════════════
    # DRAW GRID
    # ═══════════════════════════════════════════════════

    def _draw_grid(self, matrix):
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell = 500 // cols

        for i in range(rows):
            for j in range(cols):
                x1, y1 = j * cell, i * cell
                x2, y2 = x1 + cell, y1 + cell
                val = matrix[i][j]

                if val == 1:  # Wall
                    self.canvas.create_rectangle(
                        x1+1, y1+1, x2-1, y2-1,
                        fill=CELL_WALL, outline=BG_CRUST, width=1)
                    # 3D bevel
                    self.canvas.create_line(x1+1, y1+1, x2-1, y1+1, fill="#585b70", width=2)
                    self.canvas.create_line(x1+1, y1+1, x1+1, y2-1, fill="#585b70", width=2)
                    self.canvas.create_line(x2-1, y2-1, x2-1, y1+1, fill=BG_CRUST, width=2)
                    self.canvas.create_line(x2-1, y2-1, x1+1, y2-1, fill=BG_CRUST, width=2)

                else:
                    color = CELL_EMPTY
                    emoji = ""

                    if val == 3:
                        color = CELL_ROBOT
                        emoji = "🤖"
                    elif val == 7:
                        color = CELL_TRAIL
                        emoji = "🐾"

                    # Goal cell override
                    if (i, j) == self.goal_pos and val != 3:
                        color = CELL_GOAL
                        emoji = "🏁"

                    self.canvas.create_rectangle(
                        x1+1, y1+1, x2-1, y2-1,
                        fill=color, outline=BG_CRUST, width=1)

                    if emoji:
                        self.canvas.create_text(
                            x1 + cell // 2, y1 + cell // 2,
                            text=emoji,
                            font=("Arial", int(cell * 0.52)))

    # ═══════════════════════════════════════════════════
    # RESET
    # ═══════════════════════════════════════════════════

    def _reset(self):
        self.is_running = False
        self.is_paused = False
        self.step_idx = 0
        self.search_history = []
        self.path = []
        self._accepted_count = 0
        self._rejected_count = 0

        self.pause_btn.config(text="⏸  PAUSE")
        self._clear_log()

        self.sol_canvas.itemconfig(self.sol_text_id, text="Chưa chạy…")
        self.sol_canvas.config(scrollregion=(0, 0, 0, 0))
        self.path_count_lbl.config(text="—")

        self.progress["value"] = 0
        self.stat_step.config(text="0")
        self.stat_de.config(text="—")
        self.stat_prob.config(text="—")
        self.stat_h.config(text="—")
        self.temp_lbl.config(text="T = —")
        self.status_lbl.config(text="Trạng thái: Sẵn sàng", fg=COL_GREEN)

        self._update_temp_bar(0)
        self._update_accept_chart()

        # Load map
        level_name = self.selected_level.get()
        level_data = self.levels[level_name]
        current_map = copy.deepcopy(level_data["matrix"])
        self.hint_lbl.config(text=level_data.get("hint", ""))

        # Find goal
        self.goal_pos = (19, 19)
        for i in range(len(current_map)):
            for j in range(len(current_map[0])):
                if current_map[i][j] == 9:
                    self.goal_pos = (i, j)
                    current_map[i][j] = 0
                    break

        self.maze_logic = SimulatedAnnealing(
            initial_maze=current_map,
            goal=self.goal_pos,
            T0=self.var_T0.get(),
            Tmin=self.var_Tmin.get(),
            alpha=self.var_alpha.get()
        )

        self._draw_grid(current_map)
        self._log(f"✔ Đã tải: {level_name}", "success")
        self._log(f"  Đích: {self.goal_pos}", "info")
        self._log(f"  T₀={self.var_T0.get()}, α={self.var_alpha.get()}, T_min={self.var_Tmin.get()}", "info")

    # ═══════════════════════════════════════════════════
    # RUN
    # ═══════════════════════════════════════════════════

    def _run(self):
        if self.is_running:
            return

        self.is_running = True
        self.status_lbl.config(text="⚙ Đang tính toán…", fg=COL_YELLOW)
        self.root.update_idletasks()

        t0 = time.perf_counter()
        result_node = self.maze_logic.solve()
        elapsed = (time.perf_counter() - t0) * 1000

        self.search_history = self.maze_logic.search_history
        total_steps = len(self.search_history)

        self._log(f"Thời gian tính toán: {elapsed:.2f} ms", "success")
        self._log(f"Tổng số bước SA: {total_steps}", "info")

        if result_node is None:
            self._log("Không tìm thấy đường đi!", "error")
            self.status_lbl.config(text="❌ Không có đường đi", fg=COL_RED)
            self.is_running = False
            return

        # Build solution path
        self.path = self.maze_logic.get_path(result_node)
        actions = [s[1] for s in self.path if s[1] != "START"]

        ARROWS = {"up": "⬆", "down": "⬇", "left": "⬅", "right": "➡"}
        pretty = "   ".join(f"{ARROWS.get(a, a)} {a.upper()}" for a in actions)
        self.sol_canvas.itemconfig(self.sol_text_id, text=pretty)
        self.sol_canvas.update_idletasks()
        bbox = self.sol_canvas.bbox(self.sol_text_id)
        if bbox:
            self.sol_canvas.config(scrollregion=bbox)

        self.path_count_lbl.config(text=f"{len(actions)} bước")
        self.progress["maximum"] = total_steps
        self.progress["value"] = 0
        self.step_idx = 0

        self._log(f"Đường đi: {len(actions)} bước", "success")
        self.status_lbl.config(text="▶ Đang phát lại…", fg=COL_BLUE)

        self._animate_sa()

    # ═══════════════════════════════════════════════════
    # ANIMATE — SA history playback
    # ═══════════════════════════════════════════════════

    def _animate_sa(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, self._animate_sa)
            return

        if self.step_idx < len(self.search_history):
            frame = self.search_history[self.step_idx]
            matrix  = frame["matrix"]
            T       = frame["T"]
            deltaE  = frame["deltaE"]
            prob    = frame["prob"]
            h       = frame["heuristic"]
            accepted = frame["accepted"]

            # Draw
            self._draw_grid(matrix)

            # Live metrics
            self.stat_step.config(text=str(self.step_idx + 1))
            self.stat_de.config(
                text=f"{deltaE:+.2f}",
                fg=COL_GREEN if deltaE < 0 else COL_RED)
            self.stat_prob.config(
                text=f"{prob:.3f}",
                fg=COL_MAUVE)
            self.stat_h.config(text=str(h), fg=COL_TEAL)
            self.temp_lbl.config(text=f"T = {T:.4f}")
            self._update_temp_bar(T)

            if accepted:
                self._accepted_count += 1
            else:
                self._rejected_count += 1
            self._update_accept_chart()

            self.progress["value"] = self.step_idx + 1
            self.step_idx += 1

            # Log every 50 steps to avoid flooding
            if self.step_idx % 50 == 1:
                tag = "accepted" if accepted else "rejected"
                sign = "✅" if accepted else "❌"
                self._log(
                    f"Bước {self.step_idx:5d} | T={T:.3f} | ΔE={deltaE:+.2f} | "
                    f"P={prob:.3f} | {sign}",
                    tag)

            self.root.after(self.speed_var.get(), self._animate_sa)

        else:
            # SA playback done — now show final path
            self._animate_path(0)

    # ═══════════════════════════════════════════════════
    # ANIMATE — Final solution path
    # ═══════════════════════════════════════════════════

    def _animate_path(self, idx: int):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, lambda: self._animate_path(idx))
            return

        if idx < len(self.path):
            matrix, action = self.path[idx]
            self._draw_grid(matrix)
            self.progress["maximum"] = len(self.path)
            self.progress["value"] = idx + 1
            if action != "START":
                self._log(f"  → {action.upper()}", "info")
            self.root.after(self.speed_var.get() * 2,
                            lambda: self._animate_path(idx + 1))
        else:
            self.status_lbl.config(text="✔ Hoàn thành!", fg=COL_GREEN)
            self._log("🏁 DONE! Robot đã đến đích.", "success")
            self._log(f"  ✅ Chấp nhận: {self._accepted_count}  ❌ Từ chối: {self._rejected_count}", "info")
            self.is_running = False

    # ═══════════════════════════════════════════════════
    # PAUSE
    # ═══════════════════════════════════════════════════

    def _toggle_pause(self):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶  TIẾP TỤC")
            self.status_lbl.config(text="⏸ Đã tạm dừng", fg=COL_YELLOW)
        else:
            self.pause_btn.config(text="⏸  PAUSE")
            self.status_lbl.config(text="▶ Tiếp tục…", fg=COL_BLUE)


# ═══════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = SAApp(root)
    root.mainloop()
