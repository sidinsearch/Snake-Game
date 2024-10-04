import pygame
import sys
import random
import os
import math

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BACKGROUND_COLOR = (10, 20, 30)
GRID_COLOR = (30, 40, 50)
SNAKE_COLOR = (0, 255, 100)
SNAKE_BORDER_COLOR = (0, 200, 80)
FOOD_COLOR = (255, 50, 50)
FOOD_BORDER_COLOR = (200, 0, 0)
BIG_FOOD_COLOR = (255, 215, 0)
BIG_FOOD_BORDER_COLOR = (218, 165, 32)
TEXT_COLOR = (220, 220, 220)
OBSTACLE_COLOR = (100, 100, 100)
OBSTACLE_BORDER_COLOR = (80, 80, 80)
POWER_UP_COLOR = (0, 191, 255)  # Deep Sky Blue

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Fonts
font_path = os.path.join(os.path.dirname(__file__), 'PressStart2P-Regular.ttf')
if not os.path.exists(font_path):
    print("Retro font not found. Using default font.")
    font_path = None

def load_font(size):
    return pygame.font.Font(font_path, size) if font_path else pygame.font.Font(None, size)

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = SNAKE_COLOR
        self.border_color = SNAKE_BORDER_COLOR
        self.score = 0
        self.speed = 10
        self.level = 1
        self.power_up = False
        self.power_up_time = 0

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        if len(self.positions) > 2 and new in self.positions[2:]:
            return True  # Collision occurred
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
        return False

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.speed = 10
        self.level = 1
        self.power_up = False
        self.power_up_time = 0

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            r = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            
            # Create a gradient effect
            color = [max(0, c - i * 3) for c in self.color]
            if self.power_up:
                color = [min(255, c + 50) for c in POWER_UP_COLOR]  # Brighter power-up color
            pygame.draw.rect(surface, color, r)
            pygame.draw.rect(surface, self.border_color, r, 1)

            # Add eyes to the head
            if i == 0:
                self.draw_eyes(surface, r)

    def draw_eyes(self, surface, head_rect):
        eye_radius = GRID_SIZE // 5
        eye_offset = GRID_SIZE // 4

        # Determine eye positions based on direction
        if self.direction == LEFT:
            left_eye = (head_rect.left + eye_offset, head_rect.centery - eye_offset)
            right_eye = (head_rect.left + eye_offset, head_rect.centery + eye_offset)
        elif self.direction == RIGHT:
            left_eye = (head_rect.right - eye_offset, head_rect.centery - eye_offset)
            right_eye = (head_rect.right - eye_offset, head_rect.centery + eye_offset)
        elif self.direction == UP:
            left_eye = (head_rect.centerx - eye_offset, head_rect.top + eye_offset)
            right_eye = (head_rect.centerx + eye_offset, head_rect.top + eye_offset)
        else:  # DOWN
            left_eye = (head_rect.centerx - eye_offset, head_rect.bottom - eye_offset)
            right_eye = (head_rect.centerx + eye_offset, head_rect.bottom - eye_offset)

        # Draw eyes
        pygame.draw.circle(surface, (255, 255, 255), left_eye, eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), right_eye, eye_radius)
        
        # Draw pupils
        pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_radius // 2)
        pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_radius // 2)

class Food:
    def __init__(self, is_big=False):
        self.position = (0, 0)
        self.is_big = is_big
        self.color = BIG_FOOD_COLOR if is_big else FOOD_COLOR
        self.border_color = BIG_FOOD_BORDER_COLOR if is_big else FOOD_BORDER_COLOR
        self.size = 2 if is_big else 1
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = 10000 if is_big else float('inf')  # 10 seconds for big food
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - self.size), random.randint(0, GRID_HEIGHT - self.size))

    def draw(self, surface):
        if self.is_big:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.spawn_time
            if elapsed_time < self.lifespan:
                size_factor = 1 - (elapsed_time / self.lifespan)
                current_size = max(1, int(self.size * size_factor * GRID_SIZE))
            else:
                current_size = GRID_SIZE
        else:
            current_size = GRID_SIZE

        center = ((self.position[0] + 0.5) * GRID_SIZE, (self.position[1] + 0.5) * GRID_SIZE)
        pygame.draw.circle(surface, self.color, center, current_size // 2)
        pygame.draw.circle(surface, self.border_color, center, current_size // 2, 1)
        
        # Add a shine effect
        shine_radius = current_size // 8
        shine_pos = (center[0] - current_size // 4, center[1] - current_size // 4)
        pygame.draw.circle(surface, (255, 255, 255), shine_pos, shine_radius)

    def is_expired(self):
        if self.is_big:
            return pygame.time.get_ticks() - self.spawn_time > self.lifespan
        return False

class Obstacle:
    def __init__(self):
        self.shapes = []
        self.color = OBSTACLE_COLOR
        self.border_color = OBSTACLE_BORDER_COLOR

    def generate_shapes(self, num_shapes, snake_positions, food_position):
        self.shapes = []
        shapes = ['L', 'I', 'T', 'O']
        for _ in range(num_shapes):
            shape = random.choice(shapes)
            while True:
                if shape == 'L':
                    width, height = 3, 3
                    blocks = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
                elif shape == 'I':
                    width, height = 1, 4
                    blocks = [(0, i) for i in range(4)]
                elif shape == 'T':
                    width, height = 3, 2
                    blocks = [(0, 0), (1, 0), (2, 0), (1, 1)]
                elif shape == 'O':
                    width, height = 2, 2
                    blocks = [(0, 0), (0, 1), (1, 0), (1, 1)]

                x = random.randint(0, GRID_WIDTH - width)
                y = random.randint(0, GRID_HEIGHT - height)
                
                occupied = False
                for dx, dy in blocks:
                    pos = (x + dx, y + dy)
                    if pos in snake_positions or pos == food_position or any(pos in shape_blocks for shape_blocks in self.shapes):
                        occupied = True
                        break
                
                if not occupied:
                    self.shapes.append([(x + dx, y + dy) for dx, dy in blocks])
                    break

    def draw(self, surface):
        for shape in self.shapes:
            for pos in shape:
                r = pygame.Rect((pos[0] * GRID_SIZE, pos[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, self.color, r)
                pygame.draw.rect(surface, self.border_color, r, 1)
                
                # Add a 3D effect
                pygame.draw.line(surface, (50, 50, 50), r.topleft, r.bottomleft, 2)
                pygame.draw.line(surface, (50, 50, 50), r.topleft, r.topright, 2)
                pygame.draw.line(surface, (150, 150, 150), r.bottomright, r.bottomleft, 2)
                pygame.draw.line(surface, (150, 150, 150), r.bottomright, r.topright, 2)

def draw_grid(surface):
    for y in range(0, GRID_HEIGHT):
        for x in range(0, GRID_WIDTH):
            r = pygame.Rect((x * GRID_SIZE, y * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, GRID_COLOR, r, 1)

def draw_text(surface, text, size, x, y):
    font = load_font(size)
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def game_over_screen(screen, score, level):
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "GAME OVER", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, f"Score: {score}", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
    draw_text(screen, f"Level: {level}", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
    draw_text(screen, "Press SPACE to play again", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    
    snake = Snake()
    food = Food()
    big_food = None
    obstacles = Obstacle()
    obstacles.generate_shapes(snake.level, snake.positions, food.position)

    score_font = load_font(24)
    high_score = 0
    using_mouse = True
    last_mouse_pos = pygame.mouse.get_pos()

    big_food_timer = 0
    big_food_interval = 30000  # 30 seconds
    power_up_duration = 5000  # 5 seconds

    while True:
        clock.tick(snake.speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    using_mouse = False
                    if event.key == pygame.K_UP:
                        snake.turn(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.turn(RIGHT)

        current_mouse_pos = pygame.mouse.get_pos()
        if current_mouse_pos != last_mouse_pos:
            using_mouse = True
            last_mouse_pos = current_mouse_pos

        if using_mouse:
            mouse_x, mouse_y = current_mouse_pos
            head_x, head_y = snake.get_head_position()
            dx = mouse_x // GRID_SIZE - head_x
            dy = mouse_y // GRID_SIZE - head_y
            if abs(dx) > abs(dy):
                snake.turn(RIGHT if dx > 0 else LEFT)
            elif dy != 0:
                snake.turn(DOWN if dy > 0 else UP)

        pygame.mouse.set_visible(using_mouse)

        # Check for collision with obstacles
        collision = snake.move()
        if not snake.power_up:
            collision = collision or any(snake.get_head_position() in shape for shape in obstacles.shapes)
        
        if collision:
            game_over_screen(screen, snake.score, snake.level)
            snake.reset()
            food = Food()
            big_food = None
            obstacles = Obstacle()
            obstacles.generate_shapes(snake.level, snake.positions, food.position)
            using_mouse = True
            last_mouse_pos = pygame.mouse.get_pos()
            big_food_timer = 0
            game_over_screen(screen, snake.score, snake.level)
            snake.reset()
            food = Food()
            big_food = None
            obstacles = Obstacle()
            obstacles.generate_shapes(snake.level, snake.positions, food.position)
            using_mouse = True
            last_mouse_pos = pygame.mouse.get_pos()
            big_food_timer = 0
        # Check for eating food
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 1
            snake.speed = min(snake.speed + 0.5, 20)
            food.randomize_position()
            while any(food.position in shape for shape in obstacles.shapes):
                food.randomize_position()
            high_score = max(snake.score, high_score)
            
            # Level up every 5 points
            if snake.score % 5 == 0:
                snake.level += 1
                obstacles.generate_shapes(snake.level, snake.positions, food.position)

        # Handle big food and power-up
        if big_food:
            if snake.get_head_position() == big_food.position:
                snake.length += 2
                snake.score += 5
                snake.power_up = True
                snake.power_up_time = pygame.time.get_ticks()
                big_food = None
                big_food_timer = pygame.time.get_ticks()
            elif big_food.is_expired():
                big_food = None
                big_food_timer = pygame.time.get_ticks()
        else:
            if pygame.time.get_ticks() - big_food_timer > big_food_interval:
                big_food = Food(is_big=True)
                while any(big_food.position in shape for shape in obstacles.shapes):
                    big_food.randomize_position()

        # Check if power-up has expired
        if snake.power_up and pygame.time.get_ticks() - snake.power_up_time > power_up_duration:
            snake.power_up = False

        # Draw everything
        surface.fill(BACKGROUND_COLOR)
        draw_grid(surface)
        snake.draw(surface)
        food.draw(surface)
        if big_food:
            big_food.draw(surface)
        obstacles.draw(surface)

        screen.blit(surface, (0, 0))
        score_text = score_font.render(f"Score: {snake.score}  High Score: {high_score}  Level: {snake.level}", True, TEXT_COLOR)
        screen.blit(score_text, (5, 5))

        # Draw power-up timer if active
        if snake.power_up:
            power_up_time_left = (power_up_duration - (pygame.time.get_ticks() - snake.power_up_time)) // 1000
            power_up_text = score_font.render(f"Power-up: {power_up_time_left}s", True, POWER_UP_COLOR)
            screen.blit(power_up_text, (5, 35))

        pygame.display.update()

if __name__ == "__main__":
    main()