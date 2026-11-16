import math
import os
import random
import sys
import pygame
from data import WIDTH, HEIGHT, FLOOR_Y, BIOMES, BOSS_DEFS

_FONT_CACHE = {}


def resource_path(rel_path):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)


def get_font(size, bold=False):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    font_path = resource_path(os.path.join("assets", "fonts", "AstralFont.ttf"))
    if os.path.exists(font_path):
        try:
            f = pygame.font.Font(font_path, size)
            f.set_bold(bold)
            _FONT_CACHE[key] = f
            return f
        except Exception:
            pass
    f = pygame.font.SysFont("segoeui,arial,tahoma,dejavusans", size, bold=bold)
    _FONT_CACHE[key] = f
    return f


class AssetLibrary:
    """Загружает 2K-слои и HD-спрайты с диска и подготавливает их для рендера в 180 FPS."""
    def __init__(self):
        self.biome_layers = {}
        self.floor_tiles = {}
        self.hero_frames = []
        self.enemy_frames = {}
        self.boss_frames = {}
        self._load_all()

    def _load_all(self):
        bg_dir = resource_path(os.path.join("assets", "bg"))
        spr_dir = resource_path(os.path.join("assets", "sprites"))

        for biome in BIOMES:
            bid = biome["id"]
            sky_raw = pygame.image.load(os.path.join(bg_dir, f"{bid}_sky.tga")).convert()
            far_raw = pygame.image.load(os.path.join(bg_dir, f"{bid}_far.tga")).convert_alpha()
            mid_raw = pygame.image.load(os.path.join(bg_dir, f"{bid}_mid.tga")).convert_alpha()
            mist_raw = pygame.image.load(os.path.join(bg_dir, f"{bid}_mist.tga")).convert_alpha()
            fl_raw = pygame.image.load(os.path.join(bg_dir, f"{bid}_floor.tga")).convert()

            self.biome_layers[bid] = {
                "sky": pygame.transform.smoothscale(sky_raw, (WIDTH, FLOOR_Y)),
                "far": pygame.transform.smoothscale(far_raw, (WIDTH + 120, FLOOR_Y)),
                "mid": pygame.transform.smoothscale(mid_raw, (WIDTH + 160, FLOOR_Y)),
                "mist": pygame.transform.smoothscale(mist_raw, (WIDTH + 160, FLOOR_Y)),
            }
            self.floor_tiles[bid] = pygame.transform.smoothscale(fl_raw, (256, 256))

        for f in range(8):
            raw = pygame.image.load(os.path.join(spr_dir, f"hero_{f}.tga")).convert_alpha()
            self.hero_frames.append(pygame.transform.smoothscale(raw, (76, 76)))

        enemy_sizes = {
            "sentinel": (64, 64),
            "prism_drone": (60, 60),
            "aegis_warden": (84, 96),
            "nova_orb": (54, 54),
            "rift_assassin": (64, 72),
        }
        for ek, sz in enemy_sizes.items():
            frames = []
            for f in range(2):
                raw = pygame.image.load(os.path.join(spr_dir, f"enemy_{ek}_{f}.tga")).convert_alpha()
                frames.append(pygame.transform.smoothscale(raw, sz))
            self.enemy_frames[ek] = frames

        for bkind, _, _, _, _ in BOSS_DEFS:
            sz = (148, 162) if bkind == "colossus" else ((136, 150) if bkind == "solaris" else (122, 146))
            frames = []
            for f in range(4):
                raw = pygame.image.load(os.path.join(spr_dir, f"boss_{bkind}_{f}.tga")).convert_alpha()
                frames.append(pygame.transform.smoothscale(raw, sz))
            self.boss_frames[bkind] = frames


class BloomRenderer:
    """Многопроходный Bloom-буфер через smoothscale + аддитивное смешивание."""
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
        mid = pygame.transform.smoothscale(self.buffer, (WIDTH // 2, HEIGHT // 2))
        full = pygame.transform.smoothscale(mid, (WIDTH, HEIGHT))
        target_surf.blit(full, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


class RibbonTrail:
    """Ленточный шлейф клинка, оптимизированный под 180 FPS."""
    def __init__(self):
        self.points = []
        self.sample_timer = 0.0
        self.surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def add(self, tip, base, color, dt):
        self.sample_timer -= dt
        if self.sample_timer <= 0:
            self.sample_timer = 0.008
            self.points.append([tip[0], tip[1], base[0], base[1], 0.14, color])
            if len(self.points) > 16:
                self.points.pop(0)

    def update(self, dt):
        for p in self.points:
            p[4] -= dt
        self.points = [p for p in self.points if p[4] > 0]

    def draw(self, surf, bloom, ox, oy):
        if len(self.points) < 2:
            return
        self.surf.fill((0, 0, 0, 0))
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
            pygame.draw.polygon(self.surf, (*col, int(190 * ratio)), poly)
            pygame.draw.line(self.surf, (255, 255, 255, int(230 * ratio)), (p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy), max(2, int(4 * ratio)))
            bloom.add_line((p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy), col, 14)
        surf.blit(self.surf, (0, 0))


class SparkParticle:
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
        x2, y2 = x1 - self.vx * 0.025, y1 - self.vy * 0.025
        pygame.draw.line(surf, self.color, (x1, y1), (x2, y2), max(1, int(self.size * ratio)))
        bloom.add_glow(x1, y1, 14 * ratio, self.color, int(130 * ratio))


class RingWave:
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


def draw_world_backdrop(surf, bloom, assets, biome, ox, oy, altar_rect, gate_open):
    layers = assets.biome_layers[biome["id"]]
    t = pygame.time.get_ticks() * 0.001

    surf.blit(layers["sky"], (0, 0))
    surf.blit(layers["far"], (int(-60 + ox * 0.25), int(oy * 0.15)))
    surf.blit(layers["mid"], (int(-80 + ox * 0.45), int(oy * 0.25)))
    surf.blit(layers["mist"], (int(-80 + ox * 0.65), 0))

    cx, cy = int(WIDTH * 0.5 + ox * 0.12), int(215 + oy * 0.12)
    bloom.add_glow(cx, cy, 290, biome["accent"], 125)
    if biome["weather"] == "eclipse":
        pygame.draw.circle(surf, (255, 225, 130), (cx, cy), 86)
        pygame.draw.circle(surf, (10, 8, 16), (cx, cy), 78)

    if altar_rect:
        ar = altar_rect.move(int(ox), int(oy))
        bloom.add_glow(ar.centerx, ar.centery - 15, 140, biome["accent"], 160)
        pts = [(ar.centerx, ar.top), (ar.right, ar.top + 36), (ar.right - 10, ar.bottom), (ar.left + 10, ar.bottom), (ar.left, ar.top + 36)]
        pygame.draw.polygon(surf, biome["stone_mid"], pts)
        pygame.draw.polygon(surf, biome["accent"], pts, 3)
        fy = ar.top + 56 + int(math.sin(t * 3.5) * 6)
        pygame.draw.polygon(surf, (255, 255, 255), [(ar.centerx, fy - 14), (ar.centerx + 10, fy), (ar.centerx, fy + 14), (ar.centerx - 10, fy)])

    gx = WIDTH - 42 + int(ox)
    gtop = FLOOR_Y - 175 + int(oy)
    if gate_open:
        bloom.add_glow(gx + 6, gtop + 88, 95, biome["accent"], 160)
        pygame.draw.rect(surf, biome["accent"], (gx, gtop, 12, 175), border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), (gx + 4, gtop + 14, 4, 147), border_radius=2)
    else:
        pygame.draw.rect(surf, (215, 65, 95), (gx, gtop, 12, 175), border_radius=5)


def draw_reflective_floor(surf, assets, entity_layer, biome, ox, oy):
    fy = int(FLOOR_Y + oy)
    tile = assets.floor_tiles[biome["id"]]

    for tx in range(-256, WIDTH + 256, 256):
        surf.blit(tile, (tx + int(ox), fy))

    ref_h = min(HEIGHT - fy, 135)
    if ref_h > 10:
        crop = entity_layer.subsurface((0, max(0, FLOOR_Y - ref_h), WIDTH, ref_h))
        flipped = pygame.transform.flip(crop, False, True)
        flipped.set_alpha(66)
        surf.blit(flipped, (int(ox), fy + 2))

    pygame.draw.line(surf, biome["accent"], (0, fy), (WIDTH, fy), 3)
    pygame.draw.line(surf, (255, 255, 255), (0, fy), (WIDTH, fy), 1)
