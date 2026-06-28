import pygame
import random
from core.settings import SCALED_TILE_SIZE
from core.utils import get_tile
from levels.maze_data import MAZE_MAP_4, MAZE_MAP_5, RESONANCE_MAP, RESONANCE_MAP_5
from entities.player import Player

def load_level(maze_data, tileset_sheet, char_sheet):
    # Extract tiles
    floor_tile = get_tile(tileset_sheet, 1, 1)
    wall_top = get_tile(tileset_sheet, 4, 0)
    wall_left = get_tile(tileset_sheet, 0, 1)
    wall_right = get_tile(tileset_sheet, 5, 1)
    wall_bottom = get_tile(tileset_sheet, 1, 4)
    wall_corner_tl = get_tile(tileset_sheet, 0, 0)
    wall_corner_bl = get_tile(tileset_sheet, 0, 4)
    wall_corner_tr = get_tile(tileset_sheet, 5, 0)
    wall_corner_br = get_tile(tileset_sheet, 5, 4)
    wall_inner = get_tile(tileset_sheet, 4, 0)
    wall_inner_vert = get_tile(tileset_sheet, 2, 0)
    wall_t_junction = get_tile(tileset_sheet, 3, 0)
    wall_corner_right_t_left = get_tile(tileset_sheet, 6, 0)
    wall_corner_left_t_right = get_tile(tileset_sheet, 7, 0)
    ladder_tile = get_tile(tileset_sheet, 9, 3)
    cobweb_1 = get_tile(tileset_sheet, 2, 1)
    cobweb_2 = get_tile(tileset_sheet, 2, 2)
    
    # Resonance tiles for Level 4
    res_tile_0_25 = get_tile(tileset_sheet, 1, 1)
    res_tile_26_50 = get_tile(tileset_sheet, 1, 1)
    res_tile_51_75 = get_tile(tileset_sheet, 1, 1)
    res_tile_76_99 = get_tile(tileset_sheet, 1, 1)
    magic_portal = get_tile(tileset_sheet, 9, 2)
    
    maze = maze_data
    cols = len(maze[0])
    rows = len(maze)
    
    map_surface = pygame.Surface((cols * SCALED_TILE_SIZE, rows * SCALED_TILE_SIZE))
    
    start_x, start_y = 1, 1
    ladder_pos = None
    for y in range(rows):
        for x in range(cols):
            val = maze[y][x]
            if val == 1:
                tile = wall_top
                if y == 0 and x == 0:
                    tile = wall_corner_tl
                elif y == 0 and x == cols - 1:
                    tile = wall_corner_tr
                elif y == rows - 1 and x == 0:
                    tile = wall_corner_bl
                elif y == rows - 1 and x == cols - 1:
                    tile = wall_corner_br
                elif y == 0:
                    if maze[y+1][x] == 1:
                        tile = wall_t_junction
                    else:
                        tile = wall_top
                elif y == rows - 1:
                    tile = wall_bottom
                elif x == 0:
                    tile = wall_left
                elif x == cols - 1:
                    tile = wall_right
                else:
                    is_left_floor = (x == 0 or maze[y][x-1] != 1)
                    is_right_floor = (x == cols - 1 or maze[y][x+1] != 1)
                    is_bottom_floor = (y == rows - 1 or maze[y+1][x] != 1)

                    if is_bottom_floor:
                        tile = wall_inner
                    else:
                        if not is_left_floor and not is_right_floor:
                            tile = wall_t_junction
                        elif not is_left_floor and is_right_floor:
                            tile = wall_corner_right_t_left
                        elif is_left_floor and not is_right_floor:
                            tile = wall_corner_left_t_right
                        else:
                            tile = wall_inner_vert
                map_surface.blit(tile, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
            elif val == 2:
                ladder_pos = (x, y)
                if maze_data in (MAZE_MAP_4, MAZE_MAP_5):
                    map_surface.blit(magic_portal, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                else:
                    map_surface.blit(floor_tile, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                    map_surface.blit(ladder_tile, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
            elif val in (0, 3, 4, 8, 20, 21, 22, 23, 24):
                if maze_data in (MAZE_MAP_4, MAZE_MAP_5):
                    res_map_curr = RESONANCE_MAP if maze_data is MAZE_MAP_4 else RESONANCE_MAP_5
                    res = res_map_curr[y][x]
                    if res <= 25:
                        ftile = res_tile_0_25
                    elif res <= 50:
                        ftile = res_tile_26_50
                    elif res <= 75:
                        ftile = res_tile_51_75
                    else:
                        ftile = res_tile_76_99
                    map_surface.blit(ftile, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                elif val in (20, 21, 22, 23, 24):
                    gem_empty = get_tile(tileset_sheet, 1, 6)
                    map_surface.blit(gem_empty, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                    if val in (21, 22, 23, 24):
                        gem_green = get_tile(tileset_sheet, 1, 7)
                        gem_blue = get_tile(tileset_sheet, 2, 7)
                        gem_red = get_tile(tileset_sheet, 3, 7)
                        gem_yellow = get_tile(tileset_sheet, 6, 8)
                        gem_tiles = {21: gem_green, 22: gem_blue, 23: gem_red, 24: gem_yellow}
                        map_surface.blit(gem_tiles[val], (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                else:
                    map_surface.blit(floor_tile, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
                
                if val == 3:
                    start_x, start_y = x, y
                elif val == 8 and maze_data not in (MAZE_MAP_4, MAZE_MAP_5):
                    chosen_cobweb = random.choice([cobweb_1, cobweb_2])
                    map_surface.blit(chosen_cobweb, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))

    player = Player(start_x * SCALED_TILE_SIZE, start_y * SCALED_TILE_SIZE, char_sheet, maze)
    return map_surface, player, ladder_pos, maze
