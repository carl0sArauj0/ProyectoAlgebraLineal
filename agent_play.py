import pygame
import torch
import os

# Importaciones de nuestro proyecto
from agent.dql_agent import Agent
from snake_game.game import SnakeGameAI
from snake_game.menu import run_setup_menu
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MODEL_FOLDER_PATH, MODEL_FILE_NAME
)

# Velocidad a la que jugará el agente para que sea observable
GAME_SPEED_PLAYBACK = 20

def play():
    """
    Carga un agente entrenado y lo hace jugar en un tablero
    configurado por el usuario.
    """
    # --- Carga del Modelo Entrenado ---
    model_path = os.path.join(MODEL_FOLDER_PATH, MODEL_FILE_NAME)
    
    # 1. Verificar si el archivo del modelo existe
    try:
        # Cargamos los pesos (state_dict) en la CPU
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        print(f"Modelo '{MODEL_FILE_NAME}' cargado exitosamente.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo del modelo en '{model_path}'.")
        print("Por favor, ejecuta 'train.py' primero para entrenar y guardar un modelo.")
        return

    # --- Inicialización del Agente ---
    agent = Agent()
    # 2. Cargar los pesos en la arquitectura del modelo del agente
    agent.model.load_state_dict(state_dict)
    # 3. Poner el modelo en modo de evaluación
    # Esto es crucial: desactiva capas como Dropout o BatchNorm, asegurando
    # que la salida sea determinista.
    agent.model.eval()
    
    # 4. Forzar el modo de explotación (sin acciones aleatorias)
    # Al poner epsilon en un valor negativo, la condición para exploración nunca se cumplirá.
    agent.epsilon = -1 # Modo 100% explotación

    # --- Configuración del Juego a través del Menú ---
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game - Configuración para el Agente')
    
    start_pos, traps = run_setup_menu(screen)
    
    if start_pos is None: # El usuario cerró la ventana del menú
        pygame.quit()
        return

    # --- Bucle Principal del Juego ---
    pygame.display.set_caption('Snake Game - Agente DQL Jugando')
    game = SnakeGameAI(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, start_pos=start_pos, traps=list(traps))
    clock = pygame.time.Clock()
    
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # 1. Obtener el estado actual
        state = agent.get_state(game)
        
        # 2. Obtener la acción (será determinista gracias a epsilon = -1)
        action = agent.get_action(state)
        
        # 3. Realizar el movimiento y obtener el nuevo estado
        _, game_over, score = game.play_step(action)
        
        # 4. Dibujar el juego
        game.draw(screen)
        pygame.display.flip()
        
        # 5. Controlar la velocidad
        clock.tick(GAME_SPEED_PLAYBACK)

    # --- Fin de la Partida ---
    print(f"\nJuego terminado. El agente entrenado logró un puntaje de: {game.score}")
    
    # Mantener la ventana abierta por unos segundos para ver el resultado final
    pygame.time.wait(3000)
    pygame.quit()

# --- Punto de Entrada del Script ---
if __name__ == '__main__':
    play()