import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore

# Intentar importar ReportLab para PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Intentar importar qrcode para generar QR
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Intentar importar OpenCV para camara
try:
    import cv2  # type: ignore
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Intentar importar pyzbar para deteccion de codigos de barras
try:
    from pyzbar.pyzbar import decode  # type: ignore
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# Carpeta para guardar facturas
FACTURAS_DIR = Path(__file__).resolve().parents[2] / "data" / "invoices"
FACTURAS_DIR.mkdir(parents=True, exist_ok=True)


def open_caja(parent):
    win = tk.Toplevel(parent)
    win.title("Caja - Punto de Venta")
    win.geometry("960x640")

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

    COLOR_PRIMARY = "#3B00FF"
    COLOR_BG = "#F5F5F5"
    COLOR_SURFACE = "white"
    COLOR_TEXT = "#111827"

    win.configure(bg=COLOR_BG)

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

    main_frame = tk.Frame(win, bg=COLOR_BG)
    main_frame.pack(fill="both", expand=True, padx=16, pady=16)

    header = tk.Frame(main_frame, bg=COLOR_PRIMARY)
    header.pack(fill="x", pady=(0, 12))

    # Titulo centrado y logo a la derecha
    header_inner = tk.Frame(header, bg=COLOR_PRIMARY)
    header_inner.pack(fill="x", pady=4)

    title_label = tk.Label(
        header_inner,
        text="Caja - Punto de Venta",
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

    content_frame = tk.Frame(main_frame, bg=COLOR_BG)
    content_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(content_frame, bg=COLOR_BG)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

    right_frame = tk.Frame(content_frame, bg=COLOR_BG)
    right_frame.pack(side="right", fill="both", expand=True)

    # ========== Panel Cliente ==========
    client_frame = tk.Frame(left_frame, bg=COLOR_SURFACE)
    client_frame.pack(fill="x", pady=(0, 8))

    client_inner = tk.Frame(client_frame, bg=COLOR_SURFACE)
    client_inner.pack(fill="x", padx=10, pady=8)

    tk.Label(client_inner, text="Metodo de pago:", bg=COLOR_SURFACE, fg=COLOR_TEXT).grid(
        row=0, column=0, sticky="w", padx=4, pady=4
    )
    metodo_var = tk.StringVar(value="EFECTIVO")
    ttk.Combobox(
        client_inner,
        textvariable=metodo_var,
        values=["EFECTIVO", "TARJETA", "CHEQUE", "TRANSFERENCIA"],
        state="readonly",
        style="Light.TCombobox",
        width=25,
    ).grid(row=0, column=1, sticky="w", padx=4, pady=4)

    tk.Label(client_inner, text="Nombre cliente:", bg=COLOR_SURFACE, fg=COLOR_TEXT).grid(
        row=1, column=0, sticky="w", padx=4, pady=4
    )
    nombre_var = tk.StringVar()
    ttk.Entry(client_inner, textvariable=nombre_var, style="Dark.TEntry", width=30).grid(
        row=1, column=1, sticky="w", padx=4, pady=4
    )

    tk.Label(client_inner, text="Cedula cliente:", bg=COLOR_SURFACE, fg=COLOR_TEXT).grid(
        row=2, column=0, sticky="w", padx=4, pady=4
    )
    cedula_var = tk.StringVar()
    ttk.Entry(client_inner, textvariable=cedula_var, style="Dark.TEntry", width=30).grid(
        row=2, column=1, sticky="w", padx=4, pady=4
    )

    # ========== Buscar Producto ==========
    search_frame = tk.Frame(left_frame, bg=COLOR_SURFACE)
    search_frame.pack(fill="x", pady=(0, 8))

    search_inner = tk.Frame(search_frame, bg=COLOR_SURFACE)
    search_inner.pack(fill="x", padx=10, pady=8)

    tk.Label(search_inner, text="Codigo/Nombre:", bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(
        side="left", padx=4
    )
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_inner, textvariable=search_var, width=24, style="Dark.TEntry")
    search_entry.pack(side="left", padx=4)

    carrito = []
    total_var = tk.StringVar(value="$0.00")

    def actualizar_total():
        total = sum(item["subtotal"] for item in carrito)
        total_var.set(f"${total:.2f}")

    def buscar_producto():
        query = search_var.get().strip()
        if not query:
            messagebox.showwarning("Busqueda", "Ingresa un codigo de barras o nombre de producto")
            return
        try:
            prod = Conexion.busqueda_producto(query)
            if not prod:
                todos = Conexion.listar_productos()
                prods = [p for p in todos if query.lower() in p["nombre_producto"].lower()]
                if not prods:
                    messagebox.showwarning("No encontrado", "No se encontro el producto")
                    return
                if len(prods) == 1:
                    prod = prods[0]
                else:
                    mostrar_lista_seleccion(prods)
                    return
            abrir_dialog_cantidad(prod)
        except Exception as e:
            messagebox.showerror("Error", f"Error en busqueda:\n{e}")

    ttk.Button(search_inner, text="Buscar", command=buscar_producto, style="Dark.TButton").pack(
        side="left", padx=4
    )

    if OPENCV_AVAILABLE:

        def escanear_camara():
            if not PYZBAR_AVAILABLE:
                messagebox.showerror(
                    "Error", "pyzbar no instalado.\nInstala con: pip install pyzbar"
                )
                return
            cap = None
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror("Error", "No se pudo acceder a la camara")
                    return

                codigo_escaneado = None
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    for barcode in decode(frame):
                        codigo_escaneado = barcode.data.decode("utf-8")
                        (x, y, w, h) = barcode.rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            codigo_escaneado,
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

                    cv2.imshow("Escanear Codigo de Barras", frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key == 27:  # ESC
                        break
                    elif key == 32:  # SPACE
                        if codigo_escaneado:
                            cap.release()
                            cv2.destroyAllWindows()
                            try:
                                prod = Conexion.busqueda_producto(codigo_escaneado)
                                if prod:
                                    abrir_dialog_cantidad(prod)
                                else:
                                    messagebox.showwarning(
                                        "No encontrado",
                                        f'Producto con codigo "{codigo_escaneado}" no encontrado',
                                    )
                                    search_var.set("")
                            except Exception as e:
                                messagebox.showerror("Error", f"Error al buscar producto:\n{e}")
                            return
                if cap is not None:
                    cap.release()
                cv2.destroyAllWindows()
            except Exception as e:
                messagebox.showerror("Error", f"Error con escaneo:\n{e}")
                try:
                    if cap is not None:
                        cap.release()
                    cv2.destroyAllWindows()
                except Exception:
                    pass

        ttk.Button(
            search_inner,
            text="Escanear Camara",
            command=escanear_camara,
            style="Dark.TButton",
        ).pack(side="left", padx=4)

    # ========== Tabla de Items ==========
    items_frame = tk.Frame(left_frame, bg=COLOR_SURFACE)
    items_frame.pack(fill="both", expand=True, pady=(0, 8))

    tree_items = ttk.Treeview(
        items_frame,
        columns=("id", "nombre", "codigo", "cantidad", "precio_unit", "subtotal"),
        height=10,
        show="headings",
        style="Dark.Treeview",
    )
    tree_items.heading("id", text="ID")
    tree_items.heading("nombre", text="Producto")
    tree_items.heading("codigo", text="Codigo")
    tree_items.heading("cantidad", text="Cant.")
    tree_items.heading("precio_unit", text="P. Unit.")
    tree_items.heading("subtotal", text="Subtotal")

    tree_items.column("id", width=40, anchor="center")
    tree_items.column("nombre", width=260, anchor="w")
    tree_items.column("codigo", width=120, anchor="center")
    tree_items.column("cantidad", width=70, anchor="center")
    tree_items.column("precio_unit", width=90, anchor="center")
    tree_items.column("subtotal", width=90, anchor="center")

    scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=tree_items.yview)
    tree_items.configure(yscroll=scrollbar.set)
    tree_items.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def mostrar_lista_seleccion(productos):
        dlg = tk.Toplevel(win)
        dlg.title("Seleccionar Producto")
        dlg.geometry("500x380")

        label = ttk.Label(dlg, text="Selecciona un producto:")
        label.pack(anchor="w", padx=8, pady=8)

        tree = ttk.Treeview(
            dlg, columns=("nombre", "categoria", "stock"), height=15, show="headings"
        )
        tree.heading("nombre", text="Nombre")
        tree.heading("categoria", text="Categoria")
        tree.heading("stock", text="Stock")
        tree.column("nombre", width=250)
        tree.column("categoria", width=120)
        tree.column("stock", width=80)

        for p in productos:
            tree.insert(
                "",
                "end",
                values=(p["nombre_producto"], p["categoria"], p["stock_actual"]),
            )

        tree.pack(fill="both", expand=True, padx=8, pady=8)

        def seleccionar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccionar", "Selecciona un producto")
                return
            idx = tree.index(sel)
            dlg.destroy()
            abrir_dialog_cantidad(productos[idx])

        ttk.Button(dlg, text="Aceptar", command=seleccionar).pack(pady=8)
        dlg.transient(win)
        dlg.grab_set()

    def abrir_dialog_cantidad(producto):
        dlg = tk.Toplevel(win)
        dlg.title("Agregar al Carrito")
        dlg.geometry("400x280")

        frame = ttk.Frame(dlg, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=f"Producto: {producto['nombre_producto']}",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=8)
        ttk.Label(frame, text=f"Codigo: {producto['codigo_barras']}").pack(anchor="w")
        ttk.Label(
            frame, text=f"Precio venta: ${producto['precio_venta']:.2f}"
        ).pack(anchor="w")
        ttk.Label(
            frame, text=f"Stock disponible: {producto['stock_actual']}"
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(frame, text="Cantidad:").pack(anchor="w")
        cant_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=cant_var).pack(anchor="w", fill="x")

        ttk.Label(frame, text="Precio unitario ($):").pack(anchor="w", pady=(8, 0))
        precio_var = tk.StringVar(value=str(producto["precio_venta"]))
        ttk.Entry(frame, textvariable=precio_var).pack(anchor="w", fill="x")

        def agregar():
            try:
                cantidad = int(cant_var.get())
                precio = float(precio_var.get())

                if cantidad <= 0:
                    messagebox.showwarning(
                        "Validacion", "Cantidad debe ser mayor a 0"
                    )
                    return
                if precio < 0:
                    messagebox.showwarning(
                        "Validacion", "Precio no puede ser negativo"
                    )
                    return

                subtotal = cantidad * precio

                carrito.append(
                    {
                        "id_producto": producto["id_producto"],
                        "nombre_producto": producto["nombre_producto"],
                        "codigo_barras": producto["codigo_barras"],
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                        "subtotal": subtotal,
                    }
                )

                tree_items.insert(
                    "",
                    "end",
                    values=(
                        producto["id_producto"],
                        producto["nombre_producto"],
                        producto["codigo_barras"],
                        cantidad,
                        f"${precio:.2f}",
                        f"${subtotal:.2f}",
                    ),
                )

                actualizar_total()
                dlg.destroy()
                search_var.set("")
                messagebox.showinfo(
                    "Exito",
                    f"Producto '{producto['nombre_producto']}' anadido al carrito",
                )
            except ValueError:
                messagebox.showerror("Error", "Ingresa valores validos")

        def cancelar():
            dlg.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=12)
        ttk.Button(btn_frame, text="Agregar", command=agregar).pack(
            side="left", padx=4
        )
        ttk.Button(btn_frame, text="Cancelar", command=cancelar).pack(
            side="left", padx=4
        )

        dlg.transient(win)
        dlg.grab_set()

    # Botones de accion debajo de la tabla
    action_frame = tk.Frame(left_frame, bg=COLOR_BG)
    action_frame.pack(fill="x", pady=4)

    def limpiar_carrito():
        carrito.clear()
        for item in tree_items.get_children():
            tree_items.delete(item)
        actualizar_total()
        messagebox.showinfo("Carrito", "Carrito vaciado")

    def remover_item():
        sel = tree_items.focus()
        if not sel:
            messagebox.showwarning("Seleccionar", "Selecciona un item para remover")
            return
        idx = tree_items.index(sel)
        tree_items.delete(sel)
        carrito.pop(idx)
        actualizar_total()
        messagebox.showinfo("Exito", "Item removido del carrito")

    ttk.Button(
        action_frame,
        text="Limpiar Carrito",
        command=limpiar_carrito,
        style="Dark.TButton",
    ).pack(side="left", padx=4)
    ttk.Button(
        action_frame,
        text="Remover Item",
        command=remover_item,
        style="Dark.TButton",
    ).pack(side="left", padx=4)

    # ========== Resumen de Factura (derecha) ==========
    result_frame = tk.Frame(right_frame, bg=COLOR_SURFACE)
    result_frame.pack(fill="both", expand=True, pady=(0, 8))

    tk.Label(
        result_frame,
        text="Resumen de Factura",
        font=("Segoe UI", 10, "bold"),
        bg=COLOR_SURFACE,
        fg=COLOR_TEXT,
        anchor="w",
    ).pack(fill="x", padx=10, pady=(4, 4))

    result_text = tk.Text(result_frame, height=8, state="disabled", bg="white", fg="black")
    result_text.pack(fill="both", expand=True, padx=10, pady=(2, 8))

    def generar_factura():
        if not carrito:
            messagebox.showwarning(
                "Carrito vacio", "Anade items al carrito antes de generar la factura"
            )
            return

        nombre = nombre_var.get().strip()
        cedula = cedula_var.get().strip()
        metodo = metodo_var.get().strip()

        if not nombre or not cedula:
            messagebox.showwarning(
                "Validacion", "Ingresa nombre y cedula del cliente"
            )
            return

        try:
            items_bd = []
            for item in carrito:
                items_bd.append(
                    {
                        "id_producto": item["id_producto"],
                        "codigo_barras": item["codigo_barras"],
                        "cantidad": item["cantidad"],
                        "precio_unitario": item["precio_unitario"],
                    }
                )

            resultado = Conexion.generar_factura(metodo, nombre, cedula, items_bd)

            if not resultado:
                messagebox.showerror(
                    "Error", "Error al generar factura en la BD"
                )
                return

            cliente_info, productos = resultado

            # Mostrar resultado en el Text widget
            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "✓ FACTURA GENERADA\n\n")
            result_text.insert(tk.END, f"ID Venta: {cliente_info['id_venta']}\n")
            result_text.insert(tk.END, f"Fecha: {cliente_info['fecha_venta']}\n")
            result_text.insert(
                tk.END,
                f"Cliente: {cliente_info['nombre_cliente']} (Cédula: {cliente_info['cedula_cliente']})\n",
            )
            result_text.insert(
                tk.END, f"Total: ${cliente_info['total_venta']:.2f}\n"
            )
            result_text.insert(
                tk.END, f"Método: {cliente_info['metodo_pago']}\n\n"
            )
            result_text.insert(tk.END, "Detalle:\n")
            for p in productos:
                result_text.insert(
                    tk.END,
                    f"- {p['codigo_barras']} x{p['cantidad']} a ${p['precio_unitario']:.2f} = ${p['subtotal']:.2f}\n",
                )
            result_text.config(state="disabled")

            # Generar PDF
            if REPORTLAB_AVAILABLE:
                generar_pdf(cliente_info, productos)
                messagebox.showinfo(
                    "Éxito",
                    f"Factura #{cliente_info['id_venta']} generada y guardada como PDF",
                )
            else:
                messagebox.showwarning(
                    "PDF",
                    "ReportLab no instalado. Factura generada en BD pero sin PDF.\nInstala: pip install reportlab",
                )

            # Limpiar interfaz
            carrito.clear()
            for item in tree_items.get_children():
                tree_items.delete(item)
            actualizar_total()
            search_var.set("")
            nombre_var.set("")
            cedula_var.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar factura:\n{e}")

    def generar_pdf(cliente_info, productos):
        """Genera un archivo PDF con los datos de la factura"""
        try:
            import io
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            filename = FACTURAS_DIR / f"Factura_{cliente_info['id_venta']:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(
                str(filename), 
                pagesize=letter, 
                topMargin=0.5*inch, 
                bottomMargin=0.5*inch, 
                leftMargin=0.5*inch, 
                rightMargin=0.5*inch
            )
            styles = getSampleStyleSheet()
            elements = []
            
            # Encabezado con logo
            logo_path = Path(__file__).resolve().parents[2] / "assets" / "logo" / "Logo.png"
            
            if logo_path.exists():
                logo = Image(str(logo_path), width=1*inch, height=1*inch)
                header_table = Table([[logo, "FACTURA DE VENTA"]], colWidths=[1.2*inch, 4.8*inch])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (1, 0), (1, 0), 14),
                ]))
                elements.append(header_table)
            else:
                title_style = ParagraphStyle(
                    'CustomTitle', 
                    parent=styles['Heading1'], 
                    fontSize=14, 
                    textColor=colors.black, 
                    spaceAfter=12, 
                    alignment=1
                )
                elements.append(Paragraph("FACTURA DE VENTA", title_style))
            
            elements.append(Spacer(1, 0.15 * inch))
            
            # Información de factura
            info_data = [
                ['No. FACTURA:', f"FES-{cliente_info['id_venta']:05d}", 'Fecha:', cliente_info['fecha_venta']],
                ['Cliente:', cliente_info['nombre_cliente'], 'Hora:', cliente_info['hora_venta']],
                ['Cédula:', cliente_info['cedula_cliente'], 'Método Pago:', cliente_info['metodo_pago']],
            ]
            
            info_table = Table(info_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 1.6*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Tabla de productos
            product_data = [['Cant', 'Detalle', 'Valor Unit.', 'Total']]
            total_general = 0
            
            for p in productos:
                producto_nombre = p.get('nombre_producto', p.get('codigo_barras', 'Producto'))
                product_data.append([
                    str(p['cantidad']),
                    producto_nombre,
                    f"${p['precio_unitario']:.2f}",
                    f"${p['subtotal']:.2f}",
                ])
                total_general += p['subtotal']
            
            product_table = Table(product_data, colWidths=[0.6*inch, 3.5*inch, 1.2*inch, 1.1*inch])
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
            
            elements.append(product_table)
            elements.append(Spacer(1, 0.15 * inch))
            
            # Subtotal e IVA
            subtotal_data = [
                ['', '', 'Subtotal:', f"${total_general:.2f}"],
                ['', '', 'IVA:', '$0'],
                ['', '', 'TOTAL:', f"${cliente_info['total_venta']:.2f}"],
            ]
            
            subtotal_table = Table(subtotal_data, colWidths=[0.6*inch, 3.5*inch, 1.2*inch, 1.1*inch])
            subtotal_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTSIZE', (2, 2), (-1, 2), 11),
                ('FONTNAME', (2, 2), (-1, 2), 'Helvetica-Bold'),
                ('BACKGROUND', (2, 2), (-1, 2), colors.HexColor('#cccccc')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(subtotal_table)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Código QR
            try:
                if QRCODE_AVAILABLE:
                    qr_data = f"FES-{cliente_info['id_venta']:05d}|{cliente_info['nombre_cliente']}|{cliente_info['total_venta']:.2f}"
                    qr = qrcode.QRCode(version=1, box_size=4, border=2)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    qr_buffer = io.BytesIO()
                    qr_img.save(qr_buffer, format='PNG')
                    qr_buffer.seek(0)
                    
                    qr_image = Image(qr_buffer, width=1.2*inch, height=1.2*inch)
                    qr_table = Table([[qr_image]], colWidths=[6*inch])
                    qr_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER')]))
                    elements.append(qr_table)
            except Exception:
                pass
            
            elements.append(Spacer(1, 0.1 * inch))
            
            # Pie de página
            footer_style = ParagraphStyle(
                'Footer', 
                parent=styles['Normal'], 
                fontSize=8, 
                alignment=1, 
                textColor=colors.grey
            )
            elements.append(Paragraph("Gracias por su compra", footer_style))
            
            # Generar PDF
            doc.build(elements)
            print(f"✓ PDF generado: {filename}")
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            raise

    # Pie de pagina con total y boton de generar factura
    footer = tk.Frame(main_frame, bg=COLOR_SURFACE)
    footer.pack(fill="x", side="bottom", pady=(4, 0))

    tk.Label(
        footer,
        text="Total:",
        font=("Segoe UI", 11, "bold"),
        bg=COLOR_SURFACE,
        fg=COLOR_TEXT,
    ).pack(side="left", padx=(10, 4), pady=6)
    tk.Label(
        footer,
        textvariable=total_var,
        font=("Segoe UI", 16, "bold"),
        bg=COLOR_SURFACE,
        fg=COLOR_PRIMARY,
    ).pack(side="left", pady=6)

    ttk.Button(
        footer,
        text="Generar Factura",
        command=generar_factura,
        style="Dark.TButton",
    ).pack(side="right", padx=10, pady=6)

    win.transient(parent)
    win.grab_set()
    win.focus_force()