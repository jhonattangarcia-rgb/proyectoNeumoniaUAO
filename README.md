# Detección de Neumonía con IA

Herramienta de Deep Learning para clasificación automática de radiografías de tórax en formato DICOM y JPG/PNG en tres categorías:

- Neumonía Bacteriana
- Neumonía Viral
- Sin Neumonía

Utiliza Grad-CAM para generar un mapa de calor que resalta las regiones relevantes de la imagen que determinaron el diagnóstico.

---

## Arquitectura del ProyectoproyectoNeumoniaUAO/
├── app/
│   ├── read_img.py          # Lectura de imágenes DICOM, JPG y PNG
│   ├── preprocess_img.py    # Preprocesamiento de imágenes
│   ├── load_model.py        # Carga del modelo WilhemNet86.h5
│   ├── grad_cam.py          # Generación de mapa de calor
│   ├── integrator.py        # Coordinación de módulos
│   └── gui.py               # Interfaz gráfica con Tkinter
├── tests/                   # Pruebas unitarias con pytest
├── Dockerfile               # Configuración para contenedor Docker
├── pyproject.toml           # Dependencias del proyecto
└── README.md## 
## Flujo de Datos
Imagen (DICOM/JPG/PNG)
↓
read_img.py
(lectura y conversión a array RGB)
↓
preprocess_img.py
(resize 512x512 → escala de grises → CLAHE → normalización → tensor)
↓
load_model.py
(carga WilhemNet86.h5)
↓
grad_cam.py
(predicción + mapa de calor)
↓
integrator.py
(retorna clase + probabilidad + heatmap)
↓
Interfaz gráfica

---

## Requisitos Previos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) para gestión del ambiente virtual
- Docker Desktop (solo para ejecución con contenedor)

---

## Instalación y Ejecución Local

> El ambiente virtual debe crearse exclusivamente con **uv**. No usar conda, venv ni pip directamente.

**Paso 1: Clonar el repositorio**

```bash
git clone https://github.com/jhonattangarcia-rgb/proyectoNeumoniaUAO.git
cd proyectoNeumoniaUAO
```

**Paso 2: Instalar uv**

```bash
pip install uv
```

**Paso 3: Crear el ambiente virtual e instalar dependencias**

```bash
uv sync
```

**Paso 4: Activar el ambiente virtual**

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**Paso 5: Ejecutar la aplicación**

```bash
python app/integrator.py
```

---

## Ejecución con Docker

**Paso 1: Construir la imagen**

```bash
docker build -t neumonia .
```

**Paso 2: Ejecutar el contenedor**

```bash
docker run -v $(pwd)/data:/app/data neumonia --input /app/data/imagen.dcm
```

---

## Uso de la Interfaz Gráfica

1. Ingrese la cédula del paciente en la caja de texto
2. Presione **Cargar Imagen** y seleccione una imagen DICOM, JPG o PNG
3. Presione **Predecir** y espere los resultados
4. Presione **Guardar** para exportar los datos del paciente en formato CSV
5. Presione **PDF** para descargar el informe
6. Presione **Borrar** para cargar una nueva imagen

Imágenes de prueba disponibles en:
https://drive.google.com/drive/folders/1WOuL0wdVC6aojy8IfssHcqZ4Up14dy0g

---

## Acerca del Modelo

La red neuronal convolucional WilhemNet86 está basada en la arquitectura propuesta por F. Pasa, V. Golkov, F. Pfeifer, D. Cremers y D. Pfeifer en *Efficient Deep Network Architectures for Fast Chest X-Ray Tuberculosis Screening and Visualization*.

Está compuesta por 5 bloques convolucionales con conexiones skip para evitar el desvanecimiento del gradiente, seguidos de capas de pooling y tres capas Dense de 1024, 1024 y 3 neuronas. Utiliza Dropout al 20% para regularización.

---

## Acerca de Grad-CAM

Técnica de visualización que calcula el gradiente de la salida de la clase predicha respecto a las activaciones de la última capa convolucional. El resultado es un mapa de calor superpuesto sobre la radiografía que indica las regiones anatómicas que determinaron la clasificación.

---

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.
MIT License
Copyright (c) 2026 Equipo UAO - Proyecto Neumonía
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## Autores

- Jhonatan Garcia
- Andrea Mallama
- Francisco Quintero
- Jan Carlos
- Heidy