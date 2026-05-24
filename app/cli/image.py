"""Image utilities for CLI workflows."""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

from app.read_img import read_dicom_file, read_jpg_file

from .utils import ensure_folder

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".dcm"}


def read_image_file(file_path: Path) -> Tuple[np.ndarray, Image.Image]:
    """Read an image file and return the image data plus a PIL image.

    Args:
        file_path: Path to the image file.

    Returns:
        A tuple containing the image array and a PIL Image for display.

    Raises:
        ValueError: If the file extension is not supported.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".dcm":
        return read_dicom_file(str(file_path))
    if suffix in {".jpg", ".jpeg"}:
        return read_jpg_file(str(file_path))
    raise ValueError(f"Formato no soportado: {file_path}")


def save_numpy_image(image: np.ndarray, output_path: Path) -> None:
    """Save a numpy array as an image file.

    Args:
        image: Numpy array representing the image.
        output_path: Path where the image will be written.

    Raises:
        ValueError: If the image does not have 1 or 3 channels.
    """
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)

    if image.ndim == 2:
        mode = "L"
    elif image.ndim == 3 and image.shape[2] == 3:
        mode = "RGB"
    else:
        raise ValueError("La imagen debe tener 1 o 3 canales.")

    Image.fromarray(image, mode=mode).save(output_path)


def build_result_folder(output_base: Path, cedula: str) -> Path:
    """Build and ensure a result folder for the given patient ID.

    Args:
        output_base: Base output directory.
        cedula: Patient identifier used as folder name.

    Returns:
        The path to the created result folder.
    """
    folder = output_base / cedula
    return ensure_folder(folder)
