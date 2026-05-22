"""""Image loading utilities for DICOM and standard image files."""

from pathlib import Path
from typing import Tuple

# Third-party imports
import cv2
import numpy as np
import pydicom as dicom
from PIL import Image as PILImage


def read_dicom_file(path: str) -> Tuple[np.ndarray, PILImage.Image]:
    """Read a DICOM file and return the image as array and a PIL image.

    Args:
        path: Path to a DICOM file.

    Returns:
        A tuple containing the RGB image array and a PIL Image object.
    """
    try:
        # MEJORA: Uso de la API moderna de PyDicom. Reemplaza el comando obsoleto
        # 'read_file'.
        ds = dicom.dcmread(path)
        img_array = ds.pixel_array

        # MEJORA: Escudo contra división por cero en formatos médicos.
        # Si el archivo DICOM viene vacío o corrupto (máximo = 0), el código divide por 1.
        # Esto previene alertas ruidosas y caídas de la interfaz gráfica de Tkinter.
        img_norm = (
            np.maximum(img_array, 0) / (img_array.max() if img_array.max() != 0 else 1)
        ) * 255.0

        img_uint8 = np.uint8(img_norm)
        img_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)

        # MEJORA: Corrección del bug de pantalla negra en la interfaz de usuario.
        # Convierte los datos médicos crudos de 16 bits a formato RGB estándar de 8 bits.
        # Garantiza que Tkinter pueda dibujar la radiografía con contraste óptimo en pantalla.
        img2show = PILImage.fromarray(img_rgb)
        return img_rgb, img2show

    except Exception as e:
        raise ValueError(f"Error leyendo DICOM: {e}")


def read_jpg_file(path: str) -> Tuple[np.ndarray, PILImage.Image]:
    """Read a JPG or PNG file and return the image as array and a PIL image.

    Args:
        path: Path to a JPG, JPEG, or PNG file.

    Returns:
        A tuple containing the RGB image array and a PIL Image object.
    """
    try:
        img_data = np.fromfile(path, np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError(f"No se pudo cargar la imagen en {path}")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img2show = PILImage.fromarray(img_rgb)
        return img_rgb, img2show

    except Exception as e:
        raise ValueError(f"No se pudo cargar la imagen en {path}. Detalle: {e}")


def read_png_file(path: str) -> Tuple[np.ndarray, PILImage.Image]:
    """Read a PNG file and return the image as array and a PIL image.

    Args:
        path: Path to a PNG file.

    Returns:
        A tuple containing the RGB image array and a PIL Image object.
    """
    try:
        img_data = np.fromfile(path, np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError(f"No se pudo cargar la imagen PNG en {path}")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img2show = PILImage.fromarray(img_rgb)
        return img_rgb, img2show

    except Exception as e:
        raise ValueError(f"No se pudo cargar la imagen PNG en {path}. Detalle: {e}")


# Extensiones soportadas por cada función
DICOM_EXTENSIONS = {".dcm", ".dicom"}
JPG_EXTENSIONS = {".jpg", ".jpeg"}
PNG_EXTENSIONS = {".png"}


def read_image(path: str) -> Tuple[np.ndarray, PILImage.Image]:
    """Interface común para leer cualquier tipo de imagen soportada.

    Detecta automáticamente el tipo de archivo por su extensión
    y llama a la función de lectura correspondiente.

    Args:
        path: Ruta al archivo de imagen (DICOM, JPG, JPEG o PNG).

    Returns:
        A tuple containing the RGB image array and a PIL Image object.

    Raises:
        ValueError: Si el formato no es soportado o la imagen no se puede leer.
    """
    extension = Path(path).suffix.lower()

    if extension in DICOM_EXTENSIONS:
        return read_dicom_file(path)
    elif extension in JPG_EXTENSIONS:
        return read_jpg_file(path)
    elif extension in PNG_EXTENSIONS:
        return read_png_file(path)
    else:
        raise ValueError(
            f"Formato no soportado: '{extension}'. "
            f"Formatos válidos: DICOM (.dcm), JPG (.jpg, .jpeg), PNG (.png)"
        )
    