import psycopg2
from psycopg2 import sql, extras
import sys

# Conexión a la base de datos
conn = psycopg2.connect(
    host="localhost",
    user="supermercado",
    password="Super123",
    dbname="bd_productos_supermercado"
)

def crear_producto_inventario(nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual=0, codigo_barras=None):
    insert_query = sql.SQL(
        """
        INSERT INTO public."productos"
            (nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_producto;
        """
    )

    cur = conn.cursor()
    try:
        cur.execute(insert_query, (nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras))
        generated_id = cur.fetchone()[0]
        conn.commit()
        return generated_id
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"Error de integridad al insertar producto: {e}", file=sys.stderr)
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar producto: {e}", file=sys.stderr)
        return None
    finally:
        cur.close()

def busqueda_categoria(categoria):
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cur.execute('SELECT * FROM public."productos" WHERE categoria = %s ORDER BY nombre_producto', (categoria,))
        return cur.fetchall()
    finally:
        cur.close()

def busqueda_producto(codigo_barras):
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cur.execute('SELECT * FROM public."productos" WHERE codigo_barras = %s', (codigo_barras,))
        return cur.fetchone()
    finally:
        cur.close()

def generar_factura(metodo_pago, nombre_cliente, cedula_cliente, items, fecha_venta=None, hora_venta=None):
    """
    - items (list of dict): cada dict debe tener las claves:
        - id_producto (int) o codigo_barras (str)
        - cantidad (int)
        - precio_unitario (Decimal/float)
    """
    from datetime import date, datetime

    if not items or not isinstance(items, (list, tuple)):
        print("La lista de items está vacía o tiene un formato inválido.", file=sys.stderr)
        return None

    # Calcula fecha y hora si no se proporcionan
    if fecha_venta is None:
        fecha_venta = date.today()
    if hora_venta is None:
        hora_venta = datetime.now().time()

    cur = conn.cursor()
    try:
        # Calcular totales y chequear stock
        productos_a_insertar = []
        total_venta = 0

        for item in items:
            # permitir id_producto o codigo_barras
            id_producto = item.get('id_producto')
            codigo_barras = item.get('codigo_barras')
            cantidad = int(item.get('cantidad', 0))
            precio_unitario = float(item.get('precio_unitario', 0))

            if cantidad <= 0 or precio_unitario < 0:
                raise ValueError(f"Cantidad o precio inválido para el item: {item}")

            # Obtener id_producto si sólo se dio codigo_barras
            if id_producto is None and codigo_barras is not None:
                cur.execute('SELECT id_producto FROM public."productos" WHERE codigo_barras = %s', (codigo_barras,))
                row = cur.fetchone()
                if row:
                    id_producto = row[0]
                else:
                    raise ValueError(f"No existe producto con codigo_barras={codigo_barras}")

            if id_producto is None:
                raise ValueError(f"id_producto o codigo_barras requerido en el item: {item}")
            
            # Verificar stock disponible
            cur.execute('SELECT stock_actual, nombre_producto FROM public."productos" WHERE id_producto = %s FOR UPDATE', (id_producto,))
            prod = cur.fetchone()
            if not prod:
                raise ValueError(f"Producto con id {id_producto} no encontrado")
            stock_actual = prod[0]
            nombre_producto = prod[1]

            if stock_actual is None:
                stock_actual = 0

            if stock_actual < cantidad:
                raise ValueError(f"Stock insuficiente para el producto {nombre_producto} (id {id_producto}): disponible {stock_actual}, requerido {cantidad})")

            subtotal = round(cantidad * precio_unitario, 2)
            total_venta += subtotal

            productos_a_insertar.append({
                'id_producto': id_producto,
                'codigo_barras': codigo_barras,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal,
            })

        # Insertar en tabla ventas
        cur.execute(
            'INSERT INTO public."ventas" (fecha_venta, hora_venta, total_venta, metodo_pago, nombre_cliente, cedula_cliente) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_venta',
            (fecha_venta, hora_venta, total_venta, metodo_pago, nombre_cliente, cedula_cliente)
        )
        id_venta = cur.fetchone()[0]

        # Insertar cada detalle y actualizar stock
        for p in productos_a_insertar:
            cur.execute(
                'INSERT INTO public."detalle_ventas" (id_venta, id_producto, codigo_barras, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)',
                (id_venta, p['id_producto'], p['codigo_barras'], p['cantidad'], p['precio_unitario'], p['subtotal'])
            )

            # Actualizar stock
            cur.execute('UPDATE public."productos" SET stock_actual = stock_actual - %s WHERE id_producto = %s', (p['cantidad'], p['id_producto']))

        conn.commit()

        cliente_info = {
            'id_venta': id_venta,
            'fecha_venta': str(fecha_venta),
            'hora_venta': str(hora_venta),
            'total_venta': round(total_venta, 2),
            'metodo_pago': metodo_pago,
            'nombre_cliente': nombre_cliente,
            'cedula_cliente': cedula_cliente,
        }

        return [cliente_info, productos_a_insertar]

    except Exception as e:
        conn.rollback()
        print(f"Error al generar factura: {e}", file=sys.stderr)
        return None
    finally:
        cur.close()

def actualizar_stock(id_producto, nuevo_stock):
    update_query = sql.SQL(
        """
        UPDATE public."productos"
        SET stock_actual = %s
        WHERE id_producto = %s;
        """
    )

    cur = conn.cursor()
    try:
        cur.execute(update_query, (nuevo_stock, id_producto))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar el stock: {e}", file=sys.stderr)
        return False
    finally:
        cur.close()
        
def eliminar_producto(id_producto):
    delete_query = sql.SQL(
        """
        DELETE FROM public."productos"
        WHERE id_producto = %s;
        """
    )
    cur = conn.cursor()
    try:
        cur.execute(delete_query, (id_producto,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar el producto: {e}", file=sys.stderr)
        return False
    finally:
        cur.close()
        
def listar_productos():
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cur.execute('SELECT * FROM public."productos" ORDER BY nombre_producto')
        return cur.fetchall()
    finally:
        cur.close()
        
def contabilidad(año=None):
    """
    Genera un informe contable agregado por mes.

    Retorna una lista de dicts, cada uno con:
      - mes: 'YYYY-MM'
      - total_ingresos: suma de ventas (ventas.total_venta)
      - total_costos: suma de (detalle.cantidad * productos.valor_unitario)
      - total_subtotales: suma de detalle_ventas.subtotal
      - total_unidades: suma de cantidad vendida

    Parámetro opcional:
      - año (int): si se proporciona, filtra el año de las ventas.
    """
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        if año is None:
            query = '''
            SELECT
                to_char(DATE_TRUNC('month', v.fecha_venta), 'YYYY-MM') AS mes,
                COALESCE(SUM(v.total_venta),0) AS total_ingresos,
                COALESCE(SUM(d.cantidad * p.valor_unitario),0) AS total_costos,
                COALESCE(SUM(d.subtotal),0) AS total_subtotales,
                COALESCE(SUM(d.cantidad),0) AS total_unidades
            FROM public."ventas" v
            JOIN public."detalle_ventas" d ON d.id_venta = v.id_venta
            JOIN public."productos" p ON p.id_producto = d.id_producto
            GROUP BY mes
            ORDER BY mes;
            '''
            cur.execute(query)
        else:
            query = '''
            SELECT
                to_char(DATE_TRUNC('month', v.fecha_venta), 'YYYY-MM') AS mes,
                COALESCE(SUM(v.total_venta),0) AS total_ingresos,
                COALESCE(SUM(d.cantidad * p.valor_unitario),0) AS total_costos,
                COALESCE(SUM(d.subtotal),0) AS total_subtotales,
                COALESCE(SUM(d.cantidad),0) AS total_unidades
            FROM public."ventas" v
            JOIN public."detalle_ventas" d ON d.id_venta = v.id_venta
            JOIN public."productos" p ON p.id_producto = d.id_producto
            WHERE EXTRACT(YEAR FROM v.fecha_venta) = %s
            GROUP BY mes
            ORDER BY mes;
            '''
            cur.execute(query, (int(año),))

        rows = cur.fetchall()
        resultado = []
        for r in rows:
            resultado.append({
                'mes': r['mes'],
                'total_ingresos': float(r['total_ingresos']),
                'total_costos': float(r['total_costos']),
                'total_subtotales': float(r['total_subtotales']),
                'total_unidades': int(r['total_unidades']),
            })

        return resultado
    finally:
        cur.close()