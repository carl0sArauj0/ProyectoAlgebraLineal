import pygame
from snake_game.game import SnakeGameAI, Direction
from snake_game.menu import run_setup_menu
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_SPEED_HUMAN

def get_action_from_key(game, key):

    # Por defecto, la acción es seguir recto
    action = [1, 0, 0]

    # Estado actual
    current_direction = game.direction

    # Mapeo de teclas a nuevas direcciones
    key_map = {
        pygame.K_UP: Direction.UP,
        pygame.K_DOWN: Direction.DOWN,
        pygame.K_LEFT: Direction.LEFT,
        pygame.K_RIGHT: Direction.RIGHT,
    }
    
    # Si la tecla no es una flecha, no hacemos nada (sigue recto)
    if key not in key_map:
        return action

    new_direction = key_map[key]

    # Evitar que la serpiente se mueva en la dirección opuesta a la actual
    if (current_direction == Direction.UP and new_direction == Direction.DOWN) or \
       (current_direction == Direction.DOWN and new_direction == Direction.UP) or \
       (current_direction == Direction.LEFT and new_direction == Direction.RIGHT) or \
       (current_direction == Direction.RIGHT and new_direction == Direction.LEFT):
        return action # Movimiento inválido, seguir recto

    # Determinar si es un giro a la derecha o a la izquierda relativo a la dirección actual
    # Esto es un poco más complejo que solo cambiar la dirección, pero se adapta a la entrada de play_step
    
    # Definimos los giros en el sentido de las agujas del reloj
    clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    idx = clock_wise.index(current_direction)
    
    if new_direction == clock_wise[(idx + 1) % 4]:
        action = [0, 1, 0]  # Giro a la derecha
    elif new_direction == clock_wise[(idx - 1) % 4]:
        action = [0, 0, 1]  # Giro a la izquierda
    # Si la nueva dirección es la misma que la actual, la acción [1, 0, 0] ya está correcta.
    
    return action

def main():
    
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game - Configuración')

    # 1. Ejecutar el menú de configuración
    start_pos, traps = run_setup_menu(screen)

    # Si el usuario cierra la ventana en el menú, salimos
    if start_pos is None:
        pygame.quit()
        return

    # 2. Configurar el juego con los parámetros del menú
    pygame.display.set_caption('Snake Game - Jugador Humano')
    game = SnakeGameAI(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, start_pos=start_pos, traps=list(traps))
    clock = pygame.time.Clock()
    
    running = True
    last_key = None

    # 3. Bucle principal del juego
    while running:
        # Captura de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Guardamos la última tecla presionada para procesarla una vez por frame
                last_key = event.key
        
        # Procesar la entrada del jugador
        action = get_action_from_key(game, last_key)
        last_key = None # Reseteamos para que la acción no se repita si no se presiona nada

        # Avanzar un paso en el juego
        reward, game_over, score = game.play_step(action)
        
        # Dibujar el estado actual del juego
        game.draw(screen)
        pygame.display.flip()
        
        # Si el juego termina, mostrar mensaje y esperar para salir
        if game_over:
            font = pygame.font.Font(None, 50)
            text = font.render(f"Juego Terminado. Puntaje: {score}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(3000) # Esperar 3 segundos antes de cerrar
            running = False
        
        # Controlar la velocidad del juego
        clock.tick(GAME_SPEED_HUMAN)

    pygame.quit()

if __name__ == '__main__':
    main()