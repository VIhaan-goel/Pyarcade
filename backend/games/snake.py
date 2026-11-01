import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 24
GRID_WIDTH = 25
GRID_HEIGHT = 20
TOP_BAR = 30
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE + TOP_BAR
START_FPS = 6    # speed at the start
MAX_FPS = 12     # top speed

# Colors
BACKGROUND = (16, 24, 32)
GRID_COLOR = (28, 39, 50)
SNAKE_HEAD = (74, 222, 128)
SNAKE_BODY = (34, 197, 94)
FOOD_COLOR = (251, 113, 133)
TEXT_COLOR = (255, 255, 255)
EYE_WHITE = (255, 255, 255)
EYE_PUPIL = (16, 24, 32)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 20, bold=True)


def place_food(snake):
    empty = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in snake
    ]
    return random.choice(empty) if empty else None


def draw_grid():
    # Vertical lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, TOP_BAR), (x, HEIGHT))
    # Horizontal lines
    for y in range(TOP_BAR, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_snake_face(x, y, direction):
    px = x * CELL_SIZE
    py = y * CELL_SIZE + TOP_BAR
    dx, dy = direction

    # Position the eyes depending on which way the snake is facing
    if (dx, dy) == (1, 0):  # Right
        eye1, eye2 = (px + 16, py + 7), (px + 16, py + 17)
    elif (dx, dy) == (-1, 0):  # Left
        eye1, eye2 = (px + 8, py + 7), (px + 8, py + 17)
    elif (dx, dy) == (0, -1):  # Up
        eye1, eye2 = (px + 7, py + 8), (px + 17, py + 8)
    else:  # Down
        eye1, eye2 = (px + 7, py + 16), (px + 17, py + 16)

    # Draw the white part of the eyes and dark pupils
    for ex, ey in (eye1, eye2):
        pygame.draw.circle(screen, EYE_WHITE, (ex, ey), 3)
        pygame.draw.circle(screen, EYE_PUPIL, (ex + dx, ey + dy), 1.5)


def main():
    center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
    direction = (1, 0)
    next_direction = direction
    food = place_food(snake)
    score = 0
    paused = False
    fps = START_FPS
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return main()
                elif event.key == pygame.K_SPACE and not game_over:
                    paused = not paused
                elif not game_over and not paused:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                        next_direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                        next_direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                        next_direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        next_direction = (1, 0)

        if not paused and not game_over:
            direction = next_direction
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            if (
                not 0 <= new_head[0] < GRID_WIDTH
                or not 0 <= new_head[1] < GRID_HEIGHT
                or new_head in snake[:-1]
            ):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    fps = min(MAX_FPS, START_FPS + score // 4)
                    food = place_food(snake)
                else:
                    snake.pop()

        # 1. Clear Screen & Draw Grid
        screen.fill(BACKGROUND)
        draw_grid()

        # 2. Draw Top Score Bar
        pygame.draw.rect(screen, (11, 18, 24), (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(screen, GRID_COLOR, (0, TOP_BAR), (WIDTH, TOP_BAR), 2)
        score_surface = font.render(
            f"Score: {score}   (Space: Pause | R: Restart)", True, TEXT_COLOR
        )
        screen.blit(score_surface, (15, 14))

        # 3. Draw Food
        if food:
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                (
                    food[0] * CELL_SIZE + 4,
                    food[1] * CELL_SIZE + TOP_BAR + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8,
                ),
                border_radius=4,
            )

        # 4. Draw Snake Body & Face
        for i, (x, y) in enumerate(snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(
                screen,
                color,
                (
                    x * CELL_SIZE + 2,
                    y * CELL_SIZE + TOP_BAR + 2,
                    CELL_SIZE - 4,
                    CELL_SIZE - 4,
                ),
                border_radius=5 if i == 0 else 3,
            )
            if i == 0:
                draw_snake_face(x, y, direction)

        # 5. Draw Game Over / Pause Overlay
        if game_over or paused:
            msg = "Game Over! Press R to restart" if game_over else "Paused - Press Space"
            msg_surface = font.render(msg, True, TEXT_COLOR)
            rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, (11, 18, 24), rect.inflate(24, 24), border_radius=8)
            pygame.draw.rect(screen, GRID_COLOR, rect.inflate(24, 24), width=2, border_radius=8)
            screen.blit(msg_surface, rect)

        pygame.display.flip()
        clock.tick(fps)


if __name__ == "__main__":
    main()