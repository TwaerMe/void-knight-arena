import math
import random
import sys
import pygame

# --- БАЗОВЫЕ НАСТРОЙКИ ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
FLOOR_Y = 615
GRAVITY = 2300.0


def get_font(size, bold=False):
    return pygame.font.SysFont("segoeui,arial,tahoma,dejavusans", size, bold=bold)


# --- БИОМЫ ---
BIOMES = [
    {
        "name": "ЗАБЫТЫЙ ПЕРЕКРЁСТОК",
        "bg": (11, 14, 24),
        "pillar": (18, 23, 38),
        "pillar_edge": (30, 38, 60),
        "floor": (20, 25, 40),
        "floor_line": (105, 130, 175),
        "dust": (140, 175, 230),
    },
    {
        "name": "ЗЕЛЁНАЯ ТРОПА ПУСТОТЫ",
        "bg": (10, 20, 18),
        "pillar": (16, 33, 29),
        "pillar_edge": (28, 56, 48),
        "floor": (18, 36, 31),
        "floor_line": (85, 195, 150),
        "dust": (120, 240, 180),
    },
    {
        "name": "БАГРОВЫЙ КОЛИЗЕЙ",
        "bg": (22, 11, 16),
        "pillar": (38, 18, 25),
        "pillar_edge": (64, 28, 40),
        "floor": (40, 19, 26),
        "floor_line": (220, 85, 110),
        "dust": (255, 135, 110),
    },
    {
        "name": "ЯДРО БЕЗДНЫ",
        "bg": (8, 8, 13),
        "pillar": (15, 14, 24),
        "pillar_edge": (42, 34, 68),
        "floor": (16, 15, 26),
        "floor_line": (175, 135, 255),
        "dust": (200, 180, 255),
    },
]

# --- БАЗА АМУЛЕТОВ (12 ШТУК) ---
CHARMS = [
    {
        "id": "longnail",
        "name": "Длинный Гвоздь",
        "notches": 2,
        "cost": 0,
        "unlocked": True,
        "color": (165, 215, 255),
        "desc": "Увеличивает дальность удара гвоздём на 35%.",
    },
    {
        "id": "soul_catcher",
        "name": "Ловец Душ",
        "notches": 2,
        "cost": 0,
        "unlocked": True,
        "color": (235, 248, 255),
        "desc": "+45% Души при каждом попадании гвоздём.",
    },
    {
        "id": "grubsong",
        "name": "Песнь Гусеничек",
        "notches": 1,
        "cost": 0,
        "unlocked": True,
        "color": (130, 235, 155),
        "desc": "Восстанавливает 25 Души при получении урона.",
    },
    {
        "id": "quick_slash",
        "name": "Быстрый Удар",
        "notches": 3,
        "cost": 160,
        "unlocked": False,
        "color": (120, 230, 255),
        "desc": "Ускоряет взмахи гвоздём на 35%.",
    },
    {
        "id": "shaman_stone",
        "name": "Шаманский Камень",
        "notches": 3,
        "cost": 180,
        "unlocked": False,
        "color": (195, 140, 255),
        "desc": "Увеличивает размер и урон всех заклинаний на 45%.",
    },
    {
        "id": "sharp_shadow",
        "name": "Пронизывающая Тень",
        "notches": 2,
        "cost": 140,
        "unlocked": False,
        "color": (95, 85, 140),
        "desc": "Теневой рывок длиннее на 25% и наносит урон врагам насквозь.",
    },
    {
        "id": "strength",
        "name": "Нерушимая Сила",
        "notches": 3,
        "cost": 240,
        "unlocked": False,
        "color": (255, 95, 120),
        "desc": "Увеличивает урон гвоздя на 40%.",
    },
    {
        "id": "quick_focus",
        "name": "Быстрый Фокус",
        "notches": 3,
        "cost": 150,
        "unlocked": False,
        "color": (210, 240, 255),
        "desc": "Ускоряет лечение (Фокус) в 2 раза.",
    },
    {
        "id": "heart",
        "name": "Сердце Живокровки",
        "notches": 2,
        "cost": 130,
        "unlocked": False,
        "color": (90, 175, 255),
        "desc": "Добавляет +2 маски здоровья.",
    },
    {
        "id": "thorns",
        "name": "Шипы Страданий",
        "notches": 1,
        "cost": 110,
        "unlocked": False,
        "color": (140, 210, 120),
        "desc": "При получении урона выпускает кольцо шипов вокруг героя.",
    },
    {
        "id": "swarm",
        "name": "Рой Сборщиков",
        "notches": 1,
        "cost": 90,
        "unlocked": False,
        "color": (255, 215, 90),
        "desc": "Притягивает Гео со всей комнаты и даёт +25% к добыче.",
    },
    {
        "id": "mark_of_pride",
        "name": "Метка Гордости",
        "notches": 3,
        "cost": 260,
        "unlocked": False,
        "color": (245, 245, 255),
        "desc": "Огромный радиус клинка (+55%) и усиленный отскок.",
    },
]


# --- ВИЗУАЛЬНЫЕ ЭФФЕКТЫ И ОБЪЕКТЫ МИРА ---
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity

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
        pygame.draw.circle(surf, self.color, (int(self.x + ox), int(self.y + oy)), r)


class Afterimage:
    def __init__(self, rect, facing, color=(35, 42, 65)):
        self.rect = rect.copy()
        self.facing = facing
        self.color = color
        self.life = 0.22
        self.max_life = 0.22

    def update(self, dt):
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        alpha = int(160 * (self.life / self.max_life))
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, alpha), (2, 4, self.rect.width - 4, self.rect.height - 4), border_radius=8)
        surf.blit(s, (int(self.rect.x + ox), int(self.rect.y + oy)))


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size=22):
        self.x = float(x)
        self.y = float(y)
        self.text = str(text)
        self.color = color
        self.font = get_font(size, bold=True)
        self.life = 0.75

    def update(self, dt):
        self.y -= 55.0 * dt
        self.life -= dt

    def draw(self, surf, ox, oy):
        if self.life <= 0:
            return
        img = self.font.render(self.text, True, self.color)
        surf.blit(img, (int(self.x - img.get_width() // 2 + ox), int(self.y + oy)))


class GeoShard:
    def __init__(self, x, y, value=5):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-220, 220)
        self.vy = random.uniform(-460, -180)
        self.value = value
        self.life = 25.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 7), int(self.y - 7), 14, 14)

    def update(self, dt, player, magnet=False):
        self.life -= dt
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        dist = math.hypot(dx, dy) or 1.0
        pull_range = 950.0 if magnet else 145.0
        if dist < pull_range:
            spd = 780.0 if magnet else 480.0
            self.vx += (dx / dist) * spd * 6.0 * dt
            self.vy += (dy / dist) * spd * 6.0 * dt
            self.vx *= 0.92
            self.vy *= 0.92
        else:
            self.vy = min(950.0, self.vy + GRAVITY * 0.85 * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 45:
            self.x = 45.0
            self.vx *= -0.6
        elif self.x > WIDTH - 45:
            self.x = float(WIDTH - 45)
            self.vx *= -0.6

        if self.y >= FLOOR_Y - 7:
            self.y = float(FLOOR_Y - 7)
            self.vy *= -0.45
            self.vx *= 0.78

    def draw(self, surf, ox, oy):
        cx, cy = int(self.x + ox), int(self.y + oy)
        pts = [(cx, cy - 8), (cx + 6, cy), (cx, cy + 8), (cx - 6, cy)]
        pygame.draw.polygon(surf, (235, 245, 255), pts)
        pygame.draw.polygon(surf, (130, 185, 235), pts, 2)


class Platform:
    def __init__(self, x, y, w, h=18):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surf, ox, oy, biome):
        r = self.rect.move(int(ox), int(oy))
        pygame.draw.rect(surf, biome["floor"], r, border_radius=5)
        pygame.draw.line(surf, biome["floor_line"], (r.left + 3, r.top + 1), (r.right - 3, r.top + 1), 3)


class SpikeHazard:
    """Шипы: наносят урон при касании, но от них можно отпрыгивать пого-ударом вниз!"""
    def __init__(self, x, y, w):
        self.rect = pygame.Rect(x, y - 22, w, 22)

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        step = 18
        for sx in range(r.left, r.right - 6, step):
            pts = [(sx, r.bottom), (sx + step // 2, r.top), (sx + step, r.bottom)]
            pygame.draw.polygon(surf, (165, 180, 210), pts)
            pygame.draw.polygon(surf, (40, 48, 68), pts, 2)


class GeoDeposit:
    """Кристальная жила с Гео в комнатах."""
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
        col = (255, 255, 255) if self.flash > 0 else (95, 165, 225)
        pygame.draw.polygon(
            surf,
            col,
            [(r.left + 4, r.bottom), (r.left + 10, r.top + 12), (r.centerx, r.top), (r.right - 8, r.top + 16), (r.right - 4, r.bottom)],
        )
        pygame.draw.polygon(
            surf,
            (225, 245, 255),
            [(r.centerx - 6, r.bottom), (r.centerx, r.top + 8), (r.centerx + 8, r.bottom)],
        )


# --- СНАРЯДЫ, ВОЛНЫ, ЛАЗЕРЫ И ЗАКЛИНАНИЯ ---
class Shockwave:
    def __init__(self, x, y, vx, height=62, life=1.45, color=(230, 70, 100), friendly=False, damage=1):
        self.rect = pygame.Rect(int(x - 18), int(y - height), 36, height)
        self.x = float(self.rect.x)
        self.vx = vx
        self.life = life
        self.max_life = life
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
        pygame.draw.rect(surf, self.color, r, border_radius=7)
        inner = r.inflate(-14, -10)
        if inner.width > 0 and inner.height > 0:
            pygame.draw.rect(surf, (255, 245, 255), inner, border_radius=4)


class Projectile:
    def __init__(self, x, y, vx, vy, radius=13, color=(255, 75, 115), homing=False, boomerang=False, owner=None):
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
        self.age = 0.0

    @property
    def rect(self):
        s = int(self.radius * 1.45)
        return pygame.Rect(int(self.x - s // 2), int(self.y - s // 2), s, s)

    def update(self, dt, player=None):
        self.age += dt
        self.life -= dt
        if self.homing and player and self.age < 2.2:
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            dist = math.hypot(dx, dy) or 1.0
            self.vx += (dx / dist) * 520.0 * dt
            self.vy += (dy / dist) * 520.0 * dt
            spd = math.hypot(self.vx, self.vy)
            if spd > 420.0:
                self.vx = (self.vx / spd) * 420.0
                self.vy = (self.vy / spd) * 420.0
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
        if self.boomerang:
            ang = self.age * 18.0
            p1 = (pos[0] + math.cos(ang) * 26, pos[1] + math.sin(ang) * 26)
            p2 = (pos[0] - math.cos(ang) * 26, pos[1] - math.sin(ang) * 26)
            pygame.draw.line(surf, self.color, p1, p2, 6)
            pygame.draw.line(surf, (255, 240, 245), p1, p2, 2)
        else:
            pygame.draw.circle(surf, self.color, pos, self.radius)
            pygame.draw.circle(surf, (255, 240, 248), pos, max(3, self.radius // 2))


class LaserBeam:
    """Телеграфируемый лазер: сначала тонкий луч прицела, затем мощный удар."""
    def __init__(self, x1, y1, angle, length=1400, warn_time=0.65, active_time=0.32, color=(235, 110, 255)):
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
        # Проверка пересечения отрезка лазера с расширенным хитбоксом игрока
        expanded = rect.inflate(18, 18)
        return bool(expanded.clipline((self.x1, self.y1), (self.x2, self.y2)))

    def draw(self, surf, ox, oy):
        if self.timer <= 0:
            return
        p1 = (int(self.x1 + ox), int(self.y1 + oy))
        p2 = (int(self.x2 + ox), int(self.y2 + oy))
        if not self.is_firing:
            pygame.draw.line(surf, self.color, p1, p2, 2)
        else:
            pygame.draw.line(surf, self.color, p1, p2, 26)
            pygame.draw.line(surf, (255, 250, 255), p1, p2, 10)


class PlayerSpellBlast:
    """Заклинания Души игрока: Мстительный дух, Воющие духи, Опустошающее пике."""
    def __init__(self, x, y, w, h, vx, vy, damage, life, spell_type):
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.life = life
        self.max_life = life
        self.spell_type = spell_type
        self.hit_ids = set()

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.life -= dt

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        if self.spell_type == "fireball":
            pygame.draw.ellipse(surf, (190, 235, 255), r)
            inner = r.inflate(-16, -14)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(surf, (255, 255, 255), inner)
        elif self.spell_type == "wraiths":
            pygame.draw.rect(surf, (170, 210, 255), r, border_radius=24)
            inner = r.inflate(-28, -20)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.rect(surf, (255, 255, 255), inner, border_radius=18)
        elif self.spell_type == "dive_boom":
            pygame.draw.ellipse(surf, (160, 195, 255), r)
            inner = r.inflate(-30, -24)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(surf, (255, 255, 255), inner)


# --- ИГРОК ---
class Player:
    def __init__(self):
        self.rect = pygame.Rect(140, FLOOR_Y - 56, 34, 56)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1

        self.base_max_hp = 6
        self.max_hp = 6
        self.hp = 6
        self.max_soul = 100.0
        self.soul = 66.0
        self.base_damage = 15
        self.geo = 60

        self.max_notches = 4
        self.equipped = ["longnail", "soul_catcher"]

        self.on_ground = False
        self.jumps_left = 2
        self.jump_held = False
        self.drop_through_timer = 0.0

        self.dash_timer = 0.0
        self.dash_cd = 0.0
        self.dash_dir = 1
        self.dash_hit_ids = set()

        self.slash_timer = 0.0
        self.slash_cd = 0.0
        self.slash_dir = "right"
        self.hit_ids = set()

        self.dive_active = False
        self.invuln_timer = 0.0
        self.focus_timer = 0.0
        self.afterimage_timer = 0.0
        self.cape = [[self.rect.centerx, self.rect.centery] for _ in range(7)]

    def has_charm(self, cid):
        return cid in self.equipped

    def used_notches(self):
        by_id = {c["id"]: c["notches"] for c in CHARMS}
        return sum(by_id.get(cid, 0) for cid in self.equipped)

    def recalculate_stats(self):
        bonus_hp = 2 if self.has_charm("heart") else 0
        self.max_hp = self.base_max_hp + bonus_hp
        self.hp = min(self.hp, self.max_hp)

    @property
    def nail_damage(self):
        mult = 1.4 if self.has_charm("strength") else 1.0
        return int(round(self.base_damage * mult))

    @property
    def spell_mult(self):
        return 1.45 if self.has_charm("shaman_stone") else 1.0

    def reset_air_mobility(self):
        self.jumps_left = 2
        self.dash_cd = min(self.dash_cd, 0.04)

    def start_dash(self):
        if self.dash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.dash_timer = 0.21 if self.has_charm("sharp_shadow") else 0.17
            self.dash_cd = 0.52
            self.dash_dir = self.facing
            self.dash_hit_ids.clear()
            self.vy = 0.0
            self.focus_timer = 0.0
            return True
        return False

    def start_slash(self, keys):
        if self.slash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.slash_timer = 0.14
            self.slash_cd = 0.17 if self.has_charm("quick_slash") else 0.26
            self.hit_ids.clear()
            self.focus_timer = 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.slash_dir = "up"
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not self.on_ground:
                self.slash_dir = "down"
            else:
                self.slash_dir = "right" if self.facing == 1 else "left"
            return True
        return False

    def cast_spell(self, keys, spells, particles):
        if self.soul < 33.0 or self.dash_timer > 0 or self.dive_active:
            return False
        self.soul -= 33.0
        self.focus_timer = 0.0
        scale = 1.25 if self.has_charm("shaman_stone") else 1.0

        # Вверх: Воющие Духи
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            w, h = int(150 * scale), int(330 * scale)
            spells.append(
                PlayerSpellBlast(
                    self.rect.centerx - w // 2,
                    self.rect.top - h + 20,
                    w,
                    h,
                    0,
                    -140,
                    int(44 * self.spell_mult),
                    0.26,
                    "wraiths",
                )
            )
            self.vy = max(self.vy, 120.0)
            for _ in range(28):
                particles.append(
                    Particle(
                        self.rect.centerx + random.uniform(-55, 55),
                        self.rect.top,
                        random.uniform(-60, 60),
                        random.uniform(-650, -220),
                        (220, 240, 255),
                        7,
                        0.4,
                    )
                )
            return True

        # Вниз в воздухе: Опустошающее Пике
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not self.on_ground:
            self.dive_active = True
            self.vx = 0.0
            self.vy = 1480.0
            self.invuln_timer = max(self.invuln_timer, 0.7)
            return True

        # Вперёд: Мстительный Дух
        w, h = int(92 * scale), int(56 * scale)
        start_x = self.rect.right if self.facing == 1 else self.rect.left - w
        spells.append(
            PlayerSpellBlast(
                start_x,
                self.rect.centery - h // 2,
                w,
                h,
                self.facing * 940.0,
                0.0,
                int(34 * self.spell_mult),
                1.2,
                "fireball",
            )
        )
        self.vx = -self.facing * 160.0
        for _ in range(18):
            particles.append(
                Particle(
                    self.rect.centerx,
                    self.rect.centery,
                    self.facing * random.uniform(120, 380),
                    random.uniform(-140, 140),
                    (220, 245, 255),
                    6,
                    0.35,
                )
            )
        return True

    def get_slash_rect(self):
        if self.slash_timer <= 0:
            return None
        reach = 1.0
        if self.has_charm("mark_of_pride"):
            reach = 1.55
        elif self.has_charm("longnail"):
            reach = 1.35

        length = int(94 * reach)
        broad = int(78 * (1.0 + (reach - 1.0) * 0.55))
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

    def update(self, dt, keys, platforms, particles, afterimages, spells, shockwaves):
        self.dash_cd = max(0.0, self.dash_cd - dt)
        self.slash_cd = max(0.0, self.slash_cd - dt)
        self.slash_timer = max(0.0, self.slash_timer - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)
        self.drop_through_timer = max(0.0, self.drop_through_timer - dt)

        move_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir += 1

        if move_dir != 0 and self.dash_timer <= 0 and not self.dive_active:
            self.facing = move_dir

        # Фокус / Лечение (удерживать E или F)
        want_focus = keys[pygame.K_e] or keys[pygame.K_f]
        focus_needed = 0.42 if self.has_charm("quick_focus") else 0.82
        if (
            want_focus
            and self.on_ground
            and move_dir == 0
            and self.dash_timer <= 0
            and not self.dive_active
            and self.hp < self.max_hp
            and self.soul >= 33.0
        ):
            self.focus_timer += dt
            if random.random() < 0.65:
                particles.append(
                    Particle(
                        self.rect.centerx + random.uniform(-26, 26),
                        self.rect.bottom - random.uniform(0, 44),
                        random.uniform(-25, 25),
                        random.uniform(-150, -60),
                        (220, 245, 255),
                        5,
                        0.4,
                    )
                )
            if self.focus_timer >= focus_needed:
                self.focus_timer = 0.0
                self.soul -= 33.0
                self.hp = min(self.max_hp, self.hp + 1)
                for _ in range(24):
                    ang = random.uniform(0, math.tau)
                    spd = random.uniform(90, 270)
                    particles.append(
                        Particle(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, (255, 255, 255), 7, 0.5)
                    )
        else:
            self.focus_timer = 0.0

        # Движение / Теневой рывок / Пике
        if self.dive_active:
            self.vx = 0.0
            self.vy = 1480.0
            self.afterimage_timer -= dt
            if self.afterimage_timer <= 0:
                self.afterimage_timer = 0.025
                afterimages.append(Afterimage(self.rect, self.facing, (180, 220, 255)))
        elif self.dash_timer > 0:
            self.dash_timer -= dt
            dash_spd = 1120.0 if self.has_charm("sharp_shadow") else 980.0
            self.vx = self.dash_dir * dash_spd
            self.vy = 0.0
            self.afterimage_timer -= dt
            if self.afterimage_timer <= 0:
                self.afterimage_timer = 0.028
                col = (140, 85, 220) if self.has_charm("sharp_shadow") else (40, 48, 72)
                afterimages.append(Afterimage(self.rect, self.facing, col))
        else:
            target_vx = move_dir * 440.0
            accel = 3500.0 if self.on_ground else 2500.0
            if self.vx < target_vx:
                self.vx = min(target_vx, self.vx + accel * dt)
            elif self.vx > target_vx:
                self.vx = max(target_vx, self.vx - accel * dt)

            if not self.jump_held and self.vy < -260.0:
                self.vy += GRAVITY * 1.45 * dt
            self.vy = min(1200.0, self.vy + GRAVITY * dt)

        prev_bottom = self.y + self.rect.height
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 36:
            self.x = 36.0
            self.vx = 0.0
        elif self.x > WIDTH - 36 - self.rect.width:
            self.x = float(WIDTH - 36 - self.rect.width)
            self.vx = 0.0

        landed = False
        # Проверка односторонних платформ
        if self.vy >= 0 and self.drop_through_timer <= 0 and not self.dive_active:
            new_bottom = self.y + self.rect.height
            test_rect = pygame.Rect(int(self.x + 4), int(self.y), self.rect.width - 8, self.rect.height)
            for plat in platforms:
                if test_rect.colliderect(plat.rect) and prev_bottom <= plat.rect.top + 10 and new_bottom >= plat.rect.top:
                    self.y = float(plat.rect.top - self.rect.height)
                    self.vy = 0.0
                    landed = True
                    break

        # Пол арены
        if self.y + self.rect.height >= FLOOR_Y:
            self.y = float(FLOOR_Y - self.rect.height)
            self.vy = 0.0
            landed = True
            if self.dive_active:
                self.dive_active = False
                self.invuln_timer = max(self.invuln_timer, 0.35)
                dmg = int(52 * self.spell_mult)
                scale = 1.25 if self.has_charm("shaman_stone") else 1.0
                bw, bh = int(310 * scale), int(125 * scale)
                spells.append(
                    PlayerSpellBlast(
                        self.rect.centerx - bw // 2,
                        FLOOR_Y - bh,
                        bw,
                        bh,
                        0,
                        0,
                        dmg,
                        0.28,
                        "dive_boom",
                    )
                )
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, -620.0, height=54, life=0.6, color=(205, 235, 255), friendly=True, damage=int(24 * self.spell_mult)))
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, 620.0, height=54, life=0.6, color=(205, 235, 255), friendly=True, damage=int(24 * self.spell_mult)))
                for _ in range(34):
                    particles.append(
                        Particle(
                            self.rect.centerx + random.uniform(-50, 50),
                            FLOOR_Y - 6,
                            random.uniform(-450, 450),
                            random.uniform(-420, -60),
                            (225, 245, 255),
                            8,
                            0.5,
                        )
                    )

        if landed:
            self.on_ground = True
            self.jumps_left = 2
        else:
            self.on_ground = False

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Плащ
        self.cape[0] = [self.rect.centerx - self.facing * 4, self.rect.top + 24]
        for i in range(1, len(self.cape)):
            px, py = self.cape[i - 1]
            cx, cy = self.cape[i]
            tx = px - self.facing * 7
            ty = py + 5
            self.cape[i][0] += (tx - cx) * min(1.0, 22.0 * dt)
            self.cape[i][1] += (ty - cy) * min(1.0, 22.0 * dt)

    def draw(self, surf, ox, oy):
        if self.invuln_timer > 0 and not self.dive_active and int(self.invuln_timer * 22) % 2 == 0:
            return

        pts = [(int(p[0] + ox), int(p[1] + oy)) for p in self.cape]
        for i in range(len(pts) - 1):
            w = max(4, 18 - i * 2)
            pygame.draw.line(surf, (44, 52, 74), pts[i], pts[i + 1], w)

        r = self.rect.move(int(ox), int(oy))
        body_rect = pygame.Rect(r.x + 6, r.y + 22, r.width - 12, r.height - 22)
        pygame.draw.rect(surf, (18, 20, 30), body_rect, border_radius=6)

        head_rect = pygame.Rect(r.x + 2, r.y + 4, r.width - 4, 24)
        pygame.draw.rect(surf, (245, 248, 255), head_rect, border_radius=9)

        pygame.draw.polygon(
            surf,
            (245, 248, 255),
            [(head_rect.left + 4, head_rect.top + 4), (head_rect.left - 2, head_rect.top - 12), (head_rect.left + 11, head_rect.top + 2)],
        )
        pygame.draw.polygon(
            surf,
            (245, 248, 255),
            [(head_rect.right - 4, head_rect.top + 4), (head_rect.right + 2, head_rect.top - 12), (head_rect.right - 11, head_rect.top + 2)],
        )

        eye_off = 4 if self.facing == 1 else -4
        pygame.draw.ellipse(surf, (12, 14, 20), (head_rect.centerx - 9 + eye_off, head_rect.centery - 4, 6, 9))
        pygame.draw.ellipse(surf, (12, 14, 20), (head_rect.centerx + 3 + eye_off, head_rect.centery - 4, 6, 9))

        s_rect = self.get_slash_rect()
        if s_rect:
            sr = s_rect.move(int(ox), int(oy))
            pygame.draw.ellipse(surf, (185, 235, 255), sr, 6)
            inner = sr.inflate(-14, -14)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(surf, (255, 255, 255), inner, 3)


# --- ОБЫЧНЫЕ ВРАГИ (5 ТИПОВ) ---
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

        if kind == "wanderer":
            self.w, self.h = 38, 48
            self.max_hp = int(34 * scale)
            self.geo = 10
        elif kind == "aspid":
            self.w, self.h = 42, 42
            self.max_hp = int(32 * scale)
            self.geo = 14
        elif kind == "shield_knight":
            self.w, self.h = 48, 74
            self.max_hp = int(58 * scale)
            self.geo = 20
        elif kind == "spore":
            self.w, self.h = 36, 36
            self.max_hp = int(24 * scale)
            self.geo = 12
        elif kind == "stalker":
            self.w, self.h = 40, 56
            self.max_hp = int(42 * scale)
            self.geo = 16

        self.hp = self.max_hp

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, player, projectiles, particles):
        self.flash = max(0.0, self.flash - dt)
        self.timer -= dt
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1.0

        if self.kind == "wanderer":
            self.facing = 1 if dx > 0 else -1
            self.vx = self.facing * 205.0
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        elif self.kind == "aspid":
            self.facing = 1 if dx > 0 else -1
            desired_y = max(130.0, player.rect.centery - 155.0)
            self.vx = (dx / dist) * 145.0 if dist > 260 else -(dx / dist) * 90.0
            self.vy = (desired_y - self.y) * 2.5
            if self.timer <= 0:
                self.timer = 2.1
                base_ang = math.atan2(dy, dx)
                for off in (-0.24, 0.0, 0.24):
                    ang = base_ang + off
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 390, math.sin(ang) * 390, 10, (255, 165, 55)))

        elif self.kind == "shield_knight":
            if self.state == "idle":
                self.facing = 1 if dx > 0 else -1
                self.vx = self.facing * 125.0
                if abs(dx) < 170 and abs(dy) < 90 and self.timer <= 0:
                    self.state = "windup"
                    self.timer = 0.45
                    self.vx = 0.0
            elif self.state == "windup":
                if self.timer <= 0:
                    self.state = "strike"
                    self.timer = 0.28
                    self.vx = self.facing * 540.0
            elif self.state == "strike":
                if self.timer <= 0:
                    self.state = "idle"
                    self.timer = 0.85
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        elif self.kind == "spore":
            self.vx = (dx / dist) * 165.0
            self.vy = (dy / dist) * 165.0
            if dist < 68 and self.state != "arming":
                self.state = "arming"
                self.timer = 0.45
            if self.state == "arming" and self.timer <= 0:
                self.hp = 0
                for i in range(8):
                    ang = (math.tau / 8) * i
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 330, math.sin(ang) * 330, 10, (255, 120, 60)))

        elif self.kind == "stalker":
            if self.state == "idle":
                self.facing = 1 if dx > 0 else -1
                self.vx = self.facing * 170.0
                if self.timer <= 0 and abs(dx) < 380:
                    self.state = "prep"
                    self.timer = 0.42
                    self.vx = 0.0
            elif self.state == "prep":
                if self.timer <= 0:
                    self.state = "dash"
                    self.timer = 0.25
                    self.vx = self.facing * 820.0
            elif self.state == "dash":
                if self.timer <= 0:
                    self.state = "idle"
                    self.timer = 1.1
            self.vy = min(1100.0, self.vy + GRAVITY * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 50:
            self.x = 50.0
            self.vx = 0.0
        elif self.x > WIDTH - 50 - self.w:
            self.x = float(WIDTH - 50 - self.w)
            self.vx = 0.0

        if self.kind not in ("aspid", "spore"):
            if self.y + self.h >= FLOOR_Y:
                self.y = float(FLOOR_Y - self.h)
                self.vy = 0.0
        else:
            self.y = max(95.0, min(float(FLOOR_Y - self.h - 20), self.y))

    def draw(self, surf, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        flash_col = (255, 255, 255)

        if self.kind == "wanderer":
            col = flash_col if self.flash > 0 else (55, 65, 95)
            pygame.draw.rect(surf, col, r, border_radius=10)
            pygame.draw.circle(surf, (255, 150, 70), (r.centerx + self.facing * 8, r.y + 16), 4)

        elif self.kind == "aspid":
            col = flash_col if self.flash > 0 else (185, 95, 45)
            pygame.draw.ellipse(surf, col, r)
            wing_y = r.top - 6 + int(math.sin(pygame.time.get_ticks() * 0.03) * 5)
            pygame.draw.ellipse(surf, (220, 235, 255), (r.left - 8, wing_y, 20, 12))
            pygame.draw.ellipse(surf, (220, 235, 255), (r.right - 12, wing_y, 20, 12))
            pygame.draw.circle(surf, (255, 230, 120), (r.centerx + self.facing * 8, r.centery), 4)

        elif self.kind == "shield_knight":
            col = flash_col if self.flash > 0 else (40, 50, 75)
            pygame.draw.rect(surf, col, r, border_radius=12)
            # Большой щит спереди (подсказка игроку: обходи или бей сверху!)
            sx = r.right - 4 if self.facing == 1 else r.left - 10
            shield_r = pygame.Rect(sx, r.y + 10, 14, r.height - 16)
            pygame.draw.rect(surf, (175, 195, 225), shield_r, border_radius=5)
            pygame.draw.circle(surf, (120, 220, 255), (r.centerx + self.facing * 8, r.y + 18), 4)

        elif self.kind == "spore":
            col = flash_col if self.flash > 0 else ((255, 90, 60) if self.state == "arming" else (210, 120, 55))
            pygame.draw.circle(surf, col, r.center, self.w // 2)
            pygame.draw.circle(surf, (255, 225, 140), r.center, self.w // 4)

        elif self.kind == "stalker":
            col = flash_col if self.flash > 0 else (75, 42, 115)
            pygame.draw.rect(surf, col, r, border_radius=9)
            pygame.draw.circle(surf, (230, 120, 255), (r.centerx + self.facing * 9, r.y + 16), 4)
            if self.state == "prep":
                pygame.draw.line(surf, (230, 120, 255), r.center, (r.centerx + self.facing * 260, r.centery), 2)


# --- 5 УНИКАЛЬНЫХ БОССОВ ---
class Boss:
    TYPES = [
        ("juggernaut", "ЛОЖНЫЙ РЫЦАРЬ ПУСТОТЫ", (225, 55, 85), (255, 145, 165)),
        ("weaver", "БАГРОВАЯ ТАНЦОВЩИЦА", (245, 70, 120), (255, 185, 210)),
        ("watcher", "КРИСТАЛЬНЫЙ СТРАЖ БЕЗДНЫ", (185, 85, 255), (235, 180, 255)),
        ("mantis", "ПОВЕЛИТЕЛЬ БОГОМОЛОВ", (55, 215, 155), (170, 255, 220)),
        ("radiance", "ЛУЧЕЗАРНОСТЬ ПУСТОТЫ", (255, 195, 65), (255, 245, 185)),
    ]

    def __init__(self, depth):
        self.depth = depth
        idx = (depth - 1) % len(self.TYPES)
        tier = (depth - 1) // len(self.TYPES)
        self.kind, base_name, self.primary, self.glow = self.TYPES[idx]
        suffix = f" • ВОЗНЕСЕНИЕ {tier}" if tier > 0 else ""
        self.name = f"{base_name}{suffix}"

        w, h = (96, 134) if self.kind == "juggernaut" else ((84, 124) if self.kind == "radiance" else (74, 122))
        start_y = 210 if self.kind == "radiance" else (FLOOR_Y - h)
        self.rect = pygame.Rect(910, start_y, w, h)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = -1

        self.max_hp = int((270 + (depth - 1) * 115))
        self.hp = self.max_hp
        self.stagger_hits = 0

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
        if self.kind != "radiance":
            self.stagger_hits += 1
            if self.stagger_hits >= 16 and self.hp > 0 and self.state != "stagger":
                self.stagger_hits = 0
                self.state = "stagger"
                self.timer = 1.5
                self.vx = 0.0

    def update(self, dt, player, projectiles, shockwaves, lasers, enemies, particles):
        self.flash = max(0.0, self.flash - dt)
        self.timer -= dt
        spd_mult = (1.24 if self.phase2 else 1.0) + min(0.35, (self.depth - 1) * 0.04)

        if self.clone_timer > 0:
            self.clone_timer -= dt
            if self.clone_timer <= 0:
                self.clone_rect = None

        # --- 1. ЛОЖНЫЙ РЫЦАРЬ ПУСТОТЫ ---
        if self.kind == "juggernaut":
            if self.state == "idle":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["slam", "charge", "wave_spam"])
                    if pick == "slam":
                        self.state = "slam_prep"
                        self.timer = 0.42 / spd_mult
                    elif pick == "charge":
                        self.state = "charge_prep"
                        self.timer = 0.48 / spd_mult
                        self.combo = 2 if self.phase2 else 1
                    else:
                        self.state = "smash_ground"
                        self.timer = 0.45 / spd_mult
            elif self.state == "slam_prep" and self.timer <= 0:
                self.state = "slam_air"
                self.vy = -1280.0
                self.target_x = float(player.rect.centerx - self.rect.width // 2)
            elif self.state == "slam_air":
                self.vy += GRAVITY * 0.95 * dt
                self.x += (self.target_x - self.x) * min(1.0, 6.2 * dt)
                if self.y + self.rect.height >= FLOOR_Y and self.vy > 0:
                    self.y = float(FLOOR_Y - self.rect.height)
                    self.vy = 0.0
                    wspd = 520.0 * spd_mult
                    shockwaves.append(Shockwave(self.rect.left, FLOOR_Y, -wspd, color=self.primary))
                    shockwaves.append(Shockwave(self.rect.right, FLOOR_Y, wspd, color=self.primary))
                    # Обвал метеоров с потолка во 2-й фазе
                    for _ in range(5 if self.phase2 else 2):
                        projectiles.append(Projectile(random.randint(120, WIDTH - 120), 60, 0, random.uniform(360, 520), 15, self.glow))
                    self.state = "idle"
                    self.timer = 0.85 / spd_mult
            elif self.state == "charge_prep":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    self.state = "charge"
                    self.timer = 0.36
                    self.vx = self.facing * 890.0 * spd_mult
            elif self.state == "charge" and self.timer <= 0:
                self.vx = 0.0
                self.combo -= 1
                if self.combo > 0:
                    self.state = "charge_prep"
                    self.timer = 0.35 / spd_mult
                else:
                    self.state = "idle"
                    self.timer = 0.75 / spd_mult
            elif self.state == "smash_ground" and self.timer <= 0:
                wspd = 600.0 * spd_mult
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, self.facing * wspd, height=84, color=self.primary))
                if self.phase2:
                    shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, -self.facing * wspd, height=84, color=self.primary))
                self.state = "idle"
                self.timer = 0.8 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4

        # --- 2. БАГРОВАЯ ТАНЦОВЩИЦА (Хорнет-стиль) ---
        elif self.kind == "weaver":
            if self.state == "idle":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["lunge", "needle_throw", "air_dive", "thread_storm"])
                    if pick == "lunge":
                        self.state = "lunge_prep"
                        self.timer = 0.4 / spd_mult
                    elif pick == "needle_throw":
                        self.state = "throw_prep"
                        self.timer = 0.42 / spd_mult
                    elif pick == "air_dive":
                        self.state = "jump_up"
                        self.vy = -1150.0
                        self.vx = self.facing * 240.0
                    else:
                        self.state = "storm_jump"
                        self.vy = -1050.0
            elif self.state == "lunge_prep":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    self.state = "lunge"
                    self.timer = 0.28
                    self.vx = self.facing * 1060.0 * spd_mult
            elif self.state == "lunge" and self.timer <= 0:
                self.vx = 0.0
                self.state = "idle"
                self.timer = 0.65 / spd_mult
            elif self.state == "throw_prep" and self.timer <= 0:
                # Бросок иглы-бумеранга через арену!
                projectiles.append(
                    Projectile(self.rect.centerx, self.rect.centery, self.facing * 920.0, 0.0, 14, self.glow, boomerang=True, owner=self)
                )
                self.state = "idle"
                self.timer = 1.05 / spd_mult
            elif self.state == "jump_up" and self.vy >= -80:
                self.state = "dive_prep"
                self.timer = 0.28 / spd_mult
                self.vx = 0.0
                self.vy = 0.0
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                ang = math.atan2(max(80.0, dy), dx)
                self.target_x = math.cos(ang) * 1080.0 * spd_mult
                self.target_y = math.sin(ang) * 1080.0 * spd_mult
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
            elif self.state == "storm_jump" and self.vy >= -60:
                self.state = "storm_active"
                self.timer = 0.75
                self.vx = 0.0
                self.vy = 0.0
                count = 10 if self.phase2 else 6
                for i in range(count):
                    ang = (math.tau / count) * i
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 440, math.sin(ang) * 440, 11, self.primary))
            elif self.state == "storm_active":
                self.vy = 0.0
                if self.timer <= 0:
                    self.state = "idle"
                    self.timer = 0.6
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.35

        # --- 3. КРИСТАЛЬНЫЙ СТРАЖ БЕЗДНЫ (Лазеры и телепорты) ---
        elif self.kind == "watcher":
            if self.state == "idle":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["laser_aim", "laser_cross", "teleport_strike"])
                    if pick == "laser_aim":
                        self.state = "laser_aim"
                        self.timer = 0.72 / spd_mult
                        ang = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
                        lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang, warn_time=0.62 / spd_mult, color=self.glow))
                        if self.phase2:
                            lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang + 0.28, warn_time=0.62 / spd_mult, color=self.glow))
                            lasers.append(LaserBeam(self.rect.centerx, self.rect.centery - 15, ang - 0.28, warn_time=0.62 / spd_mult, color=self.glow))
                    elif pick == "laser_cross":
                        self.state = "laser_aim"
                        self.timer = 0.78 / spd_mult
                        for lx in (240, 520, 800, 1060):
                            lasers.append(LaserBeam(lx, 40, math.pi / 2, warn_time=0.68 / spd_mult, color=self.primary))
                    else:
                        # Телепорт на другую сторону арены
                        for _ in range(18):
                            particles.append(Particle(self.rect.centerx, self.rect.centery, random.uniform(-220, 220), random.uniform(-220, 220), self.glow, 7, 0.4))
                        self.x = float(random.choice([140, 590, 1020]))
                        self.state = "idle"
                        self.timer = 0.48 / spd_mult
            elif self.state == "laser_aim" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.85 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4

        # --- 4. ПОВЕЛИТЕЛЬ БОГОМОЛОВ (Клоны и быстрые рывки) ---
        elif self.kind == "mantis":
            if self.state == "idle":
                self.facing = 1 if player.rect.centerx > self.rect.centerx else -1
                if self.timer <= 0:
                    pick = random.choice(["dash_slash", "air_drop", "wind_scythe"])
                    if pick == "dash_slash":
                        self.state = "dash_prep"
                        self.timer = 0.38 / spd_mult
                        if self.phase2:
                            # Призыв теневого двойника с противоположной стороны!
                            cx = 1120 if self.x < 600 else 90
                            self.clone_rect = pygame.Rect(cx, FLOOR_Y - self.rect.height, self.rect.width, self.rect.height)
                            self.clone_timer = 0.75
                    elif pick == "air_drop":
                        self.x = float(max(80, min(WIDTH - 160, player.rect.centerx - self.rect.width // 2)))
                        self.y = 110.0
                        self.vy = 0.0
                        self.state = "drop_prep"
                        self.timer = 0.36 / spd_mult
                    else:
                        self.state = "scythe_prep"
                        self.timer = 0.42 / spd_mult
            elif self.state == "dash_prep" and self.timer <= 0:
                self.state = "dashing"
                self.timer = 0.3
                self.vx = self.facing * 1080.0 * spd_mult
                if self.clone_rect:
                    cdir = 1 if player.rect.centerx > self.clone_rect.centerx else -1
                    projectiles.append(Projectile(self.clone_rect.centerx, self.clone_rect.centery, cdir * 620.0, 0, 14, self.glow))
            elif self.state == "dashing" and self.timer <= 0:
                self.vx = 0.0
                self.state = "idle"
                self.timer = 0.62 / spd_mult
            elif self.state == "drop_prep":
                self.vy = 0.0
                if self.timer <= 0:
                    self.state = "dropping"
                    self.vy = 1380.0
            elif self.state == "dropping" and self.y + self.rect.height >= FLOOR_Y:
                self.y = float(FLOOR_Y - self.rect.height)
                self.vy = 0.0
                shockwaves.append(Shockwave(self.rect.left, FLOOR_Y, -540.0, height=48, color=self.primary))
                shockwaves.append(Shockwave(self.rect.right, FLOOR_Y, 540.0, height=48, color=self.primary))
                self.state = "idle"
                self.timer = 0.62 / spd_mult
            elif self.state == "scythe_prep" and self.timer <= 0:
                for row_y in (FLOOR_Y - 34, FLOOR_Y - 115):
                    projectiles.append(Projectile(self.rect.centerx, row_y, self.facing * 560.0 * spd_mult, 0, 13, self.glow))
                self.state = "idle"
                self.timer = 0.72 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.35

        # --- 5. ЛУЧЕЗАРНОСТЬ ПУСТОТЫ (Парящий финальный босс) ---
        elif self.kind == "radiance":
            # Плавное парение над ареной
            hover_x = 640 + math.sin(pygame.time.get_ticks() * 0.0014) * 320 - self.rect.width // 2
            hover_y = 185 + math.cos(pygame.time.get_ticks() * 0.0022) * 35
            self.x += (hover_x - self.x) * min(1.0, 2.2 * dt)
            self.y += (hover_y - self.y) * min(1.0, 2.5 * dt)
            self.vy = 0.0

            if self.state == "idle" and self.timer <= 0:
                pick = random.choice(["sunburst", "light_wall", "homing_orbs", "radial_lasers"])
                if pick == "sunburst":
                    count = 12 if self.phase2 else 8
                    base = random.uniform(0, 0.5)
                    for i in range(count):
                        ang = base + (math.tau / count) * i
                        projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * 430, math.sin(ang) * 430, 12, self.glow))
                    self.timer = 1.15 / spd_mult
                elif pick == "light_wall":
                    side = random.choice([-1, 1])
                    sx = 80 if side == 1 else WIDTH - 80
                    for py in range(150, FLOOR_Y, 85):
                        if abs(py - (FLOOR_Y - 140)) > 60:  # оставляем окно для прохода!
                            projectiles.append(Projectile(sx, py, side * 420 * spd_mult, 0, 14, self.primary))
                    self.timer = 1.35 / spd_mult
                elif pick == "homing_orbs":
                    for _ in range(3 if self.phase2 else 2):
                        projectiles.append(
                            Projectile(
                                self.rect.centerx + random.uniform(-120, 120),
                                self.rect.centery,
                                random.uniform(-180, 180),
                                -120,
                                14,
                                (255, 230, 130),
                                homing=True,
                            )
                        )
                    self.timer = 1.4 / spd_mult
                elif pick == "radial_lasers":
                    count = 6 if self.phase2 else 4
                    base = random.uniform(0.2, 1.2)
                    for i in range(count):
                        ang = base + (math.pi / count) * i
                        lasers.append(LaserBeam(self.rect.centerx, self.rect.centery, ang, warn_time=0.72 / spd_mult, color=self.glow))
                    self.timer = 1.3 / spd_mult

        # Физика и границы босса
        if self.kind != "radiance" and self.state not in ("slam_air", "diving", "storm_active", "drop_prep"):
            self.vy = min(1150.0, self.vy + GRAVITY * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 55:
            self.x = 55.0
            self.vx = 0.0
        elif self.x > WIDTH - 55 - self.rect.width:
            self.x = float(WIDTH - 55 - self.rect.width)
            self.vx = 0.0

        if self.kind != "radiance" and self.y + self.rect.height >= FLOOR_Y:
            self.y = float(FLOOR_Y - self.rect.height)
            self.vy = 0.0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surf, ox, oy):
        # Теневой двойник (для Повелителя Богомолов)
        if self.clone_rect:
            cr = self.clone_rect.move(int(ox), int(oy))
            pygame.draw.rect(surf, (45, 25, 70), cr, border_radius=12)
            pygame.draw.rect(surf, self.glow, cr, 3, border_radius=12)

        r = self.rect.move(int(ox), int(oy))
        if self.state == "stagger":
            r = pygame.Rect(r.x, r.y + 34, r.width, r.height - 34)

        body_col = (255, 255, 255) if self.flash > 0 else (26, 20, 36)
        trim_col = (255, 255, 255) if self.flash > 0 else self.primary

        if self.phase2:
            pygame.draw.rect(surf, self.primary, r.inflate(20, 20), 2, border_radius=18)

        # Крылья / нимб у Лучезарности
        if self.kind == "radiance":
            pygame.draw.circle(surf, self.glow, r.center, 74, 3)
            pygame.draw.polygon(surf, self.primary, [(r.left, r.centery), (r.left - 58, r.top - 10), (r.left + 8, r.top + 18)])
            pygame.draw.polygon(surf, self.primary, [(r.right, r.centery), (r.right + 58, r.top - 10), (r.right - 8, r.top + 18)])

        pygame.draw.rect(surf, body_col, r, border_radius=15)
        pygame.draw.rect(surf, trim_col, r, 4, border_radius=15)

        mask_r = pygame.Rect(r.x + 12, r.y + 12, r.width - 24, 34)
        pygame.draw.rect(surf, (240, 242, 252), mask_r, border_radius=10)
        pygame.draw.polygon(surf, trim_col, [(mask_r.left + 4, mask_r.top + 4), (mask_r.left - 14, mask_r.top - 28), (mask_r.left + 18, mask_r.top + 4)])
        pygame.draw.polygon(surf, trim_col, [(mask_r.right - 4, mask_r.top + 4), (mask_r.right + 14, mask_r.top - 28), (mask_r.right - 18, mask_r.top + 4)])

        eye_x = mask_r.centerx + self.facing * 8
        pygame.draw.circle(surf, trim_col, (eye_x - 8, mask_r.centery), 5)
        pygame.draw.circle(surf, trim_col, (eye_x + 8, mask_r.centery), 5)

        if self.state in ("charge_prep", "lunge_prep", "dash_prep"):
            pygame.draw.line(surf, self.glow, (r.centerx, r.centery), (r.centerx + self.facing * 540, r.centery), 3)


# --- ГЕНЕРАТОР КОМНАТ И ЭТАЖЕЙ ---
def build_room(depth, room_idx):
    """
    room_idx:
      0 -> Святилище со Скамьёй Древних (безопасный хаб)
      1, 2 -> Боевые залы с платформами, шипами, жилами Гео и врагами
      3 -> Чертог Босса
    """
    platforms = []
    spikes = []
    deposits = []
    enemies = []
    bench_rect = None

    if room_idx == 0:
        bench_rect = pygame.Rect(580, FLOOR_Y - 38, 120, 38)
        platforms.append(Platform(240, 455, 190))
        platforms.append(Platform(850, 455, 190))
        return "sanctuary", platforms, spikes, deposits, enemies, bench_rect

    if room_idx in (1, 2):
        layout = (depth + room_idx) % 3
        if layout == 0:
            platforms = [Platform(190, 470, 220), Platform(530, 355, 220), Platform(870, 470, 220)]
            spikes = [SpikeHazard(450, FLOOR_Y, 380)]
            deposits = [GeoDeposit(640, 355)]
        elif layout == 1:
            platforms = [Platform(150, 485, 210), Platform(430, 385, 190), Platform(710, 295, 210), Platform(940, 445, 210)]
            spikes = [SpikeHazard(360, FLOOR_Y, 220), SpikeHazard(740, FLOOR_Y, 220)]
            deposits = [GeoDeposit(815, 295), GeoDeposit(1050, FLOOR_Y)]
        else:
            platforms = [Platform(220, 440, 240), Platform(820, 440, 240), Platform(510, 315, 260)]
            spikes = [SpikeHazard(300, FLOOR_Y, 680)]
            deposits = [GeoDeposit(640, 315)]

        pool = ["wanderer", "aspid", "shield_knight", "spore", "stalker"]
        count = min(6, 3 + depth // 2)
        for i in range(count):
            kind = random.choice(pool)
            ex = 480 + i * 135 + random.randint(-30, 30)
            ey = 210 if kind in ("aspid", "spore") else (FLOOR_Y - 76)
            enemies.append(Enemy(kind, min(WIDTH - 130, ex), ey, depth))

        return "combat", platforms, spikes, deposits, enemies, None

    # Чертог Босса (room_idx == 3)
    boss_kind = Boss.TYPES[(depth - 1) % len(Boss.TYPES)][0]
    if boss_kind == "radiance":
        platforms = [
            Platform(160, 475, 210),
            Platform(535, 420, 210),
            Platform(910, 475, 210),
            Platform(340, 310, 180),
            Platform(760, 310, 180),
        ]
    else:
        platforms = [Platform(210, 455, 180), Platform(890, 455, 180)]
    return "boss", platforms, spikes, deposits, enemies, None


# --- ОТРИСОВКА ФОНА, СКАМЬИ, HUD И МЕНЮ ---
def draw_environment(surf, biome, ox, oy, room_type, bench_rect, gate_open):
    surf.fill(biome["bg"])
    for px in (150, 440, 840, 1130):
        col_r = pygame.Rect(int(px - 28 + ox * 0.35), 0, 56, FLOOR_Y)
        pygame.draw.rect(surf, biome["pillar"], col_r)
        pygame.draw.line(surf, biome["pillar_edge"], (col_r.left, 0), (col_r.left, FLOOR_Y), 2)

    floor_r = pygame.Rect(int(-20 + ox), int(FLOOR_Y + oy), WIDTH + 40, HEIGHT - FLOOR_Y + 30)
    pygame.draw.rect(surf, biome["floor"], floor_r)
    pygame.draw.line(surf, biome["floor_line"], (0, int(FLOOR_Y + oy)), (WIDTH, int(FLOOR_Y + oy)), 3)

    # Скамья Древних в Святилище
    if bench_rect:
        br = bench_rect.move(int(ox), int(oy))
        # Тёплый фонарь над скамьёй
        pygame.draw.line(surf, (90, 105, 135), (br.centerx, br.top - 95), (br.centerx, br.top), 3)
        pygame.draw.circle(surf, (255, 235, 175), (br.centerx, br.top - 95), 11)
        pygame.draw.circle(surf, (255, 245, 210), (br.centerx, br.top - 95), 5)
        # Сама скамья
        pygame.draw.rect(surf, (135, 150, 180), (br.left, br.top + 12, br.width, 10), border_radius=3)
        pygame.draw.rect(surf, (105, 120, 150), (br.left + 8, br.top, br.width - 16, 8), border_radius=3)
        pygame.draw.rect(surf, (95, 110, 140), (br.left + 12, br.top + 12, 10, 26))
        pygame.draw.rect(surf, (95, 110, 140), (br.right - 22, br.top + 12, 10, 26))

    # Правые врата перехода в следующую комнату
    gate_x = WIDTH - 44 + int(ox)
    gate_top = FLOOR_Y - 165 + int(oy)
    if gate_open:
        pygame.draw.rect(surf, biome["floor_line"], (gate_x, gate_top, 14, 165), border_radius=5)
        pygame.draw.rect(surf, (240, 250, 255), (gate_x + 4, gate_top + 12, 6, 141), border_radius=3)
    else:
        pygame.draw.rect(surf, (185, 55, 85), (gate_x, gate_top, 14, 165), border_radius=5)


def draw_hud(surf, player, boss, depth, room_idx, biome_name):
    f_title = get_font(22, bold=True)
    f_small = get_font(17)
    f_tiny = get_font(15)

    # Сосуд Души
    sc = (58, 56)
    pygame.draw.circle(surf, (22, 26, 40), sc, 34)
    ratio = player.soul / player.max_soul
    if ratio > 0:
        pygame.draw.circle(surf, (215, 242, 255), sc, int(30 * math.sqrt(ratio)))
    pygame.draw.circle(surf, (165, 190, 225), sc, 34, 3)

    # Маски здоровья
    for i in range(player.max_hp):
        mx = 112 + i * 33
        my = 34
        mr = pygame.Rect(mx, my, 23, 28)
        if i < player.hp:
            col = (110, 190, 255) if i >= player.base_max_hp else (244, 248, 255)
            pygame.draw.rect(surf, col, mr, border_radius=8)
            pygame.draw.circle(surf, (14, 18, 28), (mx + 8, my + 13), 2)
            pygame.draw.circle(surf, (14, 18, 28), (mx + 15, my + 13), 2)
        else:
            pygame.draw.rect(surf, (45, 52, 72), mr, 2, border_radius=8)

    # Счётчик Гео под масками
    pygame.draw.polygon(surf, (230, 245, 255), [(120, 78), (127, 86), (120, 94), (113, 86)])
    geo_txt = f_title.render(f"{player.geo}", True, (240, 246, 255))
    surf.blit(geo_txt, (136, 73))

    # Локация и прогресс этажа справа сверху
    stage_names = ["Святилище", "Зал I", "Зал II", "Чертог Босса"]
    loc_txt = f_small.render(f"Глубина {depth}: {biome_name}  •  {stage_names[room_idx]}", True, (195, 210, 238))
    surf.blit(loc_txt, (WIDTH - loc_txt.get_width() - 28, 28))

    help_txt = f_tiny.render("ЛКМ/J: Удар (W/S+Удар)  |  ПКМ/Shift: Рывок  |  Q/СКМ: Заклинание (W/S+Q)  |  E: Лечение  |  TAB: Билд", True, (130, 145, 175))
    surf.blit(help_txt, (WIDTH - help_txt.get_width() - 28, 54))

    # Полоска HP босса
    if boss and boss.hp > 0:
        bw, bh = 740, 18
        bx = (WIDTH - bw) // 2
        by = HEIGHT - 50
        t = f_title.render(boss.name, True, (242, 245, 255))
        surf.blit(t, ((WIDTH - t.get_width()) // 2, by - 30))
        pygame.draw.rect(surf, (22, 22, 34), (bx, by, bw, bh), border_radius=6)
        hw = int(bw * (boss.hp / boss.max_hp))
        if hw > 0:
            pygame.draw.rect(surf, boss.primary, (bx, by, hw, bh), border_radius=6)
        pygame.draw.rect(surf, (165, 175, 205), (bx, by, bw, bh), 2, border_radius=6)


def draw_bench_menu(surf, player, tab_idx, selected_idx, at_bench):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 215))
    surf.blit(overlay, (0, 0))

    panel = pygame.Rect(140, 75, WIDTH - 280, HEIGHT - 150)
    pygame.draw.rect(surf, (18, 22, 34), panel, border_radius=16)
    pygame.draw.rect(surf, (110, 135, 180), panel, 2, border_radius=16)

    f_head = get_font(28, bold=True)
    f_med = get_font(20, bold=True)
    f_reg = get_font(18)

    mode_str = "СКАМЬЯ ДРЕВНИХ (Можно менять амулеты и покупать улучшения)" if at_bench else "ОБЗОР СНАРЯЖЕНИЯ (Сядь на скамью в Святилище, чтобы менять билд)"
    h_txt = f_head.render(mode_str, True, (240, 245, 255))
    surf.blit(h_txt, (panel.left + 32, panel.top + 22))

    # Вкладки
    tabs = ["[1] Амулеты", "[2] Кузница и Улучшения"]
    for i, tname in enumerate(tabs):
        tx = panel.left + 32 + i * 240
        ty = panel.top + 68
        col = (120, 225, 255) if i == tab_idx else (130, 145, 175)
        surf.blit(f_med.render(tname, True, col), (tx, ty))

    # Индикатор Ячеек и Гео
    notch_info = f_med.render(f"Ячейки: {player.used_notches()}/{player.max_notches}   |   Гео: {player.geo}", True, (255, 225, 120))
    surf.blit(notch_info, (panel.right - notch_info.get_width() - 32, panel.top + 68))

    pygame.draw.line(surf, (55, 68, 98), (panel.left + 24, panel.top + 104), (panel.right - 24, panel.top + 104), 2)

    if tab_idx == 0:
        # Сетка амулетов (2 колонки по 6)
        for idx, ch in enumerate(CHARMS):
            col_i = idx % 2
            row_i = idx // 2
            bx = panel.left + 34 + col_i * 465
            by = panel.top + 122 + row_i * 58
            box = pygame.Rect(bx, by, 445, 48)

            is_sel = idx == selected_idx
            is_eq = ch["id"] in player.equipped
            bg_col = (34, 44, 68) if is_sel else (24, 29, 44)
            border_col = (130, 230, 255) if is_sel else ((110, 220, 145) if is_eq else (52, 62, 86))
            pygame.draw.rect(surf, bg_col, box, border_radius=9)
            pygame.draw.rect(surf, border_col, box, 2, border_radius=9)

            pygame.draw.circle(surf, ch["color"] if ch["unlocked"] else (70, 75, 90), (bx + 24, by + 24), 12)
            status = "[НАДЕТО]" if is_eq else (f"{ch['notches']} яч." if ch["unlocked"] else f"Открыть: {ch['cost']} Гео")
            name_col = (245, 248, 255) if ch["unlocked"] else (150, 160, 180)
            surf.blit(f_med.render(ch["name"], True, name_col), (bx + 46, by + 11))
            st_img = f_reg.render(status, True, (130, 240, 175) if is_eq else (235, 205, 120))
            surf.blit(st_img, (box.right - st_img.get_width() - 14, by + 13))

        cur = CHARMS[selected_idx % len(CHARMS)]
        desc_r = pygame.Rect(panel.left + 34, panel.bottom - 88, panel.width - 68, 42)
        pygame.draw.rect(surf, (24, 30, 46), desc_r, border_radius=8)
        surf.blit(f_reg.render(f"{cur['name']} ({cur['notches']} яч.): {cur['desc']}", True, (220, 235, 255)), (desc_r.left + 16, desc_r.top + 10))

    else:
        # Кузница и улучшения
        upgrades = [
            ("Заточка Гвоздя (+4 к базовому урону)", 110 + (player.base_damage - 15) * 20, f"Текущий урон: {player.nail_damage}"),
            ("Осколок Древней Маски (+1 макс. здоровье)", 140 + (player.base_max_hp - 6) * 65, f"Макс. масок: {player.max_hp}"),
            ("Ячейка Амулетов (+1 слот для амулетов)", 130 + (player.max_notches - 4) * 55, f"Всего ячеек: {player.max_notches}/12"),
            ("Сосуд Души (+25 к запасу Души)", 120 + int((player.max_soul - 100) * 2), f"Макс. Души: {int(player.max_soul)}"),
        ]
        for idx, (title, cost, cur_val) in enumerate(upgrades):
            by = panel.top + 135 + idx * 78
            box = pygame.Rect(panel.left + 38, by, panel.width - 76, 62)
            is_sel = idx == (selected_idx % len(upgrades))
            pygame.draw.rect(surf, (34, 44, 68) if is_sel else (24, 29, 44), box, border_radius=10)
            pygame.draw.rect(surf, (130, 230, 255) if is_sel else (55, 66, 92), box, 2, border_radius=10)
            surf.blit(f_med.render(title, True, (242, 246, 255)), (box.left + 20, box.top + 10))
            surf.blit(f_reg.render(cur_val, True, (165, 190, 225)), (box.left + 20, box.top + 35))
            c_img = f_med.render(f"Купить: {cost} Гео", True, (255, 220, 115))
            surf.blit(c_img, (box.right - c_img.get_width() - 22, box.top + 18))

    foot = f_reg.render("Стрелки / WASD: Выбор   |   Enter / Пробел: Надеть или Купить   |   ESC / TAB: Закрыть меню", True, (165, 185, 215))
    surf.blit(foot, ((WIDTH - foot.get_width()) // 2, panel.bottom - 34))


# --- ОСНОВНОЙ ИГРОВОЙ ЦИКЛ ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Void Knight: Abyssal Odyssey")
    clock = pygame.time.Clock()

    f_big = get_font(56, bold=True)
    f_med = get_font(26, bold=True)
    f_prompt = get_font(20, bold=True)

    fullscreen = False
    game_state = "title"  # title | playing | bench_menu | game_over

    def reset_game():
        for c in CHARMS:
            c["unlocked"] = c["cost"] == 0
        p = Player()
        p.recalculate_stats()
        rtype, plats, spks, deps, enms, b_rect = build_room(1, 0)
        return p, 1, 0, rtype, plats, spks, deps, enms, b_rect, None, [], [], [], [], [], [], []

    (
        player,
        depth,
        room_idx,
        room_type,
        platforms,
        spikes,
        deposits,
        enemies,
        bench_rect,
        boss,
        particles,
        afterimages,
        floating_texts,
        geo_shards,
        shockwaves,
        projectiles,
        lasers,
    ) = reset_game()
    spells = []

    hitstop = 0.0
    shake = 0.0
    banner_timer = 0.0
    banner_text = ""
    menu_tab = 0
    menu_sel = 0
    at_bench = False

    def enter_room(new_depth, new_room_idx):
        nonlocal depth, room_idx, room_type, platforms, spikes, deposits, enemies, bench_rect, boss
        nonlocal shockwaves, projectiles, lasers, spells, banner_timer, banner_text
        depth = new_depth
        room_idx = new_room_idx
        room_type, platforms, spikes, deposits, enemies, bench_rect = build_room(depth, room_idx)
        shockwaves.clear()
        projectiles.clear()
        lasers.clear()
        spells.clear()
        player.x = 85.0
        player.y = float(FLOOR_Y - player.rect.height)
        player.vx = 0.0
        player.vy = 0.0
        player.rect.topleft = (int(player.x), int(player.y))

        if room_type == "boss":
            boss = Boss(depth)
            banner_text = boss.name
            banner_timer = 2.1
        else:
            boss = None
            if room_idx == 0:
                banner_text = f"ГЛУБИНА {depth} • {BIOMES[(depth - 1) % len(BIOMES)]['name']}"
                banner_timer = 1.8

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
                        banner_text = f"ГЛУБИНА 1 • {biome['name']}"
                        banner_timer = 2.0

                elif game_state == "game_over":
                    if event.key == pygame.K_r:
                        (
                            player,
                            depth,
                            room_idx,
                            room_type,
                            platforms,
                            spikes,
                            deposits,
                            enemies,
                            bench_rect,
                            boss,
                            particles,
                            afterimages,
                            floating_texts,
                            geo_shards,
                            shockwaves,
                            projectiles,
                            lasers,
                        ) = reset_game()
                        spells.clear()
                        game_state = "playing"

                elif game_state == "bench_menu":
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
                        menu_sel = (menu_sel - step) % (len(CHARMS) if menu_tab == 0 else 4)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        step = 2 if menu_tab == 0 else 1
                        menu_sel = (menu_sel + step) % (len(CHARMS) if menu_tab == 0 else 4)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and menu_tab == 0:
                        menu_sel = (menu_sel - 1) % len(CHARMS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and menu_tab == 0:
                        menu_sel = (menu_sel + 1) % len(CHARMS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and at_bench:
                        if menu_tab == 0:
                            ch = CHARMS[menu_sel]
                            if not ch["unlocked"]:
                                if player.geo >= ch["cost"]:
                                    player.geo -= ch["cost"]
                                    ch["unlocked"] = True
                            else:
                                if ch["id"] in player.equipped:
                                    player.equipped.remove(ch["id"])
                                elif player.used_notches() + ch["notches"] <= player.max_notches:
                                    player.equipped.append(ch["id"])
                                player.recalculate_stats()
                                player.hp = player.max_hp
                        else:
                            idx = menu_sel % 4
                            if idx == 0:
                                cost = 110 + (player.base_damage - 15) * 20
                                if player.geo >= cost:
                                    player.geo -= cost
                                    player.base_damage += 4
                            elif idx == 1:
                                cost = 140 + (player.base_max_hp - 6) * 65
                                if player.geo >= cost and player.base_max_hp < 12:
                                    player.geo -= cost
                                    player.base_max_hp += 1
                                    player.recalculate_stats()
                                    player.hp = player.max_hp
                            elif idx == 2:
                                cost = 130 + (player.max_notches - 4) * 55
                                if player.geo >= cost and player.max_notches < 12:
                                    player.geo -= cost
                                    player.max_notches += 1
                            elif idx == 3:
                                cost = 120 + int((player.max_soul - 100) * 2)
                                if player.geo >= cost and player.max_soul < 200:
                                    player.geo -= cost
                                    player.max_soul += 25.0
                                    player.soul = player.max_soul

                elif game_state == "playing":
                    if event.key == pygame.K_TAB:
                        at_bench = False
                        game_state = "bench_menu"

                    # Взаимодействие со Скамьёй в Святилище
                    if room_type == "sanctuary" and bench_rect and player.rect.colliderect(bench_rect.inflate(40, 20)):
                        if event.key in (pygame.K_w, pygame.K_e):
                            player.hp = player.max_hp
                            player.soul = player.max_soul
                            at_bench = True
                            game_state = "bench_menu"
                            continue

                    # Спрыгнуть вниз с платформы: S + Space
                    if event.key == pygame.K_SPACE and (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.on_ground and player.y + player.rect.height < FLOOR_Y - 5:
                        player.drop_through_timer = 0.22
                        player.on_ground = False
                    elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        if player.jumps_left > 0 and player.dash_timer <= 0 and not player.dive_active:
                            player.vy = -805.0
                            player.jumps_left -= 1
                            player.on_ground = False
                            player.jump_held = True
                            for _ in range(9):
                                particles.append(Particle(player.rect.centerx + random.uniform(-12, 12), player.rect.bottom, random.uniform(-110, 110), random.uniform(20, 110), (210, 235, 255), 5, 0.28))

                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k):
                        if player.start_dash():
                            shake = max(shake, 4.0)

                    elif event.key == pygame.K_j:
                        player.start_slash(keys)

                    elif event.key in (pygame.K_q, pygame.K_c):
                        if player.cast_spell(keys, spells, particles):
                            shake = max(shake, 7.0)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    player.jump_held = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
                if event.button == 1:
                    player.start_slash(keys)
                elif event.button == 3:
                    if player.start_dash():
                        shake = max(shake, 4.0)
                elif event.button == 2:
                    if player.cast_spell(keys, spells, particles):
                        shake = max(shake, 7.0)

        # --- ОБНОВЛЕНИЕ ЛОГИКИ ИГРЫ ---
        if game_state == "playing":
            banner_timer = max(0.0, banner_timer - dt)
            if random.random() < 0.35:
                particles.append(Particle(random.randint(40, WIDTH - 40), random.randint(40, FLOOR_Y - 20), random.uniform(-18, 18), random.uniform(-25, -8), biome["dust"], 3, 2.2))

            if hitstop > 0:
                hitstop -= dt
            else:
                player.update(dt, keys, platforms, particles, afterimages, spells, shockwaves)

                for d in deposits:
                    d.update(dt)
                for en in enemies:
                    en.update(dt, player, projectiles, particles)
                if boss and boss.hp > 0:
                    boss.update(dt, player, projectiles, shockwaves, lasers, enemies, particles)

                for sw in shockwaves:
                    sw.update(dt)
                for pr in projectiles:
                    pr.update(dt, player)
                for lz in lasers:
                    lz.update(dt)
                for sp in spells:
                    sp.update(dt)
                for gs in geo_shards:
                    gs.update(dt, player, magnet=player.has_charm("swarm"))
                for pt in particles:
                    pt.update(dt)
                for ai in afterimages:
                    ai.update(dt)
                for ft in floating_texts:
                    ft.update(dt)

                shockwaves = [s for s in shockwaves if s.life > 0]
                projectiles = [p for p in projectiles if p.life > 0 and 0 <= p.x <= WIDTH and p.y <= FLOOR_Y + 20]
                lasers = [l for l in lasers if l.timer > 0]
                spells = [s for s in spells if s.life > 0 and -200 <= s.x <= WIDTH + 200]
                particles = [p for p in particles if p.life > 0]
                afterimages = [a for a in afterimages if a.life > 0]
                floating_texts = [f for f in floating_texts if f.life > 0]

                # Сбор Гео
                for gs in list(geo_shards):
                    if gs.life <= 0:
                        geo_shards.remove(gs)
                    elif player.rect.colliderect(gs.rect.inflate(14, 14)):
                        bonus = int(round(gs.value * (1.25 if player.has_charm("swarm") else 1.0)))
                        player.geo += bonus
                        geo_shards.remove(gs)

                # Урон от клинка игрока
                s_rect = player.get_slash_rect()
                soul_gain = 16.0 if player.has_charm("soul_catcher") else 11.0
                pogo_vy = -810.0 if player.has_charm("mark_of_pride") else -740.0

                if s_rect:
                    # Пого-отскок от шипов!
                    if player.slash_dir == "down":
                        for spk in spikes:
                            if s_rect.colliderect(spk.rect):
                                player.vy = pogo_vy
                                player.reset_air_mobility()
                                for _ in range(8):
                                    particles.append(Particle(player.rect.centerx, spk.rect.top, random.uniform(-160, 160), random.uniform(-220, -40), (220, 240, 255), 4, 0.25))
                                break

                    # Жилы Гео
                    for dep in deposits:
                        if dep.hp > 0 and s_rect.colliderect(dep.rect) and id(dep) not in player.hit_ids:
                            player.hit_ids.add(id(dep))
                            dep.hp -= 1
                            dep.flash = 0.08
                            shake = max(shake, 5.0)
                            for _ in range(4 if dep.hp > 0 else 10):
                                geo_shards.append(GeoShard(dep.rect.centerx, dep.rect.centery, 6))

                    # Обычные враги
                    for en in list(enemies):
                        if s_rect.colliderect(en.rect) and id(en) not in player.hit_ids:
                            player.hit_ids.add(id(en))
                            # Проверка щита у Рыцаря со щитом
                            blocked = (
                                en.kind == "shield_knight"
                                and player.slash_dir in ("left", "right")
                                and ((en.facing == -1 and player.rect.centerx < en.rect.centerx) or (en.facing == 1 and player.rect.centerx > en.rect.centerx))
                            )
                            if blocked:
                                player.vx = -player.facing * 320.0
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, "БЛОК!", (180, 210, 255), 18))
                                for _ in range(10):
                                    particles.append(Particle(en.rect.centerx, en.rect.centery, random.uniform(-220, 220), random.uniform(-220, 220), (200, 230, 255), 5, 0.25))
                            else:
                                dmg = player.nail_damage
                                en.hp -= dmg
                                en.flash = 0.08
                                player.soul = min(player.max_soul, player.soul + soul_gain)
                                hitstop = 0.028
                                shake = max(shake, 6.0)
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, dmg, (255, 255, 255), 20))
                                if player.slash_dir == "down":
                                    player.vy = pogo_vy
                                    player.reset_air_mobility()
                                else:
                                    en.vx += player.facing * 260.0

                    # Босс
                    if boss and boss.hp > 0 and s_rect.colliderect(boss.rect) and id(boss) not in player.hit_ids:
                        player.hit_ids.add(id(boss))
                        dmg = player.nail_damage
                        boss.take_damage(dmg)
                        player.soul = min(player.max_soul, player.soul + soul_gain)
                        hitstop = 0.036
                        shake = max(shake, 8.0)
                        floating_texts.append(FloatingText(boss.rect.centerx + random.randint(-20, 20), boss.rect.top - 14, dmg, (255, 245, 220), 23))
                        if player.slash_dir == "down":
                            player.vy = pogo_vy
                            player.reset_air_mobility()
                        elif player.slash_dir == "left":
                            player.vx = 230.0
                        elif player.slash_dir == "right":
                            player.vx = -230.0

                # Урон от Пронизывающей Тени при рывке
                if player.dash_timer > 0 and player.has_charm("sharp_shadow"):
                    sdmg = int(player.nail_damage * 1.1)
                    for en in enemies:
                        if player.rect.colliderect(en.rect) and id(en) not in player.dash_hit_ids:
                            player.dash_hit_ids.add(id(en))
                            en.hp -= sdmg
                            en.flash = 0.08
                            floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, sdmg, (185, 130, 255), 20))
                    if boss and boss.hp > 0 and player.rect.colliderect(boss.rect) and id(boss) not in player.dash_hit_ids:
                        player.dash_hit_ids.add(id(boss))
                        boss.take_damage(sdmg)
                        floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 14, sdmg, (185, 130, 255), 22))

                # Урон от заклинаний игрока
                for sp in spells:
                    for en in enemies:
                        if sp.rect.colliderect(en.rect) and id(en) not in sp.hit_ids:
                            sp.hit_ids.add(id(en))
                            en.hp -= sp.damage
                            en.flash = 0.1
                            shake = max(shake, 8.0)
                            floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 12, f"{sp.damage}!", (150, 225, 255), 24))
                    if boss and boss.hp > 0 and sp.rect.colliderect(boss.rect) and id(boss) not in sp.hit_ids:
                        sp.hit_ids.add(id(boss))
                        boss.take_damage(sp.damage)
                        hitstop = 0.04
                        shake = max(shake, 10.0)
                        floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 18, f"{sp.damage}!", (150, 225, 255), 26))

                # Смерть обычных врагов -> выпадение Гео
                for en in list(enemies):
                    if en.hp <= 0:
                        enemies.remove(en)
                        for _ in range(max(2, en.geo // 4)):
                            geo_shards.append(GeoShard(en.rect.centerx, en.rect.centery, 4))
                        for _ in range(18):
                            ang = random.uniform(0, math.tau)
                            spd = random.uniform(90, 320)
                            particles.append(Particle(en.rect.centerx, en.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, (215, 235, 255), 6, 0.4))

                # Проверка получения урона игроком
                intangible = player.dash_timer > 0 or player.invuln_timer > 0 or player.dive_active
                if not intangible:
                    hurt = False
                    for spk in spikes:
                        if player.rect.colliderect(spk.rect):
                            hurt = True
                    for en in enemies:
                        if player.rect.colliderect(en.rect):
                            hurt = True
                    if boss and boss.hp > 0 and boss.state != "stagger" and player.rect.colliderect(boss.rect):
                        hurt = True
                    if boss and boss.clone_rect and player.rect.colliderect(boss.clone_rect):
                        hurt = True
                    for sw in shockwaves:
                        if not sw.friendly and player.rect.colliderect(sw.rect):
                            hurt = True
                    for pr in projectiles:
                        if player.rect.colliderect(pr.rect):
                            hurt = True
                    for lz in lasers:
                        if lz.collides_rect(player.rect):
                            hurt = True

                    if hurt:
                        player.hp -= 1
                        player.invuln_timer = 1.2
                        player.focus_timer = 0.0
                        hitstop = 0.055
                        shake = 14.0
                        player.vy = -440.0
                        player.vx = -player.facing * 360.0

                        if player.has_charm("grubsong"):
                            player.soul = min(player.max_soul, player.soul + 25.0)
                        if player.has_charm("thorns"):
                            thorn_r = player.rect.inflate(180, 180)
                            for en in enemies:
                                if thorn_r.colliderect(en.rect):
                                    en.hp -= player.nail_damage * 2
                            if boss and boss.hp > 0 and thorn_r.colliderect(boss.rect):
                                boss.take_damage(player.nail_damage * 2)
                            for _ in range(30):
                                ang = random.uniform(0, math.tau)
                                particles.append(Particle(player.rect.centerx, player.rect.centery, math.cos(ang) * 420, math.sin(ang) * 420, (140, 230, 130), 7, 0.35))

                        if player.hp <= 0:
                            game_state = "game_over"

                # Победа над боссом
                if room_type == "boss" and boss and boss.hp <= 0:
                    shake = 18.0
                    hitstop = 0.08
                    banner_text = f"{boss.name} ПОВЕРЖЕН!"
                    banner_timer = 2.4
                    for _ in range(28):
                        geo_shards.append(GeoShard(boss.rect.centerx, boss.rect.centery, 8))
                    for _ in range(65):
                        ang = random.uniform(0, math.tau)
                        spd = random.uniform(140, 620)
                        particles.append(Particle(boss.rect.centerx, boss.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, boss.glow, 9, 0.8))
                    shockwaves.clear()
                    projectiles.clear()
                    lasers.clear()
                    boss = None

                # Переход в следующую комнату через правые врата
                gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
                if gate_open and player.rect.right >= WIDTH - 44:
                    if room_idx < 3:
                        enter_room(depth, room_idx + 1)
                    else:
                        enter_room(depth + 1, 0)

        # --- ОТРИСОВКА ---
        shake = max(0.0, shake - 44.0 * dt)
        ox = random.uniform(-shake, shake) if shake > 0 else 0.0
        oy = random.uniform(-shake, shake) if shake > 0 else 0.0

        gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
        draw_environment(screen, biome, ox, oy, room_type, bench_rect, gate_open)

        for plat in platforms:
            plat.draw(screen, ox, oy, biome)
        for spk in spikes:
            spk.draw(screen, ox, oy)
        for dep in deposits:
            dep.draw(screen, ox, oy)
        for ai in afterimages:
            ai.draw(screen, ox, oy)
        for sw in shockwaves:
            sw.draw(screen, ox, oy)
        for en in enemies:
            en.draw(screen, ox, oy)
        if boss and boss.hp > 0:
            boss.draw(screen, ox, oy)
        player.draw(screen, ox, oy)
        for sp in spells:
            sp.draw(screen, ox, oy)
        for pr in projectiles:
            pr.draw(screen, ox, oy)
        for lz in lasers:
            lz.draw(screen, ox, oy)
        for gs in geo_shards:
            gs.draw(screen, ox, oy)
        for pt in particles:
            pt.draw(screen, ox, oy)
        for ft in floating_texts:
            ft.draw(screen, ox, oy)

        # Подсказка у Скамьи
        if game_state == "playing" and room_type == "sanctuary" and bench_rect and player.rect.colliderect(bench_rect.inflate(40, 20)):
            p_img = f_prompt.render("[W / E] Сесть на Скамью (Лечение, Амулеты и Улучшения)", True, (255, 242, 185))
            screen.blit(p_img, (bench_rect.centerx - p_img.get_width() // 2 + int(ox), bench_rect.top - 135 + int(oy)))

        draw_hud(screen, player, boss, depth, room_idx, biome["name"])

        # Баннер входа в биом или появления босса
        if banner_timer > 0 and game_state == "playing":
            b_img = f_med.render(banner_text, True, (245, 248, 255))
            bx = (WIDTH - b_img.get_width()) // 2
            by = 135
            pygame.draw.line(screen, biome["floor_line"], (bx - 40, by + 38), (bx + b_img.get_width() + 40, by + 38), 2)
            screen.blit(b_img, (bx, by))

        if game_state == "title":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 10, 18, 195))
            screen.blit(ov, (0, 0))
            t1 = f_big.render("VOID KNIGHT: ABYSSAL ODYSSEY", True, (245, 248, 255))
            t2 = f_med.render("Нажми ENTER или ПРОБЕЛ, чтобы спуститься в Бездну", True, (150, 215, 255))
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 55))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 20))

        elif game_state == "bench_menu":
            draw_bench_menu(screen, player, menu_tab, menu_sel, at_bench)

        elif game_state == "game_over":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 10, 18, 200))
            screen.blit(ov, (0, 0))
            t1 = f_big.render("ТЕНЬ РАССЕЯЛАСЬ", True, (245, 248, 255))
            t2 = f_med.render(f"Достигнута Глубина: {depth}   |   Нажми R, чтобы начать новый забег", True, (185, 205, 235))
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 50))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 20))

        pygame.display.flip()


if __name__ == "__main__":
    main()
