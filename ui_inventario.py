import tkinter as tk
from tkinter import ttk, messagebox
import Conexion
def open_inventario(parent):
    win = tk.Toplevel(parent)
    win.title('Inventario')
    win.geometry('720x420')
    frame = ttk.Frame(win, padding=10)
    frame.pack(fill='both', expand=True)
    # Panel superior con filtros y acciones
    top_frame = ttk.Frame(frame)
    top_frame.pack(fill='x', pady=(0,8))
    ttk.Label(top_frame, text='Categoría:').pack(side='left')
    categoria_var = tk.StringVar()
    combo_cat = ttk.Combobox(top_frame, textvariable=categoria_var, width=24, state='readonly')
    combo_cat.pack(side='left', padx=6)
    def cargar_categorias():
        try:
            cur = Conexion.conn.cursor()
            cur.execute('SELECT DISTINCT categoria FROM public."productos" ORDER BY categoria')
            cats = [r[0] for r in cur.fetchall()]
            cur.close()
            combo_cat['values'] = [''] + cats
        except Exception as e:
            messagebox.showwarning('Aviso', f'No se pudieron cargar categorías:\n{e}')
    ttk.Button(top_frame, text='Cargar categorías', command=cargar_categorias).pack(side='left', padx=6)
    ttk.Button(top_frame, text='Filtrar', command=lambda: cargar_productos(categoria_var.get())).pack(side='left', padx=6)
    ttk.Button(top_frame, text='Mostrar todos', command=lambda: cargar_productos(None)).pack(side='left', padx=6)
    ttk.Button(top_frame, text='Añadir producto', command=lambda: abrir_agregar()).pack(side='right', padx=6)
    ttk.Button(top_frame, text='Actualizar stock', command=lambda: abrir_actualizar_stock()).pack(side='right', padx=6)
    # Lista de productos
    tree = ttk.Treeview(frame, columns=('id','nombre','categoria','marca','precio','stock','codigo'), show='headings')
    for c, w in [('id',60), ('nombre',220), ('categoria',100), ('marca',100), ('precio',80), ('stock',60), ('codigo',120)]:
        tree.heading(c, text=c)
        tree.column(c, width=w)
    tree.pack(fill='both', expand=True)
    def cargar_productos(categoria=None):
        try:
            if categoria:
                productos = Conexion.busqueda_categoria(categoria)
            else:
                productos = Conexion.listar_productos()
            for r in tree.get_children():
                tree.delete(r)
            for p in productos:
                tree.insert('', 'end', values=(p['id_producto'], p['nombre_producto'], p['categoria'], p['marca'], float(p['precio_venta']), p['stock_actual'], p['codigo_barras']))
        except Exception as e:
            messagebox.showerror('Error', f'No se pudieron cargar productos:\n{e}')
    # cargar inicialmente categorias y productos
    cargar_categorias()
    cargar_productos()
    btn_frame = ttk.Frame(win)
    btn_frame.pack(fill='x', pady=6)
    # botones adicionales en btn_frame si se desean (actualmente acciones están en top_frame)
    def abrir_agregar():
        dlg = tk.Toplevel(win)
        dlg.title('Añadir producto')
        dlg.geometry('480x380')
        f = ttk.Frame(dlg, padding=8)
        f.pack(fill='both', expand=True)
        entries = {}
        labels = [
            ('Nombre', 'nombre_producto'),
            ('Descripción', 'descripcion'),
            ('Categoría', 'categoria'),
            ('Marca', 'marca'),
            ('Valor unitario', 'valor_unitario'),
            ('Precio venta', 'precio_venta'),
            ('Stock inicial', 'stock_actual'),
            ('Código barras', 'codigo_barras'),
        ]
        for i, (lab, key) in enumerate(labels):
            ttk.Label(f, text=lab+':').grid(row=i, column=0, sticky='w', pady=4)
            var = tk.StringVar()
            ttk.Entry(f, textvariable=var, width=40).grid(row=i, column=1, sticky='w')
            entries[key] = var
        def agregar():
            try:
                nombre = entries['nombre_producto'].get().strip()
                descripcion = entries['descripcion'].get().strip()
                categoria = entries['categoria'].get().strip()
                marca = entries['marca'].get().strip()
                valor = float(entries['valor_unitario'].get() or 0)
                precio = float(entries['precio_venta'].get() or 0)
                stock = int(entries['stock_actual'].get() or 0)
                codigo = entries['codigo_barras'].get().strip() or None
                if not nombre or not categoria:
                    messagebox.showwarning('Validación', 'Nombre y categoría son obligatorios')
                    return
                new_id = Conexion.crear_producto_inventario(nombre, descripcion, categoria, marca, valor, precio, stock, codigo)
                if new_id:
                    messagebox.showinfo('Ok', f'Producto insertado con id {new_id}')
                    dlg.destroy()
                    cargar_categorias()
                    cargar_productos()
                else:
                    messagebox.showerror('Error', 'No se pudo insertar el producto (revisa consola)')
            except Exception as e:
                messagebox.showerror('Error', f'Error al agregar producto:\n{e}')
        ttk.Button(f, text='Agregar', command=agregar).grid(row=len(labels), column=0, columnspan=2, pady=12)
    def abrir_actualizar_stock():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning('Seleccionar', 'Selecciona un producto en la lista para actualizar el stock')
            return
        vals = tree.item(sel, 'values')
        id_producto = int(vals[0])
        nombre = vals[1]
        stock_actual = int(vals[5])
        dlg = tk.Toplevel(win)
        dlg.title(f'Actualizar stock - {nombre}')
        dlg.geometry('360x160')
        f = ttk.Frame(dlg, padding=8)
        f.pack(fill='both', expand=True)
        ttk.Label(f, text=f'ID: {id_producto}').pack(anchor='w')
        ttk.Label(f, text=f'Nombre: {nombre}').pack(anchor='w')
        ttk.Label(f, text=f'Stock actual: {stock_actual}').pack(anchor='w', pady=(0,8))
        nuevo_var = tk.StringVar()
        ttk.Label(f, text='Nuevo stock:').pack(anchor='w')
        ttk.Entry(f, textvariable=nuevo_var).pack(anchor='w')
        def aplicar():
            try:
                nuevo = int(nuevo_var.get())
                ok = Conexion.actualizar_stock(id_producto, nuevo)
                if ok:
                    messagebox.showinfo('Ok', 'Stock actualizado')
                    dlg.destroy()
                    cargar_productos(categoria_var.get() or None)
                else:
                    messagebox.showerror('Error', 'No se pudo actualizar stock (revisa consola)')
            except Exception as e:
                messagebox.showerror('Error', f'Error actualizando stock:\n{e}')
        ttk.Button(f, text='Aplicar', command=aplicar).pack(pady=8)

    win.transient(parent)
    win.grab_set()
    win.focus_force()

