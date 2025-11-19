import socket
import json
import sys
from typing import Optional, List, Dict, Any


#Encapsulación
class ClienteBaseDatos:
    def __init__(self, servidor: str = "localhost", puerto: int = 5000):
        self._servidor = servidor
        self._puerto = puerto
        self._tiempo_espera = 5.0

    @property
    def servidor(self) -> str:
        return self._servidor

    @property
    def puerto(self) -> int:
        return self._puerto

    def _enviar_orden(self, orden: Dict[str, Any]) -> Optional[Any]:
        try:
            conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conexion.settimeout(self._tiempo_espera)
            conexion.connect((self._servidor, self._puerto))
            conexion.sendall((json.dumps(orden) + "\n").encode("utf-8"))
            fragmentos = []
            while True:
                bloque = conexion.recv(4096)
                if not bloque:
                    break
                fragmentos.append(bloque)
                if b"\n" in bloque:
                    break
            respuesta = b"".join(fragmentos).decode("utf-8").strip()
            conexion.close()
            try:
                return json.loads(respuesta)
            except Exception:
                return respuesta
        except ConnectionRefusedError:
            print(
                f"No se puede conectar al servidor {self._servidor}:{self._puerto}",
                file=sys.stderr,
            )
            return None
        except Exception as error:
            print(f"Error de comunicación: {error}", file=sys.stderr)
            return None

    def crear_producto_inventario(
        self,
        nombre_producto: str,
        descripcion: str,
        categoria: str,
        marca: str,
        valor_unitario: float,
        precio_venta: float,
        stock_actual: int = 0,
        codigo_barras: Optional[str] = None,
    ) -> Optional[int]:
        orden = {
            "accion": "CREAR_PRODUCTO",
            "nombre_producto": nombre_producto,
            "descripcion": descripcion,
            "categoria": categoria,
            "marca": marca,
            "valor_unitario": valor_unitario,
            "precio_venta": precio_venta,
            "stock_actual": stock_actual,
            "codigo_barras": codigo_barras,
        }
        respuesta = self._enviar_orden(orden)
        if respuesta and "id_producto" in respuesta:
            return respuesta["id_producto"]
        print(f"Error al crear producto: {respuesta}", file=sys.stderr)
        return None

    def busqueda_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        orden = {"accion": "BUSQUEDA_CATEGORIA", "categoria": categoria}
        respuesta = self._enviar_orden(orden)
        return respuesta if isinstance(respuesta, list) else []

    def busqueda_producto(self, codigo_barras: str) -> Optional[Dict[str, Any]]:
        orden = {"accion": "BUSQUEDA_PRODUCTO", "codigo_barras": codigo_barras}
        respuesta = self._enviar_orden(orden)
        if isinstance(respuesta, dict) and "error" not in respuesta:
            return respuesta
        return None

    def busqueda_producto_por_id(self, id_producto: int) -> Optional[Dict[str, Any]]:
        for producto in self.listar_productos():
            if producto.get("id_producto") == id_producto:
                return producto
        return None

    def generar_factura(
        self,
        metodo_pago: str,
        nombre_cliente: str,
        cedula_cliente: str,
        articulos: List[Dict[str, Any]],
        fecha_venta: Optional[str] = None,
        hora_venta: Optional[str] = None,
    ) -> Optional[List[Any]]:
        orden = {
            "accion": "GENERAR_FACTURA",
            "metodo_pago": metodo_pago,
            "nombre_cliente": nombre_cliente,
            "cedula_cliente": cedula_cliente,
            "items": articulos,
        }
        respuesta = self._enviar_orden(orden)
        if isinstance(respuesta, dict):
            if "error" in respuesta:
                print(f"Error al generar factura: {respuesta['error']}", file=sys.stderr)
                return None
            return [respuesta.get("cliente_info"), respuesta.get("productos")]
        return None

    def actualizar_stock(self, id_producto: int, nuevo_stock: int) -> bool:
        orden = {
            "accion": "ACTUALIZAR_STOCK",
            "id_producto": id_producto,
            "nuevo_stock": nuevo_stock,
        }
        respuesta = self._enviar_orden(orden)
        if isinstance(respuesta, dict):
            return "mensaje" in respuesta or "error" not in respuesta
        return False

    def actualizar_stock_relativo(
        self,
        id_producto: int,
        cantidad: int,
        incrementar: bool = True,
    ) -> bool:
        producto = self.busqueda_producto_por_id(id_producto)
        if not producto:
            return False
        stock_actual = producto.get("stock_actual", 0)
        nuevo_stock = stock_actual + cantidad if incrementar else stock_actual - cantidad
        if nuevo_stock < 0:
            nuevo_stock = 0
        return self.actualizar_stock(id_producto, nuevo_stock)

    def eliminar_producto(self, id_producto: int) -> bool:
        orden = {"accion": "ELIMINAR_PRODUCTO", "id_producto": id_producto}
        respuesta = self._enviar_orden(orden)
        if isinstance(respuesta, dict):
            return "mensaje" in respuesta or "error" not in respuesta
        return False

    def listar_productos(self) -> List[Dict[str, Any]]:
        respuesta = self._enviar_orden({"accion": "LISTAR_PRODUCTOS"})
        return respuesta if isinstance(respuesta, list) else []

    def contabilidad(self, año: Optional[int] = None) -> List[Dict[str, Any]]:
        respuesta = self._enviar_orden({"accion": "CONTABILIDAD", "ano": año})
        return respuesta if isinstance(respuesta, list) else []

    def listar_categorias(self) -> List[str]:
        respuesta = self._enviar_orden({"accion": "LISTAR_CATEGORIAS"})
        return respuesta if isinstance(respuesta, list) else []


_cliente_bd = ClienteBaseDatos()


def crear_producto_inventario(*args, **kwargs):
    return _cliente_bd.crear_producto_inventario(*args, **kwargs)


def busqueda_categoria(*args, **kwargs):
    return _cliente_bd.busqueda_categoria(*args, **kwargs)


def busqueda_producto(*args, **kwargs):
    return _cliente_bd.busqueda_producto(*args, **kwargs)


def generar_factura(*args, **kwargs):
    return _cliente_bd.generar_factura(*args, **kwargs)


def actualizar_stock(*args, **kwargs):
    return _cliente_bd.actualizar_stock(*args, **kwargs)


def eliminar_producto(*args, **kwargs):
    return _cliente_bd.eliminar_producto(*args, **kwargs)


def listar_productos(*args, **kwargs):
    return _cliente_bd.listar_productos(*args, **kwargs)


def contabilidad(*args, **kwargs):
    return _cliente_bd.contabilidad(*args, **kwargs)


def listar_categorias(*args, **kwargs):
    return _cliente_bd.listar_categorias(*args, **kwargs)

