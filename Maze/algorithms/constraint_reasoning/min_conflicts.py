import random

class MinConflictsNode:
    def __init__(self, assignment):
        self.assignment = assignment  # dict of (r, c) -> value

class MinConflicts:
    """
    Giải bài toán CSP (ví dụ Latin Square / Đặt Gem) bằng thuật toán Min-Conflicts (Tìm kiếm cục bộ).
    """
    def __init__(self, initial_maze, goal=None, max_steps=1000):
        self.initial_maze = [row[:] for row in initial_maze]
        self.rows = len(initial_maze)
        self.cols = len(initial_maze[0])
        self.search_history = []
        self.max_steps = max_steps
        self.steps_count = 0
        
        self.puzzle_cells = []
        self.initial_assignment = {}
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.initial_maze[r][c]
                if val == 20:
                    self.puzzle_cells.append((r, c))
                elif val in [21, 22, 23, 24]:
                    self.puzzle_cells.append((r, c))
                    self.initial_assignment[(r, c)] = val
                    
                    
        self.N = 4 # Kích thước lưới 4x4
        self.colors = [21, 22, 23, 24]

    def _create_matrix(self, assignment, active_cell=None, is_failed=False):
        matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        for (r, c), val in assignment.items():
            is_conflict = self._conflicts(r, c, val, assignment) > 0
            is_active = (r, c) == active_cell
            matrix[r][c] = (val, is_conflict, is_active)

        return matrix

    def _conflicts(self, r, c, val, assignment):
        count = 0
        for (ar, ac), aval in assignment.items():
            if ar == r and ac == c: continue
            if aval == val:
                if ar == r or ac == c:
                    count += 1
        return count

    def _total_conflicts(self, assignment):
        total = 0
        for (r, c), val in assignment.items():
            total += self._conflicts(r, c, val, assignment)
        return total // 2

    def solve(self):
        import time
        pure_compute_time = 0.0
        
        if not self.puzzle_cells:
            print("Không tìm thấy lưới giải đố trong bản đồ!")
            return None
            
        # Khởi tạo trạng thái ban đầu
        t_start = time.perf_counter()
        assignment = {}
        for cell in self.puzzle_cells:
            if cell in self.initial_assignment:
                assignment[cell] = self.initial_assignment[cell]
            else:
                assignment[cell] = random.choice(self.colors)
                
        self.current_conflicts = self._total_conflicts(assignment)
        t_end = time.perf_counter()
        pure_compute_time += (t_end - t_start)
        
        # Ghi nhận khởi tạo
        matrix = self._create_matrix(assignment)
        self.search_history.append((matrix, 0, self.current_conflicts, f"Khởi tạo ngẫu nhiên (Xung đột: {self.current_conflicts})"))
        
        for step in range(1, self.max_steps + 1):
            self.steps_count = step
            
            t_start = time.perf_counter()
            if self.current_conflicts == 0:
                t_end = time.perf_counter()
                pure_compute_time += (t_end - t_start)
                final_matrix = self._create_matrix(assignment)
                self.search_history.append((final_matrix, step, 0, "Đã tìm thấy lời giải hoàn hảo (0 xung đột)!"))
                self.compute_time_ms = pure_compute_time * 1000
                return MinConflictsNode(assignment)
                
            # Lấy danh sách các ô đang có xung đột
            conflicted_cells = []
            for cell in self.puzzle_cells:
                r, c = cell
                if self._conflicts(r, c, assignment[cell], assignment) > 0:
                    conflicted_cells.append(cell)
                    
            if not conflicted_cells:
                t_end = time.perf_counter()
                pure_compute_time += (t_end - t_start)
                final_matrix = self._create_matrix(assignment)
                self.search_history.append((final_matrix, step, 0, "Đã tìm thấy lời giải hoàn hảo (0 xung đột)!"))
                self.compute_time_ms = pure_compute_time * 1000
                return MinConflictsNode(assignment)
                
            # Chọn ngẫu nhiên một biến bị xung đột
            cell = random.choice(conflicted_cells)
            r, c = cell
            
            # Tìm giá trị giảm thiểu số xung đột cho biến này
            min_conflicts_val = float('inf')
            best_colors = []
            for color in self.colors:
                c_val = self._conflicts(r, c, color, assignment)
                if c_val < min_conflicts_val:
                    min_conflicts_val = c_val
                    best_colors = [color]
                elif c_val == min_conflicts_val:
                    best_colors.append(color)
                    
            # Chọn ngẫu nhiên trong số các giá trị tốt nhất để phá vỡ thế hòa
            best_color = random.choice(best_colors)
            t_end = time.perf_counter()
            pure_compute_time += (t_end - t_start)
            
            color_names = {21: "Xanh lá", 22: "Xanh dương", 23: "Đỏ", 24: "Vàng"}
            best_color_str = color_names.get(best_color, str(best_color))
            current_color_str = color_names.get(assignment[cell], str(assignment[cell]))

            # Ghi nhận trạng thái trước khi thay đổi (hoặc giữ nguyên)
            matrix_before = self._create_matrix(assignment, active_cell=cell)
            
            if assignment[cell] != best_color:
                log_msg = f"Bước {step}: Đã chọn ô ({r},{c}) - Đổi từ {current_color_str} sang {best_color_str}"
            else:
                log_msg = f"Bước {step}: Đã chọn ô ({r},{c}) - Giữ nguyên màu {current_color_str} (không có màu tốt hơn)"
                
            self.search_history.append((matrix_before, step, self.current_conflicts, log_msg))
                
            t_start = time.perf_counter()
            assignment[cell] = best_color
            self.current_conflicts = self._total_conflicts(assignment)
            t_end = time.perf_counter()
            pure_compute_time += (t_end - t_start)
            
            matrix_after = self._create_matrix(assignment)
            self.search_history.append((matrix_after, step, self.current_conflicts, f"   -> Xung đột hiện tại: {self.current_conflicts}"))
            
        self.compute_time_ms = pure_compute_time * 1000
        return None

    def is_goal(self, node):
        return node is not None and self._total_conflicts(node.assignment) == 0

    def get_path(self, node):
        return []

