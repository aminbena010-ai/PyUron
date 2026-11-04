# Changelog

Todos los cambios importantes de PyUron se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
versionado usa [Semantic Versioning](https://semver.org/lang/es/).

## [No publicado]

### Añadido

- Plantilla de integración continua con GitHub Actions.
- Archivo `CHANGELOG.md` para registrar cada actualización del motor.
- Guía `CONTRIBUTING.md` con el flujo de trabajo del proyecto.

## [1.0.0] - 2026-11-04

Primera versión completa del motor con soporte 2D y 3D.

### Añadido

- **Física completa**: `PhysicsWorld`, `AABB`, formas `BoxShape` y `SphereShape`,
  resolución de colisiones, rebote, fricción, gravedad y `raycast`.
- **Nodos de física**: `PhysicsBody3D` y `SphereBody3D` integrados en la escena.
- **Renderizado 2D**: `Sprite2D`, `AnimatedSprite2D`, `LabelNode`, sistema de
  `Anchor`, `MeshInstance2D` y batching de sprites.
- **Cámaras**: `Camera2DNode`, `Camera3DNode` y `FPSCameraNode` para primera persona.
- **Luces**: `DirectionalLightNode` y `PointLightNode` con recolección automática.
- **Audio**: `AudioManager` con música, SFX multicanal y tonos procedurales (`make_tone`).
- **Input**: `InputManager` con mapeo de acciones para teclado y ratón.
- **Serialización**: guardado y carga de escenas completas en JSON.
- **Temporizadores**: `Timer`, `Cooldown`, `Stopwatch` y decorador `timed`.
- **Diagnóstico**: hook global de excepciones, logs mejorados y métricas de rendimiento.
- **Ejemplo jugable**: `examples/2d_coin_collector` con animación, HUD, física
  y guardado/carga de estado.
- **Documentación**: README con instalación, estructura, ejemplos y uso.
- **Tests**: suite de 76 tests unitarios sin dependencia de contexto gráfico.

### Cambiado

- API pública unificada en `pyuron/__init__.py`.
- `AssetManager` ampliado con caché de shaders, texturas y mallas.
- Cargador OBJ integrado con el sistema de recursos.

## [0.4.0] - 2026-11-03

Primera base modular del motor.

### Añadido

- **Core**: `Engine`, `EngineConfig`, ventana, logger, errores y timers.
- **Gráficos**: renderizador OpenGL 3.3, shaders GLSL, mallas, materiales,
  texturas, `Camera2D` y `Camera3D`.
- **Matemáticas**: `Vector2`, `Vector3`, matrices, `Transform` y `AABB`.
- **Escenas**: `Node`, `Node2D`, `Node3D`, `Scene`, `MeshInstance3D` y cámaras.
- **Recursos**: `AssetManager` y carga básica de modelos `.obj`.
- **Assets**: modelos y shaders base en `assets/`.
- **Tests**: pruebas iniciales de matemáticas, configuración y texturas.

### Cambiado

- Arquitectura reorganizada en paquetes independientes (`core`, `graphics`,
  `math`, `physics`, `scene`, `audio`, `input`, `resources`).
- Dependencias gestionadas con `uv` y `pyproject.toml`.

[No publicado]: https://github.com/aminbena010-ai/PyUron/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v1.0.0
[0.4.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.4.0
