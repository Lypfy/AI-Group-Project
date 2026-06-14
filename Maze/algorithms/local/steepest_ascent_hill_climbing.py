class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path


class SteepestAscentHillClimbing:
    """
    Steepest Ascent Hill Climbing cho bài toán tìm đường trong mê cung.

    search_history: list of tuple
        (matrix_snapshot, step_count, current_cost)
    """

    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze]
        self.start_node = Node(initial_maze, None, "START", self._manhattan(initial_maze))
        self.search_history = []

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    def matrix_to_tuple(self, matrix):
        return tuple(cell for row in matrix for cell in row)

    def get_location(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == 3:
                    return i, j
        return None, None

    def _manhattan(self, matrix):
        x, y = self.get_location(matrix)
        if x is None:
            return float("inf")
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
        return Node(matrix, node, m, self._manhattan(matrix))

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
                    matrix[px][py] = 7
            path.append((matrix, n.act))
        return path

    # ─────────────────────────────────────────────
    # solve
    # ─────────────────────────────────────────────

    def solve(self):
        current = self.start_node
        trail = [row[:] for row in self.initial_maze]   # vết đi tĩnh
        step = 0

        while True:
            if self.is_goal(current):
                break

            moves = self.possible_move(current)
            if not moves:
                break

            best_nxt = None
            best_cost = float('inf')

            for m in moves:
                nxt = self._do_move(current, m)
                if nxt.cost_path < best_cost:
                    best_cost = nxt.cost_path
                    best_nxt = nxt

            # Cho phép plateau hay chỉ cho strict?
            # Thường steepest ascent dừng ở local max: best_cost >= current.cost_path
            if best_nxt is None or best_nxt.cost_path >= current.cost_path:
                break

            px, py = self.get_location(current.state)
            if trail[px][py] != 3:
                trail[px][py] = 7

            current = best_nxt
            step += 1

            # Snapshot: (matrix, step_count, current_cost)
            snapshot = [row[:] for row in trail]
            cx, cy = self.get_location(current.state)
            if cx is not None:
                snapshot[cx][cy] = 3

            self.search_history.append((snapshot, step, current.cost_path))

        return current
