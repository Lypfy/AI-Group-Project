import pygame
from core.settings import SCALED_TILE_SIZE, WINDOW_SIZE
from core.utils import get_tile

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, char_sheet, maze):
        super().__init__()
        # Assuming the idle frame is the first 16x16 frame
        self.image = get_tile(char_sheet, 0, 0)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5
        self.maze = maze

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            
        # Move X
        self.rect.x += dx
        col_type_x = self.check_collision()
        if col_type_x == "wall":
            self.rect.x -= dx
            
        # Move Y
        self.rect.y += dy
        col_type_y = self.check_collision()
        if col_type_y == "wall":
            self.rect.y -= dy
            
        if col_type_x == "ladder" or col_type_y == "ladder":
            pass
            # Could trigger a win state here
            
        # Basic bounds checking
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WINDOW_SIZE[0]: self.rect.right = WINDOW_SIZE[0]
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > WINDOW_SIZE[1]: self.rect.bottom = WINDOW_SIZE[1]
        
    def check_collision(self):
        # Shrink hitbox slightly to make moving through 1-tile gaps easier
        hitbox = self.rect.inflate(-10, -10)
        corners = [
            hitbox.topleft,
            hitbox.topright,
            hitbox.bottomleft,
            hitbox.bottomright
        ]
        
        on_ladder = False
        for cx, cy in corners:
            grid_x = cx // SCALED_TILE_SIZE
            grid_y = cy // SCALED_TILE_SIZE
            if 0 <= grid_y < len(self.maze) and 0 <= grid_x < len(self.maze[0]):
                if self.maze[grid_y][grid_x] == 1:
                    return "wall"
                if self.maze[grid_y][grid_x] == 2:
                    on_ladder = True
                    
        if on_ladder:
            return "ladder"
        return None
