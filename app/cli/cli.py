"""CLI batch para procesamiento de radiografías de neumonía."""

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


@click.group(cls=HelpGroup, context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Comandos CLI para el procesamiento de radiografías y la validación del volumen."""
    pass


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
    execute_classification_logic(
        DEFAULT_INPUTS, 
        DEFAULT_OUTPUTS, 
        DEFAULT_DATABASE, 
        delta_days
    )


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
        echo_error("Se encontraron errores en la validación:")
        for err in errors:
            echo_error(f"- {err}")
        raise click.Abort()

    echo_success("Validación exitosa. El esquema de carpetas es correcto.\n")


@main.command("show-excel")
def show_excel() -> None:
    """Load the default Excel database and print its contents."""
    database = DEFAULT_DATABASE
    if not database.exists():
        echo_error(f"No existe el archivo Excel: {database}")
        return

    df = load_database(database)
    if df.empty:
        echo_warning("El Excel está vacío.")
        return

    echo_info(f"Archivo Excel cargado: {database}\n")
    click.echo(df.to_markdown(index=False)+"\n")


if __name__ == "__main__":
    main()
