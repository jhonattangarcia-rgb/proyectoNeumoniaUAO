"""Application entrypoint for the pneumonia detection app."""

# Standard library imports
import os
import logging

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("Neumonia-Detection-App")

# Force CPU-only execution and reduce TensorFlow logging noise.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Silencia todos los logs de TF
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Le dice explícitamente que use CPU
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

COMMAND_PROMPT_MODE = (
    os.getenv("COMMAND_PROMPT_MODE", "false").strip().lower() == "true"
)

if __name__ == "__main__":
    if COMMAND_PROMPT_MODE:
        from app.cli import main

        logger.info("Ejecutando en modo Command Prompt CLI...\n")
        main(standalone_mode=False)
    else:
        from app.gui import App

        logger.info("Ejecutando en modo GUI...\n")
        app = App()
