"""2048 - slide and merge tiles. Arrow keys / WASD to move, R to restart."""
import random
import sys

import pygame

pygame.init()

SIZE = 4
CELL = 100
PAD = 10
MARGIN = 20
TOP = 120
BOARD_PX = SIZE * CELL + (SIZE + 1) * PAD
WIDTH = BOARD_PX + 2 * MARGIN
HEIGHT = TOP + BOARD_PX + MARGIN
FPS = 30

BACKGROUND = (16, 24, 32)
PANEL = (34, 40, 58)
BOARD_BG = (46, 44, 64)
EMPTY = (66, 63, 88)
TEXT = (238, 228, 218)
MUTED = (150, 150, 175)
DARK_TEXT = (119, 110, 101)
LIGHT_TEXT = (249, 246, 242)
GOLD = (237, 194, 46)
BEYOND_2048 = (60, 58, 50)
TILE_COLORS = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121), 16: (245, 149, 99),
    32: (246, 124, 95), 64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")
clock = pygame.time.Clock()

FONT_TITLE = pygame.font.SysFont("Helvetica", 52, bold=True)
FONT_LABEL = pygame.font.SysFont("Helvetica", 13, bold=True)
FONT_SCORE = pygame.font.SysFont("Helvetica", 24, bold=True)
FONT_HINT = pygame.font.SysFont("Helvetica", 16)
FONT_BANNER = pygame.font.SysFont("Helvetica", 38, bold=True)
FONT_TILES = {
    "big": pygame.font.SysFont("Helvetica", 44, bold=True),
    "mid": pygame.font.SysFont("Helvetica", 36, bold=True),
    "small": pygame.font.SysFont("Helvetica", 28, bold=True),
}

KEY_DIRECTIONS = {
    pygame.K_LEFT: "left", pygame.K_a: "left",
    pygame.K_RIGHT: "right", pygame.K_d: "right",
    pygame.K_UP: "up", pygame.K_w: "up",
    pygame.K_DOWN: "down", pygame.K_s: "down",
}


# ---------------------------- game logic ----------------------------
def slide_left(row):
    """Slide and merge one row to the left. Returns (new_row, points_gained)."""
    tiles = [v for v in row if v]
    out, gained, i = [], 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            merged = tiles[i] * 2
            out.append(merged)
            gained += merged
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    out += [0] * (SIZE - len(out))
    return out, gained


def move(board, direction):
    """Return (new_board, points_gained) after sliding in a direction."""
    if direction == "left":
        rows = [r[:] for r in board]
    elif direction == "right":
        rows = [r[::-1] for r in board]
    elif direction == "up":
        rows = [list(col) for col in zip(*board)]
    else:  # down
        rows = [list(col)[::-1] for col in zip(*board)]

    new_rows, gained = [], 0
    for row in rows:
        new_row, g = slide_left(row)
        new_rows.append(new_row)
        gained += g

    if direction == "left":
        new_board = new_rows
    elif direction == "right":
        new_board = [r[::-1] for r in new_rows]
    elif direction == "up":
        new_board = [list(r) for r in zip(*new_rows)]
    else:
        new_board = [list(r) for r in zip(*[row[::-1] for row in new_rows])]
    return new_board, gained


def spawn(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if not board[r][c]]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 4 if random.random() < 0.1 else 2


def can_move(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
            if c + 1 < SIZE and board[r][c] == board[r][c + 1]:
                return True
            if r + 1 < SIZE and board[r][c] == board[r + 1][c]:
                return True
    return False


def new_board():
    board = [[0] * SIZE for _ in range(SIZE)]
    spawn(board)
    spawn(board)
    return board


# ---------------------------- drawing ----------------------------
def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_score_box(x, label, value):
    box = pygame.Rect(x, 24, 96, 56)
    pygame.draw.rect(screen, PANEL, box, border_radius=10)
    draw_text(label, FONT_LABEL, MUTED, (box.centerx, box.top + 15))
    draw_text(str(value), FONT_SCORE, TEXT, (box.centerx, box.top + 38))


def draw_overlay(lines, color, hint=None):
    veil = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
    pygame.draw.rect(veil, (16, 24, 32, 205), veil.get_rect(), border_radius=12)
    screen.blit(veil, (MARGIN, TOP))
    y = TOP + BOARD_PX // 2 - (len(lines) - 1) * 24
    for line in lines:
        draw_text(line, FONT_BANNER, color, (WIDTH // 2, y))
        y += 48
    if hint:
        draw_text(hint, FONT_HINT, MUTED, (WIDTH // 2, y + 10))


def draw(board, score, best, over, show_win):
    screen.fill(BACKGROUND)

    screen.blit(FONT_TITLE.render("2048", True, TEXT), (MARGIN, 22))
    draw_score_box(WIDTH - MARGIN - 96, "BEST", best)
    draw_score_box(WIDTH - MARGIN - 96 * 2 - 8, "SCORE", score)
    draw_text("Arrow keys / WASD to move  |  R to restart", FONT_HINT, MUTED, (WIDTH // 2, 100))

    pygame.draw.rect(screen, BOARD_BG, (MARGIN, TOP, BOARD_PX, BOARD_PX), border_radius=12)
    for r in range(SIZE):
        for c in range(SIZE):
            rect = pygame.Rect(MARGIN + PAD + c * (CELL + PAD), TOP + PAD + r * (CELL + PAD), CELL, CELL)
            value = board[r][c]
            if not value:
                pygame.draw.rect(screen, EMPTY, rect, border_radius=8)
                continue
            color = TILE_COLORS.get(value, BEYOND_2048)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            size = "big" if value < 100 else "mid" if value < 1000 else "small"
            text_color = DARK_TEXT if value <= 4 else LIGHT_TEXT
            draw_text(str(value), FONT_TILES[size], text_color, rect.center)

    if over:
        draw_overlay(["Game Over!"], TEXT, "Press R to restart")
    elif show_win:
        draw_overlay(["You made 2048!", "Keep going..."], GOLD)


def main():
    board = new_board()
    score = 0
    best = 0
    won = False
    win_banner_until = 0
    over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board, score, won, over, win_banner_until = new_board(), 0, False, False, 0
                elif not over and event.key in KEY_DIRECTIONS:
                    moved, gained = move(board, KEY_DIRECTIONS[event.key])
                    if moved != board:  # something actually slid
                        board = moved
                        score += gained
                        best = max(best, score)
                        spawn(board)
                        if not won and any(v >= 2048 for row in board for v in row):
                            won = True
                            win_banner_until = pygame.time.get_ticks() + 1500
                        if not can_move(board):
                            over = True

        show_win = pygame.time.get_ticks() < win_banner_until
        draw(board, score, best, over, show_win)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()