import pygame
import random
from enum import Enum
from config import Point, BLOCK_SIZE, COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY, COLOR_FOOD, COLOR_TRAP, COLOR_BACKGROUND, COLOR_TEXT

# Usamos Enum para una gestión de direcciones más limpia y segura
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGameAI:
    def __init__(self, width, height, start_pos, traps):
        self.width = width
        self.height = height
        self.start_pos = start_pos
        self.traps = traps

        # Estado inicial del juego
        self.direction = Direction.RIGHT  # Dirección de inicio por defecto
        self.head = self.start_pos
        self.snake = [self.head, 
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        
        while True:
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.food = Point(x, y)
            
            # La comida no puede estar en la serpiente ni en una trampa
            if self.food not in self.snake and self.food not in self.traps:
                break

    def play_step(self, action):
        
        # 1. Determinar la nueva dirección basada en la acción
        self._determine_direction(action)

        # 2. Mover la serpiente en la nueva dirección
        self._move(self.direction)
        self.snake.insert(0, self.head)

        # 3. Comprobar si el juego ha terminado (colisión)
        reward = 0
        game_over = False
        if self._is_collision():
            game_over = True
            reward = -10  # Penalización por morir
            return reward, game_over, self.score

        # 4. Comprobar si ha comido
        if self.head == self.food:
            self.score += 1
            reward = 10  # Recompensa por comer
            self._place_food()
        else:
            self.snake.pop()  # Si no come, se quita el último segmento

        return reward, game_over, self.score

    def _determine_direction(self, action):
        
        # Posibles direcciones en orden: Derecha, Izquierda, Arriba, Abajo
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if action[1] == 1:  # Giro a la derecha
            new_dir_idx = (idx + 1) % 4
            self.direction = clock_wise[new_dir_idx]
        elif action[2] == 1:  # Giro a la izquierda
            new_dir_idx = (idx - 1) % 4
            self.direction = clock_wise[new_dir_idx]
        # Si action[0] == 1, no hace falta hacer nada (sigue recto)

    def _is_collision(self, pt=None):
        
        if pt is None:
            pt = self.head
        
        # Colisión con las paredes
        if pt.x > self.width - BLOCK_SIZE or pt.x < 0 or pt.y > self.height - BLOCK_SIZE or pt.y < 0:
            return True
        # Colisión con su propio cuerpo
        if pt in self.snake[1:]:
            return True
        # Colisión con una trampa
        if pt in self.traps:
            return True
        
        return False

    def _move(self, direction):
        
        x, y = self.head.x, self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        
        self.head = Point(x, y)

    def draw(self, screen):
        
        screen.fill(COLOR_BACKGROUND)
        
        # Dibujar serpiente
        for i, pt in enumerate(self.snake):
            if i == 0: # Cabeza
                pygame.draw.rect(screen, COLOR_SNAKE_HEAD, (pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            else: # Cuerpo
                pygame.draw.rect(screen, COLOR_SNAKE_BODY, (pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        # Dibujar comida
        pygame.draw.rect(screen, COLOR_FOOD, (self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Dibujar trampas
        for trap in self.traps:
            pygame.draw.rect(screen, COLOR_TRAP, (trap.x, trap.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Dibujar puntaje
        font = pygame.font.Font(None, 36)
        text = font.render(f"Puntaje: {self.score}", True, COLOR_TEXT)
        screen.blit(text, [10, 10])