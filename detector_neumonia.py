#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from app.gui import App


# MEJORA: Arranque directo del ciclo de vida de la aplicación.
# Se elimina la función main() redundante para simplificar la sintaxis.
if __name__ == "__main__":
    app = App()
