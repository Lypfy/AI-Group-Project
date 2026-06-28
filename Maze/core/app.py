import pygame
import pygame_gui
import sys

from core.settings import WINDOW_SIZE, FPS, TILESET_PATH, CHAR_PATH, SCALED_TILE_SIZE
from core.utils import load_image, get_tile
from levels.maze_data import MAZE_MAP, MAZE_MAP_2, MAZE_MAP_3, MAZE_MAP_4, MAZE_MAP_5, MAZE_MAP_6, MAZE_MAP_7, MAZE_MAP_8, MAZE_MAP_9, MAZE_MAP_10, RESONANCE_MAP, RESONANCE_MAP_5
from ui.game_ui import GameUI
from levels.level_loader import load_level
from algorithms.algo_runner import run_algorithm

class GameApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("2D Pixel Dungeon Demo")
        self.window_surface = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE | pygame.SCALED)
        
        self.manager = pygame_gui.UIManager(WINDOW_SIZE, 'ui/theme.json')
        self.pixel_font = pygame.font.SysFont('couriernew', 16, bold=True)
        
        # Load assets
        try:
            self.tileset_sheet = load_image(TILESET_PATH)
            self.char_sheet = load_image(CHAR_PATH)
        except Exception as e:
            print(f"Failed to load assets: {e}")
            pygame.quit()
            sys.exit()
            
        bg_tile = get_tile(self.tileset_sheet, 2, 6)
        dark_surface = pygame.Surface((SCALED_TILE_SIZE, SCALED_TILE_SIZE), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 150))
        bg_tile.blit(dark_surface, (0, 0))
        
        self.background = pygame.Surface(WINDOW_SIZE)
        for y in range(0, WINDOW_SIZE[1], SCALED_TILE_SIZE):
            for x in range(0, WINDOW_SIZE[0], SCALED_TILE_SIZE):
                self.background.blit(bg_tile, (x, y))
                
        pygame.display.set_caption("AI Search Algorithms Demonstration")
        
        self.levels = [MAZE_MAP, MAZE_MAP_2, MAZE_MAP_3, MAZE_MAP_4, MAZE_MAP_5, MAZE_MAP_6, MAZE_MAP_7, MAZE_MAP_8, MAZE_MAP_9, MAZE_MAP_10]
        self.current_level_idx = 0
        
        self.all_sprites = pygame.sprite.Group()
        self.init_level(self.current_level_idx)
        
        self.game_ui = GameUI(self.manager)
        
        self.algo_generator = None
        self.visited_cells = []
        self.final_path = []
        self.last_step_time = 0
        self.STEP_DELAY = 0
        self.level_completed = False
        
        self.auto_moving = False
        self.auto_move_index = 0
        self.auto_move_last_time = 0
        self.AUTO_MOVE_DELAY = 100
        self.is_paused = False
        
        self.active_algorithm = None
        self.current_tracker = None
        
        self.clock = pygame.time.Clock()
        self.is_running = True

    def init_level(self, idx):
        self.map_surface, self.player, self.ladder_pos, self.maze = load_level(
            self.levels[idx], self.tileset_sheet, self.char_sheet
        )
        self.all_sprites.empty()
        self.all_sprites.add(self.player)
        
        self.monster = None
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 4:
                    self.monster = pygame.sprite.Sprite()
                    self.monster.image = get_tile(self.char_sheet, 6, 1)
                    self.monster.rect = self.monster.image.get_rect()
                    self.monster.rect.topleft = (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE)
                    self.all_sprites.add(self.monster)
        
        cols = len(self.maze[0])
        rows = len(self.maze)
        self.overlay_surface = pygame.Surface((cols * SCALED_TILE_SIZE, rows * SCALED_TILE_SIZE), pygame.SRCALPHA)
        
    def reset_state(self):
        self.level_completed = False
        self.visited_cells.clear()
        self.final_path.clear()
        self.overlay_surface.fill((0,0,0,0))
        self.game_ui.auto_move_button.disable()
        self.auto_moving = False
        self.algo_generator = None
        self.is_paused = False
        self.active_algorithm = None
        self.current_tracker = None
        self.game_ui.reset_pause()

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(FPS)/1000.0
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                
                action, data = self.game_ui.process_events(event)
                if action == "RUN_SKILL":
                    self.reset_state()
                    self.active_algorithm = data
                    
                    start_node = ((self.player.rect.x + self.player.rect.width//2) // SCALED_TILE_SIZE, 
                                  (self.player.rect.y + self.player.rect.height//2) // SCALED_TILE_SIZE)
                    
                    self.algo_generator = run_algorithm(data, self.maze, start_node, self.ladder_pos, self.current_level_idx)
                    
                elif action == "NEXT_LEVEL":
                    if self.current_level_idx + 1 < len(self.levels):
                        self.current_level_idx += 1
                        self.init_level(self.current_level_idx)
                        self.reset_state()
                        self.game_ui.log(f"<font color='#00FF00'>Welcome to Level {self.current_level_idx + 1}!</font>")
                        
                        level_name = f"Level {self.current_level_idx + 1}"
                        if level_name not in self.game_ui.unlocked_levels:
                            self.game_ui.unlocked_levels.append(level_name)
                        self.game_ui.update_level_selector(level_name)
                    else:
                        self.game_ui.log("<font color='#00FF00'>You have completed all levels!</font>")
                elif action == "SELECT_LEVEL":
                    self.current_level_idx = data
                    self.init_level(self.current_level_idx)
                    self.reset_state()
                    self.game_ui.log(f"<font color='#00FF00'>Switched to Level {self.current_level_idx + 1}!</font>")
                elif action == "UNLOCK_ALL":
                    self.game_ui.unlocked_levels = [f"Level {i+1}" for i in range(len(self.levels))]
                    self.game_ui.update_level_selector(f"Level {self.current_level_idx + 1}")
                    for skill in ["BFS", "DFS", "GBFS", "A*", "Hill Climbing", "Simulated Annealing", "Forward Checking", "Min-Conflicts", "Belief State DFS", "Partially Observable BFS", "Minimax", "Alpha-Beta"]:
                        if skill not in self.game_ui.player_skills:
                            self.game_ui.player_skills.append(skill)
                    if self.game_ui.skill_list:
                        self.game_ui.skill_list.set_item_list(self.game_ui.player_skills)
                    self.game_ui.log("<font color='#00FFFF'>Tất cả Màn chơi & Kỹ năng đã được mở khóa (Demo Mode)!</font>")
                elif action == "CLEAR_LOG":
                    self.game_ui.clear_log()
                elif action == "RESET":
                    self.init_level(self.current_level_idx)
                    self.reset_state()
                    self.game_ui.log(f"<font color='#00FF00'>Level {self.current_level_idx + 1} Reset!</font>")
                elif action == "SPEED_CHANGE":
                    self.STEP_DELAY = data
                elif action == "AUTO_MOVE":
                    if self.final_path:
                        self.auto_moving = True
                        self.auto_move_index = 0
                        self.auto_move_last_time = pygame.time.get_ticks()
                elif action == "PAUSE_TOGGLE":
                    self.is_paused = not self.is_paused
                    self.game_ui.log(f"<font color='#FFFF00'>{'Paused' if self.is_paused else 'Resumed'}</font>")
                
                self.manager.process_events(event)
                
            self.update_logic(keys)
            self.update_algorithm()
            self.update_auto_move()
            
            if not self.auto_moving:
                self.all_sprites.update(keys)
            self.manager.update(time_delta)
            
            self.draw()

        pygame.quit()

    def update_logic(self, keys):
        player_tile = ((self.player.rect.x + self.player.rect.width//2) // SCALED_TILE_SIZE, 
                       (self.player.rect.y + self.player.rect.height//2) // SCALED_TILE_SIZE)
        if not self.level_completed:
            if self.ladder_pos is not None and player_tile == self.ladder_pos:
                self.level_completed = True
                if self.current_level_idx == 0:
                    self.game_ui.show_level_complete("DFS")
                elif self.current_level_idx == 1:
                    self.game_ui.show_level_complete(["GBFS", "A*"])
                elif self.current_level_idx == 2:
                    self.game_ui.show_level_complete("Hill Climbing")
                elif self.current_level_idx == 3:
                    self.game_ui.show_level_complete("Simulated Annealing")
                elif self.current_level_idx == 4:
                    self.game_ui.show_level_complete("Forward Checking")
                elif self.current_level_idx == 5:
                    self.game_ui.show_level_complete("Min-Conflicts")
                elif self.current_level_idx == 6:
                    self.game_ui.show_level_complete("Belief State DFS")
                elif self.current_level_idx == 7:
                    self.game_ui.show_level_complete("Partially Observable BFS")
                elif self.current_level_idx == 8:
                    self.game_ui.show_level_complete(["Minimax", "Alpha-Beta"])
                elif self.current_level_idx == 9:
                    self.game_ui.show_victory_screen()
                else:
                    self.game_ui.show_level_complete("Trống")

    def update_algorithm(self):
        current_time = pygame.time.get_ticks()
        if not self.is_paused and self.algo_generator and current_time - self.last_step_time > self.STEP_DELAY:
            self.last_step_time = current_time
            try:
                action, data = next(self.algo_generator)
                if action == "LOG":
                    self.game_ui.log(data)
                elif action == "VISIT":
                    self.visited_cells.append(data)
                    pygame.draw.rect(self.overlay_surface, (0, 100, 255, 100), 
                                     (data[0]*SCALED_TILE_SIZE, data[1]*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                elif action == "STATE":
                    history_item = data
                    tracker = history_item[0]
                    self.current_tracker = tracker
                    if len(history_item) > 3:
                        self.game_ui.log(history_item[3])
                        if not self.level_completed and "hoàn hảo" in history_item[3]:
                            self.level_completed = True
                            if self.active_algorithm == "Forward Checking":
                                self.game_ui.show_level_complete(["Min-Conflicts"])
                            elif self.active_algorithm == "Min-Conflicts":
                                self.game_ui.show_level_complete(["Belief State DFS"])
                            else:
                                self.game_ui.show_level_complete("Màn chơi đã hoàn thành!")
                    else:
                        self.game_ui.log(f"Frontier: {history_item[2]}, Reached: {history_item[1]}")
                        
                    self.overlay_surface.fill((0,0,0,0))
                    
                    try:
                        gem_green = get_tile(self.tileset_sheet, 1, 7)
                        gem_blue = get_tile(self.tileset_sheet, 2, 7)
                        gem_red = get_tile(self.tileset_sheet, 3, 7)
                        gem_yellow = get_tile(self.tileset_sheet, 6, 8)
                        gem_tiles = {21: gem_green, 22: gem_blue, 23: gem_red, 24: gem_yellow}
                    except Exception:
                        gem_tiles = {}

                    for y in range(len(tracker)):
                        for x in range(len(tracker[0])):
                            val = tracker[y][x]
                            if val == 3:
                                self.player.rect.topleft = (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE)
                            elif val == 4 and self.monster:
                                self.monster.rect.topleft = (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE)
                            elif val == 6: # Visited / Conflict (for older algos)
                                pygame.draw.rect(self.overlay_surface, (0, 100, 255, 100), 
                                                 (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                            elif val == 5: # Frontier / Valid
                                pygame.draw.rect(self.overlay_surface, (255, 165, 0, 100),
                                                 (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                            else:
                                is_conflict = False
                                is_active = False
                                
                                if isinstance(val, tuple):
                                    val, is_conflict, is_active = val
                                
                                if is_conflict:
                                    pygame.draw.rect(self.overlay_surface, (255, 0, 0, 50), # Xung đột thì nền đỏ
                                                     (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                                elif is_active:
                                    pygame.draw.rect(self.overlay_surface, (0, 255, 0, 100), # Đang xét nền xanh lá
                                                     (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                                    
                                if val in gem_tiles:
                                    self.overlay_surface.blit(gem_tiles[val], (x*SCALED_TILE_SIZE, y*SCALED_TILE_SIZE))
                elif action == "PATH":
                    self.final_path = data
                    self.game_ui.auto_move_button.enable()
                    for i in range(len(self.final_path)-1):
                        p1 = self.final_path[i]
                        p2 = self.final_path[i+1]
                        pygame.draw.line(self.overlay_surface, (255, 0, 0, 200),
                                         (p1[0]*SCALED_TILE_SIZE + SCALED_TILE_SIZE//2, p1[1]*SCALED_TILE_SIZE + SCALED_TILE_SIZE//2),
                                         (p2[0]*SCALED_TILE_SIZE + SCALED_TILE_SIZE//2, p2[1]*SCALED_TILE_SIZE + SCALED_TILE_SIZE//2), 5)
                elif action == "DONE":
                    self.algo_generator = None
            except StopIteration:
                self.algo_generator = None

    def update_auto_move(self):
        if self.auto_moving and self.final_path:
            current_time = pygame.time.get_ticks()
            if current_time - self.auto_move_last_time > self.AUTO_MOVE_DELAY:
                self.auto_move_last_time = current_time
                if self.auto_move_index < len(self.final_path):
                    target_pos = self.final_path[self.auto_move_index]
                    self.player.rect.x = target_pos[0] * SCALED_TILE_SIZE
                    self.player.rect.y = target_pos[1] * SCALED_TILE_SIZE
                    self.auto_move_index += 1
                else:
                    self.auto_moving = False

    def draw(self):
        self.window_surface.blit(self.background, (0, 0))
        
        board_w, board_h = self.map_surface.get_size()
        game_board = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
        game_board.blit(self.map_surface, (0, 0))
        game_board.blit(self.overlay_surface, (0, 0))
        
        if self.game_ui.sensor_on and self.current_level_idx in [3, 4]:
            maze_curr = self.levels[self.current_level_idx]
            res_map = RESONANCE_MAP if self.current_level_idx == 3 else RESONANCE_MAP_5
            for y in range(len(res_map)):
                for x in range(len(res_map[0])):
                    if maze_curr[y][x] != 1:
                        text_str = str(res_map[y][x])
                        text_outline = self.pixel_font.render(text_str, True, (0, 0, 0))
                        text = self.pixel_font.render(text_str, True, (255, 255, 0))
                        text_rect = text.get_rect(center=(x * SCALED_TILE_SIZE + SCALED_TILE_SIZE//2, y * SCALED_TILE_SIZE + SCALED_TILE_SIZE//2))
                        game_board.blit(text_outline, (text_rect.x+1, text_rect.y+1))
                        game_board.blit(text, text_rect)
        
        if self.current_level_idx not in (5, 6):
            self.all_sprites.draw(game_board)
        
        offset_x = 0
        offset_y = 0
        if self.current_level_idx in (5, 6):
            game_board = pygame.transform.scale(game_board, (624, 624))
            offset_x = (816 - 624) // 2
        else:
            board_w, board_h = game_board.get_size()
            offset_x = (816 - board_w) // 2 if board_w < 816 else 0
            offset_y = (624 - board_h) // 2 if board_h < 624 else 0
            
        self.window_surface.blit(game_board, (offset_x, offset_y))
        self.manager.draw_ui(self.window_surface)
        pygame.display.update()
