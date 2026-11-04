# Changelog

Todos los cambios importantes de PyUron se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
versionado usa [Semantic Versioning](https://semver.org/lang/es/).

> Las fechas solo se incluyen cuando están disponibles en el historial de Git;
> el resto de versiones conserva su número y contenido.

## [No publicado]

### Añadido

- Integración continua con GitHub Actions para ejecutar tests y lint.
- Guía `CONTRIBUTING.md` con el flujo de trabajo del proyecto.
- Archivos `.gitattributes` y `.editorconfig` para mantener un estilo consistente.

## [1.0.0] - 2026-11-04

El hito final: un motor completo para juegos 2D y 3D.

### Añadido

- **UI con anclajes (`Anchor`)**: los textos y sprites se alinean automáticamente
  a las esquinas, al centro y a otros puntos de referencia.
- **Estructura limpia**: ejemplos organizados en `examples/` para facilitar el uso
  del motor.
- **Documentación completa**: README con instalación, estructura y ejemplos,
  además de este `CHANGELOG.md`.
- **76 tests automáticos** que cubren matemáticas, física, input, audio,
  serialización, sprites, texturas y otros sistemas del motor.

### Cambiado

- API pública unificada y organizada en `pyuron/__init__.py`.
- Versión del proyecto unificada en `1.0.0`.

## [0.9.0]

Interfaz, guardado y persistencia.

### Añadido

- **Textos (HUD)**: el motor puede escribir texto en pantalla usando fuentes.
- **Guardado en JSON**: capacidad de guardar el estado de una partida y volver a
  cargarlo después.
- **Persistencia**: al cerrar y abrir el juego se puede recuperar el progreso.

## [0.8.0]

El motor 2D.

### Añadido

- **Sprites**: dibujado eficiente de imágenes 2D.
- **Animaciones**: soporte para hojas de sprites (*spritesheets*) y personajes
  animados.
- **Cámara 2D**: cámara ortográfica pensada para juegos de plataformas.
- **Ejemplo jugable**: un personaje que recoge monedas giratorias.

## [0.7.0]

Formas y disparos.

### Añadido

- **Colisiones de esferas** además de las cajas.
- **Raycast**: rayos invisibles para saber a qué se apunta o se dispara.
- **Timers y cooldowns**: control de la cadencia de disparo.
- **Mini-juego de disparos** como ejemplo de integración.

## [0.6.0]

Controles y audio.

### Añadido

- **InputManager**: mapeo de acciones para que una tecla pueda significar
  "saltar", "disparar", etc.
- **AudioManager**: sistema de sonido con generación de tonos musicales por
  código, sin necesidad de archivos externos.
- **Gameplay**: cubo-jugador que se mueve, salta y suena al aterrizar.

## [0.5.0]

Física y colisiones.

### Añadido

- **Gravedad**: los objetos empiezan a caer.
- **Colisiones AABB**: detección y separación de cajas que chocan.
- **Fricción y rebote**: ajustes para que los cubos se sientan sólidos y no como
  plumas.

## [0.4.0] - 2026-11-03

Iluminación y cámara FPS.

### Añadido

- **Luces**: luz direccional (sol) y luces puntuales (bombillas) con sombreado
  Blinn-Phong.
- **Modelos 3D**: cargador de archivos `.obj` para usar cubos y otros modelos.
- **Cámara FPS**: control en primera persona con WASD y ratón.
- **AssetManager**: caché para no cargar el mismo archivo dos veces.

## [0.3.0]

Escenas y texturas.

### Añadido

- **Sistema de nodos**: árbol jerárquico con nodos padre e hijos.
- **Texturas**: carga de imágenes y generación de texturas de ajedrez por código.
- **Materiales**: unificación de shaders, texturas y colores.
- **Logro**: un cuadrado texturizado girando en pantalla.

## [0.2.0]

Renderizado 3D básico.

### Añadido

- **Shaders**: compilación de código GLSL para la tarjeta gráfica.
- **Mallas**: sistema para dibujar triángulos con VAO/VBO.
- **Matemáticas**: vectores, matrices y transformaciones.
- **Cámara**: primera cámara 2D/3D.
- **Logro**: un triángulo girando en pantalla.

## [0.1.0]

El núcleo del motor.

### Añadido

- **Ventana**: creación con Pygame y contexto OpenGL 3.3.
- **Bucle principal**: ejecución del motor, medición de FPS y cierre limpio.
- **Diagnóstico**: sistema de logs con colores (`[+]`, `[-]`, `[?]`) y tiempos de
  carga.

[No publicado]: https://github.com/aminbena010-ai/PyUron/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v1.0.0
[0.9.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.9.0
[0.8.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.8.0
[0.7.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.7.0
[0.6.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.6.0
[0.5.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.5.0
[0.4.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.4.0
[0.3.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.3.0
[0.2.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.2.0
[0.1.0]: https://github.com/aminbena010-ai/PyUron/releases/tag/v0.1.0
