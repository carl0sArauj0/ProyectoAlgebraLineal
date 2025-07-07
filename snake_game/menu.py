import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE, Point,
    COLOR_BACKGROUND, COLOR_GRID, COLOR_SNAKE_HEAD, COLOR_TRAP, COLOR_TEXT
)

def run_setup_menu(screen):

    start_pos = None
    traps = set()  # Usamos un set para evitar duplicados y facilitar la eliminación

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None  # Señal para salir del programa principal

            # Manejo del teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if start_pos:  # Solo se puede iniciar si se ha elegido un punto de partida
                        running = False
                    else:
                        print("Por favor, selecciona una posición de inicio para la serpiente.")

            # Manejo del ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                grid_x, grid_y = mx // BLOCK_SIZE, my // BLOCK_SIZE
                clicked_point = Point(grid_x * BLOCK_SIZE, grid_y * BLOCK_SIZE)

                if start_pos is None:
                    start_pos = clicked_point
                else:
                    if clicked_point == start_pos:
                        continue # No se puede poner una trampa en el inicio
                    
                    if clicked_point in traps:
                        traps.remove(clicked_point) # Quitar trampa si ya existe
                    else:
                        traps.add(clicked_point) # Añadir trampa

        # --- Lógica de dibujado ---
        screen.fill(COLOR_BACKGROUND)

        # Dibujar la cuadrícula
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))
            
        # Dibujar la posición de inicio
        if start_pos:
            pygame.draw.rect(screen, COLOR_SNAKE_HEAD, (start_pos.x, start_pos.y, BLOCK_SIZE, BLOCK_SIZE))

        # Dibujar las trampas
        for trap in traps:
            pygame.draw.rect(screen, COLOR_TRAP, (trap.x, trap.y, BLOCK_SIZE, BLOCK_SIZE))

        # Dibujar texto de instrucciones
        if not start_pos:
            text_surface = font.render('1. Haz clic para elegir el inicio de la serpiente', True, COLOR_TEXT)
        else:
            text_surface = font.render('2. Haz clic para poner/quitar trampas. Presiona ENTER para iniciar.', True, COLOR_TEXT)
        
        screen.blit(text_surface, (20, 20))

        pygame.display.flip()
        clock.tick(30) 

    return start_pos, list(traps)