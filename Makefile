PYTHON ?= uv run python
UV ?= uv
APP ?= detector_neumonia.py
DOCKER_IMAGE ?= ghcr.io/baronco/app-neumonia:v0.1.0
MODEL ?= conv_MLP_84.h5

.DEFAULT_GOAL := help

# 🎯 Agregamos 'start' a las tareas declaradas
.PHONY: help install start run test lint check-model clean docker-build docker-run

help:
	@chcp 65001 > nul
	@echo Targets disponibles:
	@echo   make install          - Instala dependencias y sincroniza uv
	@echo   make run              - Ejecuta la aplicación principal
	@echo   make start            - 🚀 Actualiza desde GitHub y sincroniza uv
	@echo   make lint             - Verifica calidad de código con Ruff
	@echo   make test             - Ejecuta las pruebas unitarias
	@echo   make docker-pull      - 📥 Descarga la imagen oficial desde GHCR
	@echo   make docker-validate  - 🔍 Valida la estructura de carpetas (DATA="...")
	@echo   make docker-execute   - 🚀 Procesa las imágenes (DATA="...")
	@echo   make docker-show      - 📊 Muestra el Excel de resultados (DATA="...")

install:
	$(UV) sync

# 📥 Nueva tarea para iniciar tu día de trabajo sincronizado
start:
	@chcp 65001 > nul
	@echo =========================================
	@echo 🚀 Asegurando entorno de desarrollo UAO...
	@echo =========================================
	git checkout main
	git pull origin main
	$(UV) sync
	@echo ✅ ¡Listo! Código actualizado y librerías sincronizadas.

run:
	$(PYTHON) $(APP)

# 🧹 Tu lint original reforzado con soporte de caracteres y análisis de Ruff
lint:
	@chcp 65001 > nul
	@echo 🛡️  Validando estructura básica de Python...
	@$(PYTHON) -m py_compile $(APP) && echo "Sintaxis OK: $(APP) no tiene errores estructurales."
	@echo 🧹 Analizando calidad y estilo con Ruff...
	$(UV) run ruff check .

test:
	$(PYTHON) -m pytest -v

# 🐳 Comandos Docker Simplificados
# Reemplaza 'DATA_PATH' con tu ruta absoluta si usas estos comandos directamente.
# Ejemplo: make docker-execute DATA="C:/Usuarios/Yo/Proyecto/data"
DATA ?= $(shell pwd)

docker-pull:
	@echo 📥 Descargando imagen oficial desde GitHub Container Registry...
	docker pull $(DOCKER_IMAGE)

docker-validate:
	@echo 🔍 Validando estructura de datos en $(DATA)...
	docker run --rm -v "$(DATA):/app/data" $(DOCKER_IMAGE) uv run python $(APP) validate-paths

docker-execute:
	@echo 🚀 Procesando imágenes en $(DATA)...
	docker run --rm -v "$(DATA):/app/data" $(DOCKER_IMAGE) uv run python $(APP) execute-classification --delta-days $(or $(DAYS), 30)

docker-show:
	@echo 📊 Mostrando base de datos (Excel)...
	docker run --rm -v "$(DATA):/app/data" $(DOCKER_IMAGE) uv run python $(APP) show-excel
