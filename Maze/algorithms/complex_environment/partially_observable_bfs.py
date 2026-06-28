from collections import deque

class Node:
    def __init__(self, belief_state, actual_state, parent, act, depth):
        self.belief_state = frozenset(belief_state)  # Tập các trạng thái (x, y) khả thi
        self.actual_state = actual_state  # Vị trí thực tế của robot (x, y)
        self.parent = parent
        self.act = act
        self.depth = depth

class PartiallyObservableBFS:
    """
    Belief State Search sử dụng thuật toán BFS trong môi trường Partially Observable.
    Tác nhân có cảm biến cục bộ để quan sát tường xung quanh (trên, dưới, trái, phải).
    Sử dụng BFS để tìm đường đi ngắn nhất dắt robot thực tế tới đích và thu hẹp belief state.
    """

    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze]
        self.rows = len(initial_maze)
        self.cols = len(initial_maze[0])
        
        start_x, start_y = None, None
        for i in range(self.rows):
            for j in range(self.cols):
                if self.initial_maze[i][j] == 3:
                    start_x, start_y = i, j
                    break
            if start_x is not None:
                break
        
        if start_x is None:
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.initial_maze[i][j] == 0 and (i, j) != self.goal:
                        start_x, start_y = i, j
                        break
                if start_x is not None:
                    break
        
        self.actual_start = (start_x, start_y) if start_x is not None else (1, 1)
        
        o_0 = self._get_observation(self.actual_start[0], self.actual_start[1])
        
        initial_positions = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.initial_maze[i][j] != 1 and self.initial_maze[i][j] != 9:
                    if self._get_observation(i, j) == o_0:
                        initial_positions.append((i, j))
        
        self.start_node = Node(initial_positions, self.actual_start, None, "START", 0)
        self.search_history = []

    def _get_observation(self, x, y):
        u = (x == 0 or self.initial_maze[x - 1][y] == 1)
        d = (x == self.rows - 1 or self.initial_maze[x + 1][y] == 1)
        l = (y == 0 or self.initial_maze[x][y - 1] == 1)
        r = (y == self.cols - 1 or self.initial_maze[x][y + 1] == 1)
        return (u, d, l, r)

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

    def _transition(self, node, action):
        ax, ay = node.actual_state
        nax, nay = self._do_move_state(ax, ay, action)
        new_actual = (nax, nay)
        
        obs = self._get_observation(nax, nay)
        
        new_belief = set()
        for x, y in node.belief_state:
            nx, ny = self._do_move_state(x, y, action)
            if self._get_observation(nx, ny) == obs:
                new_belief.add((nx, ny))
                
        return Node(new_belief, new_actual, node, action, node.depth + 1)

    def is_goal(self, node):
        return node.actual_state == self.goal and len(node.belief_state) == 1 and self.goal in node.belief_state

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()

        path = []
        for n in nodes:
            path.append(n.actual_state)
        return path

    def solve(self):
        frontier = deque([self.start_node])
        explored = set()
        explored.add((self.start_node.actual_state, self.start_node.belief_state))
        all_explored_positions = set(self.start_node.belief_state)
        
        while frontier:
            if len(explored) > 2500:
                print("Đạt giới hạn Belief State BFS (2500 trạng thái). Dừng lại để tránh treo máy.")
                self.explored_count = len(explored)
                return None
                
            current_node = frontier.popleft()

            tracker = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            for (ex, ey) in all_explored_positions:
                tracker[ex][ey] = 6
                
            for (cx, cy) in current_node.belief_state:
                tracker[cx][cy] = 5
                
            # Đánh dấu vị trí thực tế của robot là đặc biệt (ví dụ giá trị 3 sẽ được vẽ là robot nhưng main.py chưa vẽ, nên cứ để hiển thị tracker)
            ax, ay = current_node.actual_state
            
            log_msg = f"Belief State: <font color='#FF5555'>{len(current_node.belief_state)}</font>. Thực tế: ({ax},{ay}). "
            if current_node.act != "START":
                log_msg += f"Hành động: <font color='#FFFF55'>{current_node.act}</font>."

            if len(self.search_history) < 2000:
                self.search_history.append((tracker, len(explored), len(frontier), log_msg))

            if self.is_goal(current_node):
                log_msg = f"<font color='#00FF00'>Đã đến đích và chắc chắn 100%!</font>"
                final_tracker = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
                for (ex, ey) in all_explored_positions: final_tracker[ex][ey] = 6
                final_tracker[self.goal[0]][self.goal[1]] = 5
                self.search_history.append((final_tracker, len(explored), len(frontier), log_msg))
                self.explored_count = len(explored)
                return current_node

            for action in ["up", "down", "left", "right"]:
                child = self._transition(current_node, action)
                
                state_key = (child.actual_state, child.belief_state)
                if state_key not in explored:
                    explored.add(state_key)
                    frontier.append(child)
                    for pos in child.belief_state:
                        all_explored_positions.add(pos)

        self.explored_count = len(explored)
        return None

