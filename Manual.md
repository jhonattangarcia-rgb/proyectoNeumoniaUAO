# 📑 Manual de Configuración y Trabajo en Equipo - Proyecto Neumonía UAO

¡Hola equipo! Este documento contiene los pasos exactos para descargar el proyecto en sus computadoras, configurar el entorno virtual unificado y seguir las reglas básicas de Git para trabajar de forma organizada sin pisarnos el código.

---

## 🚀 Parte 1: Clonación e Instalación Local (Solo se hace la primera vez)

### 1. Clonar el repositorio público

Abran una terminal en su computadora, naveguen hasta su carpeta de proyectos y ejecuten:

```powershell
git clone https://github.com/jhonattangarcia-rgb/proyectoNeumoniaUAO.git
cd UAO-Neumonia (depende de su carpeta)
```

_Abran esta carpeta recién descargada directamente en su **Visual Studio Code** (`Archivo > Abrir carpeta`)._

### 2. Instalar UV (Si no lo tienen)

UV es mucho más rápido que pip y gestiona los entornos virtuales automáticamente. Si no lo tienen, instálenlo (una sola vez en su PC):

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Configurar el Entorno e Instalar Dependencias

A diferencia de antes, ya no necesitan crear el entorno manual ni activar scripts de permisos. Solo ejecuten en la raíz del proyecto:

```powershell
uv sync
```

_Esto creará la carpeta `.venv` con todas las librerías necesarias (TensorFlow, OpenCV, etc.) de forma ultra rápida._

### 4. Probar la Aplicación

Para ejecutar el proyecto usando el entorno de UV, usen:

```powershell
uv run detector_neumonia.py
```

O usen el Makefile simplificado:
```powershell
make run
```

---

## 🌿 Parte 2: Esquema de Trabajo con Ramas (Git Flow Básico)

Para trabajar de forma profesional entre los 6 integrantes y evitar dañar el código en la rama principal (`main`), utilizaremos **Ramas de características (Features)**. **Nadie debe programar ni hacer push directo sobre `main`**.

### 🛠️ Comandos del Ciclo Diario de Trabajo

#### Paso 1: Descargar lo último del equipo

Antes de empezar a escribir cualquier línea de código, sitúense en `main` y descarguen lo que sus compañeros hayan subido:

```powershell
git checkout main
git pull origin main
```

#### Paso 2: Crear su propia rama de trabajo

Creen una rama con un nombre descriptivo de la tarea que van a realizar (por ejemplo: `feature/interfaz-grafica`, `feature/entrenamiento-modelo`, `feature/pruebas-rayosx`):

```powershell
git checkout -b feature/nombre-de-tu-tarea
```

_Este comando los crea y los mueve automáticamente a su nueva rama segura._

#### Paso 3: Guardar sus avances locales

A medida que programen y modifiquen archivos, guarden sus estados de avance en su historial:

```powershell
git status  (Para ver qué archivos cambiaron)
git add .   (Prepara todos los cambios)
git commit -m "Explicación clara de lo que agregué o corrigí"
```

#### Paso 4: Subir su rama a GitHub

Cuando terminen su módulo o tarea y quieran que el resto del equipo lo revise, suban su rama específica a la nube:

```powershell
git push origin feature/nombre-de-tu-tarea
```

---

## 🚨 Reglas de Oro del Repositorio

1. **Los modelos `.h5` no se suben:** Los archivos de pesos (`conv_MLP_84.h5` y `WilhemNet86.h5`) ya están en el `.gitignore`. No intenten forzar su subida ya que pesan demasiado.
2. **La carpeta `.venv/` no se sube:** Las librerías locales se quedan en su máquina. Si agregan una librería nueva, usen `uv add nombre-libreria` para que se actualice el `pyproject.toml`.
3. **Revisión en Equipo (Pull Requests):** Una vez suban su rama a GitHub, entren a la web y creen un _Pull Request_ para que los demás compañeros revisen los cambios antes de mezclarlos con la rama `main`.
