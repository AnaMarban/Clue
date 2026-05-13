"""
La Maldición de los Moore — Versión Python/Pygame
=================================================
Juego de misterio tipo Clue con estética noir, imágenes cinematográficas,
5 acciones por ronda, 2 oportunidades de acusación y finales dinámicos.

Requisitos:
    pip install pygame

Ejecutar:
    python main.py

Controles extra:
    ESC  -> salir
    F11  -> pantalla completa / ventana
"""

from __future__ import annotations

import math
import os
import random
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pygame

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

WINDOW_SIZE = (1280, 720)
FPS = 60

GOLD = (205, 170, 78)
GOLD_LIGHT = (235, 205, 120)
DARK = (7, 6, 5)
RED = (120, 16, 18)
TEXT_DARK = (45, 25, 10)
WHITE = (240, 230, 210)

# Si quieres probar siempre un caso específico, pon 1..5. Si no, None.
FORCE_CASE_ID: Optional[int] = None


# ─────────────────────────────────────────────────────────────
# DATOS DEL JUEGO
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Case:
    id: int
    title: str
    killer: str
    victim: str
    weapon: str
    room: str
    story_hint: str


CASES: List[Case] = [
    Case(
        1,
        "Herencia silenciosa",
        killer="hijo",
        victim="abuelo",
        weapon="veneno",
        room="cava",
        story_hint="Una copa fue preparada antes de que la noche comenzara.",
    ),
    Case(
        2,
        "Decisiones que pesan",
        killer="abogado",
        victim="hijo",
        weapon="cuchillo",
        room="estudio",
        story_hint="Los papeles del estudio ocultaban más que firmas.",
    ),
    Case(
        3,
        "El peso del pasado",
        killer="tio",
        victim="nuera",
        weapon="cuerda",
        room="invernadero",
        story_hint="El silencio entre las plantas escondió una decisión fría.",
    ),
    Case(
        4,
        "Ruido en la oscuridad",
        killer="nieta",
        victim="tio",
        weapon="pistola",
        room="biblioteca",
        story_hint="El disparo no fue lo único que rompió el silencio.",
    ),
    Case(
        5,
        "Lo que queda en la mesa",
        killer="nuera",
        victim="abogado",
        weapon="copa",
        room="cocina",
        story_hint="La última conversación quedó marcada en el borde de una copa.",
    ),
]

SUSPECTS = ["abogado", "abuelo", "hijo", "nieta", "nuera", "tio"]
WEAPONS = ["cuchillo", "veneno", "cuerda", "pistola", "copa"]
ROOMS = ["biblioteca", "estudio", "invernadero", "cava", "cocina"]

NAMES = {
    "abogado": "Abogado",
    "abuelo": "Abuelo",
    "hijo": "Hijo",
    "nieta": "Nieta",
    "nuera": "Nuera",
    "tio": "Tío",
    "cuchillo": "Cuchillo",
    "veneno": "Veneno",
    "cuerda": "Cuerda",
    "pistola": "Pistola",
    "copa": "Copa",
    "biblioteca": "Biblioteca",
    "estudio": "Estudio",
    "invernadero": "Invernadero",
    "cava": "Cava",
    "cocina": "Cocina",
}

ASSETS = {
    "intro_portada": "000_intro_portada.png",
    "intro_objetivo": "000_intro_objetivo.png",
    "intro_reglas": "000_intro_reglas.png",
    "fondo_limpio": "001_imagen_limpia.png",
    "mapa": "003_mapa_mansion.png",
    "tablero_principal": "003_tablero_principal.png",
    "tablero_investigacion": "003_tablero_investigacion.png",
    "tablero_acusacion": "003_Tablero_acusaciones.png",
    "btn_continuar": "009_boton_continuar.png",
    "btn_volver": "009_boton_bolver.png",  # nombre original del paquete
    "btn_investigacion": "009_boton_investigacion.png",
    "nota_blanca": "009_nota_blanca.png",
    "nota_equivocacion": "012_nota_equivocacion.png",
    "perdiste": "011_has_perdido.png",
}

VICTIM_IMAGES = {k: f"005_victima_{k}.png" for k in SUSPECTS}
PROFILE_IMAGES = {k: f"004_perfil_{k}.png" for k in SUSPECTS}
SUSPECT_IMAGES = {k: f"007_sospechoso_{k}.png" for k in SUSPECTS}
CULPRIT_IMAGES = {k: f"008_culpable_{k}.png" for k in SUSPECTS}
DISCARDED_IMAGES = {
    "abogado": "006_descartado_abogado.png",
    "abuelo": "006_descartado_abuela.png",  # nombre original del paquete
    "hijo": "006_descartado_hijo.png",
    "nieta": "006_descartado_nieta.png",
    "nuera": "006_descartado_nuera.png",
    "tio": "006_descartado_tio.png",
}
WEAPON_IMAGES = {k: f"010_arma_{k}.png" for k in WEAPONS}
ROOM_IMAGES = {k: f"002_{k}.png" for k in ROOMS}
ROOM_DEAD_IMAGES = {k: f"002_{k}_muerto.png" for k in ROOMS}
WIN_BY_KILLER = {k: f"011_ganaste_caso_{k}.png" for k in ["abogado", "hijo", "nieta", "nuera", "tio"]}


# ─────────────────────────────────────────────────────────────
# UTILIDADES GRÁFICAS
# ─────────────────────────────────────────────────────────────

def asset_path(filename: str) -> Path:
    return ASSET_DIR / filename


def load_image(filename: str, convert_alpha: bool = True) -> pygame.Surface:
    path = asset_path(filename)
    if not path.exists():
        raise FileNotFoundError(f"No encontré el asset: {path}")
    image = pygame.image.load(str(path))
    return image.convert_alpha() if convert_alpha else image.convert()


def scale_cover(image: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
    """Escala una imagen para cubrir toda la pantalla sin deformarla."""
    sw, sh = size
    iw, ih = image.get_size()
    scale = max(sw / iw, sh / ih)
    new_size = (int(iw * scale), int(ih * scale))
    return pygame.transform.smoothscale(image, new_size)


def blit_cover(screen: pygame.Surface, image: pygame.Surface, alpha: int = 255):
    scaled = scale_cover(image, screen.get_size())
    if alpha < 255:
        scaled = scaled.copy()
        scaled.set_alpha(alpha)
    rect = scaled.get_rect(center=screen.get_rect().center)
    screen.blit(scaled, rect)


def scale_contain(image: pygame.Surface, max_size: Tuple[int, int]) -> pygame.Surface:
    mw, mh = max_size
    iw, ih = image.get_size()
    scale = min(mw / iw, mh / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    return pygame.transform.smoothscale(image, new_size)


def draw_vignette(screen: pygame.Surface):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    # Vignette sencilla por rectángulos concéntricos para no requerir shaders.
    for i in range(80):
        alpha = int((i / 80) ** 2 * 8)
        rect = pygame.Rect(i * w / 160, i * h / 160, w - i * w / 80, h - i * h / 80)
        pygame.draw.rect(overlay, (0, 0, 0, alpha), rect, border_radius=12)
    # Oscurece bordes más directo
    edge = pygame.Surface((w, h), pygame.SRCALPHA)
    # pygame.draw.rect(edge, (0, 0, 0, 120), (0, 0, w, int(h * 0.08)))
     #pygame.draw.rect(edge, (0, 0, 0, 150), (0, int(h * 0.88), w, int(h * 0.12)))
    screen.blit(overlay, (0, 0))
    screen.blit(edge, (0, 0))


def pct_rect(size: Tuple[int, int], left: float, top: float, width: float, height: float) -> pygame.Rect:
    sw, sh = size
    return pygame.Rect(int(sw * left), int(sh * top), int(sw * width), int(sh * height))


def draw_text_center(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    center: Tuple[int, int],
    color=GOLD_LIGHT,
    shadow=True,
):
    if shadow:
        surf_shadow = font.render(text, True, (0, 0, 0))
        rect_shadow = surf_shadow.get_rect(center=(center[0] + 2, center[1] + 2))
        screen.blit(surf_shadow, rect_shadow)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)


# ─────────────────────────────────────────────────────────────
# COMPONENTES UI
# ─────────────────────────────────────────────────────────────

@dataclass
class ImageButton:
    image: pygame.Surface
    pos: Tuple[int, int]
    anchor: str = "center"
    max_width_ratio: float = 0.22
    callback: Optional[Callable] = None
    visible: bool = True
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))
    hover: bool = False

    def layout(self, screen_size: Tuple[int, int]):
        sw, sh = screen_size
        max_w = int(sw * self.max_width_ratio)
        max_h = int(sh * 0.16)
        scaled = scale_contain(self.image, (max_w, max_h))
        self._scaled = scaled
        self.rect = scaled.get_rect()
        setattr(self.rect, self.anchor, self.pos)

    def update(self, mouse_pos: Tuple[int, int]):
        self.hover = self.visible and self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        if not self.visible or not self.callback:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.callback()

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        img = self._scaled
        rect = self.rect
        if self.hover:
            glow = pygame.Surface((rect.width + 28, rect.height + 28), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*GOLD, 90), glow.get_rect(), border_radius=14)
            pygame.draw.rect(glow, (*GOLD_LIGHT, 110), glow.get_rect().inflate(-10, -10), 2, border_radius=12)
            screen.blit(glow, (rect.x - 14, rect.y - 14), special_flags=pygame.BLEND_PREMULTIPLIED)
            img = img.copy()
           # img.fill((35, 30, 18, 0), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(img, rect)


@dataclass
class Hotspot:
    rect_pct: Tuple[float, float, float, float]
    value: str
    callback: Callable[[str], None]
    label: str = ""
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))
    hover: bool = False

    def layout(self, screen_size: Tuple[int, int]):
        self.rect = pct_rect(screen_size, *self.rect_pct)

    def update(self, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.callback(self.value)

    def draw(self, screen: pygame.Surface):
        if self.hover:
            glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*GOLD, 38), glow.get_rect(), border_radius=10)
            pygame.draw.rect(glow, (*GOLD_LIGHT, 180), glow.get_rect(), 3, border_radius=10)
            screen.blit(glow, self.rect.topleft)


@dataclass
class CardOption:
    key: str
    image: pygame.Surface
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))
    hover: bool = False
    selected: bool = False

    def update(self, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen: pygame.Surface):
        if self.hover or self.selected:
            pad = 8 if self.selected else 5
            glow = pygame.Surface((self.rect.width + pad * 2, self.rect.height + pad * 2), pygame.SRCALPHA)
            color = (*GOLD_LIGHT, 190 if self.selected else 110)
            pygame.draw.rect(glow, (*GOLD, 50), glow.get_rect(), border_radius=8)
            pygame.draw.rect(glow, color, glow.get_rect(), 3, border_radius=8)
            screen.blit(glow, (self.rect.x - pad, self.rect.y - pad))
        screen.blit(self.image, self.rect)


class ScreenID(str, Enum):
    PORTADA = "portada"
    OBJETIVO = "objetivo"
    REGLAS = "reglas"
    VICTIMA = "victima"
    HUB = "hub"
    INVESTIGACION = "investigacion"
    MAPA = "mapa"
    ARMAS = "armas"
    SOSPECHOSOS = "sospechosos"
    DETALLE = "detalle"
    ACUSACION = "acusacion"
    WRONG_SUSPECT = "wrong_suspect"
    WRONG_WEAPON = "wrong_weapon"
    WRONG_ROOM = "wrong_room"
    RESULT = "result"


# ─────────────────────────────────────────────────────────────
# JUEGO PRINCIPAL
# ─────────────────────────────────────────────────────────────

class MooreGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("La Maldición de los Moore")
        self.fullscreen = False
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_title = pygame.font.SysFont("georgia", 42, bold=True)
        self.font_ui = pygame.font.SysFont("georgia", 26, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 18, italic=True)
        self.font_note = pygame.font.SysFont("georgia", 18, bold=True)

        self.images: Dict[str, pygame.Surface] = {}
        self.load_assets()

        self.current_screen = ScreenID.PORTADA
        self.previous_screen = ScreenID.PORTADA
        self.fade_alpha = 255
        self.fade_target = 0
        self.fade_speed = 12

        self.case: Case = self.choose_case()
        self.round = 1
        self.actions_left = 5
        self.selected_suspect: Optional[str] = None
        self.selected_weapon: Optional[str] = None
        self.selected_room: Optional[str] = None
        self.detail_image: Optional[pygame.Surface] = None
        self.detail_from: ScreenID = ScreenID.HUB
        self.detail_show_note = False
        self.result_image: Optional[pygame.Surface] = None

        self.wrong_order: List[ScreenID] = []
        self.wrong_index = 0
        self.wrong_note_weapon = False
        self.wrong_note_room = False
        self.wrong_suspect_img: Optional[pygame.Surface] = None
        self.wrong_weapon_img: Optional[pygame.Surface] = None
        self.wrong_room_img: Optional[pygame.Surface] = None

        self.buttons: List[ImageButton] = []
        self.hotspots: List[Hotspot] = []
        self.weapon_cards: List[CardOption] = []
        self.accuse_cards: Dict[str, List[CardOption]] = {"suspect": [], "weapon": [], "room": []}

        self.rain = self.create_rain()
        self.build_layout()

    # ── Assets ───────────────────────────────────────────────
    def load_assets(self):
        all_files = set(ASSETS.values())
        all_files.update(VICTIM_IMAGES.values())
        all_files.update(PROFILE_IMAGES.values())
        all_files.update(SUSPECT_IMAGES.values())
        all_files.update(CULPRIT_IMAGES.values())
        all_files.update(DISCARDED_IMAGES.values())
        all_files.update(WEAPON_IMAGES.values())
        all_files.update(ROOM_IMAGES.values())
        all_files.update(ROOM_DEAD_IMAGES.values())
        all_files.update(WIN_BY_KILLER.values())

        for filename in sorted(all_files):
            path = asset_path(filename)
            if path.exists():
                self.images[filename] = load_image(filename)
            else:
                print(f"[AVISO] Falta asset opcional: {filename}")

    def img(self, filename: str) -> pygame.Surface:
        if filename not in self.images:
            self.images[filename] = load_image(filename)
        return self.images[filename]

    def choose_case(self) -> Case:
        if FORCE_CASE_ID is not None:
            for c in CASES:
                if c.id == FORCE_CASE_ID:
                    return c
        return random.choice(CASES)

    # ── Estado ───────────────────────────────────────────────
    def reset_game(self):
        self.case = self.choose_case()
        self.round = 1
        self.actions_left = 5
        self.selected_suspect = None
        self.selected_weapon = None
        self.selected_room = None
        self.go(ScreenID.PORTADA)

    def go(self, screen_id: ScreenID):
        self.previous_screen = self.current_screen
        self.current_screen = screen_id
        self.fade_alpha = 255
        self.fade_target = 0
        self.build_layout()

    def use_action(self):
        self.actions_left = max(0, self.actions_left - 1)

    # ── Layout ───────────────────────────────────────────────
    def build_layout(self):
        self.buttons = []
        self.hotspots = []
        self.weapon_cards = []
        self.accuse_cards = {"suspect": [], "weapon": [], "room": []}
        sw, sh = self.screen.get_size()

        def btn(filename: str, pos, anchor="center", width=0.22, cb=None):
            b = ImageButton(self.img(filename), pos=pos, anchor=anchor, max_width_ratio=width, callback=cb)
            b.layout((sw, sh))
            self.buttons.append(b)
            return b

        if self.current_screen == ScreenID.PORTADA:
            self.hotspots.append(
                Hotspot(
                    (0.35, 0.776, 0.352, 0.151),
                    "portada",
                    lambda _: self.go(ScreenID.OBJETIVO)
                )
            )
         #    btn(ASSETS["btn_continuar"], (sw // 2, int(sh * 0.88)), width=0.23, cb=lambda: self.go(ScreenID.OBJETIVO))

        elif self.current_screen == ScreenID.OBJETIVO:
            btn(ASSETS["btn_continuar"], (sw // 2, int(sh * 0.88)), width=0.23, cb=lambda: self.go(ScreenID.REGLAS))

        elif self.current_screen == ScreenID.REGLAS:
            btn(ASSETS["btn_continuar"], (sw // 2, int(sh * 0.88)), width=0.23, cb=lambda: self.go(ScreenID.VICTIMA))

        elif self.current_screen == ScreenID.VICTIMA:
            btn(ASSETS["btn_investigacion"], (sw // 2, int(sh * 0.88)), width=0.25, cb=lambda: self.go(ScreenID.HUB))

        elif self.current_screen == ScreenID.HUB:
            btn(ASSETS["btn_investigacion"], (sw // 2, int(sh * 0.88)), width=0.25, cb=lambda: self.go(ScreenID.INVESTIGACION))

        elif self.current_screen == ScreenID.INVESTIGACION:
            self.hotspots.extend([
                Hotspot((0.096, 0.43, 0.243, 0.35), "mapa", lambda _: self.go(ScreenID.MAPA)),
                Hotspot((0.380, 0.43, 0.240, 0.35), "armas", lambda _: self.go(ScreenID.ARMAS)),
                Hotspot((0.648, 0.43, 0.263, 0.35), "sospechosos", lambda _: self.go(ScreenID.SOSPECHOSOS)),
            ])
            btn(ASSETS["btn_volver"], (int(sw * 0.018), int(sh * 0.10)), anchor="bottomleft", width=0.14, cb=lambda: self.go(ScreenID.HUB))

        elif self.current_screen == ScreenID.MAPA:
            rooms = [
                ((0.176, 0.108, 0.208, 0.42), "biblioteca"),
                ((0.45, 0.110, 0.169, 0.36), "estudio"),
                ((0.68, 0.22, 0.195, 0.350), "invernadero"),
                ((0.228, 0.60, 0.18, 0.31), "cava"),
                ((0.511, 0.60, 0.189, 0.31), "cocina"),
               # ((0.55, 0.75, 0.18, 0.18), "cava"),
            ]
            for rect, room in rooms:
                self.hotspots.append(Hotspot(rect, room, self.investigate_room))
            btn(ASSETS["btn_volver"], (int(sw * 0.035), int(sh * 0.94)), anchor="bottomleft", width=0.14, cb=lambda: self.go(ScreenID.INVESTIGACION))

        elif self.current_screen == ScreenID.ARMAS:
            self.layout_weapon_cards()
            btn(ASSETS["btn_volver"], (int(sw * 0.035), int(sh * 0.94)), anchor="bottomleft", width=0.14, cb=lambda: self.go(ScreenID.INVESTIGACION))

        elif self.current_screen == ScreenID.SOSPECHOSOS:
            suspects = [
                ((0.229, 0.157, 0.13, 0.33), "abuelo"),
                ((0.44, 0.157, 0.13, 0.33), "hijo"),
                ((0.641, 0.157, 0.13, 0.33), "nuera"),
                ((0.271, 0.510, 0.138, 0.33), "tio"),
                ((0.440, 0.510, 0.13, 0.33), "abogado"),
                ((0.629, 0.510, 0.13, 0.33), "nieta"),
            ]
            for rect, suspect in suspects:
                self.hotspots.append(Hotspot(rect, suspect, self.investigate_suspect))
            btn(ASSETS["btn_volver"], (int(sw * 0.035), int(sh * 0.94)), anchor="bottomleft", width=0.14, cb=lambda: self.go(ScreenID.INVESTIGACION))

        elif self.current_screen == ScreenID.DETALLE:
            btn(ASSETS["btn_volver"], (int(sw * 0.035), int(sh * 0.09)), anchor="bottomleft", width=0.14, cb=lambda: self.go(self.detail_from))
            # Hotspot invisible en esquina inferior derecha para continuar
            self.hotspots.append(
                Hotspot(
                    (0.85, 0.88, 0.14, 0.10),
                    "detail_continue",
                    lambda _: self.detail_continue()
                )
            )

        elif self.current_screen == ScreenID.ACUSACION:
            self.layout_accusation_cards()
            btn(ASSETS["btn_volver"], (int(sw * 0.035), int(sh * 0.94)), anchor="bottomleft", width=0.14, cb=lambda: self.go(ScreenID.HUB))

        elif self.current_screen in (ScreenID.WRONG_SUSPECT, ScreenID.WRONG_WEAPON, ScreenID.WRONG_ROOM):
            btn(ASSETS["btn_continuar"], (int(sw * 0.965), int(sh * 0.94)), anchor="bottomright", width=0.18, cb=self.wrong_continue)

        elif self.current_screen == ScreenID.RESULT:
            btn(ASSETS["btn_continuar"], (sw // 2, int(sh * 0.90)), width=0.20, cb=self.reset_game)

        for h in self.hotspots:
            h.layout((sw, sh))

    def layout_weapon_cards(self):
        sw, sh = self.screen.get_size()
        margin = int(sw * 0.04)
        gap = int(sw * 0.015)
        available_w = sw - margin * 2 - gap * (len(WEAPONS) - 1)
        card_w = available_w // len(WEAPONS)
        max_h = int(sh * 0.58)
        y = int(sh * 0.28)
        for i, key in enumerate(WEAPONS):
            surf = scale_contain(self.img(WEAPON_IMAGES[key]), (card_w, max_h))
            rect = surf.get_rect()
            rect.x = margin + i * (card_w + gap) + (card_w - rect.width) // 2
            rect.y = y
            self.weapon_cards.append(CardOption(key=key, image=surf, rect=rect))

    def layout_accusation_cards(self):
        sw, sh = self.screen.get_size()

        # Definir posiciones específicas para cada carta (como porcentajes de pantalla)
        suspects_positions = [
            ((0.0208, 0.617, 0.063, 0.20), "hijo"),
            ((0.0908, 0.617, 0.063, 0.20), "abogado"),
            ((0.1608, 0.617, 0.063, 0.20), "tio"),
            ((0.2308, 0.617, 0.063, 0.20), "nieta"),
            ((0.3010, 0.617, 0.063, 0.20), "nuera"),
            # ((0.37, 0.617, 0.063, 0.20), "nieta"),
        ]
        weapons_positions = [
            ((0.393, 0.617, 0.040, 0.20), "cuchillo"),
            ((0.443, 0.617, 0.040, 0.20), "cuerda"),
            ((0.492, 0.617, 0.040, 0.20), "pistola"),
            ((0.540, 0.617, 0.040, 0.20), "veneno"),
            ((0.589, 0.617, 0.040, 0.20), "copa"),
        ]
        rooms_positions = [
            ((0.655, 0.617, 0.0488, 0.20), "biblioteca"),
            ((0.72, 0.617, 0.0488, 0.20), "estudio"),
            ((0.781, 0.617, 0.0488, 0.20), "invernadero"),
            ((0.843, 0.617, 0.053, 0.20), "cava"),
            ((0.909, 0.617, 0.055, 0.20), "cocina"),
        ]

        def add_cards(kind: str, positions: List[Tuple[Tuple[float, float, float, float], str]]):
            cards = []
            for rect_pct, key in positions:
                rect = pct_rect((sw, sh), *rect_pct)
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))  # Transparente
                cards.append(CardOption(key=key, image=surf, rect=rect))
            self.accuse_cards[kind] = cards

        add_cards("suspect", suspects_positions)
        add_cards("weapon", weapons_positions)
        add_cards("room", rooms_positions)

    # ── Acciones de investigación ────────────────────────────
    def investigate_room(self, room: str):
        if self.actions_left <= 0:
            self.go(ScreenID.ACUSACION)
            return
        self.use_action()
        filename = ROOM_DEAD_IMAGES[room] if room == self.case.room else ROOM_IMAGES[room]
        self.detail_image = self.img(filename)
        self.detail_from = ScreenID.MAPA
        self.detail_show_note = False
        self.go(ScreenID.DETALLE)

    def investigate_weapon(self, weapon: str):
        if self.actions_left <= 0:
            self.go(ScreenID.ACUSACION)
            return
        self.use_action()
        self.detail_image = self.img(WEAPON_IMAGES[weapon])
        self.detail_from = ScreenID.ARMAS
        self.detail_show_note = False
        self.go(ScreenID.DETALLE)

    def investigate_suspect(self, suspect: str):
        if self.actions_left <= 0:
            self.go(ScreenID.ACUSACION)
            return
        self.use_action()
        # Segunda ronda: imágenes más tensas de sospechoso. Primera ronda: perfil normal.
        filename = SUSPECT_IMAGES[suspect] if self.round == 2 else PROFILE_IMAGES[suspect]
        self.detail_image = self.img(filename)
        self.detail_from = ScreenID.SOSPECHOSOS
        self.detail_show_note = False
        self.go(ScreenID.DETALLE)

    def detail_continue(self):
        if self.actions_left <= 0:
            self.go(ScreenID.ACUSACION)
        else:
            self.go(self.detail_from)

    # ── Acusación ────────────────────────────────────────────
    def confirm_accusation(self):
        if not (self.selected_suspect and self.selected_weapon and self.selected_room):
            return
        suspect_ok = self.selected_suspect == self.case.killer
        weapon_ok = self.selected_weapon == self.case.weapon
        room_ok = self.selected_room == self.case.room

        if suspect_ok and weapon_ok and room_ok:
            filename = WIN_BY_KILLER.get(self.case.killer)
            self.result_image = self.img(filename) if filename and filename in self.images else self.img(CULPRIT_IMAGES[self.case.killer])
            self.go(ScreenID.RESULT)
            return

        # Secuencia de retroalimentación parcial. No revela culpable si solo acertó el personaje,
        # lo mantiene como sospechoso para no romper completamente la deducción.
        self.wrong_suspect_img = self.img(
            SUSPECT_IMAGES[self.selected_suspect]
            if suspect_ok else DISCARDED_IMAGES[self.selected_suspect]
        )
        self.wrong_weapon_img = self.img(WEAPON_IMAGES[self.selected_weapon])
        self.wrong_room_img = self.img(ROOM_IMAGES[self.selected_room])
        self.wrong_note_weapon = not weapon_ok
        self.wrong_note_room = not room_ok
        self.wrong_index = 0
        self.wrong_order = [ScreenID.WRONG_SUSPECT, ScreenID.WRONG_WEAPON, ScreenID.WRONG_ROOM]
        self.go(self.wrong_order[0])

    def wrong_continue(self):
        self.wrong_index += 1
        if self.wrong_index < len(self.wrong_order):
            self.go(self.wrong_order[self.wrong_index])
            return

        if self.round == 1:
            self.round = 2
            self.actions_left = 5
            self.selected_suspect = None
            self.selected_weapon = None
            self.selected_room = None
            self.go(ScreenID.HUB)
        else:
            self.result_image = self.img(ASSETS["perdiste"])
            self.go(ScreenID.RESULT)

    # ── Efectos ──────────────────────────────────────────────
    def create_rain(self):
        sw, sh = WINDOW_SIZE
        return [
            [random.randint(0, sw), random.randint(0, sh), random.uniform(6, 14), random.randint(10, 26)]
            for _ in range(90)
        ]

    def update_rain(self):
        sw, sh = self.screen.get_size()
        for d in self.rain:
            d[1] += d[2]
            if d[1] > sh:
                d[0] = random.randint(0, sw)
                d[1] = -d[3]
                d[2] = random.uniform(6, 14)
                d[3] = random.randint(10, 26)

    def draw_rain(self):
        rain_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for x, y, speed, length in self.rain:
            pygame.draw.line(rain_surface, (160, 185, 210, 35), (x, y), (x - 2, y + length), 1)
        self.screen.blit(rain_surface, (0, 0))

    # ── Dibujado ─────────────────────────────────────────────
    def draw_background(self):
        if self.current_screen == ScreenID.PORTADA:
            blit_cover(self.screen, self.img(ASSETS["intro_portada"]))
        elif self.current_screen == ScreenID.OBJETIVO:
            blit_cover(self.screen, self.img(ASSETS["intro_objetivo"]))
        elif self.current_screen == ScreenID.REGLAS:
            blit_cover(self.screen, self.img(ASSETS["intro_reglas"]))
        elif self.current_screen == ScreenID.VICTIMA:
            blit_cover(self.screen, self.img(VICTIM_IMAGES[self.case.victim]))
            self.draw_dark_overlay(70)
        elif self.current_screen == ScreenID.HUB:
            blit_cover(self.screen, self.img(ASSETS["tablero_principal"]))
        elif self.current_screen == ScreenID.INVESTIGACION:
            blit_cover(self.screen, self.img(ASSETS["tablero_investigacion"]))
        elif self.current_screen == ScreenID.MAPA:
            blit_cover(self.screen, self.img(ASSETS["mapa"]))
        elif self.current_screen == ScreenID.ARMAS:
            # fondo limpio del juego con oscurecimiento; las armas van encima.
            bg_name = ASSETS.get("fondo_limpio")
            if bg_name and asset_path(bg_name).exists():
                blit_cover(self.screen, self.img(bg_name))
            else:
                self.screen.fill(DARK)
            self.draw_dark_overlay(170)
        elif self.current_screen == ScreenID.SOSPECHOSOS:
            blit_cover(self.screen, self.img(ASSETS["tablero_principal"]))
        elif self.current_screen == ScreenID.DETALLE and self.detail_image:
            blit_cover(self.screen, self.detail_image)
            self.draw_dark_overlay(50)
            if self.detail_show_note:
                self.draw_note_equivocacion()
        elif self.current_screen == ScreenID.ACUSACION:
            blit_cover(self.screen, self.img(ASSETS["tablero_acusacion"]))
            self.draw_accusation_panel()
        elif self.current_screen == ScreenID.WRONG_SUSPECT and self.wrong_suspect_img:
            blit_cover(self.screen, self.wrong_suspect_img)
            self.draw_dark_overlay(40)
        elif self.current_screen == ScreenID.WRONG_WEAPON and self.wrong_weapon_img:
            blit_cover(self.screen, self.wrong_weapon_img)
            if self.wrong_note_weapon:
                self.draw_note_equivocacion()
        elif self.current_screen == ScreenID.WRONG_ROOM and self.wrong_room_img:
            blit_cover(self.screen, self.wrong_room_img)
            if self.wrong_note_room:
                self.draw_note_equivocacion()
        elif self.current_screen == ScreenID.RESULT and self.result_image:
            blit_cover(self.screen, self.result_image)
            self.draw_dark_overlay(40)
        else:
            self.screen.fill(DARK)

        draw_vignette(self.screen)

    def draw_dark_overlay(self, alpha: int):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_actions_counter(self):
        # Contador solo en pantallas de gameplay antes de acusar.
        if self.current_screen not in {ScreenID.HUB, ScreenID.INVESTIGACION, ScreenID.MAPA, ScreenID.ARMAS, ScreenID.SOSPECHOSOS, ScreenID.DETALLE}:
            return
        if self.actions_left <= 0:
            return

        sw, sh = self.screen.get_size()
        note = scale_contain(self.img(ASSETS["nota_blanca"]), (int(sw * 0.24), int(sh * 0.20)))
        rect = note.get_rect(topright=(sw - int(sw * 0.025), int(sh * 0.055)))
        self.screen.blit(note, rect)

        lines = ["Acciones", "restantes", str(self.actions_left)]
        y = rect.y + rect.height * 0.13
        for i, line in enumerate(lines):
            font = self.font_note if i < 2 else self.font_ui
            surf = font.render(line, True, TEXT_DARK)
            self.screen.blit(surf, surf.get_rect(center=(rect.centerx, int(y + i * rect.height * 0.18))))

        # Indicador visual de ronda.
        round_text = f"Ronda {self.round}/2"
        surf = self.font_small.render(round_text, True, TEXT_DARK)
        self.screen.blit(surf, surf.get_rect(center=(rect.centerx, rect.bottom - int(rect.height * 0.238))))

    def draw_note_equivocacion(self):
        sw, sh = self.screen.get_size()
        note = scale_contain(self.img(ASSETS["nota_equivocacion"]), (int(sw * 0.22), int(sh * 0.28)))
        rotated = pygame.transform.rotate(note, -2)
        self.screen.blit(rotated, (int(sw * 0.03), int(sh * 0.04)))

    def draw_weapons_screen(self):
        draw_text_center(self.screen, "¿Qué arma quieres analizar?", self.font_title, (self.screen.get_width() // 2, int(self.screen.get_height() * 0.16)))
        for card in self.weapon_cards:
            card.draw(self.screen)

    def draw_accusation_panel(self):
        sw, sh = self.screen.get_size()
        # panel = pygame.Surface((sw, int(sh * 0.31)), pygame.SRCALPHA)
        # panel.fill((0, 0, 0, 205))
        # self.screen.blit(panel, (0, int(sh * 0.69)))

        # labels = ["Sospechoso", "Arma", "Lugar"]
        # for i, label in enumerate(labels):
        #     x = int((i + 0.5) * sw / 3)
        #     draw_text_center(self.screen, label, self.font_ui, (x, int(sh * 0.705)), GOLD_LIGHT)

        for group in self.accuse_cards.values():
            for card in group:
                card.draw(self.screen)

        # Botón de confirmar dibujado por código porque no existe imagen específica.
        all_selected = self.selected_suspect and self.selected_weapon and self.selected_room
        btn_w, btn_h = int(sw * 0.24), int(sh * 0.055)
        btn_rect = pygame.Rect((sw - btn_w) // 2, int(sh * 0.91), btn_w, btn_h)
        mouse = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse) and all_selected
        color = (*GOLD, 210 if all_selected else 80)
        bg = pygame.Surface(btn_rect.size, pygame.SRCALPHA)
        bg.fill((10, 8, 6, 220))
        self.screen.blit(bg, btn_rect)
        pygame.draw.rect(self.screen, color, btn_rect, 2, border_radius=4)
        if hover:
            pygame.draw.rect(self.screen, (*GOLD_LIGHT, 45), btn_rect.inflate(10, 10), border_radius=6)
        txt_color = GOLD_LIGHT if all_selected else (110, 90, 55)
        draw_text_center(self.screen, "CONFIRMAR ACUSACIÓN", self.font_small, btn_rect.center, txt_color)
        self.confirm_rect = btn_rect

    def draw_debug_case_hint(self):
        # Desactivado por defecto para no revelar nada. Cambia False a True al probar.
        if False:
            text = f"DEBUG: {self.case.title} / {self.case.killer}-{self.case.weapon}-{self.case.room}"
            surf = self.font_small.render(text, True, (255, 220, 150))
            self.screen.blit(surf, (10, 10))

    def draw(self):
        self.draw_background()
        if self.current_screen == ScreenID.ARMAS:
            self.draw_weapons_screen()

        for hotspot in self.hotspots:
            hotspot.draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen)

        self.draw_actions_counter()
        self.draw_rain()
        self.draw_debug_case_hint()

        if self.fade_alpha > 0:
            fade = pygame.Surface(self.screen.get_size())
            fade.fill((0, 0, 0))
            fade.set_alpha(self.fade_alpha)
            self.screen.blit(fade, (0, 0))
            self.fade_alpha = max(self.fade_target, self.fade_alpha - self.fade_speed)

        pygame.display.flip()

    # ── Eventos ──────────────────────────────────────────────
    def handle_events(self):
        mouse = pygame.mouse.get_pos()

        for button in self.buttons:
            button.update(mouse)
        for hotspot in self.hotspots:
            hotspot.update(mouse)
        for card in self.weapon_cards:
            card.update(mouse)
        for group_name, cards in self.accuse_cards.items():
            for card in cards:
                card.update(mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.build_layout()

            for button in self.buttons:
                button.handle_event(event)
            for hotspot in self.hotspots:
                hotspot.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_screen == ScreenID.ARMAS:
                    for card in self.weapon_cards:
                        if card.hover:
                            self.investigate_weapon(card.key)
                            break
                elif self.current_screen == ScreenID.ACUSACION:
                    self.handle_accusation_click(event.pos)

    def handle_accusation_click(self, pos: Tuple[int, int]):
        for kind, cards in self.accuse_cards.items():
            for card in cards:
                if card.rect.collidepoint(pos):
                    for c in cards:
                        c.selected = False
                    card.selected = True
                    if kind == "suspect":
                        self.selected_suspect = card.key
                    elif kind == "weapon":
                        self.selected_weapon = card.key
                    elif kind == "room":
                        self.selected_room = card.key
                    return

        if hasattr(self, "confirm_rect") and self.confirm_rect.collidepoint(pos):
            self.confirm_accusation()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        self.build_layout()

    # ── Loop ─────────────────────────────────────────────────
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update_rain()
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        MooreGame().run()
    except Exception as exc:
        pygame.quit()
        print("\nOcurrió un error al iniciar el juego:")
        print(exc)
        print("\nRevisa que estés ejecutando este archivo desde la carpeta del proyecto")
        print("y que la carpeta assets/ exista con todas las imágenes.")
        raise
