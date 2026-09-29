import argparse
import json
import sys
import time

import pygame
import serial
from serial.tools import list_ports

WIDTH, HEIGHT, GROUND_Y, BAUD = 960, 500, 410, 115200


def find_port(preferred=None):
    ports = list(list_ports.comports())
    if preferred:
        return preferred, ports
    for port in ports:
        label = f"{port.description} {port.hwid}".lower()
        if "ch340" in label or "1a86:7523" in label or "usb-serial" in label:
            return port.device, ports
    return (ports[0].device if len(ports) == 1 else None), ports


def connect(name):
    link = serial.Serial(name, BAUD, timeout=0, write_timeout=0.2)
    time.sleep(2)
    link.reset_input_buffer()
    return link


def draw_dino(screen, x, y, running):
    color = (45, 48, 52)
    pygame.draw.rect(screen, color, (x + 10, y + 14, 31, 29), border_radius=4)
    pygame.draw.rect(screen, color, (x + 27, y, 34, 27), border_radius=4)
    pygame.draw.rect(screen, color, (x, y + 27, 22, 11), border_radius=3)
    pygame.draw.rect(screen, (245, 247, 248), (x + 51, y + 7, 4, 4))
    pygame.draw.rect(screen, color, (x + 17, y + 40, 8, 13 if running else 9))
    pygame.draw.rect(screen, color, (x + 35, y + 40, 8, 9 if running else 13))


def draw_cactus(screen, x, height):
    green = (55, 132, 83)
    top = GROUND_Y - height
    pygame.draw.rect(screen, green, (x + 13, top, 14, height), border_radius=6)
    pygame.draw.rect(screen, green, (x, top + 18, 14, 9), border_radius=4)
    pygame.draw.rect(screen, green, (x, top + 7, 8, 19), border_radius=4)
    pygame.draw.rect(screen, green, (x + 26, top + 28, 13, 9), border_radius=4)
    pygame.draw.rect(screen, green, (x + 32, top + 16, 7, 21), border_radius=4)


def draw_bird(screen, x, kind, wing_up):
    color = (67, 72, 80)
    y = 337 if kind == 1 else 300
    pygame.draw.ellipse(screen, color, (x + 10, y + 8, 37, 18))
    pygame.draw.polygon(screen, color, [(x + 43, y + 10), (x + 62, y + 16), (x + 44, y + 21)])
    pygame.draw.circle(screen, (245, 247, 248), (x + 39, y + 13), 2)
    if wing_up:
        pygame.draw.polygon(screen, color, [(x + 22, y + 12), (x + 5, y - 8), (x + 33, y + 13)])
    else:
        pygame.draw.polygon(screen, color, [(x + 22, y + 17), (x + 7, y + 35), (x + 35, y + 19)])


def draw_tea(screen, x, y):
    pygame.draw.rect(screen, (230, 70, 44), (x + 4, y + 5, 23, 31), border_radius=5)
    pygame.draw.rect(screen, (245, 185, 55), (x + 8, y, 15, 7), border_radius=2)
    pygame.draw.rect(screen, (255, 227, 143), (x + 7, y + 14, 17, 10), border_radius=2)
    pygame.draw.line(screen, (255, 255, 255), (x + 10, y + 28), (x + 21, y + 28), 2)


def draw_plane(screen, x):
    y = 135
    body = (78, 91, 112)
    pygame.draw.ellipse(screen, body, (x, y, 86, 24))
    pygame.draw.polygon(screen, body, [(x + 32, y + 8), (x + 55, y - 13), (x + 67, y + 10)])
    pygame.draw.polygon(screen, body, [(x + 20, y + 14), (x + 46, y + 38), (x + 58, y + 16)])
    pygame.draw.polygon(screen, (221, 76, 55), [(x + 3, y + 7), (x - 13, y - 3), (x + 9, y + 16)])


def draw_stickman(screen, x):
    c = (45, 48, 52)
    pygame.draw.circle(screen, c, (x + 17, 358), 8, 3)
    pygame.draw.line(screen, c, (x + 17, 366), (x + 17, 390), 4)
    pygame.draw.line(screen, c, (x + 17, 373), (x + 31, 380), 3)
    pygame.draw.line(screen, c, (x + 17, 373), (x + 5, 382), 3)
    pygame.draw.line(screen, c, (x + 17, 390), (x + 5, 409), 4)
    pygame.draw.line(screen, c, (x + 17, 390), (x + 30, 409), 4)
    pygame.draw.rect(screen, (90, 94, 101), (x + 27, 376, 17, 6), border_radius=2)


def draw_tank(screen, x):
    pygame.draw.rect(screen, (75, 105, 65), (x, 376, 66, 25), border_radius=5)
    pygame.draw.rect(screen, (89, 122, 73), (x + 15, 363, 35, 18), border_radius=6)
    pygame.draw.rect(screen, (60, 78, 57), (x + 42, 368, 37, 6), border_radius=2)
    pygame.draw.ellipse(screen, (45, 50, 45), (x + 3, 393, 62, 17))
    for wheel in (14, 31, 49):
        pygame.draw.circle(screen, (135, 145, 130), (x + wheel, 401), 6)


def draw_poison(screen, x, pulse):
    pygame.draw.ellipse(screen, (78, 48, 92), (x, 394, 92, 22))
    pygame.draw.ellipse(screen, (113, 224, 72), (x + 5, 397, 82, 14))
    for dx in (20, 46, 70):
        pygame.draw.circle(screen, (190, 255, 120), (x + dx, 399 - (pulse + dx) % 5), 3)


def draw_meteor(screen, x, y, phase, pulse):
    if phase == 1:
        radius = 23 + (pulse % 10)
        pygame.draw.circle(screen, (235, 75, 55), (x, GROUND_Y - 4), radius, 3)
        pygame.draw.circle(screen, (245, 160, 55), (x, GROUND_Y - 4), 8, 2)
    elif phase == 2:
        pygame.draw.line(screen, (255, 149, 45), (x + 12, y - 42), (x, y), 12)
        pygame.draw.circle(screen, (92, 75, 70), (x, y), 19)
        pygame.draw.circle(screen, (235, 92, 48), (x - 5, y - 5), 7)
    elif phase == 3:
        pygame.draw.circle(screen, (82, 68, 64), (x, GROUND_Y - 11), 20)
        flame = 5 + (pulse % 8)
        pygame.draw.polygon(screen, (238, 62, 35), [(x - 35, GROUND_Y), (x - 25, GROUND_Y - 35 - flame), (x - 12, GROUND_Y - 14), (x, GROUND_Y - 46 + flame), (x + 13, GROUND_Y - 13), (x + 28, GROUND_Y - 37 - flame), (x + 38, GROUND_Y)])
        pygame.draw.polygon(screen, (255, 178, 35), [(x - 22, GROUND_Y), (x - 12, GROUND_Y - 24), (x, GROUND_Y - 10), (x + 12, GROUND_Y - 30), (x + 24, GROUND_Y)])


def draw(screen, fonts, state, port, jump_pressed, connected, paused):
    night = bool(state.get("night", 0))
    distance = int(state.get("distance", 0))
    screen.fill((25, 31, 52) if night else (247, 247, 247))
    if night:
        pygame.draw.circle(screen, (240, 235, 182), (850, 72), 30)
        star_shift = (distance // 8) % WIDTH
        for sx, sy in ((90, 55), (190, 100), (310, 48), (480, 90), (620, 42), (735, 118), (910, 135)):
            pygame.draw.circle(screen, (235, 240, 255), ((sx - star_shift) % WIDTH, sy), 2)
    else:
        cloud_shift = (distance // 12) % 1200
        for base_x, base_y in ((180, 90), (620, 125), (1030, 65)):
            cx = (base_x - cloud_shift) % 1200 - 100
            pygame.draw.ellipse(screen, (220, 228, 234), (cx, base_y, 95, 24))
            pygame.draw.circle(screen, (228, 235, 240), (cx + 28, base_y + 3), 22)
            pygame.draw.circle(screen, (228, 235, 240), (cx + 60, base_y + 5), 18)
    ink = (215, 220, 232) if night else (88, 91, 95)
    pygame.draw.line(screen, ink, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
    offset = distance % 80
    for x in range(-offset, WIDTH, 80):
        pygame.draw.line(screen, (145, 160, 195) if night else (170, 173, 176), (x, GROUND_Y + 12), (x + 35, GROUND_Y + 12), 3)
    wing_up = (pygame.time.get_ticks() // 140) % 2 == 0
    for number in (1, 2):
        obstacle_x = int(state.get(f"x{number}", 900 + number * 300))
        kind = int(state.get(f"t{number}", 0))
        if -70 < obstacle_x < WIDTH + 70:
            if kind == 0:
                draw_cactus(screen, obstacle_x, int(state.get(f"h{number}", 50)))
            elif kind == 1:
                draw_bird(screen, obstacle_x, kind, wing_up)
            elif kind == 2:
                draw_stickman(screen, obstacle_x)
            elif kind == 3:
                draw_tank(screen, obstacle_x)
            else:
                draw_poison(screen, obstacle_x, pygame.time.get_ticks() // 120)
    dino_y = int(state.get("y", GROUND_Y - 53))
    draw_dino(screen, 120, dino_y, not state.get("over", 0))
    shield_count = int(state.get("shield", 0))
    if shield_count:
        for layer in range(min(shield_count, 4)):
            pad = layer * 5
            pygame.draw.ellipse(screen, (55 + layer * 25, 150 + layer * 18, 245),
                                (110 - pad, dino_y - 10 - pad, 80 + pad * 2, 75 + pad * 2), 3)
    tea_x = int(state.get("tea", -100))
    if -40 < tea_x < WIDTH + 40:
        draw_tea(screen, tea_x, int(state.get("teay", 320)))
    plane_x = int(state.get("plane", -150))
    if -120 < plane_x < WIDTH + 120:
        draw_plane(screen, plane_x)
    bullet_x = int(state.get("bullet", -100))
    if -20 < bullet_x < WIDTH + 20:
        bullet_y = int(state.get("bullety", 360))
        pygame.draw.ellipse(screen, (210, 55, 45), (bullet_x, bullet_y, 18, 8))
        pygame.draw.line(screen, (245, 155, 55), (bullet_x + 18, bullet_y + 4), (bullet_x + 32, bullet_y + 4), 4)
    enemy_shot_x = int(state.get("eshot", -100))
    if -30 < enemy_shot_x < WIDTH + 30:
        enemy_shot_y = int(state.get("eshoty", 370))
        if int(state.get("eshottype", 0)) == 0:
            pygame.draw.circle(screen, (230, 70, 55), (enemy_shot_x, enemy_shot_y), 5)
        else:
            pygame.draw.circle(screen, (55, 58, 62), (enemy_shot_x, enemy_shot_y), 10)
            pygame.draw.line(screen, (245, 125, 45), (enemy_shot_x + 10, enemy_shot_y), (enemy_shot_x + 25, enemy_shot_y), 5)
    meteor_phase = int(state.get("mphase", 0))
    draw_meteor(screen, int(state.get("meteorx", 500)), int(state.get("meteory", -60)), meteor_phase, pygame.time.get_ticks() // 80)

    title, small, large = fonts
    ui_main = (225, 230, 242) if night else (45, 48, 52)
    ui_muted = (165, 175, 198) if night else (105, 108, 112)
    screen.blit(title.render("UNO DINO", True, ui_main), (24, 20))
    score = int(state.get("score", 0))
    best = int(state.get("best", 0))
    speed = 330.0 + min(360.0, score * 0.35)
    screen.blit(small.render(f"HI {best:05d}   {score:05d}", True, ui_main), (WIDTH - 270, 26))
    screen.blit(small.render(f"SPEED x{speed / 330.0:.2f}", True, ui_main), (WIDTH - 270, 88))
    screen.blit(small.render(f"{port} / 115200", True, ui_muted), (24, 60))
    color = (50, 145, 78) if jump_pressed else (145, 148, 152)
    screen.blit(small.render(f"JUMP INPUT: {int(jump_pressed)}", True, color), (24, 88))
    if shield_count:
        screen.blit(small.render(f"ICE TEA SHIELD x{shield_count}", True, (35, 125, 220)), (WIDTH - 270, 60))
    if state.get("over", 0):
        text = large.render("G A M E   O V E R", True, (55, 58, 62))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, 190)))
        hint = small.render("SPACE / UP / CLICK TO RESTART", True, (80, 83, 87))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 240)))
    else:
        hint = small.render("SPACE/UP/CLICK: JUMP   P: PAUSE   ESC: QUIT", True, ui_muted)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 462)))
    if paused and connected:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((245, 247, 250, 175))
        screen.blit(shade, (0, 0))
        text = large.render("P A U S E D", True, (55, 85, 145))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, 215)))
        hint = small.render("Press P to continue", True, (65, 70, 78))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 260)))
    elif not connected:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((245, 247, 250, 215))
        screen.blit(shade, (0, 0))
        text = large.render("ARDUINO DISCONNECTED", True, (205, 55, 50))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, 205)))
        hint = small.render("Reconnect the Uno - searching for CH340...", True, (65, 70, 78))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 255)))


def main():
    parser = argparse.ArgumentParser(description="Arduino Uno dinosaur runner")
    parser.add_argument("--port", help="serial port, e.g. COM32")
    args = parser.parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Arduino Uno Dino")
    fonts = (pygame.font.SysFont("consolas", 28, bold=True), pygame.font.SysFont("consolas", 18), pygame.font.SysFont("consolas", 34, bold=True))
    clock = pygame.time.Clock()
    state = {"y": GROUND_Y - 53, "x1": 850, "t1": 0, "h1": 50, "x2": 1250, "t2": 2, "h2": 0, "tea": -100, "teay": 320, "shield": 0, "plane": -150, "bullet": -100, "bullety": 360, "eshot": -100, "eshoty": 370, "eshottype": 0, "mphase": 0, "meteorx": 500, "meteory": -60, "night": 0, "score": 0, "best": 0, "over": 0, "distance": 0}
    rx = bytearray()
    paused = False
    port, _ = find_port(args.port)
    link = None
    last_retry = 0.0
    running = True
    try:
        while running:
            mouse_jump = False
            restart_pulse = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    paused = not paused
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if state.get("over", 0):
                        restart_pulse = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_jump = True
                    if state.get("over", 0):
                        restart_pulse = True
            keys = pygame.key.get_pressed()
            jump = bool(keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w] or mouse_jump)
            reset = bool(keys[pygame.K_r] or restart_pulse)
            if link is None and time.monotonic() - last_retry >= 1.0:
                last_retry = time.monotonic()
                candidate, _ = find_port(args.port)
                if candidate:
                    port = candidate
                    try:
                        link = connect(candidate)
                        rx.clear()
                    except (serial.SerialException, OSError):
                        link = None
            if link is not None:
                try:
                    link.write(f"I,{int(jump)},{int(reset)},{int(paused)}\n".encode("ascii"))
                    if link.in_waiting:
                        rx.extend(link.read(link.in_waiting))
                        while b"\n" in rx:
                            raw, _, rx = rx.partition(b"\n")
                            try:
                                update = json.loads(raw.decode("ascii", errors="ignore"))
                                if "y" in update and "x1" in update:
                                    state = update
                            except (ValueError, TypeError):
                                pass
                except (serial.SerialException, OSError):
                    try:
                        link.close()
                    except Exception:
                        pass
                    link = None
                    rx.clear()
                    last_retry = time.monotonic()
            draw(screen, fonts, state, port or "NO PORT", jump, link is not None, paused)
            pygame.display.flip()
            clock.tick(60)
    finally:
        if link is not None:
            link.close()
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
