from collections import deque

class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path

class BFS:
    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze] # Lưu map gốc để làm tracker
        start_node = Node(initial_maze, None, "START", 0)
        self.frontier = deque([start_node])
        self.reached = {self.matrix_to_tuple(initial_maze)}
        self.search_history = []

    def matrix_to_tuple(self, matrix):
        return tuple(cell for row in matrix for cell in row)
    
    def get_location(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == 3:
                    return i, j
        return None, None
    
    def possible_move(self, node):
        matrix = node.state
        x, y = self.get_location(matrix)
        move = []

        if x > 0 and matrix[x-1][y] != 1: move.append("up")
        if x < len(matrix) - 1 and matrix[x+1][y] != 1: move.append("down")
        if y > 0 and matrix[x][y-1] != 1: move.append("left")
        if y < len(matrix[0]) - 1 and matrix[x][y+1] != 1: move.append("right")
        return move
    
    def act(self, node, m):
        matrix = [row[:] for row in node.state]
        x, y = self.get_location(node.state)

        target_val = 1
        if m == "up": target_val = matrix[x-1][y]
        elif m == "down": target_val = matrix[x+1][y]
        elif m == "left": target_val = matrix[x][y-1]
        elif m == "right": target_val = matrix[x][y+1]

        move_cost = 5 if target_val == 8 else 1

        if m == "up": matrix[x][y], matrix[x-1][y] = matrix[x-1][y], matrix[x][y]
        elif m == "down": matrix[x][y], matrix[x+1][y] = matrix[x+1][y], matrix[x][y]
        elif m == "left": matrix[x][y], matrix[x][y-1] = matrix[x][y-1], matrix[x][y]
        elif m == "right": matrix[x][y], matrix[x][y+1] = matrix[x][y+1], matrix[x][y]

        return Node(matrix, node, m, node.cost_path + move_cost)
    
    def is_goal(self, node):
        x, y = self.get_location(node.state)
        return (x, y) == self.goal
    
    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse() # Sắp xếp lại từ Start -> Goal
        
        path = []
        for i, n in enumerate(nodes):
            matrix = [row[:] for row in n.state]
            
            # Rải chấm vàng (7) đằng sau lưng robot cho những bước đã đi qua
            for prev_n in nodes[:i]:
                px, py = self.get_location(prev_n.state)
                if matrix[px][py] != 3: 
                    matrix[px][py] = 7
                    
            path.append((matrix, n.act))
            
        return path

    def solve(self):
        # Tracker lưu trữ tĩnh việc bung màu Frontier(5) và Visited(6)
        tracker = [row[:] for row in self.initial_maze]
        
        while len(self.frontier):
            node = self.frontier.popleft()
            
            # Đánh dấu ô đang xét là Visited (6)
            cx, cy = self.get_location(node.state)
            if tracker[cx][cy] != 3: # Không đè lên vị trí robot xuất phát
                tracker[cx][cy] = 6
                
            log_msg = f"Đang xét node ({cx}, {cy}) (cost={node.cost_path}). "
            added_nodes = []

            if self.is_goal(node):
                log_msg += "Là node đích!"
                self.search_history.append(([row[:] for row in tracker], len(self.reached), len(self.frontier), log_msg))
                return node

            move = self.possible_move(node)
            for m in move:
                new_node = self.act(node, m)
                state_tuple = self.matrix_to_tuple(new_node.state)
                
                if state_tuple not in self.reached:
                    self.frontier.append(new_node)
                    self.reached.add(state_tuple)
                    
                    # Đánh dấu ô mới đưa vào hàng đợi là Frontier (5)
                    nx, ny = self.get_location(new_node.state)
                    added_nodes.append(f"({nx}, {ny})")
                    if tracker[nx][ny] != 3:
                        tracker[nx][ny] = 5
                        
            if added_nodes:
                log_msg += f"Thêm vào frontier: {', '.join(added_nodes)}. "
            else:
                log_msg += "Không có node mới thêm vào. "
                
            frontier_nodes = []
            for f_node in self.frontier:
                fx, fy = self.get_location(f_node.state)
                frontier_nodes.append(f"({fx}, {fy})")
            log_msg += f"Frontier hiện tại: [{', '.join(frontier_nodes)}]"

            # Snapshot tracker tĩnh (robot không nhảy)
            self.search_history.append(([row[:] for row in tracker], len(self.reached), len(self.frontier), log_msg))

        return None
