import random
import math


class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path


from levels.maze_data import RESONANCE_MAP

class SimulatedAnnealing:
    """
    Simulated Annealing cho bài toán tìm đường trong mê cung.

    search_history: list of tuple
        (matrix_snapshot, T, deltaE, prob, accepted)
        - matrix_snapshot : ma trận trạng thái tại bước đó
        - T               : nhiệt độ hiện tại
        - deltaE          : chênh lệch heuristic (next - current)
        - prob            : xác suất chấp nhận trạng thái tệ hơn
        - accepted        : True nếu bước được chấp nhận
    """

    def __init__(self, initial_maze, goal=(19, 19), T0=100.0, Tmin=0.1, alpha=0.99, res_map=None):
        self.goal = goal
        self.res_map = res_map
        self.is_resonance_level = (res_map is not None)
        self.initial_maze = [row[:] for row in initial_maze]
        self.T0 = 1000.0
        self.Tmin = 0.01
        self.alpha = 0.99
        self.start_node = Node(initial_maze, None, "START", self._cost(initial_maze))
        self.search_history = []
        self.visited = set()
        self.visited.add(self.matrix_to_tuple(initial_maze))
        self.T0 = T0
        self.Tmin = Tmin
        self.alpha = alpha

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
        current = self.start_node
        T = self.T0
        trail = [row[:] for row in self.initial_maze]   # vết đi tĩnh

        # Lưu trạng thái ban đầu
        snapshot = [row[:] for row in trail]
        cx, cy = self.get_location(current.state)
        if cx is not None:
            snapshot[cx][cy] = 3
        self.search_history.append((snapshot, len(self.visited), 0, f"Start: {self._display_name()}={self._display_val(current.cost_path)}, T={T:.2f}"))

        while T > self.Tmin:
            if self.is_goal(current):
                break

            moves = self.possible_move(current)
            if not moves:
                break

            m = random.choice(moves)
            nxt = self._do_move(current, m)

            deltaE = nxt.cost_path - current.cost_path

            if deltaE < 0:
                accepted = True
                prob = 1.0
            else:
                prob = math.exp(-deltaE / T)
                accepted = random.random() < prob

            if accepted:
                px, py = self.get_location(current.state)
                if trail[px][py] != 3:
                    trail[px][py] = 6
                current = nxt

            # Snapshot: (matrix, T, deltaE, prob, accepted)
            snapshot = [row[:] for row in trail]
            cx, cy = self.get_location(current.state)
            if cx is not None:
                snapshot[cx][cy] = 3

            self.visited.add(self.matrix_to_tuple(current.state))
            
            log_msg = f"T={T:.4f}, {self._display_name()}={self._display_val(current.cost_path)}, P={prob:.4f}, Accept={accepted}"
            self.search_history.append((
                snapshot,
                len(self.visited),
                0,
                log_msg
            ))

            T *= self.alpha

        return current
