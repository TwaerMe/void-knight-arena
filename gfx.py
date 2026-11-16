import math
import random
import pygame
from data import WIDTH, HEIGHT, FLOOR_Y


def get_font(size, bold=False):
    return pygame.font.SysFont("segoeui,arial,tahoma,dejavusans", size, bold=bold)


class BloomRenderer:
    """Настоящий многопроходный Bloom-буфер через smoothscale + аддитивное смешивание."""
    def __init__(self):
        self.bw = WIDTH // 4
        self.bh = HEIGHT // 4
        self.buffer = pygame.Surface((self.bw, self.bh), pygame.SRCALPHA)
        self.glow_cache = {}

    def clear(self):
        self.buffer.fill((0, 0, 0, 255))

    def _get_radial(self, radius, color, alpha):
        key = (int(radius), color, int(alpha))
        if key in self.glow_cache:
            return self.glow_cache[key]
        r = max(3, int(radius))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            t = i / 6.0
            cr = max(1, int(r * t))
            ca = int(alpha * (1.0 - t * 0.82) ** 1.5)
            pygame.draw.circle(s, (*color, max(0, min(255, ca))), (r, r), cr)
        self.glow_cache[key] = s
        return s

    def add_glow(self, x, y, radius, color, alpha=140):
        sx = int(x * 0.25)
        sy = int(y * 0.25)
        sr = max(3, int(radius * 0.25))
        g = self._get_radial(sr, color, alpha)
        self.buffer.blit(g, (sx - sr, sy - sr), special_flags=pygame.BLEND_RGBA_ADD)

    def add_line(self, p1, p2, color, width=6):
        q1 = (int(p1[0] * 0.25), int(p1[1] * 0.25))
        q2 = (int(p2[0] * 0.25), int(p2[1] * 0.25))
        pygame.draw.line(self.buffer, color, q1, q2, max(2, int(width * 0.25)))

    def compose(self, target_surf):
        # Двухступенчатое масштабирование создаёт мягкое гауссово размытие ореолов
        mid = pygame.transform.smoothscale(self.buffer, (WIDTH // 2, HEIGHT // 2))
        full = pygame.transform.smoothscale(mid, (WIDTH, HEIGHT))
        target_surf.blit(full, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


class SpriteBank:
    """Генератор детализированных процедурных спрайтов и текстур с бликами и рунами."""
    def __init__(self):
        self.hero_frames = {}
        self.boss_sprites = {}
        self.enemy_sprites = {}
        self.tile_cache = {}
        self._build_hero_sprites()
        self._build_enemy_sprites()
        self._build_boss_sprites()

    def _build_hero_sprites(self):
        for frame in range(4):
            s = pygame.Surface((64, 72), pygame.SRCALPHA)
            cx = 32
            bob = -2 if frame in (1, 3) else 0
            leg_swing = [-7, 0, 7, 0][frame]

            # Ноги и сапоги с металлическим бликом
            pygame.draw.line(s, (20, 26, 44), (cx - 4, 48 + bob), (cx - 6 - leg_swing, 68), 6)
            pygame.draw.line(s, (28, 36, 58), (cx + 4, 48 + bob), (cx + 6 + leg_swing, 68), 6)
            pygame.draw.circle(s, (95, 220, 245), (cx + 6 + leg_swing, 67), 2)

            # Нагрудник и туника
            torso = [(cx, 24 + bob), (cx + 15, 34 + bob), (cx + 11, 54 + bob), (cx - 11, 54 + bob), (cx - 15, 34 + bob)]
            pygame.draw.polygon(s, (22, 30, 50), torso)
            pygame.draw.polygon(s, (75, 195, 235), torso, 2)
            # Руна на груди
            pygame.draw.polygon(s, (150, 245, 255), [(cx, 33 + bob), (cx + 4, 40 + bob), (cx, 47 + bob), (cx - 4, 40 + bob)])

            # Наплечники
            pygame.draw.polygon(s, (42, 56, 86), [(cx - 17, 30 + bob), (cx - 7, 25 + bob), (cx - 12, 38 + bob)])
            pygame.draw.polygon(s, (140, 235, 255), [(cx - 17, 30 + bob), (cx - 7, 25 + bob), (cx - 12, 38 + bob)], 1)
            pygame.draw.polygon(s, (42, 56, 86), [(cx + 17, 30 + bob), (cx + 7, 25 + bob), (cx + 12, 38 + bob)])
            pygame.draw.polygon(s, (140, 235, 255), [(cx + 17, 30 + bob), (cx + 7, 25 + bob), (cx + 12, 38 + bob)], 1)

            # Шлем Странника с рогами и визором
            helm = [(cx, 6 + bob), (cx + 13, 16 + bob), (cx + 10, 28 + bob), (cx - 10, 28 + bob), (cx - 13, 16 + bob)]
            pygame.draw.polygon(s, (230, 240, 255), helm)
            pygame.draw.polygon(s, (120, 175, 220), helm, 2)
            # Изогнутые астральные рога
            pygame.draw.polygon(s, (240, 248, 255), [(cx - 9, 13 + bob), (cx - 16, 1 + bob), (cx - 5, 9 + bob)])
            pygame.draw.polygon(s, (240, 248, 255), [(cx + 9, 13 + bob), (cx + 16, 1 + bob), (cx + 5, 9 + bob)])
            # Светящийся визор
            pygame.draw.polygon(s, (14, 18, 30), [(cx - 7, 17 + bob), (cx + 9, 17 + bob), (cx + 6, 23 + bob), (cx - 5, 23 + bob)])
            pygame.draw.line(s, (115, 245, 255), (cx - 5, 20 + bob), (cx + 7, 20 + bob), 3)

            self.hero_frames[frame] = s

    def _build_enemy_sprites(self):
        # 1. Sentinel
        s = pygame.Surface((56, 64), pygame.SRCALPHA)
        pygame.draw.polygon(s, (30, 38, 62), [(28, 4), (48, 24), (42, 60), (14, 60), (8, 24)])
        pygame.draw.polygon(s, (110, 145, 195), [(28, 4), (48, 24), (42, 60), (14, 60), (8, 24)], 2)
        pygame.draw.polygon(s, (255, 95, 125), [(24, 22), (38, 22), (34, 28), (24, 28)])
        self.enemy_sprites["sentinel"] = s

        # 2. Prism Drone
        s = pygame.Surface((56, 56), pygame.SRCALPHA)
        pygame.draw.polygon(s, (145, 45, 85), [(28, 2), (54, 28), (28, 54), (2, 28)])
        pygame.draw.polygon(s, (255, 145, 175), [(28, 2), (54, 28), (28, 54), (2, 28)], 2)
        pygame.draw.circle(s, (255, 235, 165), (28, 28), 8)
        self.enemy_sprites["prism_drone"] = s

        # 3. Aegis Warden
        s = pygame.Surface((68, 86), pygame.SRCALPHA)
        pygame.draw.polygon(s, (28, 36, 58), [(30, 6), (52, 22), (48, 82), (12, 82), (10, 22)])
        pygame.draw.polygon(s, (95, 165, 215), [(30, 6), (52, 22), (48, 82), (12, 82), (10, 22)], 2)
        # Ростовой башенный щит справа
        pygame.draw.polygon(s, (55, 125, 175), [(46, 12), (64, 20), (62, 78), (46, 84)])
        pygame.draw.polygon(s, (175, 240, 255), [(46, 12), (64, 20), (62, 78), (46, 84)], 2)
        pygame.draw.circle(s, (255, 120, 140), (34, 24), 4)
        self.enemy_sprites["aegis_warden"] = s

        # 4. Nova Orb
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(s, (195, 95, 45), (24, 24), 18)
        pygame.draw.circle(s, (255, 195, 110), (24, 24), 18, 2)
        pygame.draw.circle(s, (255, 245, 190), (24, 24), 7)
        self.enemy_sprites["nova_orb"] = s

        # 5. Rift Assassin
        s = pygame.Surface((56, 68), pygame.SRCALPHA)
        pygame.draw.polygon(s, (54, 28, 88), [(28, 4), (50, 64), (28, 54), (6, 64)])
        pygame.draw.polygon(s, (195, 115, 255), [(28, 4), (50, 64), (28, 54), (6, 64)], 2)
        pygame.draw.line(s, (235, 165, 255), (22, 24), (38, 24), 4)
        self.enemy_sprites["rift_assassin"] = s

    def _build_boss_sprites(self):
        configs = [
            ("colossus", (235, 155, 65), (255, 225, 145), 116, 148),
            ("seraph", (245, 75, 115), (255, 185, 205), 96, 136),
            ("arbiter", (175, 95, 255), (225, 185, 255), 96, 136),
            ("leviathan", (65, 220, 185), (175, 255, 235), 96, 136),
            ("valkyrie", (110, 205, 255), (215, 245, 255), 96, 136),
            ("solaris", (255, 205, 75), (255, 248, 195), 110, 140),
        ]
        for kind, prim, glow, w, h in configs:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            cx = w // 2
            # Плащ / нижние пластины
            body = [(cx, 18), (w - 10, 46), (w - 16, h - 4), (16, h - 4), (10, 46)]
            pygame.draw.polygon(s, (22, 20, 36), body)
            pygame.draw.polygon(s, prim, body, 3)

            # Нагрудные пластины и светящееся ядро
            chest = [(cx, 36), (w - 22, 54), (cx, 88), (22, 54)]
            pygame.draw.polygon(s, (36, 32, 58), chest)
            pygame.draw.polygon(s, glow, chest, 2)
            pygame.draw.circle(s, glow, (cx, 62), 10)
            pygame.draw.circle(s, (255, 255, 255), (cx, 62), 5)

            # Корона / шлем
            crown = [(cx - 22, 34), (cx - 16, 4), (cx - 5, 22), (cx, 2), (cx + 5, 22), (cx + 16, 4), (cx + 22, 34)]
            pygame.draw.polygon(s, (235, 240, 255), crown)
            pygame.draw.polygon(s, prim, crown, 2)
            # Визор
            pygame.draw.line(s, glow, (cx - 12, 28), (cx + 12, 28), 5)
            self.boss_sprites[kind] = s

    def get_floor_tile(self, biome):
        key = biome["name"]
        if key in self.tile_cache:
            return self.tile_cache[key]
        tile = pygame.Surface((64, 64))
        tile.fill(biome["stone_dark"])
        pygame.draw.rect(tile, biome["stone_mid"], (2, 2, 60, 28), border_radius=4)
        pygame.draw.rect(tile, biome["stone_mid"], (2, 34, 28, 28), border_radius=4)
        pygame.draw.rect(tile, biome["stone_mid"], (34, 34, 28, 28), border_radius=4)
        pygame.draw.line(tile, biome["stone_rim"], (2, 2), (62, 2), 2)
        # Декоративная руна
        pygame.draw.polygon(tile, biome["accent"], [(32, 10), (37, 16), (32, 22), (27, 16)], 1)
        self.tile_cache[key] = tile
        return tile


class RibbonTrail:
    """Гладкий ленточный шлейф движения клинка."""
    def __init__(self):
        self.points = []  # (tip_x, tip_y, base_x, base_y, life, color)

    def add(self, tip, base, color):
        self.points.append([tip[0], tip[1], base[0], base[1], 0.14, color])
        if len(self.points) > 10:
            self.points.pop(0)

    def update(self, dt):
        for p in self.points:
            p[4] -= dt
        self.points = [p for p in self.points if p[4] > 0]

    def draw(self, surf, bloom, ox, oy):
        if len(self.points) < 2:
            return
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            ratio = max(0.0, p2[4] / 0.14)
            col = p2[5]
            poly = [
                (p1[0] + ox, p1[1] + oy),
                (p2[0] + ox, p2[1] + oy),
                (p2[2] + ox, p2[3] + oy),
                (p1[2] + ox, p1[3] + oy),
            ]
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*col, int(190 * ratio)), poly)
            pygame.draw.line(s, (255, 255, 255, int(230 * ratio)), (p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy), max(2, int(4 * ratio)))
            surf.blit(s, (0, 0))
            bloom.add_line((p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy), col, 14)


class SparkParticle:
    """Искры с растяжением по вектору скорости (Motion Blur)."""
    def __init__(self, x, y, vx, vy, color, life=0.35, gravity=650.0, size=3):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.size = size

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf, bloom, ox, oy):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        x1, y1 = self.x + ox, self.y + oy
        x2, y2 = x1 - self.vx * 0.028, y1 - self.vy * 0.028
        pygame.draw.line(surf, self.color, (x1, y1), (x2, y2), max(1, int(self.size * ratio)))
        bloom.add_glow(x1, y1, 14 * ratio, self.color, int(130 * ratio))


class RingWave:
    """Расширяющееся ударное кольцо при парировании, взрывах и приземлении."""
    def __init__(self, x, y, max_r, color, life=0.32, width=5):
        self.x = x
        self.y = y
        self.max_r = max_r
        self.color = color
        self.life = life
        self.max_life = life
        self.width = width

    def update(self, dt):
        self.life -= dt

    def draw(self, surf, bloom, ox, oy):
        if self.life <= 0:
            return
        t = 1.0 - (self.life / self.max_life)
        r = max(4, int(self.max_r * (1.0 - (1.0 - t) ** 2)))
        w = max(1, int(self.width * (1.0 - t)))
        pos = (int(self.x + ox), int(self.y + oy))
        pygame.draw.circle(surf, self.color, pos, r, w)
        bloom.add_glow(pos[0], pos[1], r * 0.5, self.color, int(110 * (1.0 - t)))


class WeatherParticle:
    def __init__(self, biome):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, FLOOR_Y)
        self.phase = random.uniform(0, math.tau)
        self.size = random.uniform(2.0, 4.2)
        self.kind = biome["weather"]
        self.color = biome["accent"]

    def update(self, dt):
        self.phase += dt * 2.2
        if self.kind == "leaves":
            self.x += (math.sin(self.phase) * 60.0 - 40.0) * dt
            self.y += (52.0 + math.cos(self.phase) * 14.0) * dt
        else:
            self.x += math.sin(self.phase) * 22.0 * dt
            self.y -= 24.0 * dt

        if self.x < -12:
            self.x = WIDTH + 12
        elif self.x > WIDTH + 12:
            self.x = -12
        if self.y < 10:
            self.y = FLOOR_Y - 12
        elif self.y > FLOOR_Y - 8:
            self.y = 14.0

    def draw(self, surf, bloom, ox, oy):
        px, py = int(self.x + ox * 0.4), int(self.y + oy * 0.4)
        if self.kind == "leaves":
            ang = self.phase
            p1 = (px + math.cos(ang) * 6, py + math.sin(ang) * 3)
            p2 = (px - math.cos(ang) * 6, py - math.sin(ang) * 3)
            pygame.draw.line(surf, self.color, p1, p2, 3)
        else:
            pygame.draw.circle(surf, self.color, (px, py), int(self.size))
            bloom.add_glow(px, py, 10, self.color, 70)


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size=20):
        self.x = float(x)
        self.y = float(y)
        self.text = str(text)
        self.color = color
        self.font = get_font(size, bold=True)
        self.life = 0.72

    def update(self, dt):
        self.y -= 58.0 * dt
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        shadow = self.font.render(self.text, True, (10, 12, 20))
        img = self.font.render(self.text, True, self.color)
        tx = int(self.x - img.get_width() // 2 + ox)
        ty = int(self.y + oy)
        surf.blit(shadow, (tx + 2, ty + 2))
        surf.blit(img, (tx, ty))


def build_sky_surface(biome):
    surf = pygame.Surface((WIDTH, FLOOR_Y))
    c1, c2 = biome["sky_top"], biome["sky_bot"]
    for y in range(FLOOR_Y):
        t = y / max(1, FLOOR_Y - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf


def draw_world_backdrop(surf, bloom, sky_surf, biome, ox, oy, altar_rect, gate_open):
    surf.blit(sky_surf, (0, 0))
    t = pygame.time.get_ticks() * 0.001

    # Центральное светило / Затмение / Астрономическая розетка
    cx, cy = int(WIDTH * 0.5 + ox * 0.12), int(225 + oy * 0.12)
    bloom.add_glow(cx, cy, 290, biome["accent"], 120)
    if biome["weather"] == "eclipse":
        pygame.draw.circle(surf, (255, 225, 130), (cx, cy), 88)
        pygame.draw.circle(surf, (10, 8, 16), (cx, cy), 80)
    else:
        pygame.draw.circle(surf, biome["stone_rim"], (cx, cy), 138, 2)
        pygame.draw.circle(surf, biome["stone_rim"], (cx, cy), 96, 1)
        for i in range(8):
            ang = t * 0.3 + i * (math.pi / 4)
            px = cx + int(math.cos(ang) * 138)
            py = cy + int(math.sin(ang) * 138)
            pygame.draw.circle(surf, biome["accent"], (px, py), 4)

    # Дальний слой гор и шпилей (параллакс 0.22)
    for i in range(-1, 7):
        bx = int(i * 235 + ox * 0.22)
        pts = [(bx, FLOOR_Y), (bx + 85, 295 + (i % 3) * 45), (bx + 150, 345), (bx + 245, FLOOR_Y)]
        pygame.draw.polygon(surf, biome["stone_dark"], pts)

    # Готические арки с витражными окнами (параллакс 0.42)
    for px in (160, 480, 800, 1120):
        rx = int(px - 32 + ox * 0.42)
        pygame.draw.rect(surf, biome["stone_dark"], (rx, 0, 64, FLOOR_Y))
        pygame.draw.line(surf, biome["stone_rim"], (rx, 0), (rx, FLOOR_Y), 2)
        pygame.draw.line(surf, biome["stone_rim"], (rx + 64, 0), (rx + 64, FLOOR_Y), 1)
        # Витражная роза между колоннами
        wx = rx + 160
        if wx < WIDTH - 120:
            pygame.draw.circle(surf, biome["stone_mid"], (wx, 175), 34, 2)
            pygame.draw.circle(surf, biome["accent_2"], (wx, 175), 14, 1)

    # Объёмные солнечные/астральные лучи (God Rays)
    ray_surf = pygame.Surface((WIDTH, FLOOR_Y), pygame.SRCALPHA)
    for idx, rx in enumerate((260, 620, 960)):
        sway = math.sin(t * 0.7 + idx) * 28
        pts = [(rx - 35, 0), (rx + 55, 0), (rx + 230 + sway, FLOOR_Y), (rx + 45 + sway, FLOOR_Y)]
        pygame.draw.polygon(ray_surf, (*biome["ray_col"], 18), pts)
    surf.blit(ray_surf, (int(ox * 0.3), 0))

    # Алтарь Резонанса в Святилище
    if altar_rect:
        ar = altar_rect.move(int(ox), int(oy))
        bloom.add_glow(ar.centerx, ar.centery - 15, 130, biome["accent"], 150)
        pts = [(ar.centerx, ar.top), (ar.right, ar.top + 36), (ar.right - 10, ar.bottom), (ar.left + 10, ar.bottom), (ar.left, ar.top + 36)]
        pygame.draw.polygon(surf, biome["stone_mid"], pts)
        pygame.draw.polygon(surf, biome["accent"], pts, 3)
        fy = ar.top + 56 + int(math.sin(t * 3.5) * 6)
        pygame.draw.polygon(surf, (255, 255, 255), [(ar.centerx, fy - 14), (ar.centerx + 10, fy), (ar.centerx, fy + 14), (ar.centerx - 10, fy)])

    # Правый портал перехода
    gx = WIDTH - 42 + int(ox)
    gtop = FLOOR_Y - 175 + int(oy)
    if gate_open:
        bloom.add_glow(gx + 6, gtop + 88, 95, biome["accent"], 160)
        pygame.draw.rect(surf, biome["accent"], (gx, gtop, 12, 175), border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), (gx + 4, gtop + 14, 4, 147), border_radius=2)
    else:
        pygame.draw.rect(surf, (215, 65, 95), (gx, gtop, 12, 175), border_radius=5)


def draw_reflective_floor(surf, sprite_bank, entity_layer, biome, ox, oy):
    fy = int(FLOOR_Y + oy)
    tile = sprite_bank.get_floor_tile(biome)

    # Текстурированный базальтовый пол
    for tx in range(-64, WIDTH + 64, 64):
        for ty in range(fy, HEIGHT + 64, 64):
            surf.blit(tile, (tx + int(ox), ty))

    # Зеркальное отражение боевого слоя в полированном камне
    ref_h = min(HEIGHT - fy, 135)
    if ref_h > 10:
        crop = entity_layer.subsurface((0, max(0, FLOOR_Y - ref_h), WIDTH, ref_h))
        flipped = pygame.transform.flip(crop, False, True)
        flipped.set_alpha(64)
        surf.blit(flipped, (int(ox), fy + 2))

    # Светящаяся кромка арены
    pygame.draw.line(surf, biome["accent"], (0, fy), (WIDTH, fy), 3)
    pygame.draw.line(surf, (255, 255, 255), (0, fy), (WIDTH, fy), 1)
