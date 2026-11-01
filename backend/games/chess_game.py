import pygame
import sys
import copy
import random

# Initialize Pygame
pygame.init()

# Constants
SQUARE_SIZE = 72
BOARD_SIZE = SQUARE_SIZE * 8
TOP_BAR = 56
WIDTH = BOARD_SIZE
HEIGHT = BOARD_SIZE + TOP_BAR
FPS = 30

# Colors
LIGHT_SQ = (238, 238, 210)
DARK_SQ = (118, 150, 86)
HIGHLIGHT_SQ = (186, 202, 43)
LAST_MOVE_SQ = (246, 246, 105)
CHECK_SQ = (239, 68, 68)
TOP_BG = (24, 32, 44)
WHITE_PIECE = (248, 250, 252)
BLACK_PIECE = (30, 41, 59)
OUTLINE = (15, 23, 42)
GOLD = (250, 204, 21)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 18, bold=True)
small_font = pygame.font.SysFont("Helvetica", 13, bold=True)


def create_initial_board():
    return [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ]


def draw_piece(surface, piece, r, c):
    if not piece:
        return
    color = WHITE_PIECE if piece[0] == "w" else BLACK_PIECE
    stroke = BLACK_PIECE if piece[0] == "w" else (203, 213, 225)
    kind = piece[1]

    cx = c * SQUARE_SIZE + SQUARE_SIZE // 2
    cy = r * SQUARE_SIZE + TOP_BAR + SQUARE_SIZE // 2

    # Base pedestal for all pieces
    base_rect = pygame.Rect(cx - 20, cy + 16, 40, 8)
    pygame.draw.rect(surface, color, base_rect, border_radius=3)
    pygame.draw.rect(surface, stroke, base_rect, 2, border_radius=3)

    if kind == "P":  # Pawn
        pygame.draw.polygon(surface, color, [(cx - 14, cy + 16), (cx + 14, cy + 16), (cx + 7, cy - 4), (cx - 7, cy - 4)])
        pygame.draw.polygon(surface, stroke, [(cx - 14, cy + 16), (cx + 14, cy + 16), (cx + 7, cy - 4), (cx - 7, cy - 4)], 2)
        pygame.draw.circle(surface, color, (cx, cy - 11), 10)
        pygame.draw.circle(surface, stroke, (cx, cy - 11), 10, 2)

    elif kind == "R":  # Rook
        body = pygame.Rect(cx - 14, cy - 8, 28, 24)
        pygame.draw.rect(surface, color, body)
        pygame.draw.rect(surface, stroke, body, 2)
        for offset in (-12, -2, 8):
            tooth = pygame.Rect(cx + offset, cy - 16, 6, 8)
            pygame.draw.rect(surface, color, tooth)
            pygame.draw.rect(surface, stroke, tooth, 2)

    elif kind == "N":  # Knight
        pts = [
            (cx - 14, cy + 16),
            (cx + 14, cy + 16),
            (cx + 12, cy - 4),
            (cx + 4, cy - 18),
            (cx - 4, cy - 22),
            (cx - 18, cy - 8),
            (cx - 6, cy - 4),
            (cx - 12, cy + 6),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, stroke, pts, 2)
        pygame.draw.circle(surface, stroke, (cx - 7, cy - 12), 2)

    elif kind == "B":  # Bishop
        pygame.draw.ellipse(surface, color, (cx - 14, cy - 16, 28, 34))
        pygame.draw.ellipse(surface, stroke, (cx - 14, cy - 16, 28, 34), 2)
        pygame.draw.circle(surface, color, (cx, cy - 20), 4)
        pygame.draw.circle(surface, stroke, (cx, cy - 20), 4, 2)
        pygame.draw.line(surface, stroke, (cx - 5, cy - 5), (cx + 5, cy + 5), 2)
        pygame.draw.line(surface, stroke, (cx + 5, cy - 5), (cx - 5, cy + 5), 2)

    elif kind == "Q":  # Queen
        pts = [
            (cx - 16, cy + 16),
            (cx - 22, cy - 12),
            (cx - 8, cy + 2),
            (cx, cy - 16),
            (cx + 8, cy + 2),
            (cx + 22, cy - 12),
            (cx + 16, cy + 16),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, stroke, pts, 2)
        for px, py in [(cx - 22, cy - 14), (cx, cy - 18), (cx + 22, cy - 14)]:
            pygame.draw.circle(surface, GOLD, (px, py), 3)

    elif kind == "K":  # King
        pts = [(cx - 15, cy + 16), (cx - 18, cy - 8), (cx, cy - 14), (cx + 18, cy - 8), (cx + 15, cy + 16)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, stroke, pts, 2)
        # Cross on top
        pygame.draw.line(surface, GOLD, (cx, cy - 26), (cx, cy - 12), 4)
        pygame.draw.line(surface, GOLD, (cx - 7, cy - 20), (cx + 7, cy - 20), 4)


def get_pseudo_moves(board, r, c):
    piece = board[r][c]
    if not piece:
        return []
    color, kind = piece[0], piece[1]
    enemy = "b" if color == "w" else "w"
    moves = []

    if kind == "P":
        step = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1
        # Forward 1
        if 0 <= r + step < 8 and board[r + step][c] == "":
            moves.append((r + step, c))
            # Forward 2 from start
            if r == start_row and board[r + 2 * step][c] == "":
                moves.append((r + 2 * step, c))
        # Captures
        for dc in (-1, 1):
            nr, nc = r + step, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc].startswith(enemy):
                moves.append((nr, nc))

    elif kind == "N":
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and not board[nr][nc].startswith(color):
                moves.append((nr, nc))

    elif kind == "K":
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and not board[nr][nc].startswith(color):
                    moves.append((nr, nc))

    else:
        dirs = []
        if kind in ("R", "Q"):
            dirs.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
        if kind in ("B", "Q"):
            dirs.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == "":
                    moves.append((nr, nc))
                elif board[nr][nc].startswith(enemy):
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc

    return moves


def find_king(board, color):
    target = color + "K"
    for r in range(8):
        for c in range(8):
            if board[r][c] == target:
                return (r, c)
    return None


def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return True
    enemy = "b" if color == "w" else "w"
    for r in range(8):
        for c in range(8):
            if board[r][c].startswith(enemy):
                if king_pos in get_pseudo_moves(board, r, c):
                    return True
    return False


def make_move(board, start, end):
    new_b = [row[:] for row in board]
    sr, sc = start
    er, ec = end
    piece = new_b[sr][sc]
    new_b[er][ec] = piece
    new_b[sr][sc] = ""
    # Auto-promote pawns to Queen
    if piece == "wP" and er == 0:
        new_b[er][ec] = "wQ"
    elif piece == "bP" and er == 7:
        new_b[er][ec] = "bQ"
    return new_b


def get_legal_moves(board, r, c):
    piece = board[r][c]
    if not piece:
        return []
    color = piece[0]
    legal = []
    for er, ec in get_pseudo_moves(board, r, c):
        test_board = make_move(board, (r, c), (er, ec))
        if not is_in_check(test_board, color):
            legal.append((er, ec))
    return legal


def get_all_legal_moves(board, color):
    all_moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c].startswith(color):
                for er, ec in get_legal_moves(board, r, c):
                    all_moves.append(((r, c), (er, ec)))
    return all_moves


def choose_ai_move(board):
    moves = get_all_legal_moves(board, "b")
    if not moves:
        return None
    piece_values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 100}
    best_score = -999
    best_moves = []
    for start, end in moves:
        target = board[end[0]][end[1]]
        score = piece_values.get(target[1], 0) if target else 0
        if score > best_score:
            best_score = score
            best_moves = [(start, end)]
        elif score == best_score:
            best_moves.append((start, end))
    return random.choice(best_moves)


def main():
    board = create_initial_board()
    turn = "w"
    selected = None
    legal_moves = []
    last_move = None
    vs_ai = True
    game_over_msg = None

    while True:
        # AI Turn (Black)
        if vs_ai and turn == "b" and not game_over_msg:
            pygame.time.delay(250)
            ai_choice = choose_ai_move(board)
            if ai_choice:
                board = make_move(board, ai_choice[0], ai_choice[1])
                last_move = ai_choice
                turn = "w"
                if not get_all_legal_moves(board, "w"):
                    game_over_msg = "Checkmate! Black Wins!" if is_in_check(board, "w") else "Stalemate! Draw!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return main()
                elif event.key == pygame.K_a:
                    vs_ai = not vs_ai
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over_msg:
                mx, my = event.pos
                if my >= TOP_BAR:
                    c = mx // SQUARE_SIZE
                    r = (my - TOP_BAR) // SQUARE_SIZE
                    if selected and (r, c) in legal_moves:
                        board = make_move(board, selected, (r, c))
                        last_move = (selected, (r, c))
                        selected = None
                        legal_moves = []
                        turn = "b" if turn == "w" else "w"

                        if not get_all_legal_moves(board, turn):
                            winner = "White" if turn == "b" else "Black"
                            game_over_msg = f"Checkmate! {winner} Wins!" if is_in_check(board, turn) else "Stalemate! Draw!"
                    elif board[r][c].startswith(turn):
                        selected = (r, c)
                        legal_moves = get_legal_moves(board, r, c)
                    else:
                        selected = None
                        legal_moves = []

        # --- DRAWING ---
        screen.fill(TOP_BG)

        # Top Bar Info
        turn_str = "White's Turn" if turn == "w" else "Black's Turn"
        mode_str = "Mode: vs AI (Press A)" if vs_ai else "Mode: 2-Player (Press A)"
        header = font.render(f"{turn_str}   |   {mode_str}   |   R: Restart", True, WHITE_PIECE)
        screen.blit(header, (16, 17))

        # Draw Board Squares
        king_in_check = find_king(board, turn) if is_in_check(board, turn) else None

        for r in range(8):
            for c in range(8):
                sq_color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                if selected == (r, c):
                    sq_color = HIGHLIGHT_SQ
                elif last_move and ((r, c) == last_move[0] or (r, c) == last_move[1]):
                    sq_color = LAST_MOVE_SQ
                if king_in_check == (r, c):
                    sq_color = CHECK_SQ

                rect = (c * SQUARE_SIZE, r * SQUARE_SIZE + TOP_BAR, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, sq_color, rect)

                # Draw Legal Move Indicators
                if (r, c) in legal_moves:
                    cx = c * SQUARE_SIZE + SQUARE_SIZE // 2
                    cy = r * SQUARE_SIZE + TOP_BAR + SQUARE_SIZE // 2
                    if board[r][c] == "":
                        pygame.draw.circle(screen, (100, 116, 139), (cx, cy), 8)
                    else:
                        pygame.draw.circle(screen, CHECK_SQ, (cx, cy), SQUARE_SIZE // 2 - 4, 4)

                # Draw Piece
                draw_piece(screen, board[r][c], r, c)

        # Game Over Overlay
        if game_over_msg:
            msg_surf = font.render(f"{game_over_msg} (Press R to Restart)", True, WHITE_PIECE)
            rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, TOP_BG, rect.inflate(32, 28), border_radius=8)
            pygame.draw.rect(screen, GOLD, rect.inflate(32, 28), width=2, border_radius=8)
            screen.blit(msg_surf, rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()