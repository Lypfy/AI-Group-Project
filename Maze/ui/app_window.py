import tkinter as tk
from tkinter import ttk
import copy
import time

from core.map import MAPS
from algorithms.uninformed.bfs import BFS
from algorithms.informed.aStar import AStar
from algorithms.uninformed.dfs import DFS
from algorithms.informed.gbfs import GBFS
from algorithms.local.simulated_annealing import SimulatedAnnealing
from algorithms.local.steepest_ascent_hill_climbing import SteepestAscentHillClimbing
from algorithms.complex_environment.belief_state_dfs import BeliefStateDFS
from algorithms.complex_environment.partially_observable_bfs import PartiallyObservableBFS
from algorithms.constraint_reasoning.forward_checking import ForwardChecking
from algorithms.constraint_reasoning.min_conflicts import MinConflicts


# Nhúng các component UI
from ui.components.control_panel import ControlPanel
from ui.components.maze_view import MazeView
from ui.components.log_panel import LogPanel

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
        # DATA
        # =========================
        self.levels = MAPS
        self.algorithms = {
            "Breadth-First Search (BFS)": BFS,
            "Depth-First Search (DFS)": DFS,
            "A* Search (A-Star)": AStar,
            "Greedy Best-First Search (GBFS)": GBFS,
            "Simulated Annealing (SA)": SimulatedAnnealing,
            "Steepest Ascent Hill Climbing (SAHC)": SteepestAscentHillClimbing,
            "Sensorless Search (Belief State)": BeliefStateDFS,
            "Partially Observable Search (BFS)": PartiallyObservableBFS,
            "CSP (Forward Checking)": ForwardChecking,
            "CSP (Min-Conflicts)": MinConflicts,
        }

        
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
    # UI SETUP
    # =====================================================
    def setup_ui(self):
        # TITLE
        title = tk.Label(
            self.root, text="Maze Solver AI Engine", bg="#1e1e2e", fg="white", font=("Segoe UI", 22, "bold"),
        )
        title.pack(pady=10)
        
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True)
        
        # 1. LEFT PANEL (Control Panel)
        callbacks = {
            "on_reset": self.reset_app,
            "on_run": self.run_algorithm,
            "on_pause": self.toggle_pause
        }
        self.control_panel = ControlPanel(main_frame, callbacks=callbacks, levels=self.levels, algorithms=self.algorithms)
        self.control_panel.pack(side="left", fill="y", padx=10, pady=10)
        
        # Bắt alias các biến từ control_panel để gọi tiện hơn
        self.selected_level = self.control_panel.selected_level
        self.selected_algo = self.control_panel.selected_algo
        
        # 2. CENTER PANEL (Maze View)
        self.maze_view = MazeView(main_frame, width=500, height=500)
        self.maze_view.pack(side="left", fill="both", expand=True)
        
        # 3. RIGHT PANEL (Log Panel)
        self.log_panel = LogPanel(main_frame)
        self.log_panel.pack(side="right", fill="y", padx=10, pady=10)

    # =====================================================
    # HELPER
    # =====================================================
    def log(self, message, tag="info"):
        self.log_panel.log(message, tag)

    def _is_sa(self):
        return self.selected_algo.get() == "Simulated Annealing (SA)"

    # =====================================================
    # LOGIC
    # =====================================================
    def reset_app(self):
        self.is_running = False
        self.is_paused = False
        self.control_panel.pause_btn.config(text="⏸ DỪNG")
        self.path = []
        self.step_idx = 0
        self.log_panel.clear()
        
        # Reset Maze View
        self.maze_view.reset_ui()
        
        # Lấy thông tin map
        level_name = self.selected_level.get()
        level_data = self.levels[level_name]
        current_map = copy.deepcopy(level_data["matrix"])
        
        # Cập nhật hint
        self.control_panel.hint_label.config(text=level_data["hint"])
        
        # Tìm goal
        goal_x, goal_y = None, None
        for i in range(len(current_map)):
            for j in range(len(current_map[0])):
                if current_map[i][j] == 9:
                    goal_x, goal_y = i, j
                    current_map[i][j] = 0
                    break
        self.goal_pos = (goal_x, goal_y) if goal_x is not None else None
        
        # Khởi tạo thuật toán
        algo_name = self.selected_algo.get()
        AlgoClass = self.algorithms[algo_name]
        if self._is_sa():
            self.maze_logic = SimulatedAnnealing(
                initial_maze=current_map,
                goal=self.goal_pos,
                T0=self.control_panel.sa_T0.get(),
                Tmin=self.control_panel.sa_Tmin.get(),
                alpha=self.control_panel.sa_alpha.get(),
            )
        else:
            self.maze_logic = AlgoClass(initial_maze=current_map, goal=self.goal_pos)
            
        self.maze_view.draw_grid(current_map, self.goal_pos)
        
        self.log(f"Đã tải {level_name}", "success")
        if self.goal_pos:
            self.log(f"Điểm đích: {self.goal_pos}", "info")
        self.log(f"Thuật toán: {algo_name}", "warning")
        if self._is_sa():
            self.log(f"  T₀={self.control_panel.sa_T0.get()}, α={self.control_panel.sa_alpha.get()}, T_min={self.control_panel.sa_Tmin.get()}", "info")

    def _animate_smooth_transition(self, old_matrix, new_matrix, action, merge_cells, speed, on_complete):
        frames = 8
        interval = max(10, speed // frames)
        
        def frame_step(f):
            if not self.is_running: return
            if self.is_paused:
                self.root.after(100, lambda: frame_step(f))
                return
            
            progress = f / frames
            self.maze_view.draw_grid_smooth(old_matrix, new_matrix, self.goal_pos, action, merge_cells, progress)
            
            if f < frames:
                self.root.after(interval, lambda: frame_step(f + 1))
            else:
                on_complete()
                
        frame_step(1)

    def animate_search(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, self.animate_search)
            return
            
        if self.search_idx < len(self.search_frames):
            frame_data = self.search_frames[self.search_idx]
            
            if self._is_sa():
                matrix, T, deltaE, prob, accepted = frame_data
                sign = "✅" if accepted else "❌"
                self.maze_view.visited_label.config(text=f"T: {T:.3f}")
                self.maze_view.frontier_label.config(
                    text=f"ΔE: {deltaE:+.2f}",
                    fg="#a6e3a1" if deltaE < 0 else "#f38ba8")
                self.maze_view.path_label.config(text=f"P: {prob:.3f} {sign}")
                self.maze_view.draw_grid(matrix, self.goal_pos)
                self.search_idx += 1
                self.root.after(self.control_panel.speed_var.get(), self.animate_search)
            elif isinstance(frame_data, tuple):
                if len(frame_data) == 6:
                    matrix, visited_count, frontier_count, belief_size, action, merge_cells = frame_data
                    self.maze_view.visited_label.config(text=f"Visited: {visited_count}")
                    self.maze_view.frontier_label.config(text=f"Frontier: {frontier_count}")
                    self.maze_view.path_label.config(text=f"Belief: {belief_size}")
                    self.maze_view.draw_grid(matrix, self.goal_pos, action=action, merge_cells=merge_cells)
                            
                    self.search_idx += 1
                    self.root.after(self.control_panel.speed_var.get(), self.animate_search)
                elif len(frame_data) == 4 and self.selected_algo.get() == "CSP (Min-Conflicts)":
                    matrix, steps, conflicts, msg = frame_data
                    self.maze_view.visited_label.config(text=f"Steps: {steps}")
                    self.maze_view.frontier_label.config(text=f"Conflicts: {conflicts}")
                    self.maze_view.path_label.config(text="State: Solving")
                    if msg:
                        self.log(msg, "info")
                    self.maze_view.draw_grid(matrix, self.goal_pos)
                    self.search_idx += 1
                    self.root.after(self.control_panel.speed_var.get(), self.animate_search)
                elif len(frame_data) == 3:
                    matrix, visited_count, frontier_count = frame_data
                    if self.selected_algo.get() == "CSP (Forward Checking)":
                        self.maze_view.visited_label.config(text=f"Assignments: {visited_count}")
                        self.maze_view.frontier_label.config(text=f"Backtracks: {frontier_count}")
                        self.maze_view.path_label.config(text="State: Solving")
                    else:
                        self.maze_view.visited_label.config(text=f"Visited: {visited_count}")
                        self.maze_view.frontier_label.config(text=f"Cost/Frontier: {frontier_count}")
                    self.maze_view.draw_grid(matrix, self.goal_pos)
                    self.search_idx += 1
                    self.root.after(self.control_panel.speed_var.get(), self.animate_search)
            else:
                matrix = frame_data
                self.maze_view.draw_grid(matrix, self.goal_pos)
                self.search_idx += 1
                self.root.after(self.control_panel.speed_var.get(), self.animate_search)
        else:
            self.step_idx = 0
            self.animate_step()

    def run_algorithm(self):
        if self.is_running:
            return
        self.is_running = True
        algo_name = self.selected_algo.get()
        self.log(f"Đang chạy {algo_name}...", "warning")
        self.maze_view.status_label.config(text="Đang xử lý...", fg="#f9e2af")
        
        # Khởi tạo lại thuật toán để cập nhật các tham số mới nhất
        level_name = self.selected_level.get()
        current_map = copy.deepcopy(self.levels[level_name]["matrix"])
        AlgoClass = self.algorithms[algo_name]
        if self._is_sa():
            self.maze_logic = SimulatedAnnealing(
                initial_maze=current_map,
                goal=self.goal_pos,
                T0=self.control_panel.sa_T0.get(),
                Tmin=self.control_panel.sa_Tmin.get(),
                alpha=self.control_panel.sa_alpha.get(),
            )
        else:
            self.maze_logic = AlgoClass(initial_maze=current_map, goal=self.goal_pos)
            
        start_time = time.perf_counter()
        node = self.maze_logic.solve()
        end_time = time.perf_counter()
        thinking_time_ms = (end_time - start_time) * 1000
        
        if node is None:
            self.log("Không tìm thấy đường đi!", "error")
            self.maze_view.status_label.config(text="Không có đường đi", fg="#f38ba8")
            self.is_running = False
            return
            
        self.is_success = self.maze_logic.is_goal(node)
        self.search_frames = self.maze_logic.search_history
        self.path = self.maze_logic.get_path(node)
        
        actions = [step[1] for step in self.path if step[1] != "START"]
        pretty_actions = []
        for act in actions:
            act_upper = act.upper()
            if act_upper == "UP": pretty_actions.append("⬆ UP")
            elif act_upper == "DOWN": pretty_actions.append("⬇ DOWN")
            elif act_upper == "LEFT": pretty_actions.append("⬅ LEFT")
            elif act_upper == "RIGHT": pretty_actions.append("➡ RIGHT")
            else: pretty_actions.append(act)
            
        solution_str = "   ".join(pretty_actions)
        self.maze_view.update_solution(len(actions), solution_str)
        
        self.maze_view.progress["maximum"] = len(self.path)
        self.maze_view.progress["value"] = 0
        self.step_idx = 0
        self.log(f"Thời gian: {thinking_time_ms:.2f} ms", "success")
        self.log(f"Số bước: {len(actions)}", "success")
        self.maze_view.status_label.config(text="Đang di chuyển...", fg="#89b4fa")
        self.search_idx = 0
        self.animate_search()

    def animate_step(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.root.after(100, self.animate_step)
            return
            
        if self.step_idx < len(self.path):
            path_tuple = self.path[self.step_idx]
            is_smooth = False
            
            if len(path_tuple) == 3:
                matrix, action, merge_cells = path_tuple
                is_smooth = True
            else:
                matrix, action = path_tuple
                self.maze_view.draw_grid(matrix, self.goal_pos)
            
            if self.selected_algo.get() in ["CSP (Forward Checking)", "CSP (Min-Conflicts)"]:
                if self.selected_algo.get() == "CSP (Forward Checking)":
                    self.maze_view.visited_label.config(text=f"Assignments: {self.maze_logic.assignments_count}")
                    self.maze_view.frontier_label.config(text=f"Backtracks: {self.maze_logic.backtracks_count}")
                else:
                    self.maze_view.visited_label.config(text=f"Steps: {self.maze_logic.steps_count}")
                    self.maze_view.frontier_label.config(text=f"Conflicts: 0")
                self.maze_view.path_label.config(text="State: Solved")
            else:
                self.maze_view.path_label.config(text=f"Path: {self.step_idx}/{len(self.path) - 1}")
            
            # Use path_tuple[1] as action
            action_name = path_tuple[1]
            if action_name != "START":
                if is_smooth:
                    belief_count = sum(row.count(10) for row in matrix) + sum(row.count(3) for row in matrix)
                    merge_count = len(merge_cells) if 'merge_cells' in locals() else 0
                    msg = f"Bước {self.step_idx}: Đi {action_name} | Bóng ma còn: {belief_count}"
                    if merge_count > 0:
                        msg += f" | Dồn cục: {merge_count}"
                    self.log(msg, "warning" if merge_count > 0 else "info")
                else:
                    if self.selected_algo.get() in ["CSP (Forward Checking)", "CSP (Min-Conflicts)"]:
                        self.log("Đã tìm thấy lời giải N-Queens!", "success")
                    else:
                        self.log(f"Bước {self.step_idx}: Đi {action_name}", "info")
                
            self.maze_view.progress["value"] = self.step_idx + 1
            
            if is_smooth:
                old_matrix = matrix
                if self.step_idx > 0:
                    prev_path = self.path[self.step_idx - 1]
                    old_matrix = prev_path[0]
                
                self.step_idx += 1
                speed = self.control_panel.speed_var.get()
                self._animate_smooth_transition(old_matrix, matrix, action, merge_cells, speed, self.animate_step)
            else:
                self.step_idx += 1
                self.root.after(self.control_panel.speed_var.get(), self.animate_step)
        else:
            if getattr(self, 'is_success', True):
                self.maze_view.status_label.config(text="✔ Hoàn thành!", fg="#a6e3a1")
                if self.selected_algo.get() in ["CSP (Forward Checking)", "CSP (Min-Conflicts)"]:
                    self.log("DONE! Đã xếp thành công 8 quân Hậu thỏa mãn tất cả ràng buộc.", "success")
                else:
                    self.log("DONE! Đã tới đích.", "success")
            else:
                self.maze_view.status_label.config(text="❌ Dừng lại: Bị kẹt!", fg="#f38ba8")
                self.log("Bị kẹt ở Cực đại cục bộ hoặc hết nhiệt độ!", "error")
            self.is_running = False

    def toggle_pause(self):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.control_panel.pause_btn.config(text="▶ TIẾP TỤC")
            self.maze_view.status_label.config(text="⏸ Đã tạm dừng", fg="#f9e2af")
        else:
            self.control_panel.pause_btn.config(text="⏸ DỪNG")
            self.maze_view.status_label.config(text="▶ Tiếp tục...", fg="#89b4fa")
