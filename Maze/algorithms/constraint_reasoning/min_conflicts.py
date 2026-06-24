import random

class MinConflictsNode:
    def __init__(self, assignment):
        self.assignment = assignment  # dict of col -> row

class MinConflicts:
    """
    Giải bài toán CSP (ví dụ N-Queens) bằng thuật toán Min-Conflicts (Tìm kiếm cục bộ).
    """
    def __init__(self, initial_maze, goal=None, max_steps=1000):
        self.N = len(initial_maze)
        self.initial_maze = [row[:] for row in initial_maze]
        self.search_history = []
        self.max_steps = max_steps
        self.steps_count = 0

    def _create_matrix(self, assignment, active_cell=None, is_failed=False):
        # Tạo ma trận N x N để hiển thị
        # 0: Ô trống
        # 12: Quân Hậu hợp lệ (👑)
        # 13: Quân Hậu xung đột/đang xét (💥)
        matrix = [[0 for _ in range(self.N)] for _ in range(self.N)]
        
        for c, r in assignment.items():
            matrix[r][c] = 12
            
        # Kiểm tra và đánh dấu các quân hậu có xung đột
        for c, r in assignment.items():
            if self._conflicts(c, r, assignment) > 0:
                matrix[r][c] = 13

        if active_cell:
            r, c = active_cell
            matrix[r][c] = 13
        return matrix

    def _conflicts(self, col, row, assignment):
        count = 0
        for c, r in assignment.items():
            if c == col: continue
            if r == row or abs(r - row) == abs(c - col):
                count += 1
        return count

    def _total_conflicts(self, assignment):
        total = 0
        for c, r in assignment.items():
            total += self._conflicts(c, r, assignment)
        return total // 2

    def solve(self):
        # Khởi tạo ngẫu nhiên một trạng thái đầy đủ
        assignment = {col: random.randint(0, self.N - 1) for col in range(self.N)}
        current_conflicts = self._total_conflicts(assignment)
        
        # Ghi nhận khởi tạo
        matrix = self._create_matrix(assignment)
        self.search_history.append((matrix, 0, current_conflicts, f"Khởi tạo ngẫu nhiên (Lỗi: {current_conflicts})"))
        
        for step in range(1, self.max_steps + 1):
            self.steps_count = step
            
            if current_conflicts == 0:
                return MinConflictsNode(assignment)
                
            # Lấy danh sách các cột đang có xung đột
            conflicted_cols = []
            for col in range(self.N):
                if self._conflicts(col, assignment[col], assignment) > 0:
                    conflicted_cols.append(col)
                    
            if not conflicted_cols:
                return MinConflictsNode(assignment)
                
            # Chọn ngẫu nhiên một biến bị xung đột
            col = random.choice(conflicted_cols)
            
            # Tìm giá trị giảm thiểu số xung đột cho biến này
            min_conflicts_val = float('inf')
            best_rows = []
            for row in range(self.N):
                c_val = self._conflicts(col, row, assignment)
                if c_val < min_conflicts_val:
                    min_conflicts_val = c_val
                    best_rows = [row]
                elif c_val == min_conflicts_val:
                    best_rows.append(row)
                    
            # Chọn ngẫu nhiên trong số các giá trị tốt nhất để phá vỡ thế hòa
            best_row = random.choice(best_rows)
            
            # Nếu có sự thay đổi, ghi nhận lại để trực quan hóa việc di chuyển
            if assignment[col] != best_row:
                matrix_before = self._create_matrix(assignment, active_cell=(assignment[col], col))
                self.search_history.append((matrix_before, step, current_conflicts, f"Bước {step}: Cột {col} - Hậu dời từ hàng {assignment[col]} đến {best_row}"))
                
            assignment[col] = best_row
            current_conflicts = self._total_conflicts(assignment)
            
            matrix_after = self._create_matrix(assignment)
            self.search_history.append((matrix_after, step, current_conflicts, f"   -> Xung đột hiện tại: {current_conflicts}"))
            
        return None

    def is_goal(self, node):
        return node is not None and self._total_conflicts(node.assignment) == 0

    def get_path(self, node):
        if node is None:
            return []
        matrix = self._create_matrix(node.assignment)
        return [(matrix, "DONE")]
