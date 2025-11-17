import socket
import json
import sys

HOST = 'localhost'
PORT = 5000

def _enviar_comando(comando):
    """Envía un comando al servidor Java y recibe la respuesta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.sendall((json.dumps(comando) + '\n').encode('utf-8'))
        # Leer hasta encontrar un salto de línea (servidor envía una línea por respuesta)
        chunks = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b'\n' in chunk:
                break

        response = b''.join(chunks).decode('utf-8').strip()
        sock.close()

        # Intentar parsear JSON (aceptar objetos y arrays)
        try:
            return json.loads(response)
        except Exception:
            # Si no es JSON válido, devolver la cadena cruda
            return response
    except ConnectionRefusedError:
        print("Error: No se puede conectar al servidor Java. Asegúrate de que está ejecutándose en puerto 5000", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error de comunicación: {e}", file=sys.stderr)
        return None

def crear_producto_inventario(nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual=0, codigo_barras=None):
    comando = {
        'accion': 'CREAR_PRODUCTO',
        'nombre_producto': nombre_producto,
        'descripcion': descripcion,
        'categoria': categoria,
        'marca': marca,
        'valor_unitario': valor_unitario,
        'precio_venta': precio_venta,
        'stock_actual': stock_actual,
        'codigo_barras': codigo_barras
    }
    resultado = _enviar_comando(comando)
    if resultado and 'id_producto' in resultado:
        return resultado['id_producto']
    print(f"Error al crear producto: {resultado}", file=sys.stderr)
    return None

def busqueda_categoria(categoria):
    comando = {
        'accion': 'BUSQUEDA_CATEGORIA',
        'categoria': categoria
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, list):
        return resultado
    return []

def busqueda_producto(codigo_barras):
    comando = {
        'accion': 'BUSQUEDA_PRODUCTO',
        'codigo_barras': codigo_barras
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, dict) and 'error' not in resultado:
        return resultado
    return None

def generar_factura(metodo_pago, nombre_cliente, cedula_cliente, items, fecha_venta=None, hora_venta=None):
    comando = {
        'accion': 'GENERAR_FACTURA',
        'metodo_pago': metodo_pago,
        'nombre_cliente': nombre_cliente,
        'cedula_cliente': cedula_cliente,
        'items': items
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, dict):
        if 'error' in resultado:
            print(f"Error al generar factura: {resultado['error']}", file=sys.stderr)
            return None
        return [resultado.get('cliente_info'), resultado.get('productos')]
    return None

def actualizar_stock(id_producto, nuevo_stock):
    comando = {
        'accion': 'ACTUALIZAR_STOCK',
        'id_producto': id_producto,
        'nuevo_stock': nuevo_stock
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, dict):
        return 'mensaje' in resultado or 'error' not in resultado
    return False
        
def eliminar_producto(id_producto):
    comando = {
        'accion': 'ELIMINAR_PRODUCTO',
        'id_producto': id_producto
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, dict):
        return 'mensaje' in resultado or 'error' not in resultado
    return False
        
def listar_productos():
    comando = {
        'accion': 'LISTAR_PRODUCTOS'
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, list):
        return resultado
    return []
        
def contabilidad(año=None):
    comando = {
        'accion': 'CONTABILIDAD',
        'ano': año
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, list):
        return resultado
    return []

def listar_categorias():
    comando = {
        'accion': 'LISTAR_CATEGORIAS'
    }
    resultado = _enviar_comando(comando)
    if isinstance(resultado, list):
        return resultado
    return []
