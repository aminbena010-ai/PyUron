import pygame


class Window:
    """Posee la ventana de Pygame y su contexto OpenGL."""

    def __init__(
        self,
        title: str,
        width: int,
        height: int,
        resizable: bool = True,
        vsync: bool = True,
        gl_major: int = 3,
        gl_minor: int = 3,
    ) -> None:
        pygame.display.init()

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, gl_major)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, gl_minor)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if resizable:
            flags |= pygame.RESIZABLE

        try:
            self.surface = pygame.display.set_mode(
                (width, height), flags, vsync=int(vsync)
            )
        except TypeError:
            self.surface = pygame.display.set_mode((width, height), flags)

        pygame.display.set_caption(title)
        self.width = width
        self.height = height

    def set_size(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)

    def swap_buffers(self) -> None:
        pygame.display.flip()

    def close(self) -> None:
        pygame.display.quit()
