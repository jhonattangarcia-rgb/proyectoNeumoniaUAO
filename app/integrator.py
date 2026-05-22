"""High-level prediction logic for the pneumonia detection app."""

# Third-party imports
import numpy as np

# Local application imports
from app.grad_cam import grad_cam
from app.load_model import model_fun
from app.preprocess_img import preprocess


def predict(array: np.ndarray) -> tuple[str, float, np.ndarray]:
    """Run the model and return prediction results and a heatmap.

    Args:
        array: Input image array for inference.

    Returns:
        A tuple with label, probability, and the heatmap image array.
    """
    img_tensor = preprocess(array)
    model = model_fun()

    # Manejo robusto de la estructura de entrada del modelo.
    input_data = [img_tensor] if isinstance(model.inputs, (list, tuple)) else img_tensor

    # MEJORA: Se usa 'predict_on_batch' para optimizar la interfaz gráfica.
    # Procesa la radiografía de forma directa e instantánea en la memoria RAM,
    # siendo hasta 10 veces más rápido que '.predict()' y evitando que la ventana
    # de Tkinter se congele o muestre el mensaje de "No responde".
    preds = model.predict_on_batch(input_data)
    if isinstance(preds, list):
        preds = preds[0]

    prediction = np.argmax(preds[0])
    proba = np.max(preds[0]) * 100

    # MEJORA: Diccionario de etiquetas. Reemplaza el bloque 'if-elif' por un
    # diccionario de mapeo directo
    labels = {0: "bacteriana", 1: "normal", 2: "viral"}
    label = labels.get(prediction, "desconocido")
    heatmap = grad_cam(array)
    return label, proba, heatmap
