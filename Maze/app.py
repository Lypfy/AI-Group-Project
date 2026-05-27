# Giao diện demo

import tkinter as tk
from tkinter import ttk
from bfs import BFS 

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver AI - 20x20 BFS")
        self.root.geometry("1100x650")
        self.root.configure(bg="#1e1e2e")

        # =========================
        # VARIABLES
        # =========================
        self.maze_logic = BFS()  
        self.path = []
        self.step_idx = 0
        self.is_running = False
        self.goal_pos = (19, 19)   # Cập nhật tọa độ đích mới

        # =========================
        # SETUP UI
        # =========================
        self.setup_style()
        self.setup_ui()
        
        initial_matrix = self.maze_logic.frontier[0].state
        self.draw_grid(initial_matrix)

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TButton", font=("Segoe UI", 11, "bold"), padding=10
        )

    def setup_ui(self):
        # TITLE
        title = tk.Label(
            self.root, text="🧭 20x20 Maze Solver AI (BFS)", bg="#1e1e2e", fg="white", font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True)

        # LEFT PANEL
        self.left_frame = tk.Frame(main_frame, bg="#313244", width=220)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(
            self.left_frame, text="Điều khiển", bg="#313244", fg="white", font=("Segoe UI", 15, "bold")
        ).pack(pady=15)

        tk.Label(
            self.left_frame, text="Thuật toán hiện tại:\nBreadth-First Search\n(Ma trận 20x20)", 
            bg="#313244", fg="#89b4fa", font=("Segoe UI", 11, "italic"), justify="center"
        ).pack(pady=5)

        self.run_btn = ttk.Button(self.left_frame, text="▶ RUN", command=self.run_algorithm)
        self.run_btn.pack(pady=30, padx=15, fill="x")

        self.reset_btn = ttk.Button(self.left_frame, text="⟳ RESET", command=self.reset_app)
        self.reset_btn.pack(pady=10, padx=15, fill="x")

        # CENTER PANEL
        self.center_frame = tk.Frame(main_frame, bg="#1e1e2e")
        self.center_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.center_frame, width=500, height=500, bg="#181825", highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.status_label = tk.Label(
            self.center_frame, text="Trạng thái: Sẵn sàng", bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack()

        self.progress = ttk.Progressbar(self.center_frame, length=400, mode="determinate")
        self.progress.pack(pady=10)

        # SOLUTION FRAME
        solution_frame = tk.Frame(self.center_frame, bg="#1e1e2e")
        solution_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            solution_frame, text="Solution Path", bg="#1e1e2e", fg="white", font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        solution_container = tk.Frame(solution_frame, bg="#313244", height=60)
        solution_container.pack(fill="x", pady=5)

        self.solution_scroll = tk.Scrollbar(solution_container, orient="horizontal")
        self.solution_scroll.pack(side="bottom", fill="x")

        self.solution_canvas = tk.Canvas(
            solution_container, bg="#181825", height=50, width=500,
            highlightthickness=0, xscrollcommand=self.solution_scroll.set
        )
        self.solution_canvas.pack(side="left", fill="both", expand=True)
        self.solution_scroll.config(command=self.solution_canvas.xview)

        self.solution_text = self.solution_canvas.create_text(
            10, 22, anchor="w", text="Chưa có", fill="#89b4fa", font=("Consolas", 11, "bold")
        )

        # RIGHT PANEL
        self.right_frame = tk.Frame(main_frame, bg="#313244", width=250)
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(
            self.right_frame, text="Nhật ký (Log)", bg="#313244", fg="white", font=("Segoe UI", 15, "bold")
        ).pack(pady=10)

        self.log_text = tk.Text(self.right_frame, bg="#181825", fg="white", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # VẼ MÊ CUNG LÊN CANVAS
    # =========================
    def draw_grid(self, matrix):
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell_size = 500 // cols  # Sẽ tự động tính ra 500 // 20 = 25 pixel mỗi ô

        for i in range(rows):
            for j in range(cols):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                value = matrix[i][j]
                
                if value == 1:
                    color = "#45475a"  
                    text_char = "⬛"
                elif value == 3:
                    color = "#89b4fa"  
                    text_char = "🤖"
                else:
                    color = "#cdd6f4"  
                    text_char = ""

                if (i, j) == self.goal_pos and value != 3:
                    color = "#a6e3a1"  
                    text_char = "🏁"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#11111b", width=1 # Giảm nét viền xuống 1 pixel cho thanh thoát
                )
                
                # Điều chỉnh giảm kích thước font chữ xuống cỡ 13 để vừa ô 25x25
                if text_char:
                    self.canvas.create_text(
                        x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", 13)
                    )

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def run_algorithm(self):
        if self.is_running:
            return

        self.reset_app() 
        self.log("Running BFS on 20x20 Maze...")
        self.status_label.config(text="Đang chạy thuật toán BFS")

        node = self.maze_logic.solve()

        if node is None:
            self.log("!!! Không thể thoát khỏi mê cung")
            self.status_label.config(text="Không tìm thấy lời giải", fg="#f38ba8")
            return

        self.path = self.maze_logic.get_path(node)
        self.draw_grid(self.path[0][0])

        actions = [step[1] for step in self.path if step[1] != "START"]
        solution = "  ➜  ".join(actions)

        self.solution_canvas.itemconfig(self.solution_text, text=solution)
        self.solution_canvas.update_idletasks()
        
        bbox = self.solution_canvas.bbox(self.solution_text)
        if bbox:
            self.solution_canvas.config(scrollregion=bbox)

        self.progress["maximum"] = len(self.path)
        self.progress["value"] = 0
        self.step_idx = 0
        self.is_running = True

        self.animate_step()

    def animate_step(self):
        if self.step_idx < len(self.path):
            matrix, action = self.path[self.step_idx]
            self.draw_grid(matrix)
            
            if action != "START":
                self.log(f"Step {self.step_idx}: Move {action}")
            
            self.progress["value"] = self.step_idx + 1
            self.step_idx += 1

            # Rút ngắn thời gian delay xuống 150ms để robot chạy nhanh hơn trên map lớn
            self.root.after(150, self.animate_step) 
        else:
            self.status_label.config(text="✔ Hoàn thành", fg="#a6e3a1")
            self.log(f"DONE! Tổng số bước di chuyển: {len(self.path) - 1}")
            self.is_running = False

    def reset_app(self):
        self.is_running = False
        self.path = []
        self.step_idx = 0
        self.log_text.delete("1.0", tk.END)
        
        self.solution_canvas.itemconfig(self.solution_text, text="Chưa có")
        self.solution_canvas.config(scrollregion=(0, 0, 0, 0))
        self.progress["value"] = 0
        self.status_label.config(text="Trạng thái: Sẵn sàng", fg="#a6e3a1")

        self.maze_logic = BFS()
        initial_matrix = self.maze_logic.frontier[0].state
        self.draw_grid(initial_matrix)

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
