import tkinter as tk
from tkinter import ttk
import copy
import time
from core.map import MAPS
from algorithms.uninformed.bfs import BFS
from algorithms.informed.aStar import AStar
from algorithms.uninformed.dfs import DFS
from algorithms.informed.gbfs import GBFS


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.search_idx = 0
        self.search_frames = []
        self.root.title("Maze Solver AI - Multi-Levels & Algorithms")
        self.root.geometry("1150x750")
        self.root.configure(bg="#1e1e2e")
        # =========================
        # STATE
        # =========================
        self.is_running = False
        self.is_paused = False
        self.path = []
        self.step_idx = 0
        self.goal_pos = (19, 19)
        self.maze_logic = None
        # =========================
        # LEVELS
        # =========================
        self.levels = MAPS
        first_level_name = list(self.levels.keys())[0]
        self.selected_level = tk.StringVar(value=first_level_name)
        # =========================
        # ALGORITHMS
        # =========================
        self.algorithms = {
            "Breadth-First Search (BFS)": BFS,
            "Depth-First Search (DFS)": DFS,
            "A* Search (A-Star)": AStar,
            "Greedy Best-First Search (GBFS)": GBFS,
        }
        self.selected_algo = tk.StringVar(value="Breadth-First Search (BFS)")
        # =========================
        # INIT UI
        # =========================
        self.setup_style()
        self.setup_ui()
        self.reset_app()

    # =====================================================
    # STYLE
    # =====================================================
    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)
        self.style.configure("TCombobox", font=("Segoe UI", 10), padding=5)
        self.style.map(
            "TButton",
            background=[("active", "#89b4fa")],
            foreground=[("active", "black")],
        )

    # =====================================================
    # UI
    # =====================================================
    def setup_ui(self):
        # =========================
        # TITLE
        # =========================
        title = tk.Label(
            self.root,
            text="Maze Solver AI Engine",
            bg="#1e1e2e",
            fg="white",
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(pady=10)
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True)
        # =====================================================
        # LEFT PANEL
        # =====================================================
        self.left_outer = tk.Frame(main_frame, bg="#313244", width=265)
        self.left_outer.pack(side="left", fill="y", padx=10, pady=10)
        self.left_outer.pack_propagate(False)

        self.left_canvas = tk.Canvas(self.left_outer, bg="#313244", highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(self.left_outer, orient="vertical", command=self.left_canvas.yview)
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)

        self.left_scroll.pack(side="right", fill="y")
        self.left_canvas.pack(side="left", fill="both", expand=True)

        self.left_frame = tk.Frame(self.left_canvas, bg="#313244")
        self.left_canvas_window = self.left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")

        self.left_frame.bind("<Configure>", lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))
        self.left_canvas.bind("<Configure>", lambda e: self.left_canvas.itemconfig(self.left_canvas_window, width=e.width))
        tk.Label(
            self.left_frame,
            text="Bảng điều khiển",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=15)
        # =========================
        # LEVEL SELECT
        # =========================
        tk.Label(
            self.left_frame,
            text="1. Chọn màn chơi:",
            bg="#313244",
            fg="#a6e3a1",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(5, 0), anchor="w", padx=15)
        self.level_combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.selected_level,
            values=list(self.levels.keys()),
            state="readonly",
            width=22,
        )
        self.level_combo.pack(pady=5, padx=15, fill="x")
        self.level_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_app())
        # =========================
        # ALGORITHM SELECT
        # =========================
        tk.Label(
            self.left_frame,
            text="2. Chọn thuật toán:",
            bg="#313244",
            fg="#89b4fa",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(15, 0), anchor="w", padx=15)
        self.algo_combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.selected_algo,
            values=list(self.algorithms.keys()),
            state="readonly",
            width=22,
        )
        self.algo_combo.pack(pady=5, padx=15, fill="x")
        self.algo_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_app())
        # =========================
        # HINT
        # =========================
        tk.Label(
            self.left_frame,
            text="3. Gợi ý chiến thuật:",
            bg="#313244",
            fg="#f9e2af",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(15, 0), anchor="w", padx=15)
        self.hint_label = tk.Label(
            self.left_frame,
            text="",
            bg="#181825",
            fg="#cdd6f4",
            font=("Segoe UI", 10, "italic"),
            wraplength=220,
            justify="left",
            padx=10,
            pady=10,
        )
        self.hint_label.pack(pady=5, padx=15, fill="x")
        # =========================
        # BUTTONS
        # =========================
        self.run_btn = ttk.Button(
            self.left_frame, text="▶ BẮT ĐẦU", command=self.run_algorithm
        )
        self.run_btn.pack(pady=(20, 10), padx=15, fill="x")
        self.reset_btn = ttk.Button(
            self.left_frame, text="⟳ TẢI LẠI", command=self.reset_app
        )
        self.reset_btn.pack(pady=5, padx=15, fill="x")
        self.pause_btn = ttk.Button(
            self.left_frame, text="⏸ DỪNG", command=self.toggle_pause
        )
        self.pause_btn.pack(pady=5, padx=15, fill="x")
        # =========================
        # SPEED CONTROL
        # =========================
        tk.Label(
            self.left_frame,
            text="4. Tốc độ Animation",
            bg="#313244",
            fg="#fab387",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(20, 0), anchor="w", padx=15)
        self.speed_var = tk.IntVar(value=150)
        speed_frame = tk.Frame(self.left_frame, bg="#313244")
        speed_frame.pack(fill="x", padx=15)
        self.speed_slider = tk.Scale(
            speed_frame,
            from_=20,
            to=500,
            orient="horizontal",
            variable=self.speed_var,
            bg="#313244",
            fg="white",
            troughcolor="#181825",
            highlightthickness=0,
        )
        self.speed_slider.pack(fill="x")
        # =====================================================
        # CENTER PANEL
        # =====================================================
        self.center_frame = tk.Frame(main_frame, bg="#1e1e2e")
        self.center_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(
            self.center_frame, width=500, height=500, bg="#181825", highlightthickness=0
        )
        self.canvas.pack(pady=10)
        self.status_label = tk.Label(
            self.center_frame,
            text="Trạng thái: Sẵn sàng",
            bg="#1e1e2e",
            fg="#a6e3a1",
            font=("Segoe UI", 12, "bold"),
        )
        self.status_label.pack()
        # =========================
        # STATS
        # =========================
        stats_frame = tk.Frame(self.center_frame, bg="#313244")
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        inner_stats = tk.Frame(stats_frame, bg="#313244")
        inner_stats.pack(expand=True)

        self.visited_label = tk.Label(
            inner_stats,
            text="Visited: 0",
            bg="#313244",
            fg="#f9e2af",
            font=("Consolas", 11, "bold"),
        )
        self.visited_label.pack(side="left", padx=10)
        self.frontier_label = tk.Label(
            inner_stats,
            text="Frontier: 0",
            bg="#313244",
            fg="#89b4fa",
            font=("Consolas", 11, "bold"),
        )
        self.frontier_label.pack(side="left", padx=10)
        self.path_label = tk.Label(
            inner_stats,
            text="Path: 0",
            bg="#313244",
            fg="#a6e3a1",
            font=("Consolas", 11, "bold"),
        )
        self.path_label.pack(side="left", padx=10)
        # =========================
        # PROGRESS
        # =========================
        self.progress = ttk.Progressbar(
            self.center_frame, length=400, mode="determinate"
        )
        self.progress.pack(pady=10)
        # =========================
        # SOLUTION FRAME
        # =========================
        solution_outer = tk.Frame(self.center_frame, bg="#1e1e2e")
        solution_outer.pack(fill="x", padx=20, pady=10)
        title_frame = tk.Frame(solution_outer, bg="#1e1e2e")
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="Solution Path",
            bg="#1e1e2e",
            fg="white",
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        self.path_count_label = tk.Label(
            title_frame,
            text="0 bước",
            bg="#1e1e2e",
            fg="#89b4fa",
            font=("Segoe UI", 10, "bold"),
        )
        self.path_count_label.pack(side="right")
        # =========================
        # CARD CONTAINER
        # =========================
        solution_card = tk.Frame(
            solution_outer,
            bg="#313244",
            highlightbackground="#585b70",
            highlightthickness=1,
            bd=0,
        )
        solution_card.pack(fill="x", pady=5)
        # =========================
        # SCROLLBAR
        # =========================
        self.solution_scroll = tk.Scrollbar(
            solution_card, orient="horizontal", bg="#181825"
        )
        self.solution_scroll.pack(side="bottom", fill="x")
        # =========================
        # SOLUTION CANVAS
        # =========================
        self.solution_canvas = tk.Canvas(
            solution_card,
            bg="#181825",
            height=90,
            highlightthickness=0,
            xscrollcommand=self.solution_scroll.set,
        )
        self.solution_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.solution_scroll.config(command=self.solution_canvas.xview)
        self.solution_text = self.solution_canvas.create_text(
            15,
            35,
            anchor="w",
            text="Chưa có đường đi",
            fill="#89b4fa",
            font=("Segoe UI Emoji", 12, "bold"),
        )
        # =====================================================
        # RIGHT PANEL
        # =====================================================
        self.right_frame = tk.Frame(main_frame, bg="#313244", width=250)
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)
        tk.Label(
            self.right_frame,
            text="Nhật ký (Log)",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=10)
        self.log_text = tk.Text(
            self.right_frame, bg="#181825", fg="white", font=("Consolas", 10)
        )
        self.log_scroll = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll.set)
        
        self.log_scroll.pack(side="right", fill="y", pady=10, padx=(0, 10))
        self.log_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.log_text.tag_config("success", foreground="#a6e3a1")
        self.log_text.tag_config("error", foreground="#f38ba8")
        self.log_text.tag_config("info", foreground="#89b4fa")
        self.log_text.tag_config("warning", foreground="#f9e2af")

    # =====================================================
    # DRAW GRID
    # =====================================================
    def draw_grid(self, matrix):
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell_size = 500 // cols
        for i in range(rows):
            for j in range(cols):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                value = matrix[i][j]
                if value == 1:
                    wall_color = "#313244"
                    self.canvas.create_rectangle(
                        x1 + 1,
                        y1 + 1,
                        x2 - 1,
                        y2 - 1,
                        fill=wall_color,
                        outline="#11111b",
                        width=1,
                    )
                    self.canvas.create_line(
                        x1 + 1, y1 + 1, x2 - 1, y1 + 1, fill="#585b70", width=2
                    )
                    self.canvas.create_line(
                        x1 + 1, y1 + 1, x1 + 1, y2 - 1, fill="#585b70", width=2
                    )
                    self.canvas.create_line(
                        x2 - 1, y2 - 1, x2 - 1, y1 + 1, fill="#11111b", width=2
                    )
                    self.canvas.create_line(
                        x2 - 1, y2 - 1, x1 + 1, y2 - 1, fill="#11111b", width=2
                    )
                else:
                    color = "#cdd6f4"
                    text_char = ""
                    if value == 3:
                        color = "#89b4fa"
                        text_char = "🤖"
                    elif value == 5:
                        color = "#89b4fa"
                        text_char = "👣"
                    elif value == 6:
                        # Visited (Các ô đã quét qua)
                        color = (
                            "#585b70"  # Xám nhạt/sáng hơn nền nhiều để nổi bật dấu chân
                        )
                        text_char = "👣"
                    elif value == 7:
                        # Nền vàng nhạt
                        color = "#f9e2af"
                        # Hiển thị icon dấu chân thay vì vẽ hình tròn
                        text_char = "🐾"
                    elif value == 8:
                        color = "#f38ba8"
                        text_char = "❌"
                    if (i, j) == self.goal_pos and value != 3:
                        color = "#a6e3a1"
                        text_char = "🏁"
                    self.canvas.create_rectangle(
                        x1 + 1,
                        y1 + 1,
                        x2 - 1,
                        y2 - 1,
                        fill=color,
                        outline="#11111b",
                        width=1,
                    )
                    if text_char:
                        self.canvas.create_text(
                            x1 + cell_size // 2,
                            y1 + cell_size // 2,
                            text=text_char,
                            font=("Arial", int(cell_size * 0.5)),
                        )

    # =====================================================
    # LOG
    # =====================================================
    def log(self, message, tag="info"):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

    # =====================================================
    # RESET
    # =====================================================
    def reset_app(self):
        self.is_running = False
        self.is_paused = False
        self.pause_btn.config(text="⏸ DỪNG")
        self.path = []
        self.step_idx = 0
        self.log_text.delete("1.0", tk.END)
        self.solution_canvas.itemconfig(self.solution_text, text="Chưa có")
        self.solution_canvas.config(scrollregion=(0, 0, 0, 0))
        self.progress["value"] = 0
        self.visited_label.config(text="Visited: 0")
        self.frontier_label.config(text="Frontier: 0")
        self.path_label.config(text="Path: 0")
        self.status_label.config(text="Trạng thái: Sẵn sàng", fg="#a6e3a1")
        level_name = self.selected_level.get()
        level_data = self.levels[level_name]
        current_map = copy.deepcopy(level_data["matrix"])
        self.hint_label.config(text=level_data["hint"])
        goal_x, goal_y = 19, 19
        for i in range(len(current_map)):
            for j in range(len(current_map[0])):
                if current_map[i][j] == 9:
                    goal_x, goal_y = i, j
                    current_map[i][j] = 0
                    break
        self.goal_pos = (goal_x, goal_y)
        algo_name = self.selected_algo.get()
        AlgoClass = self.algorithms[algo_name]
        self.maze_logic = AlgoClass(initial_maze=current_map, goal=self.goal_pos)
        self.draw_grid(current_map)
        self.log(f"Đã tải {level_name}", "success")
        self.log(f"Điểm đích: {self.goal_pos}", "info")
        self.log(f"Thuật toán: {algo_name}", "warning")

    def animate_search(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, self.animate_search)
            return
        if self.search_idx < len(self.search_frames):
            frame_data = self.search_frames[self.search_idx]
            if isinstance(frame_data, tuple):
                matrix, visited_count, frontier_count = frame_data
                self.visited_label.config(text=f"Visited: {visited_count}")
                self.frontier_label.config(text=f"Frontier: {frontier_count}")
            else:
                matrix = frame_data
            
            self.draw_grid(matrix)
            self.search_idx += 1
            self.root.after(self.speed_var.get(), self.animate_search)
        else:
            self.step_idx = 0
            self.animate_step()

    # =====================================================
    # RUN
    # =====================================================
    def run_algorithm(self):
        if self.is_running:
            return
        self.is_running = True
        algo_name = self.selected_algo.get()
        self.log(f"Đang chạy {algo_name}...", "warning")
        self.status_label.config(text="Đang xử lý...", fg="#f9e2af")
        start_time = time.perf_counter()
        node = self.maze_logic.solve()
        end_time = time.perf_counter()
        thinking_time_ms = (end_time - start_time) * 1000
        if node is None:
            self.log("Không tìm thấy đường đi!", "error")
            self.status_label.config(text="Không có đường đi", fg="#f38ba8")
            self.is_running = False
            return
        self.search_frames = self.maze_logic.search_history
        self.path = self.maze_logic.get_path(node)
        actions = [step[1] for step in self.path if step[1] != "START"]
        pretty_actions = []
        for act in actions:
            act_upper = act.upper()
            if act_upper == "UP":
                pretty_actions.append("⬆ UP")
            elif act_upper == "DOWN":
                pretty_actions.append("⬇ DOWN")
            elif act_upper == "LEFT":
                pretty_actions.append("⬅ LEFT")
            elif act_upper == "RIGHT":
                pretty_actions.append("➡ RIGHT")
            else:
                pretty_actions.append(act)
        solution = "   ".join(pretty_actions)
        self.path_count_label.config(text=f"{len(actions)} bước")
        self.solution_canvas.itemconfig(self.solution_text, text=solution)
        self.solution_canvas.update_idletasks()
        bbox = self.solution_canvas.bbox(self.solution_text)
        if bbox:
            self.solution_canvas.config(scrollregion=bbox)
        self.progress["maximum"] = len(self.path)
        self.progress["value"] = 0
        self.step_idx = 0
        self.log(f"Thời gian: {thinking_time_ms:.2f} ms", "success")
        self.log(f"Số bước: {len(actions)}", "success")
        self.status_label.config(text="Đang di chuyển...", fg="#89b4fa")
        self.search_idx = 0
        self.animate_search()

    # =====================================================
    # ANIMATION
    # =====================================================
    def animate_step(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, self.animate_step)
            return
        if self.step_idx < len(self.path):
            matrix, action = self.path[self.step_idx]
            self.draw_grid(matrix)
            # Sửa lỗi hiển thị dư 1: Hiện số bước thực tế (tổng frame - 1)
            self.path_label.config(text=f"Path: {self.step_idx}/{len(self.path) - 1}")
            if action != "START":
                self.log(f"Bước {self.step_idx}: Đi {action}", "info")
            self.progress["value"] = self.step_idx + 1
            self.step_idx += 1
            self.root.after(self.speed_var.get(), self.animate_step)
        else:
            self.status_label.config(text="✔ Hoàn thành!", fg="#a6e3a1")
            self.log("DONE! Đã tới đích.", "success")
            self.is_running = False

    # =====================================================
    # PAUSE
    # =====================================================
    def toggle_pause(self):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶ TIẾP TỤC")
            self.status_label.config(text="⏸ Đã tạm dừng", fg="#f9e2af")
        else:
            self.pause_btn.config(text="⏸ DỪNG")
            self.status_label.config(text="▶ Tiếp tục...", fg="#89b4fa")
