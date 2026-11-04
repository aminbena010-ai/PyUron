# Revisión de arquitectura — PyUron 1.0.1

Documento de referencia para la refactorización incremental 1.0.0 → 1.0.1.
No sustituye a la API pública (`pyuron/__init__.py`), que se mantiene estable.

## 1. Arquitectura actual observada

```text
pyuron/
├── core/        Engine, Window, EngineConfig, Logger, timers, errores
├── graphics/    Renderer, Shader, Mesh, Material, Texture2D, cámaras matriciales
├── math/        Vector2/3, Transform, matrices, AABB (sin dependencias del motor)
├── physics/     PhysicsWorld, Shape/Box/Sphere, raycast
├── scene/       Node/Node2D/Node3D, Scene, luces, cámaras-nodo, sprites, serialización
├── audio/       AudioManager, make_tone
├── input/       InputManager
├── resources/   AssetManager (caché de shaders/texturas/mallas), cargador OBJ
└── scripting/   reservado (vacío)
```

`Engine.run()` es el único punto de entrada del runtime. `Scene` hereda de
`Node` y actúa como raíz del árbol, agregando física, luces, cámara y render.

## 2. Mapa de dependencias

Reglas observadas:

- `math` → (numpy). No importa nada del motor. Capa base.
- `graphics` → `math`, OpenGL, pygame (texturas/texto). No importa `scene` ni `core`.
- `physics` → `math`. No importa `scene` ni `graphics`.
- `scene` → `math`, `graphics`, `physics`. No importa `core` ni `audio`/`input`.
- `core` → `graphics`, `scene`, `audio`, `input`, `pygame` (coordina todo).
- `resources` → `graphics`.
- `audio`/`input` → `pygame` + `core.logger`.

Ciclos detectados en 1.0.0 (imports diferidos dentro de funciones):

- `scene.scene ↔ scene.serialization`
- `math.__init__ ↔ math.transform` (vía `pyuron.math.matrix`)

Además, `scene/__init__.py` registraba los tipos de nodo como efecto
secundario del import (side-effect no evidente).

## 3. Problemas demostrados

| # | Problema | Evidencia | Gravedad |
|---|---|---|---|
| P1 | Ciclo de vida del motor no transaccional | `Engine.initialize` crea ventana y renderer sin rollback; `run()` llama a `initialize()` fuera del `try/finally` | Alta |
| P2 | `assert` en el bucle de ejecución | `pyuron/core/engine.py` (`assert self.renderer is not None ...`) se elimina con `python -O` | Media |
| P3 | `shutdown()` no idempotente ni ordenado; llama a `pygame.quit()` aunque nunca se inicializara | `Engine.shutdown` | Alta |
| P4 | Física con `dt` variable | `scene._process(dt)` → `PhysicsWorld.step(dt)` sin acumulador | Alta (determinismo) |
| P5 | Jerarquía sin invariantes | `Node.add_child` permite `a.add_child(a)` y ciclos → recursión infinita en `_process` | Alta |
| P6 | Signo/profundidad Sphere-Box incorrectos con el centro de la esfera dentro de la caja | ternario anidado en `PhysicsWorld._resolve_sphere_box` | Alta |
| P7 | Registro de tipos como efecto de import | bucle en `scene/__init__.py` | Media |
| P8 | `world_position` duplicado y semánticamente inconsistente | `Node3D.world_position` y `_BaseCameraNode.world_position`; `Sprite2D.world_model` compone matrices | Media |
| P9 | Sin tests de ciclo de vida, jerarquía, arquitectura | `tests/` | Alta (riesgo de regresión) |
| P10 | `pyrr` declarada y sin uso | `pyproject.toml` | Baja |
| P11 | Versión de serialización hardcodeada | `scene/serialization.py` (`"version": "1.0.0"`) | Baja |

## 4. Arquitectura objetivo mínima

Se conserva la estructura de paquetes y la API pública. Cambios:

- **Core** coordina; no posee lógica de simulación. El paso de simulación se
  aísla en `Engine._update(dt)` para poder probarse sin ventana.
- **Scene** mantiene la jerarquía con invariantes verificables (sin ciclos).
- **Physics** recibe `dt` ya resuelto por el core (opcionalmente fijo).
- **Serialization** se registra de forma perezosa (`ensure_default_node_types()`),
  sin efectos al importar `pyuron.scene`.
- **Propiedad de recursos**: el `Engine` libera lo que crea (ventana, contexto,
  quad compartido de sprites). `AssetManager` lo libera su dueño (`dispose_all`).

### Reglas de dependencia

1. `math` no importa ninguna otra capa del motor.
2. `graphics`/`physics` no importan `scene` ni `core`.
3. `scene` no importa `core`.
4. `core` puede importar todas las capas inferiores (es el coordinador).
5. Ningún módulo importa `pyuron` (el paquete raíz) a nivel de módulo.
6. Dependencias opcionales (PySide6) nunca se importan desde el runtime.

## 5. Cambios compatibles e incompatibles

Compatibles:

- `Node.remove_child` pasa a devolver `bool` (antes `None`); los llamadores que
  ignoran el retorno no se ven afectados.
- `EngineConfig` gana `fixed_dt: float | None = None` (por defecto, comportamiento
  actual). `EngineConfig` es `slots`, el campo se añade al final.
- Nuevos tests y documentación.

Incompatibles (deliberadamente evitados):

- Renombrar/mover clases públicas.
- Cambiar la firma de `Scene._process`, `PhysicsWorld.step`, `Renderer.draw`.
- Sustituir `SceneTree` por ECS.
- Hacer el paso fijo obligatorio.

Cambio de comportamiento observable (corregido, no incompatible de API):

- `Node.add_child(self)` o añadir un ancestro lanza `ValueError` en vez de
  provocar recursión infinita.
- Colisión Sphere-Box con centro dentro de la caja resuelve por la cara de menor
  salida (antes: signo/profundidad incorrectos).

## 6. Plan de migración

1. Serialización perezosa + romper ciclo `math.transform`.
2. `Engine`: init con rollback, `_update(dt)` extraído, `shutdown` idempotente,
   sin `assert`.
3. `fixed_dt` opt-in con acumulador y límite de pasos por frame.
4. Invariantes del `SceneTree` + documentación del contrato de mutación.
5. Liberación del quad compartido en el cierre del motor.
6. Corrección Sphere-Box con test de regresión previo.
7. Limpieza (pyrr, versión serializada), tests de arquitectura.

## 7. Criterios de aceptación

- `pytest` y `ruff check .` en verde.
- Test que demuestra el bug Sphere-Box antes de la corrección y pasa después.
- Tests de ciclo de vida del `Engine` sin ventana ni contexto OpenGL.
- Tests de jerarquía (auto-ciclo, ciclo de ancestros, reparentado).
- Test de arquitectura: `import pyuron` no inicializa display ni importa PySide6,
  y no hay ciclos de import entre módulos.
- API pública (`pyuron.__all__`) intacta.
- Versión 1.0.1 coherente en `pyuron.__version__`, `pyproject.toml` y changelog.

## 8. Decisiones pospuestas

- **Interpolación de render con paso fijo**: requiere cambios en el contrato de
  `update`/render; se pospone.
- **Pausa del motor**: no existe API pública; añadirla implica definir su
  interacción con timers y audio. Se pospone.
- **Árbol de transformaciones completo (rotación/escala de ancestros)**: la
  física y las cámaras solo suman posiciones; cambiarlo altera el
  comportamiento de juegos existentes. Se documenta como limitación.
- **Eliminación diferida de nodos durante `update`**: el recorrido usa una copia
  de la lista de hijos; se documenta el comportamiento actual, sin cola de
  borrado.
- **Backends de render alternativos / ECS**: sin caso de uso que los justifique.
