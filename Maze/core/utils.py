import pygame
from .settings import SCALED_TILE_SIZE, TILE_SIZE

def load_image(path):
    return pygame.image.load(path).convert_alpha()

def get_tile(image, x, y):
    """Extracts a tile from the spritesheet, then scales it."""
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    tile = pygame.Surface(rect.size, pygame.SRCALPHA)
    tile.blit(image, (0, 0), rect)
    return pygame.transform.scale(tile, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
