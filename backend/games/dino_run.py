import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 750, 320
GROUND_Y = 250
FPS = 60

# Classic Chrome Monochrome Palette
BG_COLOR = (247, 247, 247)
DINO_COLOR = (83, 83, 83)
LIGHT_GRAY = (190, 190, 190)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dino Run")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 20, bold=True)


def draw_dino(x, y, ducking, tick):
    leg_step = (tick // 5) % 2 == 0
    if ducking:
        # Ducking posture (wider and lower)
        pygame.draw.rect(screen, DINO_COLOR, (x, y + 18, 52, 18), border_radius=3)
        pygame.draw.rect(screen, DINO_COLOR, (x + 36, y + 12, 22, 16), border_radius=2)
        pygame.draw.circle(screen, BG_COLOR, (x + 50, y + 16), 2)  # Eye
    else:
        # Standing T-Rex Head, Body, Tail, and Tiny Arm
        pygame.draw.rect(screen, DINO_COLOR, (x + 18, y, 24, 18), border_radius=2)
        pygame.draw.circle(screen, BG_COLOR, (x + 34, y + 5), 2)  # Eye
        pygame.draw.rect(screen, DINO_COLOR, (x + 8, y + 14, 22, 22), border_radius=2)
        pygame.draw.polygon(screen, DINO_COLOR, [(x, y + 18), (x + 8, y + 20), (x + 8, y + 32)])
        pygame.draw.rect(screen, DINO_COLOR, (x + 30, y + 20, 7, 4))

    # Animated Running Legs
    if y < GROUND_Y - 44:  # In mid-air
        pygame.draw.rect(screen, DINO_COLOR, (x + 12, y + 36, 5, 8))
        pygame.draw.rect(screen, DINO_COLOR, (x + 22, y + 36, 5, 8))
    else:
        h1, h2 = (8, 4) if leg_step else (4, 8)
        pygame.draw.rect(screen, DINO_COLOR, (x + 12, y + 36, 5, h1))
        pygame.draw.rect(screen, DINO_COLOR, (x + 22, y + 36, 5, h2))


def draw_cactus(x, h, w):
    top = GROUND_Y - h
    # Main trunk
    pygame.draw.rect(screen, DINO_COLOR, (x + 6, top, w - 12, h), border_radius=3)
    # Left & Right Cactus Arms
    pygame.draw.rect(screen, DINO_COLOR, (x, top + 10, 6, 14), border_radius=2)
    pygame.draw.rect(screen, DINO_COLOR, (x + w - 6, top + 6, 6, 16), border_radius=2)


def draw_ptero(x, y, tick):
    wing_up = (tick // 8) % 2 == 0
    # Body & Beak
    pygame.draw.rect(screen, DINO_COLOR, (x + 8, y + 10, 26, 8))
    pygame.draw.polygon(screen, DINO_COLOR, [(x, y + 14), (x + 8, y + 10), (x + 8, y + 16)])
    # Flapping Wing
    if wing_up:
        pygame.draw.polygon(screen, DINO_COLOR, [(x + 14, y + 10), (x + 20, y), (x + 26, y + 10)])
    else:
        pygame.draw.polygon(screen, DINO_COLOR, [(x + 14, y + 16), (x + 20, y + 26), (x + 26, y + 16)])


def main():
    dino_x = 65
    dino_y = GROUND_Y - 44
    dino_vel = 0
    gravity = 0.85
    ducking = False

    obstacles = []
    pebbles = [(random.randint(0, WIDTH), GROUND_Y + random.randint(4, 14)) for _ in range(18)]
    speed = 7.5
    score = 0.0
    tick = 0
    spawn_timer = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    if dino_y >= GROUND_Y - 44:
                        dino_vel = -14.5
                elif event.key == pygame.K_r and game_over:
                    return main()

        keys = pygame.key.get_pressed()
        ducking = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and dino_y >= GROUND_Y - 44

        if not game_over:
            tick += 1
            score += 0.15
            speed = min(15.0, 7.5 + score * 0.008)

            # Jump Physics
            dino_y += dino_vel
            if dino_y < GROUND_Y - 44:
                dino_vel += gravity
            else:
                dino_y = GROUND_Y - 44
                dino_vel = 0

            # Spawn Obstacles (Cacti & Flying Pterodactyls)
            spawn_timer += 1
            if spawn_timer > random.randint(48, 95):
                spawn_timer = 0
                if score > 120 and random.random() < 0.35:
                    # High or mid-level bird (requires ducking or jumping)
                    bird_y = random.choice([GROUND_Y - 68, GROUND_Y - 42])
                    obstacles.append({"type": "ptero", "x": WIDTH, "y": bird_y, "w": 36, "h": 24})
                else:
                    ch = random.choice([36, 46, 50])
                    cw = random.choice([24, 34])
                    obstacles.append({"type": "cactus", "x": WIDTH, "y": GROUND_Y - ch, "w": cw, "h": ch})

            # Hitbox shrinks vertically when ducking
            if ducking:
                dino_rect = pygame.Rect(dino_x + 4, int(dino_y) + 18, 46, 24)
            else:
                dino_rect = pygame.Rect(dino_x + 6, int(dino_y) + 4, 30, 38)

            for obs in obstacles[:]:
                obs["x"] -= speed
                obs_rect = pygame.Rect(int(obs["x"]) + 4, obs["y"] + 4, obs["w"] - 8, obs["h"] - 6)
                if dino_rect.colliderect(obs_rect):
                    game_over = True
                if obs["x"] < -60:
                    obstacles.remove(obs)

            # Scroll ground pebbles
            pebbles = [((px - speed) % WIDTH, py) for px, py in pebbles]

        # --- DRAWING ---
        screen.fill(BG_COLOR)

        # Desert Horizon & Pebbles
        pygame.draw.line(screen, DINO_COLOR, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
        for px, py in pebbles:
            pygame.draw.rect(screen, LIGHT_GRAY, (int(px), py, 4, 2))

        # Obstacles
        for obs in obstacles:
            if obs["type"] == "cactus":
                draw_cactus(int(obs["x"]), obs["h"], obs["w"])
            else:
                draw_ptero(int(obs["x"]), obs["y"], tick)

        # Dino
        draw_dino(dino_x, int(dino_y), ducking, tick)

        # Score Display (5-digit padded like Chrome)
        score_surf = font.render(f"HI  {int(score):05d}", True, DINO_COLOR)
        screen.blit(score_surf, (WIDTH - 150, 20))

        if game_over:
            over_surf = font.render("G A M E   O V E R   (Press R to Restart)", True, DINO_COLOR)
            screen.blit(over_surf, (WIDTH // 2 - over_surf.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()