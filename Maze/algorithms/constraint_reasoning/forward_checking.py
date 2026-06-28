class ForwardCheckingNode:
    def __init__(self, assignment):
        self.assignment = assignment  # dict of (r, c) -> value

class ForwardChecking:
    """
    Giải bài toán CSP (ví dụ Latin Square / Đặt Gem) bằng thuật toán Backtracking kết hợp Forward Checking và MRV heuristic.
    """
    def __init__(self, initial_maze, goal=None):
        self.initial_maze = [row[:] for row in initial_maze]
        self.rows = len(initial_maze)
        self.cols = len(initial_maze[0])
        self.search_history = []
        self.assignments_count = 0
        self.backtracks_count = 0
        self.solution_matrix = None
        
        # Tìm tọa độ của khung lưới 4x4 (nơi có giá trị 20) và ngọc có sẵn
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
        # Miền giá trị cho mỗi ô (21, 22, 23, 24 tương ứng với Xanh lá, Xanh dương, Đỏ, Vàng)
        self.colors = [21, 22, 23, 24]

    def _is_consistent(self, r, c, val, assignment):
        # Không trùng màu trên cùng hàng hoặc cùng cột
        for (ar, ac), aval in assignment.items():
            if aval == val:
                if ar == r or ac == c:
                    return False
        return True

    def _create_matrix(self, assignment, active_cell=None, is_failed=False):
        matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        for (r, c), val in assignment.items():
            matrix[r][c] = val
            
        if active_cell:
            r, c = active_cell
            if is_failed:
                matrix[r][c] = 6 # Đánh dấu lỗi
        return matrix

    def solve(self):
        import time
        self.pure_compute_time = 0.0
        
        t_start = time.perf_counter()
        if not self.puzzle_cells:
            print("Không tìm thấy lưới giải đố (giá trị 20) trong bản đồ!")
            return None
            
        # Khởi tạo miền giá trị cho các biến chưa gán
        domains = {cell: list(self.colors) for cell in self.puzzle_cells if cell not in self.initial_assignment}
        assignment = self.initial_assignment.copy()
        
        # Lọc miền giá trị ban đầu dựa trên các ngọc có sẵn
        for (pr, pc), pval in assignment.items():
            for empty_cell in domains:
                er, ec = empty_cell
                if er == pr or ec == pc:
                    if pval in domains[empty_cell]:
                        domains[empty_cell].remove(pval)
                        
        t_end = time.perf_counter()
        self.pure_compute_time += (t_end - t_start)
        
        # Snapshot ban đầu: bàn cờ với các ngọc có sẵn
        empty_matrix = self._create_matrix(assignment)
        self.search_history.append((empty_matrix, 0, 0, "Bắt đầu Backtracking với Forward Checking"))

        result_assignment = self._backtrack(assignment, domains)
        
        if result_assignment is not None:
            self.solution_matrix = self._create_matrix(result_assignment)
            self.search_history.append((self.solution_matrix, self.assignments_count, self.backtracks_count, "Đã tìm thấy lời giải hoàn hảo!"))
            self.compute_time_ms = self.pure_compute_time * 1000
            return ForwardCheckingNode(result_assignment)
        
        self.compute_time_ms = self.pure_compute_time * 1000
        return None

    def _backtrack(self, assignment, domains):
        import time
        t_start = time.perf_counter()
        if len(assignment) == len(self.puzzle_cells):
            self.pure_compute_time += (time.perf_counter() - t_start)
            return assignment

        # Chọn biến (ô) chưa gán bằng heuristic MRV (Minimum Remaining Values)
        unassigned = [cell for cell in self.puzzle_cells if cell not in assignment]
        cell = min(unassigned, key=lambda c: len(domains[c]))

        r, c = cell
        self.pure_compute_time += (time.perf_counter() - t_start)

        # Thử từng màu trong miền giá trị của ô đó
        for color in domains[cell]:
            t_start = time.perf_counter()
            is_cons = self._is_consistent(r, c, color, assignment)
            self.pure_compute_time += (time.perf_counter() - t_start)
            
            if is_cons:
                t_start = time.perf_counter()
                # Thử gán
                assignment[cell] = color
                self.assignments_count += 1
                self.pure_compute_time += (time.perf_counter() - t_start)
                
                # Snapshot khi gán
                color_names = {21: "Xanh lá", 22: "Xanh dương", 23: "Đỏ", 24: "Vàng"}
                color_str = color_names.get(color, str(color))
                
                matrix = self._create_matrix(assignment, active_cell=cell)
                self.search_history.append((matrix, self.assignments_count, self.backtracks_count, f"Thử gán {color_str} tại ô ({r}, {c})"))

                t_start = time.perf_counter()
                # Thực hiện Forward Checking
                new_domains = {k: list(v) for k, v in domains.items()}
                new_domains[cell] = [color]
                
                fc_failed = False
                reduced_count = 0
                failed_cell = None
                
                for next_cell in unassigned:
                    if next_cell == cell:
                        continue
                        
                    nr, nc = next_cell
                    # Lọc miền giá trị: nếu next_cell cùng hàng hoặc cột với cell, bỏ màu `color`
                    if nr == r or nc == c:
                        if color in new_domains[next_cell]:
                            new_domains[next_cell].remove(color)
                            reduced_count += 1
                            
                    # Nếu có ô bị rỗng miền giá trị -> Thất bại Forward Checking
                    if not new_domains[next_cell]:
                        fc_failed = True
                        failed_cell = next_cell
                        break
                self.pure_compute_time += (time.perf_counter() - t_start)
                        
                if reduced_count > 0:
                    self.search_history.append((matrix, self.assignments_count, self.backtracks_count, f"FC: Loại {color_str} khỏi {reduced_count} ô trống cùng hàng/cột."))
                
                if fc_failed:
                    t_start = time.perf_counter()
                    # Ghi nhận snapshot thất bại tại ô này trước khi backtrack
                    self.backtracks_count += 1
                    self.pure_compute_time += (time.perf_counter() - t_start)
                    
                    failed_matrix = self._create_matrix(assignment, active_cell=failed_cell, is_failed=True)
                    self.search_history.append((failed_matrix, self.assignments_count, self.backtracks_count, f"FC: Ô ({failed_cell[0]}, {failed_cell[1]}) rỗng miền giá trị -> Quay lui!"))
                    
                    t_start = time.perf_counter()
                    # Hủy gán
                    del assignment[cell]
                    self.pure_compute_time += (time.perf_counter() - t_start)
                    continue

                # Nếu không thất bại FC, đi tiếp
                result = self._backtrack(assignment, new_domains)
                if result is not None:
                    return result
                
                t_start = time.perf_counter()
                # Nếu nhánh dưới thất bại, backtrack
                self.backtracks_count += 1
                self.pure_compute_time += (time.perf_counter() - t_start)
                
                failed_matrix = self._create_matrix(assignment, active_cell=cell, is_failed=True)
                self.search_history.append((failed_matrix, self.assignments_count, self.backtracks_count, f"Nhánh dưới bế tắc. Quay lui (Backtrack)!"))
                
                t_start = time.perf_counter()
                del assignment[cell]
                self.pure_compute_time += (time.perf_counter() - t_start)
                
        return None

    def is_goal(self, node):
        return node is not None and len(node.assignment) == len(self.puzzle_cells)

    def get_path(self, node):
        return []

