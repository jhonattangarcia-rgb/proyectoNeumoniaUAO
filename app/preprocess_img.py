"""Image preprocessing utilities used before model inference."""

# Third-party imports
import cv2
import numpy as np


def preprocess(array: np.ndarray) -> np.ndarray:
    """Resize, normalize, and prepare an image array for model input.

    Args:
        array: Input image array in BGR or grayscale format.

    Returns:
        A preprocessed array shaped for the model.
    """
    array = cv2.resize(array, (512, 512))
    # Se valida que la imagen tenga 3 canales antes de convertir a escala de grises,
    # para evitar errores con imágenes ya en escala de grises
    if len(array.shape) == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    array = clahe.apply(array)
    # Se transforma a float32 y se normaliza a [0, 1] para asegurar compatibilidad
    # con el modelo, evitando errores de tipo
    array = array.astype(np.float32) / 255.0
    array = np.expand_dims(array, axis=-1)
    array = np.expand_dims(array, axis=0)
    return array
