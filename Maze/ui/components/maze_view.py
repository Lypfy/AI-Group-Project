import tkinter as tk
from tkinter import ttk

class MazeView(tk.Frame):
    def __init__(self, parent, width=500, height=500, *args, **kwargs):
        super().__init__(parent, bg="#1e1e2e", *args, **kwargs)
        self.canvas_width = width
        self.canvas_height = height
        self.setup_ui()

    def setup_ui(self):
        self.canvas = tk.Canvas(
            self, width=self.canvas_width, height=self.canvas_height, bg="#181825", highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        self.status_label = tk.Label(
            self,
            text="Trạng thái: Sẵn sàng",
            bg="#1e1e2e",
            fg="#a6e3a1",
            font=("Segoe UI", 12, "bold"),
        )
        self.status_label.pack()

        # STATS
        stats_frame = tk.Frame(self, bg="#313244")
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        inner_stats = tk.Frame(stats_frame, bg="#313244")
        inner_stats.pack(expand=True)

        self.visited_label = tk.Label(
            inner_stats, text="Visited: 0", bg="#313244", fg="#f9e2af", font=("Consolas", 11, "bold"),
        )
        self.visited_label.pack(side="left", padx=10)
        self.frontier_label = tk.Label(
            inner_stats, text="Frontier: 0", bg="#313244", fg="#89b4fa", font=("Consolas", 11, "bold"),
        )
        self.frontier_label.pack(side="left", padx=10)
        self.path_label = tk.Label(
            inner_stats, text="Path: 0", bg="#313244", fg="#a6e3a1", font=("Consolas", 11, "bold"),
        )
        self.path_label.pack(side="left", padx=10)

        # PROGRESS
        self.progress = ttk.Progressbar(self, length=400, mode="determinate")
        self.progress.pack(pady=10)

        # SOLUTION FRAME
        solution_outer = tk.Frame(self, bg="#1e1e2e")
        solution_outer.pack(fill="x", padx=20, pady=10)
        title_frame = tk.Frame(solution_outer, bg="#1e1e2e")
        title_frame.pack(fill="x")
        tk.Label(
            title_frame, text="Solution Path", bg="#1e1e2e", fg="white", font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        
        self.path_count_label = tk.Label(
            title_frame, text="0 bước", bg="#1e1e2e", fg="#89b4fa", font=("Segoe UI", 10, "bold"),
        )
        self.path_count_label.pack(side="right")
        
        # CARD CONTAINER
        solution_card = tk.Frame(
            solution_outer, bg="#313244", highlightbackground="#585b70", highlightthickness=1, bd=0,
        )
        solution_card.pack(fill="x", pady=5)
        
        # SCROLLBAR
        self.solution_scroll = tk.Scrollbar(solution_card, orient="horizontal", bg="#181825")
        self.solution_scroll.pack(side="bottom", fill="x")
        
        # SOLUTION CANVAS
        self.solution_canvas = tk.Canvas(
            solution_card, bg="#181825", height=90, highlightthickness=0, xscrollcommand=self.solution_scroll.set,
        )
        self.solution_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.solution_scroll.config(command=self.solution_canvas.xview)
        
        self.solution_text = self.solution_canvas.create_text(
            15, 35, anchor="w", text="Chưa có đường đi", fill="#89b4fa", font=("Segoe UI Emoji", 12, "bold"),
        )

    def update_solution(self, actions_count, solution_str):
        self.path_count_label.config(text=f"{actions_count} bước")
        self.solution_canvas.itemconfig(self.solution_text, text=solution_str)
        self.solution_canvas.update_idletasks()
        bbox = self.solution_canvas.bbox(self.solution_text)
        if bbox:
            self.solution_canvas.config(scrollregion=bbox)

    def reset_ui(self):
        self.solution_canvas.itemconfig(self.solution_text, text="Chưa có")
        self.solution_canvas.config(scrollregion=(0, 0, 0, 0))
        self.progress["value"] = 0
        self.visited_label.config(text="Visited: 0")
        self.frontier_label.config(text="Frontier: 0")
        self.path_label.config(text="Path: 0")
        self.status_label.config(text="Trạng thái: Sẵn sàng", fg="#a6e3a1")
        self.path_count_label.config(text="0 bước")
        self.canvas.delete("all")

    def draw_grid(self, matrix, goal_pos, action=None, merge_cells=None):
        if merge_cells is None:
            merge_cells = set()
            
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell_size = self.canvas_width // cols
        
        is_chessboard = False
        if rows == cols:
            has_walls = any(1 in row for row in matrix)
            if not has_walls or any(val in [12, 13] for row in matrix for val in row):
                is_chessboard = True
        
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
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=wall_color, outline="#11111b", width=1,
                    )
                    self.canvas.create_line(x1 + 1, y1 + 1, x2 - 1, y1 + 1, fill="#585b70", width=2)
                    self.canvas.create_line(x1 + 1, y1 + 1, x1 + 1, y2 - 1, fill="#585b70", width=2)
                    self.canvas.create_line(x2 - 1, y2 - 1, x2 - 1, y1 + 1, fill="#11111b", width=2)
                    self.canvas.create_line(x2 - 1, y2 - 1, x1 + 1, y2 - 1, fill="#11111b", width=2)
                else:
                    if is_chessboard:
                        color = "#cdd6f4" if (i + j) % 2 == 0 else "#585b70"
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
                        color = "#585b70"  
                        text_char = "👣"
                    elif value == 7:
                        color = "#f9e2af"
                        text_char = "🐾"
                    elif value == 8:
                        color = "#f38ba8"
                        text_char = "❌"
                    elif value == 10:
                        # 1. Ghost Effect: Màu xanh dương nhạt (opacity illusion)
                        color = "#b4befe"
                        text_char = "👻"
                        # 2. Merging Animation: Chớp màu vàng khi các bóng ma dồn lại
                        if (i, j) in merge_cells:
                            color = "#f9e2af"
                    elif value == 12:
                        if not is_chessboard:
                            color = "#cba6f7"
                        text_char = "👑"
                    elif value == 13:
                        color = "#f38ba8"
                        text_char = "💥"
                        
                    if (i, j) == goal_pos and value not in [3, 10, 12, 13]:
                        color = "#a6e3a1"
                        text_char = "🏁"
                        
                    self.canvas.create_rectangle(
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline="#11111b", width=1,
                    )
                    
                    if text_char:
                        self.canvas.create_text(
                            x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", int(cell_size * 0.5)),
                        )
                        
                    # 3. Hiển thị hướng di chuyển đồng loạt
                    if value == 10 and action:
                        arrow_text = ""
                        act_upper = action.upper()
                        if act_upper == "UP": arrow_text = "↑"
                        elif act_upper == "DOWN": arrow_text = "↓"
                        elif act_upper == "LEFT": arrow_text = "←"
                        elif act_upper == "RIGHT": arrow_text = "→"
                        
                        if arrow_text:
                            self.canvas.create_text(
                                x1 + cell_size // 2, y1 + cell_size // 2 + int(cell_size * 0.25), 
                                text=arrow_text, fill="#ff0400", font=("Arial", int(cell_size * 0.35), "bold")
                            )

    def draw_grid_smooth(self, old_matrix, new_matrix, goal_pos, action, merge_cells, progress):
        if merge_cells is None:
            merge_cells = set()
            
        self.canvas.delete("all")
        rows = len(new_matrix)
        cols = len(new_matrix[0])
        cell_size = self.canvas_width // cols
        
        is_chessboard = False
        if rows == cols:
            has_walls = any(1 in row for row in new_matrix)
            if not has_walls or any(val in [12, 13] for row in new_matrix for val in row):
                is_chessboard = True
        
        # 1. Draw static background
        for i in range(rows):
            for j in range(cols):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                value = new_matrix[i][j]
                
                if value == 1:
                    wall_color = "#313244"
                    self.canvas.create_rectangle(
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=wall_color, outline="#11111b", width=1,
                    )
                    self.canvas.create_line(x1 + 1, y1 + 1, x2 - 1, y1 + 1, fill="#585b70", width=2)
                    self.canvas.create_line(x1 + 1, y1 + 1, x1 + 1, y2 - 1, fill="#585b70", width=2)
                    self.canvas.create_line(x2 - 1, y2 - 1, x2 - 1, y1 + 1, fill="#11111b", width=2)
                    self.canvas.create_line(x2 - 1, y2 - 1, x1 + 1, y2 - 1, fill="#11111b", width=2)
                else:
                    if is_chessboard:
                        color = "#cdd6f4" if (i + j) % 2 == 0 else "#585b70"
                    else:
                        color = "#cdd6f4"
                    text_char = ""
                    # Static tracks/marks
                    if value == 5:
                        color = "#89b4fa"
                        text_char = "👣"
                    elif value == 6:
                        color = "#585b70"  
                        text_char = "👣"
                    elif value == 7:
                        color = "#f9e2af"
                        text_char = "🐾"
                    elif value == 8:
                        color = "#f38ba8"
                        text_char = "❌"
                    elif value == 12:
                        if not is_chessboard:
                            color = "#cba6f7"
                        text_char = "👑"
                    elif value == 13:
                        color = "#f38ba8"
                        text_char = "💥"
                        
                    if (i, j) == goal_pos and value not in [3, 10, 12, 13]:
                        color = "#a6e3a1"
                        text_char = "🏁"
                        
                    # For moving entities (3 or 10), draw empty background (tint if merging)
                    if value in [3, 10]:
                        if is_chessboard:
                            color = "#cdd6f4" if (i + j) % 2 == 0 else "#585b70"
                        else:
                            color = "#cdd6f4"
                        # Only flash merge when progress is almost complete
                        if value == 10 and (i, j) in merge_cells and progress > 0.5:
                            color = "#f9e2af"
                            
                    self.canvas.create_rectangle(
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline="#11111b", width=1,
                    )
                    
                    if text_char:
                        self.canvas.create_text(
                            x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", int(cell_size * 0.5)),
                        )

        # 2. Draw dynamic moving entities from old_matrix to new_matrix
        if action:
            act_upper = action.upper()
        else:
            act_upper = None
            
        for i in range(rows):
            for j in range(cols):
                old_val = old_matrix[i][j]
                if old_val in [3, 10]:
                    # Calculate new logical position
                    ni, nj = i, j
                    if act_upper == "UP" and i > 0 and old_matrix[i - 1][j] != 1:
                        ni = i - 1
                    elif act_upper == "DOWN" and i < rows - 1 and old_matrix[i + 1][j] != 1:
                        ni = i + 1
                    elif act_upper == "LEFT" and j > 0 and old_matrix[i][j - 1] != 1:
                        nj = j - 1
                    elif act_upper == "RIGHT" and j < cols - 1 and old_matrix[i][j + 1] != 1:
                        nj = j + 1
                        
                    # Interpolated floating coordinates
                    curr_i = i + (ni - i) * progress
                    curr_j = j + (nj - j) * progress
                    
                    x1 = curr_j * cell_size
                    y1 = curr_i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    is_robot = (new_matrix[ni][nj] == 3)
                    
                    color = "#89b4fa" if is_robot else "#b4befe"
                    text_char = "🤖" if is_robot else "👻"
                    
                    # Draw entity with slight padding
                    pad = 2
                    self.canvas.create_rectangle(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill=color, outline="#11111b", width=1,
                    )
                    self.canvas.create_text(
                        x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", int(cell_size * 0.5)),
                    )
                    
                    if act_upper and not is_robot:
                        arrow_text = ""
                        if act_upper == "UP": arrow_text = "↑"
                        elif act_upper == "DOWN": arrow_text = "↓"
                        elif act_upper == "LEFT": arrow_text = "←"
                        elif act_upper == "RIGHT": arrow_text = "→"
                        if arrow_text:
                            self.canvas.create_text(
                                x1 + cell_size // 2, y1 + cell_size // 2 + int(cell_size * 0.25), 
                                text=arrow_text, fill="#ff0400", font=("Arial", int(cell_size * 0.35), "bold")
                            )
