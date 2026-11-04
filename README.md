# PyUron 1.0.2

**Motor de videojuegos modular, Python-first, 2D y 3D.**

[![CI](https://github.com/aminbena010-ai/PyUron/actions/workflows/ci.yml/badge.svg)](https://github.com/aminbena010-ai/PyUron/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

PyUron no es un simple wrapper de Pygame. Es un motor construido desde cero en Python
con renderizado OpenGL moderno (3.3+), física, audio, sistema de nodos jerárquico y una
arquitectura pensada para crecer.

## Características

- **Ventana y contexto**: Pygame-ce + PyOpenGL (Core Profile 3.3+) con VSync y redimensionado.
- **Escenas**: nodos jerárquicos (`Node`, `Node2D`, `Node3D`, `Scene`) con recolección automática de luces y cámaras.
- **Renderizado 3D**: shaders GLSL 330, iluminación Blinn-Phong (luz direccional y hasta 4 luces puntuales), carga de modelos `.obj`.
- **Renderizado 2D**: sprites, hojas de animación (`AnimatedSprite2D`), texto (`LabelNode`), anclajes (`Anchor`) y batching.
- **Física**: AABB, formas de colisión (`BoxShape`, `SphereShape`), resolución de colisiones, rebote, fricción, gravedad y `raycast`.
- **Audio**: música, SFX con mezclador multicanal y generación de tonos procedurales (`make_tone`).
- **Input**: mapeo de acciones para teclado y ratón (`is_action_pressed("jump")`).
- **Serialización**: guardado y carga de escenas completas en JSON.
- **Diagnóstico**: logs con colores ANSI, timestamps, métricas de FPS y errores legibles.

## Requisitos

- Python **3.12+**
- GPU con soporte **OpenGL 3.3+**
- Linux, Windows o macOS

## Instalación

```bash
git clone https://github.com/aminbena010-ai/PyUron.git
cd PyUron
```

Con `uv` (recomendado):

```bash
uv sync --extra dev
uv run python main.py
```

Con `pip` y un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python main.py
```

## Ejemplos

El proyecto incluye un ejemplo jugable en `examples/`:

- **2D Coin Collector**: jugador animado, monedas giratorias, HUD interactivo, física 2D y guardado/carga de estado en JSON.

Lánzalo desde el menú principal:

```bash
uv run python main.py
```

## Estructura del proyecto

```text
PyUron/
├── pyuron/                    # Código fuente del motor
│   ├── core/                  # Engine, Window, Logger, Config, Timers
│   ├── graphics/              # Shaders, mallas, materiales, texturas, cámaras
│   ├── math/                  # Vectores, matrices, transformaciones, AABB
│   ├── physics/               # Colisiones, formas, raycast
│   ├── scene/                 # Nodos, luces, cámaras, sprites, serialización
│   ├── audio/                 # AudioManager y tonos procedurales
│   ├── input/                 # InputManager con mapeo de acciones
│   └── resources/             # AssetManager y cargador OBJ
├── examples/2d_coin_collector/
├── assets/                    # Modelos .obj y shaders GLSL base
├── tests/                     # 76 tests unitarios con pytest
├── .github/workflows/ci.yml   # Integración continua
├── CHANGELOG.md               # Historial de versiones
├── CONTRIBUTING.md            # Guía para contribuir
├── pyproject.toml
└── README.md
```

## Tests

La suite no requiere contexto gráfico para ejecutarse:

```bash
uv run pytest
```

También puedes ejecutar el linter:

```bash
uv run ruff check .
```

## Historial de cambios

Consulta [CHANGELOG.md](CHANGELOG.md) para ver todas las versiones y cada actualización del motor.

## Contribuir

Las instrucciones de instalación, estilo de commits y flujo de trabajo están en
[CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
