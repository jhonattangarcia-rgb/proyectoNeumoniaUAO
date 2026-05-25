"""Core CLI processing logic."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from tqdm import tqdm

from app.integrator import predict
from .database import (
    get_recent_cedulas,
    load_database,
    save_database,
)
from .image import (
    SUPPORTED_IMAGE_EXTENSIONS,
    build_result_folder,
    read_image_file,
    save_numpy_image,
)
from .report import create_pdf_from_image, create_summary_pdf
from .utils import echo_error, echo_info, echo_success, echo_warning, ensure_folder, is_numeric_cedula


def process_file(file_path: Path, output_base: Path) -> Dict[str, str | float]:
    """Process a single image file and save result artifacts.

    Args:
        file_path: Path to the input image file.
        output_base: Base path where result folders and files are created.

    Returns:
        A record dictionary with the patient ID, file name, label,
        probability, and timestamp.
    """
    cedula = file_path.stem
    output_folder = build_result_folder(output_base, cedula)

    image_array, original_pil = read_image_file(file_path)
    label, probability, heatmap = predict(image_array)

    original_image_path = output_folder / "original.png"
    gradcam_image_path = output_folder / "gradcam.png"
    json_path = output_folder / "resultado.json"
    gradcam_pdf_path = output_folder / "inferencia_gradcam.pdf"
    summary_pdf_path = output_folder / "resumen_inferencia.pdf"

    original_pil.save(original_image_path)
    save_numpy_image(heatmap, gradcam_image_path)

    create_pdf_from_image(gradcam_image_path, gradcam_pdf_path, title=f"Grad-CAM - {cedula}")
    create_summary_pdf(
        original_image=original_image_path,
        gradcam_image=gradcam_image_path,
        output_path=summary_pdf_path,
        label=label,
        probability=probability,
    )

    record = {
        "cedula": cedula,
        "archivo": file_path.name,
        "label": label,
        "probability": float(probability),
        "fecha": datetime.now().isoformat(timespec="seconds"),
    }

    with json_path.open("w", encoding="utf-8") as handler:
        json.dump(record, handler, indent=2, ensure_ascii=False)

    return record


def gather_input_files(inputs_path: Path) -> List[Path]:
    """Gather supported image files from the input directory.

    Args:
        inputs_path: Directory containing input image files.

    Returns:
        A sorted list of supported image file paths.

    Raises:
        FileNotFoundError: If the input directory does not exist.
    """
    if not inputs_path.exists() or not inputs_path.is_dir():
        raise FileNotFoundError(f"No existe el directorio de inputs: {inputs_path}")

    files = [
        path
        for path in inputs_path.iterdir()
        if path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    files.sort()
    return files


def filter_valid_files(files: List[Path]) -> Tuple[List[Path], List[str]]:
    """Filter valid files and collect validation warnings.

    Args:
        files: List of file paths to validate.

    Returns:
        A tuple with the list of valid file paths and validation warnings.
    """
    valid: List[Path] = []
    warnings: List[str] = []
    for file_path in files:
        if not is_numeric_cedula(file_path.stem):
            warnings.append(f"Nombre no numérico: {file_path.name}")
            continue
        valid.append(file_path)
    return valid, warnings


def execute_classification_logic(
    inputs: Path,
    outputs: Path,
    database: Path,
    delta_days: int,
) -> None:
    """Execute the classification process for a batch of input files.

    Args:
        inputs: Path to the input directory containing image files.
        outputs: Path where output artifacts should be written.
        database: Path to the Excel database file.
        delta_days: The number of days used to skip recently processed IDs.
    """
    ensure_folder(outputs)
    ensure_folder(database.parent)

    files = gather_input_files(inputs)
    valid_files, validation_warnings = filter_valid_files(files)
    for warning in validation_warnings:
        echo_warning(f"Advertencia: {warning}")

    existing_data = load_database(database)
    recent_cedulas = get_recent_cedulas(existing_data, delta_days)

    new_records: list[dict[str, str | float]] = []
    skipped_recent = 0
    skipped_warnings: list[str] = ["\n"]

    files_to_process = []
    for file_path in valid_files:
        cedula = file_path.stem
        if cedula in recent_cedulas:
            skipped_warnings.append(f"Omitido por cédula reciente en Excel: {cedula}")
            skipped_recent += 1
        else:
            files_to_process.append(file_path)

    with tqdm(files_to_process, desc="Procesando archivos", unit="archivo") as progress_bar:
        for file_path in progress_bar:
            progress_bar.set_description(f"Procesando {file_path.name}")
            try:
                record = process_file(file_path, outputs)
                new_records.append(record)
            except Exception as error:
                progress_bar.set_description("Error")
                echo_error(f"Error procesando {file_path.name}: {error}")

    for skipped_file in skipped_warnings:
        echo_warning(skipped_file)

    if new_records:
        updated_data = pd.concat([existing_data, pd.DataFrame(new_records)], ignore_index=True)
        save_database(database, updated_data)
        echo_success(f"\nSe guardaron {len(new_records)} registros nuevos en el Excel.\n")
    else:
        echo_warning("\nNo se agregaron registros nuevos al Excel.\n")

    echo_info(f"Total encontrados: {len(files)}")
    echo_info(f"Total válidos procesados: {len(new_records)}")
    echo_info(f"Omitidos por cédula reciente: {skipped_recent}\n")
