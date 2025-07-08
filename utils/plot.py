# utils/plot.py

import plotly.graph_objects as go
import os
from typing import List

# Importamos la ruta de la carpeta desde el archivo de configuración central
from config import PLOT_FOLDER_PATH

def save_plot(scores: List[float], mean_scores: List[float]):
    """
    Crea y guarda un gráfico interactivo y estático del progreso del entrenamiento
    utilizando la biblioteca Plotly.

    Esta función genera dos archivos en la carpeta definida en `config.py`:
    1. Un archivo .html interactivo.
    2. Un archivo .png estático.

    Args:
        scores (List[float]): Una lista con los puntajes de cada partida.
        mean_scores (List[float]): Una lista con la media móvil de los puntajes.
    """
    # Asegurarse de que la carpeta de destino exista
    if not os.path.exists(PLOT_FOLDER_PATH):
        os.makedirs(PLOT_FOLDER_PATH)

    # Crear una nueva figura de Plotly
    fig = go.Figure()

    # Eje X: Número de partidas (empezando desde 1)
    game_numbers = list(range(1, len(scores) + 1))

    # --- Añadir Trazas (las líneas del gráfico) ---

    # 1. Trazado para el puntaje de cada partida
    fig.add_trace(go.Scatter(
        x=game_numbers, 
        y=scores,
        mode='lines',
        name='Puntaje por Partida',
        line=dict(color='rgba(67, 160, 239, 0.8)') # Un azul suave
    ))

    # 2. Trazado para la media de puntajes
    fig.add_trace(go.Scatter(
        x=game_numbers, 
        y=mean_scores,
        mode='lines',
        name='Media de Puntajes',
        line=dict(color='rgba(239, 83, 80, 1.0)', dash='dash') # Un rojo punteado
    ))

    # --- Personalizar el Diseño del Gráfico ---
    fig.update_layout(
        title=dict(text="<b>Progreso del Entrenamiento con Deep Q-Learning</b>", x=0.5),
        xaxis_title="Número de Partidas",
        yaxis_title="Puntaje",
        legend_title_text="Leyenda",
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        # 'x unified' es excelente: muestra los datos de ambas líneas al pasar el ratón
        hovermode="x unified",
        template="plotly_white" # Un tema limpio y profesional
    )

    # --- Guardar los Archivos ---

    # 1. Guardar como archivo HTML interactivo
    html_file_path = os.path.join(PLOT_FOLDER_PATH, 'training_progress.html')
    fig.write_html(html_file_path)
    print(f"📈 Gráfico interactivo guardado en: {html_file_path}")

    # 2. Guardar como imagen estática (requiere la biblioteca `kaleido`)
    try:
        png_file_path = os.path.join(PLOT_FOLDER_PATH, 'training_progress.png')
        fig.write_image(png_file_path, width=1200, height=700, scale=1)
        print(f"🖼️ Gráfica de progreso estática guardada en: {png_file_path}")
    except ValueError as e:
        print("\nADVERTENCIA: No se pudo guardar la imagen estática (.png).")
        print("Asegúrate de tener 'kaleido' instalado: pip install kaleido")
        print(f"Error original: {e}")