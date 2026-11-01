import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 420, 650
FPS = 60

# Colors
GRASS_COLOR = (22, 101, 52)
ROAD_COLOR = (51, 65, 85)
LINE_WHITE = (248, 250, 252)
CURB_RED = (239, 68, 68)
PLAYER_COLOR = (239, 68, 68)
ENEMY_COLORS = [(59, 130, 246), (250, 204, 21), (168, 85, 247), (34, 197, 94)]
WINDOW_COLOR = (15, 23, 42)
WHEEL_COLOR = (15, 15, 15)

ROAD_X = 60
ROAD_W = 300
LANE_W = ROAD_W // 3
CAR_W, CAR_H = 46, 84

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Highway Car Racing")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 20, bold=True)


def draw_car(x, y, color, is_player=False):
    # Tires
    for wx in (x - 4, x + CAR_W - 4):
        for wy in (y + 12, y + CAR_H - 26):
            pygame.draw.rect(screen, WHEEL_COLOR, (wx, wy, 8, 16), border_radius=3)

    # Main chassis
    pygame.draw.rect(screen, color, (x, y, CAR_W, CAR_H), border_radius=10)

    # Roof & Windshield
    pygame.draw.rect(screen, WINDOW_COLOR, (x + 6, y + 18, CAR_W - 12, 46), border_radius=6)
    pygame.draw.rect(screen, color, (x + 9, y + 30, CAR_W - 18, 22), border_radius=4)

    # Headlights
    light_y = y + 2 if is_player else y + CAR_H - 6
    pygame.draw.rect(screen, (254, 240, 138), (x + 6, light_y, 10, 4), border_radius=2)
    pygame.draw.rect(screen, (254, 240, 138), (x + CAR_W - 16, light_y, 10, 4), border_radius=2)


def main():
    player_lane = 1  # 0 = left, 1 = middle, 2 = right
    player_x = ROAD_X + player_lane * LANE_W + (LANE_W - CAR_W) // 2
    player_y = HEIGHT - 120
    enemies = []
    road_offset = 0
    speed = 7
    score = 0
    spawn_timer = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return main()
                elif not game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        player_lane = max(0, player_lane - 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        player_lane = min(2, player_lane + 1)

        if not game_over:
            player_x = ROAD_X + player_lane * LANE_W + (LANE_W - CAR_W) // 2

            road_offset = (road_offset + speed) % 60
            spawn_timer += 1

            # Spawn incoming traffic
            if spawn_timer > max(26, 60 - int(speed * 2)):
                spawn_timer = 0
                lane = random.randint(0, 2)
                ex = ROAD_X + lane * LANE_W + (LANE_W - CAR_W) // 2
                enemies.append({
                    "x": ex,
                    "y": -CAR_H,
                    "color": random.choice(ENEMY_COLORS),
                })

            player_rect = pygame.Rect(player_x + 4, player_y + 4, CAR_W - 8, CAR_H - 8)

            for e in enemies[:]:
                e["y"] += speed * 0.85
                enemy_rect = pygame.Rect(e["x"] + 4, e["y"] + 4, CAR_W - 8, CAR_H - 8)
                if player_rect.colliderect(enemy_rect):
                    game_over = True
                if e["y"] > HEIGHT:
                    enemies.remove(e)
                    score += 1
                    speed = min(15, 7 + score * 0.2)

        # --- DRAWING ---
        screen.fill(GRASS_COLOR)
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_X, 0, ROAD_W, HEIGHT))

        # Red & White Curbs
        for y in range(-60, HEIGHT, 60):
            curb_y = y + road_offset
            pygame.draw.rect(screen, CURB_RED, (ROAD_X - 10, curb_y, 10, 30))
            pygame.draw.rect(screen, LINE_WHITE, (ROAD_X - 10, curb_y + 30, 10, 30))
            pygame.draw.rect(screen, CURB_RED, (ROAD_X + ROAD_W, curb_y, 10, 30))
            pygame.draw.rect(screen, LINE_WHITE, (ROAD_X + ROAD_W, curb_y + 30, 10, 30))

        # Dashed Lane Dividers
        for lane in (1, 2):
            lx = ROAD_X + lane * LANE_W
            for y in range(-60, HEIGHT, 60):
                pygame.draw.rect(screen, LINE_WHITE, (lx - 3, y + road_offset, 6, 32))

        # Cars
        for e in enemies:
            draw_car(e["x"], int(e["y"]), e["color"], is_player=False)
        draw_car(player_x, player_y, PLAYER_COLOR, is_player=True)

        # Score HUD
        score_surf = font.render(f"Score: {score}", True, LINE_WHITE)
        screen.blit(score_surf, (16, 16))

        if game_over:
            msg = font.render("Crash! Press R to Restart", True, LINE_WHITE)
            rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, WINDOW_COLOR, rect.inflate(28, 24), border_radius=8)
            pygame.draw.rect(screen, PLAYER_COLOR, rect.inflate(28, 24), 2, border_radius=8)
            screen.blit(msg, rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()