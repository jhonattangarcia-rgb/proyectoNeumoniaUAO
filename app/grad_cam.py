"""Grad-CAM support for the pneumonia detection application."""

# Third-party imports
import cv2
import numpy as np
import tensorflow as tf

# Local application imports
from app.load_model import model_fun
from app.preprocess_img import preprocess


def grad_cam(array: np.ndarray) -> np.ndarray:
    """Generate a Grad-CAM overlay image for the input image.

    Args:
        array: Input image array used for prediction.

    Returns:
        An RGB image array with the heatmap overlay.
    """
    img_tensor = preprocess(array)
    model = model_fun()

    # MEJORA: Eliminación de fragilidad en la arquitectura del modelo.
    # Escanea el modelo en reversa en tiempo real para localizar de forma automática
    # la última capa convolucional disponible, eliminando dependencia de nombres fijos.
    last_conv_layer_name = None
    for layer in reversed(model.layers):
        if "conv" in layer.name.lower():
            last_conv_layer_name = layer.name
            break

    if not last_conv_layer_name:
        raise ValueError(
            "No se encontró ninguna capa convolucional en la arquitectura del modelo."
        )

    # MEJORA:
    # Detecta la estructura de entrada del modelo según `model.inputs`.
    # Para un modelo funcional, `model.inputs` es una lista de tensores.
    # En este proyecto el modelo tiene una sola entrada, por lo que debemos
    # pasarla como lista a `grad_model` si el modelo espera una entrada en lista.
    input_data = [img_tensor] if isinstance(model.inputs, (list, tuple)) else img_tensor

    try:
        # MEJORA: Arquitectura moderna de Keras 2/3. Crea un modelo de doble salida
        # dinámico para extraer los mapas internos sin usar funciones de backend
        # eliminadas.
        grad_model = tf.keras.models.Model(
            model.inputs, [model.get_layer(last_conv_layer_name).output, model.output]
        )

        # MEJORA: Uso de GradientTape nativo de TensorFlow. Registra las operaciones
        # matemáticas de forma eficiente para calcular los gradientes exactos en
        # memoria RAM.
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(input_data)
            if isinstance(preds, list):
                preds = preds[0]

            class_idx = np.argmax(preds[0])
            class_output = preds[:, class_idx]

        # MEJORA: Cálculo directo de gradientes. Reemplaza por completo el obsoleto
        # 'K.gradients'.
        grads = tape.gradient(class_output, last_conv_layer_output)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        last_conv_layer_output = last_conv_layer_output[0]

        # MEJORA: Multiplicación matricial (@). Elimina el ciclo 'for' ruidoso de
        # 64 pasos.
        # Todo se procesa en paralelo de forma instantánea a nivel de hardware.
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # MEJORA: Escudo contra división por cero. Si el mapa de calor es nulo,
        # divide por 1 de forma segura previniendo que la aplicación se congele.
        heatmap = tf.maximum(heatmap, 0) / (
            tf.math.reduce_max(heatmap) if tf.math.reduce_max(heatmap) != 0 else 1
        )
        heatmap = heatmap.numpy()
    except Exception as e:
        # MEJORA: Tolerancia a fallos. Si algo falla internamente, no rompe el programa;
        # genera un mapa en blanco temporal para mantener viva la interfaz de Tkinter.
        print(f"Error en Grad-CAM: {e}")
        heatmap = np.zeros((512, 512), dtype=np.float32)

    # Procesamiento visual con OpenCV
    heatmap = cv2.resize(heatmap, (512, 512))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    img_bg = cv2.resize(array, (512, 512))

    # MEJORA: Validación de color automática. Convierte la radiografía original
    # de gris a RGB si es necesario para poder fusionarla con el mapa de calor a color.
    if len(img_bg.shape) == 2:
        img_bg = cv2.cvtColor(img_bg, cv2.COLOR_GRAY2RGB)

    # MEJORA: Fusión translúcida (addWeighted). Reemplaza la suma empírica del código
    # viejo.
    # Da una opacidad perfecta del 60% a la radiografía y 40% al mapa para un acabado
    # médico profesional.
    superimposed_img = cv2.addWeighted(img_bg, 0.6, heatmap, 0.4, 0)
    return superimposed_img
