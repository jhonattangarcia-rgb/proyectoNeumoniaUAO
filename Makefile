PYTHON ?= python
PIP ?= $(PYTHON) -m pip
APP ?= detector_neumonia.py
DOCKER_IMAGE ?= uao-neumonia
MODEL ?= WilhemNet86.h5

.DEFAULT_GOAL := help

.PHONY: help venv install run test lint check-model clean docker-build docker-run

help:
	@echo Targets disponibles:
	@echo   make venv          - Crea entorno virtual .venv
	@echo   make install       - Instala dependencias desde requirements.txt
	@echo   make run           - Ejecuta la app principal
	@echo   make lint          - Verifica sintaxis Python
	@echo   make test          - Ejecuta pruebas con unittest discover
	@echo   make check-model   - Verifica si existe el modelo $(MODEL)
	@echo   make clean         - Limpia caches/temporales de Python
	@echo   make docker-build  - Construye imagen Docker
	@echo   make docker-run    - Ejecuta app dentro de Docker

venv:
	$(PYTHON) -m venv .venv

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(APP)

lint:
	$(PYTHON) -m py_compile $(APP)

test:
	$(PYTHON) -m unittest discover -v

check-model:
	$(PYTHON) -c "import os,sys;p='$(MODEL)';ok=os.path.exists(p);print(('OK: modelo encontrado -> ' + p) if ok else ('ERROR: modelo no encontrado -> ' + p));sys.exit(0 if ok else 1)"

clean:
	$(PYTHON) -c "from pathlib import Path;import shutil;[shutil.rmtree(p,ignore_errors=True) for p in Path('.').rglob('__pycache__')];[p.unlink() for p in Path('.').rglob('*.pyc')];[p.unlink() for p in Path('.').rglob('*.pyo')];[shutil.rmtree(Path('.pytest_cache'),ignore_errors=True), shutil.rmtree(Path('.mypy_cache'),ignore_errors=True)];print('Limpieza completada')"

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	docker run --rm -it $(DOCKER_IMAGE)
