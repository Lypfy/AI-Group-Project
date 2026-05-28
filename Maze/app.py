import tkinter as tk
from tkinter import ttk
import copy  # Thư viện dùng để copy ma trận gốc

from map import MAPS
from bfs import BFS 
from aStar import AStar 

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver AI - Multi-Levels & Algorithms")
        self.root.geometry("1150x750") # Tăng chiều cao để chứa vùng hiển thị gợi ý
        self.root.configure(bg="#1e1e2e")

        # =========================
        # CẤU HÌNH HỆ THỐNG
        # =========================
        
        # 1. Quản lý Màn chơi (Nhận thẳng data từ file map.py)
        self.levels = MAPS
        # Tự động lấy tên của map đầu tiên làm mặc định
        first_level_name = list(self.levels.keys())[0] 
        self.selected_level = tk.StringVar(value=first_level_name)

        # 2. Quản lý Thuật toán
        self.algorithms = {
            "Breadth-First Search (BFS)": BFS,
            "A* Search (A-Star)": AStar
        }
        self.selected_algo = tk.StringVar(value="Breadth-First Search (BFS)")

        # =========================
        # BIẾN TRẠNG THÁI
        # =========================
        self.maze_logic = None 
        self.path = []
        self.step_idx = 0
        self.is_running = False
        self.goal_pos = (19, 19) # Sẽ tự động quét tìm và thay đổi theo map

        # Khởi tạo giao diện
        self.setup_style()
        self.setup_ui()
        self.reset_app()

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)
        self.style.configure("TCombobox", font=("Segoe UI", 10), padding=5)

    def setup_ui(self):
        # TITLE
        title = tk.Label(
            self.root, text="🧭 Maze Solver AI Engine", bg="#1e1e2e", fg="white", font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True)

        # =========================
        # LEFT PANEL (ĐIỀU KHIỂN)
        # =========================
        self.left_frame = tk.Frame(main_frame, bg="#313244", width=250)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(
            self.left_frame, text="Bảng điều khiển", bg="#313244", fg="white", font=("Segoe UI", 15, "bold")
        ).pack(pady=15)

        # 1. Combobox Chọn Màn chơi
        tk.Label(
            self.left_frame, text="1. Chọn màn chơi:", 
            bg="#313244", fg="#a6e3a1", font=("Segoe UI", 11, "bold")
        ).pack(pady=(5, 0), anchor="w", padx=15)

        self.level_combo = ttk.Combobox(
            self.left_frame, textvariable=self.selected_level, 
            values=list(self.levels.keys()), state="readonly", width=22
        )
        self.level_combo.pack(pady=5, padx=15, fill="x")
        self.level_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_app())

        # 2. Combobox Chọn Thuật toán
        tk.Label(
            self.left_frame, text="2. Chọn thuật toán:", 
            bg="#313244", fg="#89b4fa", font=("Segoe UI", 11, "bold")
        ).pack(pady=(15, 0), anchor="w", padx=15)

        self.algo_combo = ttk.Combobox(
            self.left_frame, textvariable=self.selected_algo, 
            values=list(self.algorithms.keys()), state="readonly", width=22
        )
        self.algo_combo.pack(pady=5, padx=15, fill="x")
        self.algo_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_app())

        # --- MỤC HIỂN THỊ GỢI Ý MỚI THÊM ---
        tk.Label(
            self.left_frame, text="3. Gợi ý chiến thuật:", 
            bg="#313244", fg="#f9e2af", font=("Segoe UI", 11, "bold")
        ).pack(pady=(15, 0), anchor="w", padx=15)

        self.hint_label = tk.Label(
            self.left_frame, text="", bg="#181825", fg="#cdd6f4", 
            font=("Segoe UI", 10, "italic"), wraplength=220, justify="left",
            padx=10, pady=10
        )
        self.hint_label.pack(pady=5, padx=15, fill="x")
        # ---------------------------------

        # 3. Nút Điều Khiển
        self.run_btn = ttk.Button(self.left_frame, text="▶ BẮT ĐẦU GIẢI", command=self.run_algorithm)
        self.run_btn.pack(pady=(20, 10), padx=15, fill="x")

        self.reset_btn = ttk.Button(self.left_frame, text="⟳ TẢI LẠI MÀN", command=self.reset_app)
        self.reset_btn.pack(pady=5, padx=15, fill="x")

        # =========================
        # CENTER PANEL (HIỂN THỊ)
        # =========================
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

        # KHUNG HIỂN THỊ ĐƯỜNG ĐI
        solution_frame = tk.Frame(self.center_frame, bg="#1e1e2e")
        solution_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            solution_frame, text="Đường đi (Solution Path)", bg="#1e1e2e", fg="white", font=("Segoe UI", 11, "bold")
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

        # =========================
        # RIGHT PANEL (NHẬT KÝ)
        # =========================
        self.right_frame = tk.Frame(main_frame, bg="#313244", width=250)
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(
            self.right_frame, text="Nhật ký (Log)", bg="#313244", fg="white", font=("Segoe UI", 15, "bold")
        ).pack(pady=10)

        self.log_text = tk.Text(self.right_frame, bg="#181825", fg="white", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # HÀM XỬ LÝ GIAO DIỆN & LOGIC
    # =========================
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
                    color = "#45475a"  # Tường
                    text_char = "⬛"
                elif value == 3:
                    color = "#89b4fa"  # Robot
                    text_char = "🤖"
                else:
                    color = "#cdd6f4"  # Đường đi
                    text_char = ""

                # Vẽ điểm đích cố định theo tọa độ đã tìm thấy động
                if (i, j) == self.goal_pos and value != 3:
                    color = "#a6e3a1"  
                    text_char = "🏁"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#11111b", width=1
                )
                
                if text_char:
                    self.canvas.create_text(
                        x1 + cell_size // 2, y1 + cell_size // 2, text=text_char, font=("Arial", 13)
                    )

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def reset_app(self):
        """Khởi tạo lại ứng dụng với Màn chơi và Thuật toán đang chọn"""
        self.is_running = False
        self.path = []
        self.step_idx = 0
        self.log_text.delete("1.0", tk.END)
        
        self.solution_canvas.itemconfig(self.solution_text, text="Chưa có")
        self.solution_canvas.config(scrollregion=(0, 0, 0, 0))
        self.progress["value"] = 0
        self.status_label.config(text="Trạng thái: Sẵn sàng", fg="#a6e3a1")

        # 1. Lấy thông tin Màn chơi hiện tại
        level_name = self.selected_level.get()
        level_data = self.levels[level_name]
        current_map = copy.deepcopy(level_data["matrix"])

        # 2. Cập nhật văn bản Gợi ý lên giao diện UI
        self.hint_label.config(text=level_data["hint"])

        # --- 3. LOGIC TỰ ĐỘNG QUÉT TÌM ĐÍCH (SỐ 9) ---
        goal_x, goal_y = 19, 19  # Tọa độ dự phòng mặc định
        for i in range(len(current_map)):
            for j in range(len(current_map[0])):
                if current_map[i][j] == 9:
                    goal_x, goal_y = i, j
                    current_map[i][j] = 0  # Hạ số 9 về 0 (đường đi) để tránh lỗi đổi chỗ đồ họa
                    break
        self.goal_pos = (goal_x, goal_y)
        # ---------------------------------------------

        # 4. Lấy Thuật toán
        algo_name = self.selected_algo.get()
        AlgoClass = self.algorithms[algo_name]

        # 5. Khởi tạo Object Thuật toán mới (Truyền map và goal động vào)
        self.maze_logic = AlgoClass(initial_maze=current_map, goal=self.goal_pos)
        
        # 6. Vẽ map lên màn hình
        self.draw_grid(current_map)
        self.log(f"Đã tải {level_name}")
        self.log(f"Điểm đích tự động quét thấy ở tọa độ: {self.goal_pos}")
        self.log(f"Thuật toán: {algo_name}")

    def run_algorithm(self):
        if self.is_running:
            return

        algo_name = self.selected_algo.get()
        self.log(f"Đang chạy {algo_name}...")
        self.status_label.config(text=f"Đang xử lý...", fg="#f9e2af")

        # Gọi hàm solve() của thuật toán
        node = self.maze_logic.solve()

        if node is None:
            self.log("!!! Không thể tìm thấy đường đi tới đích!")
            self.status_label.config(text="Thất bại: Không có đường đi", fg="#f38ba8")
            return

        # Lấy mảng đường đi
        self.path = self.maze_logic.get_path(node)
        self.draw_grid(self.path[0][0]) # Vẽ khung hình đầu tiên

        # In mảng Action ra khung Solution
        actions = [step[1] for step in self.path if step[1] != "START"]
        solution = "  ➜  ".join(actions)

        self.solution_canvas.itemconfig(self.solution_text, text=solution)
        self.solution_canvas.update_idletasks()
        
        bbox = self.solution_canvas.bbox(self.solution_text)
        if bbox:
            self.solution_canvas.config(scrollregion=bbox)

        # Cài đặt Progress bar và bắt đầu hiệu ứng
        self.progress["maximum"] = len(self.path)
        self.progress["value"] = 0
        self.step_idx = 0
        self.is_running = True

        self.log(f"Tìm thấy đường đi! (Số bước: {len(actions)})")
        self.status_label.config(text="Đang di chuyển...", fg="#89b4fa")
        self.animate_step()

    def animate_step(self):
        if self.step_idx < len(self.path):
            matrix, action = self.path[self.step_idx]
            self.draw_grid(matrix)
            
            if action != "START":
                self.log(f"Bước {self.step_idx}: Đi {action}")
            
            self.progress["value"] = self.step_idx + 1
            self.step_idx += 1

            self.root.after(150, self.animate_step) # 150ms delay mỗi khung hình
        else:
            self.status_label.config(text="✔ Hoàn thành!", fg="#a6e3a1")
            self.log(f"DONE! Đã tới đích.")
            self.is_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
