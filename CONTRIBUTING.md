# Guía para contribuir a PyUron

Gracias por tu interés en PyUron. Esta guía explica cómo preparar el entorno,
ejecutar las comprobaciones y enviar cambios.

## Requisitos

- Python 3.12 o superior.
- Git.
- GPU compatible con OpenGL 3.3+ (solo necesaria para ejecutar ventanas y ejemplos).
- [`uv`](https://docs.astral.sh/uv/) recomendado, aunque también puedes usar `pip`.

## Preparar el entorno

```bash
git clone https://github.com/aminbena010-ai/PyUron.git
cd PyUron

# Opción recomendada
uv sync --extra dev

# Opción con pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Comprobaciones antes de enviar un cambio

```bash
# Tests (76+ pruebas, sin necesidad de ventana gráfica)
uv run pytest

# Linter
uv run ruff check .

# Ejemplo jugable (requiere entorno gráfico)
uv run python main.py
```

Si usas `pip`, ejecuta `pytest` y `ruff check .` directamente.

## Estructura del código

| Carpeta | Responsabilidad |
| --- | --- |
| `pyuron/core/` | Motor, ventana, configuración, logs y temporizadores |
| `pyuron/graphics/` | Shaders, mallas, materiales, texturas y cámaras |
| `pyuron/math/` | Vectores, matrices, transformaciones y AABB |
| `pyuron/physics/` | Colisiones, formas y raycast |
| `pyuron/scene/` | Nodos, luces, cámaras, sprites y serialización |
| `pyuron/audio/` | Gestión de música, efectos y tonos procedurales |
| `pyuron/input/` | Mapeo de acciones de teclado y ratón |
| `pyuron/resources/` | Carga y caché de assets |
| `examples/` | Juegos de ejemplo |
| `tests/` | Pruebas unitarias |

## Estilo de código

- Sigue el estilo existente del proyecto.
- Usa nombres descriptivos y anotaciones de tipos cuando aporten claridad.
- No añadas comentarios obvios; documenta solo decisiones no evidentes.
- Mantén las funciones pequeñas y con una única responsabilidad.
- No incluyas dependencias nuevas sin justificarlo en el pull request.
- No subas archivos generados (`__pycache__`, `.venv`, `build/`, `dist/`, logs).

## Commits

Se recomienda el formato [Conventional Commits](https://www.conventionalcommits.org/es/):

```text
feat: añade sistema de partículas 2D
fix: corrige colisión de esferas contra paredes
docs: actualiza guía de instalación
test: cubre el caso de raycast sin impacto
refactor: simplifica la carga de shaders
chore: actualiza dependencias
```

Tipos habituales: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`.

## Flujo de trabajo

1. Crea una rama desde `main`/`master`:

   ```bash
   git switch -c feat/nombre-corto
   ```

2. Realiza los cambios y añade o actualiza tests cuando corresponda.
3. Ejecuta `pytest` y `ruff check .`.
4. Registra el cambio en `CHANGELOG.md` dentro de `[No publicado]`.
5. Haz commit con un mensaje claro.
6. Sube la rama y abre un pull request:

   ```bash
   git push -u origin feat/nombre-corto
   ```

## Publicar cambios en GitHub

Para el mantenimiento del repositorio principal:

```bash
# Revisar qué se va a subir
git status
git diff

# Añadir y confirmar cambios
git add .
git commit -m "feat: describe el cambio"

# Subir la rama actual
git push
```

Comprueba el remoto configurado con:

```bash
git remote -v
```

Si el repositorio remoto usa otra rama por defecto, ajusta el push:

```bash
git push origin main
```

## Pull requests

Incluye en la descripción:

- Qué problema resuelve o qué funcionalidad añade.
- Cómo se probó (comandos ejecutados).
- Capturas o GIF si el cambio es visual.
- Referencias a issues relacionadas.

Antes de enviarlo, verifica que:

- [ ] Los tests pasan.
- [ ] El linter no reporta errores nuevos.
- [ ] `CHANGELOG.md` está actualizado.
- [ ] No se añadieron archivos generados o secretos.
- [ ] La documentación refleja el cambio.

## Reportar errores

Abre un issue incluyendo:

- Sistema operativo y versión de Python.
- Versión de PyUron (`python -c "import pyuron; print(pyuron.__version__)"`).
- Pasos para reproducir el error.
- Mensaje de error completo o captura.
- Comportamiento esperado y comportamiento observado.

## Licencia

Al contribuir aceptas que tus cambios se publiquen bajo la licencia MIT del proyecto.
