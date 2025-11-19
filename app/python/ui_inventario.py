import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore


def open_inventario(parent=None):
    if parent is None:
        win = tk.Tk()
        win.title("D2 Supermercado - Inventario")
    else:
        win = tk.Toplevel(parent)
        win.title("D2 Supermercado - Inventario")

    COLOR_PRIMARY = "#3B00FF"
    COLOR_BG = "#F5F5F5"
    COLOR_SURFACE = "white"
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
        "Dark.Treeview",
        background=COLOR_SURFACE,
        foreground=COLOR_TEXT,
        fieldbackground=COLOR_SURFACE,
        bordercolor=COLOR_SURFACE,
    )
    style.map(
        "Dark.Treeview",
        background=[("selected", COLOR_PRIMARY)],
        foreground=[("selected", "#FFFFFF")],
    )
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
        bordercolor=COLOR_SURFACE,
    )
    style.configure(
        "Light.TCombobox",
        fieldbackground=COLOR_BG,
        foreground=COLOR_TEXT,
        background=COLOR_BG,
        selectbackground=COLOR_BG,
        selectforeground=COLOR_TEXT,
        arrowcolor=COLOR_TEXT,
    )
    style.map(
        "Light.TCombobox",
        fieldbackground=[("readonly", COLOR_BG), ("active", COLOR_BG), ("!disabled", COLOR_BG)],
        foreground=[("readonly", COLOR_TEXT), ("active", COLOR_TEXT), ("!disabled", COLOR_TEXT)],
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_PRIMARY,
        foreground="white",
        borderwidth=0,
        relief="flat",
    )

    frame = tk.Frame(win, bg=COLOR_BG)
    frame.pack(fill="both", expand=True, padx=16, pady=16)

    header = tk.Frame(frame, bg=COLOR_PRIMARY)
    header.pack(fill="x", pady=(0, 12))

    header_inner = tk.Frame(header, bg=COLOR_PRIMARY)
    header_inner.pack(fill="x", pady=4)

    title_label = tk.Label(
        header_inner,
        text="Inventario",
        font=("Segoe UI", 20, "bold"),
        bg=COLOR_PRIMARY,
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
            logo_label = tk.Label(header_inner, image=photo, bg=COLOR_PRIMARY)
            logo_label.image = photo
            logo_label.pack(side="right", padx=(8, 16), pady=8)
    except Exception:
        pass

    content_frame = tk.Frame(frame, bg=COLOR_BG)
    content_frame.pack(fill="both", expand=True, pady=(8, 0))

    left_panel = tk.Frame(content_frame, bg=COLOR_SURFACE, width=260)
    left_panel.pack(side="left", fill="y", padx=(0, 10))
    left_panel.pack_propagate(False)

    filtros_frame = tk.Frame(left_panel, bg=COLOR_SURFACE)
    filtros_frame.pack(fill="x", padx=12, pady=(12, 8))

    tk.Label(
        filtros_frame,
        text="Categoria:",
        font=("Segoe UI", 9),
        bg=COLOR_SURFACE,
        fg=COLOR_TEXT,
    ).pack(anchor="w")

    categoria_var = tk.StringVar()
    combo_cat = ttk.Combobox(
        filtros_frame,
        textvariable=categoria_var,
        width=20,
        state="readonly",
        style="Light.TCombobox",
        font=("Segoe UI", 9),
    )
    combo_cat.pack(fill="x", pady=(4, 0))

    def cargar_categorias():
        try:
            productos = Conexion.listar_productos()
            cats = sorted(set(p["categoria"] for p in productos))
            combo_cat["values"] = [""] + cats
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudieron cargar categorias:\n{e}")

    ttk.Button(
        left_panel,
        text="Cargar categorias",
        command=cargar_categorias,
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(4, 0))

    ttk.Button(
        left_panel,
        text="Filtrar",
        command=lambda: cargar_productos(categoria_var.get()),
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(4, 0))

    ttk.Button(
        left_panel,
        text="Mostrar todos",
        command=lambda: cargar_productos(None),
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(4, 0))

    ttk.Button(
        left_panel,
        text="Anadir producto",
        command=lambda: abrir_agregar(),
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(12, 0))

    ttk.Button(
        left_panel,
        text="Actualizar stock",
        command=lambda: abrir_actualizar_stock(),
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(4, 4))

    ttk.Button(
        left_panel,
        text="Eliminar producto",
        command=lambda: abrir_eliminar_producto(),
        style="Dark.TButton",
    ).pack(fill="x", padx=12, pady=(4, 12))

    right_panel = tk.Frame(content_frame, bg=COLOR_BG)
    right_panel.pack(side="left", fill="both", expand=True)

    tree_frame = tk.Frame(right_panel, bg=COLOR_SURFACE)
    tree_frame.pack(fill="both", expand=True)

    columns = ("id", "nombre", "categoria", "marca", "precio", "stock", "codigo")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        height=14,
        style="Dark.Treeview",
    )
    headers = [
        ("id", "ID", 50),
        ("nombre", "Nombre", 220),
        ("categoria", "Categoria", 110),
        ("marca", "Marca", 110),
        ("precio", "Precio", 80),
        ("stock", "Stock", 70),
        ("codigo", "Codigo", 130),
    ]
    for col, text_h, width in headers:
        tree.heading(col, text=text_h)
        tree.column(
            col,
            width=width,
            anchor="center" if col in ("id", "precio", "stock") else "w",
        )

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def cargar_productos(categoria=None):
        try:
            if categoria:
                productos = Conexion.busqueda_categoria(categoria)
            else:
                productos = Conexion.listar_productos()

            for r in tree.get_children():
                tree.delete(r)

            for p in productos:
                tree.insert(
                    "",
                    "end",
                    values=(
                        p["id_producto"],
                        p["nombre_producto"],
                        p["categoria"],
                        p["marca"],
                        float(p["precio_venta"]),
                        p["stock_actual"],
                        p["codigo_barras"],
                    ),
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar productos:\n{e}")

    def abrir_agregar():
        dlg = tk.Toplevel(win)
        dlg.title("Anadir producto")
        dlg.geometry("480x380")
        f = ttk.Frame(dlg, padding=8)
        f.pack(fill="both", expand=True)
        entries = {}
        labels = [
            ("Nombre", "nombre_producto"),
            ("Descripcion", "descripcion"),
            ("Categoria", "categoria"),
            ("Marca", "marca"),
            ("Valor unitario", "valor_unitario"),
            ("Precio venta", "precio_venta"),
            ("Stock inicial", "stock_actual"),
            ("Codigo barras", "codigo_barras"),
        ]
        for i, (lab, key) in enumerate(labels):
            ttk.Label(f, text=lab + ":").grid(row=i, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            ttk.Entry(f, textvariable=var, width=40).grid(row=i, column=1, sticky="w")
            entries[key] = var

        def agregar_prod():
            try:
                nombre = entries["nombre_producto"].get().strip()
                descripcion = entries["descripcion"].get().strip()
                categoria = entries["categoria"].get().strip()
                marca = entries["marca"].get().strip()
                valor = float(entries["valor_unitario"].get() or 0)
                precio = float(entries["precio_venta"].get() or 0)
                stock = int(entries["stock_actual"].get() or 0)
                codigo = entries["codigo_barras"].get().strip() or None
                if not nombre or not categoria:
                    messagebox.showwarning(
                        "Validacion", "Nombre y categoria son obligatorios"
                    )
                    return
                new_id = Conexion.crear_producto_inventario(
                    nombre, descripcion, categoria, marca, valor, precio, stock, codigo
                )
                if new_id:
                    messagebox.showinfo(
                        "Ok", f"Producto insertado con id {new_id}"
                    )
                    dlg.destroy()
                    cargar_categorias()
                    cargar_productos()
                else:
                    messagebox.showerror(
                        "Error", "No se pudo insertar el producto"
                    )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al agregar producto:\n{e}"
                )

        ttk.Button(f, text="Agregar", command=agregar_prod).grid(
            row=len(labels), column=0, columnspan=2, pady=12
        )

    def abrir_actualizar_stock():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning(
                "Seleccionar",
                "Selecciona un producto en la lista para actualizar el stock",
            )
            return
        vals = tree.item(sel, "values")
        id_producto = int(vals[0])
        nombre = vals[1]
        stock_actual = int(vals[5])

        dlg = tk.Toplevel(win)
        dlg.title(f"Actualizar stock - {nombre}")
        dlg.geometry("420x220")
        dlg.resizable(False, False)

        f = ttk.Frame(dlg, padding=12)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text=f"ID: {id_producto}").pack(anchor="w", pady=(0, 2))
        ttk.Label(f, text=f"Nombre: {nombre}").pack(anchor="w", pady=(0, 2))
        ttk.Label(f, text=f"Stock actual: {stock_actual}").pack(
            anchor="w", pady=(0, 8)
        )

        nuevo_var = tk.StringVar()
        ttk.Label(f, text="Nuevo stock:").pack(anchor="w")
        ttk.Entry(f, textvariable=nuevo_var).pack(anchor="w", fill="x", pady=(0, 12))

        def aplicar():
            try:
                nuevo = int(nuevo_var.get())
                ok = Conexion.actualizar_stock(id_producto, nuevo)
                if ok:
                    messagebox.showinfo("Ok", "Stock actualizado")
                    dlg.destroy()
                    cargar_productos(categoria_var.get() or None)
                else:
                    messagebox.showerror(
                        "Error", "No se pudo actualizar stock"
                    )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error actualizando stock:\n{e}"
                )

        btn_frame = ttk.Frame(f)
        btn_frame.pack(fill="x", pady=(0, 4))
        ttk.Button(btn_frame, text="Aplicar", command=aplicar).pack(
            side="right", padx=4, pady=4
        )
        ttk.Button(btn_frame, text="Cancelar", command=dlg.destroy).pack(
            side="right", padx=4, pady=4
        )

    def abrir_eliminar_producto():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning(
                "Seleccionar",
                "Selecciona un producto en la lista para eliminar",
            )
            return

        vals = tree.item(sel, "values")
        id_producto = int(vals[0])
        nombre = vals[1]

        confirmado = messagebox.askyesno(
            "Confirmar eliminacion",
            f"¿Seguro que deseas eliminar el producto:\n\nID {id_producto} - {nombre}?",
        )
        if not confirmado:
            return

        try:
            ok = Conexion.eliminar_producto(id_producto)
            if ok:
                messagebox.showinfo("Ok", "Producto eliminado del inventario")
                cargar_categorias()
                cargar_productos(categoria_var.get() or None)
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo eliminar el producto",
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al eliminar producto:\n{e}",
            )

    cargar_categorias()
    cargar_productos()

    if parent is not None:
        win.transient(parent)
        win.grab_set()
        win.focus_force()
    else:
        win.mainloop()
