import pygame
import sys
import random
import math
import traceback

try:
    pygame.init()

    # === [スマホ軽量化] 解像度を自動で半分にして爆速化 ===
    info = pygame.display.Info()
    W = int(info.current_w * 0.5)
    H = int(info.current_h * 0.5)
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)

    clock = pygame.time.Clock()
    GY = H + 25   # 地面の位置（調整済み数値）

    def get_col(i):
        # 画面に美しく映える黄緑マシマシ版パレット
        palette = [
            (170, 240, 40), (150, 225, 45), (135, 215, 50), (115, 210, 65),
            (100, 200, 75), (34, 160, 75), (20, 110, 50), (15, 120, 130)
        ]
        return palette[max(0, min(len(palette) - 1, i))]

    def get_safe_type():
        return random.randint(0, 10)

    # === グローバル変数 ===
    is_fixed_mode = False       
    saved_flower_data = None    

    pygame.font.init()
    btn_font = pygame.font.Font(None, 50)
    btn_rect = pygame.Rect(W - 270, 30, 250, 100)

    class Leaf:
        def __init__(self, h, ld, leaf_type):
            self.h = h                  
            self.ld = ld                
            self.leaf_type = leaf_type  
            self.current_scale = 1.0     
            self.is_growing = False     
            self.growth_speed = 1.0 / 42.0 
            
        def update(self):
            if self.is_growing:
                if self.current_scale < 2.0:
                    self.current_scale += self.growth_speed
                    if self.current_scale > 2.0:
                        self.current_scale = 2.0
    class Flower:
        # クローンや遺伝のために、引数の最後に cc (コアカラー) を確実に受け取れるよう固定
        def __init__(self, x, c, ml, p, n, w, s, si, pt, cc=None):
            self.x = int(x)
            self.y = int(GY)
            self.color = c
            self.max_len = ml
            self.current_len = 0.0
            self.is_bloomed = False
            self.life = 600
            self.scale = 1.0
            self.p_count = p
            self.g_len = float(n)
            self.g_wide = float(w)
            self.g_skew = float(s)
            self.stem_idx = int(si)
            self.p_type = int(pt)
            self.seed = random.uniform(0.1, 0.4)
            self.dir = -1 if random.random() < 0.5 else 1
            self.sc = get_col(self.stem_idx)
            self.core_color = cc  # 渡された花芯の色を最優先で記憶！
            
            # 花弁タイプの判定
            if self.p_type in [2, 3, 5, 6, 9]:
                self.p_count = random.randint(5, 16)
            else:
                self.p_count = int(p)
            
            s_r, s_g, s_b = float(self.sc[0]), float(self.sc[1]), float(self.sc[2])
            self.lc = (int(s_r * 0.4 + 5), int(s_g * 0.4 + 5), int(s_b * 0.4 + 9))
            
            self.core_size = random.uniform(12.0, 30.0)
            
            # 【重要】花芯の色（core_color）がまだ決まっていない新規野生種の時だけ大抽選を行う！
            if self.core_color is None:
                c_r = c[0] if isinstance(c, (list, tuple)) else c
                c_g = c[1] if isinstance(c, (list, tuple)) else c
                c_b = c[2] if isinstance(c, (list, tuple)) else c
                
                core_chance = random.random()
                if core_chance < 0.03:
                    self.core_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                elif core_chance < 0.15:
                    self.core_color = (255 - c_r, 255 - c_g, 255 - c_b)
                elif core_chance < 0.55:
                    self.core_color = (min(255, int(c_r * 1.3 + 30)), min(255, int(c_g * 1.3 + 30)), min(255, int(c_b * 1.3 + 30)))
                else:
                    wild_style = random.randint(0, 2)
                    if wild_style == 0:
                        br_r = random.randint(100, 140)
                        br_g = int(br_r * random.uniform(0.6, 0.75))
                        br_b = int(br_g * random.uniform(0.5, 0.7))
                        self.core_color = (br_r, br_g, br_b)
                    elif wild_style == 1:
                        self.core_color = (255, random.randint(180, 240), random.randint(50, 120))
                    else:
                        self.core_color = (random.randint(245, 255), random.randint(245, 255), random.randint(240, 250))
                
            self.has_b = random.random() < 0.35
            self.bh = random.randint(int(ml * 0.3), int(ml * 0.6))
            self.bd = -self.dir
            self.b_ml = random.uniform(ml * 0.4, ml * 0.7)
            self.b_p = max(3, min(10, p + random.randint(-1, 1)))
            self.b_t = get_safe_type() if random.random() < 0.3 else pt

            self.flower_leaf_type = random.randint(0, 3)

            self.leaves = []
            for i in range(0, int(self.max_len), 10):
                if i > 50 and i % 90 == 0:
                    ld = 1 if (i // 90) % 2 == 0 else -1
                    self.leaves.append(Leaf(i, ld, self.flower_leaf_type))

            self.petal_growth = 0.0
            self.cached_petals = {}

            # ======= 【新規追加】小さな丸（葯）のバリエーション設定 =======
            self.dot_count = random.randint(4, 12)
            self.dot_distance_factor = random.uniform(1.0, 1.8)
            self.dot_size_factor = random.uniform(0.15, 0.35)
            
            dot_chance = random.random()
            c_r, c_g, c_b = self.color
            if dot_chance < 0.03:
                self.dot_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            elif dot_chance < 0.22:
                self.dot_color = (255 - c_r, 255 - c_g, 255 - c_b)
            elif dot_chance < 0.41:
                self.dot_color = (min(255, int(c_r * 1.3 + 30)), min(255, int(c_g * 1.3 + 30)), min(255, int(c_b * 1.3 + 30)))
            elif dot_chance < 0.60:
                br_r = random.randint(100, 140)
                br_g = int(br_r * random.uniform(0.6, 0.75))
                br_b = int(br_g * random.uniform(0.5, 0.7))
                self.dot_color = (br_r, br_g, br_b)
            elif dot_chance < 0.80:
                self.dot_color = (255, random.randint(180, 240), random.randint(50, 120))
            else:
                self.dot_color = (random.randint(245, 255), random.randint(245, 255), random.randint(240, 250))

    class Seed:
        def __init__(self, x, y, c, p, n, w, s, si, pt, cc=None):
            self.x = int(x)
            self.y = int(y)
            self.speed = 0.0
            self.color = c
            self.p_count = p
            self.val_nagasa = float(n)
            self.val_hutosa = float(w)
            self.val_hizumi = float(s)
            self.stem_idx = int(si)
            self.p_type = int(pt)
            self.core_color = cc

    seeds, flowers = [], []
    # === メインループ ===
    while True:
        pygame.key.stop_text_input()
        
        # [スマホ位置ズレ対策] 現在のスマホの「本物の画面サイズ」を毎フレーム取得する
        CUR_W, CUR_H = screen.get_size()
        if CUR_W != W or CUR_H != H:
            W, H = CUR_W, CUR_H
            GY = H + 25  # 地面の位置を自動配置
            btn_rect = pygame.Rect(W - 270, 30, 250, 100)  # ボタンを右上に自動配置
            
        screen.fill((248, 245, 235))
        pygame.draw.line(screen, (160, 145, 130), (0, GY), (W, GY), 2)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                # 【強力連打対策】すでに上限なら同時マルチタッチイベントを即座に破棄
                if len(flowers) + len(seeds) >= 6:
                    continue
                    
                mx, my = e.pos
                
                if btn_rect.collidepoint(mx, my):
                    if saved_flower_data is not None:  
                        is_fixed_mode = not is_fixed_mode
                    continue 
                    
                flower_clicked = False
                for f in flowers:
                    if f.is_bloomed and f.scale > 0:
                        ratio = f.current_len / f.max_len
                        off = (ratio * ratio) * 80.0 * f.dir * math.sin(ratio * math.pi * 0.5)
                        fx = int(f.x + off)
                        fy = int(f.y - f.current_len)
                        
                        dist_sq = (mx - fx) ** 2 + (my - fy) ** 2
                        if dist_sq < 2500: 
                            # クローン用に、親が持っている「現在の花芯の色」も完璧に保存
                            saved_flower_data = {
                                "color": f.color, "p_count": f.p_count, "g_len": f.g_len,
                                "g_wide": f.g_wide, "g_skew": f.g_skew, "stem_idx": f.stem_idx,
                                "p_type": f.p_type, "core_color": f.core_color
                            }
                            flower_clicked = True
                            break
                            
                if flower_clicked:
                    continue 
                    
                if my < GY and len(flowers) + len(seeds) <= 5:
                    if is_fixed_mode and saved_flower_data is not None:
                        # === 【クローンモード】保存した親の花芯色を100%そのまま種に持たせる ===
                        d = saved_flower_data
                        seeds.append(Seed(
                            mx, my, d["color"], d["p_count"], d["g_len"],
                            d["g_wide"], d["g_skew"], d["stem_idx"], d["p_type"],
                            d["core_color"]
                        ))
                    else:
                        # === 【通常タップ：野生の種】 ===
                        color_chance = random.random()
                        if color_chance < 0.05:
                            rn = random.random()
                            if rn < 0.25: wc = (255, 0, 127)
                            elif rn < 0.50: wc = (0, 255, 127)
                            elif rn < 0.75: wc = (0, 200, 255)
                            else: wc = (255, 210, 0)
                        elif color_chance < 0.25:
                            wc = (random.choice([0, 255]), random.choice([0, 255]), random.choice([0, 255]))
                            if sum(wc) == 0: wc = (255, 255, 0)
                        else:
                            wc = (random.randint(120, 230), random.randint(120, 230), random.randint(120, 230))
                        
                        wild_shape = random.choice([1, 3, 3, 0, 2, 3, 4, 5, 6, 7, 8, 9])
                        
                        w_cc = (120, 80, 40)
                        c_r = wc[0] if isinstance(wc, (list, tuple)) else wc
                        c_g = wc[1] if isinstance(wc, (list, tuple)) else wc
                        c_b = wc[2] if isinstance(wc, (list, tuple)) else wc
                        core_chance = random.random()
                        if core_chance < 0.03:
                            w_cc = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        elif core_chance < 0.15:
                            w_cc = (255 - c_r, 255 - c_g, 255 - c_b)
                        elif core_chance < 0.55:
                            w_cc = (min(255, int(c_r * 1.3 + 30)), min(255, int(c_g * 1.3 + 30)), min(255, int(c_b * 1.3 + 30)))
                        else:
                            wild_style = random.randint(0, 2)
                            if wild_style == 0:
                                br_r = random.randint(100, 140)
                                br_g = int(br_r * random.uniform(0.6, 0.75))
                                br_b = int(br_g * random.uniform(0.5, 0.7))
                                w_cc = (br_r, br_g, br_b)
                            elif wild_style == 1:
                                w_cc = (255, random.randint(180, 240), random.randint(50, 120))
                            else:
                                w_cc = (random.randint(245, 255), random.randint(245, 255), random.randint(240, 250))

                        seeds.append(Seed(
                            mx, my, wc, random.randint(3, 5),
                            random.uniform(50, 90), random.uniform(25, 50), random.uniform(-10, 10),
                            random.randint(0, 6), wild_shape, w_cc
                        ))

        # --- 種の更新と落下処理 ---
        for s in seeds[:]:
            s.speed += 0.4
            s.y += s.speed
            pygame.draw.circle(screen, (130, 95, 65), (int(s.x), int(s.y)), 8)
            pygame.draw.circle(screen, (100, 90, 80), (int(s.x), int(s.y)), 12, 1)
            
            if s.y >= GY:
                near = [f for f in flowers if f.is_bloomed and f.scale == 1.0 and abs(s.x - f.x) < 250]
                
                fc = s.color
                fp = s.p_count
                f_len = s.val_nagasa
                f_wide = s.val_hutosa
                f_skew = s.val_hizumi
                fsi = s.stem_idx
                ft = s.p_type
                f_cc = s.core_color if s.core_color is not None else (120, 80, 40)
                
                if near and not is_fixed_mode: 
                    cp = random.choice(near)
                    
                    mix_chance = random.random()
                    if mix_chance < 0.30:
                        fc = (
                            int((s.color[0] + cp.color[0]) / 2),
                            int((s.color[1] + cp.color[1]) / 2),
                            int((s.color[2] + cp.color[2]) / 2)
                        )
                    else:
                        fc = (
                            s.color[0] if random.random() < 0.5 else cp.color[0],
                            s.color[1] if random.random() < 0.5 else cp.color[1],
                            s.color[2] if random.random() < 0.5 else cp.color[2]
                        )
                    
                    f_cc = s.core_color if random.random() < 0.5 else cp.core_color
                    
                    rmut = random.random()
                    if rmut < 0.05:
                        fp = random.randint(6, 10)
                        f_len = random.uniform(85, 115)
                        f_wide = random.uniform(40, 60)
                        f_skew = random.uniform(-5, 5)
                        ft = get_safe_type()
                    elif rmut < 0.10:
                        rn = random.random()
                        if rn < 0.25: fc = (255, 0, 127)
                        elif rn < 0.50: fc = (0, 255, 127)
                        elif rn < 0.75: fc = (0, 200, 255)
                        else: fc = (255, 210, 0)
                    else:
                        fp = max(3, min(8, int((s.p_count + cp.p_count) / 2) + random.randint(-1, 1)))
                        fsi = random.randint(0, 6)
                        
                        shape_mut = random.random()
                        if shape_mut < 0.05:
                            ft = 10
                        else:
                            ft = s.p_type if random.random() < 0.5 else cp.p_type
                            
                        f_len = (s.val_nagasa + cp.g_len) / 2.0
                        f_wide = (s.val_hutosa + cp.g_wide) / 2.0
                        f_skew = (s.val_hizumi + cp.g_skew) / 2.0
                elif not is_fixed_mode:
                    if random.random() < 0.05:
                        fp = random.randint(6, 10)
                        f_len = random.uniform(85, 115)
                        f_wide = random.uniform(40, 60)
                        f_skew = random.uniform(-5, 5)
                        ft = get_safe_type()
                
                for f in flowers:
                    if abs(s.x - f.x) < 30 and f.scale > 0.5:
                        s.x += -50 if random.random() < 0.5 else 50
                        
                rh = random.randint(int(H * 0.25), int(H * 0.6))
                flowers.append(Flower(s.x, fc, rh, fp, f_len, f_wide, f_skew, fsi, ft, f_cc))
                seeds.remove(s)
        # --- 花と茎・葉の更新と描画処理 ---
        for f in flowers[:]:
            if f.current_len < f.max_len:
                f.current_len += 3.5
                if f.current_len >= f.max_len:
                    f.current_len = float(f.max_len)
                    f.is_bloomed = True
            else:
                f.is_bloomed = True
                f.life -= 1
                
                if f.scale == 1.0 and random.random() < 0.001 and (len(seeds) + len(flowers)) < 10:
                    dx = max(20, min(W - 20, f.x + random.randint(-40, 40)))
                    if is_fixed_mode and saved_flower_data is not None:
                        d = saved_flower_data
                        seeds.append(Seed(dx, f.y - f.current_len, d["color"], d["p_count"], d["g_len"], d["g_wide"], d["g_skew"], d["stem_idx"], d["p_type"], d["core_color"]))
                    else:
                        seeds.append(Seed(dx, f.y - f.current_len, f.color, f.p_count, f.g_len, f.g_wide, f.g_skew, f.stem_idx, f.p_type, f.core_color))
                    
                if f.life <= 0:
                    f.scale -= 0.02
                    if f.scale <= 0:
                        flowers.remove(f)
                        continue

            w = max(1, int(5 * f.scale))
            lx, ly = int(f.x), int(f.y)
            
            for i in range(0, int(f.current_len), 10):
                ratio = i / f.max_len
                off = (ratio * ratio) * 80.0 * f.dir * math.sin(ratio * math.pi * 0.5)
                nx, ny = int(f.x + off), int(f.y - i - 5)
                pygame.draw.line(screen, f.sc, (lx, ly), (nx, ny), w)
                
                for leaf in f.leaves:
                    if leaf.h == i and f.scale > 0:
                        if f.current_len >= leaf.h: leaf.is_growing = True
                        leaf.update()
                        total_leaf_scale = f.scale * leaf.current_scale
                        
                        if not leaf.is_growing and hasattr(leaf, 'cached_plist') and leaf.cached_scale == total_leaf_scale:
                            plist = leaf.cached_plist
                        else:
                            base_ang = math.atan2(float(ny - ly), float(nx - lx)) + (math.pi / 2) * leaf.ld
                            leng, wid = 35 * total_leaf_scale, 12 * total_leaf_scale
                            plist = []
                            
                            if leaf.leaf_type == 0:
                                tx, ty = int(nx + leng * math.cos(base_ang)), int(ny + leng * math.sin(base_ang))
                                mbx = nx + (leng * 0.4) * math.cos(base_ang)
                                mby = ny + (leng * 0.4) * math.sin(base_ang)
                                m1 = [int(mbx + wid * math.cos(base_ang + math.pi / 2)), int(mby + wid * math.sin(base_ang + math.pi / 2))]
                                m2 = [int(mbx + wid * math.cos(base_ang - math.pi / 2)), int(mby + wid * math.sin(base_ang - math.pi / 2))]
                                plist = [[nx, ny], m1, [tx, ty], m2]
                            else:
                                steps = 6
                                sin, cos, m_pi = math.sin, math.cos, math.pi
                                for step in range(steps + 1):
                                    t = step / float(steps)
                                    if leaf.leaf_type == 1:
                                        r = wid * 1.6 * (sin(t * m_pi) ** 0.5)
                                        if t < 0.15: r *= (t / 0.15) * 0.3
                                    elif leaf.leaf_type == 2:
                                        r = wid * 1.5 * math.sin(t * m_pi) * (1.3 - t)
                                        if t < 0.2: r *= (t / 0.2) * 0.5
                                    else:
                                        r = wid * 1.3 * sin(t * m_pi) + wid * 0.3 * sin(t * m_pi * 3)
                                    cx, cy = nx + leng * t * cos(base_ang), ny + leng * t * sin(base_ang)
                                    plist.append([int(cx - r * sin(base_ang)), int(cy + r * cos(base_ang))])
                                for step in range(steps, -1, -1):
                                    t = step / float(steps)
                                    if leaf.leaf_type == 1:
                                        r = wid * 1.6 * (sin(t * m_pi) ** 0.5)
                                        if t < 0.15: r *= (t / 0.15) * 0.3
                                    elif leaf.leaf_type == 2:
                                        r = wid * 1.5 * math.sin(t * m_pi) * (1.3 - t)
                                        if t < 0.2: r *= (t / 0.2) * 0.5
                                    else:
                                        r = wid * 1.3 * sin(t * m_pi) + wid * 0.3 * sin(t * m_pi * 3)
                                    cx, cy = nx + leng * t * cos(base_ang), ny + leng * t * sin(base_ang)
                                    plist.append([int(cx + r * sin(base_ang)), int(cy - r * cos(base_ang))])
                            if not leaf.is_growing:
                                leaf.cached_plist = plist
                                leaf.cached_scale = total_leaf_scale
                        if len(plist) > 2:
                            pygame.draw.polygon(screen, f.lc, plist)
                            pygame.draw.polygon(screen, f.sc, plist, max(1, int(1 * total_leaf_scale)))
                lx, ly = nx, ny
            blx, bly = lx, ly
            if f.has_b and f.current_len > f.bh:
                br_ratio = f.bh / f.max_len
                bx = int(f.x + (br_ratio * br_ratio) * 80.0 * f.dir * math.sin(br_ratio * math.pi * 0.5))
                by = int(f.y - f.bh)
                blx, bly = bx, by
                cur_blen = min((f.current_len - f.bh) * 0.8, f.b_ml)
                for j in range(0, int(cur_blen), 10):
                    b_ratio = j / f.b_ml
                    bnx, bny = int(bx + (b_ratio * b_ratio) * 65.0 * f.bd), int(by - j - 5)
                    pygame.draw.line(screen, f.sc, (blx, bly), (bnx, bny), max(1, w - 1))
                    blx, bly = bnx, bny

            tgs = [(lx, ly, f.p_count, f.p_type)]
            if f.has_b and f.current_len >= f.max_len: tgs.append((blx, bly, f.b_p, f.b_t))
            for hx, hy, pc, pt in tgs:
                pos_key = (hx, hy)
                if not f.is_bloomed:
                    pygame.draw.circle(screen, (120, 180, 80), (hx, hy), max(1, int(10 * f.scale)))
                else:
                    if f.scale > 0:
                        if f.petal_growth < 1.0:
                            f.petal_growth += (1.0 / 42.0)
                            if f.petal_growth > 1.0: f.petal_growth = 1.0

                        if f.petal_growth == 1.0 and pos_key in f.cached_petals:
                            pass 
                        else:
                            f.cached_petals[pos_key] = []
                            bl = f.g_len * f.scale * f.petal_growth
                            bw = f.g_wide * f.scale * f.petal_growth
                            bs = f.g_skew * f.scale * f.petal_growth
                            sin, cos, m_pi = math.sin, math.cos, math.pi
                            
                            for num in range(pc):
                                ba = (2 * m_pi / pc) * num
                                plist = []
                                for step in range(0, 13):
                                    t = step / 12.0
                                    if pt == 2: r = bw * sin(t * m_pi) * 0.5
                                    elif pt == 3: r = bw * (t * 2.0) * 0.6 if t < 0.5 else bw * ((1.0 - t) * 2.0) * 0.6
                                    elif pt == 1: r = bw * sin(t * m_pi) * (1.1 - t)
                                    elif pt == 4: r = bw * sin(t * m_pi) ** 0.5 * 1.2
                                    elif pt == 5: r = bw * sin(t * m_pi) * 0.35
                                    elif pt == 6: r = bw * (sin(t * m_pi) ** 0.7) * 0.45
                                    elif pt == 7: r = bw * t
                                    elif pt == 8: r = bw * (t * 2.0 if t < 0.5 else (1.0 - t) * 2.0) * 0.7
                                    elif pt == 9: r = bw * (t * 2.0 if t < 0.5 else (1.0 - t) * 3.5) * 0.2
                                    elif pt == 10:
                                        wave1 = sin(t * m_pi * (3.0 + f.dir))
                                        wave2 = cos(t * m_pi * (pc % 4 + 1.5))
                                        r = bw * (wave1 * 0.4 + wave2 * f.seed * 1.5) * sin(t * m_pi)
                                    else: r = bw * sin(t * m_pi)
                                    plist.append([int(hx + (bl * t * cos(ba) - (bs * t + r) * sin(ba))), int(hy + (bl * t * sin(ba) + (bs * t + r) * cos(ba)))])
                                for step in range(12, -1, -1):
                                    t = step / 12.0
                                    if pt == 2: r = bw * sin(t * m_pi) * 0.5
                                    elif pt == 3: r = bw * (t * 2.0) * 0.6 if t < 0.5 else bw * ((1.0 - t) * 2.0) * 0.6
                                    elif pt == 1: r = bw * sin(t * m_pi) * (1.1 - t)
                                    elif pt == 4: r = bw * sin(t * m_pi) ** 0.5 * 1.2
                                    elif pt == 5: r = bw * sin(t * m_pi) * 0.35
                                    elif pt == 6: r = bw * (sin(t * m_pi) ** 0.7) * 0.45
                                    elif pt == 7: r = bw * t
                                    elif pt == 8: r = bw * (t * 2.0 if t < 0.5 else (1.0 - t) * 2.0) * 0.7
                                    elif pt == 9: r = bw * (t * 2.0 if t < 0.5 else (1.0 - t) * 3.5) * 0.2
                                    elif pt == 10:
                                        wave1 = sin(t * m_pi * (3.0 + f.dir))
                                        wave2 = cos(t * m_pi * (pc % 4 + 1.5))
                                        r = bw * (wave1 * 0.4 + wave2 * f.seed * 1.5) * sin(t * m_pi)
                                    else: r = bw * sin(t * m_pi)
                                    plist.append([int(hx + (bl * t * cos(ba) - (bs * t - r) * sin(ba))), int(hy + (bl * t * sin(ba) + (bs * t - r) * cos(ba)))])
                                f.cached_petals[pos_key].append(plist)
                        if pos_key in f.cached_petals:
                            for plist in f.cached_petals[pos_key]:
                                if len(plist) > 2 and all(isinstance(pt, (list, tuple)) and len(pt) == 2 for pt in plist):
                                    if f.scale < 1.0:
                                        scaled_plist = []
                                        for px, py in plist:
                                            spx = int(hx + (px - hx) * f.scale)
                                            spy = int(hy + (py - hy) * f.scale)
                                            scaled_plist.append([spx, spy])
                                        pygame.draw.polygon(screen, f.color, scaled_plist)
                                    else:
                                        pygame.draw.polygon(screen, f.color, plist)
                        
                        # === 花芯の大きさを計算 ===
                        calculated_core_size = max(1, int(f.core_size * f.scale * f.petal_growth))
                        
                        # 遺伝システムによって一本化された美しいランダム花芯描画
                        pygame.draw.circle(screen, f.core_color, (hx, hy), calculated_core_size)

                        # ============================================================
                        # 【パワーアップ完成版】真ん中の丸を囲む小さな丸（葯・模様）の描画
                        # ============================================================
                        if calculated_core_size > 4:
                            dot_count = f.dot_count 
                            orbit_radius = calculated_core_size * f.dot_distance_factor 
                            dot_size = max(1, int(calculated_core_size * f.dot_size_factor)) 
                            
                            for d_num in range(dot_count):
                                dot_angle = (2 * math.pi / dot_count) * d_num
                                dot_x = int(hx + orbit_radius * math.cos(dot_angle))
                                dot_y = int(hy + orbit_radius * math.sin(dot_angle))
                                pygame.draw.circle(screen, f.dot_color, (dot_x, dot_y), dot_size)
                        # ============================================================

        # === UIボタン ===
        if saved_flower_data is None:
            pygame.draw.rect(screen, (200, 200, 200), btn_rect, 0, 5)
            txt = btn_font.render("No Flower", True, (120, 120, 120))
        else:
            pygame.draw.rect(screen, (50, 180, 100) if is_fixed_mode else (130, 95, 65), btn_rect, 0, 5)  
            txt = btn_font.render("Seed Fixed" if is_fixed_mode else "Fix Seed", True, (255, 255, 255))
        screen.blit(txt, (btn_rect.x + (btn_rect.width - txt.get_width()) // 2, btn_rect.y + (btn_rect.height - txt.get_height()) // 2))
                        
        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    pygame.init()
    scr = pygame.display.set_mode((info.current_w, info.current_h))
    font = pygame.font.Font(None, 64)
    while True:
        scr.fill((20, 10, 10))
        lines = traceback.format_exc().split("\n")
        y_offset = 40
        for line in lines[:20]:
            if not line.strip(): continue
            for start in range(0, len(line), 35):
                scr.blit(font.render(line[start:start+35], True, (255, 80, 80)), (40, y_offset))
                y_offset += 70
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit()
        pygame.display.flip()
