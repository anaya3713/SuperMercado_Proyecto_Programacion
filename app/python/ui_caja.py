import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from BaseWindow import VentanaBase

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        Image,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

try:
    import qrcode

    QRCODE_DISPONIBLE = True
except ImportError:
    QRCODE_DISPONIBLE = False

try:
    import cv2  # type: ignore

    OPENCV_DISPONIBLE = True
except ImportError:
    OPENCV_DISPONIBLE = False

try:
    from pyzbar.pyzbar import decode  # type: ignore

    PYZBAR_DISPONIBLE = True
except ImportError:
    PYZBAR_DISPONIBLE = False

DIRECTORIO_FACTURAS = Path(__file__).resolve().parents[2] / "data" / "invoices"
DIRECTORIO_FACTURAS.mkdir(parents=True, exist_ok=True)


#Herencia (de VentanaBase)
class VentanaCaja(VentanaBase):
    def __init__(self, padre=None):
        super().__init__(padre, "Caja - Punto de Venta")
        self.metodo_pago = tk.StringVar(value="EFECTIVO")
        self.nombre_cliente = tk.StringVar()
        self.cedula_cliente = tk.StringVar()
        self.busqueda_producto = tk.StringVar()
        self.total_var = tk.StringVar(value="$0.00")
        self.carrito = []
        self.arbol_items = None
        self.texto_resumen = None

    def _configurar_estilos(self):
        super()._configurar_estilos()
        estilo = ttk.Style(self.ventana)
        estilo.configure(
            "TablaCaja.Treeview",
            background=self.COLOR_SUPERFICIE,
            foreground=self.COLOR_TEXTO,
            fieldbackground=self.COLOR_SUPERFICIE,
        )
        estilo.map(
            "TablaCaja.Treeview",
            background=[("selected", self.COLOR_PRIMARIO)],
            foreground=[("selected", "#FFFFFF")],
        )
        estilo.configure(
            "EncabezadoCaja.Treeview",
            background=self.COLOR_PRIMARIO,
            foreground="white",
        )
        estilo.configure(
            "ListaClara.TCombobox",
            fieldbackground=self.COLOR_FONDO,
            foreground=self.COLOR_TEXTO,
            background=self.COLOR_FONDO,
            arrowcolor=self.COLOR_TEXTO,
        )
        estilo.map(
            "ListaClara.TCombobox",
            fieldbackground=[("readonly", self.COLOR_FONDO)],
            foreground=[("readonly", self.COLOR_TEXTO)],
        )

    def _construir_interfaz(self):
        self.ventana.geometry("980x660")
        self._alternar_pantalla()
        contenedor = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=16, pady=16)
        self._construir_cabecera(contenedor)
        cuerpo = tk.Frame(contenedor, bg=self.COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True)
        panel_izquierdo = tk.Frame(cuerpo, bg=self.COLOR_FONDO)
        panel_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 10))
        panel_derecho = tk.Frame(cuerpo, bg=self.COLOR_FONDO)
        panel_derecho.pack(side="right", fill="both", expand=True)
        self._construir_panel_cliente(panel_izquierdo)
        self._construir_panel_busqueda(panel_izquierdo)
        self._construir_tabla(panel_izquierdo)
        self._construir_acciones(panel_izquierdo)
        self._construir_resumen(panel_derecho)

    def _construir_cabecera(self, contenedor):
        cabecera = tk.Frame(contenedor, bg=self.COLOR_PRIMARIO)
        cabecera.pack(fill="x", pady=(0, 12))
        interior = tk.Frame(cabecera, bg=self.COLOR_PRIMARIO)
        interior.pack(fill="x", pady=4)
        tk.Label(
            interior,
            text="Caja - Punto de Venta",
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

    def _construir_panel_cliente(self, contenedor):
        marco = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="x", pady=(0, 8))
        interior = tk.Frame(marco, bg=self.COLOR_SUPERFICIE)
        interior.pack(fill="x", padx=12, pady=10)
        ttk.Label(interior, text="Método de pago:", background=self.COLOR_SUPERFICIE).grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Combobox(
            interior,
            textvariable=self.metodo_pago,
            values=["EFECTIVO", "TARJETA", "CHEQUE", "TRANSFERENCIA"],
            state="readonly",
            style="ListaClara.TCombobox",
            width=27,
        ).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(interior, text="Nombre cliente:", background=self.COLOR_SUPERFICIE).grid(
            row=1, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Entry(interior, textvariable=self.nombre_cliente, width=32).grid(
            row=1, column=1, sticky="w", padx=4
        )
        ttk.Label(interior, text="Cédula cliente:", background=self.COLOR_SUPERFICIE).grid(
            row=2, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Entry(interior, textvariable=self.cedula_cliente, width=32).grid(
            row=2, column=1, sticky="w", padx=4
        )

    def _construir_panel_busqueda(self, contenedor):
        marco = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="x", pady=(0, 8))
        interior = tk.Frame(marco, bg=self.COLOR_SUPERFICIE)
        interior.pack(fill="x", padx=12, pady=10)
        ttk.Label(interior, text="Código o nombre:", background=self.COLOR_SUPERFICIE).pack(
            side="left", padx=4
        )
        ttk.Entry(interior, textvariable=self.busqueda_producto, width=28).pack(side="left", padx=4)
        ttk.Button(
            interior,
            text="Buscar",
            command=self._buscar_producto,
            style="BotonOscuro.TButton",
        ).pack(side="left", padx=4)
        if OPENCV_DISPONIBLE and PYZBAR_DISPONIBLE:
            ttk.Button(
                interior,
                text="Escanear cámara",
                command=self._escanear_camara,
                style="BotonOscuro.TButton",
            ).pack(side="left", padx=4)

    def _construir_tabla(self, contenedor):
        marco = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="both", expand=True, pady=(0, 8))
        columnas = ("id", "producto", "codigo", "cantidad", "precio", "subtotal")
        self.arbol_items = ttk.Treeview(
            marco, columns=columnas, show="headings", height=12, style="TablaCaja.Treeview"
        )
        configuracion = [
            ("id", "ID", 45),
            ("producto", "Producto", 220),
            ("codigo", "Código", 120),
            ("cantidad", "Cant.", 70),
            ("precio", "Precio", 90),
            ("subtotal", "Subtotal", 100),
        ]
        for clave, texto, ancho in configuracion:
            self.arbol_items.heading(clave, text=texto)
            self.arbol_items.column(
                clave,
                width=ancho,
                anchor="center" if clave != "producto" else "w",
            )
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.arbol_items.yview)
        self.arbol_items.configure(yscroll=barra.set)
        self.arbol_items.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def _construir_acciones(self, contenedor):
        barra = tk.Frame(contenedor, bg=self.COLOR_FONDO)
        barra.pack(fill="x", pady=4)
        ttk.Button(
            barra,
            text="Limpiar carrito",
            command=self._limpiar_carrito,
            style="BotonOscuro.TButton",
        ).pack(side="left", padx=4)
        ttk.Button(
            barra,
            text="Remover ítem",
            command=self._remover_item,
            style="BotonOscuro.TButton",
        ).pack(side="left", padx=4)

    def _construir_resumen(self, contenedor):
        marco = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="both", expand=True)
        ttk.Label(
            marco,
            text="Resumen de factura",
            font=("Segoe UI", 11, "bold"),
            background=self.COLOR_SUPERFICIE,
        ).pack(anchor="w", padx=12, pady=8)
        self.texto_resumen = tk.Text(
            marco,
            height=14,
            bg="white",
            fg=self.COLOR_TEXTO,
            borderwidth=0,
        )
        self.texto_resumen.pack(fill="both", expand=True, padx=12, pady=4)
        pie = tk.Frame(marco, bg=self.COLOR_SUPERFICIE)
        pie.pack(fill="x", padx=12, pady=8)
        ttk.Label(
            pie,
            text="Total:",
            font=("Segoe UI", 11, "bold"),
            background=self.COLOR_SUPERFICIE,
        ).pack(side="left")
        ttk.Label(
            pie,
            textvariable=self.total_var,
            font=("Segoe UI", 18, "bold"),
            background=self.COLOR_SUPERFICIE,
            foreground=self.COLOR_PRIMARIO,
        ).pack(side="left", padx=8)
        ttk.Button(
            pie,
            text="Generar factura",
            command=self._generar_factura,
            style="BotonOscuro.TButton",
        ).pack(side="right")

    def _actualizar_total(self):
        total = sum(item["subtotal"] for item in self.carrito)
        self.total_var.set(f"${total:.2f}")

    def _buscar_producto(self):
        consulta = self.busqueda_producto.get().strip()
        if not consulta:
            messagebox.showwarning("Caja", "Ingresa un código o nombre de producto")
            return
        try:
            producto = Conexion.busqueda_producto(consulta)
            if producto:
                self._abrir_dialogo_cantidad(producto)
                return
            coincidencias = [
                prod
                for prod in Conexion.listar_productos()
                if consulta.lower() in prod["nombre_producto"].lower()
            ]
            if not coincidencias:
                messagebox.showwarning("Caja", "Producto no encontrado")
            elif len(coincidencias) == 1:
                self._abrir_dialogo_cantidad(coincidencias[0])
            else:
                self._mostrar_selector(coincidencias)
        except Exception as error:
            messagebox.showerror("Caja", f"Error en la búsqueda:\n{error}")

    def _mostrar_selector(self, productos):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Seleccionar producto")
        ventana.geometry("520x360")
        ttk.Label(ventana, text="Selecciona un producto").pack(anchor="w", padx=10, pady=8)
        tabla = ttk.Treeview(
            ventana,
            columns=("nombre", "categoria", "stock"),
            show="headings",
            height=12,
        )
        tabla.heading("nombre", text="Nombre")
        tabla.heading("categoria", text="Categoría")
        tabla.heading("stock", text="Stock")
        tabla.column("nombre", width=250)
        tabla.column("categoria", width=140)
        tabla.column("stock", width=80, anchor="center")
        for prod in productos:
            tabla.insert(
                "",
                "end",
                values=(prod["nombre_producto"], prod["categoria"], prod["stock_actual"]),
            )
        tabla.pack(fill="both", expand=True, padx=10, pady=6)

        def elegir():
            item = tabla.focus()
            if not item:
                messagebox.showwarning("Caja", "Selecciona un producto")
                return
            indice = tabla.index(item)
            ventana.destroy()
            self._abrir_dialogo_cantidad(productos[indice])

        ttk.Button(ventana, text="Aceptar", command=elegir).pack(pady=8)
        ventana.transient(self.ventana)
        ventana.grab_set()

    def _abrir_dialogo_cantidad(self, producto):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Agregar al carrito")
        ventana.geometry("380x260")
        marco = ttk.Frame(ventana, padding=12)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text=f"Producto: {producto['nombre_producto']}", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=4
        )
        ttk.Label(marco, text=f"Código: {producto['codigo_barras']}").pack(anchor="w")
        ttk.Label(marco, text=f"Precio venta: ${producto['precio_venta']:.2f}").pack(anchor="w")
        ttk.Label(marco, text=f"Stock disponible: {producto['stock_actual']}").pack(anchor="w", pady=(0, 10))
        ttk.Label(marco, text="Cantidad:").pack(anchor="w")
        var_cantidad = tk.StringVar(value="1")
        ttk.Entry(marco, textvariable=var_cantidad).pack(fill="x", pady=(0, 8))
        ttk.Label(marco, text="Precio unitario:").pack(anchor="w")
        var_precio = tk.StringVar(value=str(producto["precio_venta"]))
        ttk.Entry(marco, textvariable=var_precio).pack(fill="x")

        def agregar():
            try:
                cantidad = int(var_cantidad.get())
                precio = float(var_precio.get())
                if cantidad <= 0 or precio < 0:
                    messagebox.showwarning("Caja", "Cantidad y precio deben ser positivos")
                    return
                subtotal = cantidad * precio
                self.carrito.append(
                    {
                        "id_producto": producto["id_producto"],
                        "nombre": producto["nombre_producto"],
                        "codigo": producto["codigo_barras"],
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                        "subtotal": subtotal,
                    }
                )
                self.arbol_items.insert(
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
                self._actualizar_total()
                self.busqueda_producto.set("")
                ventana.destroy()
            except ValueError:
                messagebox.showerror("Caja", "Ingresa valores numéricos válidos")

        ttk.Button(marco, text="Agregar", command=agregar, style="BotonOscuro.TButton").pack(
            side="left", padx=4, pady=10
        )
        ttk.Button(marco, text="Cancelar", command=ventana.destroy).pack(side="left", padx=4, pady=10)
        ventana.transient(self.ventana)
        ventana.grab_set()

    def _limpiar_carrito(self):
        if not self.carrito:
            return
        self.carrito.clear()
        self.arbol_items.delete(*self.arbol_items.get_children())
        self._actualizar_total()
        messagebox.showinfo("Caja", "Carrito vaciado")

    def _remover_item(self):
        seleccion = self.arbol_items.focus()
        if not seleccion:
            messagebox.showwarning("Caja", "Selecciona un ítem para remover")
            return
        indice = self.arbol_items.index(seleccion)
        self.arbol_items.delete(seleccion)
        self.carrito.pop(indice)
        self._actualizar_total()

    def _generar_factura(self):
        if not self.carrito:
            messagebox.showwarning("Caja", "Agrega productos al carrito antes de facturar")
            return
        nombre = self.nombre_cliente.get().strip()
        cedula = self.cedula_cliente.get().strip()
        if not nombre or not cedula:
            messagebox.showwarning("Caja", "Ingresa nombre y cédula del cliente")
            return
        items_bd = []
        for item in self.carrito:
            items_bd.append(
                {
                    "id_producto": item["id_producto"],
                    "codigo_barras": item["codigo"],
                    "cantidad": item["cantidad"],
                    "precio_unitario": item["precio_unitario"],
                }
            )
        try:
            respuesta = Conexion.generar_factura(
                self.metodo_pago.get(),
                nombre,
                cedula,
                items_bd,
            )
            if not respuesta:
                messagebox.showerror("Caja", "No se pudo generar la factura")
                return
            cliente_info, productos = respuesta
            self._mostrar_resumen(cliente_info, productos)
            if REPORTLAB_DISPONIBLE:
                try:
                    self._crear_pdf(cliente_info, productos)
                except Exception as error:
                    messagebox.showwarning("Caja", f"Factura generada sin PDF:\n{error}")
            else:
                messagebox.showwarning(
                    "Caja",
                    "ReportLab no está instalado. Instálalo para generar el PDF.",
                )
            self._limpiar_carrito()
            self.nombre_cliente.set("")
            self.cedula_cliente.set("")
        except Exception as error:
            messagebox.showerror("Caja", f"Error al generar factura:\n{error}")

    def _mostrar_resumen(self, cliente_info, productos):
        self.texto_resumen.config(state="normal")
        self.texto_resumen.delete("1.0", tk.END)
        self.texto_resumen.insert(tk.END, "✓ FACTURA GENERADA\n\n")
        self.texto_resumen.insert(tk.END, f"ID Venta: {cliente_info['id_venta']}\n")
        self.texto_resumen.insert(tk.END, f"Fecha: {cliente_info['fecha_venta']}\n")
        self.texto_resumen.insert(
            tk.END,
            f"Cliente: {cliente_info['nombre_cliente']} (Cédula: {cliente_info['cedula_cliente']})\n",
        )
        self.texto_resumen.insert(tk.END, f"Total: ${cliente_info['total_venta']:.2f}\n")
        self.texto_resumen.insert(tk.END, f"Método: {cliente_info['metodo_pago']}\n\n")
        self.texto_resumen.insert(tk.END, "Detalle:\n")
        for prod in productos:
            self.texto_resumen.insert(
                tk.END,
                f"- {prod['codigo_barras']} x{prod['cantidad']} "
                f"a ${prod['precio_unitario']:.2f} = ${prod['subtotal']:.2f}\n",
            )
        self.texto_resumen.config(state="disabled")

    def _crear_pdf(self, cliente_info, productos):
        archivo = (
            DIRECTORIO_FACTURAS
            / f"Factura_{cliente_info['id_venta']:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        doc = SimpleDocTemplate(
            str(archivo),
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )
        estilos = getSampleStyleSheet()
        elementos = []
        ruta_logo = Path(__file__).resolve().parents[2] / "assets" / "logo" / "Logo.png"
        if ruta_logo.exists():
            imagen = Image(str(ruta_logo), width=1.2 * inch, height=1.2 * inch)
            tabla_logo = Table([[imagen, "FACTURA DE VENTA"]], colWidths=[1.4 * inch, 4.6 * inch])
            tabla_logo.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (1, 0), "CENTER"),
                        ("FONTSIZE", (1, 0), (1, 0), 16),
                        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            elementos.append(tabla_logo)
        else:
            elementos.append(
                Paragraph(
                    "FACTURA DE VENTA",
                    ParagraphStyle("Titulo", parent=estilos["Heading1"], alignment=1),
                )
            )
        elementos.append(Spacer(1, 0.2 * inch))
        informacion = [
            ["Factura:", f"FES-{cliente_info['id_venta']:05d}", "Fecha:", cliente_info["fecha_venta"]],
            ["Cliente:", cliente_info["nombre_cliente"], "Hora:", cliente_info["hora_venta"]],
            ["Cédula:", cliente_info["cedula_cliente"], "Método:", cliente_info["metodo_pago"]],
        ]
        tabla_info = Table(informacion, colWidths=[1.1 * inch, 2.2 * inch, 1.1 * inch, 1.4 * inch])
        tabla_info.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        elementos.append(tabla_info)
        elementos.append(Spacer(1, 0.2 * inch))
        cabecera_productos = [["Cant", "Producto", "Valor unit.", "Subtotal"]]
        total_general = 0
        for prod in productos:
            cabecera_productos.append(
                [
                    str(prod["cantidad"]),
                    prod.get("nombre_producto", prod["codigo_barras"]),
                    f"${prod['precio_unitario']:.2f}",
                    f"${prod['subtotal']:.2f}",
                ]
            )
            total_general += prod["subtotal"]
        tabla_productos = Table(cabecera_productos, colWidths=[0.6 * inch, 3.4 * inch, 1.2 * inch, 1.2 * inch])
        tabla_productos.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ]
            )
        )
        elementos.append(tabla_productos)
        elementos.append(Spacer(1, 0.2 * inch))
        totales = [
            ["", "", "Subtotal:", f"${total_general:.2f}"],
            ["", "", "Total:", f"${cliente_info['total_venta']:.2f}"],
        ]
        tabla_totales = Table(totales, colWidths=[0.6 * inch, 3.4 * inch, 1.2 * inch, 1.2 * inch])
        tabla_totales.setStyle(
            TableStyle(
                [
                    ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (2, 0), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )
        elementos.append(tabla_totales)
        if QRCODE_DISPONIBLE:
            try:
                datos_qr = f"{cliente_info['id_venta']}|{cliente_info['nombre_cliente']}|{cliente_info['total_venta']:.2f}"
                codigo = qrcode.QRCode(version=1, box_size=4, border=2)
                codigo.add_data(datos_qr)
                codigo.make(fit=True)
                imagen_qr = codigo.make_image(fill_color="black", back_color="white")
                ruta_temp = DIRECTORIO_FACTURAS / "qr_temp.png"
                imagen_qr.save(ruta_temp)
                elementos.append(Spacer(1, 0.2 * inch))
                elementos.append(Image(str(ruta_temp), width=1.4 * inch, height=1.4 * inch))
                ruta_temp.unlink(missing_ok=True)
            except Exception:
                pass
        doc.build(elementos)

    def _escanear_camara(self):
        if not (OPENCV_DISPONIBLE and PYZBAR_DISPONIBLE):
            messagebox.showwarning("Caja", "Instala OpenCV y pyzbar para escanear códigos")
            return
        captura = None
        try:
            captura = cv2.VideoCapture(0)
            if not captura.isOpened():
                messagebox.showerror("Caja", "No se pudo acceder a la cámara")
                return
            codigo = None
            while True:
                ret, frame = captura.read()
                if not ret:
                    break
                for barra in decode(frame):
                    codigo = barra.data.decode("utf-8")
                    (x, y, w, h) = barra.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, codigo, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imshow("Escanear código", frame)
                tecla = cv2.waitKey(1) & 0xFF
                if tecla == 27:
                    break
                if tecla == 32 and codigo:
                    self.busqueda_producto.set(codigo)
                    self._buscar_producto()
                    break
        except Exception as error:
            messagebox.showerror("Caja", f"Error con la cámara:\n{error}")
        finally:
            if captura:
                captura.release()
            cv2.destroyAllWindows()


def open_caja(parent):
    VentanaCaja(parent).mostrar()

