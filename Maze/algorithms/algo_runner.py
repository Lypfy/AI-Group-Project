import time
from algorithms.uninformed.bfs import BFS
from algorithms.uninformed.dfs import DFS
from algorithms.informed.gbfs import GBFS
from algorithms.informed.aStar import AStar
from algorithms.local.simulated_annealing import SimulatedAnnealing
from algorithms.local.steepest_ascent_hill_climbing import SteepestAscentHillClimbing
from algorithms.constraint_reasoning.forward_checking import ForwardChecking
from algorithms.constraint_reasoning.min_conflicts import MinConflicts
from levels.maze_data import RESONANCE_MAP, RESONANCE_MAP_5

def run_algorithm(algo_name, maze, start_node, goal_node, current_level_idx):
    maze_copy = [row[:] for row in maze]
    
    # Ensure player start pos is 3 in maze_copy (only for pathfinding algos)
    if algo_name not in ["Forward Checking", "Min-Conflicts"]:
        for r in range(len(maze_copy)):
            for c in range(len(maze_copy[0])):
                if maze_copy[r][c] == 3:
                    maze_copy[r][c] = 0
        maze_copy[start_node[1]][start_node[0]] = 3
    
    goal_rc = (goal_node[1], goal_node[0]) if goal_node else None
    
    if algo_name == "BFS":
        algo = BFS(maze_copy, goal_rc)
    elif algo_name == "DFS":
        algo = DFS(maze_copy, goal_rc)
    elif algo_name == "GBFS":
        algo = GBFS(maze_copy, goal_rc)
    elif algo_name == "A*":
        algo = AStar(maze_copy, goal_rc)
    elif algo_name == "Hill Climbing":
        res = RESONANCE_MAP if current_level_idx == 3 else (RESONANCE_MAP_5 if current_level_idx == 4 else None)
        algo = SteepestAscentHillClimbing(maze_copy, goal_rc, res_map=res)
    elif algo_name == "Simulated Annealing":
        res = RESONANCE_MAP if current_level_idx == 3 else (RESONANCE_MAP_5 if current_level_idx == 4 else None)
        algo = SimulatedAnnealing(maze_copy, goal_rc, res_map=res)
    elif algo_name == "Forward Checking":
        algo = ForwardChecking(maze_copy)
    elif algo_name == "Min-Conflicts":
        algo = MinConflicts(maze_copy)
    elif algo_name == "Belief State DFS":
        from algorithms.complex_environment.belief_state_dfs import BeliefStateDFS
        algo = BeliefStateDFS(maze_copy, goal_rc)
    elif algo_name == "Partially Observable BFS":
        from algorithms.complex_environment.partially_observable_bfs import PartiallyObservableBFS
        algo = PartiallyObservableBFS(maze_copy, goal_rc)
    elif algo_name == "Minimax":
        from algorithms.adversarial_search.minimax import Minimax
        algo = Minimax(maze_copy, goal_rc)
    elif algo_name == "Alpha-Beta":
        from algorithms.adversarial_search.alpha_beta import AlphaBeta
        algo = AlphaBeta(maze_copy, goal_rc)
    else:
        algo = None

    if algo:
        start_time = time.time()
        goal_result = algo.solve()
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        
        return _make_generator(algo, goal_result, algo_name, elapsed_time_ms)
    
    return None

def _make_generator(algo_obj, result, algo_name, elapsed_ms):
    yield ("LOG", f"Bắt đầu {algo_name}...")
    if algo_name == "Simulated Annealing":
        yield ("LOG", f"Thông số ban đầu: T0={algo_obj.T0}, Tmin={algo_obj.Tmin}, alpha={algo_obj.alpha}")
    for history_item in algo_obj.search_history:
        yield ("STATE", history_item)
        
    if result:
        if hasattr(algo_obj, 'is_goal') and getattr(algo_obj, 'is_goal')(result) == False:
            yield ("LOG", "Đã đạt cực đại cục bộ!")
        else:
            yield ("LOG", "Đã tìm thấy đích!")
        path_states = algo_obj.get_path(result)
        xy_path = []
        if algo_name in ["Belief State DFS", "Partially Observable BFS"]:
            for r, c in path_states:
                xy_path.append((c, r))
        else:
            for st_matrix, act in path_states:
                r, c = algo_obj.get_location(st_matrix)
                if r is not None and c is not None:
                    xy_path.append((c, r))
        yield ("PATH", xy_path)
        
        if algo_name == "Forward Checking":
            yield ("LOG", f"<font color='#00FFFF'>Số phép gán: {algo_obj.assignments_count}</font>")
            yield ("LOG", f"<font color='#00FFFF'>Số lần quay lui: {algo_obj.backtracks_count}</font>")
            yield ("LOG", f"<font color='#00FFFF'>Thời gian chạy: {elapsed_ms:.2f} ms</font>")
        elif algo_name == "Min-Conflicts":
            yield ("LOG", f"<font color='#00FFFF'>Số bước lặp: {algo_obj.steps_count}</font>")
            yield ("LOG", f"<font color='#00FFFF'>Thời gian chạy: {elapsed_ms:.2f} ms</font>")
        else:
            explored_count = 0
            if hasattr(algo_obj, 'reached'):
                explored_count = len(algo_obj.reached)
            elif hasattr(algo_obj, 'visited'):
                explored_count = len(algo_obj.visited)
            elif hasattr(algo_obj, 'explored_count'):
                explored_count = algo_obj.explored_count
                
            path_length = len(xy_path) - 1 if xy_path else 0
            
            yield ("LOG", f"<font color='#00FFFF'>Số Node đã duyệt: {explored_count}</font>")
            yield ("LOG", f"<font color='#00FFFF'>Độ dài đường đi: {path_length}</font>")
            yield ("LOG", f"<font color='#00FFFF'>Thời gian chạy: {elapsed_ms:.2f} ms</font>")
    else:
        yield ("LOG", "Không tìm thấy kết quả!")
    yield ("DONE", None)
