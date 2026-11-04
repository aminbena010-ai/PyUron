# PyUron — Contexto para agentes IA

Este archivo evita que un agente tenga que leer todo el repositorio desde cero.
Léelo completo antes de empezar una tarea y consulta solo los archivos que el
**mapa** indique. Si cambias arquitectura, comandos o estructura, actualiza este
archivo en el mismo cambio.

## Qué es el proyecto

PyUron es un motor de videojuegos modular **Python-first**, 2D y 3D, construido
desde cero (no es un wrapper de Pygame). Renderiza con **OpenGL 3.3+ Core**,
tiene escena de nodos jerárquica, física, audio, input y serialización JSON.

- Versión actual: **1.0.0** (`pyuron.__version__`).
- Python **3.12+**. Dependencias: `pygame-ce`, `PyOpenGL`, `numpy`, `pyrr`.
- Dev: `pytest`, `ruff`. Opcional: `PySide6` (extra `editor`).
- Licencia MIT. Repo: `github.com/aminbena010-ai/PyUron`.

## Comandos (usar `uv` si está disponible)

```bash
uv sync --extra dev          # instalar entorno
uv run python main.py        # lanzador de ejemplos (requiere GPU/GL)
uv run pytest                # tests (NO requieren contexto gráfico)
uv run ruff check .          # linter obligatorio
```

Equivalentes con pip/venv: `pip install -e ".[dev]"`, `pytest`, `ruff check .`.

Antes de terminar cualquier tarea: **pytest + ruff check . en verde**.
Añadir/actualizar tests en `tests/` para lógica nueva o corregida.

## Mapa del repositorio

```text
PyUron/
├── main.py                  # Lanzador de ejemplos (menú por consola)
├── pyuron/                  # Código del motor (API pública en __init__.py)
│   ├── core/                # Engine, Window, Config, Logger, Timers, banner, errores
│   ├── graphics/            # Renderer, Shader, Mesh, Material, Texture2D, cámaras, procedural
│   ├── math/                # Vector2/3, Transform, matrices, AABB
│   ├── physics/             # PhysicsWorld, Shape/Box/Sphere, raycast
│   ├── scene/               # Nodos, Scene, luces, cámaras, sprites, labels, serialización
│   ├── audio/               # AudioManager, make_tone
│   ├── input/               # InputManager (mapa de acciones)
│   ├── resources/           # AssetManager, cargador OBJ
│   └── scripting/           # (vacío, reservado)
├── examples/2d_coin_collector/main.py
├── assets/                  # cube.obj + shaders GLSL (basic, lit, sprite)
├── tests/                   # Suite pytest (no abre ventana)
├── .github/workflows/ci.yml # CI: ruff + pytest en Python 3.12 y 3.13
├── CHANGELOG.md             # Keep a Changelog; cambios en [No publicado]
├── CONTRIBUTING.md          # Flujo de contribución
└── pyproject.toml           # Deps, ruff (line-length 100), pytest
```

### Archivos clave

| Necesitas…                        | Mira en |
| --- | --- |
| Ciclo de vida, loop, eventos      | `pyuron/core/engine.py` (`Engine.run`) |
| Ventana/contexto GL               | `pyuron/core/window.py`, `graphics/renderer.py` |
| Config del motor                  | `pyuron/core/config.py` (`EngineConfig`) |
| Jerarquía de nodos                | `pyuron/scene/node.py`, `node2d.py`, `node3d.py` |
| Escena y su render                | `pyuron/scene/scene.py` |
| Sprites / animación / texto       | `scene/sprite2d.py`, `animated_sprite2d.py`, `label_node.py` |
| Cámaras y luces                   | `scene/camera_node.py`, `fps_camera.py`, `light_node.py` |
| Serialización de escenas          | `scene/serialization.py` |
| Shaders/mallas/materiales/texturas| `graphics/shader.py`, `mesh.py`, `material.py`, `texture.py` |
| Shaders GLSL base                 | `assets/shaders/*.vert|.frag` |
| Física / colisiones / raycast     | `physics/world.py`, `shapes.py`, `raycast.py` |
| Vectores, matrices, AABB          | `math/vector.py`, `matrix.py`, `transform.py`, `aabb.py` |
| Audio                             | `audio/audio_manager.py` |
| Input y acciones                  | `input/input_manager.py` |
| Carga de assets / OBJ             | `resources/assets.py`, `obj_loader.py` |
| API que ve el usuario             | `pyuron/__init__.py` (y los `__init__.py` de cada paquete) |

### Flujo de ejecución

`Engine.run()` → `initialize()` (Window → Renderer/GL → Audio) → bucle:
`clock.tick` → `input.begin_frame` + eventos → callbacks `on_update` →
`scene._process(dt)` (recorre nodos y llama `update`) → `renderer.begin_frame` →
callbacks `on_render` → `scene.render(renderer)` → `end_frame` + `swap_buffers` →
métricas FPS. `Node._process` propaga `update(dt)` a los hijos.

## Reglas de trabajo para agentes

- **Lee el mapa primero**; abre solo los archivos relevantes. No recorras el repo entero.
- **No leas** `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `build/`, `dist/`.
- Sigue el estilo existente y los patrones de los módulos vecinos.
- **No añadas dependencias** sin justificarlo; el proyecto es deliberadamente ligero.
- No edites archivos generados ni comitees secretos/artefactos.
- Documenta el cambio en `CHANGELOG.md` dentro de `## [No publicado]`.
- Commits estilo **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`,
  `refactor:`, `perf:`, `build:`, `ci:`, `chore:`.
- No hagas commit ni push salvo que el usuario lo pida explícitamente.
- Al terminar: ejecuta `pytest` y `ruff check .`; reporta el resultado.
- Si cambias estructura, comandos o API pública, **actualiza este archivo**.

## Convenciones de código

- Python 3.12+, anotaciones de tipos cuando aporten claridad.
- `ruff`: line-length **100**, reglas `E4,E7,E9,F`; `E701`/`E702` ignoradas.
- Preferir composición de nodos y `add_child`; el motor recoge luces/cámaras de la escena.
- Nombres descriptivos, funciones pequeñas y una sola responsabilidad.
- Evitar comentarios obvios; documentar solo decisiones no evidentes.
- La suite de tests no debe requerir ventana ni contexto OpenGL real.
