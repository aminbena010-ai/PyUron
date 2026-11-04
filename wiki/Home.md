# PyUron Wiki

**Motor de videojuegos modular, Python-first, 2D y 3D.**

> **Rol de esta wiki:** la [documentación web](https://aminbena010-ai.github.io/PyUron/) es la
> introducción y guía rápida (qué es, cómo instalarlo, cómo empezar). Esta wiki es la
> **referencia profunda**: arquitectura, módulos, conceptos, casos de uso y análisis
> técnico de cómo encaja todo.

**Versión actual:** `1.0.0` · **Python:** 3.12+ · **Render:** OpenGL 3.3+ Core · **Licencia:** MIT

---

## Índice

- [¿Qué es PyUron?](#qué-es-pyuron)
- [¿Por qué existe?](#por-qué-existe)
- [¿Para quién es?](#para-quién-es)
- [Instalación](#instalación)
- [Inicio rápido](#inicio-rápido)
- [Conceptos clave](#conceptos-clave)
- [Arquitectura en profundidad](#arquitectura-en-profundidad)
- [Cómo usarlo paso a paso](#cómo-usarlo-paso-a-paso)
- [Ejemplo incluido](#ejemplo-incluido)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Comandos](#comandos)
- [Casos de uso](#casos-de-uso)
- [Limitaciones y roadmap](#limitaciones-y-roadmap)
- [Contribuir](#contribuir)
- [Enlaces](#enlaces)

---

## ¿Qué es PyUron?

PyUron es un motor de videojuegos escrito **desde cero en Python**. No es un wrapper
de Pygame: usa pygame-ce para la ventana y los eventos, pero el renderizado, el árbol
de escena, la física, la carga de assets y la serialización son implementaciones
propias.

Su diseño es **modular**: cada responsabilidad vive en un paquete independiente
(`core`, `graphics`, `math`, `physics`, `scene`, `audio`, `input`, `resources`), de
modo que puedes leer un módulo sin entender todo el motor.

---

## ¿Por qué existe?

- **Python-first:** toda la API es Python idiomático, sin capas de C++ ni editores
  obligatorios.
- **Render moderno:** OpenGL 3.3+ Core con shaders GLSL 330, no un blitter 2D.
- **Arquitectura explícita:** escenas de nodos jerárquicas, transforms, cámaras y
  luces que la escena recoge automáticamente.
- **Aprendizaje real:** el código está separado por responsabilidades y la suite de
  tests corre sin contexto gráfico, lo que lo hace fácil de estudiar y extender.
- **Prototipado rápido:** sprites, texto, física, audio y guardado/carga de escenas
  listos para un demo jugable.

---

## ¿Para quién es?

| Perfil | Por qué le sirve |
| --- | --- |
| **Desarrolladores Python** | Un motor con API limpia para prototipos 2D/3D. |
| **Estudiantes** | Un motor pequeño y legible para entender cómo funciona uno real. |
| **Docentes** | Base para explicar bucles de juego, render, jerarquías y colisiones. |
| **Creadores de herramientas** | Nodos y serialización registrables para visores o editores. |

---

## Instalación

Requisitos: **Python 3.12+**, **GPU con OpenGL 3.3+** y Linux, Windows o macOS.

Con [`uv`](https://docs.astral.sh/uv/) (recomendado):

```bash
git clone https://github.com/aminbena010-ai/PyUron.git
cd PyUron
uv sync --extra dev
uv run python main.py
```

Con `pip` y un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python main.py
```

---

## Inicio rápido

Una escena mínima necesita un motor, una escena y una cámara:

```python
from pyuron import Engine, EngineConfig, Scene, Camera2DNode

engine = Engine(EngineConfig(title="Mi juego"))

scene = Scene("Nivel 1")
cam = Camera2DNode("Cam")
cam.size_y = 12.0
scene.add_child(cam)

engine.set_scene(scene)
engine.run()
```

`Engine.run()` inicializa ventana, renderer y audio, y entra en el bucle principal.
Los nodos se añaden con `add_child` y se actualizan sobrescribiendo `update(dt)`.

---

## Conceptos clave

### Nodos y escena

Todo objeto del juego es un `Node`. `Node2D` y `Node3D` añaden un `Transform`
(posición, rotación, escala). Una `Scene` es la raíz del árbol; recorre sus hijos
en cada frame y llama a `update(dt)`.

```python
class Spinner(Node2D):
    def update(self, dt):
        self.transform.rotation.z += dt * 90.0
```

### Transform

Cada `Node2D`/`Node3D` tiene `transform.position`, `rotation` y `scale`. Los sprites
y mallas acumulan los transforms de sus ancestros, así que mover un padre mueve a
toda su descendencia.

### Cámaras y luces

- `Camera2DNode` / `Camera3DNode` / `FPSCameraNode`.
- `DirectionalLightNode` (una) y `PointLightNode` (hasta cuatro).
- La escena localiza la cámara activa y recoge las luces automáticamente: no hay
  que registrarlas a mano.

### Render 2D y 3D

El render se hace en dos pasadas:

1. **3D:** mallas (`MeshInstance3D`) con shader `lit` e iluminación Blinn-Phong.
2. **2D:** sprites (`Sprite2D`, `AnimatedSprite2D`, `LabelNode`) ordenados por
   `z_index`, con depth test desactivado y blending alfa.

### Física

`PhysicsWorld` integra gravedad, damping y colisiones con substeps. Soporta
`BoxShape` y `SphereShape` con resolución Box-Box, Sphere-Sphere y Sphere-Box,
rebote por `restitution` y `raycast` contra la escena.

### Input

`InputManager` mapea acciones a teclas o botones de ratón:

```python
inp.bind_action("jump", pygame.K_SPACE)
if inp.is_action_just_pressed("jump"):
    ...
```

### Audio

`AudioManager` gestiona música y SFX multicanal; `make_tone` genera tonos
procedurales sin archivos externos.

### Assets

`AssetManager` carga y cachea modelos `.obj`, texturas y shaders. Los shaders base
viven en `assets/shaders/`.

### Serialización

`Scene.save_json(path)` y `Scene.load_json(path)` guardan y restauran el árbol
completo. Los tipos de nodo se resuelven mediante un registro:

```python
from pyuron.scene.serialization import register_node_type

@register_node_type
class MiNodo(Node2D):
    ...
```

---

## Arquitectura en profundidad

### Bucle principal (`pyuron/core/engine.py`)

```text
Engine.run()
  initialize()            # Window → Renderer/GL → Audio
  while is_running:
    clock.tick()          # delta_time
    input.begin_frame()   # eventos pygame
    on_update(dt)         # callbacks del usuario
    scene._process(dt)    # física + update del árbol
    renderer.begin_frame()
    on_render()
    scene.render(renderer)
    renderer.end_frame()
    window.swap_buffers()
    reportar FPS
  shutdown()
```

`Scene._process` hace dos cosas: recolecta los `PhysicsBody3D` del árbol y avanza
`PhysicsWorld`, y después recorre los nodos llamando a `update(dt)`.

### Pipeline de render (`pyuron/graphics/renderer.py`)

- `Renderer` encapsula el estado global (depth test, blending, viewport).
- `Shader`, `Mesh`, `Material` y `Texture2D` son los bloques de dibujo.
- `Renderer.draw(mesh, shader, uniforms)` resuelve uniforms por tipo: matrices 4×4,
  vec3, floats y texturas.
- `Scene.render` calcula la vista/proyección de la cámara y dibuja primero las
  mallas 3D y después los sprites 2D.

### Física (`pyuron/physics/world.py`)

- Integración con gravedad y `linear_damping` por substeps.
- Detección por pares y resolución iterativa (3 pasadas) con empuje y rebote.
- `BoxShape` usa AABB; `SphereShape` usa radio efectivo según escala.
- `raycast` devuelve el `RayHit` más cercano contra los cuerpos de la escena.

### Recursos y shaders

Los shaders GLSL (`basic`, `lit`, `sprite`) viven en `assets/shaders/` y se cargan
desde disco. `AssetManager` evita recargar el mismo recurso.

---

## Cómo usarlo paso a paso

1. **Instala** el entorno con `uv sync --extra dev`.
2. **Crea** un `Engine` con `EngineConfig` (título, tamaño, VSync, OpenGL).
3. **Construye** una `Scene` y añade una cámara con `add_child`.
4. **Añade nodos**: sprites, mallas, luces, cuerpos físicos o tus propias clases.
5. **Implementa** `update(dt)` en tus nodos para la lógica por frame.
6. **Ejecuta** `engine.set_scene(scene)` y `engine.run()`.
7. **Guarda** el estado con `scene.save_json("saves/nivel.json")` si lo necesitas.

---

## Ejemplo incluido

`examples/2d_coin_collector/` es un demo jugable con jugador animado, monedas
giratorias, HUD, física 2D y guardado/carga en JSON. Se lanza desde `main.py`.

Fragmento de construcción del jugador:

```python
player = AnimatedSprite2D(
    textures["player"], sprite_shader,
    frame_w=32, frame_h=32, name="Player",
)
player.size = (1.5, 1.5)
player.fps = 8.0
player.z_index = 10
scene.add_child(player)
```

---

## Estructura del proyecto

| Carpeta | Responsabilidad |
| --- | --- |
| `pyuron/core/` | Motor, ventana, configuración, logs y temporizadores |
| `pyuron/graphics/` | Shaders, mallas, materiales, texturas y cámaras |
| `pyuron/math/` | Vectores, matrices, transformaciones y AABB |
| `pyuron/physics/` | Colisiones, formas y raycast |
| `pyuron/scene/` | Nodos, luces, cámaras, sprites y serialización |
| `pyuron/audio/` | Música, efectos y tonos procedurales |
| `pyuron/input/` | Mapeo de acciones de teclado y ratón |
| `pyuron/resources/` | Carga y caché de assets |
| `examples/` | Juegos de ejemplo |
| `tests/` | Pruebas unitarias |
| `assets/` | Modelos `.obj` y shaders GLSL base |
| `docs/` | Documentación web (GitHub Pages) |

---

## Comandos

```bash
uv run python main.py         # lanzador de ejemplos (requiere GPU/GL)
uv run pytest                 # tests (no requieren ventana gráfica)
uv run ruff check .           # linter
uv sync --extra dev           # instalar dependencias de desarrollo
```

---

## Casos de uso

- **Prototipos jugables 2D:** sprites animados, HUD, colisiones y guardado de estado.
- **Demos 3D:** mallas `.obj`, iluminación direccional/puntual y cámara FPS.
- **Docencia:** ejemplo real de bucle de juego, jerarquías, render y física en Python.
- **Herramientas y editores:** nodos personalizados y serialización registrable.
- **Base para experimentos:** shaders propios, formas de colisión y componentes nuevos.

---

## Limitaciones y roadmap

Limitaciones actuales:

- Las colisiones usan **AABB**; no hay rotación avanzada de cajas.
- El backend de ventana y eventos es **pygame-ce**.
- No hay editor visual completo ni API de scripting separada.
- El paquete `pyuron/scripting/` está reservado y aún vacío.

Ideas de roadmap:

- Formas de colisión rotadas y mejor resolución de contactos.
- Más tipos de luces y sombras.
- Editor/visor de escenas sobre la serialización JSON.
- Sistema de scripting y recursos ampliado.

---

## Contribuir

1. Crea una rama: `git switch -c feat/nombre-corto`.
2. Implementa el cambio y añade/actualiza tests.
3. Ejecuta `pytest` y `ruff check .`.
4. Registra el cambio en `CHANGELOG.md` dentro de `[No publicado]`.
5. Haz commit con [Conventional Commits](https://www.conventionalcommits.org/es/).
6. Abre un pull request describiendo qué resuelve y cómo se probó.

Consulta [CONTRIBUTING.md](https://github.com/aminbena010-ai/PyUron/blob/main/CONTRIBUTING.md).

---

## Enlaces

- [Repositorio](https://github.com/aminbena010-ai/PyUron)
- [Documentación web](https://aminbena010-ai.github.io/PyUron/)
- [README](https://github.com/aminbena010-ai/PyUron/blob/main/README.md)
- [Guía de contribución](https://github.com/aminbena010-ai/PyUron/blob/main/CONTRIBUTING.md)
- [Changelog](https://github.com/aminbena010-ai/PyUron/blob/main/CHANGELOG.md)
- [Issues](https://github.com/aminbena010-ai/PyUron/issues)

---

## Licencia

MIT. Consulta [LICENSE](https://github.com/aminbena010-ai/PyUron/blob/main/LICENSE).
