FROM python:3.11-slim

# Instalar dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias (sin el proyecto)
RUN uv sync --frozen --no-install-project

# Copiar el código de la aplicación
COPY detector_neumonia.py ./
COPY app/ ./app/
COPY conv_MLP_84.h5 ./

## Mantener el contenedor activo sin ejecutar la app automáticamente.
ENV COMMAND_PROMPT_MODE=true
CMD ["tail", "-f", "/dev/null"]

