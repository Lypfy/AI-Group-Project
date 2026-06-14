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
    Giải quyết bài toán trong môi trường Unobservable (Không quan sát được).
    """

    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze]
        
        # Môi trường Sensorless: Tác nhân không biết mình bắt đầu ở đâu.
        # Khởi tạo Belief State B0 chứa TẤT CẢ các vị trí không phải là tường.
        initial_positions = []
        for i in range(len(initial_maze)):
            for j in range(len(initial_maze[0])):
                # Chấp nhận tất cả ô trống và cả ô start (3) nếu có
                if initial_maze[i][j] != 1 and initial_maze[i][j] != 9:
                    initial_positions.append((i, j))
        
        self.start_node = Node(initial_positions, None, "START", 0)
        self.search_history = []

    def _do_move_state(self, x, y, m):
        # Tính toán kết quả cho TỪNG vị trí cụ thể
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

    def _do_move_belief(self, node, m):
        # Cập nhật Belief State: Result(B, a) = {Result(s, a) | s thuộc B}
        new_belief = set()
        for x, y in node.belief_state:
            new_belief.add(self._do_move_state(x, y, m))
        return Node(new_belief, node, m, node.depth + 1)

    def is_goal(self, node):
        # Đạt được đích khi toàn bộ Belief State hội tụ về DUY NHẤT 1 ô đích (Goal).
        # Kế hoạch tuân thủ (Conformant Plan) yêu cầu sự chắc chắn 100%.
        return len(node.belief_state) == 1 and self.goal in node.belief_state

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()

        path = []
        for n in nodes:
            # Tạo snapshot ma trận để vẽ Belief State tại bước di chuyển đó
            matrix = [row[:] for row in self.initial_maze]
            
            # Xóa vị trí robot ban đầu đi (nếu có vẽ sẵn trên map)
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if matrix[i][j] == 3:
                        matrix[i][j] = 0
                        
            # Cập nhật lại các robot ảo đại diện cho các khả năng
            is_certain = (len(n.belief_state) == 1)
            robot_val = 3 if is_certain else 10
            
            for x, y in n.belief_state:
                if (x, y) != self.goal:
                    matrix[x][y] = robot_val
            
            # Ưu tiên vẽ goal nếu robot tụ về goal
            gx, gy = self.goal
            if (gx, gy) in n.belief_state:
                matrix[gx][gy] = robot_val  # Đè lên Goal
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
        explored.add(self.start_node.belief_state)
        
        while frontier:
            # Ngăn chặn treo UI (Crash/Freeze) nếu map quá lớn hoặc không có Conformant Plan
            if len(explored) > 2500:
                print("Đạt giới hạn Belief State DFS (2500 trạng thái). Dừng lại để tránh treo máy.")
                return None
                
            # ĐIỂM KHÁC BIỆT CHÍNH: Dùng LIFO (Stack) cho DFS thay vì FIFO (Queue) cho BFS
            current_node = frontier.pop()

            # Bỏ qua lưu search_history trong lúc duyệt DFS để tránh giao diện giật nháy hỗn loạn
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

            # Kiểm tra trạng thái Goal
            if self.is_goal(current_node):
                # Lưu thêm snapshot cuối
                snapshot = [row[:] for row in self.initial_maze]
                gx, gy = self.goal
                snapshot[gx][gy] = 3
                self.search_history.append((snapshot, len(explored), len(frontier), 1, "Goal", set()))
                return current_node

            # Explore 4 hành động (để DFS duyệt ƯU TIÊN giống logic cũ, có thể đảo ngược thứ tự insert, nhưng cứ giữ nguyên là được)
            for action in ["up", "down", "left", "right"]:
                child = self._do_move_belief(current_node, action)
                
                if child.belief_state not in explored:
                    explored.add(child.belief_state)
                    frontier.append(child)

        return None
