import math
import random
import pygame
from data import WIDTH, FLOOR_Y, GRAVITY, WEAPONS, RELICS, SYNERGIES
from gfx import RibbonTrail, SparkParticle, RingWave, FloatingText


class Platform:
    def __init__(self, x, y, w, h=18):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surf, bloom, ox, oy, biome):
        r = self.rect.move(int(ox), int(oy))
        pygame.draw.rect(surf, biome["stone_dark"], r, border_radius=6)
        pygame.draw.rect(surf, biome["stone_rim"], r, 2, border_radius=6)
        pygame.draw.line(surf, biome["accent"], (r.left + 8, r.top + 1), (r.right - 8, r.top + 1), 2)
        bloom.add_line((r.left + 10, r.top + 2), (r.right - 10, r.top + 2), biome["accent"], 6)


class CrystalHazard:
    def __init__(self, x, y, w):
        self.rect = pygame.Rect(x, y - 24, w, 24)

    def draw(self, surf, bloom, ox, oy, biome):
        r = self.rect.move(int(ox), int(oy))
        step = 20
        for sx in range(r.left, r.right - 6, step):
            pts = [(sx + 2, r.bottom), (sx + step // 2, r.top), (sx + step - 2, r.bottom)]
            pygame.draw.polygon(surf, biome["stone_mid"], pts)
            pygame.draw.polygon(surf, biome["accent"], pts, 2)
        bloom.add_line((r.left, r.top + 8), (r.right, r.top + 8), biome["accent"], 10)


class LumenCluster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 22, y - 50, 44, 50)
        self.hp = 3
        self.flash = 0.0

    def update(self, dt):
        self.flash = max(0.0, self.flash - dt)

    def draw(self, surf, bloom, ox, oy):
        if self.hp <= 0:
            return
        r = self.rect.move(int(ox), int(oy))
        bloom.add_glow(r.centerx, r.centery, 60, (95, 225, 255), 110)
        col = (255, 255, 255) if self.flash > 0 else (75, 195, 235)
        pygame.draw.polygon(surf, col, [(r.left + 6, r.bottom), (r.left + 12, r.top + 14), (r.centerx, r.top), (r.right - 10, r.top + 16), (r.right - 6, r.bottom)])
        pygame.draw.polygon(surf, (235, 252, 255), [(r.centerx - 5, r.bottom), (r.centerx, r.top + 10), (r.centerx + 7, r.bottom)])


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

    def update(self, dt, hero, magnet=False):
        self.life -= dt
        self.spin += dt * 6.0
        dx = hero.rect.centerx - self.x
        dy = hero.rect.centery - self.y
        dist = math.hypot(dx, dy) or 1.0
        pull = 1150.0 if magnet else 165.0
        if dist < pull:
            spd = 840.0 if magnet else 530.0
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

    def draw(self, surf, bloom, ox, oy):
        cx, cy = int(self.x + ox), int(self.y + oy)
        w = max(3, int(abs(math.cos(self.spin)) * 6))
        pts = [(cx, cy - 9), (cx + w, cy), (cx, cy + 9), (cx - w, cy)]
        bloom.add_glow(cx, cy, 24, (110, 235, 255), 110)
        pygame.draw.polygon(surf, (215, 250, 255), pts)
        pygame.draw.polygon(surf, (95, 215, 245), pts, 2)


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

    def draw(self, surf, bloom, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        bloom.add_glow(r.centerx, r.centery, 60, self.color, 130)
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
            self.vx += (dx / dist) * 640.0 * dt
            self.vy += (dy / dist) * 640.0 * dt
            spd = math.hypot(self.vx, self.vy)
            if spd > 470.0:
                self.vx = (self.vx / spd) * 470.0
                self.vy = (self.vy / spd) * 470.0
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

    def draw(self, surf, bloom, ox, oy):
        pos = (int(self.x + ox), int(self.y + oy))
        bloom.add_glow(pos[0], pos[1], self.radius * 3.0, self.color, 145)
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

    def draw(self, surf, bloom, ox, oy):
        if self.timer <= 0:
            return
        p1 = (int(self.x1 + ox), int(self.y1 + oy))
        p2 = (int(self.x2 + ox), int(self.y2 + oy))
        if not self.is_firing:
            pygame.draw.line(surf, self.color, p1, p2, 2)
        else:
            bloom.add_line(p1, p2, self.color, 34)
            pygame.draw.line(surf, self.color, p1, p2, 26)
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
        self.art_type = art_type
        self.hit_ids = set()

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.life -= dt

    def draw(self, surf, bloom, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        bloom.add_glow(r.centerx, r.centery, max(r.width, r.height) * 0.85, (95, 230, 255), 155)
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


class Hero:
    def __init__(self):
        self.rect = pygame.Rect(140, FLOOR_Y - 64, 36, 64)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1

        self.weapon_id = "saber"
        self.base_max_hp = 6
        self.max_hp = 6
        self.hp = 6
        self.max_aether = 100.0
        self.aether = 70.0
        self.base_damage = 16
        self.lumen = 80

        self.max_slots = 4
        self.equipped = ["echo_edge", "mirror_aegis"]
        self.blessings = []  # IDs выбранных даров забега
        self.immortal_used = False
        self.parry_heal_cd = 0.0

        self.resonance = 0.0
        self.combo_count = 0
        self.walk_anim = 0.0

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
        self.slash_max_time = 0.15
        self.slash_cd = 0.0
        self.slash_step = 0
        self.slash_dir = "right"
        self.hit_ids = set()
        self.pending_echo = None

        self.dive_active = False
        self.invuln_timer = 0.0
        self.mend_timer = 0.0
        self.scarf = [[self.rect.centerx, self.rect.top + 26] for _ in range(9)]
        self.trail = RibbonTrail()

    @property
    def weapon(self):
        return WEAPONS[self.weapon_id]

    def has_relic(self, rid):
        return rid in self.equipped

    def has_blessing(self, bid):
        return bid in self.blessings

    def active_synergies(self):
        res = []
        for syn in SYNERGIES:
            if syn["req"][0] in self.equipped and syn["req"][1] in self.equipped:
                res.append(syn["id"])
        return res

    def used_slots(self):
        by_id = {r["id"]: r["slots"] for r in RELICS}
        return sum(by_id.get(rid, 0) for rid in self.equipped)

    def recalculate_stats(self):
        bonus = 2 if self.has_relic("titan_heart") else 0
        bonus += self.blessings.count("b_hp")
        self.max_hp = self.base_max_hp + bonus
        self.hp = min(self.hp, self.max_hp)

    @property
    def resonance_tier(self):
        if self.resonance >= 85:
            return 3
        if self.resonance >= 55:
            return 2
        if self.resonance >= 25:
            return 1
        return 0

    @property
    def blade_damage(self):
        res_bonus = [1.0, 1.15, 1.3, 1.5][self.resonance_tier]
        b_mult = 1.0 + 0.20 * self.blessings.count("b_dmg")
        od_crit = 1.35 if (self.has_relic("crimson_fang") and self.resonance_tier == 3) else 1.0
        return int(round(self.base_damage * self.weapon["dmg_mult"] * res_bonus * b_mult * od_crit))

    @property
    def art_mult(self):
        m = 1.45 if self.has_relic("prism_lens") else 1.0
        m += 0.25 * self.blessings.count("b_art")
        return m

    def add_resonance(self, amount):
        mult = 1.5 if self.has_relic("harmonic_core") else 1.0
        self.resonance = min(100.0, self.resonance + amount * mult * (self.weapon["flow_gain"] / 12.0))

    def reset_air_mobility(self):
        self.jumps_left = 3 if self.has_relic("celestial_wing") else 2
        self.dash_cd = min(self.dash_cd, 0.04)

    def start_dash(self):
        if self.dash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.dash_timer = 0.19
            base_cd = 0.36 if self.has_relic("gale_tempo") else 0.50
            if self.has_blessing("b_speed"):
                base_cd *= 0.82
            self.dash_cd = base_cd
            self.dash_dir = self.facing
            self.dash_hit_ids.clear()
            self.vy = 0.0
            self.mend_timer = 0.0
            if "tempest_dance" in self.active_synergies() and not self.on_ground:
                self.slash_cd = 0.0
            return True
        return False

    def start_parry(self):
        if self.parry_cd <= 0 and self.parry_timer <= 0 and not self.dive_active:
            self.parry_timer = 0.34 if self.has_relic("chrono_thread") else 0.24
            self.parry_cd = 0.60
            self.mend_timer = 0.0
            return True
        return False

    def start_slash(self, keys, projectiles):
        if self.slash_cd <= 0 and self.dash_timer <= 0 and not self.dive_active:
            self.slash_max_time = 0.15
            self.slash_timer = self.slash_max_time
            cd = self.weapon["cd"] * (0.72 if self.has_relic("gale_tempo") else 1.0)
            self.slash_cd = cd
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
                if self.has_relic("echo_edge"):
                    self.pending_echo = (0.11, s_rect.copy(), self.slash_dir)

                if (self.weapon_id == "saber" and self.slash_step == 3) or (self.has_relic("solar_crest") and self.hp == self.max_hp):
                    vx = self.facing * 780.0 if self.slash_dir in ("left", "right") else 0.0
                    vy = -780.0 if self.slash_dir == "up" else (780.0 if self.slash_dir == "down" else 0.0)
                    projectiles.append(Projectile(s_rect.centerx, s_rect.centery, vx, vy, radius=14, color=(255, 215, 110), friendly=True, damage=int(self.blade_damage * 0.85)))
            return True
        return False

    def cast_art(self, keys, arts, sparks):
        cost = 26.0 if self.has_blessing("b_art") else 33.0
        if self.aether < cost or self.dash_timer > 0 or self.dive_active:
            return False
        self.aether -= cost
        self.mend_timer = 0.0
        scale = 1.25 if self.has_relic("prism_lens") else 1.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            rad = int(265 * scale)
            arts.append(AstralArtBlast(self.rect.centerx - rad // 2, self.rect.centery - rad // 2, rad, rad, 0, 0, int(44 * self.art_mult), 0.26, "nova"))
            for _ in range(28):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(180, 480)
                sparks.append(SparkParticle(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, (150, 235, 255), 0.38, 0))
            return True

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not self.on_ground:
            self.dive_active = True
            self.vx = 0.0
            self.vy = 1520.0
            self.invuln_timer = max(self.invuln_timer, 0.7)
            return True

        w, h = int(130 * scale), int(48 * scale)
        sx = self.rect.right if self.facing == 1 else self.rect.left - w
        arts.append(AstralArtBlast(sx, self.rect.centery - h // 2, w, h, self.facing * 1040.0, 0.0, int(36 * self.art_mult), 1.1, "lance"))
        self.vx = -self.facing * 150.0
        return True

    def get_slash_rect(self):
        if self.slash_timer <= 0:
            return None
        reach_mult = 1.22 if self.resonance_tier == 3 else 1.0
        length = int(self.weapon["reach"] * reach_mult)
        broad = int(self.weapon["broad"] * reach_mult)
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

    def update(self, dt, keys, platforms, sparks, rings, arts, shockwaves):
        self.dash_cd = max(0.0, self.dash_cd - dt)
        self.slash_cd = max(0.0, self.slash_cd - dt)
        self.slash_timer = max(0.0, self.slash_timer - dt)
        self.parry_cd = max(0.0, self.parry_cd - dt)
        self.parry_timer = max(0.0, self.parry_timer - dt)
        self.parry_heal_cd = max(0.0, self.parry_heal_cd - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)
        self.drop_through_timer = max(0.0, self.drop_through_timer - dt)

        decay = 4.0 if self.has_relic("harmonic_core") else 6.5
        floor_res = 30.0 if self.has_blessing("b_flow") else 0.0
        self.resonance = max(floor_res, self.resonance - decay * dt)
        if self.resonance == 0:
            self.combo_count = 0

        move_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir += 1

        if move_dir != 0 and self.dash_timer <= 0 and not self.dive_active:
            self.facing = move_dir
            if self.on_ground:
                self.walk_anim += dt * 12.0
        else:
            self.walk_anim = 0.0

        # Обновление ленты меча (Ribbon Trail) во время взмаха
        if self.slash_timer > 0:
            prog = 1.0 - (self.slash_timer / self.slash_max_time)
            ang_span = (-1.1 + prog * 2.2)
            reach = self.weapon["reach"]
            cx, cy = self.rect.center
            if self.slash_dir == "right":
                ang = ang_span
            elif self.slash_dir == "left":
                ang = math.pi - ang_span
            elif self.slash_dir == "up":
                ang = -math.pi / 2 + ang_span
            else:
                ang = math.pi / 2 + ang_span
            tip = (cx + math.cos(ang) * reach, cy + math.sin(ang) * reach)
            base = (cx + math.cos(ang) * 24, cy + math.sin(ang) * 24)
            col = (255, 220, 105) if self.resonance_tier == 3 else self.weapon["color"]
            self.trail.add(tip, base, col)
        self.trail.update(dt)

        # Гармоническое Восстановление (F)
        if keys[pygame.K_f] and self.on_ground and move_dir == 0 and self.dash_timer <= 0 and not self.dive_active and self.hp < self.max_hp and self.aether >= 33.0:
            self.mend_timer += dt
            if random.random() < 0.65:
                sparks.append(SparkParticle(self.rect.centerx + random.uniform(-26, 26), self.rect.bottom - random.uniform(0, 46), random.uniform(-20, 20), random.uniform(-180, -70), (130, 245, 255), 0.35, 0))
            if self.mend_timer >= 0.72:
                self.mend_timer = 0.0
                self.aether -= 33.0
                self.hp = min(self.max_hp, self.hp + 1)
                rings.append(RingWave(self.rect.centerx, self.rect.centery, 95, (140, 245, 255), 0.35, 4))
        else:
            self.mend_timer = 0.0

        # Движение
        if self.dive_active:
            self.vx = 0.0
            self.vy = 1520.0
        elif self.dash_timer > 0:
            self.dash_timer -= dt
            self.vx = self.dash_dir * 1060.0
            self.vy = 0.0
            if random.random() < 0.7:
                sparks.append(SparkParticle(self.rect.centerx, self.rect.centery + random.uniform(-20, 20), -self.dash_dir * random.uniform(120, 280), random.uniform(-40, 40), self.weapon["color"], 0.25, 0))
        else:
            spd_mult = (1.12 if self.resonance_tier >= 2 else 1.0) * (1.18 if self.has_blessing("b_speed") else 1.0)
            target_vx = move_dir * 455.0 * spd_mult
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
                bw, bh = int(330 * scale), int(125 * scale)
                arts.append(AstralArtBlast(self.rect.centerx - bw // 2, FLOOR_Y - bh, bw, bh, 0, 0, dmg, 0.28, "meteor"))
                rings.append(RingWave(self.rect.centerx, FLOOR_Y - 10, 190, (120, 240, 255), 0.38, 6))
                w_spd = 720.0 if ("cataclysm_dive" in self.active_synergies() or self.has_relic("meteor_core")) else 620.0
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, -w_spd, height=62, life=0.75, color=(110, 235, 255), friendly=True, damage=int(28 * self.art_mult)))
                shockwaves.append(Shockwave(self.rect.centerx, FLOOR_Y, w_spd, height=62, life=0.75, color=(110, 235, 255), friendly=True, damage=int(28 * self.art_mult)))

        if landed:
            self.on_ground = True
            self.jumps_left = 3 if self.has_relic("celestial_wing") else 2
        else:
            self.on_ground = False

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Шарф
        self.scarf[0] = [self.rect.centerx - self.facing * 5, self.rect.top + 26]
        for i in range(1, len(self.scarf)):
            px, py = self.scarf[i - 1]
            cx, cy = self.scarf[i]
            tx = px - self.facing * 7
            ty = py + 4 + math.sin(pygame.time.get_ticks() * 0.012 + i) * 1.6
            self.scarf[i][0] += (tx - cx) * min(1.0, 24.0 * dt)
            self.scarf[i][1] += (ty - cy) * min(1.0, 24.0 * dt)

    def draw(self, surf, bloom, sprite_bank, ox, oy):
        self.trail.draw(surf, bloom, ox, oy)
        if self.invuln_timer > 0 and not self.dive_active and int(self.invuln_timer * 22) % 2 == 0:
            return

        r = self.rect.move(int(ox), int(oy))
        w_col = (255, 215, 105) if self.resonance_tier == 3 else self.weapon["color"]
        bloom.add_glow(r.centerx, r.centery, 65 + self.resonance_tier * 12, w_col, 110 + self.resonance_tier * 20)

        # Развевающийся шёлковый шарф
        pts = [(int(p[0] + ox), int(p[1] + oy)) for p in self.scarf]
        for i in range(len(pts) - 1):
            w = max(3, 13 - i)
            col = (255, 200, 95) if (self.resonance_tier == 3 and i > 4) else (55, 175, 220)
            pygame.draw.line(surf, col, pts[i], pts[i + 1], w)

        # Спрайт героя
        frame_idx = int(self.walk_anim) % 4 if self.on_ground else 1
        spr = sprite_bank.hero_frames[frame_idx]
        if self.facing == -1:
            spr = pygame.transform.flip(spr, True, False)
        surf.blit(spr, (r.centerx - spr.get_width() // 2, r.bottom - spr.get_height()))

        # Оружие в руке героя
        hx = r.centerx + self.facing * 12
        hy = r.centery + 4
        if self.weapon_id == "saber":
            tip = (hx + self.facing * 32, hy - 22)
            pygame.draw.line(surf, (230, 245, 255), (hx, hy), tip, 4)
            pygame.draw.line(surf, w_col, (hx, hy), tip, 2)
        elif self.weapon_id == "daggers":
            pygame.draw.line(surf, w_col, (hx, hy), (hx + self.facing * 22, hy - 12), 3)
            pygame.draw.line(surf, (255, 255, 255), (hx - self.facing * 8, hy + 4), (hx + self.facing * 14, hy + 12), 3)
        elif self.weapon_id == "greatsword":
            tip = (hx - self.facing * 18, hy - 44)
            pygame.draw.line(surf, (255, 235, 180), (hx, hy), tip, 7)
            pygame.draw.line(surf, w_col, (hx, hy), tip, 3)

        # Щит Парирования
        if self.parry_timer > 0:
            bloom.add_glow(r.centerx, r.centery, 85, (255, 235, 140), 180)
            pygame.draw.circle(surf, (255, 245, 180), r.center, 46, 4)
            pygame.draw.circle(surf, (130, 235, 255), r.center, 38, 2)


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

        cfg = {
            "sentinel": (42, 58, 38, 12),
            "prism_drone": (44, 44, 34, 15),
            "aegis_warden": (54, 80, 65, 22),
            "nova_orb": (38, 38, 26, 14),
            "rift_assassin": (42, 62, 44, 18),
        }[kind]
        self.w, self.h, base_hp, self.lumen = cfg
        self.max_hp = int(base_hp * scale)
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

    def draw(self, surf, bloom, sprite_bank, ox, oy):
        r = self.rect.move(int(ox), int(oy))
        spr = sprite_bank.enemy_sprites[self.kind]
        if self.facing == -1:
            spr = pygame.transform.flip(spr, True, False)
        surf.blit(spr, (r.centerx - spr.get_width() // 2, r.bottom - spr.get_height()))
        if self.flash > 0:
            pygame.draw.rect(surf, (255, 255, 255), r, 3, border_radius=8)
        if self.kind in ("prism_drone", "nova_orb"):
            bloom.add_glow(r.centerx, r.centery, 42, (255, 115, 145), 110)


class Boss:
    def __init__(self, depth, boss_def):
        self.depth = depth
        self.kind, base_name, self.primary, self.glow, self.lore = boss_def
        tier = (depth - 1) // 6
        self.name = f"{base_name}{' [ВОЗНЕСЕНИЕ ' + str(tier) + ']' if tier > 0 else ''}"

        w, h = (102, 138) if self.kind == "colossus" else ((94, 128) if self.kind == "solaris" else (82, 126))
        start_y = 200 if self.kind == "solaris" else (FLOOR_Y - h)
        self.rect = pygame.Rect(910, start_y, w, h)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = -1

        self.max_hp = int(300 + (depth - 1) * 125)
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

    def update(self, dt, hero, projectiles, shockwaves, lasers, sparks):
        self.flash = max(0.0, self.flash - dt)
        self.timer -= dt
        spd_mult = (1.24 if self.phase2 else 1.0) + min(0.35, (self.depth - 1) * 0.04)

        if self.clone_timer > 0:
            self.clone_timer -= dt
            if self.clone_timer <= 0:
                self.clone_rect = None

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

        elif self.kind in ("seraph", "valkyrie"):
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
                if self.kind == "valkyrie":
                    for sx in range(160, WIDTH - 140, 210):
                        lasers.append(LaserBeam(sx, 20, math.pi / 2 + random.uniform(-0.15, 0.15), warn_time=0.65 / spd_mult, color=self.glow))
                else:
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
                            sparks.append(SparkParticle(self.rect.centerx, self.rect.centery, random.uniform(-240, 240), random.uniform(-240, 240), self.glow, 0.4, 0))
                        self.x = float(random.choice([140, 590, 1020]))
                        self.state = "idle"
                        self.timer = 0.48 / spd_mult
            elif self.state == "laser_aim" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.85 / spd_mult
            elif self.state == "stagger" and self.timer <= 0:
                self.state = "idle"
                self.timer = 0.4

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

    def draw(self, surf, bloom, sprite_bank, ox, oy):
        t = pygame.time.get_ticks() * 0.003
        if self.clone_rect:
            cr = self.clone_rect.move(int(ox), int(oy))
            bloom.add_glow(cr.centerx, cr.centery, 85, self.glow, 120)
            pygame.draw.polygon(surf, (45, 25, 75), [(cr.centerx, cr.top), (cr.right, cr.centery), (cr.centerx, cr.bottom), (cr.left, cr.centery)])
            pygame.draw.polygon(surf, self.glow, [(cr.centerx, cr.top), (cr.right, cr.centery), (cr.centerx, cr.bottom), (cr.left, cr.centery)], 3)

        r = self.rect.move(int(ox), int(oy))
        bloom.add_glow(r.centerx, r.centery, 125 if self.phase2 else 95, self.primary, 130)

        # Вращающийся астрономический нимб за спиной босса
        ring_r = 74 if self.phase2 else 58
        pygame.draw.circle(surf, self.glow, r.center, ring_r, 2)
        for i in range(4):
            ang = t * (1.6 if self.phase2 else 0.9) + i * (math.pi / 2)
            ox_r = r.centerx + int(math.cos(ang) * ring_r)
            oy_r = r.centery + int(math.sin(ang) * ring_r)
            pygame.draw.circle(surf, self.glow, (ox_r, oy_r), 5)

        if self.kind in ("seraph", "valkyrie", "solaris"):
            flap = math.sin(t * 2.2) * 14
            for side in (-1, 1):
                wx = r.right if side == 1 else r.left
                pygame.draw.polygon(surf, self.primary, [(wx, r.centery - 10), (wx + side * 72, r.top - 22 + flap), (wx + side * 46, r.centery + 10)])
                pygame.draw.polygon(surf, self.glow, [(wx, r.centery + 6), (wx + side * 56, r.centery + 24 - flap), (wx + side * 26, r.bottom)])

        spr = sprite_bank.boss_sprites[self.kind]
        if self.facing == 1:
            spr = pygame.transform.flip(spr, True, False)
        if self.state == "stagger":
            spr = pygame.transform.scale(spr, (spr.get_width(), int(spr.get_height() * 0.78)))
        surf.blit(spr, (r.centerx - spr.get_width() // 2, r.bottom - spr.get_height()))

        if self.flash > 0:
            pygame.draw.rect(surf, (255, 255, 255), r, 4, border_radius=12)

        if self.state in ("charge_prep", "lunge_prep", "dash_prep"):
            pygame.draw.line(surf, self.glow, (r.centerx, r.centery), (r.centerx + self.facing * 560, r.centery), 3)
            bloom.add_line((r.centerx, r.centery), (r.centerx + self.facing * 560, r.centery), self.glow, 10)
