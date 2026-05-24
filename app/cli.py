"""CLI batch para procesamiento de radiografías de neumonía."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import click
import numpy as np
import pandas as pd
from fpdf import FPDF
from PIL import Image

from app.integrator import predict
from app.read_img import read_dicom_file, read_jpg_file

DATABASE_COLUMNS = ["cedula", "archivo", "label", "probability", "fecha"]
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".dcm"}

DEFAULT_INPUTS = Path("/app/data/inputs")
DEFAULT_OUTPUTS = Path("/app/data/outputs")
DEFAULT_DATABASE = Path("/app/data/database/database.xlsx")


def ensure_folder(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_numeric_cedula(name: str) -> bool:
    return name.isdigit()


def load_database(database_path: Path) -> pd.DataFrame:
    if database_path.exists():
        df = pd.read_excel(database_path, engine="openpyxl")
        for column in DATABASE_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df[DATABASE_COLUMNS]

    return pd.DataFrame(columns=DATABASE_COLUMNS)


def save_database(database_path: Path, df: pd.DataFrame) -> None:
    ensure_folder(database_path.parent)
    df.to_excel(database_path, index=False, engine="openpyxl")


def read_image_file(file_path: Path) -> tuple[np.ndarray, Image.Image]:
    suffix = file_path.suffix.lower()
    if suffix == ".dcm":
        return read_dicom_file(str(file_path))
    if suffix in {".jpg", ".jpeg"}:
        return read_jpg_file(str(file_path))
    raise ValueError(f"Formato no soportado: {file_path}")


def save_numpy_image(image: np.ndarray, output_path: Path) -> None:
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    if image.ndim == 2:
        mode = "L"
    elif image.shape[2] == 3:
        mode = "RGB"
    else:
        raise ValueError("La imagen debe tener 1 o 3 canales.")
    Image.fromarray(image).save(output_path)


def create_pdf_from_image(image_path: Path, pdf_path: Path, title: str | None = None) -> None:
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=14)
    if title:
        pdf.cell(0, 10, title, ln=1)
    pdf.image(str(image_path), x=10, y=25, w=190)
    pdf.output(str(pdf_path))


def create_summary_pdf(
    original_image: Path,
    gradcam_image: Path,
    output_path: Path,
    label: str,
    probability: float,
) -> None:
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Informe de Inferencia", ln=1, align="C")
    pdf.ln(4)
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 8, f"Clasificación: {label}", ln=1)
    pdf.cell(0, 8, f"Probabilidad: {probability:.2f} %", ln=1)
    pdf.ln(4)
    pdf.multi_cell(0, 6, "Se muestra la radiografía original y el mapa Grad-CAM generado.")
    pdf.ln(6)

    image_width = 90
    pdf.image(str(original_image), x=10, y=pdf.get_y(), w=image_width)
    pdf.image(str(gradcam_image), x=110, y=pdf.get_y(), w=image_width)
    pdf.output(str(output_path))


def build_result_folder(output_base: Path, cedula: str) -> Path:
    folder = output_base / cedula
    return ensure_folder(folder)


def process_file(file_path: Path, output_base: Path) -> dict[str, str | float]:
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


def gather_input_files(inputs_path: Path) -> list[Path]:
    if not inputs_path.exists() or not inputs_path.is_dir():
        raise FileNotFoundError(f"No existe el directorio de inputs: {inputs_path}")

    files = [path for path in inputs_path.iterdir() if path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS]
    files.sort()
    return files


def filter_valid_files(files: list[Path]) -> tuple[list[Path], list[str]]:
    valid = []
    warnings: list[str] = []
    for file_path in files:
        if not is_numeric_cedula(file_path.stem):
            warnings.append(f"Nombre no numérico: {file_path.name}")
            continue
        valid.append(file_path)
    return valid, warnings


def get_recent_cedulas(existing_data: pd.DataFrame, delta_days: int) -> set[str]:
    if existing_data.empty:
        return set()
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=delta_days)
    recent_rows = existing_data.loc[existing_data["fecha"] >= cutoff]
    return set(recent_rows["cedula"].astype(str).tolist())


def has_registered_file(existing_data: pd.DataFrame, file_name: str) -> bool:
    if existing_data.empty:
        return False
    return file_name in existing_data["archivo"].astype(str).tolist()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Comandos CLI para el procesamiento de radiografías y la validación del volumen."""
    pass


def execute_classification_logic(inputs: Path, outputs: Path, database: Path, delta_days: int) -> None:
    """Procesa las radiografías y guarda resultados en outputs y en el Excel."""
    click.echo(f"Inputs: {inputs}")
    click.echo(f"Outputs: {outputs}")
    click.echo(f"Database: {database}")
    click.echo(f"Delta (días): {delta_days}")

    ensure_folder(outputs)
    ensure_folder(database.parent)

    files = gather_input_files(inputs)
    valid_files, validation_warnings = filter_valid_files(files)
    for warning in validation_warnings:
        click.echo(f"Advertencia: {warning}")

    existing_data = load_database(database)
    recent_cedulas = get_recent_cedulas(existing_data, delta_days)

    new_records: list[dict[str, str | float]] = []
    skipped_recent = 0
    skipped_registered = 0

    for file_path in valid_files:
        cedula = file_path.stem
        if has_registered_file(existing_data, file_path.name):
            click.echo(f"Omitido porque ya está registrado: {file_path.name}")
            skipped_registered += 1
            continue
        if cedula in recent_cedulas:
            click.echo(f"Omitido por cédula reciente en Excel: {cedula}")
            skipped_recent += 1
            continue

        try:
            click.echo(f"Procesando {file_path.name}...")
            record = process_file(file_path, outputs)
            new_records.append(record)
        except Exception as error:
            click.echo(f"Error procesando {file_path.name}: {error}")

    if new_records:
        updated_data = pd.concat([existing_data, pd.DataFrame(new_records)], ignore_index=True)
        save_database(database, updated_data)
        click.echo(f"Se guardaron {len(new_records)} registros nuevos en el Excel.")
    else:
        click.echo("No se agregaron registros nuevos al Excel.")

    click.echo(f"Total encontrados: {len(files)}")
    click.echo(f"Total válidos procesados: {len(new_records)}")
    click.echo(f"Omitidos por archivo registrado: {skipped_registered}")
    click.echo(f"Omitidos por cédula reciente: {skipped_recent}")


@main.command("execute-classification")
@click.option(
    "--delta-days",
    type=int,
    default=30,
    show_default=True,
    help="Cantidad de días para omitir cédulas recientes en el Excel.",
)
def execute_classification(delta_days: int) -> None:
    """Ejecuta la clasificación usando las rutas por defecto del volumen."""
    execute_classification_logic(DEFAULT_INPUTS, DEFAULT_OUTPUTS, DEFAULT_DATABASE, delta_days)


@main.command("validate-paths")
def validate_paths() -> None:
    """Valida que las rutas del volumen sean las esperadas."""
    inputs = DEFAULT_INPUTS
    outputs = DEFAULT_OUTPUTS
    database = DEFAULT_DATABASE
    errors = []
    click.echo(f"Validando inputs: {inputs}")
    click.echo(f"Validando outputs: {outputs}")
    click.echo(f"Validando database: {database}")

    if not inputs.exists() or not inputs.is_dir():
        errors.append(f"No existe el directorio inputs: {inputs}")
    if not outputs.exists() or not outputs.is_dir():
        errors.append(f"No existe el directorio outputs: {outputs}")
    if not database.parent.exists() or not database.parent.is_dir():
        errors.append(f"No existe el directorio database: {database.parent}")

    if inputs.exists() and inputs.is_dir():
        for path in sorted(inputs.iterdir()):
            if path.is_dir():
                errors.append(f"Debe haber solo archivos en inputs: {path.name}")
                continue
            if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                errors.append(f"Extensión no soportada: {path.name}")
            if not path.stem.isdigit():
                errors.append(f"Nombre no numérico: {path.name}")

    if errors:
        click.echo("Se encontraron errores en la validación:")
        for err in errors:
            click.echo(f"- {err}")
        raise click.Abort()

    click.echo("Validación exitosa. El esquema de carpetas es correcto.")


@main.command("show-excel")
def show_excel() -> None:
    """Carga el Excel por defecto y muestra su contenido en pantalla."""
    database = DEFAULT_DATABASE
    if not database.exists():
        click.echo(f"No existe el archivo Excel: {database}")
        return

    df = load_database(database)
    if df.empty:
        click.echo("El Excel está vacío.")
        return

    click.echo(f"Archivo Excel cargado: {database}")
    click.echo(df.to_string(index=False))


if __name__ == "__main__":
    main()
