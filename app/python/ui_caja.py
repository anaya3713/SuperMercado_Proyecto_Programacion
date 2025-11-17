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
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Intentar importar qrcode para generar QR
try:
    import qrcode # type: ignore
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Intentar importar OpenCV para cámara
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Intentar importar pyzbar para detección de códigos de barras
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


# Guardar facturas en la carpeta `data/invoices` en la raíz del proyecto
FACTURAS_DIR = Path(__file__).resolve().parents[2] / "data" / "invoices"
FACTURAS_DIR.mkdir(parents=True, exist_ok=True)


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
            """Escanea códigos de barras CODE-128 usando la cámara"""
            if not PYZBAR_AVAILABLE:
                messagebox.showerror('Error', 'pyzbar no instalado.\nInstala con: pip install pyzbar')
                return
            
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror('Error', 'No se pudo acceder a la cámara')
                    return
                
                # Configurar resolución de la cámara
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                codigo_escaneado = None
                frames_sin_codigo = 0
                
                # Crear ventana
                cv2.namedWindow('Escanear Código de Barras CODE-128', cv2.WINDOW_AUTOSIZE)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Convertir a escala de grises para mejor detección
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detectar códigos de barras
                    codigos = decode(gray)
                    
                    # Procesar códigos encontrados
                    if codigos:
                        frames_sin_codigo = 0
                        for barcode in codigos:
                            # Decodificar el código
                            codigo_bytes = barcode.data
                            codigo_str = codigo_bytes.decode('utf-8') if isinstance(codigo_bytes, bytes) else codigo_bytes
                            tipo_codigo = barcode.type
                            
                            # Filtrar solo CODE-128
                            if tipo_codigo == 'CODE128':
                                codigo_escaneado = codigo_str
                                
                                # Dibujar rectángulo alrededor del código
                                (x, y, w, h) = barcode.rect
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                
                                # Mostrar el código en el frame
                                cv2.putText(frame, f"Código: {codigo_str}", (x, y - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                cv2.putText(frame, f"Tipo: {tipo_codigo}", (x, y + h + 20),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        frames_sin_codigo += 1
                        # Si pasan 5 frames sin detectar código, limpiar el anterior
                        if frames_sin_codigo > 5:
                            codigo_escaneado = None
                    
                    # Mostrar instrucciones en el frame
                    cv2.putText(frame, "Presiona SPACE para confirmar o ESC para cancelar", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    if codigo_escaneado:
                        cv2.putText(frame, f"Código detectado: {codigo_escaneado}", (10, 70),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Mostrar el frame
                    cv2.imshow('Escanear Código de Barras CODE-128', frame)
                    
                    # Capturar teclas
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == 27:  # ESC - Cancelar
                        break
                    elif key == 32:  # SPACE - Confirmar
                        if codigo_escaneado:
                            cap.release()
                            cv2.destroyAllWindows()
                            
                            # Buscar el producto con el código escaneado
                            try:
                                prod = Conexion.busqueda_producto(codigo_escaneado)
                                if prod:
                                    abrir_dialog_cantidad(prod)
                                else:
                                    messagebox.showwarning('No encontrado', f'Producto con código "{codigo_escaneado}" no encontrado en la base de datos')
                                    search_var.set('')
                            except Exception as e:
                                messagebox.showerror('Error', f'Error al buscar producto:\n{e}')
                            return
                        else:
                            messagebox.showwarning('Escaneo', 'No hay código detectado para confirmar')
                
                cap.release()
                cv2.destroyAllWindows()
                
            except ImportError:
                messagebox.showerror('Error', 'pyzbar no instalado.\nInstala con: pip install pyzbar')
            except Exception as e:
                messagebox.showerror('Error', f'Error con escaneo:\n{e}')
                try:
                    cap.release()
                    cv2.destroyAllWindows()
                except:
                    pass
        
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
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            import io
            
            filename = FACTURAS_DIR / f"Factura_{cliente_info['id_venta']:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(str(filename), pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
            styles = getSampleStyleSheet()
            elements = []
            
            # Encabezado con logo
            logo_path = Path(__file__).resolve().parents[2] / "assets" / "logo" / "Logo.png"
            header_data = []
            
            if logo_path.exists():
                logo = Image(str(logo_path), width=1*inch, height=1*inch)
                header_table = Table([[logo, f"FACTURA DE VENTA"]], colWidths=[1.2*inch, 4.8*inch])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (1, 0), (1, 0), 14),
                ]))
                elements.append(header_table)
            else:
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=14, textColor=colors.black, spaceAfter=12, alignment=1)
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
                ['', '', 'Iva:', '$0'],
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
            
            # QR simulado
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
            except Exception as e:
                pass
            
            elements.append(Spacer(1, 0.1 * inch))
            
            # Pie de página
            footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)
            elements.append(Paragraph("Gracias por su compra", footer_style))
            
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
