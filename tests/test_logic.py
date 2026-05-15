import unittest
import numpy as np
import os
import sys

# Añadir el directorio raíz al path para poder importar detector_neumonia
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detector_neumonia import preprocess

class TestNeumoniaLogic(unittest.TestCase):
    def test_preprocess_shape(self):
        # Crear imagen dummy (H, W, C)
        dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        processed = preprocess(dummy_img)
        
        # El modelo espera (1, 512, 512, 1) después del preprocesamiento
        self.assertEqual(processed.shape, (1, 512, 512, 1))
        self.assertEqual(processed.dtype, np.float32)

    def test_model_file_exists(self):
        # Verifica la existencia del archivo de pesos actual
        self.assertTrue(os.path.exists("conv_MLP_84.h5"), "El archivo del modelo conv_MLP_84.h5 debe existir en la raíz.")

if __name__ == '__main__':
    unittest.main()
