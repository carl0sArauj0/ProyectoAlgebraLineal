"""
Este archivo contiene todas las constantes y parámetros de configuración
para el juego Snake y el agente de Deep Q-Learning.
"""
import collections

# Representación de un punto en el espacio 2D del juego
Point = collections.namedtuple('Point', 'x, y')

# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA 
# Tamaño de cada bloque en la cuadrícula del juego
BLOCK_SIZE = 20

# Dimensiones de la ventana del juego 
SCREEN_WIDTH = 40 * BLOCK_SIZE  # 800 píxeles
SCREEN_HEIGHT = 30 * BLOCK_SIZE # 600 píxeles

# Velocidad del juego 
GAME_SPEED_HUMAN = 15
GAME_SPEED_AGENT = 100

# Paleta de colores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN = (0, 200, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Colores específicos del juego
COLOR_BACKGROUND = BLACK
COLOR_SNAKE_HEAD = GREEN
COLOR_SNAKE_BODY = (0, 150, 0)  # Un verde más oscuro
COLOR_FOOD = RED
COLOR_TRAP = YELLOW
COLOR_TEXT = WHITE
COLOR_GRID = GRAY



# CONFIGURACIÓN DEL AGENTE Y ENTRENAMIENTO (DEEP Q-LEARNING)
# Hiperparámetros
MAX_MEMORY = 100_000        # Tamaño máximo de la memoria de repetición 
BATCH_SIZE = 1000           # Tamaño del lote para el entrenamiento desde la memoria
LR = 0.001                  # Tasa de aprendizaje para el optimizador Adam
GAMMA = 0.9                 # Factor de descuento para recompensas futuras

# --- Modelo de Red Neuronal ---
INPUT_SIZE = 11
HIDDEN_SIZE = 256           # Número de neuronas en la capa oculta
OUTPUT_SIZE = 3             # Número de acciones posibles: [Recto, Derecha, Izquierda]

# --- Parámetros de Entrenamiento ---
# El número de juegos 
NUM_EPISODES = 1000

# CONFIGURACIÓN DE ARCHIVOS Y CARPETAS
# Carpeta donde se guardarán los modelos entrenados
MODEL_FOLDER_PATH = './trained_models'

# Nombre del archivo para el modelo
MODEL_FILE_NAME = 'dql_snake_model.pth'

# Carpeta para guardar gráficos de progreso
PLOT_FOLDER_PATH = './plots'