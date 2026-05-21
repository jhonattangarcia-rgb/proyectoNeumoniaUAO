"""Graphical application entry point for the pneumonia detection app."""

# Standard library imports
import csv
from tkinter import Tk, Text, StringVar, END
from tkinter import ttk, font, filedialog
from tkinter.messagebox import askokcancel, showinfo, WARNING

# Third-party imports
from PIL import ImageGrab, ImageTk, Image as PILImage

# Local application imports
from app.read_img import read_dicom_file, read_jpg_file
from app.integrator import predict


class App:
    """Main GUI class for the pneumonia detection application."""

    def __init__(self) -> None:
        """Initialize the application window and internal state."""
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

    def setup_ui(self, fonti: font.Font) -> None:
        """Create and configure the main Tkinter widgets.

        Args:
            fonti: Font object used for widget labels.
        """
        ttk.Label(self.root, text="Imagen Radiográfica", font=fonti).place(x=110, y=65)
        ttk.Label(self.root, text="Imagen con Heatmap", font=fonti).place(x=545, y=65)
        ttk.Label(self.root, text="Resultado:", font=fonti).place(x=500, y=350)
        ttk.Label(self.root, text="Cédula Paciente:", font=fonti).place(x=65, y=350)
        ttk.Label(
            self.root,
            text="SOFTWARE PARA EL APOYO AL DIAGNÓSTICO MÉDICO DE NEUMONÍA",
            font=fonti,
        ).place(x=122, y=25)
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
        self.button1 = ttk.Button(
            self.root, text="Predecir", state="disabled", command=self.run_model
        )
        self.button1.place(x=220, y=460)
        ttk.Button(self.root, text="Cargar Imagen", command=self.load_img_file).place(
            x=70, y=460
        )
        ttk.Button(self.root, text="Borrar", command=self.delete).place(x=670, y=460)
        ttk.Button(self.root, text="PDF", command=self.create_pdf).place(x=520, y=460)
        ttk.Button(self.root, text="Guardar", command=self.save_results_csv).place(
            x=370, y=460
        )
        self.text1.focus_set()

    def load_img_file(self) -> None:
        """Load an image from disk and display it in the GUI."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=(
                ("Todos", "*.dcm *.jpg *.jpeg *.png"),
                ("DICOM", "*.dcm"),
                ("Imágenes", "*.jpg *.jpeg *.png"),
            ),
        )
        if filepath:
            try:
                if filepath.lower().endswith(".dcm"):
                    self.array, img2show = read_dicom_file(filepath)
                else:
                    self.array, img2show = read_jpg_file(filepath)
                self.img1_pil = img2show.resize((250, 250), PILImage.LANCZOS)
                self.img1_tk = ImageTk.PhotoImage(self.img1_pil)
                self.text_img1.delete("1.0", END)
                self.text_img1.image_create(END, image=self.img1_tk)
                self.button1["state"] = "enabled"
            except Exception as e:
                showinfo(title="Error", message=f"No se pudo cargar la imagen: {e}")

    def run_model(self) -> None:
        """Run the model on the loaded image and display results."""
        try:
            self.label, self.proba, self.heatmap = predict(self.array)
            img_h = PILImage.fromarray(self.heatmap)
            self.img2_pil = img_h.resize((250, 250), PILImage.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(self.img2_pil)
            self.text_img2.delete("1.0", END)
            self.text_img2.image_create(END, image=self.img2_tk)
            self.text2.delete("1.0", END)
            self.text2.insert(END, self.label)
            self.text3.delete("1.0", END)
            self.text3.insert(END, f"{self.proba:.2f}%")
        except Exception as e:
            showinfo(title="Error en Predicción", message=f"Hubo un problema: {e}")

    def save_results_csv(self) -> None:
        """Save the current prediction results into the CSV history file."""
        patient_id = self.ID.get().strip()
        if not patient_id:
            showinfo(
                title="Cédula requerida",
                message="Debe ingresar la cédula del paciente antes de guardar los resultados.",
            )
            return
        if not patient_id.isdigit():
            showinfo(
                title="Cédula inválida",
                message="La cédula debe contener solo números enteros.",
            )
            return
        if not self.label:
            showinfo(
                title="Predicción requerida",
                message="Debe ejecutar una predicción antes de guardar los resultados.",
            )
            return
        try:
            with open("historial.csv", "a", newline="") as csvfile:
                w = csv.writer(csvfile, delimiter="-")
                w.writerow([self.text1.get(), self.label, f"{self.proba:.2f}%"])
            showinfo(title="Guardar", message="Datos guardados.")
        except Exception as e:
            showinfo(title="Error", message=f"No se pudo guardar: {e}")

    def create_pdf(self) -> None:
        """Capture the current interface area and save it as a PDF file."""
        patient_id = self.ID.get().strip()
        if not patient_id:
            showinfo(
                title="Cédula requerida",
                message="Debe ingresar la cédula del paciente antes de generar el PDF.",
            )
            return
        if not patient_id.isdigit():
            showinfo(
                title="Cédula inválida",
                message="La cédula debe contener solo números enteros.",
            )
            return
        patient_id = patient_id.replace(" ", "_")

        pdf_path = filedialog.asksaveasfilename(
            title="Guardar reporte como",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Reporte_{patient_id}_{self.reportID}.pdf",
        )
        if not pdf_path:
            return

        image_path = filedialog.asksaveasfilename(
            title="Guardar imagen como",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg")],
            initialfile=f"Reporte_{patient_id}_{self.reportID}.jpg",
        )

        try:
            self.root.update()
            bbox = (
                self.root.winfo_rootx(),
                self.root.winfo_rooty(),
                self.root.winfo_rootx() + self.root.winfo_width(),
                self.root.winfo_rooty() + self.root.winfo_height(),
            )
            img = ImageGrab.grab(bbox).convert("RGB")
            img.save(pdf_path, "PDF", resolution=100.0)

            if image_path:
                img.save(image_path, "JPEG")

            self.reportID += 1
            showinfo(
                title="PDF",
                message=("PDF Generado ✅,\nImagen guardada ✅"),
            )
        except Exception as e:
            showinfo(title="Error PDF", message=f"Error: {e}")

    def delete(self) -> None:
        """Reset the form and clear loaded image data from the GUI."""
        if askokcancel(
            title="Confirmación", message="¿Borrar todos los datos?", icon=WARNING
        ):
            self.text1.delete(0, END)
            self.text2.delete("1.0", END)
            self.text3.delete("1.0", END)
            self.text_img1.delete("1.0", END)
            self.text_img2.delete("1.0", END)
            self.array = None
            self.button1["state"] = "disabled"
