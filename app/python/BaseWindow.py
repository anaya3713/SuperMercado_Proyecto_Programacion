import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from pathlib import Path


#Abstracción
class VentanaBase(ABC):
    COLOR_PRIMARIO = "#3B00FF"
    COLOR_FONDO = "#F5F5F5"
    COLOR_SUPERFICIE = "white"
    COLOR_TEXTO = "#111827"

    def __init__(self, padre=None, titulo="D2 Supermercado"):
        self.padre = padre
        self.titulo = titulo
        self.ventana = None
        self.estado_pantalla = {"valor": False}
        self._crear_ventana()
        self._configurar_estilos()
        self._configurar_eventos()

    def _crear_ventana(self):
        if self.padre is None:
            self.ventana = tk.Tk()
        else:
            self.ventana = tk.Toplevel(self.padre)
        self.ventana.title(self.titulo)
        self.ventana.configure(bg=self.COLOR_FONDO)

    def _configurar_estilos(self):
        estilo = ttk.Style(self.ventana)
        try:
            estilo.theme_use("clam")
        except Exception:
            pass
        estilo.configure(
            "BotonOscuro.TButton",
            background=self.COLOR_PRIMARIO,
            foreground="white",
            borderwidth=0,
            focusthickness=0,
            padding=(8, 4),
        )
        estilo.map("BotonOscuro.TButton", background=[("active", self.COLOR_PRIMARIO)])
        estilo.configure(
            "EntradaOscura.TEntry",
            fieldbackground="white",
            foreground=self.COLOR_TEXTO,
            bordercolor=self.COLOR_SUPERFICIE,
        )

    def _configurar_eventos(self):
        self.ventana.bind("<F11>", self._alternar_pantalla)
        self.ventana.bind("<Escape>", self._salir_pantalla)

    def _alternar_pantalla(self, evento=None):
        self.estado_pantalla["valor"] = not self.estado_pantalla["valor"]
        self.ventana.attributes("-fullscreen", self.estado_pantalla["valor"])

    def _salir_pantalla(self, evento=None):
        self.estado_pantalla["valor"] = False
        self.ventana.attributes("-fullscreen", False)

    def _cargar_logo(self, contenedor, tamano=(64, 64)):
        try:
            from PIL import Image, ImageTk  # type: ignore
            ruta_logo = (
                Path(__file__).resolve().parents[2]
                / "assets"
                / "logo"
                / "Logo.png"
            )
            if ruta_logo.exists():
                imagen = Image.open(ruta_logo)
                imagen.thumbnail(tamano)
                foto = ImageTk.PhotoImage(imagen)
                etiqueta = tk.Label(contenedor, image=foto, bg=self.COLOR_PRIMARIO)
                etiqueta.image = foto
                return etiqueta
        except Exception:
            pass
        return None

    @abstractmethod
    def _construir_interfaz(self):
        pass

    def mostrar(self):
        self._construir_interfaz()
        if self.padre is not None:
            self.ventana.transient(self.padre)
            self.ventana.grab_set()
            self.ventana.focus_force()
        self.ventana.mainloop()

    def cerrar(self):
        if self.ventana:
            self.ventana.destroy()

