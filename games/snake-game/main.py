"""
╔══════════════════════════════════════════════════════════════════╗
║              SUPER SNAKE  –  A Feature-Rich Snake Game           ║
║                                                                  ║
║  Features:                                                       ║
║   • 4 Game Modes: Classic, Speed Run, Maze, Survival            ║
║   • Power-ups: Shield, Slow, Ghost, Magnet, Double Points       ║
║   • Particle system with explosions and trails                  ║
║   • Animated neon retro-futuristic visual theme                 ║
║   • Persistent high score & settings saved to disk              ║
║   • Level progression with increasing speed & obstacles         ║
║   • Sound effects generated procedurally (no files needed)      ║
║   • Pause menu, settings menu, achievements                     ║
║   • Snake skin / color customization                            ║
║   • Bonus food, poison food, moving food                        ║
║   • Wall-wrap toggle, obstacle toggle                           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pygame
import pygame.gfxdraw
import random
import math
import json
import os
import sys
import time
import colorsys
from collections import deque
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS & CONFIGURATION
# ══════════════════════════════════════════════════════════════════

WINDOW_W        = 900
WINDOW_H        = 660
GRID_COLS       = 40
GRID_ROWS       = 30
CELL            = 18          # pixel size of each grid cell
GRID_OFFSET_X   = (WINDOW_W - GRID_COLS * CELL) // 2
GRID_OFFSET_Y   = (WINDOW_H - GRID_ROWS * CELL) // 2 + 20
SIDEBAR_W       = GRID_OFFSET_X - 4

FPS             = 60
SAVE_FILE       = "snake_save.json"

# Speed (game-ticks per second the snake moves)
BASE_SPEED      = 8
MAX_SPEED       = 22
SPEED_PER_LEVEL = 1.4

# Points
PTS_FOOD        = 10
PTS_BONUS       = 30
PTS_POISON      = -15
PTS_LEVEL_BONUS = 100

# Food lifetimes (in game ticks)
BONUS_LIFETIME  = 120
MOVING_LIFETIME = 200

# Power-up durations (in game ticks)
POWERUP_DURATION = {
    "shield":  80,
    "slow":    60,
    "ghost":   70,
    "magnet":  90,
    "double":  100,
}

# ── Colour Palette ─────────────────────────────────────────────────
class C:
    # Backgrounds
    BG_DEEP     = (4,   6,  18)
    BG_PANEL    = (8,  12,  30)
    BG_GRID     = (12, 18,  42)
    GRID_LINE   = (18, 26,  58)

    # Neon accents
    NEON_GREEN  = (57, 255, 120)
    NEON_CYAN   = (0,  230, 255)
    NEON_PINK   = (255, 50, 180)
    NEON_YELLOW = (255, 230,  30)
    NEON_ORANGE = (255, 140,  20)
    NEON_PURPLE = (180,  50, 255)
    NEON_RED    = (255,  50,  50)

    # Snake skins
    SKINS = {
        "Classic":   [(57, 255, 120), (20, 180, 80)],
        "Cyber":     [(0,  230, 255), (0,  140, 200)],
        "Magma":     [(255, 140, 20), (200, 70, 10)],
        "Phantom":   [(180, 50, 255), (100, 20, 180)],
        "Blaze":     [(255, 50,  50), (180, 20, 20)],
        "Gold":      [(255, 220, 30), (180, 150, 10)],
    }

    # UI text
    TEXT_BRIGHT = (220, 235, 255)
    TEXT_MID    = (140, 160, 210)
    TEXT_DIM    = ( 70,  90, 140)

    # Food colours
    FOOD_RED    = (255,  70,  70)
    FOOD_GOLD   = (255, 215,   0)
    FOOD_POISON = ( 80, 200,  40)
    FOOD_MOVING = (255, 120, 200)

    # Power-up colours
    PU_SHIELD   = (80,  160, 255)
    PU_SLOW     = (150, 255, 150)
    PU_GHOST    = (200, 200, 255)
    PU_MAGNET   = (255, 180,  50)
    PU_DOUBLE   = (255,  50, 180)

    # Misc
    WHITE       = (255, 255, 255)
    BLACK       = (0,   0,   0)
    SHADOW      = (0,   0,   0, 120)

# ══════════════════════════════════════════════════════════════════
#  ENUMS
# ══════════════════════════════════════════════════════════════════

class Direction(Enum):
    UP    = (0, -1)
    DOWN  = (0,  1)
    LEFT  = (-1, 0)
    RIGHT = (1,  0)

class GameMode(Enum):
    CLASSIC   = "Classic"
    SPEEDRUN  = "Speed Run"
    MAZE      = "Maze"
    SURVIVAL  = "Survival"

class GameState(Enum):
    MENU        = auto()
    MODE_SELECT = auto()
    SKIN_SELECT = auto()
    SETTINGS    = auto()
    PLAYING     = auto()
    PAUSED      = auto()
    GAME_OVER   = auto()
    LEVEL_UP    = auto()
    ACHIEVEMENTS= auto()

class FoodType(Enum):
    NORMAL  = "normal"
    BONUS   = "bonus"
    POISON  = "poison"
    MOVING  = "moving"

class PowerUpType(Enum):
    SHIELD  = "shield"
    SLOW    = "slow"
    GHOST   = "ghost"
    MAGNET  = "magnet"
    DOUBLE  = "double"

# ══════════════════════════════════════════════════════════════════
#  DATA CLASSES
# ══════════════════════════════════════════════════════════════════

@dataclass
class Food:
    col: int
    row: int
    food_type: FoodType  = FoodType.NORMAL
    lifetime: int        = -1          # -1 = infinite
    dx: int              = 0
    dy: int              = 0
    move_timer: int      = 0
    move_interval: int   = 15
    pulse: float         = 0.0

    def grid_pos(self):
        return (self.col, self.row)

@dataclass
class PowerUp:
    col: int
    row: int
    pu_type: PowerUpType
    lifetime: int = 100
    pulse: float  = 0.0

    def grid_pos(self):
        return (self.col, self.row)

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float           # 0..1
    decay: float
    color: Tuple[int,int,int]
    size: float
    gravity: float = 0.0
    glow: bool     = False

@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    color: Tuple[int,int,int]
    life: float = 1.0
    decay: float = 0.025
    vy: float    = -1.2

@dataclass
class Achievement:
    key: str
    name: str
    desc: str
    unlocked: bool = False

# ══════════════════════════════════════════════════════════════════
#  SAVE / SETTINGS MANAGER
# ══════════════════════════════════════════════════════════════════

class SaveManager:
    DEFAULT = {
        "high_scores": {m.value: 0 for m in GameMode},
        "total_games": 0,
        "total_food":  0,
        "achievements": {},
        "settings": {
            "wall_wrap":    False,
            "obstacles":    True,
            "show_grid":    True,
            "skin":         "Classic",
            "sfx_volume":   0.6,
            "particle_fx":  True,
        }
    }

    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    loaded = json.load(f)
                # merge missing keys from DEFAULT
                for k, v in self.DEFAULT.items():
                    if k not in loaded:
                        loaded[k] = v
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            if kk not in loaded[k]:
                                loaded[k][kk] = vv
                return loaded
            except Exception:
                pass
        import copy
        return copy.deepcopy(self.DEFAULT)

    def save(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get_high_score(self, mode: GameMode) -> int:
        return self.data["high_scores"].get(mode.value, 0)

    def update_high_score(self, mode: GameMode, score: int):
        if score > self.get_high_score(mode):
            self.data["high_scores"][mode.value] = score
            self.save()

    @property
    def settings(self) -> dict:
        return self.data["settings"]

    def unlock_achievement(self, key: str):
        self.data["achievements"][key] = True
        self.save()

    def is_achieved(self, key: str) -> bool:
        return self.data["achievements"].get(key, False)

# ══════════════════════════════════════════════════════════════════
#  SOUND ENGINE  (procedurally generated, no files needed)
# ══════════════════════════════════════════════════════════════════

class SoundEngine:
    def __init__(self):
        self.enabled = True
        self.volume  = 0.6
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
            self._sounds = {
                "eat":      self._gen_eat(),
                "bonus":    self._gen_bonus(),
                "poison":   self._gen_poison(),
                "die":      self._gen_die(),
                "powerup":  self._gen_powerup(),
                "levelup":  self._gen_levelup(),
                "shield":   self._gen_shield_hit(),
            }
        except Exception:
            self.enabled = False
            self._sounds = {}

    def _make_wave(self, freq, duration, wave="sine",
                   attack=0.01, decay=0.1, vol=0.5) -> pygame.mixer.Sound:
        sample_rate = 44100
        n_samples   = int(sample_rate * duration)
        buf = []
        for i in range(n_samples):
            t   = i / sample_rate
            env = 1.0
            if t < attack:
                env = t / attack
            elif t > duration - decay:
                env = (duration - t) / decay
            if wave == "sine":
                s = math.sin(2 * math.pi * freq * t)
            elif wave == "square":
                s = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif wave == "saw":
                s = 2 * ((freq * t) % 1) - 1
            elif wave == "noise":
                s = random.uniform(-1, 1)
            else:
                s = math.sin(2 * math.pi * freq * t)
            buf.append(int(s * env * vol * 32767))
        raw = bytes(b for v in buf
                    for b in v.to_bytes(2, "little", signed=True))
        snd = pygame.mixer.Sound(buffer=raw)
        return snd

    def _gen_eat(self):
        return self._make_wave(880, 0.08, "sine", vol=0.4)

    def _gen_bonus(self):
        return self._make_wave(1200, 0.15, "sine", vol=0.5)

    def _gen_poison(self):
        return self._make_wave(200, 0.2, "saw", vol=0.4)

    def _gen_die(self):
        return self._make_wave(120, 0.4, "square", decay=0.3, vol=0.5)

    def _gen_powerup(self):
        return self._make_wave(660, 0.18, "sine", vol=0.45)

    def _gen_levelup(self):
        return self._make_wave(1047, 0.25, "sine", vol=0.5)

    def _gen_shield_hit(self):
        return self._make_wave(440, 0.12, "square", vol=0.3)

    def play(self, name: str):
        if not self.enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            snd.set_volume(self.volume)
            snd.play()

# ══════════════════════════════════════════════════════════════════
#  PARTICLE SYSTEM
# ══════════════════════════════════════════════════════════════════

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        self.texts:     List[FloatingText] = []
        self.enabled    = True

    def emit_explosion(self, x: float, y: float,
                       color: Tuple, count: int = 20, glow=True):
        if not self.enabled:
            return
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 5)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle)*speed,
                vy=math.sin(angle)*speed,
                life=1.0,
                decay=random.uniform(0.025, 0.06),
                color=color,
                size=random.uniform(2, 5),
                gravity=0.08,
                glow=glow,
            ))

    def emit_trail(self, x: float, y: float, color: Tuple, count: int = 3):
        if not self.enabled:
            return
        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.uniform(-4, 4),
                y=y + random.uniform(-4, 4),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                life=0.7,
                decay=random.uniform(0.04, 0.08),
                color=color,
                size=random.uniform(1, 3),
                glow=False,
            ))

    def emit_sparkle(self, x: float, y: float, color: Tuple, count: int = 8):
        if not self.enabled:
            return
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(0.5, 2.5)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle)*speed,
                vy=math.sin(angle)*speed,
                life=1.0,
                decay=random.uniform(0.03, 0.05),
                color=color,
                size=random.uniform(1, 2.5),
                glow=True,
            ))

    def add_text(self, text: str, x: float, y: float,
                 color: Tuple = C.NEON_YELLOW):
        self.texts.append(FloatingText(text=text, x=x, y=y, color=color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.x    += p.vx
            p.y    += p.vy
            p.vy   += p.gravity
            p.life -= p.decay
            p.size  = max(0, p.size - p.decay * 0.5)

        self.texts = [t for t in self.texts if t.life > 0]
        for t in self.texts:
            t.y    += t.vy
            t.life -= t.decay

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            alpha = int(p.life * 255)
            col   = tuple(min(255, int(c)) for c in p.color)
            sz    = max(1, int(p.size))
            if p.glow:
                # draw glow halo
                glow_surf = pygame.Surface((sz*6, sz*6), pygame.SRCALPHA)
                ga = max(0, int(alpha * 0.3))
                pygame.draw.circle(glow_surf, col+(ga,), (sz*3, sz*3), sz*3)
                surface.blit(glow_surf,
                             (int(p.x)-sz*3, int(p.y)-sz*3),
                             special_flags=pygame.BLEND_ADD)
            pygame.draw.circle(surface, col+(alpha,) if len(col)==3 else col,
                                (int(p.x), int(p.y)), sz)

        font = pygame.font.SysFont("consolas", 20, bold=True)
        for t in self.texts:
            alpha = int(t.life * 255)
            col   = t.color
            s     = font.render(t.text, True, col)
            s.set_alpha(alpha)
            surface.blit(s, (int(t.x - s.get_width()//2), int(t.y)))

# ══════════════════════════════════════════════════════════════════
#  MAZE GENERATOR  (for Maze mode)
# ══════════════════════════════════════════════════════════════════

class MazeGenerator:
    """Generates a random maze using recursive backtracking."""

    def __init__(self, cols: int, rows: int):
        self.cols  = cols
        self.rows  = rows

    def generate(self) -> List[Tuple[int,int]]:
        """Return a list of wall cell positions (col, row)."""
        # Work on half-resolution grid then scale
        mc = self.cols // 2
        mr = self.rows // 2
        visited = [[False]*mr for _ in range(mc)]
        walls_between = {}   # (c1,r1,c2,r2) -> True  means wall removed

        def carve(c, r):
            visited[c][r] = True
            dirs = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(dirs)
            for dc, dr in dirs:
                nc, nr = c+dc, r+dr
                if 0 <= nc < mc and 0 <= nr < mr and not visited[nc][nr]:
                    walls_between[(c,r,nc,nr)] = True
                    walls_between[(nc,nr,c,r)] = True
                    carve(nc, nr)

        carve(0, 0)

        # Convert maze to wall grid
        walls = set()
        for fc in range(self.cols):
            for fr in range(self.rows):
                walls.add((fc, fr))   # start with all walls

        for mc_c in range(mc):
            for mc_r in range(mr):
                # carve the cell itself
                real_c = mc_c * 2
                real_r = mc_r * 2
                walls.discard((real_c, real_r))
                # carve passages
                for dc, dr in [(0,1),(1,0)]:
                    nc, nr = mc_c+dc, mc_r+dr
                    if walls_between.get((mc_c,mc_r,nc,nr)):
                        walls.discard((real_c+dc, real_r+dr))
                        walls.discard((real_c+dc*2, real_r+dr*2))

        return list(walls)

# ══════════════════════════════════════════════════════════════════
#  OBSTACLE MANAGER
# ══════════════════════════════════════════════════════════════════

class ObstacleManager:
    def __init__(self):
        self.cells: set = set()

    def clear(self):
        self.cells = set()

    def generate_random(self, count: int, exclude: set):
        self.cells = set()
        attempts   = 0
        while len(self.cells) < count and attempts < count * 20:
            col = random.randint(2, GRID_COLS - 3)
            row = random.randint(2, GRID_ROWS - 3)
            if (col, row) not in exclude:
                self.cells.add((col, row))
            attempts += 1

    def generate_maze(self):
        gen = MazeGenerator(GRID_COLS, GRID_ROWS)
        self.cells = set(gen.generate())

    def __contains__(self, pos):
        return pos in self.cells

# ══════════════════════════════════════════════════════════════════
#  ACHIEVEMENT SYSTEM
# ══════════════════════════════════════════════════════════════════

ACHIEVEMENTS: List[Achievement] = [
    Achievement("first_blood",  "First Blood",     "Score your first point"),
    Achievement("century",      "Century",         "Reach score 100"),
    Achievement("speed_demon",  "Speed Demon",     "Reach level 5"),
    Achievement("glutton",      "Glutton",         "Eat 50 foods in one game"),
    Achievement("survivor",     "Survivor",        "Survive 2 min in Survival"),
    Achievement("bonus_hunter", "Bonus Hunter",    "Eat 10 bonus foods total"),
    Achievement("poison_dodger","Poison Dodger",   "Avoid poison 20 times"),
    Achievement("power_addict", "Power Addict",    "Collect 5 power-ups in one game"),
    Achievement("ghost_rider",  "Ghost Rider",     "Use Ghost power-up"),
    Achievement("collector",    "Collector",       "Unlock all skins"),
    Achievement("high_roller",  "High Roller",     "Score 500 in any mode"),
    Achievement("no_walls",     "Through the Wall","Use wall-wrap 10 times"),
]

# ══════════════════════════════════════════════════════════════════
#  DRAWING UTILITIES
# ══════════════════════════════════════════════════════════════════

class Draw:
    """Static helpers for drawing UI elements."""

    @staticmethod
    def grid_to_px(col: int, row: int) -> Tuple[int, int]:
        return (GRID_OFFSET_X + col * CELL, GRID_OFFSET_Y + row * CELL)

    @staticmethod
    def cell_center(col: int, row: int) -> Tuple[int, int]:
        x, y = Draw.grid_to_px(col, row)
        return (x + CELL // 2, y + CELL // 2)

    @staticmethod
    def neon_rect(surface, color, rect, width=2, glow_size=6, alpha=180):
        """Draw a rectangle with a neon glow effect."""
        gx, gy, gw, gh = (rect[0]-glow_size, rect[1]-glow_size,
                           rect[2]+glow_size*2, rect[3]+glow_size*2)
        glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, color+(alpha//3,),
                         (0, 0, gw, gh), border_radius=6)
        surface.blit(glow_surf, (gx, gy), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surface, color, rect, width, border_radius=4)

    @staticmethod
    def neon_circle(surface, color, center, radius, width=2, glow=True):
        if glow:
            gsurf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, color+(60,),
                               (radius*2, radius*2), radius*2)
            surface.blit(gsurf,
                         (center[0]-radius*2, center[1]-radius*2),
                         special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surface, color, center, radius, width)

    @staticmethod
    def gradient_rect(surface, color_top, color_bot, rect):
        r1,g1,b1 = color_top
        r2,g2,b2 = color_bot
        x, y, w, h = rect
        for i in range(h):
            t   = i / max(h-1, 1)
            col = (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))
            pygame.draw.line(surface, col, (x, y+i), (x+w, y+i))

    @staticmethod
    def text(surface, txt, font, color, cx, cy, anchor="center"):
        surf = font.render(txt, True, color)
        r    = surf.get_rect()
        if anchor == "center":
            r.center = (cx, cy)
        elif anchor == "midleft":
            r.midleft = (cx, cy)
        elif anchor == "midright":
            r.midright = (cx, cy)
        elif anchor == "topleft":
            r.topleft  = (cx, cy)
        surface.blit(surf, r)
        return r

    @staticmethod
    def shadowed_text(surface, txt, font, color, cx, cy):
        # shadow
        Draw.text(surface, txt, font, (0,0,0), cx+2, cy+2)
        return Draw.text(surface, txt, font, color, cx, cy)

    @staticmethod
    def panel(surface, rect, alpha=180, border_color=None):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        s.fill((*C.BG_PANEL, alpha))
        surface.blit(s, (rect[0], rect[1]))
        if border_color:
            pygame.draw.rect(surface, border_color, rect, 1, border_radius=4)

    @staticmethod
    def progress_bar(surface, rect, value, maximum, fg_color, bg_color=C.BG_GRID, border=True):
        x, y, w, h = rect
        pygame.draw.rect(surface, bg_color, rect, border_radius=3)
        fill_w = int(w * min(1, value / max(maximum, 1)))
        if fill_w > 0:
            pygame.draw.rect(surface, fg_color,
                             (x, y, fill_w, h), border_radius=3)
        if border:
            pygame.draw.rect(surface, C.TEXT_DIM, rect, 1, border_radius=3)


# ══════════════════════════════════════════════════════════════════
#  SNAKE  (the player entity)
# ══════════════════════════════════════════════════════════════════

class Snake:
    def __init__(self, skin: str = "Classic"):
        self.skin     = skin
        self.body     = deque()   # deque of (col, row)
        self.direction         = Direction.RIGHT
        self.next_direction    = Direction.RIGHT
        self.direction_queue: deque[Direction] = deque(maxlen=2)
        self.grew     = False
        self.alive    = True

        # Power-up state
        self.active_powerups: Dict[str, int] = {}   # name -> ticks_remaining
        self.wall_wrap_count = 0

        self.reset()

    def reset(self):
        self.body.clear()
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        for i in range(3):
            self.body.appendleft((cx - i, cy))
        self.direction       = Direction.RIGHT
        self.next_direction  = Direction.RIGHT
        self.direction_queue.clear()
        self.alive           = True
        self.active_powerups = {}
        self.wall_wrap_count = 0

    def queue_direction(self, d: Direction):
        """Queue a direction change, preventing reversal."""
        cur = self.direction_queue[-1] if self.direction_queue else self.direction
        if (d.value[0] != -cur.value[0] or d.value[1] != -cur.value[1]):
            self.direction_queue.append(d)

    def apply_queued_direction(self):
        if self.direction_queue:
            self.direction = self.direction_queue.popleft()

    def head(self) -> Tuple[int,int]:
        return self.body[0]

    def has_powerup(self, name: str) -> bool:
        return self.active_powerups.get(name, 0) > 0

    def give_powerup(self, name: str):
        self.active_powerups[name] = POWERUP_DURATION[name]

    def tick_powerups(self):
        expired = []
        for name in self.active_powerups:
            self.active_powerups[name] -= 1
            if self.active_powerups[name] <= 0:
                expired.append(name)
        for name in expired:
            del self.active_powerups[name]

    def move(self, grow: bool, wall_wrap: bool,
             obstacles: ObstacleManager) -> str:
        """
        Move snake one step.
        Returns: "ok" | "wall" | "self" | "obstacle"
        """
        self.apply_queued_direction()
        hc, hr = self.head()
        dc, dr = self.direction.value
        nc, nr = hc + dc, hr + dr

        # Boundary check
        if wall_wrap:
            if nc < 0:             nc = GRID_COLS - 1; self.wall_wrap_count += 1
            elif nc >= GRID_COLS:  nc = 0;             self.wall_wrap_count += 1
            if nr < 0:             nr = GRID_ROWS - 1; self.wall_wrap_count += 1
            elif nr >= GRID_ROWS:  nr = 0;             self.wall_wrap_count += 1
        else:
            if not (0 <= nc < GRID_COLS and 0 <= nr < GRID_ROWS):
                if self.has_powerup("ghost"):
                    nc = max(0, min(GRID_COLS-1, nc))
                    nr = max(0, min(GRID_ROWS-1, nr))
                else:
                    return "wall"

        new_head = (nc, nr)

        # Obstacle check
        if new_head in obstacles and not self.has_powerup("ghost"):
            return "obstacle"

        # Self-collision (ghost skips this)
        if not self.has_powerup("ghost"):
            body_set = set(self.body)
            if not grow:
                body_set.discard(list(self.body)[-1])
            if new_head in body_set:
                return "self"

        self.body.appendleft(new_head)
        if not grow:
            self.body.pop()

        return "ok"

    def get_head_color(self) -> Tuple:
        return C.SKINS.get(self.skin, C.SKINS["Classic"])[0]

    def get_body_color(self) -> Tuple:
        return C.SKINS.get(self.skin, C.SKINS["Classic"])[1]

    def length(self) -> int:
        return len(self.body)

    def body_set(self) -> set:
        return set(self.body)


# ══════════════════════════════════════════════════════════════════
#  GAME SESSION  (one round of play)
# ══════════════════════════════════════════════════════════════════

class GameSession:
    def __init__(self, mode: GameMode, settings: dict,
                 skin: str, sound: SoundEngine,
                 particles: ParticleSystem):
        self.mode      = mode
        self.settings  = settings
        self.skin      = skin
        self.sound     = sound
        self.particles = particles

        self.snake     = Snake(skin)
        self.obstacles = ObstacleManager()
        self.foods:     List[Food]    = []
        self.powerups:  List[PowerUp] = []

        self.score         = 0
        self.level         = 1
        self.foods_eaten   = 0
        self.bonus_eaten   = 0
        self.poison_dodged = 0
        self.powerups_collected = 0
        self.survival_ticks= 0

        self.tick          = 0
        self.move_timer    = 0.0
        self.move_interval = self._calc_move_interval()

        self.double_pts    = False
        self.level_up_pending = False
        self.just_died     = False

        self._setup()

    def _calc_move_interval(self) -> float:
        """Frames per snake move step."""
        speed = min(MAX_SPEED, BASE_SPEED + (self.level - 1) * SPEED_PER_LEVEL)
        if self.mode == GameMode.SPEEDRUN:
            speed *= 1.4
        if self.snake.has_powerup("slow"):
            speed *= 0.6
        return FPS / speed

    def _setup(self):
        self.obstacles.clear()
        if self.mode == GameMode.MAZE:
            self.obstacles.generate_maze()
            # ensure snake start area is clear
            for i in range(-2, 5):
                self.obstacles.cells.discard((GRID_COLS//2 + i, GRID_ROWS//2))
                self.obstacles.cells.discard((GRID_COLS//2 + i, GRID_ROWS//2-1))
                self.obstacles.cells.discard((GRID_COLS//2 + i, GRID_ROWS//2+1))
        elif self.settings.get("obstacles") and self.mode != GameMode.CLASSIC:
            self.obstacles.generate_random(
                count   = 8 + self.level * 2,
                exclude = set(self.snake.body)
            )
        self._spawn_food()

    def _spawn_food(self, food_type: FoodType = FoodType.NORMAL):
        occupied = self.snake.body_set() | self.obstacles.cells
        occupied |= {f.grid_pos() for f in self.foods}
        occupied |= {p.grid_pos() for p in self.powerups}

        for _ in range(200):
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in occupied:
                lt = -1
                dx, dy = 0, 0
                if food_type == FoodType.BONUS:
                    lt = BONUS_LIFETIME
                elif food_type == FoodType.MOVING:
                    lt = MOVING_LIFETIME
                    dx = random.choice([-1, 1])
                    dy = random.choice([-1, 1])
                f = Food(col=col, row=row, food_type=food_type,
                         lifetime=lt, dx=dx, dy=dy)
                self.foods.append(f)
                return

    def _spawn_powerup(self):
        occupied = self.snake.body_set() | self.obstacles.cells
        occupied |= {f.grid_pos() for f in self.foods}
        for _ in range(200):
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in occupied:
                pu_type = random.choice(list(PowerUpType))
                self.powerups.append(
                    PowerUp(col=col, row=row, pu_type=pu_type))
                return

    def _points_for(self, food: Food) -> int:
        base = {
            FoodType.NORMAL:  PTS_FOOD,
            FoodType.BONUS:   PTS_BONUS,
            FoodType.POISON:  PTS_POISON,
            FoodType.MOVING:  PTS_FOOD * 2,
        }.get(food.food_type, PTS_FOOD)
        if self.snake.has_powerup("double"):
            base *= 2
        return base

    def _check_level_up(self):
        threshold = self.level * 5   # foods per level
        if self.foods_eaten >= threshold:
            self.level += 1
            self.score += PTS_LEVEL_BONUS
            self.level_up_pending = True
            self.sound.play("levelup")
            # Respawn obstacles for new level
            if self.settings.get("obstacles") and self.mode not in (GameMode.MAZE, GameMode.CLASSIC):
                self.obstacles.generate_random(
                    count   = 8 + self.level * 2,
                    exclude = set(self.snake.body)
                )

    def update(self) -> Optional[str]:
        """
        Advance one frame.
        Returns None normally, or an event string:
          "level_up" | "died"
        """
        self.tick += 1
        self.survival_ticks += 1

        # Animate food/powerup pulses
        t = self.tick * 0.05
        for f in self.foods:
            f.pulse = math.sin(t + f.col * 0.3 + f.row * 0.5)
        for p in self.powerups:
            p.pulse = math.sin(t * 1.4 + p.col * 0.2)

        # Expire timed foods
        for f in self.foods:
            if f.lifetime > 0:
                f.lifetime -= 1
        self.foods = [f for f in self.foods if f.lifetime != 0]

        # Expire timed powerups on ground
        for p in self.powerups:
            p.lifetime -= 1
        self.powerups = [p for p in self.powerups if p.lifetime > 0]

        # Move moving foods
        for f in self.foods:
            if f.food_type == FoodType.MOVING:
                f.move_timer += 1
                if f.move_timer >= f.move_interval:
                    f.move_timer = 0
                    nc, nr = f.col + f.dx, f.row + f.dy
                    if 0 <= nc < GRID_COLS and 0 <= nr < GRID_ROWS \
                       and (nc, nr) not in self.obstacles.cells:
                        f.col, f.row = nc, nr
                    else:
                        f.dx = -f.dx
                        f.dy = -f.dy

        # Magnet: pull food closer
        if self.snake.has_powerup("magnet"):
            hc, hr = self.snake.head()
            for f in self.foods:
                if f.food_type == FoodType.NORMAL:
                    dc = hc - f.col
                    dr = hr - f.row
                    if abs(dc) + abs(dr) <= 6 and abs(dc) + abs(dr) > 0:
                        if abs(dc) >= abs(dr):
                            f.col += 1 if dc > 0 else -1
                        else:
                            f.row += 1 if dr > 0 else -1

        # Tick snake power-ups
        self.snake.tick_powerups()
        self.move_interval = self._calc_move_interval()

        # Spawn extra content periodically
        normal_food_count = sum(1 for f in self.foods
                                if f.food_type == FoodType.NORMAL)
        if normal_food_count == 0:
            self._spawn_food(FoodType.NORMAL)

        if self.tick % 120 == 0 and random.random() < 0.5:
            self._spawn_food(FoodType.BONUS)

        if self.tick % 100 == 0 and random.random() < 0.4 \
                and self.mode != GameMode.CLASSIC:
            self._spawn_food(FoodType.POISON)

        if self.mode == GameMode.SURVIVAL and self.tick % 90 == 0:
            self._spawn_food(FoodType.MOVING)

        if self.tick % 200 == 0 and random.random() < 0.35:
            self._spawn_powerup()

        # Snake movement
        self.move_timer += 1
        if self.move_timer < self.move_interval:
            return None
        self.move_timer = 0

        # Check if snake will eat food (grow flag)
        head_next = (
            self.snake.head()[0] + self.snake.direction_queue[0].value[0]
            if self.snake.direction_queue else
            self.snake.head()[0] + self.snake.direction.value[0],
        )
        # Determine grow before move
        next_hc = self.snake.head()[0] + (
            self.snake.direction_queue[0].value[0]
            if self.snake.direction_queue
            else self.snake.direction.value[0])
        next_hr = self.snake.head()[1] + (
            self.snake.direction_queue[0].value[1]
            if self.snake.direction_queue
            else self.snake.direction.value[1])
        # Will eat normal/bonus/moving food?
        grow_now = any(
            (f.col == next_hc and f.row == next_hr and
             f.food_type in (FoodType.NORMAL, FoodType.BONUS, FoodType.MOVING))
            for f in self.foods
        )

        wall_wrap = self.settings.get("wall_wrap", False)
        result    = self.snake.move(grow_now, wall_wrap, self.obstacles)

        hc, hr = self.snake.head()
        hx, hy = Draw.cell_center(hc, hr)

        # Trail particle
        self.particles.emit_trail(hx, hy,
                                  self.snake.get_head_color(), count=2)

        if result != "ok":
            # Shield absorbs one hit
            if self.snake.has_powerup("shield") and result in ("wall","self","obstacle"):
                del self.snake.active_powerups["shield"]
                self.sound.play("shield")
                self.particles.emit_explosion(hx, hy, C.PU_SHIELD, 15)
                self.particles.add_text("SHIELD!", hx, hy - 20, C.PU_SHIELD)
                return None
            # Ghost can pass through self/obstacles
            if self.snake.has_powerup("ghost") and result in ("self","obstacle"):
                return None
            # Dead
            self.sound.play("die")
            self.particles.emit_explosion(hx, hy,
                                          self.snake.get_head_color(), 40, glow=True)
            self.just_died = True
            self.snake.alive = False
            return "died"

        # ── Check food collisions ──────────────────────────────────
        eaten = None
        for f in self.foods:
            if (f.col, f.row) == (hc, hr):
                eaten = f
                break
        if eaten:
            pts = self._points_for(eaten)
            if eaten.food_type == FoodType.POISON:
                self.score = max(0, self.score + pts)
                self.sound.play("poison")
                self.particles.emit_explosion(hx, hy, C.FOOD_POISON, 12)
                self.particles.add_text(str(pts), hx, hy-20, C.FOOD_POISON)
                # Shrink snake by 3
                for _ in range(3):
                    if len(self.snake.body) > 1:
                        self.snake.body.pop()
            else:
                self.score += pts
                self.foods_eaten += 1
                if eaten.food_type == FoodType.BONUS:
                    self.bonus_eaten += 1
                    self.sound.play("bonus")
                    self.particles.emit_sparkle(hx, hy, C.FOOD_GOLD, 12)
                else:
                    self.sound.play("eat")
                    self.particles.emit_sparkle(hx, hy,
                                                self.snake.get_head_color(), 6)
                col = C.NEON_YELLOW if pts > PTS_FOOD else C.NEON_GREEN
                sign = "+" if pts >= 0 else ""
                self.particles.add_text(f"{sign}{pts}", hx, hy-20, col)
                self._check_level_up()
            self.foods.remove(eaten)
            if self.level_up_pending:
                self.level_up_pending = False
                return "level_up"

        # ── Check power-up collisions ──────────────────────────────
        for pu in self.powerups:
            if (pu.col, pu.row) == (hc, hr):
                self.snake.give_powerup(pu.pu_type.value)
                self.powerups_collected += 1
                self.sound.play("powerup")
                col = self._pu_color(pu.pu_type)
                self.particles.emit_sparkle(hx, hy, col, 14)
                label = pu.pu_type.value.upper()
                self.particles.add_text(label, hx, hy-30, col)
                self.powerups.remove(pu)
                break

        return None

    @staticmethod
    def _pu_color(pu_type: PowerUpType) -> Tuple:
        return {
            PowerUpType.SHIELD:  C.PU_SHIELD,
            PowerUpType.SLOW:    C.PU_SLOW,
            PowerUpType.GHOST:   C.PU_GHOST,
            PowerUpType.MAGNET:  C.PU_MAGNET,
            PowerUpType.DOUBLE:  C.PU_DOUBLE,
        }.get(pu_type, C.WHITE)


# ══════════════════════════════════════════════════════════════════
#  RENDERER
# ══════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.fonts   = {
            "title":  pygame.font.SysFont("consolas", 52, bold=True),
            "head":   pygame.font.SysFont("consolas", 32, bold=True),
            "mid":    pygame.font.SysFont("consolas", 22, bold=True),
            "small":  pygame.font.SysFont("consolas", 16),
            "tiny":   pygame.font.SysFont("consolas", 13),
            "hud":    pygame.font.SysFont("consolas", 20, bold=True),
        }
        self._star_field = self._gen_stars(120)
        self._star_timer = 0.0

    def _gen_stars(self, n: int) -> List[dict]:
        stars = []
        for _ in range(n):
            stars.append({
                "x": random.randint(0, WINDOW_W),
                "y": random.randint(0, WINDOW_H),
                "r": random.uniform(0.5, 2),
                "speed": random.uniform(0.01, 0.05),
                "phase": random.uniform(0, math.tau),
            })
        return stars

    def _draw_starfield(self, tick: int):
        t = tick * 0.02
        for s in self._star_field:
            alpha = int(140 + 80 * math.sin(t * s["speed"] * 10 + s["phase"]))
            alpha = max(40, min(220, alpha))
            col   = (alpha, alpha, min(255, alpha + 40))
            pygame.draw.circle(self.surface, col,
                               (int(s["x"]), int(s["y"])), max(1, int(s["r"])))

    def draw_background(self, tick: int):
        self.surface.fill(C.BG_DEEP)
        self._draw_starfield(tick)

    def draw_grid_area(self, show_grid: bool):
        # Grid background
        gx = GRID_OFFSET_X
        gy = GRID_OFFSET_Y
        gw = GRID_COLS * CELL
        gh = GRID_ROWS * CELL
        pygame.draw.rect(self.surface, C.BG_GRID, (gx, gy, gw, gh))

        if show_grid:
            for col in range(GRID_COLS + 1):
                x = gx + col * CELL
                pygame.draw.line(self.surface, C.GRID_LINE, (x, gy), (x, gy+gh))
            for row in range(GRID_ROWS + 1):
                y = gy + row * CELL
                pygame.draw.line(self.surface, C.GRID_LINE, (gx, y), (gx+gw, y))

        # Border glow
        Draw.neon_rect(self.surface, C.NEON_CYAN,
                       (gx, gy, gw, gh), width=2, glow_size=4)

    def draw_obstacles(self, obstacles: ObstacleManager, mode: GameMode, tick: int):
        gx = GRID_OFFSET_X
        gy = GRID_OFFSET_Y
        wall_col = C.NEON_PURPLE if mode == GameMode.MAZE else (80, 60, 130)
        for (col, row) in obstacles.cells:
            x = gx + col * CELL
            y = gy + row * CELL
            # gradient fill
            Draw.gradient_rect(self.surface, wall_col,
                               tuple(max(0,c-40) for c in wall_col),
                               (x+1, y+1, CELL-2, CELL-2))
            pygame.draw.rect(self.surface, wall_col, (x, y, CELL, CELL), 1)

    def draw_food(self, foods: List[Food], tick: int):
        gx = GRID_OFFSET_X
        gy = GRID_OFFSET_Y
        for f in foods:
            x  = gx + f.col * CELL
            y  = gy + f.row * CELL
            cx = x + CELL // 2
            cy = y + CELL // 2
            pulse = f.pulse
            r     = max(3, int(CELL // 2 - 1 + pulse))

            if f.food_type == FoodType.NORMAL:
                col = C.FOOD_RED
                # draw apple shape
                Draw.neon_circle(self.surface, col, (cx, cy), r, width=0)
                # shine
                pygame.draw.circle(self.surface, (255,180,180), (cx-2, cy-2), max(1,r//3))
                # stem
                pygame.draw.line(self.surface, C.NEON_GREEN,
                                 (cx, cy-r), (cx+2, cy-r-3), 2)

            elif f.food_type == FoodType.BONUS:
                col   = C.FOOD_GOLD
                angle = tick * 3
                points = []
                for i in range(5):
                    a = math.radians(angle + i * 72 - 90)
                    b = math.radians(angle + i * 72 + 36 - 90)
                    points.append((cx + int(r*math.cos(a)), cy + int(r*math.sin(a))))
                    points.append((cx + int((r//2)*math.cos(b)), cy + int((r//2)*math.sin(b))))
                if len(points) >= 3:
                    gsurf = pygame.Surface((CELL*2, CELL*2), pygame.SRCALPHA)
                    pygame.draw.polygon(gsurf, col+(160,), [
                        (px - x + CELL//2, py - y + CELL//2) for px,py in points])
                    self.surface.blit(gsurf, (x-CELL//2, y-CELL//2),
                                      special_flags=pygame.BLEND_ADD)
                    pygame.draw.polygon(self.surface, col, points)

            elif f.food_type == FoodType.POISON:
                col = C.FOOD_POISON
                # skull-ish: circle with X
                pygame.draw.circle(self.surface, col, (cx, cy), r)
                pygame.draw.line(self.surface, C.BG_DEEP,
                                 (cx-3, cy-3), (cx+3, cy+3), 2)
                pygame.draw.line(self.surface, C.BG_DEEP,
                                 (cx+3, cy-3), (cx-3, cy+3), 2)
                Draw.neon_circle(self.surface, col, (cx, cy), r, width=1)

            elif f.food_type == FoodType.MOVING:
                col = C.FOOD_MOVING
                # diamond
                pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
                pygame.draw.polygon(self.surface, col, pts)
                pygame.draw.polygon(self.surface, C.WHITE, pts, 1)

    def draw_powerups(self, powerups: List[PowerUp], tick: int):
        gx = GRID_OFFSET_X
        gy = GRID_OFFSET_Y
        icons = {
            PowerUpType.SHIELD: "S",
            PowerUpType.SLOW:   "~",
            PowerUpType.GHOST:  "G",
            PowerUpType.MAGNET: "M",
            PowerUpType.DOUBLE: "x2",
        }
        colors = {
            PowerUpType.SHIELD: C.PU_SHIELD,
            PowerUpType.SLOW:   C.PU_SLOW,
            PowerUpType.GHOST:  C.PU_GHOST,
            PowerUpType.MAGNET: C.PU_MAGNET,
            PowerUpType.DOUBLE: C.PU_DOUBLE,
        }
        font = self.fonts["tiny"]
        for p in powerups:
            x  = gx + p.col * CELL
            y  = gy + p.row * CELL
            cx = x + CELL // 2
            cy = y + CELL // 2
            col   = colors[p.pu_type]
            pulse = p.pulse
            r     = max(4, int(CELL//2 - 1 + pulse))

            # spinning hexagon
            angle = tick * 2
            pts   = []
            for i in range(6):
                a = math.radians(angle + i * 60)
                pts.append((cx + int(r*math.cos(a)), cy + int(r*math.sin(a))))
            if len(pts) >= 3:
                pygame.draw.polygon(self.surface, col, pts)
                pygame.draw.polygon(self.surface, C.WHITE, pts, 1)

            lbl = icons[p.pu_type]
            Draw.text(self.surface, lbl, font, C.BG_DEEP, cx, cy)

    def draw_snake(self, snake: Snake, tick: int):
        if not snake.alive and tick % 6 < 3:
            return   # blink on death
        body  = list(snake.body)
        n     = len(body)
        head_col = snake.get_head_color()
        body_col = snake.get_body_color()
        ghost    = snake.has_powerup("ghost")

        gx = GRID_OFFSET_X
        gy = GRID_OFFSET_Y

        for i, (col, row) in enumerate(body):
            x  = gx + col * CELL
            y  = gy + row * CELL
            is_head  = (i == 0)
            t_ratio  = i / max(n-1, 1)   # 0 at head, 1 at tail

            # Colour gradient head→tail
            r = int(head_col[0] + (body_col[0]-head_col[0])*t_ratio)
            g = int(head_col[1] + (body_col[1]-head_col[1])*t_ratio)
            b = int(head_col[2] + (body_col[2]-head_col[2])*t_ratio)
            col_rgb = (r, g, b)

            shrink = 0 if is_head else 2
            rect   = pygame.Rect(x+shrink, y+shrink,
                                 CELL-shrink*2, CELL-shrink*2)

            if ghost:
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((*col_rgb, 100))
                self.surface.blit(s, rect.topleft)
                pygame.draw.rect(self.surface, col_rgb, rect, 1, border_radius=3)
            else:
                pygame.draw.rect(self.surface, col_rgb, rect, border_radius=3)

            # Head details
            if is_head:
                dc, dr = snake.direction.value
                # eyes
                eye_offsets = {
                    Direction.RIGHT: [(11, 4), (11, 12)],
                    Direction.LEFT:  [(4,  4), (4,  12)],
                    Direction.UP:    [(4,  4), (12,  4)],
                    Direction.DOWN:  [(4, 12), (12, 12)],
                }
                for ex, ey in eye_offsets.get(snake.direction, [(11,4),(11,12)]):
                    pygame.draw.circle(self.surface, C.BG_DEEP,
                                       (x+ex, y+ey), 3)
                    pygame.draw.circle(self.surface, C.WHITE,
                                       (x+ex+1, y+ey-1), 1)

                # Active power-up glow on head
                for name, ticks in snake.active_powerups.items():
                    pu_col = {
                        "shield": C.PU_SHIELD, "slow": C.PU_SLOW,
                        "ghost":  C.PU_GHOST,  "magnet": C.PU_MAGNET,
                        "double": C.PU_DOUBLE,
                    }.get(name, C.WHITE)
                    gsurf = pygame.Surface((CELL*3, CELL*3), pygame.SRCALPHA)
                    a     = int(60 + 40*math.sin(tick*0.15))
                    pygame.draw.rect(gsurf, (*pu_col, a),
                                     (0, 0, CELL*3, CELL*3), border_radius=6)
                    self.surface.blit(gsurf, (x-CELL, y-CELL),
                                      special_flags=pygame.BLEND_ADD)

    def draw_hud(self, session: GameSession, tick: int):
        """Left and right sidebar HUD."""
        # ── Left sidebar ──────────────────────────────────────────
        lx  = 10
        font_h = self.fonts["hud"]
        font_s = self.fonts["small"]
        font_t = self.fonts["tiny"]

        # Score panel
        Draw.panel(self.surface, (lx, 40, SIDEBAR_W-10, 90), alpha=160,
                   border_color=C.NEON_CYAN)
        Draw.text(self.surface, "SCORE", font_s, C.TEXT_DIM, lx+10, 52, "topleft")
        Draw.shadowed_text(self.surface, str(session.score),
                           self.fonts["head"], C.NEON_YELLOW,
                           lx + (SIDEBAR_W-10)//2, 90)

        # Level
        Draw.panel(self.surface, (lx, 145, SIDEBAR_W-10, 55), alpha=160,
                   border_color=C.NEON_GREEN)
        Draw.text(self.surface, f"LEVEL  {session.level}", font_h, C.NEON_GREEN,
                  lx + (SIDEBAR_W-10)//2, 172)

        # Level progress bar
        foods_for_level  = session.level * 5
        foods_this_level = session.foods_eaten % foods_for_level if foods_for_level else 0
        Draw.progress_bar(self.surface,
                          (lx, 206, SIDEBAR_W-10, 8),
                          foods_this_level, foods_for_level,
                          C.NEON_GREEN)

        # Snake length
        Draw.text(self.surface, f"LENGTH: {session.snake.length()}",
                  font_s, C.TEXT_MID, lx+5, 225, "topleft")
        Draw.text(self.surface, f"EATEN:  {session.foods_eaten}",
                  font_s, C.TEXT_MID, lx+5, 243, "topleft")

        # Mode
        Draw.panel(self.surface, (lx, 270, SIDEBAR_W-10, 32), alpha=120)
        Draw.text(self.surface, session.mode.value, font_s, C.NEON_PINK,
                  lx + (SIDEBAR_W-10)//2, 286)

        # Power-ups active
        if session.snake.active_powerups:
            Draw.text(self.surface, "POWER-UPS", font_t, C.TEXT_DIM, lx+5, 315, "topleft")
            py = 330
            for name, ticks in session.snake.active_powerups.items():
                max_t = POWERUP_DURATION.get(name, 80)
                col   = {
                    "shield": C.PU_SHIELD, "slow": C.PU_SLOW,
                    "ghost":  C.PU_GHOST,  "magnet": C.PU_MAGNET,
                    "double": C.PU_DOUBLE,
                }.get(name, C.WHITE)
                Draw.text(self.surface, name.upper(), font_t, col, lx+5, py, "topleft")
                Draw.progress_bar(self.surface,
                                  (lx+55, py+2, SIDEBAR_W-70, 9),
                                  ticks, max_t, col)
                py += 18
                if py > WINDOW_H - 60:
                    break

        # Survival timer
        if session.mode == GameMode.SURVIVAL:
            secs = session.survival_ticks // FPS
            Draw.text(self.surface,
                      f"TIME: {secs//60:02d}:{secs%60:02d}",
                      font_s, C.NEON_ORANGE, lx+5, WINDOW_H-80, "topleft")

        # ── Right sidebar ─────────────────────────────────────────
        rx  = WINDOW_W - SIDEBAR_W + 4
        rw  = SIDEBAR_W - 14

        Draw.panel(self.surface, (rx, 40, rw, 55), alpha=150,
                   border_color=C.NEON_PINK)
        Draw.text(self.surface, "HI-SCORE", font_t, C.TEXT_DIM, rx+5, 50, "topleft")
        hi = session.score  # will be updated at end
        Draw.text(self.surface, str(hi), font_h, C.NEON_PINK,
                  rx + rw//2, 72)

        # Mini legend
        items = [
            (C.FOOD_RED,    "Food   +10"),
            (C.FOOD_GOLD,   "Bonus  +30"),
            (C.FOOD_POISON, "Poison -15"),
            (C.FOOD_MOVING, "Moving +20"),
        ]
        Draw.text(self.surface, "FOOD GUIDE", font_t, C.TEXT_DIM, rx+5, 110, "topleft")
        for i, (col, label) in enumerate(items):
            y = 125 + i * 16
            pygame.draw.circle(self.surface, col, (rx+10, y+6), 5)
            Draw.text(self.surface, label, font_t, C.TEXT_MID, rx+20, y, "topleft")

        # Power-up legend
        pus = [
            (C.PU_SHIELD, "S=Shield"),
            (C.PU_SLOW,   "~=Slow"),
            (C.PU_GHOST,  "G=Ghost"),
            (C.PU_MAGNET, "M=Magnet"),
            (C.PU_DOUBLE, "x2=Double"),
        ]
        Draw.text(self.surface, "POWER-UPS", font_t, C.TEXT_DIM, rx+5, 195, "topleft")
        for i, (col, label) in enumerate(pus):
            y = 210 + i * 16
            pygame.draw.rect(self.surface, col, (rx+5, y+2, 8, 8), border_radius=2)
            Draw.text(self.surface, label, font_t, C.TEXT_MID, rx+18, y, "topleft")

        # Wall-wrap / ghost status
        status_items = []
        if session.settings.get("wall_wrap"):
            status_items.append(("WRAP ON", C.NEON_CYAN))
        if session.snake.has_powerup("ghost"):
            status_items.append(("GHOST",   C.PU_GHOST))
        sy = WINDOW_H - 100
        for label, col in status_items:
            Draw.neon_rect(self.surface, col,
                           (rx+5, sy, rw-5, 22), width=1)
            Draw.text(self.surface, label, font_t, col, rx+5+rw//2, sy+11)
            sy += 26

        # Controls reminder
        ctrl_y = WINDOW_H - 55
        for line in ["ESC=Pause", "Arrows=Move"]:
            Draw.text(self.surface, line, font_t, C.TEXT_DIM,
                      rx + rw//2, ctrl_y)
            ctrl_y += 16

    def draw_game_title(self, tick: int):
        """Animated title bar."""
        t   = tick * 0.04
        col = self._hue_shift(C.NEON_CYAN, t)
        Draw.shadowed_text(self.surface, "SUPER SNAKE",
                           self.fonts["mid"], col,
                           WINDOW_W // 2, 16)

    @staticmethod
    def _hue_shift(base_col: Tuple, t: float) -> Tuple:
        h, s, v = colorsys.rgb_to_hsv(base_col[0]/255,
                                       base_col[1]/255,
                                       base_col[2]/255)
        h = (h + t * 0.05) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r*255), int(g*255), int(b*255))

    # ── Menu screens ──────────────────────────────────────────────

    def draw_main_menu(self, tick: int, options: List[str],
                       selected: int, hi_scores: dict):
        self.draw_background(tick)

        # Animated title
        t = tick * 0.03
        for i, ch in enumerate("SUPER SNAKE"):
            wave_y = int(8 * math.sin(t + i * 0.5))
            col    = self._hue_shift(C.NEON_GREEN, i * 0.08 + t)
            font   = self.fonts["title"]
            s      = font.render(ch, True, col)
            tx     = WINDOW_W//2 - len("SUPER SNAKE")*30//2 + i*30
            ty     = 90 + wave_y
            # shadow
            sh = font.render(ch, True, (0,0,0))
            self.surface.blit(sh, (tx+3, ty+3))
            self.surface.blit(s,  (tx, ty))

        # High scores strip
        hs_y = 170
        Draw.panel(self.surface, (WINDOW_W//2-200, hs_y, 400, 34), alpha=140)
        hs_text = "  ".join(f"{m.value}: {hi_scores.get(m.value,0)}"
                            for m in GameMode)
        Draw.text(self.surface, hs_text, self.fonts["tiny"], C.NEON_YELLOW,
                  WINDOW_W//2, hs_y+17)

        # Menu options
        for i, opt in enumerate(options):
            is_sel = (i == selected)
            y      = 230 + i * 52
            col    = C.NEON_CYAN if is_sel else C.TEXT_MID
            rect   = (WINDOW_W//2-120, y-18, 240, 38)
            if is_sel:
                Draw.panel(self.surface, rect, alpha=180, border_color=C.NEON_CYAN)
                pulse = int(4 * math.sin(tick * 0.12))
                pygame.draw.rect(self.surface, C.NEON_CYAN,
                                 (rect[0]-2+pulse, rect[1]-2,
                                  rect[2]+4, rect[3]+4), 2, border_radius=5)
            Draw.shadowed_text(self.surface, opt,
                               self.fonts["mid"], col,
                               WINDOW_W//2, y)

        Draw.text(self.surface,
                  "↑↓ Navigate   ENTER Select   ESC Quit",
                  self.fonts["tiny"], C.TEXT_DIM, WINDOW_W//2, WINDOW_H-20)

    def draw_mode_select(self, tick: int, modes: List[GameMode],
                         selected: int, descriptions: dict):
        self.draw_background(tick)
        Draw.shadowed_text(self.surface, "SELECT MODE",
                           self.fonts["head"], C.NEON_CYAN,
                           WINDOW_W//2, 60)

        for i, mode in enumerate(modes):
            is_sel = (i == selected)
            y      = 140 + i * 100
            col    = C.NEON_YELLOW if is_sel else C.TEXT_MID
            rect   = (WINDOW_W//2-220, y-25, 440, 80)
            alpha  = 190 if is_sel else 110
            border = C.NEON_YELLOW if is_sel else C.TEXT_DIM
            Draw.panel(self.surface, rect, alpha=alpha, border_color=border)
            Draw.text(self.surface, mode.value, self.fonts["mid"], col,
                      WINDOW_W//2, y)
            Draw.text(self.surface, descriptions.get(mode.value, ""),
                      self.fonts["small"], C.TEXT_DIM,
                      WINDOW_W//2, y+28)

        Draw.text(self.surface, "↑↓ Choose   ENTER Start   ESC Back",
                  self.fonts["tiny"], C.TEXT_DIM, WINDOW_W//2, WINDOW_H-20)

    def draw_skin_select(self, tick: int, skins: List[str],
                         selected: int, current: str):
        self.draw_background(tick)
        Draw.shadowed_text(self.surface, "CHOOSE SKIN",
                           self.fonts["head"], C.NEON_PINK,
                           WINDOW_W//2, 55)

        cols_per_row = 3
        for i, skin in enumerate(skins):
            row_i = i // cols_per_row
            col_i = i %  cols_per_row
            sx    = 180 + col_i * 190
            sy    = 140 + row_i * 140
            is_sel = (i == selected)
            head_c, body_c = C.SKINS.get(skin, [C.NEON_GREEN, C.NEON_GREEN])
            border = head_c if is_sel else C.TEXT_DIM
            alpha  = 180 if is_sel else 100
            Draw.panel(self.surface, (sx-70, sy-40, 140, 110), alpha=alpha,
                       border_color=border)

            # Mini snake preview
            seg_positions = [(sx + (2-j)*14, sy) for j in range(4)]
            for j, (px, py) in enumerate(seg_positions):
                c = head_c if j==0 else body_c
                pygame.draw.rect(self.surface, c,
                                 (px-6, py-6, 12, 12), border_radius=2)
            # Eyes on head
            pygame.draw.circle(self.surface, C.BG_DEEP,
                               (seg_positions[0][0]+3, seg_positions[0][1]-2), 2)

            Draw.text(self.surface, skin, self.fonts["small"],
                      head_c if is_sel else C.TEXT_MID,
                      sx, sy+28)
            if skin == current:
                Draw.text(self.surface, "✓", self.fonts["small"],
                          C.NEON_GREEN, sx+50, sy-30)

        Draw.text(self.surface, "←→↑↓ Choose   ENTER Select   ESC Back",
                  self.fonts["tiny"], C.TEXT_DIM, WINDOW_W//2, WINDOW_H-20)

    def draw_settings(self, tick: int, settings: dict,
                      options: List[dict], selected: int):
        self.draw_background(tick)
        Draw.shadowed_text(self.surface, "SETTINGS",
                           self.fonts["head"], C.NEON_ORANGE,
                           WINDOW_W//2, 60)

        for i, opt in enumerate(options):
            is_sel = (i == selected)
            y      = 150 + i * 60
            label  = opt["label"]
            key    = opt["key"]
            val    = settings.get(key)
            col    = C.NEON_ORANGE if is_sel else C.TEXT_MID

            rect   = (WINDOW_W//2-220, y-20, 440, 44)
            if is_sel:
                Draw.panel(self.surface, rect, alpha=170,
                           border_color=C.NEON_ORANGE)
            Draw.text(self.surface, label, self.fonts["small"], col,
                      WINDOW_W//2-100, y, "midleft")

            # Value display
            if isinstance(val, bool):
                v_text = "ON" if val else "OFF"
                v_col  = C.NEON_GREEN if val else C.NEON_RED
            elif isinstance(val, float):
                v_text = f"{int(val*100)}%"
                v_col  = C.NEON_CYAN
            else:
                v_text = str(val)
                v_col  = C.NEON_YELLOW
            Draw.text(self.surface, v_text, self.fonts["mid"], v_col,
                      WINDOW_W//2+100, y)

        Draw.text(self.surface,
                  "↑↓ Choose   ←→ / ENTER Toggle   ESC Back",
                  self.fonts["tiny"], C.TEXT_DIM, WINDOW_W//2, WINDOW_H-20)

    def draw_pause(self, tick: int):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 180))
        self.surface.blit(overlay, (0, 0))
        Draw.shadowed_text(self.surface, "PAUSED",
                           self.fonts["title"], C.NEON_CYAN,
                           WINDOW_W//2, WINDOW_H//2 - 60)
        Draw.text(self.surface, "ENTER / ESC  –  Resume",
                  self.fonts["mid"], C.TEXT_MID, WINDOW_W//2, WINDOW_H//2 + 10)
        Draw.text(self.surface, "Q  –  Quit to Menu",
                  self.fonts["mid"], C.TEXT_MID, WINDOW_W//2, WINDOW_H//2 + 50)

    def draw_game_over(self, tick: int, session: GameSession,
                       hi_score: int, new_record: bool):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 200))
        self.surface.blit(overlay, (0, 0))

        t = tick * 0.06
        col = (
            int(200 + 55*math.sin(t)),
            int(50  + 30*math.sin(t+1)),
            int(50  + 30*math.sin(t+2)),
        )
        Draw.shadowed_text(self.surface, "GAME OVER",
                           self.fonts["title"], col,
                           WINDOW_W//2, WINDOW_H//2 - 110)

        if new_record:
            rec_col = C.NEON_YELLOW
            pr = int(3 * math.sin(tick * 0.2))
            Draw.shadowed_text(self.surface, "★ NEW RECORD! ★",
                               self.fonts["mid"], rec_col,
                               WINDOW_W//2, WINDOW_H//2 - 60)

        stats = [
            (f"Score:    {session.score}", C.NEON_YELLOW),
            (f"Level:    {session.level}", C.NEON_GREEN),
            (f"Length:   {session.snake.length()}", C.NEON_CYAN),
            (f"Eaten:    {session.foods_eaten}", C.TEXT_BRIGHT),
            (f"Hi-Score: {hi_score}", C.NEON_PINK),
        ]
        for i, (line, lcol) in enumerate(stats):
            Draw.text(self.surface, line, self.fonts["small"], lcol,
                      WINDOW_W//2, WINDOW_H//2 - 20 + i * 26)

        Draw.text(self.surface, "ENTER  –  Play Again      Q  –  Menu",
                  self.fonts["mid"], C.TEXT_MID, WINDOW_W//2,
                  WINDOW_H//2 + 130)

    def draw_level_up(self, tick: int, level: int):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 160))
        self.surface.blit(overlay, (0, 0))
        t   = tick * 0.1
        col = self._hue_shift(C.NEON_YELLOW, t)
        scale_val = 1.0 + 0.1 * math.sin(t * 3)
        Draw.shadowed_text(self.surface, f"LEVEL  {level}",
                           self.fonts["title"], col,
                           WINDOW_W//2, WINDOW_H//2 - 40)
        Draw.text(self.surface, f"+{PTS_LEVEL_BONUS} BONUS POINTS",
                  self.fonts["mid"], C.NEON_GREEN,
                  WINDOW_W//2, WINDOW_H//2 + 30)

    def draw_achievements(self, tick: int, achievements: List[Achievement],
                          save: SaveManager, selected: int):
        self.draw_background(tick)
        Draw.shadowed_text(self.surface, "ACHIEVEMENTS",
                           self.fonts["head"], C.NEON_YELLOW,
                           WINDOW_W//2, 55)
        per_page = 8
        page     = selected // per_page
        start    = page * per_page
        shown    = achievements[start: start+per_page]
        for i, ach in enumerate(shown):
            is_sel   = (start + i == selected)
            unlocked = save.is_achieved(ach.key)
            y        = 110 + i * 62
            col      = C.NEON_YELLOW if unlocked else C.TEXT_DIM
            border   = C.NEON_YELLOW if (is_sel and unlocked) else (
                       C.TEXT_DIM if not is_sel else C.NEON_CYAN)
            Draw.panel(self.surface, (50, y-22, WINDOW_W-100, 50),
                       alpha=140, border_color=border)
            icon = "★" if unlocked else "○"
            Draw.text(self.surface, icon, self.fonts["mid"], col, 80, y)
            Draw.text(self.surface, ach.name, self.fonts["small"], col, 110, y-8, "topleft")
            Draw.text(self.surface, ach.desc, self.fonts["tiny"], C.TEXT_DIM,
                      110, y+10, "topleft")

        page_text = f"Page {page+1}/{math.ceil(len(achievements)/per_page)}"
        Draw.text(self.surface, page_text, self.fonts["tiny"], C.TEXT_DIM,
                  WINDOW_W//2, WINDOW_H-35)
        Draw.text(self.surface, "↑↓ Scroll   ESC Back",
                  self.fonts["tiny"], C.TEXT_DIM, WINDOW_W//2, WINDOW_H-18)


# ══════════════════════════════════════════════════════════════════
#  ACHIEVEMENT CHECKER
# ══════════════════════════════════════════════════════════════════

class AchievementChecker:
    def __init__(self, save: SaveManager, particles: ParticleSystem,
                 renderer: Renderer):
        self.save      = save
        self.particles = particles
        self.renderer  = renderer
        self._queue: List[Achievement] = []

    def check(self, session: GameSession):
        checks = {
            "first_blood":  session.score > 0,
            "century":      session.score >= 100,
            "speed_demon":  session.level >= 5,
            "glutton":      session.foods_eaten >= 50,
            "survivor":     (session.mode == GameMode.SURVIVAL and
                             session.survival_ticks >= 120*FPS),
            "bonus_hunter": session.bonus_eaten >= 10,
            "power_addict": session.powerups_collected >= 5,
            "ghost_rider":  session.snake.has_powerup("ghost"),
            "high_roller":  session.score >= 500,
            "no_walls":     session.snake.wall_wrap_count >= 10,
        }
        for key, cond in checks.items():
            if cond and not self.save.is_achieved(key):
                self.save.unlock_achievement(key)
                ach = next((a for a in ACHIEVEMENTS if a.key == key), None)
                if ach:
                    self._queue.append(ach)

    def pop_notification(self) -> Optional[Achievement]:
        if self._queue:
            return self._queue.pop(0)
        return None

@dataclass
class AchievementNotification:
    ach: Achievement
    timer: int = 180   # frames to show

# ══════════════════════════════════════════════════════════════════
#  MAIN GAME  (state machine)
# ══════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Super Snake")
        try:
            pygame.display.set_icon(self._make_icon())
        except Exception:
            pass
        self.clock   = pygame.time.Clock()
        self.tick    = 0

        self.save      = SaveManager()
        self.sound     = SoundEngine()
        self.particles = ParticleSystem()
        self.renderer  = Renderer(self.screen)
        self.ach_checker = None  # set per session

        self.state     = GameState.MENU
        self.session: Optional[GameSession] = None
        self.selected_mode  = GameMode.CLASSIC
        self.selected_skin  = self.save.settings.get("skin", "Classic")

        # Menu navigation
        self.menu_sel   = 0
        self.mode_sel   = 0
        self.skin_sel   = list(C.SKINS.keys()).index(self.selected_skin)
        self.settings_sel = 0
        self.ach_sel    = 0

        self.menu_options = ["Play", "Mode", "Skin", "Settings",
                             "Achievements", "Quit"]
        self.mode_descriptions = {
            GameMode.CLASSIC.value:  "No obstacles. Classic gameplay. Wall = death.",
            GameMode.SPEEDRUN.value: "40% faster. Race for the high score!",
            GameMode.MAZE.value:     "Navigate a maze. Ghost power-up recommended.",
            GameMode.SURVIVAL.value: "Moving food, obstacles grow. Survive!",
        }
        self.settings_options = [
            {"label": "Wall Wrap",     "key": "wall_wrap"},
            {"label": "Obstacles",     "key": "obstacles"},
            {"label": "Show Grid",     "key": "show_grid"},
            {"label": "Particles",     "key": "particle_fx"},
            {"label": "SFX Volume",    "key": "sfx_volume"},
        ]

        self.level_up_timer    = 0
        self.new_record        = False
        self.ach_notifications: List[AchievementNotification] = []

    def _make_icon(self) -> pygame.Surface:
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        col  = C.NEON_GREEN
        for i, (cx, cy) in enumerate([(24,16),(18,16),(12,16),(6,16)]):
            c = col if i==0 else C.SKINS["Classic"][1]
            pygame.draw.rect(icon, c, (cx-5, cy-5, 10, 10), border_radius=2)
        return icon

    # ── Event handling ────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key):
        S = GameState
        if self.state == S.MENU:
            self._menu_key(key)
        elif self.state == S.MODE_SELECT:
            self._mode_key(key)
        elif self.state == S.SKIN_SELECT:
            self._skin_key(key)
        elif self.state == S.SETTINGS:
            self._settings_key(key)
        elif self.state == S.PLAYING:
            self._playing_key(key)
        elif self.state == S.PAUSED:
            self._paused_key(key)
        elif self.state == S.GAME_OVER:
            self._game_over_key(key)
        elif self.state == S.LEVEL_UP:
            pass  # auto-advance
        elif self.state == S.ACHIEVEMENTS:
            self._achievements_key(key)

    def _menu_key(self, key):
        n = len(self.menu_options)
        if key == pygame.K_UP:
            self.menu_sel = (self.menu_sel - 1) % n
        elif key == pygame.K_DOWN:
            self.menu_sel = (self.menu_sel + 1) % n
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            opt = self.menu_options[self.menu_sel]
            if opt == "Play":
                self._start_game()
            elif opt == "Mode":
                self.state = GameState.MODE_SELECT
            elif opt == "Skin":
                self.state = GameState.SKIN_SELECT
            elif opt == "Settings":
                self.state = GameState.SETTINGS
            elif opt == "Achievements":
                self.state = GameState.ACHIEVEMENTS
            elif opt == "Quit":
                self.quit_game()
        elif key == pygame.K_ESCAPE:
            self.quit_game()

    def _mode_key(self, key):
        modes = list(GameMode)
        n     = len(modes)
        if key == pygame.K_UP:
            self.mode_sel = (self.mode_sel - 1) % n
        elif key == pygame.K_DOWN:
            self.mode_sel = (self.mode_sel + 1) % n
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.selected_mode = modes[self.mode_sel]
            self.state = GameState.MENU
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def _skin_key(self, key):
        skins = list(C.SKINS.keys())
        n     = len(skins)
        cols  = 3
        if key == pygame.K_LEFT:
            self.skin_sel = (self.skin_sel - 1) % n
        elif key == pygame.K_RIGHT:
            self.skin_sel = (self.skin_sel + 1) % n
        elif key == pygame.K_UP:
            self.skin_sel = (self.skin_sel - cols) % n
        elif key == pygame.K_DOWN:
            self.skin_sel = (self.skin_sel + cols) % n
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.selected_skin = skins[self.skin_sel]
            self.save.settings["skin"] = self.selected_skin
            self.save.save()
            self.state = GameState.MENU
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def _settings_key(self, key):
        n   = len(self.settings_options)
        opt = self.settings_options[self.settings_sel]
        sk  = opt["key"]
        if key == pygame.K_UP:
            self.settings_sel = (self.settings_sel - 1) % n
        elif key == pygame.K_DOWN:
            self.settings_sel = (self.settings_sel + 1) % n
        elif key in (pygame.K_RETURN, pygame.K_LEFT, pygame.K_RIGHT):
            val = self.save.settings.get(sk)
            if isinstance(val, bool):
                self.save.settings[sk] = not val
            elif isinstance(val, float):
                step = 0.1 if key == pygame.K_RIGHT else -0.1
                self.save.settings[sk] = round(max(0, min(1, val+step)), 1)
            self.save.save()
            # Apply volume immediately
            self.sound.volume = self.save.settings.get("sfx_volume", 0.6)
            self.particles.enabled = self.save.settings.get("particle_fx", True)
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def _playing_key(self, key):
        snake = self.session.snake
        dir_map = {
            pygame.K_UP:    Direction.UP,
            pygame.K_DOWN:  Direction.DOWN,
            pygame.K_LEFT:  Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_w:     Direction.UP,
            pygame.K_s:     Direction.DOWN,
            pygame.K_a:     Direction.LEFT,
            pygame.K_d:     Direction.RIGHT,
        }
        if key in dir_map:
            snake.queue_direction(dir_map[key])
        elif key == pygame.K_ESCAPE or key == pygame.K_p:
            self.state = GameState.PAUSED
        elif key == pygame.K_F1:
            # debug: force level up
            self.session.level += 1

    def _paused_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN):
            self.state = GameState.PLAYING
        elif key == pygame.K_q:
            self.state = GameState.MENU

    def _game_over_key(self, key):
        if key == pygame.K_RETURN:
            self._start_game()
        elif key == pygame.K_q:
            self.state = GameState.MENU

    def _achievements_key(self, key):
        n = len(ACHIEVEMENTS)
        if key == pygame.K_UP:
            self.ach_sel = max(0, self.ach_sel - 1)
        elif key == pygame.K_DOWN:
            self.ach_sel = min(n-1, self.ach_sel + 1)
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    # ── Game lifecycle ────────────────────────────────────────────

    def _start_game(self):
        self.save.data["total_games"] += 1
        settings = dict(self.save.settings)
        self.session = GameSession(
            mode      = self.selected_mode,
            settings  = settings,
            skin      = self.selected_skin,
            sound     = self.sound,
            particles = self.particles,
        )
        self.particles.enabled = settings.get("particle_fx", True)
        self.sound.volume = settings.get("sfx_volume", 0.6)
        self.ach_checker = AchievementChecker(self.save, self.particles, self.renderer)
        self.new_record  = False
        self.state       = GameState.PLAYING
        self.level_up_timer = 0

    def _end_game(self):
        mode  = self.session.mode
        score = self.session.score
        hi    = self.save.get_high_score(mode)
        if score > hi:
            self.new_record = True
            self.save.update_high_score(mode, score)
        self.save.data["total_food"] += self.session.foods_eaten
        self.save.save()
        self.state = GameState.GAME_OVER

    # ── Update ────────────────────────────────────────────────────

    def update(self):
        self.tick += 1
        self.particles.update()

        # Tick achievement notifications
        self.ach_notifications = [n for n in self.ach_notifications
                                  if n.timer > 0]
        for n in self.ach_notifications:
            n.timer -= 1

        if self.state == GameState.PLAYING and self.session:
            result = self.session.update()

            # Check achievements
            self.ach_checker.check(self.session)
            notif = self.ach_checker.pop_notification()
            if notif:
                self.ach_notifications.append(AchievementNotification(notif))

            if result == "died":
                self._end_game()
            elif result == "level_up":
                self.state         = GameState.LEVEL_UP
                self.level_up_timer = 90   # frames to show level up screen

        elif self.state == GameState.LEVEL_UP:
            self.level_up_timer -= 1
            if self.level_up_timer <= 0:
                self.state = GameState.PLAYING
                # Spawn fresh food for new level
                self.session._spawn_food(FoodType.NORMAL)

    # ── Draw ──────────────────────────────────────────────────────

    def draw(self):
        R  = self.renderer
        S  = GameState
        t  = self.tick

        if self.state == S.MENU:
            R.draw_main_menu(t, self.menu_options, self.menu_sel,
                             self.save.data["high_scores"])

        elif self.state == S.MODE_SELECT:
            R.draw_mode_select(t, list(GameMode), self.mode_sel,
                               self.mode_descriptions)

        elif self.state == S.SKIN_SELECT:
            R.draw_skin_select(t, list(C.SKINS.keys()), self.skin_sel,
                               self.selected_skin)

        elif self.state == S.SETTINGS:
            R.draw_settings(t, self.save.settings,
                            self.settings_options, self.settings_sel)

        elif self.state == S.ACHIEVEMENTS:
            R.draw_achievements(t, ACHIEVEMENTS, self.save, self.ach_sel)

        elif self.state in (S.PLAYING, S.LEVEL_UP):
            sess = self.session
            R.draw_background(t)
            R.draw_grid_area(sess.settings.get("show_grid", True))
            R.draw_obstacles(sess.obstacles, sess.mode, t)
            R.draw_food(sess.foods, t)
            R.draw_powerups(sess.powerups, t)
            R.draw_snake(sess.snake, t)
            self.particles.draw(self.screen)
            R.draw_hud(sess, t)
            R.draw_game_title(t)

            if self.state == S.LEVEL_UP:
                R.draw_level_up(t, sess.level)

        elif self.state == S.PAUSED:
            sess = self.session
            R.draw_background(t)
            R.draw_grid_area(sess.settings.get("show_grid", True))
            R.draw_obstacles(sess.obstacles, sess.mode, t)
            R.draw_food(sess.foods, t)
            R.draw_snake(sess.snake, t)
            R.draw_hud(sess, t)
            R.draw_pause(t)

        elif self.state == S.GAME_OVER:
            sess = self.session
            R.draw_background(t)
            R.draw_grid_area(sess.settings.get("show_grid", True))
            R.draw_snake(sess.snake, t)
            self.particles.draw(self.screen)
            R.draw_game_over(t, sess,
                             self.save.get_high_score(sess.mode),
                             self.new_record)

        # Achievement notifications (overlay on any state)
        self._draw_ach_notifications()

        pygame.display.flip()

    def _draw_ach_notifications(self):
        if not self.ach_notifications:
            return
        notif = self.ach_notifications[0]
        alpha = min(255, notif.timer * 4) if notif.timer < 60 else 255
        bx    = WINDOW_W - 310
        by    = 10
        bw    = 300
        bh    = 55
        panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
        panel.fill((*C.BG_PANEL, alpha))
        self.screen.blit(panel, (bx, by))
        pygame.draw.rect(self.screen, C.NEON_YELLOW,
                         (bx, by, bw, bh), 1, border_radius=4)
        f_s = self.renderer.fonts["small"]
        f_t = self.renderer.fonts["tiny"]
        s1  = f_s.render("★ ACHIEVEMENT", True, C.NEON_YELLOW)
        s1.set_alpha(alpha)
        self.screen.blit(s1, (bx+8, by+5))
        s2  = f_t.render(notif.ach.name, True, C.TEXT_BRIGHT)
        s2.set_alpha(alpha)
        self.screen.blit(s2, (bx+8, by+26))
        s3  = f_t.render(notif.ach.desc, True, C.TEXT_DIM)
        s3.set_alpha(alpha)
        self.screen.blit(s3, (bx+8, by+40))

    # ── Main loop ─────────────────────────────────────────────────

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def quit_game(self):
        self.save.save()
        pygame.quit()
        sys.exit()


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    game = Game()
    game.run()
