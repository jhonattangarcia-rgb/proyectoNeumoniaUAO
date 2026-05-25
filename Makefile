PYTHON ?= uv run python
UV ?= uv
APP ?= detector_neumonia.py
DOCKER_IMAGE ?= uao-neumonia
MODEL ?= conv_MLP_84.h5

.DEFAULT_GOAL := help

# 🎯 Agregamos 'start' a las tareas declaradas
.PHONY: help install start run test lint check-model clean docker-build docker-run

help:
	@chcp 65001 > nul
	@echo Targets disponibles:
	@echo   make install       - Instala dependencias usando uv sync
	@echo   make start         - 🚀 Cambia a dev, baja cambios de GitHub y sincroniza uv
	@echo   make run           - Ejecuta la app principal con uv run
	@echo   make lint          - Verifica sintaxis Python y calidad de código con Ruff
	@echo   make test          - Ejecuta pruebas con uv run unittest
	@echo   make check-model   - Verifica si existe el modelo $(MODEL)
	@echo   make clean         - Limpia caches/temporales y entorno uv
	@echo   make docker-build  - Construye imagen Docker
	@echo   make docker-run    - Ejecuta app dentro de Docker

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
	$(PYTHON) -m unittest discover -v

check-model:
	@chcp 65001 > nul
	@$(PYTHON) -c "import os,sys;p='$(MODEL)';ok=os.path.exists(p);print(('OK: modelo encontrado -> ' + p) if ok else ('ERROR: modelo no encontrado -> ' + p));sys.exit(0 if ok else 1)"

clean:
	@chcp 65001 > nul
	@$(PYTHON) -c "from pathlib import Path;import shutil;[shutil.rmtree(p,ignore_errors=True) for p in Path('.').rglob('__pycache__')];[p.unlink() for p in Path('.').rglob('*.pyc')];[p.unlink() for p in Path('.').rglob('*.pyo')];[shutil.rmtree(Path('.pytest_cache'),ignore_errors=True), shutil.rmtree(Path('.mypy_cache'),ignore_errors=True)];print('Limpieza completada')"
	rm -rf .venv uv.lock

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	docker run --rm -it $(DOCKER_IMAGE)
