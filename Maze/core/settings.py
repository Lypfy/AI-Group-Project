import os

WINDOW_SIZE = (1200, 650)
FPS = 60
TILE_SIZE = 16
SCALE = 3
SCALED_TILE_SIZE = TILE_SIZE * SCALE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "asset")
TILESET_PATH = os.path.join(ASSET_DIR, "character and tileset", "Dungeon_Tileset_0002.png")
CHAR_PATH = os.path.join(ASSET_DIR, "character and tileset", "Dungeon_Character.png")
