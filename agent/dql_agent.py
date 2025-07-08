import torch
import random
import numpy as np
from collections import deque
from snake_game.game import SnakeGameAI, Direction, Point
from .model import Linear_QNet
from config import MAX_MEMORY, BATCH_SIZE, LR, GAMMA, BLOCK_SIZE

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # Parámetro para la aleatoriedad (exploración)
        self.gamma = GAMMA  # Factor de descuento
        self.memory = deque(maxlen=MAX_MEMORY)  # Estructura de datos que auto-elimina elementos viejos
        
        # Modelo y optimizador
        self.model = Linear_QNet()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=LR)
        self.criterion = torch.nn.MSELoss() # Mean Squared Error como función de pérdida

    def get_state(self, game: SnakeGameAI):
        """
        Construye el vector de estado de 11 elementos a partir del juego.
        """
        head = game.head
        
        # Puntos de referencia para comprobar colisiones
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)
        
        # Dirección actual (one-hot encoded)
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN
        
        state = [
            # Peligro inmediato (recto, derecha, izquierda)
            # Peligro recto
            (dir_r and game._is_collision(point_r)) or 
            (dir_l and game._is_collision(point_l)) or 
            (dir_u and game._is_collision(point_u)) or 
            (dir_d and game._is_collision(point_d)),

            # Peligro a la derecha (relativo a la dirección actual)
            (dir_u and game._is_collision(point_r)) or 
            (dir_d and game._is_collision(point_l)) or 
            (dir_l and game._is_collision(point_u)) or 
            (dir_r and game._is_collision(point_d)),

            # Peligro a la izquierda (relativo a la dirección actual)
            (dir_d and game._is_collision(point_r)) or 
            (dir_u and game._is_collision(point_l)) or 
            (dir_r and game._is_collision(point_u)) or 
            (dir_l and game._is_collision(point_d)),
            
            # Dirección del movimiento
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Ubicación de la comida
            game.food.x < game.head.x,  # Comida a la izquierda
            game.food.x > game.head.x,  # Comida a la derecha
            game.food.y < game.head.y,  # Comida arriba
            game.food.y > game.head.y   # Comida abajo
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        """Almacena una tupla de experiencia en la memoria de repetición."""
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        """Entrena el modelo usando un lote de experiencias de la memoria."""
        if len(self.memory) > BATCH_SIZE:
            # Muestreo aleatorio para romper la correlación entre experiencias consecutivas
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory # Usar toda la memoria si es más pequeña que el BATCH_SIZE

        # Descomprimir las tuplas en listas separadas
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """Entrena el modelo con la última experiencia obtenida."""
        self.train_step(state, action, reward, next_state, done)
    
    def train_step(self, state, action, reward, next_state, done):
        """
        Realiza un paso de entrenamiento completo (el corazón del algoritmo DQL).
        Calcula la pérdida usando la ecuación de Bellman y actualiza los pesos del modelo.
        """
        # Convertir a tensores de PyTorch
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        
        # Ajustar dimensiones si es un solo elemento (entrenamiento de memoria corta)
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1. Obtener los Q-valores predichos por el modelo actual (Q(s, a))
        pred = self.model(state)
        
        # 2. Calcular los Q-valores objetivo usando la ecuación de Bellman:
        # Q_nuevo = r si done, o r + gamma * max(Q(s')) si not done
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            
            # El target para la acción tomada es el Q_nuevo
            target[idx][torch.argmax(action[idx]).item()] = Q_new
            
        # 3. Calcular la pérdida y optimizar
        self.optimizer.zero_grad()  # Limpiar gradientes anteriores
        loss = self.criterion(target, pred) # Comparar Q-target con Q-predicción
        loss.backward() # Propagar el error hacia atrás (backpropagation)
        self.optimizer.step() # Actualizar los pesos del modelo

    def get_action(self, state):
        """
        Decide una acción usando la estrategia épsilon-greedy.
        Con probabilidad épsilon, toma una acción aleatoria (exploración).
        Con probabilidad 1-épsilon, toma la mejor acción según el modelo (explotación).
        """
        # El valor de épsilon disminuye a medida que el agente juega más partidas,
        # favoreciendo la explotación sobre la exploración con el tiempo.
        # Esta es una heurística simple; se pueden usar decaimientos más complejos.
        self.epsilon = 80 - self.n_games
        
        final_move = [0, 0, 0] # [recto, derecha, izquierda]
        if random.randint(0, 200) < self.epsilon:
            # Acción aleatoria (Exploración)
            move_idx = random.randint(0, 2)
            final_move[move_idx] = 1
        else:
            # Acción basada en el modelo (Explotación)
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            move_idx = torch.argmax(prediction).item()
            final_move[move_idx] = 1
            
        return final_move