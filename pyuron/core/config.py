from dataclasses import dataclass


@dataclass(slots=True)
class EngineConfig:
    """Configuracion usada al crear una instancia del motor."""

    title: str = "PyUron"
    width: int = 1280
    height: int = 720
    resizable: bool = True
    vsync: bool = True
    gl_major: int = 3
    gl_minor: int = 3
    clear_color: tuple[float, float, float, float] = (0.055, 0.065, 0.085, 1.0)
    # None = paso variable (comportamiento 1.0.0). Si se define, la
    # actualización se ejecuta en pasos de esa duración (segundos).
    fixed_dt: float | None = None

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Las dimensiones de la ventana deben ser positivas.")
        if len(self.clear_color) != 4:
            raise ValueError("clear_color debe tener cuatro componentes.")
        if not all(0.0 <= c <= 1.0 for c in self.clear_color):
            raise ValueError("Los componentes de clear_color deben estar en [0, 1].")
        if self.fixed_dt is not None and self.fixed_dt <= 0.0:
            raise ValueError("fixed_dt debe ser positivo o None.")
