import tkinter as tk
from tkinter import messagebox
from pathlib import Path


def ejecutar_aplicacion():
    raiz = tk.Tk()
    raiz.title("D2 Supermercado")
    raiz.minsize(720, 600)
    color_primario = "#3B00FF"
    color_resalte = "#FFFF00"
    color_fondo = "#F5F5F5"
    color_tarjeta = "white"
    color_texto = "#111111"
    color_neutro = "#6B7280"
    raiz.configure(bg=color_fondo)
    estado_pantalla = {"valor": False}

    def alternar_pantalla(_evento=None):
        estado_pantalla["valor"] = not estado_pantalla["valor"]
        raiz.attributes("-fullscreen", estado_pantalla["valor"])

    def salir_pantalla(_evento=None):
        estado_pantalla["valor"] = False
        raiz.attributes("-fullscreen", False)

    raiz.bind("<F11>", alternar_pantalla)
    raiz.bind("<Escape>", salir_pantalla)
    marco_principal = tk.Frame(raiz, bg=color_fondo)
    marco_principal.pack(fill="both", expand=True)
    cabecera = tk.Frame(marco_principal, bg=color_primario)
    cabecera.pack(fill="x", pady=(0, 16))
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
            imagen.thumbnail((120, 120))
            foto = ImageTk.PhotoImage(imagen)
            etiqueta_logo = tk.Label(cabecera, image=foto, bg=color_primario)
            etiqueta_logo.image = foto
            etiqueta_logo.pack(pady=(15, 4))
    except Exception:
        pass
    tk.Label(
        cabecera,
        text="D2 Supermercado",
        font=("Segoe UI", 22, "bold"),
        bg=color_primario,
        fg="white",
    ).pack(pady=(4, 8))
    cuerpo = tk.Frame(marco_principal, bg=color_fondo)
    cuerpo.pack(fill="both", expand=True, padx=32, pady=(16, 8))

    def crear_tarjeta(contenedor, titulo, descripcion, accion):
        tarjeta = tk.Frame(contenedor, bg=color_tarjeta, bd=0)
        tarjeta.pack(fill="x", pady=10)

        def resaltar(_evento):
            tarjeta.configure(bg="#EEF2FF")

        def normalizar(_evento):
            tarjeta.configure(bg=color_tarjeta)

        tarjeta.bind("<Enter>", resaltar)
        tarjeta.bind("<Leave>", normalizar)
        interior = tk.Frame(tarjeta, bg=color_tarjeta)
        interior.pack(fill="x", padx=16, pady=12)
        titulo_lbl = tk.Label(
            interior,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg=color_tarjeta,
            fg=color_texto,
            anchor="w",
        )
        titulo_lbl.pack(fill="x")
        descripcion_lbl = tk.Label(
            interior,
            text=descripcion,
            font=("Segoe UI", 9),
            bg=color_tarjeta,
            fg=color_neutro,
            anchor="w",
            justify="left",
        )
        descripcion_lbl.pack(fill="x", pady=(2, 0))

        def ejecutar(_evento=None):
            accion()

        for elemento in (tarjeta, interior, titulo_lbl, descripcion_lbl):
            elemento.bind("<Button-1>", ejecutar)

    crear_tarjeta(
        cuerpo,
        "Caja (Facturación)",
        "Registrar ventas y generar comprobantes de forma rápida.",
        lambda: abrir_caja(raiz),
    )
    crear_tarjeta(
        cuerpo,
        "Inventario",
        "Gestionar stock, productos y categorías del supermercado.",
        lambda: abrir_inventario(raiz),
    )
    crear_tarjeta(
        cuerpo,
        "Contabilidad",
        "Visualizar ingresos, costos y unidades vendidas por mes.",
        lambda: abrir_contabilidad(raiz),
    )
    pie = tk.Frame(marco_principal, bg=color_primario, height=24)
    pie.pack(fill="x", side="bottom")
    raiz.mainloop()


def abrir_contabilidad(padre):
    try:
        import ui_contabilidad as ui_contabilidad

        ui_contabilidad.open_contabilidad(padre)
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo abrir contabilidad:\n{error}")


def abrir_inventario(padre):
    try:
        import ui_inventario as ui_inventario

        ui_inventario.open_inventario(padre)
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo abrir inventario:\n{error}")


def abrir_caja(padre):
    try:
        import ui_caja as ui_caja

        ui_caja.open_caja(padre)
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo abrir caja:\n{error}")


if __name__ == "__main__":
    ejecutar_aplicacion()
