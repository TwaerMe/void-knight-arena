import math
import random
import sys
import pygame

# --- БАЗОВЫЕ ПАРАМЕТРЫ ЭКРАНА И ФИЗИКИ ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
FLOOR_Y = 595
GRAVITY = 2320.0


def get_font(size, bold=False):
    return pygame.font.SysFont("segoeui,arial,tahoma,dejavusans", size, bold=bold)


# --- 4 АВТОРСКИХ БИОМА ---
BIOMES = [
    {
        "name": "ЗАТОНУВШАЯ ОБСЕРВАТОРИЯ",
        "sky_top": (8, 12, 26),
        "sky_bot": (18, 32, 56),
        "accent": (85, 225, 245),
        "accent_soft": (45, 130, 165),
        "arch": (16, 24, 42),
        "arch_rim": (48, 82, 118),
        "floor_top": (14, 24, 40),
        "floor_bot": (6, 10, 18),
        "weather": "stars",
        "weather_col": (165, 240, 255),
    },
    {
        "name": "ЯНТАРНЫЙ ЛИСТОПАД",
        "sky_top": (24, 12, 22),
        "sky_bot": (62, 28, 34),
        "accent": (255, 185, 85),
        "accent_soft": (185, 95, 55),
        "arch": (34, 17, 24),
        "arch_rim": (96, 48, 52),
        "floor_top": (28, 15, 22),
        "floor_bot": (12, 6, 10),
        "weather": "leaves",
        "weather_col": (255, 165, 75),
    },
    {
        "name": "ХРУСТАЛЬНЫЕ КАТАКОМБЫ",
        "sky_top": (8, 22, 24),
        "sky_bot": (16, 48, 46),
        "accent": (95, 245, 185),
        "accent_soft": (42, 145, 115),
        "arch": (13, 34, 34),
        "arch_rim": (42, 98, 92),
        "floor_top": (12, 30, 30),
        "floor_bot": (5, 14, 15),
        "weather": "spores",
        "weather_col": (140, 255, 210),
    },
    {
        "name": "РАЗЛОМ ЗАТМЕНИЯ",
        "sky_top": (10, 8, 16),
        "sky_bot": (34, 22, 42),
        "accent": (255, 215, 110),
        "accent_soft": (165, 115, 235),
        "arch": (20, 14, 28),
        "arch_rim": (78, 56, 105),
        "floor_top": (18, 14, 26),
        "floor_bot": (8, 6, 12),
        "weather": "eclipse",
        "weather_col": (255, 225, 140),
    },
]

# --- 12 АВТОРСКИХ РЕЛИКВИЙ СИНЕРГИИ ---
RELICS = [
    {
        "id": "echo_blade",
        "name": "Эхо-Клинок",
        "slots": 2,
        "cost": 0,
        "unlocked": True,
        "color": (95, 230, 255),
        "desc": "Каждый взмах клинка вызывает второй фантомный разрез с задержкой.",
    },
    {
        "id": "mirror_aegis",
        "name": "Зеркальный Бастион",
        "slots": 2,
        "cost": 0,
        "unlocked": True,
        "color": (255, 225, 120),
        "desc": "Успешное парирование выпускает 3 самонаводящиеся звезды в ближайших врагов.",
    },
    {
        "id": "harmonic_core",
        "name": "Ядро Резонанса",
        "slots": 1,
        "cost": 0,
        "unlocked": True,
        "color": (185, 130, 255),
        "desc": "Шкала Резонанса заполняется на 50% быстрее и дольше не спадает.",
    },
    {
        "id": "volt_step",
        "name": "Искровой Шаг",
        "slots": 2,
        "cost": 130,
        "unlocked": False,
        "color": (110, 200, 255),
        "desc": "Фазовый рывок пронзает врагов и оставляет на месте разряд молнии.",
    },
    {
        "id": "solar_crescent",
        "name": "Солнечный Серп",
        "slots": 3,
        "cost": 180,
        "unlocked": False,
        "color": (255, 195, 85),
        "desc": "Каждый удар выпускает летящий энергетический серп (усиленный при полном HP).",
    },
    {
        "id": "astral_vortex",
        "name": "Астральный Вихрь",
        "slots": 2,
        "cost": 140,
        "unlocked": False,
        "color": (120, 250, 200),
        "desc": "Удар вниз в воздухе (отскок) создаёт вокруг героя режущий вихрь.",
    },
    {
        "id": "prism_lens",
        "name": "Призма Света",
        "slots": 3,
        "cost": 200,
        "unlocked": False,
        "color": (235, 150, 255),
        "desc": "Увеличивает размер и урон всех Астральных Искусств на 45%.",
    },
    {
        "id": "gale_tempo",
        "name": "Ритм Ветра",
        "slots": 3,
        "cost": 190,
        "unlocked": False,
        "color": (145, 245, 255),
        "desc": "Ускоряет серию атак на 35% и сокращает перезарядку рывка.",
    },
    {
        "id": "crystal_reaper",
        "name": "Кристальный Жнец",
        "slots": 2,
        "cost": 150,
        "unlocked": False,
        "color": (255, 110, 145),
        "desc": "Попадания дают на 40% больше Эфира, а убийство врага слегка лечит.",
    },
    {
        "id": "briar_halo",
        "name": "Венец Возмездия",
        "slots": 1,
        "cost": 110,
        "unlocked": False,
        "color": (255, 130, 95),
        "desc": "При получении урона высвобождает взрывную волну и 25 Эфира.",
    },
    {
        "id": "lumen_magnet",
        "name": "Магнит Люмена",
        "slots": 1,
        "cost": 95,
        "unlocked": False,
        "color": (255, 235, 140),
        "desc": "Притягивает осколки Люмена со всей арены и даёт +30% к добыче.",
    },
    {
        "id": "titan_heart",
        "name": "Сердце Титана",
        "slots": 2,
        "cost": 160,
        "unlocked": False,
        "color": (115, 215, 255),
        "desc": "Добавляет +2 ячейки прочности (HP) и усиливает отбрасывание.",
    },
]


# --- КЭШ СВЕТОВЫХ ТЕКСТУР ДЛЯ 60 FPS ---
GLOW_CACHE = {}


def get_glow_surface(radius, color, alpha=110):
    key = (int(radius), color, int(alpha))
    if key in GLOW_CACHE:
        return GLOW_CACHE[key]
    r = max(4, int(radius))
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        ratio = i / steps
        cur_r = int(r * ratio)
        cur_a = int(alpha * (1.0 - ratio * 0.85) ** 1.6)
        pygame.draw.circle(surf, (*color, max(0, min(255, cur_a))), (r, r), cur_r)
    GLOW_CACHE[key] = surf
    return surf


def blit_glow(surf, x, y, radius, color, alpha=110):
    g = get_glow_surface(radius, color, alpha)
    surf.blit(g, (int(x - g.get_width() // 2), int(y - g.get_height() // 2)), special_flags=pygame.BLEND_RGBA_ADD)


def build_sky_surface(biome):
    surf = pygame.Surface((WIDTH, FLOOR_Y))
    c1 = biome["sky_top"]
    c2 = biome["sky_bot"]
    for y in range(FLOOR_Y):
        t = y / max(1, FLOOR_Y - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf


def build_floor_surface(biome):
    h = HEIGHT - FLOOR_Y + 40
    surf = pygame.Surface((WIDTH + 60, h))
    c1 = biome["floor_top"]
    c2 = biome["floor_bot"]
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH + 60, y))
    return surf


# --- ЧАСТИЦЫ, ШЛЕЙФЫ, ТЕКСТЫ И ОБЪЕКТЫ ---
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity=0.0, glow=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.glow = glow

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        r = max(1, int(self.size * ratio))
        px, py = int(self.x + ox), int(self.y + oy)
        if self.glow and r >= 2:
            blit_glow(surf, px, py, r * 3, self.color, int(85 * ratio))
        pygame.draw.circle(surf, self.color, (px, py), r)


class WeatherMote:
    def __init__(self, biome):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, FLOOR_Y)
        self.phase = random.uniform(0, math.tau)
        self.size = random.uniform(2.0, 4.5)
        self.kind = biome["weather"]
        self.color = biome["weather_col"]

    def update(self, dt):
        self.phase += dt * 2.4
        if self.kind == "leaves":
            self.x += (math.sin(self.phase) * 55.0 - 35.0) * dt
            self.y += (48.0 + math.cos(self.phase) * 15.0) * dt
        elif self.kind == "spores":
            self.x += math.sin(self.phase) * 28.0 * dt
            self.y -= 26.0 * dt
        else:
            self.x += math.sin(self.phase * 0.7) * 18.0 * dt
            self.y -= 14.0 * dt

        if self.x < -10:
            self.x = WIDTH + 10
        elif self.x > WIDTH + 10:
            self.x = -10
        if self.y < 10:
            self.y = FLOOR_Y - 10
        elif self.y > FLOOR_Y - 8:
            self.y = 14.0

    def draw(self, surf, ox, oy):
        px, py = int(self.x + ox * 0.5), int(self.y + oy * 0.5)
        if self.kind == "leaves":
            ang = self.phase
            p1 = (px + math.cos(ang) * 6, py + math.sin(ang) * 3)
            p2 = (px - math.cos(ang) * 6, py - math.sin(ang) * 3)
            pygame.draw.line(surf, self.color, p1, p2, 3)
        else:
            pygame.draw.circle(surf, self.color, (px, py), int(self.size))


class Afterimage:
    def __init__(self, rect, facing, color=(90, 220, 255)):
        self.rect = rect.copy()
        self.facing = facing
        self.color = color
        self.life = 0.24
        self.max_life = 0.24

    def update(self, dt):
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        alpha = int(150 * ratio)
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.polygon(
            s,
            (*self.color, alpha),
            [(self.rect.width // 2, 0), (self.rect.width, self.rect.height // 2), (self.rect.width // 2, self.rect.height), (0, self.rect.height // 2)],
        )
        surf.blit(s, (int(self.rect.x + ox), int(self.rect.y + oy)))


class SlashArc:
    """Красивая полумесячная дуга удара с затуханием."""
    def __init__(self, rect, direction, color=(120, 240, 255), is_echo=False):
        self.rect = rect.copy()
        self.direction = direction
        self.color = color
        self.is_echo = is_echo
        self.life = 0.16
        self.max_life = 0.16

    def update(self, dt):
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        r = self.rect.move(int(ox), int(oy))
        s = pygame.Surface((r.width + 20, r.height + 20), pygame.SRCALPHA)
        local = pygame.Rect(10, 10, r.width, r.height)
        alpha = int((170 if self.is_echo else 235) * ratio)
        pygame.draw.ellipse(s, (*self.color, alpha), local, max(2, int(9 * ratio)))
        inner = local.inflate(-14, -14)
        if inner.width > 0 and inner.height > 0:
            pygame.draw.ellipse(s, (255, 255, 255, alpha), inner, max(1, int(4 * ratio)))
        surf.blit(s, (r.x - 10, r.y - 10))


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
        img = self.font.render(self.text, True, self.color)
        surf.blit(img, (int(self.x - img.get_width() // 2 + ox), int(self.y + oy)))


class LumenCrystal:
    def __init__(self, x, y, value=6):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-220, 220)
        self.vy = random.uniform(-470, -190)
        self.value = value
        self.life = 25.0
        self.spin = random.uniform(0, math.tau)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 8), int(self.y - 8), 16, 16)

    def update(self, dt, player, magnet=False):
        self.life -= dt
        self.spin += dt * 6.0
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        dist = math.hypot(dx, dy) or 1.0
        pull = 1100.0 if magnet else 160.0
        if dist < pull:
            spd = 820.0 if magnet else 520.0
            self.vx += (dx / dist) * spd * 6.0 * dt
            self.vy += (dy / dist) * spd * 6.0 * dt
            self.vx *= 0.91
            self.vy *= 0.91
        else:
            self.vy = min(960.0, self.vy + GRAVITY * 0.85 * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < 45:
            self.x = 45.0
            self.vx *= -0.6
        elif self.x > WIDTH - 45:
            self.x = float(WIDTH - 45)
            self.vx *= -0.6
        if self.y >= FLOOR_Y - 8:
            self.y = float(FLOOR_Y - 8)
            self.vy *= -0.45
            self.vx *= 0.78

    def draw(self, surf, ox, oy):
        cx, cy = int(self.x + ox), int(self.y + oy)
        w = max(3, int(abs(math.cos(self.spin)) * 6))
        pts = [(cx, cy - 9), (cx + w, cy), (cx, cy + 9), (cx - w, cy)]
        blit_glow(surf, cx, cy, 18, (110, 235, 255), 75)
        pygame.draw.polygon(surf, (215, 250, 255), pts)
        pygame.draw.polygon(surf, (95, 215, 245), pts, 2)


class Platform:
    def __init__(self, x, y, w, h=16):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surf, ox, oy, biome):
        r = self.rect.move(int(ox), int(oy))
        pygame.draw.rect(surf, biome["arch"], r, border_radius=6)
        pygame.draw.rect(surf, biome["arch_rim"], r, 2, border_radius=6)
        pygame.draw.line(surf, biome["accent"], (r.left + 8, r.top + 1), (r.right - 8, r.top + 1), 2)


class CrystalHazard:
    """Кристальные шипы: наносят урон при касании, но позволяют оттолкнуться ударом вниз!"""
    def __init__(self, x, y, w):
        self.rect = pygame.Rect(x, y - 24, w, 24)

    def draw(self, surf, ox, oy, biome):
        r = self.rect.move(int(ox), int(oy))
        step = 20
        for sx in range(r.left, r.right - 6, step):
            pts = [(sx + 2, r.bottom), (sx + step // 2, r.top), (sx + step - 2, r.bottom)]
            pygame.draw.polygon(surf, biome["accent_soft"], pts)
            pygame.draw.polygon(surf, biome["accent"], pts, 2)


class LumenCluster:
    """Кристальная друза с Люменом."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 22, y - 48, 44, 48)
        self.hp = 3
        self.flash = 0.0

    def update(self, dt):
        self.flash = max(0.0, self.flash - dt)

    def draw(self, surf, ox, oy):
        if self.hp <= 0:
            return
        r = self.rect.move(int(ox), int(oy))
        blit_glow(surf, r.centerx, r.centery, 42, (95, 225, 255), 65)
        col = (255, 255, 255) if self.flash > 0 else (75, 195, 235)
        pygame.draw.polygon(surf, col, [(r.left + 6, r.bottom), (r.left + 12, r.top + 14), (r.centerx, r.top), (r.right - 10, r.top + 16), (r.right - 6, r.bottom)])
        pygame.draw.polygon(surf, (230, 252, 255), [(r.centerx - 5, r.bottom), (r.centerx, r.top + 10), (r.centerx + 7, r.bottom)])


# --- СНАРЯДЫ, ВОЛНЫ, ЛАЗЕРЫ И ЗАКЛИНАНИЯ ---
class Shockwave:
    def __init__(self, x, y, vx, height=64, life=1.4, color=(255, 110, 120), friendly=False, damage=1):
        self.rect = pygame.Rect(int(x - 16), int(y - height), 32, height)
        self.x = float(self.rect.x)
        self.vx = vx
        self.life = life
        self.color = color
        self.friendly = friendly
        self.damage = damage
        self.hit_ids = set()

    def update(self, dt):
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        self.life -= dt

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        blit_glow(surf, r.centerx, r.centery, 45, self.color, 80)
        pts = [(r.left, r.bottom), (r.centerx, r.top), (r.right, r.bottom)]
        pygame.draw.polygon(surf, self.color, pts)
        pygame.draw.polygon(surf, (255, 250, 255), [(r.left + 8, r.bottom), (r.centerx, r.top + 14), (r.right - 8, r.bottom)])


class Projectile:
    def __init__(self, x, y, vx, vy, radius=12, color=(255, 100, 130), homing=False, boomerang=False, owner=None, friendly=False, damage=1):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = 4.2
        self.homing = homing
        self.boomerang = boomerang
        self.owner = owner
        self.friendly = friendly
        self.damage = damage
        self.age = 0.0
        self.hit_ids = set()

    @property
    def rect(self):
        s = int(self.radius * 1.5)
        return pygame.Rect(int(self.x - s // 2), int(self.y - s // 2), s, s)

    def update(self, dt, target=None):
        self.age += dt
        self.life -= dt
        if self.homing and target and self.age < 2.4:
            dx = target.rect.centerx - self.x
            dy = target.rect.centery - self.y
            dist = math.hypot(dx, dy) or 1.0
            self.vx += (dx / dist) * 620.0 * dt
            self.vy += (dy / dist) * 620.0 * dt
            spd = math.hypot(self.vx, self.vy)
            if spd > 460.0:
                self.vx = (self.vx / spd) * 460.0
                self.vy = (self.vy / spd) * 460.0
        elif self.boomerang and self.owner and self.age > 0.55:
            dx = self.owner.rect.centerx - self.x
            dy = self.owner.rect.centery - self.y
            dist = math.hypot(dx, dy) or 1.0
            self.vx += (dx / dist) * 1850.0 * dt
            self.vy += (dy / dist) * 1850.0 * dt
            if dist < 48:
                self.life = 0.0

        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf, ox, oy):
        pos = (int(self.x + ox), int(self.y + oy))
        blit_glow(surf, pos[0], pos[1], self.radius * 2.4, self.color, 95)
        if self.boomerang:
            ang = self.age * 20.0
            p1 = (pos[0] + math.cos(ang) * 26, pos[1] + math.sin(ang) * 26)
            p2 = (pos[0] - math.cos(ang) * 26, pos[1] - math.sin(ang) * 26)
            pygame.draw.line(surf, self.color, p1, p2, 6)
            pygame.draw.line(surf, (255, 245, 255), p1, p2, 2)
        else:
            pygame.draw.circle(surf, self.color, pos, self.radius)
            pygame.draw.circle(surf, (255, 250, 255), pos, max(3, self.radius // 2))


class LaserBeam:
    def __init__(self, x1, y1, angle, length=1450, warn_time=0.65, active_time=0.32, color=(215, 130, 255)):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + math.cos(angle) * length
        self.y2 = y1 + math.sin(angle) * length
        self.warn_time = warn_time
        self.active_time = active_time
        self.timer = warn_time + active_time
        self.color = color

    @property
    def is_firing(self):
        return 0 < self.timer <= self.active_time

    def update(self, dt):
        self.timer -= dt

    def collides_rect(self, rect):
        if not self.is_firing:
            return False
        return bool(rect.inflate(18, 18).clipline((self.x1, self.y1), (self.x2, self.y2)))

    def draw(self, surf, ox, oy):
        if self.timer <= 0:
            return
        p1 = (int(self.x1 + ox), int(self.y1 + oy))
        p2 = (int(self.x2 + ox), int(self.y2 + oy))
        if not self.is_firing:
            pygame.draw.line(surf, self.color, p1, p2, 2)
        else:
            pygame.draw.line(surf, self.color, p1, p2, 28)
            pygame.draw.line(surf, (255, 252, 255), p1, p2, 10)


class AstralArtBlast:
    def __init__(self, x, y, w, h, vx, vy, damage, life, art_type):
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.life = life
        self.max_life = life
        self.art_type = art_type
        self.hit_ids = set()

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.life -= dt

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        blit_glow(surf, r.centerx, r.centery, max(r.width, r.height) * 0.75, (95, 230, 255), 95)
        if self.art_type == "lance":
            pygame.draw.polygon(surf, (110, 235, 255), [(r.left, r.centery), (r.centerx, r.top), (r.right, r.centery), (r.centerx, r.bottom)])
            pygame.draw.polygon(surf, (255, 255, 255), [(r.left + 16, r.centery), (r.centerx, r.top + 10), (r.right - 16, r.centery), (r.centerx, r.bottom - 10)])
        elif self.art_type == "nova":
            pygame.draw.ellipse(surf, (130, 220, 255), r, 8)
            inner = r.inflate(-36, -36)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(surf, (255, 255, 255), inner, 4)
        elif self.art_type == "meteor":
            pygame.draw.ellipse(surf, (125, 235, 255), r)
            inner = r.inflate(-32, -22)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(surf, (255, 255, 255), inner)


# --- ГЕРОЙ: АСТРАЛЬНЫЙ СТРАННИК ---
class Hero:
    def __init__(self):
        self.rect = pygame.Rect(140, FLOOR_Y - 58, 34, 58)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1

        self.base_max_hp = 6
        self.max_hp = 6
        self.hp = 6
        self.max_aether = 100.0
        self.aether = 65.0
        self.base_damage = 16
        self.lumen = 65

        self.max_slots = 4
        self.equipped = ["echo_blade", "mirror_aegis"]

        # Шкала Резонанса (растёт от темпа боя)
        self.resonance = 0.0  # 0..100
        self.combo_count = 0

        self.on_ground = False
        self.jumps_left = 2
        self.jump_held = False
        self.drop_through_timer = 0.0

        self.dash_timer = 0.0
        self.dash_cd = 0.0
        self.dash_dir = 1
        self.dash_hit_ids = set()

        self.parry_timer = 0.0
        self.parry_cd = 0.0

        self.slash_timer = 0.0
        self.slash_cd = 0.0
        self.slash_step = 0
        self.slash_dir = "right"
        self.hit_ids = set()
        self.pending_echo = None  # (delay, rect, direction)

        self.dive_active = False
        self.invuln_timer = 0.0
        self.mend_timer = 0.0
        self.afterimage_timer = 0.0
        self.scarf = [[self.rect.centerx, self.rect.top + 22] for _ in range(8)]

    def has_relic(self, rid):
        return rid in self.equipped

    def used_slots(self):
        by_id = {r["id"]: r["slots"] for r in RELICS}
        return sum(by_id.get(rid, 0) for rid in self.equipped)

    def recalculate_stats(self):
        bonus = 2 if self.has_relic("titan_heart") else 0
        self.max_hp = self.base_max_hp + bonus
        self.hp = min(self.hp, self.max_hp)

    @property
    def resonance_tier(self):
        if self.resonance >= 85:
            return 3  # OVERDRIVE
        if self.resonance >= 55:
            return 2  # x1.5
        if self.resonance >= 25:
            return 1  # x1.25
        return 0

    @property
    def blade_damage(self):
        res_bonus = [1.0, 1.15, 1.3, 1.5][self.resonance_tier]
        return int(round(self.base_damage * res_bonus))

    @property
    def art_mult(self):
        return 1.45 if self.has_relic("prism_lens") else 1.0

    def add_resonance(self, amount):
        mult = 1.5 if self.has_relic("harmonic_core") else 1.0
        self.resonance = min(100.0, self.resonance + amount * mult)

    def reset_air_mobility(self):
        self.jumps_left = 2
        self.dash_cd = min(self.dash_cd, 0.04)

    def start_dash(self):
        if self.dash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.dash_timer = 0.19
            self.dash_cd = 0.36 if self.has_relic("gale_tempo") else 0.50
            self.dash_dir = self.facing
            self.dash_hit_ids.clear()
            self.vy = 0.0
            self.mend_timer = 0.0
            return True
        return False

    def start_parry(self):
        if self.parry_cd <= 0 and self.parry_timer <= 0 and not self.dive_active:
            self.parry_timer = 0.24
            self.parry_cd = 0.62
            self.mend_timer = 0.0
            return True
        return False

    def start_slash(self, keys, slash_arcs, projectiles):
        if self.slash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.slash_timer = 0.14
            self.slash_cd = 0.17 if self.has_relic("gale_tempo") else 0.24
            self.slash_step = (self.slash_step + 1) % 4
            self.hit_ids.clear()
            self.mend_timer = 0.0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.slash_dir = "up"
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not self.on_ground:
                self.slash_dir = "down"
            else:
                self.slash_dir = "right" if self.facing == 1 else "left"

            s_rect = self.get_slash_rect()
            if s_rect:
                col = (255, 220, 110) if self.resonance_tier == 3 else (105, 235, 255)
                slash_arcs.append(SlashArc(s_rect, self.slash_dir, col))
                if self.has_relic("echo_blade"):
                    self.pending_echo = (0.11, s_rect.copy(), self.slash_dir)

                # Каждый 4-й удар в серии или реликвия Солнечный Серп выпускает волну!
                if self.slash_step == 3 or (self.has_relic("solar_crescent") and self.hp == self.max_hp):
                    vx = self.facing * 760.0 if self.slash_dir in ("left", "right") else 0.0
                    vy = -760.0 if self.slash_dir == "up" else (760.0 if self.slash_dir == "down" else 0.0)
                    projectiles.append(
                        Projectile(
                            s_rect.centerx,
                            s_rect.centery,
                            vx,
                            vy,
                            radius=14,
                            color=(255, 215, 110),
                            friendly=True,
                            damage=int(self.blade_damage * 0.85),
                        )
                    )
            return True
        return False

    def cast_art(self, keys, arts, particles):
        if self.aether < 33.0 or self.dash_timer > 0 or self.dive_active:
            return False
        self.aether -= 33.0
        self.mend_timer = 0.0
        scale = 1.25 if self.has_relic("prism_lens") else 1.0

        # Вверх + E: Звёздная Нова
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            rad = int(260 * scale)
            arts.append(
                AstralArtBlast(
                    self.rect.centerx - rad // 2,
                    self.rect.centery - rad // 2,
                    rad,
                    rad,
                    0,
                    0,
                    int(44 * self.art_mult),
                    0.26,
                    "nova",
                )
            )
            for _ in range(28):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(180, 480)
                particles.append(Particle(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, (150, 235, 255), 6, 0.4, glow=True))
            return True

        # Вниз в воздухе + E: Метеорный Удар
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not self.on_ground:
            self.dive_active = True
            self.vx = 0.0
            self.vy = 1520.0
            self.invuln_timer = max(self.invuln_timer, 0.7)
            return True

        # Вперёд + E: Копьё Эфира
        w, h = int(125 * scale), int(48 * scale)
        sx = self.rect.right if self.facing == 1 else self.rect.left - w
        arts.append(
            AstralArtBlast(
                sx,
                self.rect.centery - h // 2,
                w,
                h,
                self.facing * 1020.0,
                0.0,
                int(36 * self.art_mult),
                1.1,
                "lance",
            )
        )
        self.vx = -self.facing * 150.0
        return True

    def get_slash_rect(self):
        if self.slash_timer <= 0:
            return None
        reach = 1.25 if self.resonance_tier == 3 else 1.08
        length = int(102 * reach)
        broad = int(84 * reach)
        cx, cy = self.rect.center
        if self.slash_dir == "right":
            return pygame.Rect(self.rect.right - 6, cy - broad // 2, length, broad)
        if self.slash_dir == "left":
            return pygame.Rect(self.rect.left - length + 6, cy - broad // 2, length, broad)
        if self.slash_dir == "up":
            return pygame.Rect(cx - broad // 2, self.rect.top - length + 6, broad, length)
        if self.slash_dir == "down":
            return pygame.Rect(cx - broad // 2, self.rect.bottom - 6, broad, length)
        return None

    def update(self, dt, keys, platforms, particles, afterimages, arts, shockwaves, slash_arcs):
        self.dash_cd = max(0.0, self.dash_cd - dt)
        self.slash_cd = max(0.0, self.slash_cd - dt)
        self.slash_timer = max(0.0, self.slash_timer - dt)
        self.parry_cd = max(0.0, self.parry_cd - dt)
        self.parry_timer = max(0.0, self.parry_timer - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)
        self.drop_through_timer = max(0.0, self.drop_through_timer - dt)

        # Плавное затухание Резонанса вне боя
        decay = 4.2 if self.has_relic("harmonic_core") else 6.8
        self.resonance = max(0.0, self.resonance - decay * dt)
        if self.resonance == 0:
            self.combo_count = 0

        move_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir += 1

        if move_dir != 0 and self.dash_timer <= 0 and not self.dive_active:
            self.facing = move_dir

        # Гармоническое Восстановление (удерживать F на земле)
        if (
            keys[pygame.K_f]
            and self.on_ground
            and move_dir == 0
            and self.dash_timer <= 0
            and not self.dive_active
            and self.hp < self.max_hp
            and self.aether >= 33.0
        ):
            self.mend_timer += dt
            if random.random() < 0.65:
                particles.append(Particle(self.rect.centerx + random.uniform(-28, 28), self.rect.bottom - random.uniform(0, 46), random.uniform(-20, 20), random.uniform(-160, -60), (130, 245, 255), 5, 0.4, glow=True))
            if self.mend_timer >= 0.72:
                self.mend_timer = 0.0
                self.aether -= 33.0
                self.hp = min(self.max_hp, self.hp + 1)
                for _ in range(24):
                    ang = random.uniform(0, math.tau)
                    spd = random.uniform(90, 270)
                    particles.append(Particle(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, (255, 255, 255), 7, 0.5, glow=True))
        else:
            self.mend_timer = 0.0

        # Движение / Метеорный удар / Фазовый рывок
        if self.dive_active:
            self.vx = 0.0
            self.vy = 1520.0
            self.afterimage_timer -= dt
            if self.afterimage_timer <= 0:
                self.afterimage_timer = 0.024
                afterimages.append(Afterimage(self.rect, self.facing, (130, 240, 255)))
        elif self.dash_timer > 0:
            self.dash_timer -= dt
            self.vx = self.dash_dir * 1050.0
            self.vy = 0.0
            self.afterimage_timer -= dt
            if self.afterimage_timer <= 0:
                self.afterimage_timer = 0.025
                col = (140, 195, 255) if self.has_relic("volt_step") else (95, 225, 245)
                afterimages.append(Afterimage(self.rect, self.facing, col))
        else:
            spd_bonus = 1.12 if self.resonance_tier >= 2 else 1.0
            target_vx = move_dir * 450.0 * spd_bonus
            accel = 3600.0 if self.on_ground else 2600.0
            if self.vx < target_vx:
                self.vx = min(target_vx, self.vx + accel * dt)
            elif self.vx > target_vx:
                self.vx = max(target_vx, self.vx - accel * dt)

            if not self.jump_held and self.vy < -260.0:
                self.vy += GRAVITY * 1.45 * dt
            self.vy = min(1220.0, self.vy + GRAVITY * dt)

        prev_bottom = self.y + self.rect.height
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 38:
            self.x = 38.0
            self.vx = 0.0
        elif self.x > WIDTH - 38 - self.rect.width:
            self.x = float(WIDTH - 38 - self.rect.width)
            self.vx = 0.0

        landed = False
        if self.vy >= 0 and self.drop_through_timer <= 0 and not self.dive_active:
            new_bottom = self.y + self.rect.height
            test_rect = pygame.Rect(int(self.x + 4), int(self.y), self.rect.width - 8, self.rect.height)
            for plat in platforms:
                if test_rect.colliderect(plat.rect) and prev_bottom <= plat.rect.top + 10 and new_bottom >= plat.rect.top:
                    self.y = float(plat.rect.top - self.rect.height)
                    self.vy = 0.0
                    landed = True
                    break

        if self.y + self.rect.height >= FLOOR_Y:
            self.y = float(FLOOR_Y - self.rect.height)
            self.vy = 0.0
            landed = True
            if self.dive_active:
                self.dive_active = False
                self.invuln_timer = max(self.invuln_timer, 0.35)
                dmg = int(54 * self.art_mult)
                scale = 1.25 if self.has_relic("prism_lens") else 1.0
                bw, bh = int(320 * scale), int(125 * scale)
                arts.append(AstralArtBlast(self.rect.centerx - bw // 2, FLOOR_Y - bh, bw, bh, 0, 0, dmg, 0.28, "meteor"))
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, -640.0, height=56, life=0.6, color=(110, 235, 255), friendly=True, damage=int(26 * self.art_mult)))
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, 640.0, height=56, life=0.6, color=(110, 235, 255), friendly=True, damage=int(26 * self.art_mult)))
                for _ in range(36):
                    particles.append(Particle(self.rect.centerx + random.uniform(-50, 50), FLOOR_Y - 6, random.uniform(-460, 460), random.uniform(-430, -60), (140, 240, 255), 8, 0.5, glow=True))

        if landed:
            self.on_ground = True
            self.jumps_left = 2
        else:
            self.on_ground = False

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Физика шёлкового шарфа
        self.scarf[0] = [self.rect.centerx - self.facing * 5, self.rect.top + 22]
        for i in range(1, len(self.scarf)):
            px, py = self.scarf[i - 1]
            cx, cy = self.scarf[i]
            tx = px - self.facing * 8
            ty = py + 4 + math.sin(pygame.time.get_ticks() * 0.012 + i) * 1.5
            self.scarf[i][0] += (tx - cx) * min(1.0, 24.0 * dt)
            self.scarf[i][1] += (ty - cy) * min(1.0, 24.0 * dt)

    def draw(self, surf, ox, oy):
        if self.invuln_timer > 0 and not self.dive_active and int(self.invuln_timer * 22) % 2 == 0:
            return

        r = self.rect.move(int(ox), int(oy))
        aura_col = (255, 215, 105) if self.resonance_tier == 3 else (95, 225, 245)
        blit_glow(surf, r.centerx, r.centery, 48 + self.resonance_tier * 8, aura_col, 55 + self.resonance_tier * 12)

        # Развевающийся шарф
        pts = [(int(p[0] + ox), int(p[1] + oy)) for p in self.scarf]
        for i in range(len(pts) - 1):
            w = max(3, 14 - i)
            col = (255, 200, 95) if (self.resonance_tier == 3 and i > 3) else (65, 185, 225)
            pygame.draw.line(surf, col, pts[i], pts[i + 1], w)

        # Плащ-туника и доспех Странника
        cloak = [(r.centerx, r.top + 18), (r.left + 2, r.bottom), (r.right - 2, r.bottom)]
        pygame.draw.polygon(surf, (22, 30, 48), cloak)
        pygame.draw.polygon(surf, (95, 215, 245), cloak, 2)

        # Капюшон и светящийся визор
        hood = [(r.centerx, r.top), (r.left + 3, r.top + 18), (r.centerx, r.top + 25), (r.right - 3, r.top + 18)]
        pygame.draw.polygon(surf, (238, 246, 255), hood)
        visor_x = r.centerx + self.facing * 5
        pygame.draw.line(surf, aura_col, (visor_x - 6, r.top + 14), (visor_x + 6, r.top + 14), 4)

        # Визуальный щит Астрального Парирования
        if self.parry_timer > 0:
            blit_glow(surf, r.centerx, r.centery, 64, (255, 235, 140), 130)
            pygame.draw.circle(surf, (255, 245, 180), r.center, 44, 4)
            pygame.draw.circle(surf, (130, 235, 255), r.center, 36, 2)


# --- 5 АВТОРСКИХ ПРОТИВНИКОВ ---
class Enemy:
    def __init__(self, kind, x, y, depth):
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = -1
        self.flash = 0.0
        self.timer = random.uniform(0.4, 1.3)
        self.state = "idle"
        scale = 1.0 + (depth - 1) * 0.16

        if kind == "sentinel":
            self.w, self.h = 40, 54
            self.max_hp = int(38 * scale)
            self.lumen = 12
        elif kind == "prism_drone":
            self.w, self.h = 42, 42
            self.max_hp = int(34 * scale)
            self.lumen = 15
        elif kind == "aegis_warden":
            self.w, self.h = 50, 76
            self.max_hp = int(62 * scale)
            self.lumen = 22
        elif kind == "nova_orb":
            self.w, self.h = 36, 36
            self.max_hp = int(26 * scale)
            self.lumen = 14
        elif kind == "rift_assassin":
            self.w, self.h = 40, 58
            self.max_hp = int(44 * scale)
            self.lumen = 18

        self.hp = self.max_hp

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, hero, projectiles):
        self.flash = max(0.0, self.flash - dt)
        self.timer -= dt
        dx = hero.rect.centerx - self.rect.centerx
        dy = hero.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1.0

        if self.kind == "sentinel":
            self.facing = 1 if dx > 0 else -1
            self.vx = self.facing * 210.0
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        elif self.kind == "prism_drone":
            self.facing = 1 if dx > 0 else -1
            desired_y = max(130.0, hero.rect.centery - 160.0)
            self.vx = (dx / dist) * 150.0 if dist > 270 else -(dx / dist) * 95.0
            self.vy = (desired_y - self.y) * 2.5
            if self.timer <= 0:
                self.timer = 2.0
                base_ang = math.atan2(dy, dx)
                for off in (-0.22, 0.0, 0.22):
                    ang = base_ang + off
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 410, math.sin(ang) * 410, 10, (255, 115, 145)))

        elif self.kind == "aegis_warden":
            if self.state == "idle":
                self.facing = 1 if dx > 0 else -1
                self.vx = self.facing * 125.0
                if abs(dx) < 175 and abs(dy) < 95 and self.timer <= 0:
                    self.state = "windup"
                    self.timer = 0.45
                    self.vx = 0.0
            elif self.state == "windup" and self.timer <= 0:
                self.state = "strike"
                self.timer = 0.28
                self.vx = self.facing * 550.0
            elif self.state == "strike" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.85
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        elif self.kind == "nova_orb":
            self.vx = (dx / dist) * 170.0
            self.vy = (dy / dist) * 170.0
            if dist < 72 and self.state != "arming":
                self.state = "arming"
                self.timer = 0.45
            if self.state == "arming" and self.timer <= 0:
                self.hp = 0
                for i in range(8):
                    ang = (math.tau / 8) * i
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 340, math.sin(ang) * 340, 10, (255, 145, 80)))

        elif self.kind == "rift_assassin":
            if self.state == "idle":
                self.facing = 1 if dx > 0 else -1
                self.vx = self.facing * 175.0
                if self.timer <= 0 and abs(dx) < 390:
                    self.state = "prep"
                    self.timer = 0.42
                    self.vx = 0.0
            elif self.state == "prep" and self.timer <= 0:
                self.state = "dash"
                self.timer = 0.24
                self.vx = self.facing * 840.0
            elif self.state == "dash" and self.timer <= 0:
                self.state = "idle"
                self.timer = 1.05
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < 50:
            self.x = 50.0
            self.vx = 0.0
        elif self.x > WIDTH - 50 - self.w:
            self.x = float(WIDTH - 50 - self.w)
            self.vx = 0.0

        if self.kind not in ("prism_drone", "nova_orb"):
            if self.y + self.h >= FLOOR_Y:
                self.y = float(FLOOR_Y - self.h)
                self.vy = 0.0
        else:
            self.y = max(95.0, min(float(FLOOR_Y - self.h - 20), self.y))

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        flash_col = (255, 255, 255)

        if self.kind == "sentinel":
            col = flash_col if self.flash > 0 else (38, 46, 72)
            pygame.draw.polygon(surf, col, [(r.centerx, r.top), (r.right, r.centery), (r.right - 6, r.bottom), (r.left + 6, r.bottom), (r.left, r.centery)])
            pygame.draw.circle(surf, (255, 115, 135), (r.centerx + self.facing * 8, r.y + 18), 4)

        elif self.kind == "prism_drone":
            col = flash_col if self.flash > 0 else (180, 65, 105)
            blit_glow(surf, r.centerx, r.centery, 36, (255, 95, 135), 65)
            pygame.draw.polygon(surf, col, [(r.centerx, r.top), (r.right, r.centery), (r.centerx, r.bottom), (r.left, r.centery)])
            pygame.draw.circle(surf, (255, 235, 160), r.center, 6)

        elif self.kind == "aegis_warden":
            col = flash_col if self.flash > 0 else (34, 42, 66)
            pygame.draw.rect(surf, col, r, border_radius=10)
            sx = r.right - 2 if self.facing == 1 else r.left - 12
            shield_r = pygame.Rect(sx, r.y + 8, 14, r.height - 14)
            pygame.draw.rect(surf, (135, 225, 255), shield_r, border_radius=4)
            pygame.draw.circle(surf, (255, 130, 145), (r.centerx + self.facing * 8, r.y + 18), 4)

        elif self.kind == "nova_orb":
            col = flash_col if self.flash > 0 else ((255, 95, 70) if self.state == "arming" else (215, 125, 65))
            blit_glow(surf, r.centerx, r.centery, 34, col, 75)
            pygame.draw.circle(surf, col, r.center, self.w // 2)
            pygame.draw.circle(surf, (255, 240, 180), r.center, self.w // 4)

        elif self.kind == "rift_assassin":
            col = flash_col if self.flash > 0 else (68, 36, 105)
            pygame.draw.polygon(surf, col, [(r.centerx, r.top), (r.right, r.bottom), (r.left, r.bottom)])
            pygame.draw.circle(surf, (220, 130, 255), (r.centerx + self.facing * 8, r.y + 20), 4)
            if self.state == "prep":
                pygame.draw.line(surf, (220, 130, 255), r.center, (r.centerx + self.facing * 270, r.centery), 2)


# --- 5 АВТОРСКИХ БОССОВ ---
class Boss:
    TYPES = [
        ("colossus", "АСТРАЛЬНЫЙ КОЛОСС", (235, 155, 65), (255, 225, 145)),
        ("seraph", "СЕРАФИМ ПЕПЛА", (245, 75, 115), (255, 185, 205)),
        ("arbiter", "ХРАНИТЕЛЬ ЧАСОВ", (175, 95, 255), (225, 185, 255)),
        ("leviathan", "ЛЕВИАФАН БЕЗДНЫ", (65, 220, 185), (175, 255, 235)),
        ("solaris", "СОЛЯРИС, СЕРДЦЕ ЗАТМЕНИЯ", (255, 205, 75), (255, 248, 195)),
    ]

    def __init__(self, depth):
        self.depth = depth
        idx = (depth - 1) % len(self.TYPES)
        tier = (depth - 1) // len(self.TYPES)
        self.kind, base_name, self.primary, self.glow = self.TYPES[idx]
        suffix = f" [ЦИКЛ {tier + 1}]" if tier > 0 else ""
        self.name = f"{base_name}{suffix}"

        w, h = (98, 136) if self.kind == "colossus" else ((88, 126) if self.kind == "solaris" else (76, 124))
        start_y = 205 if self.kind == "solaris" else (FLOOR_Y - h)
        self.rect = pygame.Rect(910, start_y, w, h)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = -1

        self.max_hp = int(285 + (depth - 1) * 120)
        self.hp = self.max_hp
        self.poise_hits = 0

        self.state = "idle"
        self.timer = 1.0
        self.flash = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.combo = 0
        self.clone_rect = None
        self.clone_timer = 0.0

    @property
    def phase2(self):
        return self.hp <= self.max_hp * 0.5

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.flash = 0.08
        if self.kind != "solaris":
            self.poise_hits += 1
            if self.poise_hits >= 16 and self.hp > 0 and self.state != "stagger":
                self.poise_hits = 0
                self.state = "stagger"
                self.timer = 1.45
                self.vx = 0.0

    def update(self, dt, hero, projectiles, shockwaves, lasers, particles):
        self.flash = max(0.0, self.flash - dt)
        self.timer -= dt
        spd_mult = (1.24 if self.phase2 else 1.0) + min(0.35, (self.depth - 1) * 0.04)

        if self.clone_timer > 0:
            self.clone_timer -= dt
            if self.clone_timer <= 0:
                self.clone_rect = None

        # 1. АСТРАЛЬНЫЙ КОЛОСС
        if self.kind == "colossus":
            if self.state == "idle":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["slam", "charge", "eruption"])
                    if pick == "slam":
                        self.state = "slam_prep"
                        self.timer = 0.42 / spd_mult
                    elif pick == "charge":
                        self.state = "charge_prep"
                        self.timer = 0.48 / spd_mult
                        self.combo = 2 if self.phase2 else 1
                    else:
                        self.state = "eruption_prep"
                        self.timer = 0.45 / spd_mult
            elif self.state == "slam_prep" and self.timer <= 0:
                self.state = "slam_air"
                self.vy = -1280.0
                self.target_x = float(hero.rect.centerx - self.rect.width // 2)
            elif self.state == "slam_air":
                self.vy += GRAVITY * 0.95 * dt
                self.x += (self.target_x - self.x) * min(1.0, 6.2 * dt)
                if self.y + self.rect.height >= FLOOR_Y and self.vy > 0:
                    self.y = float(FLOOR_Y - self.rect.height)
                    self.vy = 0.0
                    wspd = 520.0 * spd_mult
                    shockwaves.append(Shockwave(self.rect.left, FLOOR_Y, -wspd, color=self.primary))
                    shockwaves.append(Shockwave(self.rect.right, FLOOR_Y, wspd, color=self.primary))
                    for _ in range(5 if self.phase2 else 2):
                        projectiles.append(Projectile(random.randint(120, WIDTH - 120), 60, 0, random.uniform(370, 520), 15, self.glow))
                    self.state = "idle"
                    self.timer = 0.85 / spd_mult
            elif self.state == "charge_prep":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    self.state = "charge"
                    self.timer = 0.36
                    self.vx = self.facing * 900.0 * spd_mult
            elif self.state == "charge" and self.timer <= 0:
                self.vx = 0.0
                self.combo -= 1
                if self.combo > 0:
                    self.state = "charge_prep"
                    self.timer = 0.35 / spd_mult
                else:
                    self.state = "idle"
                    self.timer = 0.75 / spd_mult
            elif self.state == "eruption_prep" and self.timer <= 0:
                wspd = 600.0 * spd_mult
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, self.facing * wspd, height=86, color=self.primary))
                if self.phase2:
                    shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, -self.facing * wspd, height=86, color=self.primary))
                self.state = "idle"
                self.timer = 0.8 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4

        # 2. СЕРАФИМ ПЕПЛА
        elif self.kind == "seraph":
            if self.state == "idle":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["lunge", "chakram", "sky_dive", "feather_nova"])
                    if pick == "lunge":
                        self.state = "lunge_prep"
                        self.timer = 0.4 / spd_mult
                    elif pick == "chakram":
                        self.state = "throw_prep"
                        self.timer = 0.42 / spd_mult
                    elif pick == "sky_dive":
                        self.state = "jump_up"
                        self.vy = -1150.0
                        self.vx = self.facing * 240.0
                    else:
                        self.state = "nova_jump"
                        self.vy = -1050.0
            elif self.state == "lunge_prep":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    self.state = "lunge"
                    self.timer = 0.28
                    self.vx = self.facing * 1080.0 * spd_mult
            elif self.state == "lunge" and self.timer <= 0:
                self.vx = 0.0
                self.state = "idle"
                self.timer = 0.65 / spd_mult
            elif self.state == "throw_prep" and self.timer <= 0:
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, self.facing * 930.0, 0.0, 14, self.glow, boomerang=True, owner=self))
                self.state = "idle"
                self.timer = 1.05 / spd_mult
            elif self.state == "jump_up" and self.vy >= -80:
                self.state = "dive_prep"
                self.timer = 0.28 / spd_mult
                self.vx = 0.0
                self.vy = 0.0
                dx = hero.rect.centerx - self.rect.centerx
                dy = hero.rect.centery - self.rect.centery
                ang = math.atan2(max(80.0, dy), dx)
                self.target_x = math.cos(ang) * 1100.0 * spd_mult
                self.target_y = math.sin(ang) * 1100.0 * spd_mult
            elif self.state == "dive_prep" and self.timer <= 0:
                self.state = "diving"
                self.vx = self.target_x
                self.vy = self.target_y
            elif self.state == "diving" and self.y + self.rect.height >= FLOOR_Y:
                self.y = float(FLOOR_Y - self.rect.height)
                self.vx = 0.0
                self.vy = 0.0
                self.state = "idle"
                self.timer = 0.65 / spd_mult
            elif self.state == "nova_jump" and self.vy >= -60:
                self.state = "nova_active"
                self.timer = 0.72
                self.vx = 0.0
                self.vy = 0.0
                count = 10 if self.phase2 else 6
                for i in range(count):
                    ang = (math.tau / count) * i
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 440, math.sin(ang) * 440, 11, self.primary))
            elif self.state == "nova_active":
                self.vy = 0.0
                if self.timer <= 0:
                    self.state = "idle"
                    self.timer = 0.6
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.35

        # 3. ХРАНИТЕЛЬ ЧАСОВ
        elif self.kind == "arbiter":
            if self.state == "idle":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["chrono_beam", "grid_lasers", "blink"])
                    if pick == "chrono_beam":
                        self.state = "laser_aim"
                        self.timer = 0.72 / spd_mult
                        ang = math.atan2(hero.rect.centery - self.rect.centery, hero.rect.centerx - self.rect.centerx)
                        lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang, warn_time=0.62 / spd_mult, color=self.glow))
                        if self.phase2:
                            lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang + 0.27, warn_time=0.62 / spd_mult, color=self.glow))
                            lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang - 0.27, warn_time=0.62 / spd_mult, color=self.glow))
                    elif pick == "grid_lasers":
                        self.state = "laser_aim"
                        self.timer = 0.78 / spd_mult
                        for lx in (230, 510, 790, 1070):
                            lasers.append(LaserBeam(lx, 40, math.pi / 2, warn_time=0.68 / spd_mult, color=self.primary))
                    else:
                        for _ in range(20):
                            particles.append(Particle(self.rect.centerx, self.rect.centery, random.uniform(-240, 240), random.uniform(-240, 240), self.glow, 7, 0.4, glow=True))
                        self.x = float(random.choice([140, 590, 1020]))
                        self.state = "idle"
                        self.timer = 0.48 / spd_mult
            elif self.state == "laser_aim" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.85 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4

        # 4. ЛЕВИАФАН БЕЗДНЫ
        elif self.kind == "leviathan":
            if self.state == "idle":
                self.facing = 1 if hero.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["dash_lance", "sky_pierce", "tidal_blades"])
                    if pick == "dash_lance":
                        self.state = "dash_prep"
                        self.timer = 0.38 / spd_mult
                        if self.phase2:
                            cx = 1120 if self.x < 600 else 90
                            self.clone_rect = pygame.Rect(cx, FLOOR_Y - self.rect.height, self.rect.width, self.rect.height)
                            self.clone_timer = 0.75
                    elif pick == "sky_pierce":
                        self.x = float(max(80, min(WIDTH - 160, hero.rect.centerx - self.rect.width // 2)))
                        self.y = 110.0
                        self.vy = 0.0
                        self.state = "drop_prep"
                        self.timer = 0.36 / spd_mult
                    else:
                        self.state = "blades_prep"
                        self.timer = 0.42 / spd_mult
            elif self.state == "dash_prep" and self.timer <= 0:
                self.state = "dashing"
                self.timer = 0.3
                self.vx = self.facing * 1090.0 * spd_mult
                if self.clone_rect:
                    cdir = 1 if hero.rect.centerx > self.clone_rect.centerx else -1
                    projectiles.append(Projectile(self.clone_rect.centerx, self.clone_rect.centery, cdir * 630.0, 0, 14, self.glow))
            elif self.state == "dashing" and self.timer <= 0:
                self.vx = 0.0
                self.state = "idle"
                self.timer = 0.62 / spd_mult
            elif self.state == "drop_prep":
                self.vy = 0.0
                if self.timer <= 0:
                    self.state = "dropping"
                    self.vy = 1400.0
            elif self.state == "dropping" and self.y + self.rect.height >= FLOOR_Y:
                self.y = float(FLOOR_Y - self.rect.height)
                self.vy = 0.0
                shockwaves.append(Shockwave(self.rect.left, FLOOR_Y, -550.0, height=50, color=self.primary))
                shockwaves.append(Shockwave(self.rect.right, FLOOR_Y, 550.0, height=50, color=self.primary))
                self.state = "idle"
                self.timer = 0.62 / spd_mult
            elif self.state == "blades_prep" and self.timer <= 0:
                for row_y in (FLOOR_Y - 34, FLOOR_Y - 115):
                    projectiles.append(Projectile(self.rect.centerx, row_y, self.facing * 570.0 * spd_mult, 0, 13, self.glow))
                self.state = "idle"
                self.timer = 0.72 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.35

        # 5. СОЛЯРИС, СЕРДЦЕ ЗАТМЕНИЯ
        elif self.kind == "solaris":
            hover_x = 640 + math.sin(pygame.time.get_ticks() * 0.0014) * 320 - self.rect.width // 2
            hover_y = 180 + math.cos(pygame.time.get_ticks() * 0.0022) * 34
            self.x += (hover_x - self.x) * min(1.0, 2.2 * dt)
            self.y += (hover_y - self.y) * min(1.0, 2.5 * dt)
            self.vy = 0.0

            if self.state == "idle" and self.timer <= 0:
                pick = random.choice(["corona_burst", "eclipse_wall", "star_seekers", "constellation"])
                if pick == "corona_burst":
                    count = 12 if self.phase2 else 8
                    base = random.uniform(0, 0.5)
                    for i in range(count):
                        ang = base + (math.tau / count) * i
                        projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 435, math.sin(ang) * 435, 12, self.glow))
                    self.timer = 1.15 / spd_mult
                elif pick == "eclipse_wall":
                    side = random.choice([-1, 1])
                    sx = 80 if side == 1 else WIDTH - 80
                    for py in range(150, FLOOR_Y, 85):
                        if abs(py - (FLOOR_Y - 140)) > 60:
                            projectiles.append(Projectile(sx, py, side * 425 * spd_mult, 0, 14, self.primary))
                    self.timer = 1.35 / spd_mult
                elif pick == "star_seekers":
                    for _ in range(3 if self.phase2 else 2):
                        projectiles.append(Projectile(self.rect.centerx + random.uniform(-120, 120), self.rect.centery, random.uniform(-180, 180), -120, 14, (255, 235, 145), homing=True))
                    self.timer = 1.4 / spd_mult
                elif pick == "constellation":
                    count = 6 if self.phase2 else 4
                    base = random.uniform(0.2, 1.2)
                    for i in range(count):
                        ang = base + (math.pi / count) * i
                        lasers.append(LaserBeam(self.rect.centerx, self.rect.centery, ang, warn_time=0.72 / spd_mult, color=self.glow))
                    self.timer = 1.3 / spd_mult

        if self.kind != "solaris" and self.state not in ("slam_air", "diving", "nova_active", "drop_prep"):
            self.vy = min(1150.0, self.vy + GRAVITY * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < 55:
            self.x = 55.0
            self.vx = 0.0
        elif self.x > WIDTH - 55 - self.rect.width:
            self.x = float(WIDTH - 55 - self.rect.width)
            self.vx = 0.0

        if self.kind != "solaris" and self.y + self.rect.height >= FLOOR_Y:
            self.y = float(FLOOR_Y - self.rect.height)
            self.vy = 0.0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surf, ox, oy):
        t = pygame.time.get_ticks() * 0.003
        if self.clone_rect:
            cr = self.clone_rect.move(int(ox), int(oy))
            blit_glow(surf, cr.centerx, cr.centery, 65, self.glow, 70)
            pygame.draw.polygon(surf, (45, 25, 75), [(cr.centerx, cr.top), (cr.right, cr.centery), (cr.centerx, cr.bottom), (cr.left, cr.centery)])
            pygame.draw.polygon(surf, self.glow, [(cr.centerx, cr.top), (cr.right, cr.centery), (cr.centerx, cr.bottom), (cr.left, cr.centery)], 3)

        r = self.rect.move(int(ox), int(oy))
        if self.state == "stagger":
            r = pygame.Rect(r.x, r.y + 34, r.width, r.height - 34)

        blit_glow(surf, r.centerx, r.centery, 95 if self.phase2 else 75, self.primary, 85)
        body_col = (255, 255, 255) if self.flash > 0 else (24, 20, 38)
        trim_col = (255, 255, 255) if self.flash > 0 else self.primary

        # Вращающиеся астрономические кольца за спиной босса
        ring_r = 68 if self.phase2 else 54
        pygame.draw.circle(surf, self.glow, r.center, ring_r, 2)
        for i in range(4):
            ang = t * (1.5 if self.phase2 else 0.9) + i * (math.pi / 2)
            ox_r = r.centerx + int(math.cos(ang) * ring_r)
            oy_r = r.centery + int(math.sin(ang) * ring_r)
            pygame.draw.circle(surf, self.glow, (ox_r, oy_r), 5)

        # Крылья для Серафима и Соляриса
        if self.kind in ("seraph", "solaris"):
            flap = math.sin(t * 2.2) * 14
            for side in (-1, 1):
                wx = r.right if side == 1 else r.left
                pygame.draw.polygon(surf, self.primary, [(wx, r.centery - 10), (wx + side * 66, r.top - 22 + flap), (wx + side * 44, r.centery + 10)])
                pygame.draw.polygon(surf, self.glow, [(wx, r.centery + 6), (wx + side * 52, r.centery + 24 - flap), (wx + side * 24, r.bottom)])

        # Многогранный силуэт доспеха
        chassis = [
            (r.centerx, r.top),
            (r.right, r.top + 28),
            (r.right - 8, r.bottom),
            (r.left + 8, r.bottom),
            (r.left, r.top + 28),
        ]
        pygame.draw.polygon(surf, body_col, chassis)
        pygame.draw.polygon(surf, trim_col, chassis, 3)

        # Корона / Визор
        crown = [(r.centerx - 18, r.top + 22), (r.centerx - 12, r.top - 14), (r.centerx, r.top + 10), (r.centerx + 12, r.top - 14), (r.centerx + 18, r.top + 22)]
        pygame.draw.polygon(surf, trim_col, crown)
        eye_x = r.centerx + self.facing * 10
        pygame.draw.line(surf, (255, 250, 255), (eye_x - 10, r.top + 32), (eye_x + 10, r.top + 32), 4)

        if self.state in ("charge_prep", "lunge_prep", "dash_prep"):
            pygame.draw.line(surf, self.glow, (r.centerx, r.centery), (r.centerx + self.facing * 560, r.centery), 3)


# --- ГЕНЕРАТОР КОМНАТ ---
def build_room(depth, room_idx):
    platforms, hazards, clusters, enemies = [], [], [], []
    obelisk_rect = None

    if room_idx == 0:
        obelisk_rect = pygame.Rect(610, FLOOR_Y - 128, 60, 128)
        platforms = [Platform(220, 445, 200), Platform(860, 445, 200)]
        return "sanctuary", platforms, hazards, clusters, enemies, obelisk_rect

    if room_idx in (1, 2):
        layout = (depth + room_idx) % 3
        if layout == 0:
            platforms = [Platform(180, 465, 220), Platform(530, 350, 220), Platform(880, 465, 220)]
            hazards = [CrystalHazard(440, FLOOR_Y, 400)]
            clusters = [LumenCluster(640, 350)]
        elif layout == 1:
            platforms = [Platform(140, 475, 210), Platform(430, 375, 190), Platform(720, 285, 210), Platform(950, 440, 210)]
            hazards = [CrystalHazard(355, FLOOR_Y, 220), CrystalHazard(745, FLOOR_Y, 220)]
            clusters = [LumenCluster(825, 285), LumenCluster(1055, FLOOR_Y)]
        else:
            platforms = [Platform(210, 435, 240), Platform(830, 435, 240), Platform(510, 310, 260)]
            hazards = [CrystalHazard(300, FLOOR_Y, 680)]
            clusters = [LumenCluster(640, 310)]

        pool = ["sentinel", "prism_drone", "aegis_warden", "nova_orb", "rift_assassin"]
        count = min(6, 3 + depth // 2)
        for i in range(count):
            kind = random.choice(pool)
            ex = 480 + i * 135 + random.randint(-30, 30)
            ey = 210 if kind in ("prism_drone", "nova_orb") else (FLOOR_Y - 78)
            enemies.append(Enemy(kind, min(WIDTH - 130, ex), ey, depth))
        return "combat", platforms, hazards, clusters, enemies, None

    boss_kind = Boss.TYPES[(depth - 1) % len(Boss.TYPES)][0]
    if boss_kind == "solaris":
        platforms = [Platform(160, 465, 210), Platform(535, 410, 210), Platform(910, 465, 210), Platform(340, 300, 180), Platform(760, 300, 180)]
    else:
        platforms = [Platform(200, 450, 190), Platform(890, 450, 190)]
    return "boss", platforms, hazards, clusters, enemies, None


# --- ОТРИСОВКА МНОГОСЛОЙНОГО МИРА И ЗЕРКАЛЬНОГО ПОЛА ---
def draw_backdrop(surf, sky_surf, biome, ox, oy, obelisk_rect, gate_open):
    surf.blit(sky_surf, (0, 0))
    t = pygame.time.get_ticks() * 0.001

    # Небесное светило / Астролябия / Затмение на заднем плане
    cx, cy = int(WIDTH * 0.5 + ox * 0.15), int(235 + oy * 0.15)
    blit_glow(surf, cx, cy, 240, biome["accent_soft"], 75)
    if biome["weather"] == "eclipse":
        pygame.draw.circle(surf, (255, 225, 130), (cx, cy), 84)
        pygame.draw.circle(surf, (12, 10, 20), (cx, cy), 76)
    else:
        pygame.draw.circle(surf, biome["arch_rim"], (cx, cy), 125, 2)
        pygame.draw.circle(surf, biome["arch_rim"], (cx, cy), 85, 1)
        for i in range(6):
            ang = t * 0.35 + i * (math.pi / 3)
            px = cx + int(math.cos(ang) * 125)
            py = cy + int(math.sin(ang) * 125)
            pygame.draw.circle(surf, biome["accent"], (px, py), 4)

    # Дальний слой силуэтов гор/руин (параллакс 0.25)
    for i in range(-1, 7):
        bx = int(i * 230 + ox * 0.25)
        pts = [(bx, FLOOR_Y), (bx + 90, 320 + (i % 3) * 45), (bx + 180, 370), (bx + 250, FLOOR_Y)]
        pygame.draw.polygon(surf, biome["arch"], pts)

    # Ближние готические арки и колонны (параллакс 0.45)
    for px in (150, 450, 830, 1130):
        rx = int(px - 26 + ox * 0.45)
        pygame.draw.rect(surf, biome["arch"], (rx, 0, 52, FLOOR_Y))
        pygame.draw.line(surf, biome["arch_rim"], (rx, 0), (rx, FLOOR_Y), 2)
        pygame.draw.line(surf, biome["arch_rim"], (rx + 52, 0), (rx + 52, FLOOR_Y), 1)

    # Обелиск Гармонии в Святилище
    if obelisk_rect:
        or_r = obelisk_rect.move(int(ox), int(oy))
        blit_glow(surf, or_r.centerx, or_r.centery - 15, 95, biome["accent"], 90)
        pts = [(or_r.centerx, or_r.top), (or_r.right, or_r.top + 32), (or_r.right - 8, or_r.bottom), (or_r.left + 8, or_r.bottom), (or_r.left, or_r.top + 32)]
        pygame.draw.polygon(surf, (24, 32, 52), pts)
        pygame.draw.polygon(surf, biome["accent"], pts, 3)
        float_y = or_r.top + 54 + int(math.sin(t * 3.5) * 6)
        pygame.draw.polygon(surf, (255, 255, 255), [(or_r.centerx, float_y - 12), (or_r.centerx + 9, float_y), (or_r.centerx, float_y + 12), (or_r.centerx - 9, float_y)])

    # Правый портал перехода
    gx = WIDTH - 42 + int(ox)
    gtop = FLOOR_Y - 170 + int(oy)
    if gate_open:
        blit_glow(surf, gx + 6, gtop + 85, 70, biome["accent"], 95)
        pygame.draw.rect(surf, biome["accent"], (gx, gtop, 12, 170), border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), (gx + 4, gtop + 14, 4, 142), border_radius=2)
    else:
        pygame.draw.rect(surf, (215, 65, 95), (gx, gtop, 12, 170), border_radius=5)


def draw_reflective_floor(surf, floor_surf, entity_layer, biome, ox, oy):
    fy = int(FLOOR_Y + oy)
    surf.blit(floor_surf, (int(-30 + ox), fy))

    # Зеркальное отражение всего боевого слоя на полу!
    ref_h = min(HEIGHT - fy, 130)
    if ref_h > 10:
        crop = entity_layer.subsurface((0, max(0, FLOOR_Y - ref_h), WIDTH, ref_h))
        flipped = pygame.transform.flip(crop, False, True)
        flipped.set_alpha(58)
        surf.blit(flipped, (int(ox), fy + 2))

    # Светящаяся кромка воды/обсидиана
    pygame.draw.line(surf, biome["accent"], (0, fy), (WIDTH, fy), 3)
    pygame.draw.line(surf, (255, 255, 255), (0, fy), (WIDTH, fy), 1)


# --- ИНТЕРФЕЙС (HUD) И МЕНЮ РЕЛИКВИЙ ---
def draw_hud(surf, hero, boss, depth, room_idx, biome):
    f_title = get_font(21, bold=True)
    f_small = get_font(16)
    f_tiny = get_font(14)

    # Сфера Эфира
    sc = (56, 54)
    blit_glow(surf, sc[0], sc[1], 46, (85, 225, 245), 65)
    pygame.draw.circle(surf, (18, 24, 40), sc, 33)
    ratio = hero.aether / hero.max_aether
    if ratio > 0:
        pygame.draw.circle(surf, (105, 235, 255), sc, int(29 * math.sqrt(ratio)))
        pygame.draw.circle(surf, (235, 252, 255), sc, int(16 * math.sqrt(ratio)))
    pygame.draw.circle(surf, (175, 210, 245), sc, 33, 3)

    # Ячейки прочности (Ромбы HP)
    for i in range(hero.max_hp):
        mx = 114 + i * 32
        my = 38
        pts = [(mx, my - 13), (mx + 11, my), (mx, my + 13), (mx - 11, my)]
        if i < hero.hp:
            col = (255, 215, 115) if i >= hero.base_max_hp else (115, 235, 255)
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (255, 255, 255), pts, 2)
        else:
            pygame.draw.polygon(surf, (45, 56, 82), pts, 2)

    # Счётчик Люмена и Индикатор Резонанса
    pygame.draw.polygon(surf, (215, 250, 255), [(114, 68), (121, 76), (114, 84), (107, 76)])
    surf.blit(f_title.render(f"{hero.lumen}", True, (240, 248, 255)), (130, 63))

    tier_names = ["ПОТОК x1.0", "ПОТОК x1.15", "ПОТОК x1.3", "OVERDRIVE x1.5"]
    tier_cols = [(145, 165, 195), (105, 235, 255), (185, 140, 255), (255, 215, 105)]
    t_idx = hero.resonance_tier
    res_bar_x, res_bar_y, res_bar_w = 225, 71, 160
    pygame.draw.rect(surf, (22, 28, 44), (res_bar_x, res_bar_y, res_bar_w, 10), border_radius=5)
    pygame.draw.rect(surf, tier_cols[t_idx], (res_bar_x, res_bar_y, int(res_bar_w * (hero.resonance / 100.0)), 10), border_radius=5)
    surf.blit(f_small.render(f"{tier_names[t_idx]} ({hero.combo_count} уд.)", True, tier_cols[t_idx]), (res_bar_x + res_bar_w + 12, 65))

    # Информация о биоме справа сверху
    stage_names = ["Святилище", "Зал I", "Зал II", "Чертог Босса"]
    loc_txt = f_small.render(f"Этаж {depth}: {biome['name']}  |  {stage_names[room_idx]}", True, (205, 222, 248))
    surf.blit(loc_txt, (WIDTH - loc_txt.get_width() - 26, 24))

    ctrl_txt = f_tiny.render("ЛКМ/J: Комбо (S+Удар: отскок)  |  ПКМ/Shift: Рывок  |  СКМ/Q: Парирование  |  E: Искусство  |  F: Лечение  |  TAB: Реликвии", True, (135, 155, 185))
    surf.blit(ctrl_txt, (WIDTH - ctrl_txt.get_width() - 26, 48))

    # Полоска HP босса
    if boss and boss.hp > 0:
        bw, bh = 740, 16
        bx = (WIDTH - bw) // 2
        by = HEIGHT - 46
        t = f_title.render(boss.name, True, (245, 248, 255))
        surf.blit(t, ((WIDTH - t.get_width()) // 2, by - 30))
        pygame.draw.rect(surf, (18, 20, 32), (bx, by, bw, bh), border_radius=6)
        hw = int(bw * (boss.hp / boss.max_hp))
        if hw > 0:
            pygame.draw.rect(surf, boss.primary, (bx, by, hw, bh), border_radius=6)
        pygame.draw.rect(surf, (175, 190, 220), (bx, by, bw, bh), 2, border_radius=6)


def draw_shrine_menu(surf, hero, tab_idx, selected_idx, at_obelisk):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((6, 9, 18, 218))
    surf.blit(ov, (0, 0))

    panel = pygame.Rect(140, 72, WIDTH - 280, HEIGHT - 144)
    pygame.draw.rect(surf, (15, 20, 34), panel, border_radius=16)
    pygame.draw.rect(surf, (95, 215, 245), panel, 2, border_radius=16)

    f_head = get_font(26, bold=True)
    f_med = get_font(19, bold=True)
    f_reg = get_font(17)

    title_str = "ОБЕЛИСК ГАРМОНИИ (Настройка Реликвий и Улучшений)" if at_obelisk else "ОБЗОР РЕЛИКВИЙ (Подойди к Обелиску в Святилище, чтобы менять билд)"
    surf.blit(f_head.render(title_str, True, (242, 248, 255)), (panel.left + 30, panel.top + 20))

    tabs = ["[1] Реликвии Синергии", "[2] Ковка и Характеристики"]
    for i, tname in enumerate(tabs):
        col = (105, 235, 255) if i == tab_idx else (130, 145, 175)
        surf.blit(f_med.render(tname, True, col), (panel.left + 30 + i * 260, panel.top + 66))

    info = f_med.render(f"Ячейки: {hero.used_slots()}/{hero.max_slots}   |   Люмен: {hero.lumen}", True, (255, 220, 115))
    surf.blit(info, (panel.right - info.get_width() - 30, panel.top + 66))
    pygame.draw.line(surf, (48, 64, 96), (panel.left + 24, panel.top + 102), (panel.right - 24, panel.top + 102), 2)

    if tab_idx == 0:
        for idx, rel in enumerate(RELICS):
            col_i = idx % 2
            row_i = idx // 2
            bx = panel.left + 32 + col_i * 468
            by = panel.top + 120 + row_i * 58
            box = pygame.Rect(bx, by, 448, 48)

            is_sel = idx == selected_idx
            is_eq = rel["id"] in hero.equipped
            bg_col = (30, 44, 70) if is_sel else (21, 28, 44)
            border_col = (110, 235, 255) if is_sel else ((115, 240, 175) if is_eq else (48, 60, 86))
            pygame.draw.rect(surf, bg_col, box, border_radius=9)
            pygame.draw.rect(surf, border_col, box, 2, border_radius=9)

            c_col = rel["color"] if rel["unlocked"] else (68, 76, 94)
            pygame.draw.polygon(surf, c_col, [(bx + 24, by + 12), (bx + 35, by + 24), (bx + 24, by + 36), (bx + 13, by + 24)])
            status = "[АКТИВНА]" if is_eq else (f"{rel['slots']} яч." if rel["unlocked"] else f"Открыть: {rel['cost']} Люм.")
            surf.blit(f_med.render(rel["name"], True, (245, 248, 255) if rel["unlocked"] else (150, 160, 180)), (bx + 46, by + 11))
            st_img = f_reg.render(status, True, (125, 245, 180) if is_eq else (255, 215, 115))
            surf.blit(st_img, (box.right - st_img.get_width() - 14, by + 13))

        cur = RELICS[selected_idx % len(RELICS)]
        desc_r = pygame.Rect(panel.left + 32, panel.bottom - 88, panel.width - 64, 42)
        pygame.draw.rect(surf, (22, 30, 48), desc_r, border_radius=8)
        surf.blit(f_reg.render(f"{cur['name']} ({cur['slots']} яч.): {cur['desc']}", True, (215, 238, 255)), (desc_r.left + 16, desc_r.top + 10))
    else:
        upgrades = [
            ("Закалка Астрального Клинка (+4 к базовому урону)", 110 + (hero.base_damage - 16) * 20, f"Базовый урон: {hero.base_damage}"),
            ("Кристалл Прочности (+1 ячейка здоровья)", 140 + (hero.base_max_hp - 6) * 65, f"Макс. прочность: {hero.max_hp}"),
            ("Слот Резонанса (+1 ячейка для реликвий)", 130 + (hero.max_slots - 4) * 55, f"Всего ячеек: {hero.max_slots}/12"),
            ("Сосуд Эфира (+25 к запасу энергии)", 120 + int((hero.max_aether - 100) * 2), f"Макс. Эфир: {int(hero.max_aether)}"),
        ]
        for idx, (title, cost, cur_val) in enumerate(upgrades):
            by = panel.top + 135 + idx * 78
            box = pygame.Rect(panel.left + 38, by, panel.width - 76, 62)
            is_sel = idx == (selected_idx % len(upgrades))
            pygame.draw.rect(surf, (30, 44, 70) if is_sel else (21, 28, 44), box, border_radius=10)
            pygame.draw.rect(surf, (110, 235, 255) if is_sel else (50, 64, 92), box, 2, border_radius=10)
            surf.blit(f_med.render(title, True, (242, 248, 255)), (box.left + 20, box.top + 10))
            surf.blit(f_reg.render(cur_val, True, (155, 200, 235)), (box.left + 20, box.top + 35))
            c_img = f_med.render(f"Улучшить: {cost} Люмена", True, (255, 220, 115))
            surf.blit(c_img, (box.right - c_img.get_width() - 22, box.top + 18))

    foot = f_reg.render("WASD / Стрелки: Выбор   |   Enter / Пробел: Активировать или Купить   |   ESC / TAB: Закрыть", True, (165, 190, 220))
    surf.blit(foot, ((WIDTH - foot.get_width()) // 2, panel.bottom - 34))


# --- ОСНОВНОЙ ЦИКЛ ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AETHERFALL: RESONANCE")
    clock = pygame.time.Clock()
    entity_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    f_big = get_font(58, bold=True)
    f_med = get_font(24, bold=True)
    f_prompt = get_font(19, bold=True)

    fullscreen = False
    game_state = "title"

    def init_run():
        for r in RELICS:
            r["unlocked"] = r["cost"] == 0
        h = Hero()
        h.recalculate_stats()
        rtype, plats, hazs, clsts, enms, ob_rect = build_room(1, 0)
        b = BIOMES[0]
        motes = [WeatherMote(b) for _ in range(38)]
        return h, 1, 0, rtype, plats, hazs, clsts, enms, ob_rect, None, build_sky_surface(b), build_floor_surface(b), motes

    hero, depth, room_idx, room_type, platforms, hazards, clusters, enemies, obelisk_rect, boss, sky_surf, floor_surf, motes = init_run()

    particles, afterimages, slash_arcs, floating_texts = [], [], [], []
    lumen_crystals, shockwaves, projectiles, lasers, arts = [], [], [], [], []

    hitstop = 0.0
    shake = 0.0
    banner_timer = 0.0
    banner_text = ""
    menu_tab = 0
    menu_sel = 0
    at_obelisk = False

    def enter_room(new_depth, new_room_idx):
        nonlocal depth, room_idx, room_type, platforms, hazards, clusters, enemies, obelisk_rect, boss
        nonlocal sky_surf, floor_surf, motes, banner_timer, banner_text
        depth = new_depth
        room_idx = new_room_idx
        biome = BIOMES[(depth - 1) % len(BIOMES)]
        if room_idx == 0:
            sky_surf = build_sky_surface(biome)
            floor_surf = build_floor_surface(biome)
            motes = [WeatherMote(biome) for _ in range(38)]

        room_type, platforms, hazards, clusters, enemies, obelisk_rect = build_room(depth, room_idx)
        shockwaves.clear()
        projectiles.clear()
        lasers.clear()
        arts.clear()
        slash_arcs.clear()

        hero.x = 85.0
        hero.y = float(FLOOR_Y - hero.rect.height)
        hero.vx = 0.0
        hero.vy = 0.0
        hero.rect.topleft = (int(hero.x), int(hero.y))

        if room_type == "boss":
            boss = Boss(depth)
            banner_text = boss.name
            banner_timer = 2.1
        else:
            boss = None
            if room_idx == 0:
                banner_text = f"ЭТАЖ {depth}  |  {biome['name']}"
                banner_timer = 1.9

    while True:
        dt = min(0.04, clock.tick(FPS) / 1000.0)
        keys = pygame.key.get_pressed()
        biome = BIOMES[(depth - 1) % len(BIOMES)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscreen else 0)

                if game_state == "title":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "playing"
                        banner_text = f"ЭТАЖ 1  |  {biome['name']}"
                        banner_timer = 2.0

                elif game_state == "game_over":
                    if event.key == pygame.K_r:
                        hero, depth, room_idx, room_type, platforms, hazards, clusters, enemies, obelisk_rect, boss, sky_surf, floor_surf, motes = init_run()
                        particles.clear()
                        afterimages.clear()
                        slash_arcs.clear()
                        floating_texts.clear()
                        lumen_crystals.clear()
                        shockwaves.clear()
                        projectiles.clear()
                        lasers.clear()
                        arts.clear()
                        game_state = "playing"

                elif game_state == "shrine_menu":
                    if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                        game_state = "playing"
                    elif event.key == pygame.K_1:
                        menu_tab = 0
                        menu_sel = 0
                    elif event.key == pygame.K_2:
                        menu_tab = 1
                        menu_sel = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        step = 2 if menu_tab == 0 else 1
                        menu_sel = (menu_sel - step) % (len(RELICS) if menu_tab == 0 else 4)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        step = 2 if menu_tab == 0 else 1
                        menu_sel = (menu_sel + step) % (len(RELICS) if menu_tab == 0 else 4)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and menu_tab == 0:
                        menu_sel = (menu_sel - 1) % len(RELICS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and menu_tab == 0:
                        menu_sel = (menu_sel + 1) % len(RELICS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and at_obelisk:
                        if menu_tab == 0:
                            rel = RELICS[menu_sel]
                            if not rel["unlocked"]:
                                if hero.lumen >= rel["cost"]:
                                    hero.lumen -= rel["cost"]
                                    rel["unlocked"] = True
                            else:
                                if rel["id"] in hero.equipped:
                                    hero.equipped.remove(rel["id"])
                                elif hero.used_slots() + rel["slots"] <= hero.max_slots:
                                    hero.equipped.append(rel["id"])
                                hero.recalculate_stats()
                                hero.hp = hero.max_hp
                        else:
                            idx = menu_sel % 4
                            if idx == 0:
                                cost = 110 + (hero.base_damage - 16) * 20
                                if hero.lumen >= cost:
                                    hero.lumen -= cost
                                    hero.base_damage += 4
                            elif idx == 1:
                                cost = 140 + (hero.base_max_hp - 6) * 65
                                if hero.lumen >= cost and hero.base_max_hp < 12:
                                    hero.lumen -= cost
                                    hero.base_max_hp += 1
                                    hero.recalculate_stats()
                                    hero.hp = hero.max_hp
                            elif idx == 2:
                                cost = 130 + (hero.max_slots - 4) * 55
                                if hero.lumen >= cost and hero.max_slots < 12:
                                    hero.lumen -= cost
                                    hero.max_slots += 1
                            elif idx == 3:
                                cost = 120 + int((hero.max_aether - 100) * 2)
                                if hero.lumen >= cost and hero.max_aether < 200:
                                    hero.lumen -= cost
                                    hero.max_aether += 25.0
                                    hero.aether = hero.max_aether

                elif game_state == "playing":
                    if event.key == pygame.K_TAB:
                        at_obelisk = False
                        game_state = "shrine_menu"

                    if room_type == "sanctuary" and obelisk_rect and hero.rect.colliderect(obelisk_rect.inflate(46, 20)):
                        if event.key in (pygame.K_w, pygame.K_e):
                            hero.hp = hero.max_hp
                            hero.aether = hero.max_aether
                            at_obelisk = True
                            game_state = "shrine_menu"
                            continue

                    if event.key == pygame.K_SPACE and (keys[pygame.K_s] or keys[pygame.K_DOWN]) and hero.on_ground and hero.y + hero.rect.height < FLOOR_Y - 5:
                        hero.drop_through_timer = 0.22
                        hero.on_ground = False
                    elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        if hero.jumps_left > 0 and hero.dash_timer <= 0 and not hero.dive_active:
                            hero.vy = -810.0
                            hero.jumps_left -= 1
                            hero.on_ground = False
                            hero.jump_held = True
                            for _ in range(10):
                                particles.append(Particle(hero.rect.centerx + random.uniform(-12, 12), hero.rect.bottom, random.uniform(-110, 110), random.uniform(20, 110), (145, 235, 255), 5, 0.3, glow=True))

                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k):
                        if hero.start_dash():
                            shake = max(shake, 4.0)

                    elif event.key == pygame.K_j:
                        hero.start_slash(keys, slash_arcs, projectiles)

                    elif event.key in (pygame.K_q, pygame.K_c):
                        hero.start_parry()

                    elif event.key == pygame.K_e:
                        if hero.cast_art(keys, arts, particles):
                            shake = max(shake, 7.0)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    hero.jump_held = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
                if event.button == 1:
                    hero.start_slash(keys, slash_arcs, projectiles)
                elif event.button == 3:
                    if hero.start_dash():
                        shake = max(shake, 4.0)
                elif event.button == 2:
                    hero.start_parry()

        # --- ОБНОВЛЕНИЕ ЛОГИКИ ---
        if game_state == "playing":
            banner_timer = max(0.0, banner_timer - dt)
            for m in motes:
                m.update(dt)

            if hitstop > 0:
                hitstop -= dt
            else:
                hero.update(dt, keys, platforms, particles, afterimages, arts, shockwaves, slash_arcs)

                # Обработка отложенного Эхо-Клинка
                if hero.pending_echo:
                    delay, e_rect, e_dir = hero.pending_echo
                    delay -= dt
                    if delay <= 0:
                        hero.pending_echo = None
                        slash_arcs.append(SlashArc(e_rect, e_dir, (195, 145, 255), is_echo=True))
                        edmg = max(4, int(hero.blade_damage * 0.55))
                        for en in enemies:
                            if e_rect.colliderect(en.rect):
                                en.hp -= edmg
                                en.flash = 0.06
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 8, edmg, (205, 160, 255), 17))
                        if boss and boss.hp > 0 and e_rect.colliderect(boss.rect):
                            boss.take_damage(edmg)
                            floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 12, edmg, (205, 160, 255), 18))
                    else:
                        hero.pending_echo = (delay, e_rect, e_dir)

                for cl in clusters:
                    cl.update(dt)
                for en in enemies:
                    en.update(dt, hero, projectiles)
                if boss and boss.hp > 0:
                    boss.update(dt, hero, projectiles, shockwaves, lasers, particles)

                for sw in shockwaves:
                    sw.update(dt)
                for pr in projectiles:
                    target = boss if (pr.friendly and boss and boss.hp > 0) else (enemies[0] if (pr.friendly and enemies) else hero)
                    pr.update(dt, target)
                for lz in lasers:
                    lz.update(dt)
                for ar in arts:
                    ar.update(dt)
                for lc in lumen_crystals:
                    lc.update(dt, hero, magnet=hero.has_relic("lumen_magnet"))
                for pt in particles:
                    pt.update(dt)
                for ai in afterimages:
                    ai.update(dt)
                for sa in slash_arcs:
                    sa.update(dt)
                for ft in floating_texts:
                    ft.update(dt)

                shockwaves = [s for s in shockwaves if s.life > 0]
                projectiles = [p for p in projectiles if p.life > 0 and -50 <= p.x <= WIDTH + 50 and p.y <= FLOOR_Y + 25]
                lasers = [l for l in lasers if l.timer > 0]
                arts = [a for a in arts if a.life > 0 and -250 <= a.x <= WIDTH + 250]
                particles = [p for p in particles if p.life > 0]
                afterimages = [a for a in afterimages if a.life > 0]
                slash_arcs = [s for s in slash_arcs if s.life > 0]
                floating_texts = [f for f in floating_texts if f.life > 0]

                # Сбор Люмена
                for lc in list(lumen_crystals):
                    if lc.life <= 0:
                        lumen_crystals.remove(lc)
                    elif hero.rect.colliderect(lc.rect.inflate(14, 14)):
                        bonus = int(round(lc.value * (1.3 if hero.has_relic("lumen_magnet") else 1.0)))
                        hero.lumen += bonus
                        lumen_crystals.remove(lc)

                # Попадания клинка
                s_rect = hero.get_slash_rect()
                aether_gain = 16.0 if hero.has_relic("crystal_reaper") else 11.5
                vault_vy = -805.0

                if s_rect:
                    # Отскок от кристальных шипов
                    if hero.slash_dir == "down":
                        for hz in hazards:
                            if s_rect.colliderect(hz.rect):
                                hero.vy = vault_vy
                                hero.reset_air_mobility()
                                for _ in range(8):
                                    particles.append(Particle(hero.rect.centerx, hz.rect.top, random.uniform(-160, 160), random.uniform(-220, -40), biome["accent"], 4, 0.25, glow=True))
                                break

                    # Кристальные друзы
                    for cl in clusters:
                        if cl.hp > 0 and s_rect.colliderect(cl.rect) and id(cl) not in hero.hit_ids:
                            hero.hit_ids.add(id(cl))
                            cl.hp -= 1
                            cl.flash = 0.08
                            shake = max(shake, 5.0)
                            for _ in range(4 if cl.hp > 0 else 10):
                                lumen_crystals.append(LumenCrystal(cl.rect.centerx, cl.rect.centery, 6))

                    # Враги
                    for en in list(enemies):
                        if s_rect.colliderect(en.rect) and id(en) not in hero.hit_ids:
                            hero.hit_ids.add(id(en))
                            blocked = (
                                en.kind == "aegis_warden"
                                and hero.slash_dir in ("left", "right")
                                and ((en.facing == -1 and hero.rect.centerx < en.rect.centerx) or (en.facing == 1 and hero.rect.centerx > en.rect.centerx))
                            )
                            if blocked:
                                hero.vx = -hero.facing * 320.0
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, "ЩИТ!", (140, 225, 255), 18))
                            else:
                                dmg = hero.blade_damage
                                en.hp -= dmg
                                en.flash = 0.08
                                hero.aether = min(hero.max_aether, hero.aether + aether_gain)
                                hero.add_resonance(12.0)
                                hero.combo_count += 1
                                hitstop = 0.026
                                shake = max(shake, 6.0)
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, dmg, (255, 255, 255), 20))
                                if hero.slash_dir == "down":
                                    hero.vy = vault_vy
                                    hero.reset_air_mobility()
                                    if hero.has_relic("astral_vortex"):
                                        arts.append(AstralArtBlast(hero.rect.centerx - 90, hero.rect.centery - 90, 180, 180, 0, 0, int(dmg * 0.8), 0.18, "nova"))
                                else:
                                    en.vx += hero.facing * 260.0

                    # Босс
                    if boss and boss.hp > 0 and s_rect.colliderect(boss.rect) and id(boss) not in hero.hit_ids:
                        hero.hit_ids.add(id(boss))
                        dmg = hero.blade_damage
                        boss.take_damage(dmg)
                        hero.aether = min(hero.max_aether, hero.aether + aether_gain)
                        hero.add_resonance(11.0)
                        hero.combo_count += 1
                        hitstop = 0.034
                        shake = max(shake, 8.0)
                        floating_texts.append(FloatingText(boss.rect.centerx + random.randint(-20, 20), boss.rect.top - 14, dmg, (255, 240, 185), 23))
                        if hero.slash_dir == "down":
                            hero.vy = vault_vy
                            hero.reset_air_mobility()
                            if hero.has_relic("astral_vortex"):
                                arts.append(AstralArtBlast(hero.rect.centerx - 95, hero.rect.centery - 95, 190, 190, 0, 0, int(dmg * 0.8), 0.18, "nova"))
                        elif hero.slash_dir == "left":
                            hero.vx = 220.0
                        elif hero.slash_dir == "right":
                            hero.vx = -220.0

                # Урон от Искрового Шага при рывке
                if hero.dash_timer > 0 and hero.has_relic("volt_step"):
                    vdmg = int(hero.blade_damage * 1.15)
                    for en in enemies:
                        if hero.rect.colliderect(en.rect) and id(en) not in hero.dash_hit_ids:
                            hero.dash_hit_ids.add(id(en))
                            en.hp -= vdmg
                            en.flash = 0.08
                            floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, vdmg, (120, 220, 255), 20))
                    if boss and boss.hp > 0 and hero.rect.colliderect(boss.rect) and id(boss) not in hero.dash_hit_ids:
                        hero.dash_hit_ids.add(id(boss))
                        boss.take_damage(vdmg)
                        floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 14, vdmg, (120, 220, 255), 22))

                # Дружественные снаряды (Солнечный Серп, отражённые пули, Звёзды Парирования)
                for pr in list(projectiles):
                    if pr.friendly:
                        for en in enemies:
                            if pr.rect.colliderect(en.rect) and id(en) not in pr.hit_ids:
                                pr.hit_ids.add(id(en))
                                en.hp -= pr.damage
                                en.flash = 0.08
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, pr.damage, (255, 220, 115), 20))
                        if boss and boss.hp > 0 and pr.rect.colliderect(boss.rect) and id(boss) not in pr.hit_ids:
                            pr.hit_ids.add(id(boss))
                            boss.take_damage(pr.damage)
                            floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 14, pr.damage, (255, 220, 115), 22))

                # Астральные Искусства
                for ar in arts:
                    for en in enemies:
                        if ar.rect.colliderect(en.rect) and id(en) not in ar.hit_ids:
                            ar.hit_ids.add(id(en))
                            en.hp -= ar.damage
                            en.flash = 0.1
                            shake = max(shake, 8.0)
                            floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 12, f"{ar.damage}!", (115, 235, 255), 24))
                    if boss and boss.hp > 0 and ar.rect.colliderect(boss.rect) and id(boss) not in ar.hit_ids:
                        ar.hit_ids.add(id(boss))
                        boss.take_damage(ar.damage)
                        hitstop = 0.04
                        shake = max(shake, 10.0)
                        floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 18, f"{ar.damage}!", (115, 235, 255), 26))

                # Смерть обычных врагов
                for en in list(enemies):
                    if en.hp <= 0:
                        enemies.remove(en)
                        if hero.has_relic("crystal_reaper") and hero.hp < hero.max_hp and random.random() < 0.35:
                            hero.hp += 1
                        for _ in range(max(2, en.lumen // 4)):
                            lumen_crystals.append(LumenCrystal(en.rect.centerx, en.rect.centery, 4))
                        for _ in range(20):
                            ang = random.uniform(0, math.tau)
                            spd = random.uniform(90, 340)
                            particles.append(Particle(en.rect.centerx, en.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, biome["accent"], 6, 0.42, glow=True))

                # --- ПРОВЕРКА АСТРАЛЬНОГО ПАРИРОВАНИЯ И УРОНА ---
                parry_zone = hero.rect.inflate(36, 36)
                if hero.parry_timer > 0:
                    parried_any = False
                    for pr in projectiles:
                        if not pr.friendly and parry_zone.colliderect(pr.rect):
                            pr.friendly = True
                            pr.vx = -pr.vx * 1.45
                            pr.vy = -pr.vy * 1.45
                            pr.color = (255, 230, 120)
                            pr.damage = int(hero.blade_damage * 1.6)
                            parried_any = True
                    for en in enemies:
                        if parry_zone.colliderect(en.rect):
                            en.hp -= int(hero.blade_damage * 1.4)
                            en.vx = -en.facing * 450.0
                            parried_any = True
                    if boss and boss.hp > 0 and parry_zone.colliderect(boss.rect):
                        boss.take_damage(int(hero.blade_damage * 1.5))
                        parried_any = True
                    if parried_any:
                        hero.parry_timer = 0.0
                        hero.parry_cd = 0.15
                        hero.invuln_timer = max(hero.invuln_timer, 0.45)
                        hero.aether = min(hero.max_aether, hero.aether + 28.0)
                        hero.add_resonance(25.0)
                        hero.combo_count += 2
                        hitstop = 0.065
                        shake = 12.0
                        floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 22, "ПАРИРОВАНИЕ!", (255, 235, 130), 22))
                        for _ in range(26):
                            ang = random.uniform(0, math.tau)
                            particles.append(Particle(hero.rect.centerx, hero.rect.centery, math.cos(ang) * 380, math.sin(ang) * 380, (255, 235, 140), 6, 0.35, glow=True))
                        if hero.has_relic("mirror_aegis"):
                            for i in range(3):
                                ang = -0.3 + i * 0.3 + (0 if hero.facing == 1 else math.pi)
                                projectiles.append(Projectile(hero.rect.centerx, hero.rect.centery, math.cos(ang) * 460, math.sin(ang) * 460, 10, (255, 235, 140), homing=True, friendly=True, damage=hero.blade_damage))

                intangible = hero.dash_timer > 0 or hero.invuln_timer > 0 or hero.dive_active or hero.parry_timer > 0
                if not intangible:
                    hurt = False
                    for hz in hazards:
                        if hero.rect.colliderect(hz.rect):
                            hurt = True
                    for en in enemies:
                        if hero.rect.colliderect(en.rect):
                            hurt = True
                    if boss and boss.hp > 0 and boss.state != "stagger" and hero.rect.colliderect(boss.rect):
                        hurt = True
                    if boss and boss.clone_rect and hero.rect.colliderect(boss.clone_rect):
                        hurt = True
                    for sw in shockwaves:
                        if not sw.friendly and hero.rect.colliderect(sw.rect):
                            hurt = True
                    for pr in projectiles:
                        if not pr.friendly and hero.rect.colliderect(pr.rect):
                            hurt = True
                    for lz in lasers:
                        if lz.collides_rect(hero.rect):
                            hurt = True

                    if hurt:
                        hero.hp -= 1
                        hero.invuln_timer = 1.2
                        hero.mend_timer = 0.0
                        hero.resonance = max(0.0, hero.resonance - 35.0)
                        hero.combo_count = 0
                        hitstop = 0.055
                        shake = 14.0
                        hero.vy = -440.0
                        hero.vx = -hero.facing * 360.0

                        if hero.has_relic("briar_halo"):
                            hero.aether = min(hero.max_aether, hero.aether + 25.0)
                            blast_r = hero.rect.inflate(190, 190)
                            for en in enemies:
                                if blast_r.colliderect(en.rect):
                                    en.hp -= hero.blade_damage * 2
                            if boss and boss.hp > 0 and blast_r.colliderect(boss.rect):
                                boss.take_damage(hero.blade_damage * 2)
                            for _ in range(30):
                                ang = random.uniform(0, math.tau)
                                particles.append(Particle(hero.rect.centerx, hero.rect.centery, math.cos(ang) * 430, math.sin(ang) * 430, (255, 130, 95), 7, 0.35, glow=True))

                        if hero.hp <= 0:
                            game_state = "game_over"

                # Победа над боссом
                if room_type == "boss" and boss and boss.hp <= 0:
                    shake = 18.0
                    hitstop = 0.085
                    banner_text = f"{boss.name} ПОВЕРЖЕН!"
                    banner_timer = 2.4
                    for _ in range(30):
                        lumen_crystals.append(LumenCrystal(boss.rect.centerx, boss.rect.centery, 8))
                    for _ in range(70):
                        ang = random.uniform(0, math.tau)
                        spd = random.uniform(140, 640)
                        particles.append(Particle(boss.rect.centerx, boss.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, boss.glow, 9, 0.85, glow=True))
                    shockwaves.clear()
                    projectiles.clear()
                    lasers.clear()
                    boss = None

                # Переход в следующую комнату
                gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
                if gate_open and hero.rect.right >= WIDTH - 42:
                    if room_idx < 3:
                        enter_room(depth, room_idx + 1)
                    else:
                        enter_room(depth + 1, 0)

        # --- ОТРИСОВКА КАДРА ---
        shake = max(0.0, shake - 44.0 * dt)
        ox = random.uniform(-shake, shake) if shake > 0 else 0.0
        oy = random.uniform(-shake, shake) if shake > 0 else 0.0

        gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
        draw_backdrop(screen, sky_surf, biome, ox, oy, obelisk_rect, gate_open)
        for m in motes:
            m.draw(screen, ox, oy)

        # Боевой слой (рендерится на экран И отражается в полу)
        entity_layer.fill((0, 0, 0, 0))
        for plat in platforms:
            plat.draw(entity_layer, 0, 0, biome)
        for hz in hazards:
            hz.draw(entity_layer, 0, 0, biome)
        for cl in clusters:
            cl.draw(entity_layer, 0, 0)
        for ai in afterimages:
            ai.draw(entity_layer, 0, 0)
        for sw in shockwaves:
            sw.draw(entity_layer, 0, 0)
        for en in enemies:
            en.draw(entity_layer, 0, 0)
        if boss and boss.hp > 0:
            boss.draw(entity_layer, 0, 0)
        hero.draw(entity_layer, 0, 0)
        for sa in slash_arcs:
            sa.draw(entity_layer, 0, 0)
        for ar in arts:
            ar.draw(entity_layer, 0, 0)
        for pr in projectiles:
            pr.draw(entity_layer, 0, 0)
        for lz in lasers:
            lz.draw(entity_layer, 0, 0)
        for lc in lumen_crystals:
            lc.draw(entity_layer, 0, 0)
        for pt in particles:
            pt.draw(entity_layer, 0, 0)

        draw_reflective_floor(screen, floor_surf, entity_layer, biome, ox, oy)
        screen.blit(entity_layer, (int(ox), int(oy)))

        for ft in floating_texts:
            ft.draw(screen, ox, oy)

        if game_state == "playing" and room_type == "sanctuary" and obelisk_rect and hero.rect.colliderect(obelisk_rect.inflate(46, 20)):
            p_img = f_prompt.render("[W / E] Коснуться Обелиска Гармонии (Реликвии и Ковка)", True, (255, 240, 175))
            screen.blit(p_img, (obelisk_rect.centerx - p_img.get_width() // 2 + int(ox), obelisk_rect.top - 42 + int(oy)))

        draw_hud(screen, hero, boss, depth, room_idx, biome)

        if banner_timer > 0 and game_state == "playing":
            b_img = f_med.render(banner_text, True, (245, 250, 255))
            bx = (WIDTH - b_img.get_width()) // 2
            by = 132
            pygame.draw.line(screen, biome["accent"], (bx - 45, by + 36), (bx + b_img.get_width() + 45, by + 36), 2)
            screen.blit(b_img, (bx, by))

        if game_state == "title":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((6, 9, 18, 190))
            screen.blit(ov, (0, 0))
            t1 = f_big.render("AETHERFALL: RESONANCE", True, (245, 250, 255))
            t2 = f_med.render("Нажми ENTER или ПРОБЕЛ, чтобы шагнуть в Разлом", True, (110, 235, 255))
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 58))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 18))

        elif game_state == "shrine_menu":
            draw_shrine_menu(screen, hero, menu_tab, menu_sel, at_obelisk)

        elif game_state == "game_over":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((6, 9, 18, 200))
            screen.blit(ov, (0, 0))
            t1 = f_big.render("НИТЬ РЕЗОНАНСА ПРЕРВАНА", True, (245, 250, 255))
            t2 = f_med.render(f"Пройдено этажей: {depth}   |   Нажми R, чтобы начать новый забег", True, (175, 215, 245))
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 52))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 18))

        pygame.display.flip()


if __name__ == "__main__":
    main()
