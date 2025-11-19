package com.supermercado;

import java.util.List;
import java.util.Map;

//Abstracción
public interface OperacionesBaseDatos {
    Integer crearProductoInventario(String nombreProducto, String descripcion, String categoria,
                                    String marca, double valorUnitario, double precioVenta,
                                    int stockActual, String codigoBarras);

    List<Map<String, Object>> busquedaCategoria(String categoria);

    Map<String, Object> busquedaProducto(String codigoBarras);

    Object generarFactura(String metodoPago, String nombreCliente, String cedulaCliente,
                          List<Map<String, Object>> items);

    boolean actualizarStock(int idProducto, int nuevoStock);

    boolean actualizarStock(int idProducto, int cantidad, boolean incrementar);

    boolean eliminarProducto(int idProducto);

    void close();

    List<Map<String, Object>> listarProductos();

    List<Map<String, Object>> contabilidad(Integer ano);

    List<String> listarCategorias();
}

