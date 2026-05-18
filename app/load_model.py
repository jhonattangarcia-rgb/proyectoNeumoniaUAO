"""Model loading utilities for the pneumonia detection application."""

# Standard library imports
import os
from functools import lru_cache

# Third-party imports
import tensorflow as tf

# Compatibility configuration
MODEL_PATH: str = "conv_MLP_84.h5"

# Se define una función con caché para cargar el modelo una sola vez. Se maneja la ausencia del modelo
@lru_cache(maxsize=1)
def model_fun(model_path: str = MODEL_PATH) -> tf.keras.Model:
    """Load and return the saved TensorFlow model.

    Args:
        model_path: Path to the saved model file.

    Returns:
        A loaded TensorFlow Keras model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el modelo en '{model_path}'.")
    return tf.keras.models.load_model(model_path, compile=False)