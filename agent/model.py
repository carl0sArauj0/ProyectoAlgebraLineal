import torch
import torch.nn as nn
import torch.nn.functional as F
import os
from config import INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, MODEL_FOLDER_PATH

class Linear_QNet(nn.Module):
    """
    Red Neuronal para aproximar la función Q.
    Es una red feed-forward simple con una capa oculta.
    """
    def __init__(self):
        super().__init__()
        # Definimos las capas. Las dimensiones se importan desde config.py para modularidad.
        # Capa de entrada (tamaño del estado) a capa oculta.
        self.linear1 = nn.Linear(INPUT_SIZE, HIDDEN_SIZE)
        # Capa oculta a capa de salida (número de acciones).
        self.linear2 = nn.Linear(HIDDEN_SIZE, OUTPUT_SIZE)

    def forward(self, x):
        # Aplicamos la función de activación ReLU después de la primera capa.
        # ReLU es una elección estándar y efectiva para evitar el problema del desvanecimiento del gradiente.
        x = F.relu(self.linear1(x))
        
        # La capa de salida no tiene función de activación.
        # Esto es porque queremos los Q-valores brutos, no probabilidades (como daría Softmax).
        # El valor más alto corresponderá a la mejor acción predicha.
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        """
        Guarda el estado del modelo en un archivo.
        """
        # Asegurarse de que la carpeta de modelos exista
        if not os.path.exists(MODEL_FOLDER_PATH):
            os.makedirs(MODEL_FOLDER_PATH)

        file_path = os.path.join(MODEL_FOLDER_PATH, file_name)
        
        # Guardamos solo el state_dict, que contiene los pesos y sesgos aprendidos.
        # Es la forma recomendada y más portable.
        torch.save(self.state_dict(), file_path)