#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# Silenciar logs de TensorFlow (0=all, 1=no info, 2=no warning, 3=no error)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import warnings
warnings.filterwarnings('ignore') # Ignorar advertencias de Keras/Pillow

import csv
import cv2
import numpy as np
import pydicom as dicom
import tensorflow as tf
from PIL import ImageTk, Image as PILImage
from tkinter import *
from tkinter import ttk, font, filedialog
from tkinter.messagebox import askokcancel, showinfo, WARNING
from functools import lru_cache
import tkcap

# Configuración de compatibilidad
MODEL_PATH = "conv_MLP_84.h5"

@lru_cache(maxsize=1)
def model_fun(model_path=MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el modelo en '{model_path}'.")
    return tf.keras.models.load_model(model_path, compile=False)

def preprocess(array):
    array = cv2.resize(array, (512, 512))
    if len(array.shape) == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    array = clahe.apply(array)
    array = array.astype(np.float32) / 255.0
    array = np.expand_dims(array, axis=-1)
    array = np.expand_dims(array, axis=0)
    return array

def grad_cam(array):
    img_tensor = preprocess(array)
    model = model_fun()
    last_conv_layer_name = "conv10_thisone"
    
    # Manejo robusto de nombres de input en Keras 3
    try:
        input_names = getattr(model, "input_names", [])
        input_data = [img_tensor] if input_names else img_tensor
    except:
        input_data = img_tensor

    try:
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
        )
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(input_data)
            if isinstance(preds, list):
                preds = preds[0]
            
            class_idx = np.argmax(preds[0])
            class_output = preds[:, class_idx]
        grads = tape.gradient(class_output, last_conv_layer_output)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) if tf.math.reduce_max(heatmap) != 0 else 1)
        heatmap = heatmap.numpy()
    except Exception as e:
        print(f"Error en Grad-CAM: {e}")
        heatmap = np.zeros((512, 512), dtype=np.float32)

    heatmap = cv2.resize(heatmap, (512, 512))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    img_bg = cv2.resize(array, (512, 512))
    if len(img_bg.shape) == 2:
        img_bg = cv2.cvtColor(img_bg, cv2.COLOR_GRAY2RGB)
    superimposed_img = cv2.addWeighted(img_bg, 0.6, heatmap, 0.4, 0)
    return superimposed_img

def predict(array):
    img_tensor = preprocess(array)
    model = model_fun()
    
    # Manejo robusto de nombres de input en Keras 3
    try:
        input_names = getattr(model, "input_names", [])
        input_data = [img_tensor] if input_names else img_tensor
    except:
        input_data = img_tensor
    
    preds = model.predict_on_batch(input_data)
    if isinstance(preds, list):
        preds = preds[0]
        
    prediction = np.argmax(preds[0])
    proba = np.max(preds[0]) * 100
    labels = {0: "bacteriana", 1: "normal", 2: "viral"}
    label = labels.get(prediction, "desconocido")
    heatmap = grad_cam(array)
    return label, proba, heatmap

def read_dicom_file(path):
    try:
        ds = dicom.dcmread(path)
        img_array = ds.pixel_array
        img_norm = (np.maximum(img_array, 0) / (img_array.max() if img_array.max() != 0 else 1)) * 255.0
        img_uint8 = np.uint8(img_norm)
        img_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)
        img2show = PILImage.fromarray(img_rgb)
        return img_rgb, img2show
    except Exception as e:
        raise ValueError(f"Error leyendo DICOM: {e}")

def read_jpg_file(path):
    img_data = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen en {path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img2show = PILImage.fromarray(img_rgb)
    return img_rgb, img2show

class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Herramienta para la detección rápida de neumonía")
        fonti = font.Font(weight="bold")
        self.root.geometry("815x560")
        self.root.resizable(0, 0)
        self.setup_ui(fonti)
        self.array = None
        self.reportID = 0
        self.label = ""
        self.proba = 0.0
        self.heatmap = None
        self.root.mainloop()

    def setup_ui(self, fonti):
        ttk.Label(self.root, text="Imagen Radiográfica", font=fonti).place(x=110, y=65)
        ttk.Label(self.root, text="Imagen con Heatmap", font=fonti).place(x=545, y=65)
        ttk.Label(self.root, text="Resultado:", font=fonti).place(x=500, y=350)
        ttk.Label(self.root, text="Cédula Paciente:", font=fonti).place(x=65, y=350)
        ttk.Label(self.root, text="SOFTWARE PARA EL APOYO AL DIAGNÓSTICO MÉDICO DE NEUMONÍA", font=fonti).place(x=122, y=25)
        ttk.Label(self.root, text="Probabilidad:", font=fonti).place(x=500, y=400)
        self.ID = StringVar()
        self.text1 = ttk.Entry(self.root, textvariable=self.ID, width=15)
        self.text1.place(x=200, y=350)
        self.text_img1 = Text(self.root, width=31, height=15)
        self.text_img1.place(x=65, y=90)
        self.text_img2 = Text(self.root, width=31, height=15)
        self.text_img2.place(x=500, y=90)
        self.text2 = Text(self.root)
        self.text2.place(x=610, y=350, width=120, height=30)
        self.text3 = Text(self.root)
        self.text3.place(x=610, y=400, width=120, height=30)
        self.button1 = ttk.Button(self.root, text="Predecir", state="disabled", command=self.run_model)
        self.button1.place(x=220, y=460)
        ttk.Button(self.root, text="Cargar Imagen", command=self.load_img_file).place(x=70, y=460)
        ttk.Button(self.root, text="Borrar", command=self.delete).place(x=670, y=460)
        ttk.Button(self.root, text="PDF", command=self.create_pdf).place(x=520, y=460)
        ttk.Button(self.root, text="Guardar", command=self.save_results_csv).place(x=370, y=460)
        self.text1.focus_set()

    def load_img_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=(("Todos", "*.dcm *.jpg *.jpeg *.png"), ("DICOM", "*.dcm"), ("Imágenes", "*.jpg *.jpeg *.png"))
        )
        if filepath:
            try:
                if filepath.lower().endswith(".dcm"):
                    self.array, img2show = read_dicom_file(filepath)
                else:
                    self.array, img2show = read_jpg_file(filepath)
                self.img1_pil = img2show.resize((250, 250), PILImage.LANCZOS)
                self.img1_tk = ImageTk.PhotoImage(self.img1_pil)
                self.text_img1.delete('1.0', END)
                self.text_img1.image_create(END, image=self.img1_tk)
                self.button1["state"] = "enabled"
            except Exception as e:
                showinfo(title="Error", message=f"No se pudo cargar la imagen: {e}")

    def run_model(self):
        try:
            self.label, self.proba, self.heatmap = predict(self.array)
            img_h = PILImage.fromarray(self.heatmap)
            self.img2_pil = img_h.resize((250, 250), PILImage.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(self.img2_pil)
            self.text_img2.delete('1.0', END)
            self.text_img2.image_create(END, image=self.img2_tk)
            self.text2.delete('1.0', END)
            self.text2.insert(END, self.label)
            self.text3.delete('1.0', END)
            self.text3.insert(END, f"{self.proba:.2f}%")
        except Exception as e:
            showinfo(title="Error en Predicción", message=f"Hubo un problema: {e}")

    def save_results_csv(self):
        if not self.label: return
        try:
            with open("historial.csv", "a", newline='') as csvfile:
                w = csv.writer(csvfile, delimiter="-")
                w.writerow([self.text1.get(), self.label, f"{self.proba:.2f}%"])
            showinfo(title="Guardar", message="Datos guardados.")
        except Exception as e:
            showinfo(title="Error", message=f"No se pudo guardar: {e}")

    def create_pdf(self):
        try:
            cap = tkcap.CAP(self.root)
            filename = f"Reporte_{self.reportID}.jpg"
            cap.capture(filename)
            img = PILImage.open(filename).convert("RGB")
            pdf_path = f"Reporte_{self.reportID}.pdf"
            img.save(pdf_path)
            self.reportID += 1
            showinfo(title="PDF", message=f"Generado: {pdf_path}")
        except Exception as e:
            showinfo(title="Error PDF", message=f"Error: {e}")

    def delete(self):
        if askokcancel(title="Confirmación", message="¿Borrar todos los datos?", icon=WARNING):
            self.text1.delete(0, END)
            self.text2.delete('1.0', END)
            self.text3.delete('1.0', END)
            self.text_img1.delete('1.0', END)
            self.text_img2.delete('1.0', END)
            self.array = None
            self.button1["state"] = "disabled"

if __name__ == "__main__":
    App()
