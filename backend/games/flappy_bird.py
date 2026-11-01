import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 420, 620
GROUND_Y = HEIGHT - 70
FPS = 60

# Colors
SKY_BLUE = (112, 197, 206)
CLOUD_WHITE = (236, 254, 255)
GROUND_TAN = (222, 216, 149)
GRASS_GREEN = (115, 191, 46)
PIPE_GREEN = (84, 168, 40)
PIPE_BORDER = (43, 89, 19)
BIRD_YELLOW = (250, 204, 21)
BEAK_ORANGE = (249, 115, 22)
WHITE = (255, 255, 255)
DARK = (15, 23, 42)

PIPE_W = 64
PIPE_GAP = 145

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 28, bold=True)
small_font = pygame.font.SysFont("Helvetica", 20, bold=True)


def draw_bird(x, y, vel):
    # Body & Outline
    pygame.draw.circle(screen, BIRD_YELLOW, (x, int(y)), 16)
    pygame.draw.circle(screen, DARK, (x, int(y)), 16, 2)

    # Flapping Wing
    wing_offset = 4 if vel < 0 else -2
    pygame.draw.ellipse(screen, WHITE, (x - 12, int(y) + wing_offset, 14, 9))
    pygame.draw.ellipse(screen, DARK, (x - 12, int(y) + wing_offset, 14, 9), 2)

    # Eye
    pygame.draw.circle(screen, WHITE, (x + 6, int(y) - 5), 5)
    pygame.draw.circle(screen, DARK, (x + 8, int(y) - 5), 2)

    # Beak
    beak = [(x + 12, int(y) - 2), (x + 22, int(y) + 2), (x + 12, int(y) + 6)]
    pygame.draw.polygon(screen, BEAK_ORANGE, beak)
    pygame.draw.polygon(screen, DARK, beak, 2)


def draw_pipe(x, top_h):
    bottom_y = top_h + PIPE_GAP
    bottom_h = GROUND_Y - bottom_y

    # Top Pipe & Lip
    pygame.draw.rect(screen, PIPE_GREEN, (x, 0, PIPE_W, top_h))
    pygame.draw.rect(screen, PIPE_BORDER, (x, 0, PIPE_W, top_h), 3)
    pygame.draw.rect(screen, PIPE_GREEN, (x - 4, top_h - 24, PIPE_W + 8, 24))
    pygame.draw.rect(screen, PIPE_BORDER, (x - 4, top_h - 24, PIPE_W + 8, 24), 3)

    # Bottom Pipe & Lip
    pygame.draw.rect(screen, PIPE_GREEN, (x, bottom_y, PIPE_W, bottom_h))
    pygame.draw.rect(screen, PIPE_BORDER, (x, bottom_y, PIPE_W, bottom_h), 3)
    pygame.draw.rect(screen, PIPE_GREEN, (x - 4, bottom_y, PIPE_W + 8, 24))
    pygame.draw.rect(screen, PIPE_BORDER, (x - 4, bottom_y, PIPE_W + 8, 24), 3)


def main():
    bird_x = 100
    bird_y = HEIGHT // 2 - 40
    bird_vel = 0
    gravity = 0.42
    flap_power = -7.8

    pipes = [{"x": WIDTH + 40, "top": random.randint(80, GROUND_Y - PIPE_GAP - 80), "passed": False}]
    score = 0
    started = False
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    started = True
                    bird_vel = flap_power
                elif event.key == pygame.K_r and game_over:
                    return main()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                started = True
                bird_vel = flap_power

        if started and not game_over:
            bird_vel += gravity
            bird_y += bird_vel

            # Spawn new pipes
            if pipes[-1]["x"] < WIDTH - 210:
                pipes.append({
                    "x": WIDTH,
                    "top": random.randint(70, GROUND_Y - PIPE_GAP - 70),
                    "passed": False,
                })

            bird_rect = pygame.Rect(bird_x - 13, int(bird_y) - 13, 26, 26)

            for p in pipes[:]:
                p["x"] -= 3.2
                top_rect = pygame.Rect(p["x"], 0, PIPE_W, p["top"])
                bot_rect = pygame.Rect(p["x"], p["top"] + PIPE_GAP, PIPE_W, GROUND_Y - (p["top"] + PIPE_GAP))

                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
                    game_over = True

                if not p["passed"] and p["x"] + PIPE_W < bird_x:
                    p["passed"] = True
                    score += 1

                if p["x"] < -PIPE_W - 10:
                    pipes.remove(p)

            if bird_y + 16 >= GROUND_Y or bird_y - 16 <= 0:
                game_over = True

        # --- DRAWING ---
        screen.fill(SKY_BLUE)

        # Background Clouds
        for cx, cy in [(80, 110), (260, 80), (350, 150)]:
            pygame.draw.circle(screen, CLOUD_WHITE, (cx, cy), 24)
            pygame.draw.circle(screen, CLOUD_WHITE, (cx + 20, cy + 4), 20)
            pygame.draw.circle(screen, CLOUD_WHITE, (cx - 20, cy + 4), 18)

        # Pipes
        for p in pipes:
            draw_pipe(int(p["x"]), p["top"])

        # Ground & Grass Strip
        pygame.draw.rect(screen, GROUND_TAN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, WIDTH, 14))
        pygame.draw.line(screen, DARK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

        # Bird
        draw_bird(bird_x, bird_y, bird_vel)

        # Score
        score_surf = font.render(str(score), True, WHITE)
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 24))

        if not started and not game_over:
            hint = small_font.render("Press SPACE or Click to Flap", True, DARK)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 50))

        if game_over:
            msg = small_font.render("Game Over! Press R to Restart", True, WHITE)
            rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK, rect.inflate(28, 24), border_radius=8)
            screen.blit(msg, rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()