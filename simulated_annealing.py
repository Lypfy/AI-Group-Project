import random
import math

class Node:
    def __init__(self, state, parent, act, cost_path):
        self.state = state
        self.parent = parent
        self.act = act
        self.cost_path = cost_path

class simulatedAnnealing:
    def __init__(self, initial_maze, goal=(19, 19), T0 = 100, Tmin = 0.1, alpha = 0.99):
        self.goal = goal
        self.initial_maze = [row[:] for row in initial_maze] # Lưu map gốc để làm tracker
        self.start_node = Node(initial_maze, None, "START", 0)
        self.search_history = []
        self.T0 = T0
        self.Tmin = Tmin
        self.alpha = alpha

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

        if m == "up": matrix[x][y], matrix[x-1][y] = matrix[x-1][y], matrix[x][y]
        elif m == "down": matrix[x][y], matrix[x+1][y] = matrix[x+1][y], matrix[x][y]
        elif m == "left": matrix[x][y], matrix[x][y-1] = matrix[x][y-1], matrix[x][y]
        elif m == "right": matrix[x][y], matrix[x][y+1] = matrix[x][y+1], matrix[x][y]

        return Node(matrix, node, m, self.mahattan(matrix))
    
    def is_goal(self, node):
        x, y = self.get_location(node.state)
        return (x, y) == self.goal
    
    def mahattan(self, matrix):
        x, y = self.get_location(matrix)
        return abs(x - self.goal[0]) + abs(y - self.goal[1])

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
            for prev_n in nodes[1:i]:
                px, py = self.get_location(prev_n.state)
                if matrix[px][py] != 3: 
                    matrix[px][py] = 7
                    
            path.append((matrix, n.act))
            
        return path

    def solve(self):

        current_node = self.start_node
        T = self.T0
        while T > self.Tmin:
            move = self.possible_move(current_node)
            next_node = self.act(current_node, random.choice(move))

            deltaE = next_node.cost_path - current_node.cost_path

            if deltaE < 0:
                current_node = next_node
            else:
                p = math.exp((-1) * deltaE / T)
                if random.random() < p:
                    current_node = next_node
            T = T * self.alpha
        return current_node