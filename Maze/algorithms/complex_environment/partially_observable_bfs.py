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
        
        # Tìm vị trí bắt đầu thực tế (ưu tiên ô có giá trị 3)
        start_x, start_y = None, None
        for i in range(len(self.initial_maze)):
            for j in range(len(self.initial_maze[0])):
                if self.initial_maze[i][j] == 3:
                    start_x, start_y = i, j
                    break
            if start_x is not None:
                break
        
        # Nếu không có ô 3 (như Màn 7), chọn ô trống đầu tiên không phải tường/đích
        if start_x is None:
            for i in range(len(self.initial_maze)):
                for j in range(len(self.initial_maze[0])):
                    if self.initial_maze[i][j] == 0 and (i, j) != self.goal:
                        start_x, start_y = i, j
                        break
                if start_x is not None:
                    break
        
        self.actual_start = (start_x, start_y) if start_x is not None else (1, 1)
        
        # Lấy quan sát ban đầu tại vị trí bắt đầu thực tế
        o_0 = self._get_observation(self.actual_start[0], self.actual_start[1])
        
        # Khởi tạo Belief State B0 chứa tất cả các vị trí trống có cùng cấu hình quan sát o_0
        initial_positions = []
        for i in range(len(self.initial_maze)):
            for j in range(len(self.initial_maze[0])):
                if self.initial_maze[i][j] != 1:  # Không phải tường
                    if self._get_observation(i, j) == o_0:
                        initial_positions.append((i, j))
        
        self.start_node = Node(initial_positions, self.actual_start, None, "START", 0)
        self.search_history = []

    def _get_observation(self, x, y):
        # Cảm biến trả về tuple 4 phần tử tương ứng với: (up_wall, down_wall, left_wall, right_wall)
        u = (x == 0 or self.initial_maze[x - 1][y] == 1)
        d = (x == len(self.initial_maze) - 1 or self.initial_maze[x + 1][y] == 1)
        l = (y == 0 or self.initial_maze[x][y - 1] == 1)
        r = (y == len(self.initial_maze[0]) - 1 or self.initial_maze[x][y + 1] == 1)
        return (u, d, l, r)

    def _do_move_state(self, x, y, m):
        nx, ny = x, y
        if m == "up" and x > 0 and self.initial_maze[x - 1][y] != 1:
            nx = x - 1
        elif m == "down" and x < len(self.initial_maze) - 1 and self.initial_maze[x + 1][y] != 1:
            nx = x + 1
        elif m == "left" and y > 0 and self.initial_maze[x][y - 1] != 1:
            ny = y - 1
        elif m == "right" and y < len(self.initial_maze[0]) - 1 and self.initial_maze[x][y + 1] != 1:
            ny = y + 1
        return nx, ny

    def _transition(self, node, action):
        # 1. Tính toán thực tế di chuyển
        ax, ay = node.actual_state
        nax, nay = self._do_move_state(ax, ay, action)
        new_actual = (nax, nay)
        
        # 2. Nhận quan sát cảm biến thực tế tại vị trí mới
        obs = self._get_observation(nax, nay)
        
        # 3. Dự đoán và cập nhật Belief State mới
        new_belief = set()
        for x, y in node.belief_state:
            nx, ny = self._do_move_state(x, y, action)
            # Chỉ giữ lại các robot ảo có quan sát trùng khớp
            if self._get_observation(nx, ny) == obs:
                new_belief.add((nx, ny))
                
        return Node(new_belief, new_actual, node, action, node.depth + 1)

    def is_goal(self, node):
        # Robot thực tế đến goal và tin tưởng tuyệt đối mình ở goal
        return node.actual_state == self.goal and len(node.belief_state) == 1 and self.goal in node.belief_state

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()

        path = []
        for n in nodes:
            matrix = [row[:] for row in self.initial_maze]
            
            # Xóa robot 3 ban đầu
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if matrix[i][j] == 3:
                        matrix[i][j] = 0
                        
            is_certain = (len(n.belief_state) == 1)
            robot_val = 3 if is_certain else 10
            
            for x, y in n.belief_state:
                if (x, y) != self.goal:
                    matrix[x][y] = robot_val
            
            gx, gy = self.goal
            if (gx, gy) in n.belief_state:
                matrix[gx][gy] = robot_val
            else:
                matrix[gx][gy] = 9
                
            merge_cells = set()
            if n.parent and n.act != "START":
                counts = {}
                for px, py in n.parent.belief_state:
                    nx, ny = self._do_move_state(px, py, n.act)
                    counts[(nx, ny)] = counts.get((nx, ny), 0) + 1
                for k, v in counts.items():
                    if v > 1:
                        merge_cells.add(k)
                        
            path.append((matrix, n.act, merge_cells))
        return path

    def solve(self):
        frontier = deque([self.start_node])
        explored = set()
        explored.add((self.start_node.actual_state, self.start_node.belief_state))
        
        while frontier:
            if len(explored) > 2500:
                print("Đạt giới hạn Belief State BFS (2500 trạng thái). Dừng lại để tránh treo máy.")
                return None
                
            current_node = frontier.popleft()

            if len(self.search_history) < 2000:
                snapshot = [row[:] for row in self.initial_maze]
                for i in range(len(snapshot)):
                    for j in range(len(snapshot[0])):
                        if snapshot[i][j] == 3:
                            snapshot[i][j] = 0
                
                is_certain = (len(current_node.belief_state) == 1)
                robot_val = 3 if is_certain else 10
                
                for x, y in current_node.belief_state:
                    snapshot[x][y] = robot_val
                        
                merge_cells = set()
                if current_node.parent and current_node.act != "START":
                    counts = {}
                    for px, py in current_node.parent.belief_state:
                        nx, ny = self._do_move_state(px, py, current_node.act)
                        counts[(nx, ny)] = counts.get((nx, ny), 0) + 1
                    for k, v in counts.items():
                        if v > 1:
                            merge_cells.add(k)
                            
                self.search_history.append((snapshot, len(explored), len(frontier), len(current_node.belief_state), current_node.act, merge_cells))

            if self.is_goal(current_node):
                snapshot = [row[:] for row in self.initial_maze]
                gx, gy = self.goal
                snapshot[gx][gy] = 3
                self.search_history.append((snapshot, len(explored), len(frontier), 1, "Goal", set()))
                return current_node

            for action in ["up", "down", "left", "right"]:
                child = self._transition(current_node, action)
                
                state_key = (child.actual_state, child.belief_state)
                if state_key not in explored:
                    explored.add(state_key)
                    frontier.append(child)

        return None
