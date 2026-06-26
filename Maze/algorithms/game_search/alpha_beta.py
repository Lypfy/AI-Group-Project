from collections import deque

class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path

class AlphaBeta:
    def __init__(self, initial_maze, goal=(19, 19)):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze]
        self.search_history = []
        self.rows = len(initial_maze)
        self.cols = len(initial_maze[0])
        
        self.robot_start = None
        self.enemy_start = None
        self.walls = set()
        
        for r in range(self.rows):
            for c in range(self.cols):
                if initial_maze[r][c] == 3:
                    self.robot_start = (r, c)
                elif initial_maze[r][c] == 4:
                    self.enemy_start = (r, c)
                elif initial_maze[r][c] == 1:
                    self.walls.add((r, c))
                    
        if self.enemy_start is None:
            # Fallback if no enemy is present
            self.enemy_start = (self.rows - 1, 0)
            
        self.goal_distances = self.get_bfs_distances(self.goal)

    def get_bfs_distances(self, start_pos):
        distances = {start_pos: 0}
        queue = deque([start_pos])
        while queue:
            curr = queue.popleft()
            cx, cy = curr
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and (nx, ny) not in self.walls:
                    if (nx, ny) not in distances:
                        distances[(nx, ny)] = distances[curr] + 1
                        queue.append((nx, ny))
        return distances

    def get_robot_location(self, matrix):
        for i in range(self.rows):
            for j in range(self.cols):
                if matrix[i][j] == 3:
                    return i, j
        return None

    def get_valid_moves(self, pos):
        x, y = pos
        moves = []
        if x > 0 and (x-1, y) not in self.walls: moves.append("up")
        if x < self.rows - 1 and (x+1, y) not in self.walls: moves.append("down")
        if y > 0 and (x, y-1) not in self.walls: moves.append("left")
        if y < self.cols - 1 and (x, y+1) not in self.walls: moves.append("right")
        return moves

    def apply_move(self, pos, move):
        x, y = pos
        if move == "up": return (x - 1, y)
        elif move == "down": return (x + 1, y)
        elif move == "left": return (x, y - 1)
        elif move == "right": return (x, y + 1)
        return pos

    def evaluate_state(self, robot, enemy, goal_distances):
        d_goal = goal_distances.get(robot, 999)
        enemy_distances = self.get_bfs_distances(enemy)
        d_enemy = enemy_distances.get(robot, 999)
        
        # Utility function
        utility = -d_goal * 15
        if d_enemy <= 4:
            utility += (d_enemy - 5) * 50  # Heavy penalty for being close to enemy
        else:
            utility += d_enemy * 2  # Reward for staying far
        return utility

    def create_board_matrix(self, robot, enemy):
        matrix = [row[:] for row in self.initial_maze]
        for r in range(self.rows):
            for c in range(self.cols):
                if matrix[r][c] in [3, 4]:
                    matrix[r][c] = 0
        matrix[robot[0]][robot[1]] = 3
        matrix[enemy[0]][enemy[1]] = 4
        return matrix

    def alpha_beta_search(self, robot_pos, enemy_pos, depth_limit=4, record_history=False):
        evaluations = 0
        prunings = 0
        
        def max_value(robot, enemy, alpha, beta, depth):
            nonlocal evaluations, prunings
            evaluations += 1
            
            if record_history:
                matrix = self.create_board_matrix(robot, enemy)
                self.search_history.append((matrix, evaluations, prunings))
                
            if robot == self.goal:
                return 10000 - depth
            if robot == enemy:
                return -10000 + depth
            if depth >= depth_limit:
                return self.evaluate_state(robot, enemy, self.goal_distances)
                
            v = float('-inf')
            moves = self.get_valid_moves(robot)
            if not moves:
                return -10000 + depth
                
            for m in moves:
                nr = self.apply_move(robot, m)
                v = max(v, min_value(nr, enemy, alpha, beta, depth + 1))
                if v >= beta:
                    prunings += 1
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(robot, enemy, alpha, beta, depth):
            nonlocal evaluations, prunings
            evaluations += 1
            
            if record_history:
                matrix = self.create_board_matrix(robot, enemy)
                self.search_history.append((matrix, evaluations, prunings))
                
            if robot == self.goal:
                return 10000 - depth
            if robot == enemy:
                return -10000 + depth
            if depth >= depth_limit:
                return self.evaluate_state(robot, enemy, self.goal_distances)
                
            v = float('inf')
            moves = self.get_valid_moves(enemy)
            if not moves:
                return 10000 - depth
                
            for m in moves:
                ne = self.apply_move(enemy, m)
                v = min(v, max_value(robot, ne, alpha, beta, depth + 1))
                if v <= alpha:
                    prunings += 1
                    return v
                beta = min(beta, v)
            return v

        best_move = None
        best_val = float('-inf')
        moves = self.get_valid_moves(robot_pos)
        for m in moves:
            nr = self.apply_move(robot_pos, m)
            val = min_value(nr, enemy_pos, best_val, float('inf'), 1)
            if val > best_val:
                best_val = val
                best_move = m
                
        return best_move, evaluations, prunings

    def solve(self):
        curr_robot = self.robot_start
        curr_enemy = self.enemy_start
        
        curr_matrix = [row[:] for row in self.initial_maze]
        root_node = Node(curr_matrix, None, "START", 0)
        curr_node = root_node
        
        max_steps = 150
        step = 0
        is_first_search = True
        
        while step < max_steps:
            # 1. ROBOT'S TURN
            best_move, evals, prunes = self.alpha_beta_search(
                curr_robot, curr_enemy, depth_limit=4, record_history=is_first_search
            )
            is_first_search = False
            
            if not best_move:
                break
                
            new_robot = self.apply_move(curr_robot, best_move)
            matrix_after_robot = self.create_board_matrix(new_robot, curr_enemy)
            robot_node = Node(matrix_after_robot, curr_node, f"Robot: {best_move}", curr_node.cost_path + 1)
            curr_node = robot_node
            
            curr_robot = new_robot
            
            if curr_robot == self.goal:
                return curr_node
            if curr_robot == curr_enemy:
                return curr_node
                
            # 2. ENEMY'S TURN
            enemy_moves = self.get_valid_moves(curr_enemy)
            if not enemy_moves:
                continue
                
            best_enemy_move = None
            min_val = float('inf')
            for m in enemy_moves:
                ne = self.apply_move(curr_enemy, m)
                val = self.evaluate_state(curr_robot, ne, self.goal_distances)
                if val < min_val:
                    min_val = val
                    best_enemy_move = m
                    
            if best_enemy_move:
                new_enemy = self.apply_move(curr_enemy, best_enemy_move)
                matrix_after_enemy = self.create_board_matrix(curr_robot, new_enemy)
                enemy_node = Node(matrix_after_enemy, curr_node, f"Enemy: {best_enemy_move}", curr_node.cost_path + 1)
                curr_node = enemy_node
                
                curr_enemy = new_enemy
                
                if curr_robot == curr_enemy:
                    return curr_node
                    
            step += 1
            
        return curr_node

    def is_goal(self, node):
        if node is None:
            return False
        for r in range(self.rows):
            for c in range(self.cols):
                if node.state[r][c] == 3:
                    return (r, c) == self.goal
        return False

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()
        
        path = []
        for i, n in enumerate(nodes):
            matrix = [row[:] for row in n.state]
            # Mark trail for robot with value 7
            for prev_n in nodes[:i]:
                rx, ry = self.get_robot_location(prev_n.state)
                if rx is not None and matrix[rx][ry] not in [3, 4]:
                    matrix[rx][ry] = 7
            path.append((matrix, n.act))
        return path
