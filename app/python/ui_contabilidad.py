import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from BaseWindow import VentanaBase

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore

try:
    from matplotlib.figure import Figure  # type: ignore
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore

    MATPLOTLIB_DISPONIBLE = True
except Exception:
    MATPLOTLIB_DISPONIBLE = False


#Herencia (de VentanaBase)
class VentanaContabilidad(VentanaBase):
    def __init__(self, padre=None):
        super().__init__(padre, "D2 Supermercado - Contabilidad")
        self.valor_anio = tk.StringVar()
        self.area_texto = None
        self.marco_grafico = None

    def _configurar_estilos(self):
        super()._configurar_estilos()
        estilo = ttk.Style(self.ventana)
        estilo.configure(
            "BotonClaro.TButton",
            background=self.COLOR_PRIMARIO,
            foreground="white",
            borderwidth=0,
            padding=(8, 4),
        )
        estilo.map("BotonClaro.TButton", background=[("active", self.COLOR_PRIMARIO)])
        estilo.configure(
            "EntradaClara.TEntry",
            fieldbackground="white",
            foreground=self.COLOR_TEXTO,
        )

    def _construir_interfaz(self):
        self.ventana.geometry("900x640")
        self._alternar_pantalla()
        contenedor = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=18, pady=16)
        self._construir_cabecera(contenedor)
        self._construir_controles(contenedor)

    def _construir_cabecera(self, contenedor):
        cabecera = tk.Frame(contenedor, bg=self.COLOR_PRIMARIO)
        cabecera.pack(fill="x")
        interior = tk.Frame(cabecera, bg=self.COLOR_PRIMARIO)
        interior.pack(fill="x", pady=6)
        tk.Label(
            interior,
            text="Contabilidad Mensual",
            font=("Segoe UI", 20, "bold"),
            bg=self.COLOR_PRIMARIO,
            fg="white",
        ).pack(side="left", expand=True, padx=16)
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
                imagen.thumbnail((64, 64))
                foto = ImageTk.PhotoImage(imagen)
                etiqueta = tk.Label(interior, image=foto, bg=self.COLOR_PRIMARIO)
                etiqueta.image = foto
                etiqueta.pack(side="right", padx=(8, 16))
        except Exception:
            pass

    def _construir_controles(self, contenedor):
        panel_superior = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE)
        panel_superior.pack(fill="x", pady=(12, 10))
        tk.Label(
            panel_superior,
            text="Año (opcional):",
            bg=self.COLOR_SUPERFICIE,
            fg=self.COLOR_TEXTO,
        ).pack(side="left", padx=(10, 4), pady=8)
        ttk.Entry(
            panel_superior,
            width=8,
            textvariable=self.valor_anio,
            style="EntradaClara.TEntry",
        ).pack(side="left")
        ttk.Button(
            panel_superior,
            text="Cargar",
            command=self._cargar_datos,
            style="BotonClaro.TButton",
        ).pack(side="left", padx=8)
        panel_contenido = tk.Frame(contenedor, bg=self.COLOR_FONDO)
        panel_contenido.pack(fill="both", expand=True)
        self.marco_grafico = tk.Frame(panel_contenido, bg=self.COLOR_SUPERFICIE)
        self.marco_grafico.pack(side="left", fill="both", expand=True, padx=(0, 8))
        contenedor_texto = tk.Frame(panel_contenido, bg=self.COLOR_SUPERFICIE, width=320)
        contenedor_texto.pack(side="right", fill="y")
        contenedor_texto.pack_propagate(False)
        self.area_texto = tk.Text(
            contenedor_texto,
            bg=self.COLOR_SUPERFICIE,
            fg=self.COLOR_TEXTO,
            borderwidth=0,
        )
        self.area_texto.pack(fill="both", expand=True, padx=6, pady=6)

    def _cargar_datos(self):
        try:
            texto_anio = self.valor_anio.get().strip()
            anio = int(texto_anio) if texto_anio else None
        except ValueError:
            messagebox.showwarning("Contabilidad", "El año debe ser numérico")
            return
        try:
            datos = Conexion.contabilidad(anio)
        except Exception as error:
            messagebox.showerror("Contabilidad", f"Error consultando datos:\n{error}")
            return
        self.area_texto.delete("1.0", tk.END)
        for widget in self.marco_grafico.winfo_children():
            widget.destroy()
        if not datos:
            self.area_texto.insert(tk.END, "No hay datos disponibles.\n")
            return
        for fila in datos:
            self.area_texto.insert(
                tk.END,
                f"Mes: {fila['mes']}\n"
                f"  Ingresos: {fila['total_ingresos']:.2f}\n"
                f"  Costos: {fila['total_costos']:.2f}\n"
                f"  Subtotales: {fila['total_subtotales']:.2f}\n"
                f"  Unidades vendidas: {fila['total_unidades']}\n\n",
            )
        if not MATPLOTLIB_DISPONIBLE:
            messagebox.showwarning(
                "Contabilidad", "Matplotlib no está disponible. Instale la librería."
            )
            return
        self._dibujar_grafico(datos)

    def _dibujar_grafico(self, datos):
        meses = [fila["mes"] for fila in datos]
        ingresos = [fila["total_ingresos"] for fila in datos]
        costos = [fila["total_costos"] for fila in datos]
        figura = Figure(figsize=(6, 4), dpi=100)
        eje = figura.add_subplot(111)
        eje.plot(meses, ingresos, marker="o", label="Ingresos", color=self.COLOR_PRIMARIO)
        eje.plot(meses, costos, marker="o", label="Costos", color="#EF4444")
        eje.set_title("Ingresos y costos por mes", color=self.COLOR_TEXTO)
        eje.set_xlabel("Mes", color=self.COLOR_TEXTO)
        eje.set_ylabel("Valor", color=self.COLOR_TEXTO)
        eje.grid(True, linestyle="--", alpha=0.3)
        eje.legend()
        for etiqueta in eje.get_xticklabels():
            etiqueta.set_rotation(45)
            etiqueta.set_color(self.COLOR_TEXTO)
        for etiqueta in eje.get_yticklabels():
            etiqueta.set_color(self.COLOR_TEXTO)
        figura.patch.set_facecolor(self.COLOR_SUPERFICIE)
        eje.set_facecolor(self.COLOR_FONDO)
        lienzo = FigureCanvasTkAgg(figura, master=self.marco_grafico)  # type: ignore
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)


def open_contabilidad(parent=None):
    ventana = VentanaContabilidad(parent)
    ventana.mostrar()
