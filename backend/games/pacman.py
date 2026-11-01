import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 28
TOP_BAR = 50
FPS = 7

# Maze Layout:
# '#' = Wall, '.' = Dot, 'o' = Power Pellet, ' ' = Empty
MAZE_LAYOUT = [
    "###################",
    "#o.......#.......o#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.### # ###.####",
    "   #.#       #.#   ",
    "####.# ## ## #.####",
    "    .  #   #  .    ",
    "####.# ##### #.####",
    "   #.#       #.#   ",
    "####.# ##### #.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o.#..... .....#.o#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]

GRID_WIDTH = len(MAZE_LAYOUT[0])
GRID_HEIGHT = len(MAZE_LAYOUT)
WIDTH = GRID_WIDTH * TILE_SIZE
HEIGHT = GRID_HEIGHT * TILE_SIZE + TOP_BAR

# Colors
BLACK = (11, 15, 25)
WALL_COLOR = (37, 99, 235)
DOT_COLOR = (254, 240, 138)
PACMAN_COLOR = (250, 204, 21)
SCARED_COLOR = (59, 130, 246)
WHITE = (255, 255, 255)
GHOST_COLORS = [
    (239, 68, 68),    # Blinky (Red)
    (244, 114, 182),  # Pinky (Pink)
    (34, 211, 238),   # Inky (Cyan)
    (251, 146, 60),   # Clyde (Orange)
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 20, bold=True)


def can_move(x, y, maze):
    # Wrap around the side tunnels
    x = x % GRID_WIDTH
    if 0 <= y < GRID_HEIGHT:
        return maze[y][x] != "#"
    return False


def draw_pacman(x, y, direction, mouth_open):
    cx = x * TILE_SIZE + TILE_SIZE // 2
    cy = y * TILE_SIZE + TOP_BAR + TILE_SIZE // 2
    radius = TILE_SIZE // 2 - 2

    pygame.draw.circle(screen, PACMAN_COLOR, (cx, cy), radius)

    # Cut out a triangle for the animated mouth
    if mouth_open:
        dx, dy = direction
        if (dx, dy) == (0, 0):
            dx, dy = (1, 0)
        angle = math.atan2(-dy, dx)
        mouth_angle = 0.5  # Radians

        p1 = (cx, cy)
        p2 = (
            cx + int(radius * 1.3 * math.cos(angle - mouth_angle)),
            cy - int(radius * 1.3 * math.sin(angle - mouth_angle)),
        )
        p3 = (
            cx + int(radius * 1.3 * math.cos(angle + mouth_angle)),
            cy - int(radius * 1.3 * math.sin(angle + mouth_angle)),
        )
        pygame.draw.polygon(screen, BLACK, [p1, p2, p3])


def draw_ghost(x, y, color, scared):
    px = x * TILE_SIZE + 4
    py = y * TILE_SIZE + TOP_BAR + 4
    w = TILE_SIZE - 8
    h = TILE_SIZE - 8
    draw_color = SCARED_COLOR if scared else color

    # Head (dome) & lower body
    pygame.draw.circle(screen, draw_color, (px + w // 2, py + h // 2 - 2), w // 2)
    pygame.draw.rect(screen, draw_color, (px, py + h // 2 - 2, w, h // 2 + 2))

    # Eyes
    for offset in (-4, 4):
        ex = px + w // 2 + offset
        ey = py + h // 2 - 3
        pygame.draw.circle(screen, WHITE, (ex, ey), 3)
        pygame.draw.circle(screen, BLACK, (ex, ey), 1.5)


def main():
    maze = [list(row) for row in MAZE_LAYOUT]
    pac_x, pac_y = 9, 15
    pac_dir = (0, 0)
    next_dir = (0, 0)
    mouth_open = True

    ghosts = [
        {"x": 9, "y": 8, "dir": (0, -1), "color": GHOST_COLORS[0]},
        {"x": 8, "y": 9, "dir": (0, -1), "color": GHOST_COLORS[1]},
        {"x": 9, "y": 9, "dir": (0, -1), "color": GHOST_COLORS[2]},
        {"x": 10, "y": 9, "dir": (0, -1), "color": GHOST_COLORS[3]},
    ]

    score = 0
    power_timer = 0
    paused = False
    game_over = False
    won = False

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
                    if event.key in (pygame.K_UP, pygame.K_w):
                        next_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        next_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        next_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        next_dir = (1, 0)

        if not paused and not game_over:
            mouth_open = not mouth_open
            if power_timer > 0:
                power_timer -= 1

            # 1. Move Pac-Man (queued direction makes turning corners easy)
            if can_move(pac_x + next_dir[0], pac_y + next_dir[1], maze):
                pac_dir = next_dir
            if can_move(pac_x + pac_dir[0], pac_y + pac_dir[1], maze):
                pac_x = (pac_x + pac_dir[0]) % GRID_WIDTH
                pac_y += pac_dir[1]

            # 2. Eat Dots & Power Pellets
            tile = maze[pac_y][pac_x]
            if tile == ".":
                maze[pac_y][pac_x] = " "
                score += 10
            elif tile == "o":
                maze[pac_y][pac_x] = " "
                score += 50
                power_timer = 35  # Ticks that ghosts stay blue

            # Check if all dots are eaten
            if not any("." in row or "o" in row for row in maze):
                won = True
                game_over = True

            # 3. Check Collisions & Move Ghosts
            for g in ghosts:
                # Check collision before ghost moves
                if g["x"] == pac_x and g["y"] == pac_y:
                    if power_timer > 0:
                        score += 200
                        g["x"], g["y"] = 9, 9
                    else:
                        game_over = True

                # Ghost AI movement
                possible_dirs = []
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    if can_move(g["x"] + dx, g["y"] + dy, maze):
                        # Avoid turning straight backward unless trapped
                        if (dx, dy) != (-g["dir"][0], -g["dir"][1]):
                            possible_dirs.append((dx, dy))

                if not possible_dirs:
                    possible_dirs = [(-g["dir"][0], -g["dir"][1])]

                g["dir"] = random.choice(possible_dirs)
                g["x"] = (g["x"] + g["dir"][0]) % GRID_WIDTH
                g["y"] += g["dir"][1]

                # Check collision after ghost moves
                if g["x"] == pac_x and g["y"] == pac_y:
                    if power_timer > 0:
                        score += 200
                        g["x"], g["y"] = 9, 9
                    else:
                        game_over = True

        # --- DRAWING ---
        screen.fill(BLACK)

        # Top Score Bar
        pygame.draw.rect(screen, (17, 24, 39), (0, 0, WIDTH, TOP_BAR))
        score_text = font.render(
            f"Score: {score}   (Space: Pause | R: Restart)", True, WHITE
        )
        screen.blit(score_text, (15, 14))

        # Draw Maze, Dots, and Power Pellets
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                cell = maze[r][c]
                px = c * TILE_SIZE
                py = r * TILE_SIZE + TOP_BAR
                if cell == "#":
                    pygame.draw.rect(
                        screen,
                        WALL_COLOR,
                        (px + 2, py + 2, TILE_SIZE - 4, TILE_SIZE - 4),
                        border_radius=5,
                    )
                elif cell == ".":
                    pygame.draw.circle(
                        screen,
                        DOT_COLOR,
                        (px + TILE_SIZE // 2, py + TILE_SIZE // 2),
                        3,
                    )
                elif cell == "o":
                    pygame.draw.circle(
                        screen,
                        DOT_COLOR,
                        (px + TILE_SIZE // 2, py + TILE_SIZE // 2),
                        7,
                    )

        # Draw Pac-Man & Ghosts
        draw_pacman(pac_x, pac_y, pac_dir, mouth_open)
        for g in ghosts:
            draw_ghost(g["x"], g["y"], g["color"], power_timer > 0)

        # Draw Pause / Game Over / Win Overlay
        if game_over or paused:
            if won:
                msg = "You Win! Press R to play again"
            elif game_over:
                msg = "Game Over! Press R to restart"
            else:
                msg = "Paused - Press Space"

            msg_surface = font.render(msg, True, WHITE)
            rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, (17, 24, 39), rect.inflate(28, 24), border_radius=8)
            pygame.draw.rect(screen, WALL_COLOR, rect.inflate(28, 24), width=2, border_radius=8)
            screen.blit(msg_surface, rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()