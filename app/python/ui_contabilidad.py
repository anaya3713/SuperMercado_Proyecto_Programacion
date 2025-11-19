import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore

try:
    from matplotlib.figure import Figure  # type: ignore
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore

    _HAS_MATPLOTLIB = True
except Exception:
    _HAS_MATPLOTLIB = False


def open_contabilidad(parent=None):
    if parent is None:
        win = tk.Tk()
        win.title("D2 Supermercado - Contabilidad")
    else:
        win = tk.Toplevel(parent)
        win.title("D2 Supermercado - Contabilidad")

    COLOR_PRIMARY = "#3B00FF"
    COLOR_BG = "#F5F5F5"
    COLOR_SURFACE = "white"
    COLOR_HEADER = COLOR_PRIMARY
    COLOR_TEXT = "#111827"

    win.configure(bg=COLOR_BG)

    # Pantalla completa por defecto
    fullscreen_state = {"value": False}

    def _toggle_fullscreen(_event=None):
        fullscreen_state["value"] = not fullscreen_state["value"]
        win.attributes("-fullscreen", fullscreen_state["value"])

    def _exit_fullscreen(_event=None):
        fullscreen_state["value"] = False
        win.attributes("-fullscreen", False)

    win.bind("<F11>", _toggle_fullscreen)
    _toggle_fullscreen()

    style = ttk.Style(win)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "Dark.TButton",
        background=COLOR_PRIMARY,
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        padding=(8, 4),
    )
    style.map("Dark.TButton", background=[("active", COLOR_PRIMARY)])
    style.configure(
        "Dark.TEntry",
        fieldbackground="white",
        foreground=COLOR_TEXT,
    )

    frame = tk.Frame(win, bg=COLOR_BG)
    frame.pack(fill="both", expand=True, padx=16, pady=16)

    title_frame = tk.Frame(frame, bg=COLOR_HEADER)
    title_frame.pack(fill="x", pady=(0, 10))

    header_inner = tk.Frame(title_frame, bg=COLOR_HEADER)
    header_inner.pack(fill="x", pady=4)

    title_label = tk.Label(
        header_inner,
        text="Contabilidad Mensual",
        font=("Segoe UI", 20, "bold"),
        bg=COLOR_HEADER,
        fg="white",
        anchor="center",
    )
    title_label.pack(side="left", expand=True, padx=16, pady=8)

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
            img.thumbnail((64, 64))
            photo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header_inner, image=photo, bg=COLOR_HEADER)
            logo_label.image = photo
            logo_label.pack(side="right", padx=(8, 16), pady=8)
    except Exception:
        pass

    top = tk.Frame(frame, bg=COLOR_SURFACE)
    top.pack(fill="x", pady=(10, 8))

    tk.Label(top, text="Anio (opcional):", bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(
        side="left", padx=(10, 4), pady=8
    )
    year_var = tk.StringVar()
    ttk.Entry(top, width=8, textvariable=year_var, style="Dark.TEntry").pack(
        side="left", padx=4
    )

    btn = ttk.Button(top, text="Cargar", style="Dark.TButton")
    btn.pack(side="left", padx=8)

    content_frame = tk.Frame(frame, bg=COLOR_BG)
    content_frame.pack(fill="both", expand=True, pady=(8, 0))

    plot_frame = tk.Frame(content_frame, bg=COLOR_SURFACE)
    plot_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

    text_frame = tk.Frame(content_frame, bg=COLOR_SURFACE, width=320)
    text_frame.pack(side="right", fill="y")
    text_frame.pack_propagate(False)

    text = tk.Text(
        text_frame,
        wrap="none",
        height=10,
        bg=COLOR_SURFACE,
        fg=COLOR_TEXT,
        borderwidth=0,
        relief="flat",
    )
    text.pack(fill="both", expand=True, padx=4, pady=4)

    canvas_holder = {"canvas": None}

    def cargar():
        try:
            anio_txt = year_var.get().strip()
            anio_val = int(anio_txt) if anio_txt else None
            datos = Conexion.contabilidad(anio_val)

            text.delete("1.0", tk.END)

            for w in plot_frame.winfo_children():
                w.destroy()

            if not datos:
                text.insert(tk.END, "No hay datos o ocurrio un error.\n")
                return

            for row in datos:
                text.insert(tk.END, f"Mes: {row['mes']}\n")
                text.insert(tk.END, f"  Ingresos: {row['total_ingresos']:.2f}\n")
                text.insert(tk.END, f"  Costos: {row['total_costos']:.2f}\n")
                text.insert(tk.END, f"  Subtotales: {row['total_subtotales']:.2f}\n")
                text.insert(tk.END, f"  Unidades vendidas: {row['total_unidades']}\n\n")

            if not _HAS_MATPLOTLIB:
                messagebox.showwarning(
                    "Matplotlib no disponible",
                    "La libreria matplotlib no esta instalada.\nInstala con: pip install matplotlib",
                )
                return

            meses = [r["mes"] for r in datos]
            ingresos = [r["total_ingresos"] for r in datos]
            costos = [r["total_costos"] for r in datos]

            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            ax.plot(meses, ingresos, marker="o", label="Ingresos", color=COLOR_PRIMARY)
            ax.plot(meses, costos, marker="o", label="Costos", color="#EF4444")

            ax.set_title("Ingresos y Costos por mes", color=COLOR_TEXT)
            ax.set_xlabel("Mes", color=COLOR_TEXT)
            ax.set_ylabel("Valor", color=COLOR_TEXT)
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()

            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_color(COLOR_TEXT)
            for label in ax.get_yticklabels():
                label.set_color(COLOR_TEXT)

            fig.patch.set_facecolor(COLOR_SURFACE)
            ax.set_facecolor(COLOR_BG)

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)  # type: ignore
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(fill="both", expand=True, padx=4, pady=4)
            canvas_holder["canvas"] = canvas

        except Exception as e:
            messagebox.showerror("Error", f"Error consultando contabilidad:\n{e}")

    btn.configure(command=cargar)

    if parent is not None:
        win.transient(parent)
        win.grab_set()
        win.focus_force()
    else:
        win.mainloop()


if __name__ == "__main__":
    open_contabilidad()
