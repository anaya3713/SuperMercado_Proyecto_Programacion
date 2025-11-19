import tkinter as tk
from tkinter import ttk, messagebox
from BaseWindow import VentanaBase

try:
    from . import Conexion as Conexion  # type: ignore
except ImportError:
    import Conexion as Conexion  # type: ignore


#Herencia (de VentanaBase)
class VentanaInventario(VentanaBase):
    def __init__(self, padre=None):
        super().__init__(padre, "D2 Supermercado - Inventario")
        self.valor_categoria = None
        self.tabla_productos = None
        self.selector_categoria = None

    def _construir_interfaz(self):
        self.ventana.geometry("960x640")
        self._alternar_pantalla()
        self._configurar_estilos()
        self.valor_categoria = tk.StringVar()
        contenedor = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=16, pady=16)
        cabecera = tk.Frame(contenedor, bg=self.COLOR_PRIMARIO)
        cabecera.pack(fill="x", pady=(0, 12))
        interior_cabecera = tk.Frame(cabecera, bg=self.COLOR_PRIMARIO)
        interior_cabecera.pack(fill="x", pady=4)
        tk.Label(
            interior_cabecera,
            text="Inventario",
            font=("Segoe UI", 20, "bold"),
            bg=self.COLOR_PRIMARIO,
            fg="white",
        ).pack(side="left", expand=True, padx=16, pady=8)
        logo = self._cargar_logo(interior_cabecera, tamano=(64, 64))
        if logo:
            logo.pack(side="right", padx=(8, 16), pady=8)
        cuerpo = tk.Frame(contenedor, bg=self.COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True)
        self._construir_panel_filtros(cuerpo)
        self._construir_panel_tabla(cuerpo)
        self._cargar_categorias()
        self._cargar_productos()

    def _configurar_estilos(self):
        estilo = ttk.Style(self.ventana)
        estilo.configure(
            "TablaInventario.Treeview",
            background=self.COLOR_SUPERFICIE,
            foreground=self.COLOR_TEXTO,
            fieldbackground=self.COLOR_SUPERFICIE,
            bordercolor=self.COLOR_SUPERFICIE,
        )
        estilo.map(
            "TablaInventario.Treeview",
            background=[("selected", self.COLOR_PRIMARIO)],
            foreground=[("selected", "#FFFFFF")],
        )
        estilo.configure(
            "TablaInventario.Heading",
            background=self.COLOR_PRIMARIO,
            foreground="white",
            borderwidth=0,
            relief="flat",
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

    def _construir_panel_filtros(self, contenedor):
        panel = tk.Frame(contenedor, bg=self.COLOR_SUPERFICIE, width=260)
        panel.pack(side="left", fill="y", padx=(0, 12))
        panel.pack_propagate(False)
        marco = tk.Frame(panel, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(
            marco,
            text="Categoría",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_SUPERFICIE,
            fg=self.COLOR_TEXTO,
        ).pack(anchor="w")
        self.selector_categoria = ttk.Combobox(
            marco,
            textvariable=self.valor_categoria,
            state="readonly",
            style="ListaClara.TCombobox",
        )
        self.selector_categoria.pack(fill="x", pady=4)
        botones = [
            ("Cargar categorías", self._cargar_categorias),
            ("Filtrar", lambda: self._cargar_productos(self.valor_categoria.get())),
            ("Mostrar todo", lambda: self._cargar_productos(None)),
            ("Añadir producto", self._abrir_formulario_producto),
            ("Actualizar stock", self._abrir_formulario_stock),
            ("Eliminar producto", self._confirmar_eliminacion),
        ]
        for texto, accion in botones:
            ttk.Button(panel, text=texto, command=accion, style="BotonOscuro.TButton").pack(
                fill="x", padx=12, pady=4
            )

    def _construir_panel_tabla(self, contenedor):
        panel = tk.Frame(contenedor, bg=self.COLOR_FONDO)
        panel.pack(side="left", fill="both", expand=True)
        marco = tk.Frame(panel, bg=self.COLOR_SUPERFICIE)
        marco.pack(fill="both", expand=True)
        columnas = ("id", "nombre", "categoria", "marca", "precio", "stock", "codigo")
        self.tabla_productos = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings",
            height=16,
            style="TablaInventario.Treeview",
        )
        configuracion = {
            "id": ("ID", 50, "center"),
            "nombre": ("Nombre", 220, "w"),
            "categoria": ("Categoría", 110, "w"),
            "marca": ("Marca", 110, "w"),
            "precio": ("Precio", 90, "center"),
            "stock": ("Stock", 80, "center"),
            "codigo": ("Código", 130, "center"),
        }
        for clave, (titulo, ancho, alineacion) in configuracion.items():
            self.tabla_productos.heading(clave, text=titulo)
            self.tabla_productos.column(clave, width=ancho, anchor=alineacion)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscroll=barra.set)
        self.tabla_productos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def _cargar_categorias(self):
        try:
            productos = Conexion.listar_productos()
            categorias = sorted({p["categoria"] for p in productos})
            self.selector_categoria["values"] = [""] + categorias
        except Exception as error:
            messagebox.showwarning("Aviso", f"No se pudieron cargar categorías:\n{error}")

    def _cargar_productos(self, categoria=None):
        try:
            productos = (
                Conexion.busqueda_categoria(categoria) if categoria else Conexion.listar_productos()
            )
            self.tabla_productos.delete(*self.tabla_productos.get_children())
            for producto in productos:
                self.tabla_productos.insert(
                    "",
                    "end",
                    values=(
                        producto["id_producto"],
                        producto["nombre_producto"],
                        producto["categoria"],
                        producto["marca"],
                        f"${float(producto['precio_venta']):.2f}",
                        producto["stock_actual"],
                        producto["codigo_barras"],
                    ),
                )
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar productos:\n{error}")

    def _obtener_seleccion(self):
        identificador = self.tabla_productos.focus()
        if not identificador:
            return None
        valores = self.tabla_productos.item(identificador, "values")
        return {
            "id": int(valores[0]),
            "nombre": valores[1],
            "stock": int(valores[5]),
        }

    def _abrir_formulario_producto(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Añadir producto")
        ventana.geometry("460x380")
        contenedor = ttk.Frame(ventana, padding=12)
        contenedor.pack(fill="both", expand=True)
        campos = [
            ("Nombre", "nombre_producto"),
            ("Descripción", "descripcion"),
            ("Categoría", "categoria"),
            ("Marca", "marca"),
            ("Valor unitario", "valor_unitario"),
            ("Precio venta", "precio_venta"),
            ("Stock inicial", "stock_actual"),
            ("Código barras", "codigo_barras"),
        ]
        valores = {}
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(contenedor, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=4)
            dato = tk.StringVar()
            ttk.Entry(contenedor, textvariable=dato, width=32).grid(row=fila, column=1, sticky="w")
            valores[clave] = dato

        def guardar():
            try:
                nombre = valores["nombre_producto"].get().strip()
                categoria = valores["categoria"].get().strip()
                if not nombre or not categoria:
                    messagebox.showwarning("Validación", "Nombre y categoría son obligatorios")
                    return
                nuevo = Conexion.crear_producto_inventario(
                    nombre,
                    valores["descripcion"].get().strip(),
                    categoria,
                    valores["marca"].get().strip(),
                    float(valores["valor_unitario"].get() or 0),
                    float(valores["precio_venta"].get() or 0),
                    int(valores["stock_actual"].get() or 0),
                    valores["codigo_barras"].get().strip() or None,
                )
                if nuevo:
                    messagebox.showinfo("Inventario", f"Producto registrado con ID {nuevo}")
                    ventana.destroy()
                    self._cargar_categorias()
                    self._cargar_productos()
                else:
                    messagebox.showerror("Inventario", "No se pudo registrar el producto")
            except Exception as error:
                messagebox.showerror("Inventario", f"Error al guardar:\n{error}")

        ttk.Button(contenedor, text="Guardar", command=guardar, style="BotonOscuro.TButton").grid(
            row=len(campos), column=0, columnspan=2, pady=12
        )

    def _abrir_formulario_stock(self):
        seleccion = self._obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Inventario", "Selecciona un producto para actualizar")
            return
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Actualizar stock")
        ventana.geometry("360x200")
        marco = ttk.Frame(ventana, padding=12)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text=f"ID: {seleccion['id']}").pack(anchor="w")
        ttk.Label(marco, text=f"Producto: {seleccion['nombre']}").pack(anchor="w")
        ttk.Label(marco, text=f"Stock actual: {seleccion['stock']}").pack(anchor="w", pady=(0, 8))
        nuevo_stock = tk.StringVar()
        ttk.Entry(marco, textvariable=nuevo_stock).pack(fill="x", pady=4)

        def aplicar():
            try:
                valor = int(nuevo_stock.get())
                if Conexion.actualizar_stock(seleccion["id"], valor):
                    messagebox.showinfo("Inventario", "Stock actualizado")
                    ventana.destroy()
                    self._cargar_productos(self.valor_categoria.get() or None)
                else:
                    messagebox.showerror("Inventario", "No se pudo actualizar el stock")
            except Exception as error:
                messagebox.showerror("Inventario", f"Error al actualizar:\n{error}")

        ttk.Button(marco, text="Aplicar", command=aplicar, style="BotonOscuro.TButton").pack(
            side="right", pady=8
        )

    def _confirmar_eliminacion(self):
        seleccion = self._obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Inventario", "Selecciona un producto para eliminar")
            return
        if not messagebox.askyesno(
            "Inventario",
            f"¿Deseas eliminar el producto {seleccion['nombre']} (ID {seleccion['id']})?",
        ):
            return
        try:
            if Conexion.eliminar_producto(seleccion["id"]):
                messagebox.showinfo("Inventario", "Producto eliminado")
                self._cargar_categorias()
                self._cargar_productos(self.valor_categoria.get() or None)
            else:
                messagebox.showerror("Inventario", "No se pudo eliminar el producto")
        except Exception as error:
            messagebox.showerror("Inventario", f"Error al eliminar:\n{error}")


def open_inventario(parent=None):
    ventana = VentanaInventario(parent)
    ventana.mostrar()

