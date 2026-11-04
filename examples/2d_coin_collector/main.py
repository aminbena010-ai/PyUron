"""PyUron 0.9 — Demo: jugador + monedas + HUD + save/load JSON."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pygame

from pyuron import (
    AnimatedSprite2D, Camera2DNode, Engine, EngineConfig, Log,
    Anchor, LabelNode, Scene, Texture2D, Vector3, __version__, make_tone,
    install_exception_hook, show_banner,
)


PLAYER_SPEED = 5.0
SAVE_PATH = "saves/demo_0.9.json"


def make_player_spritesheet() -> np.ndarray:
    fs, n = 32, 4
    img = np.zeros((fs, fs * n, 4), dtype=np.uint8)
    yy, xx = np.meshgrid(np.arange(fs), np.arange(fs), indexing="ij")
    for f in range(n):
        cy = fs // 2 + int(np.sin(f / n * 2 * math.pi) * 3)
        mask = (xx - fs // 2) ** 2 + (yy - cy) ** 2 < 10 ** 2
        img[yy[mask], xx[mask] + f * fs] = (100, 180, 255, 255)
    return img


def make_coin_sheet() -> np.ndarray:
    fs, n = 24, 4
    img = np.zeros((fs, fs * n, 4), dtype=np.uint8)
    yy, xx = np.meshgrid(np.arange(fs), np.arange(fs), indexing="ij")
    for f in range(n):
        rx = 10 * abs(math.cos(f / n * math.pi)) + 4
        mask = ((xx - fs // 2) / rx) ** 2 + ((yy - fs // 2) / 10) ** 2 < 1.0
        img[yy[mask], xx[mask] + f * fs] = (255, 210, 60, 255)
    return img


def build_fresh_scene(sprite_shader, textures: dict) -> Scene:
    scene = Scene("Demo2D")

    cam = Camera2DNode("Cam")
    cam.size_y = 12.0
    scene.add_child(cam)

    player = AnimatedSprite2D(textures["player"], sprite_shader,
                              frame_w=32, frame_h=32, name="Player")
    player.size = (1.5, 1.5)
    player.fps = 8.0
    player.z_index = 10
    scene.add_child(player)

    for i in range(6):
        angle = (i / 6) * 2 * math.pi
        coin = AnimatedSprite2D(textures["coin"], sprite_shader,
                                frame_w=24, frame_h=24, name=f"Coin{i}")
        coin.size = (0.8, 0.8)
        coin.fps = 6.0
        coin.transform.position = Vector3(
            math.cos(angle) * 5.0, math.sin(angle) * 3.0, 0.0,
        )
        coin.z_index = 5
        scene.add_child(coin)

    # HUD
    hud = LabelNode("Monedas: 0/6", font_size=32,
                    shader=sprite_shader, name="HUD")
    hud.ppu = 24.0
    hud.anchor = Anchor.TOP_LEFT  # ← Anclaje automático
    hud.transform.position = Vector3(-10.0, 5.5, 0.0) # solo posición, el anchor hace el resto
    hud.z_index = 100
    scene.add_child(hud)

    return scene


def main() -> None:
    install_exception_hook()
    show_banner(__version__)

    config = EngineConfig(
        title=f"PyUron {__version__} — HUD + Save/Load",
        width=1280, height=720, resizable=True, vsync=True,
        clear_color=(0.05, 0.06, 0.09, 1.0),
    )
    engine = Engine(config)
    engine.initialize()

    inp = engine.input
    inp.bind_action("left",  pygame.K_a, pygame.K_LEFT)
    inp.bind_action("right", pygame.K_d, pygame.K_RIGHT)
    inp.bind_action("up",    pygame.K_w, pygame.K_UP)
    inp.bind_action("down",  pygame.K_s, pygame.K_DOWN)
    inp.bind_action("save",  pygame.K_g)
    inp.bind_action("load",  pygame.K_l)
    inp.bind_action("quit",  pygame.K_ESCAPE)

    audio = engine.audio
    if audio._initialized:
        audio.register_sound("pick", make_tone(990, 0.06, volume=0.4))
        audio.register_sound("save", make_tone(660, 0.08, volume=0.3))
        audio.register_sound("load", make_tone(440, 0.10, volume=0.3))

    assets = engine.assets
    sprite_shader = assets.get_shader("assets/shaders/sprite.vert",
                                       "assets/shaders/sprite.frag")

    # Texturas compartidas (se pasan al contexto de save/load)
    textures = {
        "player": Texture2D.from_array(make_player_spritesheet()),
        "coin":   Texture2D.from_array(make_coin_sheet()),
    }
    Log.ok("Texturas procedurales listas")

    scene = build_fresh_scene(sprite_shader, textures)
    engine.set_scene(scene)
    Log.ok("Escena 2D lista")
    Log.info("WASD mover · G guardar · L cargar · ESC salir")

    score = {"value": 0}

    def update(dt: float) -> None:
        nonlocal scene

        # Referencias (se regeneran al cargar)
        player = scene.children[1]
        for c in scene.children:
            if c.name == "Player":
                player = c
        hud = None
        for c in scene.children:
            if c.name == "HUD":
                hud = c

        vx = (1.0 if inp.is_action_pressed("right") else 0.0) - \
             (1.0 if inp.is_action_pressed("left") else 0.0)
        vy = (1.0 if inp.is_action_pressed("up") else 0.0) - \
             (1.0 if inp.is_action_pressed("down") else 0.0)
        p = player.transform.position
        player.transform.position = Vector3(
            p.x + vx * PLAYER_SPEED * dt,
            p.y + vy * PLAYER_SPEED * dt,
            0.0,
        )
        if vx < 0: player.flip_x = True
        elif vx > 0: player.flip_x = False

        # Pickup
        for coin in list(scene.children):
            if not isinstance(coin, AnimatedSprite2D) or not coin.name.startswith("Coin"):
                continue
            if not coin.visible:
                continue
            cp = coin.transform.position
            dx = cp.x - p.x
            dy = cp.y - p.y
            if dx * dx + dy * dy < 1.0:
                coin.visible = False
                score["value"] += 1
                if audio._initialized:
                    audio.play_sfx("pick")
                if hud is not None:
                    hud.set_text(f"Monedas: {score['value']}/6")

        # Save
        if inp.is_action_just_pressed("save"):
            scene.save_json(SAVE_PATH)
            Log.ok(f"Escena guardada → {SAVE_PATH}")
            if audio._initialized:
                audio.play_sfx("save")

        # Load
        if inp.is_action_just_pressed("load"):
            if Path(SAVE_PATH).exists():
                # Detach para no acumular hijos
                for c in scene.children[:]:
                    scene.remove_child(c)
                try:
                    new_scene = Scene.load_json(
                        SAVE_PATH,
                        sprite_shader=sprite_shader,
                        textures={
                            "tex_Player": textures["player"],
                            "tex_Coin0": textures["coin"],
                            "tex_Coin1": textures["coin"],
                            "tex_Coin2": textures["coin"],
                            "tex_Coin3": textures["coin"],
                            "tex_Coin4": textures["coin"],
                            "tex_Coin5": textures["coin"],
                            "tex_HUD": None,  # HUD no necesita textura previa
                        },
                    )
                    engine.set_scene(new_scene)
                    scene = new_scene
                    Log.ok(f"Escena cargada ← {SAVE_PATH}")
                    if audio._initialized:
                        audio.play_sfx("load")
                except Exception as e:
                    Log.err(f"Error al cargar: {e}")
            else:
                Log.warn(f"No existe {SAVE_PATH} — pulsa G para guardar primero")

        if inp.is_action_pressed("quit"):
            engine.stop()

    engine.on_update(update)
    engine.run()

    assets.dispose_all()
    Log.info(f"Juego terminado · monedas: {score['value']}/6")


if __name__ == "__main__":
    main()
