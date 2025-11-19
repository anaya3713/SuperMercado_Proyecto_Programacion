from DatabaseClient import ClienteBaseDatos

_cliente = ClienteBaseDatos()


def crear_producto_inventario(nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual=0, codigo_barras=None):
    return _cliente.crear_producto_inventario(nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras)


def busqueda_categoria(categoria):
    return _cliente.busqueda_categoria(categoria)


def busqueda_producto(codigo_barras):
    return _cliente.busqueda_producto(codigo_barras)


def generar_factura(metodo_pago, nombre_cliente, cedula_cliente, items, fecha_venta=None, hora_venta=None):
    return _cliente.generar_factura(metodo_pago, nombre_cliente, cedula_cliente, items, fecha_venta, hora_venta)


def actualizar_stock(id_producto, nuevo_stock):
    return _cliente.actualizar_stock(id_producto, nuevo_stock)


def eliminar_producto(id_producto):
    return _cliente.eliminar_producto(id_producto)


def listar_productos():
    return _cliente.listar_productos()


def contabilidad(año=None):
    return _cliente.contabilidad(año)


def listar_categorias():
    return _cliente.listar_categorias()
