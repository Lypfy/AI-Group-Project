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

    def draw_grid(self, matrix, goal_pos):
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell_size = self.canvas_width // cols
        
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
                        
                    if (i, j) == goal_pos and value != 3:
                        color = "#a6e3a1"
                        text_char = "🏁"
                        
                    self.canvas.create_rectangle(
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline="#11111b", width=1,
                    )
                    
                    if text_char:
                        self.canvas.create_text(
                            x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", int(cell_size * 0.5)),
                        )
