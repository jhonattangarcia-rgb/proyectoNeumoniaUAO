"""Application entrypoint for the pneumonia detection app."""

# Standard library imports
import os
from app.cli import main
from app.gui import App

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
COMMAND_PROMPT_MODE = os.getenv("COMMAND_PROMPT_MODE", "false").strip().lower() == "true"

if __name__ == "__main__":
    if COMMAND_PROMPT_MODE:
        print("Starting pneumonia detection application in command prompt mode...")

        main(standalone_mode=False)
    else:
        print("Starting pneumonia detection application in GUI mode...")
        

        app = App()
