from collections import deque

class Node:
    def __init__(self, belief_state, parent, act, depth):
        self.belief_state = frozenset(belief_state)  # Tập các trạng thái (x, y)
        self.parent = parent
        self.act = act
        self.depth = depth


class BeliefStateDFS:
    """
    Belief State Search sử dụng thuật toán DFS.
    Thuật toán tìm kiếm trong không gian các tập hợp vị trí (Belief States).
    Giải quyết bài toán trong môi trường Sensorless (Không quan sát được).
    """

    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze]
        
        self.actual_start = None
        
        initial_positions = []
        for i in range(len(initial_maze)):
            for j in range(len(initial_maze[0])):
                if initial_maze[i][j] == 3:
                    self.actual_start = (i, j)
                if initial_maze[i][j] != 1 and initial_maze[i][j] != 9:
                    initial_positions.append((i, j))
        
        if self.actual_start is None:
            self.actual_start = (1, 1)

        self.start_node = Node(initial_positions, None, "START", 0)
        self.search_history = []
        self.rows = len(initial_maze)
        self.cols = len(initial_maze[0])

    def _do_move_state(self, x, y, m):
        nx, ny = x, y
        if m == "up" and x > 0 and self.initial_maze[x - 1][y] != 1:
            nx = x - 1
        elif m == "down" and x < self.rows - 1 and self.initial_maze[x + 1][y] != 1:
            nx = x + 1
        elif m == "left" and y > 0 and self.initial_maze[x][y - 1] != 1:
            ny = y - 1
        elif m == "right" and y < self.cols - 1 and self.initial_maze[x][y + 1] != 1:
            ny = y + 1
        return nx, ny

    def _do_move_belief(self, node, m):
        new_belief = set()
        for x, y in node.belief_state:
            new_belief.add(self._do_move_state(x, y, m))
        return Node(new_belief, node, m, node.depth + 1)

    def is_goal(self, node):
        return len(node.belief_state) == 1 and self.goal in node.belief_state

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()

        path = [self.actual_start]
        cx, cy = self.actual_start
        for n in nodes:
            if n.act != "START":
                cx, cy = self._do_move_state(cx, cy, n.act)
                path.append((cx, cy))
        return path

    def solve(self):
        import time
        self.pure_compute_time = 0.0
        
        t_start = time.perf_counter()
        frontier = deque([self.start_node])
        explored = set()
        explored.add(self.start_node.belief_state)
        
        all_explored_positions = set(self.start_node.belief_state)
        t_end = time.perf_counter()
        self.pure_compute_time += (t_end - t_start)
        
        while frontier:
            t_start = time.perf_counter()
            if len(explored) > 2500:
                self.explored_count = len(explored)
                self.pure_compute_time += (time.perf_counter() - t_start)
                print("Đạt giới hạn Belief State DFS (2500 trạng thái). Dừng lại để tránh treo máy.")
                self.compute_time_ms = self.pure_compute_time * 1000
                return None
                
            current_node = frontier.pop()
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            # Tracker matrix for rendering
            tracker = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            for (ex, ey) in all_explored_positions:
                tracker[ex][ey] = 6
                
            for (cx, cy) in current_node.belief_state:
                tracker[cx][cy] = 5
                
            log_msg = f"Xét Belief State (size: <font color='#FF5555'>{len(current_node.belief_state)}</font>). "
            if current_node.act != "START":
                log_msg += f"Hành động: <font color='#FFFF55'>{current_node.act}</font>."

            if len(self.search_history) < 2000:
                self.search_history.append((tracker, len(explored), len(frontier), log_msg))

            t_start = time.perf_counter()
            is_goal = self.is_goal(current_node)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)

            if is_goal:
                log_msg = f"<font color='#00FF00'>Đã tìm thấy kế hoạch chắc chắn (100% đến đích).</font>"
                final_tracker = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
                for (ex, ey) in all_explored_positions: final_tracker[ex][ey] = 6
                final_tracker[self.goal[0]][self.goal[1]] = 5
                self.search_history.append((final_tracker, len(explored), len(frontier), log_msg))
                self.explored_count = len(explored)
                self.compute_time_ms = self.pure_compute_time * 1000
                return current_node

            t_start = time.perf_counter()
            for m in ["up", "down", "left", "right"]:
                child = self._do_move_belief(current_node, m)
                if child.belief_state not in explored:
                    explored.add(child.belief_state)
                    frontier.append(child)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)

        self.explored_count = len(explored)
        self.compute_time_ms = self.pure_compute_time * 1000
        return None
