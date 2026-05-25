"""Pruebas unitarias para el módulo de preprocesamiento de imágenes."""

import os
import sys
import numpy as np

# Añadir el directorio raíz al path para poder importar la carpeta app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.preprocess_img import preprocess


def test_preprocess_shape():
    """Validar que el preprocesamiento devuelva las dimensiones correctas.

    Crea una imagen dummy aleatoria y verifica que el tensor final
    tenga la forma (1, 512, 512, 1) y el tipo float32 requeridos.
    """
    # Simula una imagen de entrada de 100x100 píxeles con 3 canales
    dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    processed = preprocess(dummy_img)

    # El modelo funcional espera exactamente estas dimensiones de entrada
    msg_dimension = "La dimensión final debe ser (1, 512, 512, 1)"
    assert processed.shape == (1, 512, 512, 1), msg_dimension
    assert processed.dtype == np.float32, "El tipo de dato debe ser float32"


def test_preprocess_empty_image():
    """Validar que el preprocesamiento maneje imágenes con valores en cero.

    Asegura que una matriz completamente negra no genere errores de división
    por cero durante la normalización de la imagen.
    """
    black_img = np.zeros((100, 100, 3), dtype=np.uint8)
    processed = preprocess(black_img)

    assert processed is not None, "El resultado no debería ser None"
    assert processed.shape == (1, 512, 512, 1)