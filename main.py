import math
import random
import sys
import pygame
from data import WIDTH, HEIGHT, FPS, FLOOR_Y, BIOMES, WEAPONS, RELICS, SYNERGIES, BLESSINGS, BOSS_DEFS
from gfx import get_font, BloomRenderer, SpriteBank, SparkParticle, RingWave, WeatherParticle, FloatingText, build_sky_surface, draw_world_backdrop, draw_reflective_floor
from entities import Platform, CrystalHazard, LumenCluster, LumenCrystal, Shockwave, Projectile, LaserBeam, AstralArtBlast, Hero, Enemy, Boss


def build_room(depth, room_idx):
    platforms, hazards, clusters, enemies = [], [], [], []
    altar_rect = None

    if room_idx == 0:
        altar_rect = pygame.Rect(605, FLOOR_Y - 134, 70, 134)
        platforms = [Platform(210, 445, 210), Platform(860, 445, 210)]
        return "sanctuary", platforms, hazards, clusters, enemies, altar_rect

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
            ey = 210 if kind in ("prism_drone", "nova_orb") else (FLOOR_Y - 82)
            enemies.append(Enemy(kind, min(WIDTH - 130, ex), ey, depth))
        return "combat", platforms, hazards, clusters, enemies, None

    boss_def = BOSS_DEFS[(depth - 1) % len(BOSS_DEFS)]
    if boss_def[0] == "solaris":
        platforms = [Platform(160, 465, 210), Platform(535, 410, 210), Platform(910, 465, 210), Platform(340, 300, 180), Platform(760, 300, 180)]
    else:
        platforms = [Platform(200, 450, 190), Platform(890, 450, 190)]
    return "boss", platforms, hazards, clusters, enemies, None


def draw_hud(surf, hero, boss, depth, room_idx, biome):
    f_title = get_font(21, bold=True)
    f_small = get_font(16)
    f_tiny = get_font(14)

    # Сфера Эфира
    sc = (56, 54)
    pygame.draw.circle(surf, (16, 22, 38), sc, 33)
    ratio = hero.aether / hero.max_aether
    if ratio > 0:
        pygame.draw.circle(surf, (95, 235, 255), sc, int(29 * math.sqrt(ratio)))
        pygame.draw.circle(surf, (235, 252, 255), sc, int(16 * math.sqrt(ratio)))
    pygame.draw.circle(surf, (175, 215, 245), sc, 33, 3)

    # Ячейки прочности (Ромбы HP)
    for i in range(hero.max_hp):
        mx = 114 + i * 31
        my = 36
        pts = [(mx, my - 13), (mx + 11, my), (mx, my + 13), (mx - 11, my)]
        if i < hero.hp:
            col = (255, 215, 115) if i >= hero.base_max_hp else (115, 235, 255)
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (255, 255, 255), pts, 2)
        else:
            pygame.draw.polygon(surf, (45, 56, 82), pts, 2)

    # Люмен + Поток + Оружие
    pygame.draw.polygon(surf, (215, 250, 255), [(114, 68), (121, 76), (114, 84), (107, 76)])
    surf.blit(f_title.render(f"{hero.lumen}", True, (240, 248, 255)), (130, 63))

    tier_names = ["ПОТОК x1.0", "ПОТОК x1.15", "ПОТОК x1.3", "OVERDRIVE x1.5"]
    tier_cols = [(145, 165, 195), (105, 235, 255), (185, 140, 255), (255, 215, 105)]
    t_idx = hero.resonance_tier
    rx, ry, rw = 215, 71, 150
    pygame.draw.rect(surf, (22, 28, 44), (rx, ry, rw, 10), border_radius=5)
    pygame.draw.rect(surf, tier_cols[t_idx], (rx, ry, int(rw * (hero.resonance / 100.0)), 10), border_radius=5)
    surf.blit(f_small.render(f"{tier_names[t_idx]} ({hero.combo_count})", True, tier_cols[t_idx]), (rx + rw + 10, 65))

    # Активное оружие
    w_txt = f_small.render(f"[{hero.weapon['key']}] {hero.weapon['name']}", True, hero.weapon["color"])
    surf.blit(w_txt, (560, 65))

    stage_names = ["Святилище", "Зал I", "Зал II", "Чертог Босса"]
    loc_txt = f_small.render(f"Этаж {depth}: {biome['name']}  |  {stage_names[room_idx]}", True, (205, 222, 248))
    surf.blit(loc_txt, (WIDTH - loc_txt.get_width() - 26, 22))

    ctrl_txt = f_tiny.render("1/2/3: Оружие  |  ЛКМ/J: Атака  |  ПКМ/Shift: Рывок  |  СКМ/Q: Парирование  |  E: Искусство  |  F: Лечение  |  TAB: Меню", True, (135, 155, 185))
    surf.blit(ctrl_txt, (WIDTH - ctrl_txt.get_width() - 26, 46))

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


def draw_blessing_draft(surf, choices, selected_idx):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((6, 9, 18, 205))
    surf.blit(ov, (0, 0))

    f_head = get_font(34, bold=True)
    f_card = get_font(22, bold=True)
    f_desc = get_font(17)

    title = f_head.render("ЗАЛ ОЧИЩЕН — ВЫБЕРИ АСТРАЛЬНЫЙ ДАР", True, (245, 250, 255))
    surf.blit(title, ((WIDTH - title.get_width()) // 2, 115))

    for i, bl in enumerate(choices):
        cw, ch = 310, 340
        cx = 145 + i * 340
        cy = 195
        card = pygame.Rect(cx, cy, cw, ch)
        is_sel = i == selected_idx
        pygame.draw.rect(surf, (24, 34, 56) if is_sel else (16, 22, 36), card, border_radius=16)
        pygame.draw.rect(surf, bl["color"] if is_sel else (55, 70, 102), card, 3 if is_sel else 2, border_radius=16)

        pygame.draw.polygon(surf, bl["color"], [(card.centerx, cy + 55), (card.centerx + 26, cy + 88), (card.centerx, cy + 121), (card.centerx - 26, cy + 88)])
        t_img = f_card.render(f"[{i + 1}] {bl['name']}", True, (245, 250, 255))
        surf.blit(t_img, (card.centerx - t_img.get_width() // 2, cy + 150))

        # Перенос текста описания по строкам
        words = bl["desc"].split()
        lines, line = [], ""
        for w in words:
            if len(line + w) < 28:
                line += w + " "
            else:
                lines.append(line)
                line = w + " "
        lines.append(line)
        for li, ltxt in enumerate(lines):
            d_img = f_desc.render(ltxt.strip(), True, (195, 218, 245))
            surf.blit(d_img, (card.centerx - d_img.get_width() // 2, cy + 195 + li * 24))


def draw_altar_menu(surf, hero, tab_idx, selected_idx, at_altar, defeated_bosses):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((6, 9, 18, 220))
    surf.blit(ov, (0, 0))

    panel = pygame.Rect(110, 62, WIDTH - 220, HEIGHT - 124)
    pygame.draw.rect(surf, (15, 20, 34), panel, border_radius=16)
    pygame.draw.rect(surf, (95, 215, 245), panel, 2, border_radius=16)

    f_head = get_font(24, bold=True)
    f_med = get_font(18, bold=True)
    f_reg = get_font(16)

    mode = "АЛТАРЬ РЕЗОНАНСА (Смена Реликвий, Оружия и Ковка)" if at_altar else "ЖУРНАЛ СТРАННИКА (Подойди к Алтарю в Святилище, чтобы менять билд)"
    surf.blit(f_head.render(mode, True, (242, 248, 255)), (panel.left + 28, panel.top + 18))

    tabs = ["[1] Реликвии и Синергии", "[2] Арсенал Оружия", "[3] Ковка", "[4] Бестиарий"]
    for i, tname in enumerate(tabs):
        col = (105, 235, 255) if i == tab_idx else (130, 145, 175)
        surf.blit(f_med.render(tname, True, col), (panel.left + 28 + i * 240, panel.top + 58))

    info = f_med.render(f"Ячейки: {hero.used_slots()}/{hero.max_slots}  |  Люмен: {hero.lumen}", True, (255, 220, 115))
    surf.blit(info, (panel.right - info.get_width() - 28, panel.top + 58))
    pygame.draw.line(surf, (48, 64, 96), (panel.left + 22, panel.top + 92), (panel.right - 22, panel.top + 92), 2)

    if tab_idx == 0:
        # 16 реликвий в 2 колонки по 8
        for idx, rel in enumerate(RELICS):
            col_i = idx % 2
            row_i = idx // 2
            bx = panel.left + 28 + col_i * 505
            by = panel.top + 105 + row_i * 46
            box = pygame.Rect(bx, by, 485, 40)

            is_sel = idx == (selected_idx % len(RELICS))
            is_eq = rel["id"] in hero.equipped
            bg_col = (30, 44, 70) if is_sel else (21, 28, 44)
            border_col = (110, 235, 255) if is_sel else ((115, 240, 175) if is_eq else (48, 60, 86))
            pygame.draw.rect(surf, bg_col, box, border_radius=8)
            pygame.draw.rect(surf, border_col, box, 2, border_radius=8)

            c_col = rel["color"] if rel["unlocked"] else (68, 76, 94)
            pygame.draw.polygon(surf, c_col, [(bx + 20, by + 10), (bx + 30, by + 20), (bx + 20, by + 30), (bx + 10, by + 20)])
            status = "[АКТИВНА]" if is_eq else (f"{rel['slots']} яч." if rel["unlocked"] else f"{rel['cost']} Люм.")
            surf.blit(f_med.render(rel["name"], True, (245, 248, 255) if rel["unlocked"] else (150, 160, 180)), (bx + 42, by + 9))
            st_img = f_reg.render(status, True, (125, 245, 180) if is_eq else (255, 215, 115))
            surf.blit(st_img, (box.right - st_img.get_width() - 12, by + 10))

        cur = RELICS[selected_idx % len(RELICS)]
        active_syns = [s["name"] for s in SYNERGIES if s["id"] in hero.active_synergies()]
        syn_str = f"Активные Синергии: {', '.join(active_syns)}" if active_syns else "Подсказка: комбинируй реликвии для открытия скрытых Синергий!"
        surf.blit(f_reg.render(f"{cur['name']} ({cur['slots']} яч.): {cur['desc']}", True, (215, 238, 255)), (panel.left + 28, panel.bottom - 88))
        surf.blit(f_reg.render(syn_str, True, (255, 215, 115)), (panel.left + 28, panel.bottom - 62))

    elif tab_idx == 1:
        w_keys = ["saber", "daggers", "greatsword"]
        for idx, wk in enumerate(w_keys):
            wp = WEAPONS[wk]
            by = panel.top + 115 + idx * 115
            box = pygame.Rect(panel.left + 36, by, panel.width - 72, 96)
            is_sel = idx == (selected_idx % 3)
            is_cur = hero.weapon_id == wk
            pygame.draw.rect(surf, (30, 44, 70) if is_sel else (21, 28, 44), box, border_radius=12)
            pygame.draw.rect(surf, wp["color"] if (is_sel or is_cur) else (50, 64, 92), box, 3 if is_cur else 2, border_radius=12)
            tag = " [ВЫБРАНО]" if is_cur else ""
            surf.blit(f_head.render(f"[{wp['key']}] {wp['name']}{tag}", True, wp["color"]), (box.left + 20, box.top + 14))
            surf.blit(f_reg.render(wp["desc"], True, (220, 235, 255)), (box.left + 20, box.top + 52))

    elif tab_idx == 2:
        upgrades = [
            ("Закалка Астрального Клинка (+4 к базовому урону)", 110 + (hero.base_damage - 16) * 20, f"Базовый урон: {hero.base_damage}"),
            ("Кристалл Прочности (+1 ячейка здоровья)", 140 + (hero.base_max_hp - 6) * 65, f"Макс. прочность: {hero.max_hp}"),
            ("Слот Резонанса (+1 ячейка для реликвий)", 130 + (hero.max_slots - 4) * 55, f"Всего ячеек: {hero.max_slots}/12"),
            ("Сосуд Эфира (+25 к запасу энергии)", 120 + int((hero.max_aether - 100) * 2), f"Макс. Эфир: {int(hero.max_aether)}"),
        ]
        for idx, (title, cost, cur_val) in enumerate(upgrades):
            by = panel.top + 118 + idx * 82
            box = pygame.Rect(panel.left + 36, by, panel.width - 72, 66)
            is_sel = idx == (selected_idx % 4)
            pygame.draw.rect(surf, (30, 44, 70) if is_sel else (21, 28, 44), box, border_radius=10)
            pygame.draw.rect(surf, (110, 235, 255) if is_sel else (50, 64, 92), box, 2, border_radius=10)
            surf.blit(f_med.render(title, True, (242, 248, 255)), (box.left + 20, box.top + 10))
            surf.blit(f_reg.render(cur_val, True, (155, 200, 235)), (box.left + 20, box.top + 38))
            c_img = f_med.render(f"Улучшить: {cost} Люмена", True, (255, 220, 115))
            surf.blit(c_img, (box.right - c_img.get_width() - 22, box.top + 20))

    else:
        for idx, bdef in enumerate(BOSS_DEFS):
            kind, bname, prim, glow, lore = bdef
            by = panel.top + 108 + idx * 66
            box = pygame.Rect(panel.left + 36, by, panel.width - 72, 54)
            killed = kind in defeated_bosses
            pygame.draw.rect(surf, (21, 28, 44), box, border_radius=9)
            pygame.draw.rect(surf, prim if killed else (48, 58, 82), box, 2, border_radius=9)
            surf.blit(f_med.render(bname if killed else "??? (Неизвестный Владыка)", True, glow if killed else (125, 135, 160)), (box.left + 18, box.top + 7))
            surf.blit(f_reg.render(lore if killed else "Победи этого босса в Чертоге, чтобы открыть запись.", True, (200, 218, 242)), (box.left + 18, box.top + 30))

    foot = f_reg.render("WASD / Стрелки: Выбор   |   Enter / Пробел: Применить   |   1-4: Вкладки   |   ESC / TAB: Закрыть", True, (165, 190, 220))
    surf.blit(foot, ((WIDTH - foot.get_width()) // 2, panel.bottom - 30))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Astral Knight")
    clock = pygame.time.Clock()
    entity_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    bloom = BloomRenderer()
    sprite_bank = SpriteBank()

    f_big = get_font(62, bold=True)
    f_med = get_font(24, bold=True)
    f_prompt = get_font(19, bold=True)

    fullscreen = False
    game_state = "title"
    defeated_bosses = set()

    def init_run():
        for r in RELICS:
            r["unlocked"] = r["cost"] == 0
        h = Hero()
        h.recalculate_stats()
        rtype, plats, hazs, clsts, enms, al_rect = build_room(1, 0)
        b = BIOMES[0]
        motes = [WeatherParticle(b) for _ in range(42)]
        return h, 1, 0, rtype, plats, hazs, clsts, enms, al_rect, None, build_sky_surface(b), motes

    hero, depth, room_idx, room_type, platforms, hazards, clusters, enemies, altar_rect, boss, sky_surf, motes = init_run()

    sparks, rings, floating_texts = [], [], []
    lumen_crystals, shockwaves, projectiles, lasers, arts = [], [], [], [], []
    draft_choices = []
    draft_sel = 0

    hitstop = 0.0
    shake = 0.0
    banner_timer = 0.0
    banner_text = ""
    menu_tab = 0
    menu_sel = 0
    at_altar = False

    def enter_room(new_depth, new_room_idx):
        nonlocal depth, room_idx, room_type, platforms, hazards, clusters, enemies, altar_rect, boss
        nonlocal sky_surf, motes, banner_timer, banner_text
        depth = new_depth
        room_idx = new_room_idx
        biome = BIOMES[(depth - 1) % len(BIOMES)]
        if room_idx == 0:
            sky_surf = build_sky_surface(biome)
            motes = [WeatherParticle(biome) for _ in range(42)]
            hero.immortal_used = False

        room_type, platforms, hazards, clusters, enemies, altar_rect = build_room(depth, room_idx)
        shockwaves.clear()
        projectiles.clear()
        lasers.clear()
        arts.clear()

        hero.x = 85.0
        hero.y = float(FLOOR_Y - hero.rect.height)
        hero.vx = 0.0
        hero.vy = 0.0
        hero.rect.topleft = (int(hero.x), int(hero.y))

        if room_type == "boss":
            bdef = BOSS_DEFS[(depth - 1) % len(BOSS_DEFS)]
            boss = Boss(depth, bdef)
            banner_text = boss.name
            banner_timer = 2.1
        else:
            boss = None
            if room_idx == 0:
                banner_text = f"ЭТАЖ {depth}  |  {biome['name']}"
                banner_timer = 1.9

    def apply_blessing(bl):
        hero.blessings.append(bl["id"])
        hero.recalculate_stats()
        if bl["id"] == "b_hp":
            hero.hp = min(hero.max_hp, hero.hp + 3)
        elif bl["id"] == "b_flow":
            hero.resonance = max(hero.resonance, 30.0)

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
                        hero, depth, room_idx, room_type, platforms, hazards, clusters, enemies, altar_rect, boss, sky_surf, motes = init_run()
                        sparks.clear()
                        rings.clear()
                        floating_texts.clear()
                        lumen_crystals.clear()
                        shockwaves.clear()
                        projectiles.clear()
                        lasers.clear()
                        arts.clear()
                        game_state = "playing"

                elif game_state == "blessing_draft":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        draft_sel = (draft_sel - 1) % 3
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        draft_sel = (draft_sel + 1) % 3
                    elif event.key == pygame.K_1:
                        apply_blessing(draft_choices[0])
                        enter_room(depth, room_idx + 1)
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        apply_blessing(draft_choices[1])
                        enter_room(depth, room_idx + 1)
                        game_state = "playing"
                    elif event.key == pygame.K_3:
                        apply_blessing(draft_choices[2])
                        enter_room(depth, room_idx + 1)
                        game_state = "playing"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        apply_blessing(draft_choices[draft_sel])
                        enter_room(depth, room_idx + 1)
                        game_state = "playing"

                elif game_state == "altar_menu":
                    if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                        game_state = "playing"
                    elif event.key == pygame.K_1:
                        menu_tab = 0
                        menu_sel = 0
                    elif event.key == pygame.K_2:
                        menu_tab = 1
                        menu_sel = 0
                    elif event.key == pygame.K_3:
                        menu_tab = 2
                        menu_sel = 0
                    elif event.key == pygame.K_4:
                        menu_tab = 3
                        menu_sel = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        step = 2 if menu_tab == 0 else 1
                        limit = len(RELICS) if menu_tab == 0 else (3 if menu_tab == 1 else 4)
                        menu_sel = (menu_sel - step) % limit
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        step = 2 if menu_tab == 0 else 1
                        limit = len(RELICS) if menu_tab == 0 else (3 if menu_tab == 1 else 4)
                        menu_sel = (menu_sel + step) % limit
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and menu_tab == 0:
                        menu_sel = (menu_sel - 1) % len(RELICS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and menu_tab == 0:
                        menu_sel = (menu_sel + 1) % len(RELICS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and at_altar:
                        if menu_tab == 0:
                            rel = RELICS[menu_sel % len(RELICS)]
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
                        elif menu_tab == 1:
                            hero.weapon_id = ["saber", "daggers", "greatsword"][menu_sel % 3]
                        elif menu_tab == 2:
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
                    # Смена оружия на лету (1, 2, 3)
                    if event.key == pygame.K_1:
                        hero.weapon_id = "saber"
                        floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 16, "Астральная Сабля", WEAPONS["saber"]["color"], 18))
                    elif event.key == pygame.K_2:
                        hero.weapon_id = "daggers"
                        floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 16, "Звёздные Кинжалы", WEAPONS["daggers"]["color"], 18))
                    elif event.key == pygame.K_3:
                        hero.weapon_id = "greatsword"
                        floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 16, "Солнечный Клеймор", WEAPONS["greatsword"]["color"], 18))

                    elif event.key == pygame.K_TAB:
                        at_altar = False
                        game_state = "altar_menu"

                    elif room_type == "sanctuary" and altar_rect and hero.rect.colliderect(altar_rect.inflate(48, 20)) and event.key in (pygame.K_w, pygame.K_e):
                        hero.hp = hero.max_hp
                        hero.aether = hero.max_aether
                        at_altar = True
                        game_state = "altar_menu"

                    elif event.key == pygame.K_SPACE and (keys[pygame.K_s] or keys[pygame.K_DOWN]) and hero.on_ground and hero.y + hero.rect.height < FLOOR_Y - 5:
                        hero.drop_through_timer = 0.22
                        hero.on_ground = False
                    elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        if hero.jumps_left > 0 and hero.dash_timer <= 0 and not hero.dive_active:
                            hero.vy = -815.0
                            hero.jumps_left -= 1
                            hero.on_ground = False
                            hero.jump_held = True
                            rings.append(RingWave(hero.rect.centerx, hero.rect.bottom, 42, (135, 235, 255), 0.25, 3))

                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k):
                        if hero.start_dash():
                            shake = max(shake, 4.0)

                    elif event.key == pygame.K_j:
                        hero.start_slash(keys, projectiles)

                    elif event.key in (pygame.K_q, pygame.K_c):
                        hero.start_parry()

                    elif event.key == pygame.K_e:
                        if hero.cast_art(keys, arts, sparks):
                            shake = max(shake, 7.0)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    hero.jump_held = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
                if event.button == 1:
                    hero.start_slash(keys, projectiles)
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
                hero.update(dt, keys, platforms, sparks, rings, arts, shockwaves)
                syns = hero.active_synergies()

                # Отложенный Эхо-Клинок + синергия Тройная Нова
                if hero.pending_echo:
                    delay, e_rect, e_dir = hero.pending_echo
                    delay -= dt
                    if delay <= 0:
                        hero.pending_echo = None
                        rings.append(RingWave(e_rect.centerx, e_rect.centery, 58, (195, 145, 255), 0.22, 4))
                        edmg = max(4, int(hero.blade_damage * 0.55))
                        for en in enemies:
                            if e_rect.colliderect(en.rect):
                                en.hp -= edmg
                                en.flash = 0.06
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 8, edmg, (205, 160, 255), 17))
                        if boss and boss.hp > 0 and e_rect.colliderect(boss.rect):
                            boss.take_damage(edmg)
                            floating_texts.append(FloatingText(boss.rect.centerx, boss.rect.top - 12, edmg, (205, 160, 255), 18))
                        if "trinity_nova" in syns:
                            for off in (-0.25, 0.0, 0.25):
                                ang = (0 if hero.facing == 1 else math.pi) + off
                                projectiles.append(Projectile(e_rect.centerx, e_rect.centery, math.cos(ang) * 720, math.sin(ang) * 720, 11, (255, 215, 115), friendly=True, damage=edmg))
                    else:
                        hero.pending_echo = (delay, e_rect, e_dir)

                for cl in clusters:
                    cl.update(dt)
                for en in enemies:
                    en.update(dt, hero, projectiles)
                if boss and boss.hp > 0:
                    boss.update(dt, hero, projectiles, shockwaves, lasers, sparks)

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
                for spk in sparks:
                    spk.update(dt)
                for rng in rings:
                    rng.update(dt)
                for ft in floating_texts:
                    ft.update(dt)

                shockwaves = [s for s in shockwaves if s.life > 0]
                projectiles = [p for p in projectiles if p.life > 0 and -50 <= p.x <= WIDTH + 50 and p.y <= FLOOR_Y + 25]
                lasers = [l for l in lasers if l.timer > 0]
                arts = [a for a in arts if a.life > 0 and -250 <= a.x <= WIDTH + 250]
                sparks = [s for s in sparks if s.life > 0]
                rings = [r for r in rings if r.life > 0]
                floating_texts = [f for f in floating_texts if f.life > 0]

                # Сбор Люмена
                for lc in list(lumen_crystals):
                    if lc.life <= 0:
                        lumen_crystals.remove(lc)
                    elif hero.rect.colliderect(lc.rect.inflate(14, 14)):
                        mult = (1.3 if hero.has_relic("lumen_magnet") else 1.0) * (1.4 if hero.has_blessing("b_lumen") else 1.0)
                        hero.lumen += int(round(lc.value * mult))
                        lumen_crystals.remove(lc)

                # Попадания клинка
                s_rect = hero.get_slash_rect()
                aether_gain = hero.weapon["aether_gain"] * (1.45 if hero.has_relic("void_siphon") else 1.0)

                if s_rect:
                    if hero.slash_dir == "down":
                        for hz in hazards:
                            if s_rect.colliderect(hz.rect):
                                hero.vy = -810.0
                                hero.reset_air_mobility()
                                rings.append(RingWave(hero.rect.centerx, hz.rect.top, 45, biome["accent"], 0.25, 3))
                                break

                    for cl in clusters:
                        if cl.hp > 0 and s_rect.colliderect(cl.rect) and id(cl) not in hero.hit_ids:
                            hero.hit_ids.add(id(cl))
                            cl.hp -= 1
                            cl.flash = 0.08
                            shake = max(shake, 5.0)
                            for _ in range(4 if cl.hp > 0 else 10):
                                lumen_crystals.append(LumenCrystal(cl.rect.centerx, cl.rect.centery, 6))

                    for en in list(enemies):
                        if s_rect.colliderect(en.rect) and id(en) not in hero.hit_ids:
                            hero.hit_ids.add(id(en))
                            blocked = (
                                not hero.weapon["guard_break"]
                                and en.kind == "aegis_warden"
                                and hero.slash_dir in ("left", "right")
                                and ((en.facing == -1 and hero.rect.centerx < en.rect.centerx) or (en.facing == 1 and hero.rect.centerx > en.rect.centerx))
                            )
                            if blocked:
                                hero.vx = -hero.facing * 320.0
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, "ЩИТ! (Нажми 3)", (140, 225, 255), 17))
                            else:
                                crit = hero.has_blessing("b_crit") and random.random() < 0.25
                                dmg = hero.blade_damage * (2 if crit else 1)
                                en.hp -= dmg
                                en.flash = 0.08
                                hero.aether = min(hero.max_aether, hero.aether + aether_gain)
                                hero.add_resonance(12.0)
                                hero.combo_count += 1
                                hitstop = 0.026
                                shake = max(shake, 6.0)
                                floating_texts.append(FloatingText(en.rect.centerx, en.rect.top - 10, f"{dmg}{'!' if crit else ''}", (255, 225, 110) if crit else (255, 255, 255), 21 if crit else 19))
                                for _ in range(10):
                                    sparks.append(SparkParticle(en.rect.centerx, en.rect.centery, random.uniform(-340, 340), random.uniform(-340, 120), hero.weapon["color"], 0.28))
                                if hero.slash_dir == "down":
                                    hero.vy = -810.0
                                    hero.reset_air_mobility()
                                    if hero.has_relic("astral_vortex"):
                                        arts.append(AstralArtBlast(hero.rect.centerx - 90, hero.rect.centery - 90, 180, 180, 0, 0, int(dmg * 0.8), 0.18, "nova"))
                                else:
                                    en.vx += hero.facing * 260.0

                    if boss and boss.hp > 0 and s_rect.colliderect(boss.rect) and id(boss) not in hero.hit_ids:
                        hero.hit_ids.add(id(boss))
                        crit = hero.has_blessing("b_crit") and random.random() < 0.25
                        dmg = hero.blade_damage * (2 if crit else 1)
                        boss.take_damage(dmg)
                        hero.aether = min(hero.max_aether, hero.aether + aether_gain)
                        hero.add_resonance(11.0)
                        hero.combo_count += 1
                        hitstop = 0.034
                        shake = max(shake, 8.0)
                        floating_texts.append(FloatingText(boss.rect.centerx + random.randint(-20, 20), boss.rect.top - 14, f"{dmg}{'!' if crit else ''}", (255, 230, 115), 23))
                        for _ in range(14):
                            sparks.append(SparkParticle(boss.rect.centerx, boss.rect.centery, random.uniform(-420, 420), random.uniform(-420, 140), boss.glow, 0.32))
                        if "overdrive_fury" in syns and hero.resonance_tier == 3:
                            rings.append(RingWave(boss.rect.centerx, boss.rect.centery, 110, (255, 210, 105), 0.25, 5))
                            boss.take_damage(int(dmg * 0.4))
                        if hero.slash_dir == "down":
                            hero.vy = -810.0
                            hero.reset_air_mobility()
                            if hero.has_relic("astral_vortex"):
                                arts.append(AstralArtBlast(hero.rect.centerx - 95, hero.rect.centery - 95, 190, 190, 0, 0, int(dmg * 0.8), 0.18, "nova"))
                        elif hero.slash_dir == "left":
                            hero.vx = 220.0
                        elif hero.slash_dir == "right":
                            hero.vx = -220.0

                # Искровой Шаг при рывке
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

                # Дружественные снаряды и Астральные Искусства
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

                for en in list(enemies):
                    if en.hp <= 0:
                        enemies.remove(en)
                        if hero.has_relic("crimson_fang") and hero.hp < hero.max_hp and random.random() < 0.35:
                            hero.hp += 1
                        rings.append(RingWave(en.rect.centerx, en.rect.centery, 65, biome["accent"], 0.28, 4))
                        for _ in range(max(2, en.lumen // 4)):
                            lumen_crystals.append(LumenCrystal(en.rect.centerx, en.rect.centery, 4))
                        for _ in range(18):
                            ang = random.uniform(0, math.tau)
                            spd = random.uniform(120, 380)
                            sparks.append(SparkParticle(en.rect.centerx, en.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, biome["accent"], 0.38))

                # Астральное Парирование
                parry_zone = hero.rect.inflate(40, 40)
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
                        shake = 13.0
                        rings.append(RingWave(hero.rect.centerx, hero.rect.centery, 145, (255, 235, 130), 0.35, 6))
                        floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 22, "ПАРИРОВАНИЕ!", (255, 235, 130), 22))
                        if hero.has_blessing("b_parry") and hero.parry_heal_cd <= 0 and hero.hp < hero.max_hp:
                            hero.hp += 1
                            hero.parry_heal_cd = 15.0
                        if hero.has_relic("mirror_aegis"):
                            for i in range(3):
                                ang = -0.3 + i * 0.3 + (0 if hero.facing == 1 else math.pi)
                                projectiles.append(Projectile(hero.rect.centerx, hero.rect.centery, math.cos(ang) * 480, math.sin(ang) * 480, 10, (255, 235, 140), homing=True, friendly=True, damage=hero.blade_damage))
                        if "storm_parry" in syns:
                            for en in enemies:
                                en.hp -= hero.blade_damage * 2
                            if boss and boss.hp > 0:
                                boss.take_damage(hero.blade_damage * 2)

                # Получение урона
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
                        floor_res = 30.0 if hero.has_blessing("b_flow") else 0.0
                        hero.resonance = max(floor_res, hero.resonance - 35.0)
                        hero.combo_count = 0
                        hitstop = 0.055
                        shake = 15.0
                        hero.vy = -440.0
                        hero.vx = -hero.facing * 360.0
                        rings.append(RingWave(hero.rect.centerx, hero.rect.centery, 110, (255, 85, 115), 0.3, 5))

                        if hero.has_relic("briar_halo"):
                            hero.aether = min(hero.max_aether, hero.aether + 25.0)
                            blast_r = hero.rect.inflate(190, 190)
                            for en in enemies:
                                if blast_r.colliderect(en.rect):
                                    en.hp -= hero.blade_damage * 2
                            if boss and boss.hp > 0 and blast_r.colliderect(boss.rect):
                                boss.take_damage(hero.blade_damage * 2)

                        if hero.hp <= 0:
                            if "immortal_aegis" in syns and not hero.immortal_used:
                                hero.immortal_used = True
                                hero.hp = 1
                                rings.append(RingWave(hero.rect.centerx, hero.rect.centery, 260, (255, 225, 120), 0.5, 8))
                                floating_texts.append(FloatingText(hero.rect.centerx, hero.rect.top - 26, "БЕССМЕРТНЫЙ СТРАЖ!", (255, 230, 120), 24))
                            else:
                                game_state = "game_over"

                # Победа над боссом
                if room_type == "boss" and boss and boss.hp <= 0:
                    defeated_bosses.add(boss.kind)
                    shake = 18.0
                    hitstop = 0.085
                    banner_text = f"{boss.name} ПОВЕРЖЕН!"
                    banner_timer = 2.4
                    rings.append(RingWave(boss.rect.centerx, boss.rect.centery, 280, boss.glow, 0.55, 8))
                    for _ in range(32):
                        lumen_crystals.append(LumenCrystal(boss.rect.centerx, boss.rect.centery, 8))
                    for _ in range(60):
                        ang = random.uniform(0, math.tau)
                        spd = random.uniform(160, 660)
                        sparks.append(SparkParticle(boss.rect.centerx, boss.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, boss.glow, 0.65))
                    shockwaves.clear()
                    projectiles.clear()
                    lasers.clear()
                    boss = None

                # Переход в следующую комнату + Драфт Астральных Даров после залов I и II
                gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
                if gate_open and hero.rect.right >= WIDTH - 42:
                    if room_type == "combat":
                        draft_choices = random.sample(BLESSINGS, 3)
                        draft_sel = 0
                        game_state = "blessing_draft"
                    elif room_idx < 3:
                        enter_room(depth, room_idx + 1)
                    else:
                        enter_room(depth + 1, 0)

        # --- ОТРИСОВКА КАДРА ---
        shake = max(0.0, shake - 44.0 * dt)
        ox = random.uniform(-shake, shake) if shake > 0 else 0.0
        oy = random.uniform(-shake, shake) if shake > 0 else 0.0

        bloom.clear()
        gate_open = (room_type == "sanctuary") or (room_type == "combat" and len(enemies) == 0) or (room_type == "boss" and boss is None)
        draw_world_backdrop(screen, bloom, sky_surf, biome, ox, oy, altar_rect, gate_open)
        for m in motes:
            m.draw(screen, bloom, ox, oy)

        entity_layer.fill((0, 0, 0, 0))
        for plat in platforms:
            plat.draw(entity_layer, bloom, 0, 0, biome)
        for hz in hazards:
            hz.draw(entity_layer, bloom, 0, 0, biome)
        for cl in clusters:
            cl.draw(entity_layer, bloom, 0, 0)
        for sw in shockwaves:
            sw.draw(entity_layer, bloom, 0, 0)
        for en in enemies:
            en.draw(entity_layer, bloom, sprite_bank, 0, 0)
        if boss and boss.hp > 0:
            boss.draw(entity_layer, bloom, sprite_bank, 0, 0)
        hero.draw(entity_layer, bloom, sprite_bank, 0, 0)
        for ar in arts:
            ar.draw(entity_layer, bloom, 0, 0)
        for pr in projectiles:
            pr.draw(entity_layer, bloom, 0, 0)
        for lz in lasers:
            lz.draw(entity_layer, bloom, 0, 0)
        for lc in lumen_crystals:
            lc.draw(entity_layer, bloom, 0, 0)
        for spk in sparks:
            spk.draw(entity_layer, bloom, 0, 0)
        for rng in rings:
            rng.draw(entity_layer, bloom, 0, 0)

        draw_reflective_floor(screen, sprite_bank, entity_layer, biome, ox, oy)
        screen.blit(entity_layer, (int(ox), int(oy)))
        bloom.compose(screen)

        for ft in floating_texts:
            ft.draw(screen, ox, oy)

        if game_state == "playing" and room_type == "sanctuary" and altar_rect and hero.rect.colliderect(altar_rect.inflate(48, 20)):
            p_img = f_prompt.render("[W / E] Коснуться Алтаря Резонанса (Реликвии, Оружие и Ковка)", True, (255, 240, 175))
            screen.blit(p_img, (altar_rect.centerx - p_img.get_width() // 2 + int(ox), altar_rect.top - 42 + int(oy)))

        draw_hud(screen, hero, boss, depth, room_idx, biome)

        if banner_timer > 0 and game_state == "playing":
            b_img = f_med.render(banner_text, True, (245, 250, 255))
            bx = (WIDTH - b_img.get_width()) // 2
            by = 132
            pygame.draw.line(screen, biome["accent"], (bx - 45, by + 36), (bx + b_img.get_width() + 45, by + 36), 2)
            screen.blit(b_img, (bx, by))

        if game_state == "title":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((6, 9, 18, 185))
            screen.blit(ov, (0, 0))
            t1 = f_big.render("ASTRAL KNIGHT", True, (245, 250, 255))
            t2 = f_med.render("Нажми ENTER или ПРОБЕЛ, чтобы войти в Разлом", True, (110, 235, 255))
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 58))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 18))

        elif game_state == "blessing_draft":
            draw_blessing_draft(screen, draft_choices, draft_sel)

        elif game_state == "altar_menu":
            draw_altar_menu(screen, hero, menu_tab, menu_sel, at_altar, defeated_bosses)

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
