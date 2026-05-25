"""Report generation helpers for CLI workflows."""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from fpdf import FPDF

def create_pdf_from_image(
    image_path: Path,
    pdf_path: Path,
    title: Optional[str] = None,
) -> None:
    """Create a PDF file containing a single image.

    Args:
        image_path: Path to the image to embed.
        pdf_path: Destination PDF file path.
        title: Optional title to add at the top of the PDF.
    """
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
    """Create a PDF summary report for an inference result.

    Args:
        original_image: Path to the original radiograph image.
        gradcam_image: Path to the Grad-CAM heatmap image.
        output_path: Destination PDF file path.
        label: Predicted label for the image.
        probability: Predicted probability as a percentage.
    """
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
    pdf.multi_cell(
        0, 6, "Se muestra la radiografía original y el mapa Grad-CAM generado."
    )
    pdf.ln(6)

    image_width = 90
    pdf.image(str(original_image), x=10, y=pdf.get_y(), w=image_width)
    pdf.image(str(gradcam_image), x=110, y=pdf.get_y(), w=image_width)
    pdf.output(str(output_path))
