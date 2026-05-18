"""Application entrypoint for the pneumonia detection GUI."""

# Standard library imports
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Local application imports
from app.gui import App

# MEJORA: Arranque directo del ciclo de vida de la aplicación.
# Se elimina la función main() redundante para simplificar la sintaxis.
if __name__ == "__main__":
    app = App()
