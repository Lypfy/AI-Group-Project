class ForwardCheckingNode:
    def __init__(self, assignment):
        self.assignment = assignment  # dict of col -> row

class ForwardChecking:
    """
    Giải bài toán CSP (ví dụ N-Queens) bằng thuật toán Backtracking kết hợp Forward Checking và MRV heuristic.
    """
    def __init__(self, initial_maze, goal=None):
        self.N = len(initial_maze)
        self.initial_maze = [row[:] for row in initial_maze]
        self.search_history = []
        self.assignments_count = 0
        self.backtracks_count = 0
        self.solution_matrix = None

    def _is_consistent(self, col, row, assignment):
        # Kiểm tra xem việc đặt Hậu tại (row, col) có xung đột với các quân Hậu đã xếp không
        for c, r in assignment.items():
            if r == row:  # Trùng hàng
                return False
            if abs(r - row) == abs(c - col):  # Trùng đường chéo
                return False
        return True

    def _create_matrix(self, assignment, active_cell=None, is_failed=False):
        # Tạo ma trận N x N để hiển thị
        # 0: Ô trống
        # 12: Quân Hậu hợp lệ (👑)
        # 13: Quân Hậu xung đột/thất bại (💥)
        matrix = [[0 for _ in range(self.N)] for _ in range(self.N)]
        
        for c, r in assignment.items():
            matrix[r][c] = 12
            
        if active_cell:
            r, c = active_cell
            if is_failed:
                matrix[r][c] = 13
            else:
                matrix[r][c] = 12
        return matrix

    def solve(self):
        # Khởi tạo miền giá trị cho các biến (cột)
        domains = {col: list(range(self.N)) for col in range(self.N)}
        assignment = {}
        
        # Snapshot ban đầu: bàn cờ trống
        empty_matrix = self._create_matrix(assignment)
        self.search_history.append((empty_matrix, 0, 0))

        result_assignment = self._backtrack(assignment, domains)
        
        if result_assignment is not None:
            self.solution_matrix = self._create_matrix(result_assignment)
            return ForwardCheckingNode(result_assignment)
        return None

    def _backtrack(self, assignment, domains):
        if len(assignment) == self.N:
            return assignment

        # Chọn biến (cột) chưa gán bằng heuristic MRV (Minimum Remaining Values)
        unassigned = [c for c in range(self.N) if c not in assignment]
        # Sắp xếp các cột theo kích thước miền giá trị còn lại tăng dần
        col = min(unassigned, key=lambda c: len(domains[c]))

        # Thử từng giá trị (hàng) trong miền giá trị của cột đó
        for row in domains[col]:
            if self._is_consistent(col, row, assignment):
                # Thử gán
                assignment[col] = row
                self.assignments_count += 1
                
                # Snapshot khi gán
                matrix = self._create_matrix(assignment, active_cell=(row, col))
                self.search_history.append((matrix, self.assignments_count, self.backtracks_count))

                # Thực hiện Forward Checking
                new_domains = {c: list(d) for c, d in domains.items()}
                new_domains[col] = [row]
                
                fc_failed = False
                for next_col in range(self.N):
                    if next_col not in assignment:
                        # Lọc miền giá trị của next_col: bỏ các hàng bị tấn công bởi (row, col)
                        filtered = []
                        for r_val in new_domains[next_col]:
                            # check if consistent with the new assignment
                            if r_val != row and abs(r_val - row) != abs(next_col - col):
                                filtered.append(r_val)
                        new_domains[next_col] = filtered
                        
                        # Nếu có cột bị rỗng miền giá trị -> Thất bại Forward Checking
                        if not filtered:
                            fc_failed = True
                
                if fc_failed:
                    # Ghi nhận snapshot thất bại tại ô này trước khi backtrack
                    self.backtracks_count += 1
                    failed_matrix = self._create_matrix(assignment, active_cell=(row, col), is_failed=True)
                    self.search_history.append((failed_matrix, self.assignments_count, self.backtracks_count))
                    
                    # Hủy gán
                    del assignment[col]
                    continue

                # Nếu không thất bại FC, đi tiếp
                result = self._backtrack(assignment, new_domains)
                if result is not None:
                    return result
                
                # Nếu nhánh dưới thất bại, backtrack
                self.backtracks_count += 1
                failed_matrix = self._create_matrix(assignment, active_cell=(row, col), is_failed=True)
                self.search_history.append((failed_matrix, self.assignments_count, self.backtracks_count))
                del assignment[col]
                
        return None

    def is_goal(self, node):
        return node is not None and len(node.assignment) == self.N

    def get_path(self, node):
        if node is None:
            return []
        # Trả về kết quả cuối cùng để hiển thị đường dẫn kết thúc
        matrix = self._create_matrix(node.assignment)
        return [(matrix, "DONE")]
