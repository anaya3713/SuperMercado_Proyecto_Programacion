import tkinter as tk
from tkinter import messagebox
from pathlib import Path
def run_app():
    root = tk.Tk()
    root.title("D2 Supermercado")
    root.minsize(720, 600)

    color_primary = "#3B00FF"
    color_accent = "#FFFF00"
    color_bg = "#F5F5F5"
    color_card = "white"
    color_text = "#000000"
    color_muted = "#6B7280"

    root.configure(bg=color_bg)

    fullscreen_state = {"value": False}

    def _toggle_fullscreen(_event=None):
        fullscreen_state["value"] = not fullscreen_state["value"]
        root.attributes("-fullscreen", fullscreen_state["value"])

    def _exit_fullscreen(_event=None):
        fullscreen_state["value"] = False
        root.attributes("-fullscreen", False)

    root.bind("<F11>", _toggle_fullscreen)
    root.bind("<Escape>", _exit_fullscreen)

    main_frame = tk.Frame(root, bg=color_bg)
    main_frame.pack(fill="both", expand=True)

    header = tk.Frame(main_frame, bg=color_primary)
    header.pack(fill="x", pady=(0, 16))

    try:
        from PIL import Image, ImageTk  # type: ignore

        logo_path = (
            Path(__file__).resolve().parents[2] 
            / "assets" 
            / "logo"
            / "Logo.png"
        )
        if logo_path.exists():
            img = Image.open(logo_path)
            img.thumbnail((120, 120))
            photo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=photo, bg=color_primary)
            logo_label.image = photo
            logo_label.pack(pady=(15, 4))
    except Exception:
        pass

    title = tk.Label(
        header,
        text="D2 Supermercado",
        font=("Segoe UI", 22, "bold"),
        bg=color_primary,
        fg="white",
    )
    title.pack(pady=(4, 8))

    content_frame = tk.Frame(main_frame, bg=color_bg)
    content_frame.pack(fill="both", expand=True, padx=32, pady=(16, 8))

    def create_card(parent, title_text, description, command):
        card = tk.Frame(
            parent,
            bg=color_card,
            highlightthickness=0,
            bd=0,
        )
        card.pack(fill="x", pady=10)

        def on_enter(_event):
            card.configure(bg="#EEF2FF")

        def on_leave(_event):
            card.configure(bg=color_card)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        inner = tk.Frame(card, bg=color_card)
        inner.pack(fill="x", padx=16, pady=12)

        title_lbl = tk.Label(
            inner,
            text=title_text,
            font=("Segoe UI", 11, "bold"),
            bg=color_card,
            fg=color_text,
            anchor="w",
        )
        title_lbl.pack(fill="x")

        desc_lbl = tk.Label(
            inner,
            text=description,
            font=("Segoe UI", 9),
            bg=color_card,
            fg=color_muted,
            anchor="w",
            justify="left",
        )
        desc_lbl.pack(fill="x", pady=(2, 0))

        def _click(_event=None):
            command()

        for widget in (card, inner, title_lbl, desc_lbl):
            widget.bind("<Button-1>", _click)

        return card

    # Orden 
    create_card(
        content_frame,
        "Caja (Facturacion)",
        "Registrar ventas y generar comprobantes de forma rapida.",
        lambda: open_caja(root),
    )

    create_card(
        content_frame,
        "Inventario",
        "Gestionar stock, productos y categorias del supermercado.",
        lambda: open_inventario(root),
    )

    create_card(
        content_frame,
        "Contabilidad",
        "Visualizar ingresos, costos y unidades vendidas por mes.",
        lambda: open_contabilidad(root),
    )

    footer = tk.Frame(main_frame, bg=color_primary, height=24)
    footer.pack(fill="x", side="bottom")

    root.mainloop()


def open_contabilidad(parent):
    try:
        import ui_contabilidad as ui_contabilidad

        ui_contabilidad.open_contabilidad(parent)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir contabilidad:\n{e}")


def open_inventario(parent):
    try:
        import ui_inventario as ui_inventario

        ui_inventario.open_inventario(parent)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir inventario:\n{e}")


def open_caja(parent):
    try:
        import ui_caja as ui_caja

        ui_caja.open_caja(parent)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir caja:\n{e}")


if __name__ == "__main__":
    run_app()
