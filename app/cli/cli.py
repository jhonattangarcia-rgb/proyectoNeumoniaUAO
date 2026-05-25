"""CLI batch for pneumonia X-ray processing."""

from pathlib import Path
from typing import List

import click

from .database import load_database
from .image import SUPPORTED_IMAGE_EXTENSIONS

from .process import execute_classification_logic
from .utils import echo_error, echo_info, echo_success, echo_warning

DEFAULT_INPUTS = Path("/app/data/inputs")
DEFAULT_OUTPUTS = Path("/app/data/outputs")
DEFAULT_DATABASE = Path("/app/data/database/database.xlsx")

# Custom click Group to include subcommand options in root help.
class HelpGroup(click.Group):
    """Custom click Group to include subcommand options in root help."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Override to add subcommand options to the main help output."""
        super().format_help(ctx, formatter)
        if not self.commands:
            return

        with formatter.section("Command options"):
            for name, command in self.commands.items():
                if command is None or command.hidden:
                    continue
                options = [
                    (", ".join(param.opts), param.help or "")
                    for param in command.params
                    if isinstance(param, click.Option)
                ]
                if options:
                    formatter.write_text(f"{name}:")
                    formatter.write_dl(options)


# Root CLI group for all commands.
@click.group(cls=HelpGroup, context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Comandos CLI para el procesamiento de radiografías y la validación del volumen."""
    pass


# Command to run batch classification on the default volume.
@main.command("execute-classification")
@click.option(
    "--delta-days",
    type=int,
    default=30,
    show_default=True,
    help="Number of days to skip recent IDs from the Excel database.",
)
def execute_classification(delta_days: int) -> None:
    """Run classification using the default volume paths."""
    # Delegate actual processing to the reusable CLI logic module.
    execute_classification_logic(
        DEFAULT_INPUTS, 
        DEFAULT_OUTPUTS, 
        DEFAULT_DATABASE, 
        delta_days
    )


# Command to verify required input/output/database folders.
@main.command("validate-paths")
def validate_paths() -> None:
    """Validate that the default volume paths are configured correctly."""
    inputs = DEFAULT_INPUTS
    outputs = DEFAULT_OUTPUTS
    database = DEFAULT_DATABASE
    errors: List[str] = []

    echo_info(f"Validando inputs: {inputs}")
    echo_info(f"Validando outputs: {outputs}")
    echo_info(f"Validando database: {database}")

    # Validate that the expected volume directories exist.
    if not inputs.exists() or not inputs.is_dir():
        errors.append(f"No existe el directorio inputs: {inputs}")
    if not outputs.exists() or not outputs.is_dir():
        errors.append(f"No existe el directorio outputs: {outputs}")
    if not database.parent.exists() or not database.parent.is_dir():
        errors.append(f"No existe el directorio database: {database.parent}")
    
    # Validate the inputs dir contains only supported image files with numeric names.
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
        echo_error("Se encontraron errores en la validación:")
        for err in errors:
            echo_error(f"- {err}")
        raise click.Abort()

    echo_success("Validación exitosa. El esquema de carpetas es correcto.\n")


# Command to show current records from the default Excel database.
@main.command("show-excel")
def show_excel() -> None:
    """Load the default Excel database and print its contents."""
    database = DEFAULT_DATABASE
    if not database.exists():
        echo_error(f"No existe el archivo Excel: {database}")
        return

    # Load and display the database if present.
    df = load_database(database)
    if df.empty:
        echo_warning("El Excel está vacío.")
        return

    echo_info(f"Archivo Excel cargado: {database}\n")
    click.echo(df.to_markdown(index=False)+"\n")


if __name__ == "__main__":
    main()
