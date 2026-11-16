import math
import os
import random
import wave
import numpy as np
import pygame
from data import BIOMES, BOSS_DEFS


def _save_wav(path, left, right, sr=44100):
    left = np.clip(left, -1.0, 1.0)
    right = np.clip(right, -1.0, 1.0)
    stereo = np.column_stack((left, right))
    pcm = (stereo * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def generate_sfx(sfx_dir):
    os.makedirs(sfx_dir, exist_ok=True)
    sr = 44100
    rng = np.random.default_rng(42)

    def t_arr(dur):
        return np.linspace(0, dur, int(sr * dur), endpoint=False)

    # 1. Взмахи 3 видов оружия
    t = t_arr(0.16)
    noise = rng.normal(0, 1, len(t))
    env = np.exp(-t * 24.0) * np.sin(np.minimum(1.0, t / 0.02) * math.pi * 0.5)
    sweep = np.sin(2 * math.pi * (950 * np.exp(-t * 14.0) + 180) * t)
    sig = (noise * 0.45 + sweep * 0.4) * env
    _save_wav(os.path.join(sfx_dir, "slash_saber.wav"), sig * 0.9, sig * 1.0)

    t = t_arr(0.10)
    noise = rng.normal(0, 1, len(t))
    env = np.exp(-t * 36.0)
    sweep = np.sin(2 * math.pi * (1650 * np.exp(-t * 20.0) + 320) * t)
    sig = (noise * 0.5 + sweep * 0.35) * env
    _save_wav(os.path.join(sfx_dir, "slash_daggers.wav"), sig * 1.0, sig * 0.85)

    t = t_arr(0.28)
    noise = rng.normal(0, 1, len(t))
    env = np.exp(-t * 13.0) * np.sin(np.minimum(1.0, t / 0.035) * math.pi * 0.5)
    sweep = np.sin(2 * math.pi * (440 * np.exp(-t * 10.0) + 85) * t)
    sig = (noise * 0.4 + sweep * 0.65) * env
    _save_wav(os.path.join(sfx_dir, "slash_greatsword.wav"), sig, sig)

    # 2. Эхо-клинок
    t = t_arr(0.18)
    sig = np.sin(2 * math.pi * (1200 - 500 * t / 0.18) * t) * np.exp(-t * 20.0) * 0.6
    _save_wav(os.path.join(sfx_dir, "echo_slash.wav"), sig * 0.7, sig)

    # 3. Попадания, крит, щит, смерть врага
    t = t_arr(0.14)
    hit = (np.sin(2 * math.pi * (280 * np.exp(-t * 22.0) + 65) * t) * 0.7 + rng.normal(0, 0.35, len(t))) * np.exp(-t * 28.0)
    _save_wav(os.path.join(sfx_dir, "hit_enemy.wav"), hit, hit)

    t = t_arr(0.24)
    crit = (np.sin(2 * math.pi * 880 * t) * 0.4 + np.sin(2 * math.pi * 1320 * t) * 0.4 + rng.normal(0, 0.3, len(t))) * np.exp(-t * 18.0)
    _save_wav(os.path.join(sfx_dir, "hit_crit.wav"), crit * 1.0, crit * 0.9)

    t = t_arr(0.22)
    clang = (np.sin(2 * math.pi * 1480 * t) * 0.5 + np.sin(2 * math.pi * 2210 * t) * 0.4 + np.sin(2 * math.pi * 3190 * t) * 0.25) * np.exp(-t * 19.0)
    _save_wav(os.path.join(sfx_dir, "hit_shield.wav"), clang, clang * 0.85)

    t = t_arr(0.32)
    die = (rng.normal(0, 0.5, len(t)) + np.sin(2 * math.pi * (240 * np.exp(-t * 9.0) + 45) * t) * 0.7) * np.exp(-t * 12.0)
    _save_wav(os.path.join(sfx_dir, "enemy_die.wav"), die, die)

    # 4. Передвижение: прыжок, двойной прыжок, приземление, пого, рывок
    t = t_arr(0.16)
    jmp = np.sin(2 * math.pi * (220 + 520 * (t / 0.16)) * t) * np.exp(-t * 18.0) * 0.65
    _save_wav(os.path.join(sfx_dir, "jump.wav"), jmp, jmp)

    t = t_arr(0.20)
    djmp = (np.sin(2 * math.pi * (420 + 780 * (t / 0.20)) * t) + 0.5 * np.sin(2 * math.pi * 840 * t)) * np.exp(-t * 16.0) * 0.55
    _save_wav(os.path.join(sfx_dir, "double_jump.wav"), djmp * 0.85, djmp)

    t = t_arr(0.11)
    land = (np.sin(2 * math.pi * (120 * np.exp(-t * 25.0) + 38) * t) * 0.8 + rng.normal(0, 0.2, len(t))) * np.exp(-t * 32.0)
    _save_wav(os.path.join(sfx_dir, "land.wav"), land, land)

    t = t_arr(0.18)
    pogo = np.sin(2 * math.pi * (520 + 680 * (t / 0.18)) * t) * np.exp(-t * 18.0) * 0.75
    _save_wav(os.path.join(sfx_dir, "pogo_bounce.wav"), pogo, pogo)

    t = t_arr(0.20)
    dash = (rng.normal(0, 0.55, len(t)) * np.sin(np.minimum(1.0, t / 0.03) * math.pi * 0.5) + np.sin(2 * math.pi * (620 * np.exp(-t * 15.0) + 120) * t) * 0.45) * np.exp(-t * 16.0)
    _save_wav(os.path.join(sfx_dir, "dash.wav"), dash * 0.8, dash)

    # 5. Парирование
    t = t_arr(0.18)
    pact = np.sin(2 * math.pi * (740 + 420 * t) * t) * np.exp(-t * 20.0) * 0.6
    _save_wav(os.path.join(sfx_dir, "parry_activate.wav"), pact, pact)

    t = t_arr(0.45)
    psuc = (
        np.sin(2 * math.pi * 1046.5 * t) * 0.45
        + np.sin(2 * math.pi * 1567.98 * t) * 0.4
        + np.sin(2 * math.pi * 2093.0 * t) * 0.35
        + np.sin(2 * math.pi * 90 * t) * 0.4
    ) * np.exp(-t * 8.5)
    _save_wav(os.path.join(sfx_dir, "parry_success.wav"), psuc, psuc * 0.92)

    # 6. Астральные искусства
    t = t_arr(0.32)
    lance = (np.sin(2 * math.pi * (980 * np.exp(-t * 8.0) + 260) * t) * 0.6 + rng.normal(0, 0.25, len(t))) * np.exp(-t * 12.0)
    _save_wav(os.path.join(sfx_dir, "art_lance.wav"), lance, lance * 0.85)

    t = t_arr(0.42)
    nova = (np.sin(2 * math.pi * (320 + 640 * t) * t) * 0.5 + np.sin(2 * math.pi * 640 * t) * 0.4 + rng.normal(0, 0.25, len(t))) * np.exp(-t * 9.5)
    _save_wav(os.path.join(sfx_dir, "art_nova.wav"), nova * 0.9, nova)

    t = t_arr(0.25)
    mdive = np.sin(2 * math.pi * (680 * np.exp(-t * 10.0) + 140) * t) * np.exp(-t * 12.0) * 0.75
    _save_wav(os.path.join(sfx_dir, "art_meteor_dive.wav"), mdive, mdive)

    t = t_arr(0.55)
    mimp = (np.sin(2 * math.pi * (145 * np.exp(-t * 9.0) + 34) * t) * 0.85 + rng.normal(0, 0.45, len(t))) * np.exp(-t * 7.5)
    _save_wav(os.path.join(sfx_dir, "art_meteor_impact.wav"), mimp, mimp)

    # 7. Лечение, Overdrive, Люмен, Урон игрока
    t = t_arr(0.14)
    htick = np.sin(2 * math.pi * 880 * t) * np.exp(-t * 22.0) * 0.4
    _save_wav(os.path.join(sfx_dir, "heal_tick.wav"), htick, htick)

    t = t_arr(0.42)
    hcomp = (np.sin(2 * math.pi * 523.25 * t) + np.sin(2 * math.pi * 659.25 * t) + np.sin(2 * math.pi * 1046.5 * t)) * 0.32 * np.exp(-t * 8.0)
    _save_wav(os.path.join(sfx_dir, "heal_complete.wav"), hcomp, hcomp * 0.95)

    t = t_arr(0.55)
    od = (np.sin(2 * math.pi * (110 + 330 * t) * t) * 0.5 + np.sin(2 * math.pi * 440 * t) * 0.35 + np.sin(2 * math.pi * 660 * t) * 0.3) * np.exp(-t * 6.5)
    _save_wav(os.path.join(sfx_dir, "overdrive.wav"), od * 0.9, od)

    t = t_arr(0.12)
    lum = (np.sin(2 * math.pi * 1568 * t) * 0.5 + np.sin(2 * math.pi * 2349 * t) * 0.35) * np.exp(-t * 26.0)
    _save_wav(os.path.join(sfx_dir, "lumen_pickup.wav"), lum, lum * 0.85)

    t = t_arr(0.34)
    hurt = (np.sin(2 * math.pi * (190 * np.exp(-t * 8.0) + 48) * t) * 0.8 + rng.normal(0, 0.4, len(t))) * np.exp(-t * 11.0)
    _save_wav(os.path.join(sfx_dir, "player_hurt.wav"), hurt, hurt)

    # 8. Боссы и интерфейс
    t = t_arr(0.75)
    roar = (np.sin(2 * math.pi * (135 * np.exp(-t * 2.5) + 42) * t) * 0.75 + rng.normal(0, 0.35, len(t))) * np.exp(-t * 4.2)
    _save_wav(os.path.join(sfx_dir, "boss_roar.wav"), roar, roar)

    t = t_arr(0.45)
    bslam = (np.sin(2 * math.pi * (125 * np.exp(-t * 11.0) + 32) * t) * 0.9 + rng.normal(0, 0.45, len(t))) * np.exp(-t * 8.5)
    _save_wav(os.path.join(sfx_dir, "boss_slam.wav"), bslam, bslam)

    t = t_arr(0.40)
    blaser = (np.sin(2 * math.pi * (1350 - 700 * t) * t) * 0.45 + rng.normal(0, 0.35, len(t))) * np.exp(-t * 9.0)
    _save_wav(os.path.join(sfx_dir, "boss_laser.wav"), blaser, blaser * 0.9)

    t = t_arr(0.95)
    bdef = (
        np.sin(2 * math.pi * (160 * np.exp(-t * 4.0) + 36) * t) * 0.7
        + np.sin(2 * math.pi * 523.25 * t) * 0.3
        + np.sin(2 * math.pi * 783.99 * t) * 0.3
        + rng.normal(0, 0.35, len(t))
    ) * np.exp(-t * 3.8)
    _save_wav(os.path.join(sfx_dir, "boss_defeat.wav"), bdef, bdef)

    t = t_arr(0.28)
    door = np.sin(2 * math.pi * (330 + 330 * (t / 0.28)) * t) * np.exp(-t * 11.0) * 0.55
    _save_wav(os.path.join(sfx_dir, "door_open.wav"), door, door)

    t = t_arr(0.07)
    uim = np.sin(2 * math.pi * 920 * t) * np.exp(-t * 45.0) * 0.45
    _save_wav(os.path.join(sfx_dir, "ui_move.wav"), uim, uim)

    t = t_arr(0.15)
    uis = (np.sin(2 * math.pi * 660 * t) + np.sin(2 * math.pi * 990 * t)) * 0.35 * np.exp(-t * 18.0)
    _save_wav(os.path.join(sfx_dir, "ui_select.wav"), uis, uis)

    t = t_arr(0.16)
    wsw = (np.sin(2 * math.pi * 1180 * t) * 0.45 + np.sin(2 * math.pi * 1760 * t) * 0.35) * np.exp(-t * 22.0)
    _save_wav(os.path.join(sfx_dir, "weapon_switch.wav"), wsw, wsw)


def _create_gradient_2k(w, h, c1, c2, accent):
    """Векторный рендер 2K неба с туманностями и звёздной пылью (~14.7 МБ на слой)."""
    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    x = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    r = c1[0] + (c2[0] - c1[0]) * y
    g = c1[1] + (c2[1] - c1[1]) * y
    b = c1[2] + (c2[2] - c1[2]) * y

    # Мягкое астральное свечение туманности
    nebula = np.exp(-((x - 0.5) ** 2 / 0.09 + (y - 0.38) ** 2 / 0.08))
    wave = 0.5 + 0.5 * np.sin(x * 11.0 + np.cos(y * 7.0) * 2.5)
    glow = nebula * wave * 0.45

    r = np.clip(r + accent[0] * glow, 0, 255).astype(np.uint8)
    g = np.clip(g + accent[1] * glow, 0, 255).astype(np.uint8)
    b = np.clip(b + accent[2] * glow, 0, 255).astype(np.uint8)
    a = np.full((h, w), 255, dtype=np.uint8)

    rgba = np.dstack((r, g, b, a))
    return pygame.image.frombuffer(rgba.tobytes(), (w, h), "RGBA").convert_alpha()


def generate_biomes_2k(bg_dir):
    os.makedirs(bg_dir, exist_ok=True)
    w, h = 2560, 1440
    rng = random.Random(108)

    for biome in BIOMES:
        bid = biome["id"]

        # 1. Sky 2K
        sky = _create_gradient_2k(w, h, biome["sky_top"], biome["sky_bot"], biome["accent"])
        for _ in range(340):
            sx, sy = rng.randint(0, w - 1), rng.randint(0, int(h * 0.78))
            sr = rng.choice([1, 1, 2, 3])
            pygame.draw.circle(sky, (235, 245, 255, rng.randint(90, 230)), (sx, sy), sr)
        pygame.image.save(sky, os.path.join(bg_dir, f"{bid}_sky.tga"))

        # 2. Far Parallax 2K (горные шпили, астролябия, древние руины)
        far = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, 430
        pygame.draw.circle(far, (*biome["stone_rim"], 130), (cx, cy), 280, 4)
        pygame.draw.circle(far, (*biome["accent"], 95), (cx, cy), 210, 2)
        for i in range(12):
            ang = i * (math.tau / 12)
            px = cx + int(math.cos(ang) * 280)
            py = cy + int(math.sin(ang) * 280)
            pygame.draw.circle(far, (*biome["accent"], 190), (px, py), 7)

        for i in range(-1, 13):
            bx = i * 240
            peak_y = 540 + (i % 4) * 85
            pts = [(bx, h), (bx + 95, peak_y), (bx + 165, peak_y + 75), (bx + 260, h)]
            pygame.draw.polygon(far, (*biome["stone_dark"], 235), pts)
            pygame.draw.line(far, (*biome["stone_rim"], 120), (bx + 95, peak_y), (bx + 165, peak_y + 75), 2)
        pygame.image.save(far, os.path.join(bg_dir, f"{bid}_far.tga"))

        # 3. Mid Parallax 2K (готические арки и витражные розы)
        mid = pygame.Surface((w, h), pygame.SRCALPHA)
        for px in range(180, w, 460):
            pygame.draw.rect(mid, (*biome["stone_dark"], 245), (px - 48, 0, 96, h))
            pygame.draw.line(mid, (*biome["stone_rim"], 170), (px - 48, 0), (px - 48, h), 3)
            pygame.draw.line(mid, (*biome["stone_rim"], 110), (px + 48, 0), (px + 48, h), 2)
            # Капитель и арка
            pygame.draw.polygon(mid, (*biome["stone_mid"], 245), [(px - 68, 180), (px + 68, 180), (px + 48, 240), (px - 48, 240)])
            wx = px + 230
            if wx < w - 120:
                pygame.draw.circle(mid, (*biome["stone_rim"], 140), (wx, 340), 74, 4)
                pygame.draw.circle(mid, (*biome["accent_2"], 110), (wx, 340), 42, 2)
                for k in range(8):
                    a = k * (math.pi / 4)
                    pygame.draw.line(mid, (*biome["accent"], 90), (wx, 340), (wx + int(math.cos(a) * 70), 340 + int(math.sin(a) * 70)), 2)
        pygame.image.save(mid, os.path.join(bg_dir, f"{bid}_mid.tga"))

        # 4. Volumetric Light Rays & Mist 2K
        mist = pygame.Surface((w, h), pygame.SRCALPHA)
        for idx, rx in enumerate((380, 920, 1520, 2080)):
            pts = [(rx - 70, 0), (rx + 110, 0), (rx + 420, h), (rx + 90, h)]
            pygame.draw.polygon(mist, (*biome["ray_col"], 22), pts)
        pygame.image.save(mist, os.path.join(bg_dir, f"{bid}_mist.tga"))

        # 5. Carved Runic Floor Tile 1024x1024
        fw = 1024
        fl = pygame.Surface((fw, fw), pygame.SRCALPHA)
        fl.fill((*biome["stone_dark"], 255))
        for ty in range(0, fw, 128):
            for tx in range(0, fw, 256):
                off = 128 if (ty // 128) % 2 == 1 else 0
                rx = (tx + off) % fw
                pygame.draw.rect(fl, (*biome["stone_mid"], 255), (rx + 4, ty + 4, 248, 120), border_radius=10)
                pygame.draw.rect(fl, (*biome["stone_rim"], 135), (rx + 4, ty + 4, 248, 120), 2, border_radius=10)
                # Светящаяся руна внутри плиты
                cx_r, cy_r = rx + 128, ty + 64
                pygame.draw.polygon(fl, (*biome["accent"], 95), [(cx_r, cy_r - 18), (cx_r + 14, cy_r), (cx_r, cy_r + 18), (cx_r - 14, cy_r)], 2)
        pygame.image.save(fl, os.path.join(bg_dir, f"{bid}_floor.tga"))


def generate_hd_sprites(spr_dir):
    os.makedirs(spr_dir, exist_ok=True)

    # 1. Герой: 8 кадров 512x512 (~8 МБ)
    for f in range(8):
        sz = 512
        s = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = sz // 2
        phase = (f / 8.0) * math.tau
        bob = int(math.sin(phase * 2.0) * 10)
        leg_a = int(math.sin(phase) * 46)

        # Ноги и поножи
        pygame.draw.line(s, (22, 30, 52), (cx - 26, 330 + bob), (cx - 34 - leg_a, 488), 34)
        pygame.draw.line(s, (34, 46, 76), (cx + 26, 330 + bob), (cx + 34 + leg_a, 488), 34)
        pygame.draw.circle(s, (105, 235, 255), (cx + 34 + leg_a, 475), 10)

        # Плащ и кираса
        torso = [(cx, 175 + bob), (cx + 96, 245 + bob), (cx + 72, 395 + bob), (cx - 72, 395 + bob), (cx - 96, 245 + bob)]
        pygame.draw.polygon(s, (20, 28, 48), torso)
        pygame.draw.polygon(s, (85, 215, 250), torso, 8)
        pygame.draw.polygon(s, (165, 248, 255), [(cx, 235 + bob), (cx + 26, 285 + bob), (cx, 335 + bob), (cx - 26, 285 + bob)])

        # Наплечники
        for side in (-1, 1):
            sh = [(cx + side * 112, 215 + bob), (cx + side * 46, 182 + bob), (cx + side * 82, 275 + bob)]
            pygame.draw.polygon(s, (44, 60, 94), sh)
            pygame.draw.polygon(s, (145, 240, 255), sh, 5)

        # Шлем и астральные рога
        helm = [(cx, 44 + bob), (cx + 82, 114 + bob), (cx + 64, 198 + bob), (cx - 64, 198 + bob), (cx - 82, 114 + bob)]
        pygame.draw.polygon(s, (234, 244, 255), helm)
        pygame.draw.polygon(s, (115, 175, 225), helm, 7)
        pygame.draw.polygon(s, (245, 250, 255), [(cx - 56, 94 + bob), (cx - 104, 12 + bob), (cx - 32, 66 + bob)])
        pygame.draw.polygon(s, (245, 250, 255), [(cx + 56, 94 + bob), (cx + 104, 12 + bob), (cx + 32, 66 + bob)])

        # Светящийся визор
        pygame.draw.polygon(s, (12, 16, 28), [(cx - 44, 122 + bob), (cx + 58, 122 + bob), (cx + 42, 162 + bob), (cx - 32, 162 + bob)])
        pygame.draw.line(s, (115, 245, 255), (cx - 34, 142 + bob), (cx + 46, 142 + bob), 14)
        pygame.image.save(s, os.path.join(spr_dir, f"hero_{f}.tga"))

    # 2. 5 типов врагов: по 2 кадра 512x512 (~10 МБ)
    enemy_kinds = ["sentinel", "prism_drone", "aegis_warden", "nova_orb", "rift_assassin"]
    for ek in enemy_kinds:
        for f in range(2):
            sz = 512
            s = pygame.Surface((sz, sz), pygame.SRCALPHA)
            cx = sz // 2
            pulse = 14 if f == 1 else 0

            if ek == "sentinel":
                pts = [(cx, 36 - pulse), (430, 190), (380, 488), (132, 488), (82, 190)]
                pygame.draw.polygon(s, (30, 38, 62), pts)
                pygame.draw.polygon(s, (115, 155, 210), pts, 10)
                pygame.draw.polygon(s, (255, 95, 125), [(cx - 20, 175), (cx + 95, 175), (cx + 68, 220), (cx - 20, 220)])
            elif ek == "prism_drone":
                pts = [(cx, 24 - pulse), (488 + pulse, cx), (cx, 488 + pulse), (24 - pulse, cx)]
                pygame.draw.polygon(s, (145, 45, 85), pts)
                pygame.draw.polygon(s, (255, 145, 175), pts, 12)
                pygame.draw.circle(s, (255, 235, 165), (cx, cx), 68 + pulse)
            elif ek == "aegis_warden":
                pts = [(cx - 20, 40), (380, 150), (355, 490), (95, 490), (80, 150)]
                pygame.draw.polygon(s, (28, 36, 58), pts)
                pygame.draw.polygon(s, (95, 165, 215), pts, 10)
                shield = [(340, 80 - pulse), (475, 135), (460, 475), (340, 502)]
                pygame.draw.polygon(s, (55, 125, 175), shield)
                pygame.draw.polygon(s, (185, 242, 255), shield, 10)
                pygame.draw.circle(s, (255, 120, 140), (265, 165), 26)
            elif ek == "nova_orb":
                pygame.draw.circle(s, (195, 95, 45), (cx, cx), 175 + pulse)
                pygame.draw.circle(s, (255, 195, 110), (cx, cx), 175 + pulse, 12)
                pygame.draw.circle(s, (255, 245, 190), (cx, cx), 68)
            elif ek == "rift_assassin":
                pts = [(cx, 28 - pulse), (450, 490), (cx, 410), (62, 490)]
                pygame.draw.polygon(s, (54, 28, 88), pts)
                pygame.draw.polygon(s, (195, 115, 255), pts, 10)
                pygame.draw.line(s, (235, 165, 255), (cx - 45, 185), (cx + 85, 185), 18)

            pygame.image.save(s, os.path.join(spr_dir, f"enemy_{ek}_{f}.tga"))

    # 3. 6 Боссов: по 4 кадра 1024x1024 (24 * 4 МБ = 96 МБ)
    for bkind, _, prim, glow, _ in BOSS_DEFS:
        for f in range(4):
            sz = 1024
            s = pygame.Surface((sz, sz), pygame.SRCALPHA)
            cx = sz // 2
            breath = int(math.sin((f / 4.0) * math.tau) * 18)

            body = [(cx, 140 + breath), (sz - 95, 360 + breath), (sz - 145, sz - 24), (145, sz - 24), (95, 360 + breath)]
            pygame.draw.polygon(s, (22, 20, 36), body)
            pygame.draw.polygon(s, prim, body, 18)

            chest = [(cx, 275 + breath), (sz - 205, 420 + breath), (cx, 690 + breath), (205, 420 + breath)]
            pygame.draw.polygon(s, (36, 32, 58), chest)
            pygame.draw.polygon(s, glow, chest, 12)
            pygame.draw.circle(s, glow, (cx, 480 + breath), 76 + breath // 2)
            pygame.draw.circle(s, (255, 255, 255), (cx, 480 + breath), 36)

            crown = [
                (cx - 190, 260 + breath),
                (cx - 140, 26 + breath),
                (cx - 45, 165 + breath),
                (cx, 12 + breath),
                (cx + 45, 165 + breath),
                (cx + 140, 26 + breath),
                (cx + 190, 260 + breath),
            ]
            pygame.draw.polygon(s, (235, 240, 255), crown)
            pygame.draw.polygon(s, prim, crown, 12)
            pygame.draw.line(s, glow, (cx - 110, 215 + breath), (cx + 110, 215 + breath), 28)

            pygame.image.save(s, os.path.join(spr_dir, f"boss_{bkind}_{f}.tga"))


def build_all(base_dir="assets"):
    pygame.init()
    os.makedirs(base_dir, exist_ok=True)
    generate_sfx(os.path.join(base_dir, "sfx"))
    generate_biomes_2k(os.path.join(base_dir, "bg"))
    generate_hd_sprites(os.path.join(base_dir, "sprites"))
    with open(os.path.join(base_dir, "manifest.ok"), "w", encoding="utf-8") as f:
        f.write("ASTRAL KNIGHT HD ASSETS READY\n")


if __name__ == "__main__":
    build_all()
