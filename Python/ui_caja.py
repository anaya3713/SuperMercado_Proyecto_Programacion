import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import Conexion
from datetime import datetime
import os
from pathlib import Path

# Intentar importar ReportLab para PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Intentar importar OpenCV para cámara
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


FACTURAS_DIR = Path(__file__).parent / "facturas"
FACTURAS_DIR.mkdir(exist_ok=True)


def open_caja(parent):
    win = tk.Toplevel(parent)
    win.title('Caja - Generar Factura')
    win.geometry('900x700')

    main_frame = ttk.Frame(win, padding=10)
    main_frame.pack(fill='both', expand=True)

    # ========== Panel Cliente ==========
    client_frame = ttk.LabelFrame(main_frame, text='Datos del Cliente', padding=8)
    client_frame.pack(fill='x', pady=(0, 8))

    ttk.Label(client_frame, text='Método de pago:').grid(row=0, column=0, sticky='w', padx=4, pady=4)
    metodo_var = tk.StringVar(value='EFECTIVO')
    ttk.Combobox(client_frame, textvariable=metodo_var, values=['EFECTIVO', 'TARJETA', 'CHEQUE', 'TRANSFERENCIA'], state='readonly').grid(row=0, column=1, sticky='w', padx=4)

    ttk.Label(client_frame, text='Nombre cliente:').grid(row=1, column=0, sticky='w', padx=4, pady=4)
    nombre_var = tk.StringVar()
    ttk.Entry(client_frame, textvariable=nombre_var).grid(row=1, column=1, sticky='w', padx=4)

    ttk.Label(client_frame, text='Cédula cliente:').grid(row=2, column=0, sticky='w', padx=4, pady=4)
    cedula_var = tk.StringVar()
    ttk.Entry(client_frame, textvariable=cedula_var).grid(row=2, column=1, sticky='w', padx=4)

    # ========== Panel Búsqueda de Productos ==========
    search_frame = ttk.LabelFrame(main_frame, text='Buscar Producto', padding=8)
    search_frame.pack(fill='x', pady=(0, 8))

    ttk.Label(search_frame, text='Código/Nombre:').pack(side='left', padx=4)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=20)
    search_entry.pack(side='left', padx=4)

    def buscar_producto():
        query = search_var.get().strip()
        if not query:
            messagebox.showwarning('Búsqueda', 'Ingresa un código de barras o nombre de producto')
            return
        try:
            # Buscar por código de barras primero
            prod = Conexion.busqueda_producto(query)
            if not prod:
                # Buscar por nombre
                todos = Conexion.listar_productos()
                prods = [p for p in todos if query.lower() in p['nombre_producto'].lower()]
                if not prods:
                    messagebox.showwarning('No encontrado', 'No se encontró el producto')
                    return
                if len(prods) == 1:
                    prod = prods[0]
                else:
                    # Mostrar diálogo de selección múltiple
                    mostrar_lista_seleccion(prods)
                    return
            abrir_dialog_cantidad(prod)
        except Exception as e:
            messagebox.showerror('Error', f'Error en búsqueda:\n{e}')

    ttk.Button(search_frame, text='Buscar', command=buscar_producto).pack(side='left', padx=4)

    if OPENCV_AVAILABLE:
        def escanear_camara():
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror('Error', 'No se pudo acceder a la cámara')
                    return
                
                messagebox.showinfo('Cámara', 'Presiona SPACE para capturar o ESC para cancelar')
                codigo_escaneado = None
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    cv2.imshow('Escanear Código de Barras', frame)
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == 27:  # ESC
                        break
                    elif key == 32:  # SPACE
                        # Aquí se podría integrar una librería de detección de códigos
                        # Por ahora, mostramos un prompt
                        messagebox.showinfo('Cámara', 'Función de escaneo aún en desarrollo')
                        break
                
                cap.release()
                cv2.destroyAllWindows()
            except Exception as e:
                messagebox.showerror('Error', f'Error con cámara:\n{e}')
        
        ttk.Button(search_frame, text='Escanear Cámara', command=escanear_camara).pack(side='left', padx=4)

    # ========== Tabla de Items ==========
    items_frame = ttk.LabelFrame(main_frame, text='Items del Carrito', padding=8)
    items_frame.pack(fill='both', expand=True, pady=(0, 8))

    # Crear Treeview para mostrar items
    tree_items = ttk.Treeview(items_frame, columns=('id', 'nombre', 'codigo', 'cantidad', 'precio_unit', 'subtotal'), height=10, show='headings')
    tree_items.heading('id', text='ID')
    tree_items.heading('nombre', text='Producto')
    tree_items.heading('codigo', text='Código')
    tree_items.heading('cantidad', text='Cant.')
    tree_items.heading('precio_unit', text='P. Unit.')
    tree_items.heading('subtotal', text='Subtotal')

    tree_items.column('id', width=40)
    tree_items.column('nombre', width=250)
    tree_items.column('codigo', width=100)
    tree_items.column('cantidad', width=60)
    tree_items.column('precio_unit', width=80)
    tree_items.column('subtotal', width=80)

    scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=tree_items.yview)
    tree_items.configure(yscroll=scrollbar.set)
    tree_items.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    carrito = []  # Lista para guardar items

    def mostrar_lista_seleccion(productos):
        """Muestra diálogo con lista de productos para seleccionar"""
        dlg = tk.Toplevel(win)
        dlg.title('Seleccionar Producto')
        dlg.geometry('500x400')
        
        ttk.Label(dlg, text='Selecciona un producto:').pack(anchor='w', padx=8, pady=8)
        
        tree = ttk.Treeview(dlg, columns=('nombre', 'categoria', 'stock'), height=15, show='headings')
        tree.heading('nombre', text='Nombre')
        tree.heading('categoria', text='Categoría')
        tree.heading('stock', text='Stock')
        tree.column('nombre', width=250)
        tree.column('categoria', width=120)
        tree.column('stock', width=80)
        
        for p in productos:
            tree.insert('', 'end', values=(p['nombre_producto'], p['categoria'], p['stock_actual']))
        
        tree.pack(fill='both', expand=True, padx=8, pady=8)
        
        def seleccionar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning('Seleccionar', 'Selecciona un producto')
                return
            idx = tree.index(sel)
            dlg.destroy()
            abrir_dialog_cantidad(productos[idx])
        
        ttk.Button(dlg, text='Aceptar', command=seleccionar).pack(pady=8)
        dlg.transient(win)
        dlg.grab_set()

    def abrir_dialog_cantidad(producto):
        """Abre diálogo para ingresar cantidad y agregar al carrito"""
        dlg = tk.Toplevel(win)
        dlg.title('Agregar al Carrito')
        dlg.geometry('400x280')
        
        frame = ttk.Frame(dlg, padding=12)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text=f"Producto: {producto['nombre_producto']}", font=('Arial', 10, 'bold')).pack(anchor='w', pady=8)
        ttk.Label(frame, text=f"Código: {producto['codigo_barras']}").pack(anchor='w')
        ttk.Label(frame, text=f"Precio venta: ${producto['precio_venta']:.2f}").pack(anchor='w')
        ttk.Label(frame, text=f"Stock disponible: {producto['stock_actual']}").pack(anchor='w', pady=(0, 8))
        
        ttk.Label(frame, text='Cantidad:').pack(anchor='w')
        cant_var = tk.StringVar(value='1')
        ttk.Entry(frame, textvariable=cant_var).pack(anchor='w', fill='x')
        
        ttk.Label(frame, text='Precio unitario ($):').pack(anchor='w', pady=(8, 0))
        precio_var = tk.StringVar(value=str(producto['precio_venta']))
        ttk.Entry(frame, textvariable=precio_var).pack(anchor='w', fill='x')
        
        def agregar():
            try:
                cantidad = int(cant_var.get())
                precio = float(precio_var.get())
                
                if cantidad <= 0:
                    messagebox.showwarning('Validación', 'Cantidad debe ser mayor a 0')
                    return
                if precio < 0:
                    messagebox.showwarning('Validación', 'Precio no puede ser negativo')
                    return
                
                subtotal = cantidad * precio
                
                carrito.append({
                    'id_producto': producto['id_producto'],
                    'nombre_producto': producto['nombre_producto'],
                    'codigo_barras': producto['codigo_barras'],
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal,
                })
                
                # Añadir a la tabla
                tree_items.insert('', 'end', values=(
                    producto['id_producto'],
                    producto['nombre_producto'],
                    producto['codigo_barras'],
                    cantidad,
                    f"${precio:.2f}",
                    f"${subtotal:.2f}"
                ))
                
                dlg.destroy()
                search_var.set('')
                messagebox.showinfo('Éxito', f"Producto '{producto['nombre_producto']}' añadido al carrito")
            except ValueError:
                messagebox.showerror('Error', 'Ingresa valores válidos')
        
        def cancelar():
            dlg.destroy()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=12)
        ttk.Button(btn_frame, text='Agregar', command=agregar).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Cancelar', command=cancelar).pack(side='left', padx=4)
        
        dlg.transient(win)
        dlg.grab_set()

    # ========== Botones de Acción ==========
    action_frame = ttk.Frame(main_frame)
    action_frame.pack(fill='x', pady=8)

    def limpiar_carrito():
        carrito.clear()
        for item in tree_items.get_children():
            tree_items.delete(item)
        messagebox.showinfo('Carrito', 'Carrito vaciado')

    def remover_item():
        sel = tree_items.focus()
        if not sel:
            messagebox.showwarning('Seleccionar', 'Selecciona un item para remover')
            return
        idx = tree_items.index(sel)
        tree_items.delete(sel)
        carrito.pop(idx)
        messagebox.showinfo('Éxito', 'Item removido del carrito')

    ttk.Button(action_frame, text='Limpiar Carrito', command=limpiar_carrito).pack(side='left', padx=4)
    ttk.Button(action_frame, text='Remover Item', command=remover_item).pack(side='left', padx=4)

    # ========== Resultado y Generación de Factura ==========
    result_frame = ttk.LabelFrame(main_frame, text='Resumen de Factura', padding=8)
    result_frame.pack(fill='both', expand=True)

    result_text = tk.Text(result_frame, height=8, state='disabled')
    result_text.pack(fill='both', expand=True)

    def generar_factura():
        if not carrito:
            messagebox.showwarning('Carrito vacío', 'Añade items al carrito antes de generar la factura')
            return
        
        nombre = nombre_var.get().strip()
        cedula = cedula_var.get().strip()
        metodo = metodo_var.get().strip()
        
        if not nombre or not cedula:
            messagebox.showwarning('Validación', 'Ingresa nombre y cédula del cliente')
            return
        
        try:
            # Preparar items para la BD
            items_bd = []
            for item in carrito:
                items_bd.append({
                    'id_producto': item['id_producto'],
                    'codigo_barras': item['codigo_barras'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                })
            
            # Generar factura en BD
            resultado = Conexion.generar_factura(metodo, nombre, cedula, items_bd)
            
            if not resultado:
                messagebox.showerror('Error', 'Error al generar factura en la BD')
                return
            
            cliente_info, productos = resultado
            
            # Mostrar resultado
            result_text.config(state='normal')
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, f"✓ FACTURA GENERADA\n")
            result_text.insert(tk.END, f"ID Venta: {cliente_info['id_venta']}\n")
            result_text.insert(tk.END, f"Fecha: {cliente_info['fecha_venta']}\n")
            result_text.insert(tk.END, f"Cliente: {cliente_info['nombre_cliente']} (Cédula: {cliente_info['cedula_cliente']})\n")
            result_text.insert(tk.END, f"Total: ${cliente_info['total_venta']:.2f}\n")
            result_text.insert(tk.END, f"Método: {cliente_info['metodo_pago']}\n")
            result_text.config(state='disabled')
            
            # Generar PDF
            if REPORTLAB_AVAILABLE:
                generar_pdf(cliente_info, productos)
                messagebox.showinfo('Éxito', f'Factura #{cliente_info["id_venta"]} generada y guardada como PDF')
            else:
                messagebox.showwarning('PDF', 'ReportLab no instalado. Factura generada en BD pero sin PDF.\nInstala: pip install reportlab')
            
            # Limpiar
            carrito.clear()
            for item in tree_items.get_children():
                tree_items.delete(item)
            search_var.set('')
            nombre_var.set('')
            cedula_var.set('')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al generar factura:\n{e}')

    def generar_pdf(cliente_info, productos):
        """Genera un archivo PDF con los datos de la factura"""
        try:
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            filename = FACTURAS_DIR / f"Factura_{cliente_info['id_venta']:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=12,
                alignment=1  # Center
            )
            
            elements = []
            
            # Título
            elements.append(Paragraph("FACTURA DE VENTA", title_style))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Datos del cliente
            client_data = [
                ['Factura #', f"{cliente_info['id_venta']:06d}"],
                ['Fecha', cliente_info['fecha_venta']],
                ['Hora', cliente_info['hora_venta']],
                ['Cliente', cliente_info['nombre_cliente']],
                ['Cédula', cliente_info['cedula_cliente']],
                ['Método Pago', cliente_info['metodo_pago']],
            ]
            
            client_table = Table(client_data, colWidths=[2 * inch, 4 * inch])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(client_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Tabla de productos
            product_data = [['ID', 'Producto', 'Código', 'Cantidad', 'Precio Unit.', 'Subtotal']]
            for p in productos:
                product_data.append([
                    str(p['id_producto']),
                    p['codigo_barras'],
                    f"{p['cantidad']}",
                    f"${p['precio_unitario']:.2f}",
                    f"${p['subtotal']:.2f}",
                ])
            
            product_table = Table(product_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(product_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Total
            total_data = [['TOTAL A PAGAR', f"${cliente_info['total_venta']:.2f}"]]
            total_table = Table(total_data, colWidths=[5*inch, 1.5*inch])
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#cccccc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(total_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Pie de página
            footer = Paragraph(
                "Gracias por su compra",
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.grey)
            )
            elements.append(footer)
            
            # Generar PDF
            doc.build(elements)
            print(f"✓ PDF generado: {filename}")
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            raise

    gen_btn_frame = ttk.Frame(main_frame)
    gen_btn_frame.pack(fill='x', pady=8)
    ttk.Button(gen_btn_frame, text='Generar Factura', command=generar_factura).pack(side='left', padx=4)

    win.transient(parent)
    win.grab_set()
    win.focus_force()
