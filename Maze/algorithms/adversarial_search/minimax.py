class Node:
    def __init__(self, state, parent, act, depth):
        self.state = state
        self.parent = parent
        self.act = act
        self.depth = depth

class Minimax:
    def __init__(self, initial_maze, goal=(19, 19), max_depth=3):
        self.initial_maze = [row[:] for row in initial_maze]
        self.goal = goal
        self.max_depth = max_depth
        self.search_history = []
        self.explored_count = 0

    def translate_dir(self, move):
        dirs = {"up": "Lên", "down": "Xuống", "left": "Trái", "right": "Phải"}
        return dirs.get(move, move)

    def get_location(self, matrix, entity_type=3):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == entity_type:
                    return i, j
        return None

    def manhattan(self, pos1, pos2):
        if not pos1 or not pos2:
            return 9999
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def evaluate(self, matrix):
        max_pos = self.get_location(matrix, 3)
        min_pos = self.get_location(matrix, 4) # Assume 4 is MIN (enemy)
        
        if not max_pos:
            return -10000
        if max_pos == self.goal:
            return 10000
            
        score = -self.manhattan(max_pos, self.goal)
        if min_pos:
            dist = self.manhattan(max_pos, min_pos)
            if dist == 0:
                return -10000
            score += dist * 0.5
        return score

    def possible_moves(self, matrix, entity_type):
        pos = self.get_location(matrix, entity_type)
        if not pos:
            return []
        x, y = pos
        moves = []
        if x > 0 and matrix[x-1][y] not in [1]: moves.append("up")
        if x < len(matrix) - 1 and matrix[x+1][y] not in [1]: moves.append("down")
        if y > 0 and matrix[x][y-1] not in [1]: moves.append("left")
        if y < len(matrix[0]) - 1 and matrix[x][y+1] not in [1]: moves.append("right")
        return moves

    def apply_move(self, matrix, move, entity_type):
        new_matrix = [row[:] for row in matrix]
        pos = self.get_location(new_matrix, entity_type)
        if not pos:
            return new_matrix
        x, y = pos
        
        new_x, new_y = x, y
        if move == "up": new_x = x - 1
        elif move == "down": new_x = x + 1
        elif move == "left": new_y = y - 1
        elif move == "right": new_y = y + 1

        target_val = new_matrix[new_x][new_y]
        
        if entity_type == 3:
            if target_val == 4:
                new_matrix[x][y] = 0
            else:
                new_matrix[x][y] = 0
                new_matrix[new_x][new_y] = 3
        elif entity_type == 4:
            if target_val == 3:
                new_matrix[x][y] = 0
                new_matrix[new_x][new_y] = 4
            else:
                new_matrix[x][y] = 0
                new_matrix[new_x][new_y] = 4
        return new_matrix

    def minimax(self, depth, is_max, matrix):
        self.explored_count += 1
        
        max_pos = self.get_location(matrix, 3)
        min_pos = self.get_location(matrix, 4)
        
        if depth == 0 or not max_pos or max_pos == self.goal or (min_pos and max_pos == min_pos):
            score = self.evaluate(matrix)
            if score >= 10000:
                score += depth * 10
            return score, None

        if is_max:
            best_val = -float('inf')
            best_move = None
            moves = self.possible_moves(matrix, 3)
            if not moves:
                return self.evaluate(matrix), None
                
            for move in moves:
                new_state = self.apply_move(matrix, move, 3)
                next_is_max = False if self.get_location(new_state, 4) else True
                val, _ = self.minimax(depth - 1, next_is_max, new_state)
                if val > best_val:
                    best_val = val
                    best_move = move
            return best_val, best_move
        else:
            best_val = float('inf')
            best_move = None
            moves = self.possible_moves(matrix, 4)
            if not moves:
                return self.evaluate(matrix), None
                
            for move in moves:
                new_state = self.apply_move(matrix, move, 4)
                val, _ = self.minimax(depth - 1, True, new_state)
                if val < best_val:
                    best_val = val
                    best_move = move
            return best_val, best_move

    def is_goal(self, node):
        max_pos = self.get_location(node.state, 3)
        return max_pos == self.goal

    def get_path(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()
        
        path = []
        for i, n in enumerate(nodes):
            matrix = [row[:] for row in n.state]
            for prev_n in nodes[:i]:
                px, py = self.get_location(prev_n.state, 3)
                if px is not None and matrix[px][py] != 3:
                    matrix[px][py] = 7
            path.append((matrix, n.act))
        return path

    def solve(self):
        import time
        self.pure_compute_time = 0.0
        
        t_start = time.perf_counter()
        tracker = [row[:] for row in self.initial_maze]
        current_node = Node(tracker, None, "START", 0)
        t_end = time.perf_counter()
        self.pure_compute_time += (t_end - t_start)
        
        self.search_history.append(([row[:] for row in tracker], self.explored_count, 0, "<font color='#00FFFF'>[Minimax]</font> Bắt đầu mô phỏng chiến thuật..."))

        # Limit to 100 steps to avoid infinite loops if it gets stuck
        for step in range(100):
            t_start = time.perf_counter()
            is_goal = self.is_goal(current_node)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if is_goal:
                self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, "<font color='#FFFF00'>[Thành công]</font> Đã trốn thoát an toàn!"))
                self.compute_time_ms = self.pure_compute_time * 1000
                return current_node
                
            t_start = time.perf_counter()
            max_pos = self.get_location(current_node.state, 3)
            min_pos = self.get_location(current_node.state, 4)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if not max_pos or (min_pos and max_pos == min_pos):
                self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, "<font color='#FF0000'>[Thất bại]</font> Người chơi đã bị quái vật bắt!"))
                break

            # MAX turn
            t_start = time.perf_counter()
            val, best_move = self.minimax(self.max_depth, True, current_node.state)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if not best_move:
                self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, "<font color='#FF0000'>[Thất bại]</font> Người chơi bị kẹt đường!"))
                break
                
            t_start = time.perf_counter()
            current_max_pos = self.get_location(current_node.state, 3)
            new_state = self.apply_move(current_node.state, best_move, 3)
            new_max_pos = self.get_location(new_state, 3)
            current_node = Node(new_state, current_node, best_move, current_node.depth + 1)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            dir_vn = self.translate_dir(best_move)
            if val >= 10000:
                log_msg = f"<font color='#00FF00'>[Player]</font> Đi <b>{dir_vn}</b> (Tìm thấy đích! Điểm: {round(val, 1)})"
            else:
                if new_max_pos:
                    t_start = time.perf_counter()
                    old_dist = self.manhattan(current_max_pos, self.goal)
                    new_dist = self.manhattan(new_max_pos, self.goal)
                    t_end = time.perf_counter()
                    self.pure_compute_time += (t_end - t_start)
                    if new_dist < old_dist:
                        bonus = "<font color='#00FF00'>+1 Tới gần đích</font>"
                    else:
                        bonus = "<font color='#FF0000'>-1 Xa đích</font>"
                else:
                    bonus = ""
                log_msg = f"<font color='#00FF00'>[Player]</font> Đi <b>{dir_vn}</b> ({bonus} | Điểm: {round(val, 1)})"
                
            self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, log_msg))
            
            t_start = time.perf_counter()
            is_goal = self.is_goal(current_node)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if is_goal:
                self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, "<font color='#FFFF00'>[Thành công]</font> Đã trốn thoát an toàn!"))
                self.compute_time_ms = self.pure_compute_time * 1000
                return current_node

            # MIN turn (if MIN exists)
            t_start = time.perf_counter()
            current_min_pos = self.get_location(current_node.state, 4)
            t_end = time.perf_counter()
            self.pure_compute_time += (t_end - t_start)
            
            if current_min_pos:
                t_start = time.perf_counter()
                val, best_min_move = self.minimax(self.max_depth, False, current_node.state)
                t_end = time.perf_counter()
                self.pure_compute_time += (t_end - t_start)
                
                if best_min_move:
                    t_start = time.perf_counter()
                    current_max_pos = self.get_location(current_node.state, 3)
                    new_state = self.apply_move(current_node.state, best_min_move, 4)
                    new_min_pos = self.get_location(new_state, 4)
                    current_node = Node(new_state, current_node, best_min_move, current_node.depth + 1)
                    t_end = time.perf_counter()
                    self.pure_compute_time += (t_end - t_start)
                    
                    dir_min_vn = self.translate_dir(best_min_move)
                    
                    if current_max_pos and new_min_pos:
                        t_start = time.perf_counter()
                        old_dist_min = self.manhattan(current_max_pos, current_min_pos)
                        new_dist_min = self.manhattan(current_max_pos, new_min_pos)
                        t_end = time.perf_counter()
                        self.pure_compute_time += (t_end - t_start)
                        if new_dist_min < old_dist_min:
                            penalty = "<font color='#FF0000'>-0.5 Áp sát</font>"
                        else:
                            penalty = "<font color='#00FF00'>+0.5 Lùi xa</font>"
                    else:
                        penalty = "<font color='#FF0000'>Đã ăn thịt</font>"
                        
                    self.search_history.append(([row[:] for row in current_node.state], self.explored_count, 0, f"<font color='#FF4444'>[Monster]</font> Đuổi theo <b>{dir_min_vn}</b> ({penalty} | Điểm: {round(val, 1)})"))
                    
        t_start = time.perf_counter()
        is_goal = self.is_goal(current_node)
        t_end = time.perf_counter()
        self.pure_compute_time += (t_end - t_start)
        
        self.compute_time_ms = self.pure_compute_time * 1000
        if is_goal:
            return current_node
        return None
