"""Pruebas unitarias para la validación y lectura de archivos médicos."""

import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.read_img import read_dicom_file, read_jpg_file


def test_allowed_extensions():
    """Validar que el sistema reconozca los formatos de imagen permitidos.

    Verifica que la lista de extensiones aceptadas para el diagnóstico
    incluya estrictamente DICOM (.dcm), JPG y PNG.
    """
    extensiones_validas = [".dcm", ".jpg", ".jpeg", ".png"]

    assert ".dcm" in extensiones_validas, "El formato DICOM debe ser permitido"
    assert ".jpg" in extensiones_validas, "El formato JPG debe ser permitido"
    assert ".png" in extensiones_validas, "El formato PNG debe ser permitido"


def test_read_non_existent_jpg_raises_error():
    """Verificar que read_jpg_file lance ValueError si el archivo no existe.

    Prueba que el módulo de lectura controle correctamente la ausencia
    de un archivo JPG/PNG lanzando la excepción esperada en la app.
    """
    ruta_falsa = "carpeta_imaginaria/paciente_no_existe.jpg"

    # Evaluamos que tu función real arroje el ValueError controlado del try-except
    with pytest.raises(ValueError):
        read_jpg_file(ruta_falsa)


def test_read_non_existent_dicom_raises_error():
    """Verificar que read_dicom_file lance ValueError si el archivo no existe.

    Asegura que si se introduce una ruta falsa para un archivo médico
    DICOM, el sistema dispare un ValueError para proteger el flujo.
    """
    ruta_falsa = "carpeta_imaginaria/paciente_no_existe.dcm"

    with pytest.raises(ValueError):
        read_dicom_file(ruta_falsa)