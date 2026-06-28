class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path


from levels.maze_data import RESONANCE_MAP

class SteepestAscentHillClimbing:
    """
    Steepest Ascent Hill Climbing cho bài toán tìm đường trong mê cung.

    search_history: list of tuple
        (matrix_snapshot, step_count, current_cost)
    """

    def __init__(self, initial_maze, goal=(19, 19), res_map=None):
        self.goal = goal
        self.res_map = res_map
        self.is_resonance_level = (res_map is not None)
        self.initial_maze = [row[:] for row in initial_maze]
        self.start_node = Node(initial_maze, None, "START", self._cost(initial_maze))
        self.search_history = []
        self.visited = set()
        self.visited.add(self.matrix_to_tuple(initial_maze))

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    def _display_val(self, cost):
        return 100 - cost if self.is_resonance_level else cost

    def _display_name(self):
        return "Resonance" if self.is_resonance_level else "Chi phí"

    def matrix_to_tuple(self, matrix):
        return tuple(cell for row in matrix for cell in row)

    def get_location(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == 3:
                    return i, j
        return None, None

    def _cost(self, matrix):
        x, y = self.get_location(matrix)
        if x is None:
            return float("inf")
            
        if self.is_resonance_level:
            res = self.res_map[x][y]
            return 100 - res
            
        return abs(x - self.goal[0]) + abs(y - self.goal[1])

    def possible_move(self, node):
        matrix = node.state
        x, y = self.get_location(matrix)
        moves = []
        if x > 0 and matrix[x - 1][y] != 1:             moves.append("up")
        if x < len(matrix) - 1 and matrix[x + 1][y] != 1: moves.append("down")
        if y > 0 and matrix[x][y - 1] != 1:             moves.append("left")
        if y < len(matrix[0]) - 1 and matrix[x][y + 1] != 1: moves.append("right")
        return moves

    def _do_move(self, node, m):
        matrix = [row[:] for row in node.state]
        x, y = self.get_location(node.state)
        if m == "up":    matrix[x][y], matrix[x - 1][y] = matrix[x - 1][y], matrix[x][y]
        elif m == "down":  matrix[x][y], matrix[x + 1][y] = matrix[x + 1][y], matrix[x][y]
        elif m == "left":  matrix[x][y], matrix[x][y - 1] = matrix[x][y - 1], matrix[x][y]
        elif m == "right": matrix[x][y], matrix[x][y + 1] = matrix[x][y + 1], matrix[x][y]
        return Node(matrix, node, m, self._cost(matrix))

    def is_goal(self, node):
        x, y = self.get_location(node.state)
        return (x, y) == self.goal

    # ─────────────────────────────────────────────
    # get_path — tương thích với app_window
    # ─────────────────────────────────────────────

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()

        path = []
        for i, n in enumerate(nodes):
            matrix = [row[:] for row in n.state]
            for prev_n in nodes[1:i]:
                px, py = self.get_location(prev_n.state)
                if matrix[px][py] != 3:
                    matrix[px][py] = 6
            path.append((matrix, n.act))
        return path

    # ─────────────────────────────────────────────
    # solve
    # ─────────────────────────────────────────────

    def solve(self):
        import time
        current = self.start_node
        trail = [row[:] for row in self.initial_maze]   # vết đi tĩnh
        step = 0
        dn = self._display_name()
        self.pure_compute_time = 0.0
        
        # Thêm trạng thái ban đầu vào history để thấy được trên UI
        snapshot = [row[:] for row in trail]
        cx, cy = self.get_location(current.state)
        if cx is not None:
            snapshot[cx][cy] = 3
        self.search_history.append((snapshot, len(self.visited), 0, f"Bắt đầu tại ({cy}, {cx}): {dn}={self._display_val(current.cost_path)}"))

        while True:
            t_start = time.perf_counter()
            is_goal = self.is_goal(current)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if is_goal:
                self.search_history.append((snapshot, len(self.visited), 0, f"Đã đến đích {self.goal}!"))
                break

            t_start = time.perf_counter()
            moves = self.possible_move(current)
            if not moves:
                self.pure_compute_time += (time.perf_counter() - t_start)
                self.search_history.append((snapshot, len(self.visited), 0, f"Không có bước đi tiếp theo. Bị kẹt!"))
                break

            best_nxt = None
            best_cost = float('inf')

            eval_details = []
            for m in moves:
                nxt = self._do_move(current, m)
                nx, ny = self.get_location(nxt.state)
                eval_details.append(f"{m}({ny},{nx}):{self._display_val(nxt.cost_path)}")
                if nxt.cost_path < best_cost:
                    best_cost = nxt.cost_path
                    best_nxt = nxt

            eval_str = ", ".join(eval_details)

            if best_nxt is None or best_nxt.cost_path >= current.cost_path:
                self.pure_compute_time += (time.perf_counter() - t_start)
                msg = f"Đánh giá: {eval_str}. {dn} tốt nhất {self._display_val(best_cost if best_nxt else current.cost_path)} không tốt hơn hiện tại {self._display_val(current.cost_path)}. Dừng."
                self.search_history.append((snapshot, len(self.visited), 0, msg))
                break

            px, py = self.get_location(current.state)
            if trail[px][py] != 3:
                trail[px][py] = 6

            current = best_nxt
            step += 1
            self.visited.add(self.matrix_to_tuple(current.state))
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)

            # Snapshot: (matrix, step_count, current_cost)
            snapshot = [row[:] for row in trail]
            cx, cy = self.get_location(current.state)
            if cx is not None:
                snapshot[cx][cy] = 3
            
            log_msg = f"Bước {step}: {eval_str}. Chọn {best_nxt.act} tới ({cy},{cx}) ({dn}={self._display_val(best_nxt.cost_path)})"
            self.search_history.append((snapshot, len(self.visited), 0, log_msg))

        self.compute_time_ms = self.pure_compute_time * 1000
        return current
