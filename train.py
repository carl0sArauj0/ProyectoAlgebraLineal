import pygame

# Importaciones de nuestro proyecto
from agent.dql_agent import Agent
from snake_game.game import SnakeGameAI, Point
from utils.plot import save_plot # Usamos nuestra utilidad de graficado con Plotly
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GAME_SPEED_AGENT, NUM_EPISODES,
    MODEL_FILE_NAME
)

# --- Configuración de la Visualización ---
VISUALIZE_TRAINING = False  # Cambia a True si quieres ver el entrenamiento en tiempo real

def train():
    """
    Función principal que ejecuta el bucle de entrenamiento completo.
    Orquesta la interacción entre el agente y el entorno del juego,
    registra el progreso y guarda tanto el modelo como los gráficos.
    """
    # --- Listas para el seguimiento de métricas ---
    scores = []
    mean_scores = []
    total_score = 0
    record_score = 0
    
    # --- Inicialización del Agente y el Entorno ---
    agent = Agent()
    
    start_pos = Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    traps = [] 
    game = SnakeGameAI(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, start_pos=start_pos, traps=traps)

    # --- Inicialización de Pygame (si se visualiza) ---
    if VISUALIZE_TRAINING:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game - Entrenamiento DQL")
        clock = pygame.time.Clock()

    # --- Bucle de Entrenamiento Principal ---
    while agent.n_games < NUM_EPISODES:
        
        if VISUALIZE_TRAINING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        # --- Interacción Agente-Entorno ---
        
        # 1. Obtener el estado actual del juego
        state_old = agent.get_state(game)

        # 2. El agente decide una acción basada en el estado actual
        final_move = agent.get_action(state_old)

        # 3. El entorno ejecuta la acción y devuelve los resultados
        # ESTA LÍNEA DEFINE reward, done, y score.
        reward, done, score = game.play_step(final_move)
        
        # 4. Obtener el nuevo estado después de la acción
        state_new = agent.get_state(game)

        # 5. Entrenar al agente en el paso inmediato (memoria a corto plazo)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # 6. Almacenar la transición (s, a, r, s') en la memoria de repetición
        agent.remember(state_old, final_move, reward, state_new, done)

        # --- Lógica de Fin de Partida ---
        if done:
            # Acciones cuando la partida termina:
            
            # a) Reiniciar el juego para el siguiente episodio
            game = SnakeGameAI(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, start_pos=start_pos, traps=traps)
            agent.n_games += 1
            
            # b) Entrenar la memoria a largo plazo con un lote de experiencias pasadas
            agent.train_long_memory()

            # c) Comprobar si se ha batido un nuevo récord
            if score > record_score:
                record_score = score
                # Guardar el modelo solo cuando mejora
                agent.model.save(file_name=MODEL_FILE_NAME)
                print(f"¡Nuevo récord! Puntaje: {record_score}. Modelo guardado.")

            # d) Imprimir progreso en la consola
            print(f'Partida: {agent.n_games}, Puntaje: {score}, Récord: {record_score}')

            # e) Actualizar las métricas para el graficado
            scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            mean_scores.append(mean_score)
            
            # f) Generar y guardar el gráfico a intervalos para no ralentizar el proceso
            if agent.n_games % 25 == 0 and agent.n_games > 0:
                save_plot(scores, mean_scores)

        # --- Actualización de la Pantalla (si se visualiza) ---
        if VISUALIZE_TRAINING:
            game.draw(screen)
            pygame.display.flip()
            clock.tick(GAME_SPEED_AGENT)

    # --- Acciones Finales al Terminar el Entrenamiento ---
    print("Entrenamiento finalizado.")
    # Guardar la gráfica final con todos los datos
    save_plot(scores, mean_scores)

    if VISUALIZE_TRAINING:
        pygame.quit()

# --- Punto de Entrada del Script ---
if __name__ == '__main__':
    train()