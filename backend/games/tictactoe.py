"""Tic Tac Toe - click the menu to pick a mode, then click squares. R = new round, M = menu."""
import random
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 420, 580
FPS = 30
COMPUTER_DELAY_MS = 500

BG = (30, 30, 46)
PANEL = (49, 50, 68)
CELL_COLOR = (69, 71, 90)
X_COLOR = (137, 180, 250)
O_COLOR = (243, 139, 168)
WIN_COLOR = (166, 227, 161)
TEXT = (205, 214, 244)
MUTED = (166, 173, 200)

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]

CELL = 110
GAP = 8
BOARD_X = (WIDTH - (3 * CELL + 2 * GAP)) // 2
BOARD_Y = 170
NEW_ROUND_BTN = pygame.Rect(BOARD_X, 528, 165, 42)
MENU_BTN = pygame.Rect(BOARD_X + 165 + 16, 528, 165, 42)
ONE_PLAYER_BTN = pygame.Rect((WIDTH - 320) // 2, 340, 320, 58)
TWO_PLAYER_BTN = pygame.Rect((WIDTH - 320) // 2, 420, 320, 58)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

FONT_TITLE = pygame.font.SysFont("Helvetica", 40, bold=True)
FONT_STATUS = pygame.font.SysFont("Helvetica", 24, bold=True)
FONT_SCORE = pygame.font.SysFont("Helvetica", 30, bold=True)
FONT_LABEL = pygame.font.SysFont("Helvetica", 13, bold=True)
FONT_BUTTON = pygame.font.SysFont("Helvetica", 20, bold=True)
FONT_SMALL = pygame.font.SysFont("Helvetica", 18)


def cell_rect(i):
    row, col = divmod(i, 3)
    return pygame.Rect(BOARD_X + col * (CELL + GAP), BOARD_Y + row * (CELL + GAP), CELL, CELL)


def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=12)
    draw_text(text, FONT_BUTTON, BG, rect.center)


def draw_symbol(rect, symbol, color, pad=28):
    if symbol == "X":
        pygame.draw.line(screen, color, (rect.left + pad, rect.top + pad), (rect.right - pad, rect.bottom - pad), 10)
        pygame.draw.line(screen, color, (rect.right - pad, rect.top + pad), (rect.left + pad, rect.bottom - pad), 10)
    else:
        pygame.draw.circle(screen, color, rect.center, (rect.width - 2 * pad) // 2 + 2, 10)


class TicTacToe:
    def __init__(self):
        self.screen_name = "menu"      # "menu" or "game"
        self.single_player = True
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.reset_round()

    # ---------------------------- game logic ----------------------------
    def start_game(self, single_player):
        self.single_player = single_player
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.screen_name = "game"
        self.reset_round()

    def reset_round(self):
        self.board = [""] * 9
        self.current = "X"
        self.game_over = False
        self.win_line = None
        self.result = None            # text shown when the round ends
        self.computer_at = None       # time (ms) when the computer will play

    def find_winner(self):
        for a, b, c in WIN_LINES:
            if self.board[a] != "" and self.board[a] == self.board[b] == self.board[c]:
                return (a, b, c)
        return None

    def make_move(self, n):
        self.board[n] = self.current
        line = self.find_winner()
        if line:
            self.end_round(line)
            return
        if "" not in self.board:
            self.end_round(None)
            return
        self.current = "O" if self.current == "X" else "X"
        if self.single_player and self.current == "O":
            self.computer_at = pygame.time.get_ticks() + COMPUTER_DELAY_MS

    def end_round(self, line):
        self.game_over = True
        self.computer_at = None
        self.win_line = line
        if line:
            winner = self.board[line[0]]
            self.scores[winner] += 1
            if self.single_player:
                self.result = ("You win!" if winner == "X" else "Computer wins!", WIN_COLOR)
            else:
                self.result = (f"Player {winner} wins!", WIN_COLOR)
        else:
            self.scores["Draw"] += 1
            self.result = ("It's a draw!", MUTED)

    def computer_move(self):
        free = [i for i in range(9) if self.board[i] == ""]
        # 1) win if possible, 2) block the human, 3) take the centre, 4) random
        for player in ("O", "X"):
            for n in free:
                self.board[n] = player
                wins = self.find_winner() is not None
                self.board[n] = ""
                if wins:
                    self.make_move(n)
                    return
        self.make_move(4 if 4 in free else random.choice(free))

    def update(self):
        if self.computer_at is not None and not self.game_over and pygame.time.get_ticks() >= self.computer_at:
            self.computer_at = None
            self.computer_move()

    # ---------------------------- input ----------------------------
    def handle_click(self, pos):
        if self.screen_name == "menu":
            if ONE_PLAYER_BTN.collidepoint(pos):
                self.start_game(True)
            elif TWO_PLAYER_BTN.collidepoint(pos):
                self.start_game(False)
            return
        if NEW_ROUND_BTN.collidepoint(pos):
            self.reset_round()
        elif MENU_BTN.collidepoint(pos):
            self.screen_name = "menu"
        elif not self.game_over and not (self.single_player and self.current == "O"):
            for i in range(9):
                if self.board[i] == "" and cell_rect(i).collidepoint(pos):
                    self.make_move(i)
                    break

    def handle_key(self, key):
        if self.screen_name != "game":
            return
        if key == pygame.K_r:
            self.reset_round()
        elif key == pygame.K_m:
            self.screen_name = "menu"

    # ---------------------------- drawing ----------------------------
    def draw_menu(self):
        draw_text("TIC TAC TOE", FONT_TITLE, TEXT, (WIDTH // 2, 80))
        draw_symbol(pygame.Rect(WIDTH // 2 - 120, 130, 100, 100), "X", X_COLOR, pad=22)
        draw_symbol(pygame.Rect(WIDTH // 2 + 20, 130, 100, 100), "O", O_COLOR, pad=22)
        draw_text("Choose a game mode", FONT_SMALL, MUTED, (WIDTH // 2, 295))
        draw_button(ONE_PLAYER_BTN, "1 Player  (vs Computer)", X_COLOR)
        draw_button(TWO_PLAYER_BTN, "2 Players  (Local)", O_COLOR)

    def draw_game(self):
        names = {"X": "YOU (X)" if self.single_player else "PLAYER X",
                 "Draw": "DRAWS",
                 "O": "COMPUTER (O)" if self.single_player else "PLAYER O"}
        colors = {"X": X_COLOR, "Draw": MUTED, "O": O_COLOR}
        for i, key in enumerate(("X", "Draw", "O")):
            box = pygame.Rect(20 + i * 130, 20, 120, 70)
            pygame.draw.rect(screen, PANEL, box, border_radius=10)
            draw_text(names[key], FONT_LABEL, colors[key], (box.centerx, box.top + 18))
            draw_text(str(self.scores[key]), FONT_SCORE, TEXT, (box.centerx, box.top + 46))

        if self.game_over:
            text, color = self.result
        elif self.single_player:
            text = "Your turn" if self.current == "X" else "Computer is thinking..."
            color = X_COLOR if self.current == "X" else O_COLOR
        else:
            text = f"Player {self.current}'s turn"
            color = X_COLOR if self.current == "X" else O_COLOR
        draw_text(text, FONT_STATUS, color, (WIDTH // 2, 130))

        for i in range(9):
            rect = cell_rect(i)
            winning = self.win_line is not None and i in self.win_line
            pygame.draw.rect(screen, WIN_COLOR if winning else CELL_COLOR, rect, border_radius=12)
            if self.board[i]:
                symbol_color = BG if winning else (X_COLOR if self.board[i] == "X" else O_COLOR)
                draw_symbol(rect, self.board[i], symbol_color)

        draw_button(NEW_ROUND_BTN, "New Round", WIN_COLOR)
        draw_button(MENU_BTN, "Menu", MUTED)

    def draw(self):
        screen.fill(BG)
        if self.screen_name == "menu":
            self.draw_menu()
        else:
            self.draw_game()


def main():
    game = TicTacToe()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()