import os
from functools import lru_cache
import tensorflow as tf

# Configuración de compatibilidad
MODEL_PATH = "conv_MLP_84.h5"

# Se define una función con caché para cargar el modelo una sola vez. Se maneja la ausencia del modelo
@lru_cache(maxsize=1)
def model_fun(model_path=MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el modelo en '{model_path}'.")
    return tf.keras.models.load_model(model_path, compile=False)