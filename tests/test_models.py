"""Pruebas de integración para verificar la disponibilidad de los modelos de IA."""

import os
import sys

# Añadir el directorio raíz al path para poder importar la carpeta app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.load_model import MODEL_PATH


def test_weight_model_file_exists():
    """Verificar la existencia del archivo de pesos conv_MLP en la raíz.

    Asegura que el archivo binario del modelo 'conv_MLP_84.h5' esté
    disponible en el directorio del proyecto antes de la ejecución.
    """
    # Usamos la constante real importada desde load_model.py
    assert os.path.exists(MODEL_PATH), f"Falta el modelo {MODEL_PATH} en la raíz."