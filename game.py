"""
DDR Bomb - Juego estilo Dance Dance Revolution hecho con pygame.
DDR Bomb - Dance Dance Revolution style rhythm game made with pygame.

Las flechas caen desde arriba y el jugador debe pulsar la flecha del teclado
correspondiente cuando coincidan con sus flechas MORADAS (zona de pulsación).
Cuidado con las flechas BOMBA: si las pulsas, pierdes la partida.

Controles: flechas del teclado (izquierda, abajo, arriba, derecha).
Soporte bilingüe: English / Español (seleccionable al inicio).
"""

import random
import sys
import math

import pygame

# ----------------------------------------------------------------------------
# Configuración general / General settings
# ----------------------------------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60

NUM_LANES = 4
LANE_WIDTH = 110
FIELD_LEFT = (SCREEN_WIDTH - NUM_LANES * LANE_WIDTH) // 2
LANE_CENTERS = [FIELD_LEFT + LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(NUM_LANES)]

TARGET_Y = SCREEN_HEIGHT - 130      # Altura de las flechas moradas del jugador
PERFECT_WINDOW = 25                 # Distancia (px) para un acierto perfecto
GOOD_WINDOW = 75                    # Distancia (px) máxima para acertar
ARROW_SIZE = 40

START_LIVES = 3

# Dirección de cada carril: 0 izquierda, 1 abajo, 2 arriba, 3 derecha
LANE_ANGLES = [270, 180, 0, 90]     # Ángulo de giro de una flecha "hacia arriba"
KEY_TO_LANE = {
    pygame.K_LEFT: 0,
    pygame.K_DOWN: 1,
    pygame.K_UP: 2,
    pygame.K_RIGHT: 3,
}

# Colores
BG_COLOR = (14, 12, 30)
LANE_COLOR = (24, 22, 48)
LANE_LINE = (50, 46, 90)
PURPLE = (150, 60, 230)             # Flechas del jugador (MORADO)
PURPLE_LIGHT = (205, 140, 255)
WHITE = (245, 245, 250)
GREY = (150, 150, 175)
RED = (235, 55, 70)
BOMB_BODY = (30, 30, 38)
YELLOW = (255, 215, 90)
GREEN = (110, 235, 170)
ARROW_COLORS = [
    (80, 200, 255),     # izquierda - azul claro
    (110, 235, 170),    # abajo - verde
    (255, 215, 90),     # arriba - amarillo
    (255, 130, 110),    # derecha - coral
]

# Estados del juego / Game states
STATE_LANGUAGE = "language"
STATE_WELCOME = "welcome"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Idiomas disponibles (English arriba, Español abajo)
LANG_OPTIONS = [
    ("English", "en"),
    ("Español", "es"),
]

TEXTS = {
    "en": {
        "title": "DDR BOMB",
        "welcome_instruction_1": "Press arrows when they match the purple targets",
        "welcome_instruction_2": "Do NOT press the bomb arrows!",
        "welcome_controls": "Controls: ← ↓ ↑ →   ·   ESC: exit   ·   L: change language",
        "welcome_start": "Press any key to start",
        "score_label": "Score",
        "level_label": "Level",
        "combo_label": "Combo",
        "feedback_too_early": "Too early!",
        "feedback_perfect": "PERFECT!",
        "feedback_good": "Good!",
        "feedback_level": "LEVEL {level}!",
        "feedback_bomb_dodged": "Bomb dodged! +25",
        "feedback_miss": "MISS!",
        "reason_bomb": "You pressed a bomb arrow!",
        "reason_lives": "You ran out of lives",
        "game_over_title": "GAME OVER",
        "game_over_final_score": "Final score: {score}",
        "game_over_best_score": "Best score: {best_score}",
        "game_over_stats": "Max combo: {max_combo}   ·   Level reached: {level}",
        "game_over_restart": "ENTER / SPACE: play again",
        "game_over_lang": "L: change language",
        "game_over_exit": "ESC: exit",
        "lang_title": "SELECT LANGUAGE",
        "lang_subtitle": "Choose your language / Elige tu idioma",
        "lang_hint_keys": "Use  ↑ / ↓  to select,  ENTER  to confirm",
        "lang_hint_quick": "Quick keys: [1] English   ·   [2] Español",
        "lang_hint_esc": "ESC: exit",
    },
    "es": {
        "title": "DDR BOMB",
        "welcome_instruction_1": "Pulsa las flechas cuando coincidan con las moradas",
        "welcome_instruction_2": "¡Pero NO pulses las flechas bomba!",
        "welcome_controls": "Controles: ← ↓ ↑ →   ·   ESC: salir   ·   L: cambiar idioma",
        "welcome_start": "Pulsa cualquier tecla para empezar",
        "score_label": "Puntos",
        "level_label": "Nivel",
        "combo_label": "Combo",
        "feedback_too_early": "¡Demasiado pronto!",
        "feedback_perfect": "¡PERFECTO!",
        "feedback_good": "¡Bien!",
        "feedback_level": "¡NIVEL {level}!",
        "feedback_bomb_dodged": "¡Bomba esquivada! +25",
        "feedback_miss": "¡FALLO!",
        "reason_bomb": "¡Has pulsado una flecha bomba!",
        "reason_lives": "Te has quedado sin vidas",
        "game_over_title": "FIN DEL JUEGO",
        "game_over_final_score": "Puntuación final: {score}",
        "game_over_best_score": "Mejor puntuación: {best_score}",
        "game_over_stats": "Mayor combo: {max_combo}   ·   Nivel alcanzado: {level}",
        "game_over_restart": "ENTER / ESPACIO: jugar de nuevo",
        "game_over_lang": "L: cambiar idioma",
        "game_over_exit": "ESC: salir",
        "lang_title": "SELECCIONAR IDIOMA",
        "lang_subtitle": "Choose your language / Elige tu idioma",
        "lang_hint_keys": "Usa  ↑ / ↓  para elegir,  ENTER  para confirmar",
        "lang_hint_quick": "Teclas directas: [1] English   ·   [2] Español",
        "lang_hint_esc": "ESC: salir",
    },
}


# ----------------------------------------------------------------------------
# Dibujo de flechas / Arrow rendering
# ----------------------------------------------------------------------------
def arrow_points(cx, cy, lane, size):
    """Devuelve los puntos de un polígono de flecha orientada según el carril."""
    base = [
        (0, -size),
        (size, 0),
        (size * 0.45, 0),
        (size * 0.45, size),
        (-size * 0.45, size),
        (-size * 0.45, 0),
        (-size, 0),
    ]
    angle = math.radians(LANE_ANGLES[lane])
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    points = []
    for x, y in base:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        points.append((cx + rx, cy + ry))
    return points


def draw_arrow(surface, cx, cy, lane, fill, outline, size=ARROW_SIZE, width=4):
    points = arrow_points(cx, cy, lane, size)
    pygame.draw.polygon(surface, fill, points)
    pygame.draw.polygon(surface, outline, points, width)


def draw_bomb_arrow(surface, cx, cy, lane, t):
    """Flecha bomba: cuerpo oscuro, borde rojo parpadeante y una bomba en el centro."""
    pulse = 0.5 + 0.5 * math.sin(t * 10)
    outline = (int(200 + 55 * pulse), int(40 + 30 * pulse), int(50 + 20 * pulse))
    draw_arrow(surface, cx, cy, lane, BOMB_BODY, outline, width=5)
    # Bomba dibujada en el centro de la flecha
    pygame.draw.circle(surface, (70, 70, 85), (cx, cy + 4), 13)
    pygame.draw.circle(surface, (15, 15, 20), (cx, cy + 4), 13, 2)
    pygame.draw.line(surface, YELLOW, (cx + 6, cy - 6), (cx + 12, cy - 13), 3)
    spark = 3 + int(2 * pulse)
    pygame.draw.circle(surface, RED, (cx + 13, cy - 14), spark)
    pygame.draw.circle(surface, WHITE, (cx - 5, cy), 3)


def draw_avatar(surface, cx, cy, mood, t, radius=55):
    """Avatar morado. mood: 'neutral', 'happy' (sonríe) o 'sad' (triste)."""
    if mood == "happy":
        cy -= int(abs(math.sin(t * 14)) * radius * 0.18)
    elif mood == "sad":
        cx += int(math.sin(t * 30) * radius * 0.04)
        cy += int(radius * 0.06)

    r = radius
    # Sombra, cuerpo y borde
    pygame.draw.ellipse(surface, (8, 6, 18), (cx - r * 0.8, cy + r * 0.95, r * 1.6, r * 0.22))
    pygame.draw.circle(surface, PURPLE, (cx, cy), r)
    pygame.draw.circle(surface, PURPLE_LIGHT, (cx, cy), r, 4)
    # Brillo
    pygame.draw.circle(surface, PURPLE_LIGHT, (int(cx - r * 0.45), int(cy - r * 0.5)), int(r * 0.12))

    eye_dx = int(r * 0.38)
    eye_y = int(cy - r * 0.18)
    eye_r = max(4, int(r * 0.15))
    mouth_w = int(r * 0.8)

    if mood == "happy":
        for sign in (-1, 1):
            rect = pygame.Rect(cx + sign * eye_dx - eye_r * 1.4, eye_y - eye_r * 0.4,
                               eye_r * 2.8, eye_r * 2.4)
            pygame.draw.arc(surface, WHITE, rect, 0, math.pi, 4)
        mouth = pygame.Rect(cx - mouth_w // 2, int(cy + r * 0.05), mouth_w, int(r * 0.6))
        pygame.draw.ellipse(surface, (60, 15, 90), mouth)
        pygame.draw.rect(surface, PURPLE, (mouth.x, mouth.y, mouth.w, mouth.h // 2 - 2))
        pygame.draw.arc(surface, WHITE, mouth, math.pi, 2 * math.pi, 4)
        for sign in (-1, 1):
            pygame.draw.circle(surface, (255, 130, 190),
                               (cx + sign * int(r * 0.66), int(cy + r * 0.2)), int(r * 0.11))
    elif mood == "sad":
        for sign in (-1, 1):
            ex = cx + sign * eye_dx
            pygame.draw.circle(surface, WHITE, (ex, eye_y), eye_r)
            pygame.draw.circle(surface, BG_COLOR, (ex, eye_y + 2), max(2, eye_r // 2))
            inner = (ex - sign * eye_r, eye_y - int(r * 0.42))
            outer = (ex + sign * eye_r * 1.4, eye_y - int(r * 0.24))
            pygame.draw.line(surface, WHITE, inner, outer, 4)
        frown = pygame.Rect(cx - mouth_w // 2, int(cy + r * 0.38), mouth_w, int(r * 0.45))
        pygame.draw.arc(surface, WHITE, frown, 0, math.pi, 4)
        tear_y = eye_y + eye_r + int((t * 60) % (r * 0.5))
        pygame.draw.circle(surface, (120, 200, 255), (cx + eye_dx, tear_y), max(3, int(r * 0.08)))
    else:
        for sign in (-1, 1):
            ex = cx + sign * eye_dx
            pygame.draw.circle(surface, WHITE, (ex, eye_y), eye_r)
            pygame.draw.circle(surface, BG_COLOR, (ex, eye_y), max(2, eye_r // 2))
        pygame.draw.line(surface, WHITE, (cx - mouth_w // 4, int(cy + r * 0.4)),
                         (cx + mouth_w // 4, int(cy + r * 0.4)), 4)


# ----------------------------------------------------------------------------
# Elementos del juego / Game elements
# ----------------------------------------------------------------------------
class Note:
    """Una flecha que cae. Si bomb=True es una flecha bomba (no se debe pulsar)."""

    def __init__(self, lane, bomb):
        self.lane = lane
        self.bomb = bomb
        self.y = -ARROW_SIZE * 1.5

    @property
    def x(self):
        return LANE_CENTERS[self.lane]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DDR Bomb")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 64, bold=True)
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font = pygame.font.SysFont("arial", 26)
        self.font_small = pygame.font.SysFont("arial", 20)

        # Estado inicial: Selección de idioma
        self.state = STATE_LANGUAGE
        self.selected_lang_idx = 0      # 0: English (arriba), 1: Español (abajo)
        self.lang = "en"               # Idioma activo
        self.death_reason_key = ""

        self.best_score = 0
        self.time = 0.0
        self.reset()

    def t(self, key, **kwargs):
        """Retorna el texto en el idioma seleccionado según la clave."""
        lang_dict = TEXTS.get(self.lang, TEXTS["en"])
        val = lang_dict.get(key, key)
        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val

    # ------------------------------------------------------------------ estado
    def reset(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.lives = START_LIVES
        self.resolved = 0            # notas resueltas (aciertos + fallos + bombas esquivadas)
        self.level = 1
        self.spawn_timer = 1.0
        self.last_lane = -1
        self.lane_flash = [0.0] * NUM_LANES
        self.feedback_text = ""
        self.feedback_color = WHITE
        self.feedback_timer = 0.0
        self.death_reason_key = ""
        self.explosion = None        # (x, y, tiempo)
        self.avatar_mood = "neutral"
        self.avatar_timer = 0.0

    def set_avatar(self, mood, duration):
        """Cambia el estado de ánimo del avatar durante 'duration' segundos."""
        self.avatar_mood = mood
        self.avatar_timer = duration

    def fall_speed(self):
        """Velocidad de caída (px/s): aumenta con el nivel."""
        return min(260 + 45 * (self.level - 1), 820)

    def spawn_interval(self):
        """Tiempo entre flechas (s): disminuye con el nivel."""
        return max(0.28, 0.85 - 0.06 * (self.level - 1))

    def bomb_chance(self):
        """Probabilidad de que una flecha sea bomba: aumenta con el nivel."""
        return min(0.14 + 0.02 * (self.level - 1), 0.32)

    def multiplier(self):
        return min(1 + self.combo // 10, 4)

    def set_feedback(self, text, color):
        self.feedback_text = text
        self.feedback_color = color
        self.feedback_timer = 0.6

    # ------------------------------------------------------------------ lógica
    def spawn_notes(self):
        lane = random.choice([l for l in range(NUM_LANES) if l != self.last_lane])
        self.last_lane = lane
        self.notes.append(Note(lane, random.random() < self.bomb_chance()))

        # A partir del nivel 3 pueden aparecer dos flechas a la vez
        if self.level >= 3 and random.random() < min(0.12 + 0.03 * self.level, 0.35):
            other = random.choice([l for l in range(NUM_LANES) if l != lane])
            self.notes.append(Note(other, random.random() < self.bomb_chance()))

    def press_lane(self, lane):
        self.lane_flash[lane] = 0.15

        # Buscamos la flecha más cercana al objetivo dentro de la ventana de pulsación
        candidates = [n for n in self.notes
                      if n.lane == lane and abs(n.y - TARGET_Y) <= GOOD_WINDOW]
        if not candidates:
            self.combo = 0
            self.set_feedback(self.t("feedback_too_early"), GREY)
            self.set_avatar("sad", 0.5)
            return
        note = min(candidates, key=lambda n: abs(n.y - TARGET_Y))

        if note.bomb:
            # COLISIÓN: pulsar una bomba termina la partida
            self.explosion = (note.x, note.y, 0.0)
            self.notes.remove(note)
            self.end_game("reason_bomb")
            return

        distance = abs(note.y - TARGET_Y)
        if distance <= PERFECT_WINDOW:
            points, text, color = 100, self.t("feedback_perfect"), PURPLE_LIGHT
        else:
            points, text, color = 50, self.t("feedback_good"), GREEN
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.score += points * self.multiplier()
        self.set_feedback(text, color)
        self.set_avatar("happy", 0.8)
        self.notes.remove(note)
        self.register_resolved()

    def register_resolved(self):
        """Cada 8 notas resueltas subimos de nivel (más rápido y más difícil)."""
        self.resolved += 1
        new_level = 1 + self.resolved // 8
        if new_level != self.level:
            self.level = new_level
            self.set_feedback(self.t("feedback_level", level=self.level), YELLOW)

    def end_game(self, reason_key):
        self.death_reason_key = reason_key
        self.best_score = max(self.best_score, self.score)
        self.set_avatar("sad", 0.0)      # Triste de forma permanente en el fin de partida
        self.state = STATE_GAME_OVER

    def update(self, dt):
        self.time += dt
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        if self.state == STATE_PLAYING and self.avatar_timer > 0:
            self.avatar_timer -= dt
            if self.avatar_timer <= 0:
                self.avatar_mood = "neutral"
        for i in range(NUM_LANES):
            if self.lane_flash[i] > 0:
                self.lane_flash[i] -= dt
        if self.explosion:
            x, y, t = self.explosion
            self.explosion = (x, y, t + dt) if t < 0.6 else None

        if self.state != STATE_PLAYING:
            return

        # Aparición de flechas
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_notes()
            self.spawn_timer = self.spawn_interval()

        # Movimiento y fallos
        speed = self.fall_speed()
        for note in self.notes[:]:
            note.y += speed * dt
            if note.y > TARGET_Y + GOOD_WINDOW:
                self.notes.remove(note)
                if note.bomb:
                    # Bomba esquivada: puntos extra
                    self.score += 25
                    self.set_feedback(self.t("feedback_bomb_dodged"), YELLOW)
                    self.set_avatar("happy", 0.8)
                    self.register_resolved()
                else:
                    self.lives -= 1
                    self.combo = 0
                    self.set_feedback(self.t("feedback_miss"), RED)
                    self.set_avatar("sad", 1.0)
                    self.register_resolved()
                    if self.lives <= 0:
                        self.end_game("reason_lives")
                        return

    # ------------------------------------------------------------------ dibujo
    def draw_text(self, text, font, color, center=None, topleft=None, topright=None):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = center
        elif topleft:
            rect.topleft = topleft
        elif topright:
            rect.topright = topright
        self.screen.blit(surf, rect)

    def draw_field(self):
        self.screen.fill(BG_COLOR)
        for i in range(NUM_LANES):
            rect = pygame.Rect(FIELD_LEFT + i * LANE_WIDTH, 0, LANE_WIDTH, SCREEN_HEIGHT)
            pygame.draw.rect(self.screen, LANE_COLOR, rect)
            pygame.draw.rect(self.screen, LANE_LINE, rect, 2)
            if self.lane_flash[i] > 0:
                glow = pygame.Surface((LANE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                glow.fill((*PURPLE, 70))
                self.screen.blit(glow, rect.topleft)

        # Flechas del jugador (MORADAS)
        for i in range(NUM_LANES):
            pressed = self.lane_flash[i] > 0
            fill = PURPLE_LIGHT if pressed else PURPLE
            draw_arrow(self.screen, LANE_CENTERS[i], TARGET_Y, i, fill, WHITE,
                       size=ARROW_SIZE + (4 if pressed else 0), width=3)

    def draw_hud(self):
        self.draw_text(f"{self.t('score_label')}: {self.score}", self.font_big, WHITE, topleft=(20, 15))
        self.draw_text(f"{self.t('level_label')} {self.level}", self.font, YELLOW, topleft=(20, 65))
        self.draw_text(f"{self.t('combo_label')}: {self.combo}  (x{self.multiplier()})", self.font,
                       PURPLE_LIGHT, topright=(SCREEN_WIDTH - 20, 20))
        # Vidas
        for i in range(START_LIVES):
            color = RED if i < self.lives else (60, 40, 55)
            pygame.draw.circle(self.screen, color, (SCREEN_WIDTH - 40 - i * 36, 75), 13)
            pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH - 40 - i * 36, 75), 13, 2)

        if self.feedback_timer > 0:
            self.draw_text(self.feedback_text, self.font_big, self.feedback_color,
                           center=(SCREEN_WIDTH // 2, TARGET_Y - 110))

        # Avatar morado a la izquierda del campo de juego
        draw_avatar(self.screen, FIELD_LEFT // 2, 360, self.avatar_mood, self.time, radius=55)

    def draw_notes(self):
        for note in self.notes:
            if note.bomb:
                draw_bomb_arrow(self.screen, int(note.x), int(note.y), note.lane, self.time)
            else:
                draw_arrow(self.screen, int(note.x), int(note.y), note.lane,
                           ARROW_COLORS[note.lane], WHITE, width=3)

    def draw_explosion(self):
        if self.explosion:
            x, y, t = self.explosion
            radius = int(20 + t * 160)
            alpha = max(0, int(255 * (1 - t / 0.6)))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 140, 40, alpha), (radius, radius), radius)
            pygame.draw.circle(surf, (255, 230, 120, alpha), (radius, radius), radius // 2)
            self.screen.blit(surf, (x - radius, y - radius))

    def draw_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 22, 215))
        self.screen.blit(overlay, (0, 0))

    def get_lang_rects(self):
        """Retorna los rectángulos de los botones de idioma."""
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 360, 68
        spacing = 26
        y_start = 285
        rects = []
        for i in range(len(LANG_OPTIONS)):
            y = y_start + i * (btn_h + spacing)
            rects.append(pygame.Rect(cx - btn_w // 2, y, btn_w, btn_h))
        return rects

    def draw_language_select(self):
        """Pantalla de selección de idioma con English arriba y Español abajo."""
        self.draw_field()
        self.draw_overlay()
        cx = SCREEN_WIDTH // 2

        # Avatar simpático en la parte superior
        draw_avatar(self.screen, cx, 85, "happy", self.time, radius=36)

        # Título bilingüe
        self.draw_text("SELECT LANGUAGE", self.font_title, PURPLE_LIGHT, center=(cx, 165))
        self.draw_text("SELECCIONAR IDIOMA", self.font, GREY, center=(cx, 225))

        # Botones de idioma
        rects = self.get_lang_rects()
        for i, (name, _) in enumerate(LANG_OPTIONS):
            rect = rects[i]
            is_selected = (i == self.selected_lang_idx)

            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            if is_selected:
                # Botón seleccionado: resaltado violeta brillante
                btn_surf.fill((75, 35, 125, 230))
                self.screen.blit(btn_surf, rect.topleft)
                pygame.draw.rect(self.screen, PURPLE_LIGHT, rect, width=3, border_radius=14)
                text = f"▶   {name}"
                self.draw_text(text, self.font_big, WHITE, center=rect.center)
            else:
                # Botón no seleccionado: fondo oscuro sutil
                btn_surf.fill((25, 22, 50, 180))
                self.screen.blit(btn_surf, rect.topleft)
                pygame.draw.rect(self.screen, LANE_LINE, rect, width=2, border_radius=14)
                text = f"     {name}"
                self.draw_text(text, self.font_big, GREY, center=rect.center)

        # Instrucciones de selección
        pulse = int(self.time * 2) % 2 == 0
        if pulse:
            self.draw_text("↑ / ↓ : Select   ·   ENTER / SPACE : Confirm",
                           self.font, YELLOW, center=(cx, 510))
        else:
            self.draw_text("↑ / ↓ : Seleccionar   ·   ENTER / ESPACIO : Confirmar",
                           self.font, WHITE, center=(cx, 510))

        self.draw_text("Shortcut: [1] English   ·   [2] Español",
                       self.font_small, GREY, center=(cx, 565))
        self.draw_text("ESC : Exit", self.font_small, GREY, center=(cx, 600))

    def draw_welcome(self):
        self.draw_field()
        self.draw_overlay()
        cx = SCREEN_WIDTH // 2
        draw_avatar(self.screen, cx, 78, "happy", self.time, radius=36)
        self.draw_text(self.t("title"), self.font_title, PURPLE_LIGHT, center=(cx, 170))
        self.draw_text(self.t("welcome_instruction_1"), self.font,
                       WHITE, center=(cx, 260))
        self.draw_text(self.t("welcome_instruction_2"), self.font, RED, center=(cx, 300))
        self.draw_text(self.t("welcome_controls"), self.font_small, GREY,
                       center=(cx, 350))
        # Ejemplo visual
        draw_arrow(self.screen, cx - 70, 440, 2, PURPLE, WHITE, width=3)
        draw_bomb_arrow(self.screen, cx + 70, 440, 2, self.time)
        if int(self.time * 2) % 2 == 0:
            self.draw_text(self.t("welcome_start"), self.font_big, YELLOW,
                           center=(cx, 560))

    def draw_game_over(self):
        self.draw_field()
        self.draw_notes()
        self.draw_explosion()
        self.draw_overlay()
        cx = SCREEN_WIDTH // 2
        draw_avatar(self.screen, cx, 62, "sad", self.time, radius=36)
        self.draw_text(self.t("game_over_title"), self.font_title, RED, center=(cx, 150))
        reason_text = self.t(self.death_reason_key) if self.death_reason_key else ""
        self.draw_text(reason_text, self.font, GREY, center=(cx, 215))
        self.draw_text(self.t("game_over_final_score", score=self.score), self.font_big, WHITE, center=(cx, 300))
        self.draw_text(self.t("game_over_best_score", best_score=self.best_score), self.font, YELLOW, center=(cx, 355))
        self.draw_text(self.t("game_over_stats", max_combo=self.max_combo, level=self.level),
                       self.font, PURPLE_LIGHT, center=(cx, 400))
        self.draw_text(self.t("game_over_restart"), self.font, GREEN, center=(cx, 490))
        self.draw_text(self.t("game_over_lang"), self.font_small, PURPLE_LIGHT, center=(cx, 532))
        self.draw_text(self.t("game_over_exit"), self.font_small, GREY, center=(cx, 565))

    def draw(self):
        if self.state == STATE_LANGUAGE:
            self.draw_language_select()
        elif self.state == STATE_WELCOME:
            self.draw_welcome()
        elif self.state == STATE_PLAYING:
            self.draw_field()
            self.draw_notes()
            self.draw_explosion()
            self.draw_hud()
        else:
            self.draw_game_over()
        pygame.display.flip()

    # ------------------------------------------------------------------ eventos
    def quit(self):
        pygame.quit()
        sys.exit()

    def confirm_language(self):
        """Confirma el idioma seleccionado y pasa a la pantalla de bienvenida."""
        self.lang = LANG_OPTIONS[self.selected_lang_idx][1]
        self.state = STATE_WELCOME

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            # Gestión de eventos en la pantalla de selección de idioma
            if self.state == STATE_LANGUAGE:
                if event.type == pygame.MOUSEMOTION:
                    rects = self.get_lang_rects()
                    for idx, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            self.selected_lang_idx = idx

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rects = self.get_lang_rects()
                    for idx, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            self.selected_lang_idx = idx
                            self.confirm_language()
                            return

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_lang_idx = (self.selected_lang_idx - 1) % len(LANG_OPTIONS)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_lang_idx = (self.selected_lang_idx + 1) % len(LANG_OPTIONS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.confirm_language()
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        self.selected_lang_idx = 0
                        self.confirm_language()
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.selected_lang_idx = 1
                        self.confirm_language()

            # Gestión de eventos en los demás estados
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

                if self.state == STATE_WELCOME:
                    if event.key == pygame.K_l:
                        self.state = STATE_LANGUAGE
                    else:
                        self.reset()
                        self.state = STATE_PLAYING
                elif self.state == STATE_PLAYING:
                    if event.key in KEY_TO_LANE:
                        self.press_lane(KEY_TO_LANE[event.key])
                elif self.state == STATE_GAME_OVER:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_l:
                        self.state = STATE_LANGUAGE

    # ------------------------------------------------------------------ bucle
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0   # Control de FPS con reloj
            dt = min(dt, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
