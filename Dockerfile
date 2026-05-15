FROM python:3.11-slim

# Instalar dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias (sin el proyecto)
RUN uv sync --frozen --no-install-project

# Copiar el resto del código
COPY . .

# Comando por defecto
CMD ["uv", "run", "detector_neumonia.py"]
