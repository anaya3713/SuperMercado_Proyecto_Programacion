package com.supermercado;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

//Herencia (implementa OperacionesBaseDatos)
public class ConexionBaseDatos implements OperacionesBaseDatos {
    private static final String URL = "jdbc:postgresql://localhost:5432/bd_productos_supermercado";
    private static final String USUARIO = "supermercado";
    private static final String CLAVE = "Super123";
    //Encapsulación
    private Connection conexion;

    public ConexionBaseDatos() {
        try {
            Class.forName("org.postgresql.Driver");
            conexion = DriverManager.getConnection(URL, USUARIO, CLAVE);
            System.out.println("[BD] Conectado a " + URL);
        } catch (ClassNotFoundException | SQLException error) {
            System.err.println("[BD] Error de conexión: " + error.getMessage());
        }
    }

    public boolean estaConectado() {
        try {
            return conexion != null && !conexion.isClosed();
        } catch (SQLException error) {
            return false;
        }
    }

    private Map<String, Object> mapearProducto(ResultSet resultado) throws SQLException {
        Map<String, Object> fila = new HashMap<>();
        fila.put("id_producto", resultado.getInt("id_producto"));
        fila.put("nombre_producto", resultado.getString("nombre_producto"));
        fila.put("descripcion", resultado.getString("descripcion"));
        fila.put("categoria", resultado.getString("categoria"));
        fila.put("marca", resultado.getString("marca"));
        fila.put("valor_unitario", resultado.getDouble("valor_unitario"));
        fila.put("precio_venta", resultado.getDouble("precio_venta"));
        fila.put("stock_actual", resultado.getInt("stock_actual"));
        fila.put("codigo_barras", resultado.getString("codigo_barras"));
        return fila;
    }

    @Override
    public void close() {
        try {
            if (conexion != null && !conexion.isClosed()) {
                conexion.close();
            }
        } catch (SQLException error) {
            System.err.println("Error al cerrar conexión: " + error.getMessage());
        }
    }

    @Override
    public Integer crearProductoInventario(String nombreProducto, String descripcion, String categoria,
                                           String marca, double valorUnitario, double precioVenta,
                                           int stockActual, String codigoBarras) {
        String sql = "INSERT INTO public.\"productos\" (nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras) VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id_producto";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setString(1, nombreProducto);
            sentencia.setString(2, descripcion);
            sentencia.setString(3, categoria);
            sentencia.setString(4, marca);
            sentencia.setDouble(5, valorUnitario);
            sentencia.setDouble(6, precioVenta);
            sentencia.setInt(7, stockActual);
            sentencia.setString(8, codigoBarras);
            ResultSet resultado = sentencia.executeQuery();
            if (resultado.next()) {
                return resultado.getInt("id_producto");
            }
        } catch (SQLException error) {
            System.err.println("Error al insertar producto: " + error.getMessage());
        }
        return null;
    }

    @Override
    public List<Map<String, Object>> busquedaCategoria(String categoria) {
        List<Map<String, Object>> filas = new ArrayList<>();
        String sql = "SELECT * FROM public.\"productos\" WHERE categoria = ? ORDER BY nombre_producto";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setString(1, categoria);
            ResultSet resultado = sentencia.executeQuery();
            while (resultado.next()) {
                filas.add(mapearProducto(resultado));
            }
        } catch (SQLException error) {
            System.err.println("Error en busquedaCategoria: " + error.getMessage());
        }
        return filas;
    }

    @Override
    public Map<String, Object> busquedaProducto(String codigoBarras) {
        String sql = "SELECT * FROM public.\"productos\" WHERE codigo_barras = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setString(1, codigoBarras);
            ResultSet resultado = sentencia.executeQuery();
            if (resultado.next()) {
                return mapearProducto(resultado);
            }
        } catch (SQLException error) {
            System.err.println("Error en busquedaProducto: " + error.getMessage());
        }
        return null;
    }

    //Sobrecarga
    public Map<String, Object> busquedaProducto(int idProducto) {
        String sql = "SELECT * FROM public.\"productos\" WHERE id_producto = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setInt(1, idProducto);
            ResultSet resultado = sentencia.executeQuery();
            if (resultado.next()) {
                return mapearProducto(resultado);
            }
        } catch (SQLException error) {
            System.err.println("Error en busquedaProducto por ID: " + error.getMessage());
        }
        return null;
    }

    //Sobrecarga
    public List<Map<String, Object>> busquedaProductoPorNombre(String nombreProducto) {
        List<Map<String, Object>> filas = new ArrayList<>();
        String sql = "SELECT * FROM public.\"productos\" WHERE LOWER(nombre_producto) LIKE LOWER(?) ORDER BY nombre_producto";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setString(1, "%" + nombreProducto + "%");
            ResultSet resultado = sentencia.executeQuery();
            while (resultado.next()) {
                filas.add(mapearProducto(resultado));
            }
        } catch (SQLException error) {
            System.err.println("Error en busquedaProductoPorNombre: " + error.getMessage());
        }
        return filas;
    }

    @Override
    public Object generarFactura(String metodoPago, String nombreCliente, String cedulaCliente, List<Map<String, Object>> items) {
        if (items == null || items.isEmpty()) {
            return null;
        }
        try {
            conexion.setAutoCommit(false);
            double totalVenta = 0;
            List<Map<String, Object>> productosPreparados = new ArrayList<>();
            for (Map<String, Object> item : items) {
                Integer idProducto = item.containsKey("id_producto") && item.get("id_producto") != null
                        ? ((Number) item.get("id_producto")).intValue()
                        : null;
                String codigoBarras = item.containsKey("codigo_barras") ? (String) item.get("codigo_barras") : null;
                int cantidad = ((Number) item.get("cantidad")).intValue();
                double precioUnitario = ((Number) item.get("precio_unitario")).doubleValue();
                if (idProducto == null && codigoBarras != null) {
                    String sql = "SELECT id_producto FROM public.\"productos\" WHERE codigo_barras = ?";
                    try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
                        sentencia.setString(1, codigoBarras);
                        ResultSet resultado = sentencia.executeQuery();
                        if (resultado.next()) {
                            idProducto = resultado.getInt("id_producto");
                        }
                    }
                }
                if (idProducto == null) {
                    conexion.rollback();
                    conexion.setAutoCommit(true);
                    return null;
                }
                String sqlStock = "SELECT stock_actual, nombre_producto, codigo_barras FROM public.\"productos\" WHERE id_producto = ? FOR UPDATE";
                try (PreparedStatement sentenciaStock = conexion.prepareStatement(sqlStock)) {
                    sentenciaStock.setInt(1, idProducto);
                    ResultSet resultadoStock = sentenciaStock.executeQuery();
                    if (!resultadoStock.next() || resultadoStock.getInt("stock_actual") < cantidad) {
                        conexion.rollback();
                        conexion.setAutoCommit(true);
                        return null;
                    }
                    double subtotal = Math.round(cantidad * precioUnitario * 100.0) / 100.0;
                    totalVenta += subtotal;
                    Map<String, Object> preparado = new HashMap<>();
                    preparado.put("id_producto", idProducto);
                    preparado.put("nombre_producto", resultadoStock.getString("nombre_producto"));
                    String codigoFinal = codigoBarras;
                    if (codigoFinal == null || codigoFinal.isEmpty()) {
                        codigoFinal = resultadoStock.getString("codigo_barras");
                        if (codigoFinal == null) {
                            codigoFinal = "";
                        }
                    }
                    preparado.put("codigo_barras", codigoFinal);
                    preparado.put("cantidad", cantidad);
                    preparado.put("precio_unitario", precioUnitario);
                    preparado.put("subtotal", subtotal);
                    productosPreparados.add(preparado);
                }
            }
            int idVenta = insertarVenta(metodoPago, nombreCliente, cedulaCliente, totalVenta);
            registrarDetalleYStock(productosPreparados, idVenta);
            conexion.commit();
            conexion.setAutoCommit(true);
            Map<String, Object> clienteInfo = new HashMap<>();
            clienteInfo.put("id_venta", idVenta);
            clienteInfo.put("fecha_venta", new java.util.Date());
            clienteInfo.put("hora_venta", new java.sql.Time(System.currentTimeMillis()).toString());
            clienteInfo.put("total_venta", totalVenta);
            clienteInfo.put("metodo_pago", metodoPago);
            clienteInfo.put("nombre_cliente", nombreCliente);
            clienteInfo.put("cedula_cliente", cedulaCliente);
            Map<String, Object> respuesta = new HashMap<>();
            respuesta.put("cliente_info", clienteInfo);
            respuesta.put("productos", productosPreparados);
            return respuesta;
        } catch (SQLException error) {
            try {
                conexion.rollback();
                conexion.setAutoCommit(true);
            } catch (SQLException rollback) {
                System.err.println("Error al revertir transacción: " + rollback.getMessage());
            }
            System.err.println("Error al generar factura: " + error.getMessage());
        }
        return null;
    }

    private int insertarVenta(String metodoPago, String nombreCliente, String cedulaCliente, double totalVenta) throws SQLException {
        String sqlVenta = "INSERT INTO public.\"ventas\" (fecha_venta, hora_venta, total_venta, metodo_pago, nombre_cliente, cedula_cliente) VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, ?, ?) RETURNING id_venta";
        try (PreparedStatement sentencia = conexion.prepareStatement(sqlVenta)) {
            sentencia.setDouble(1, totalVenta);
            sentencia.setString(2, metodoPago);
            sentencia.setString(3, nombreCliente);
            sentencia.setString(4, cedulaCliente);
            ResultSet resultado = sentencia.executeQuery();
            if (resultado.next()) {
                return resultado.getInt("id_venta");
            }
        }
        return 0;
    }

    private void registrarDetalleYStock(List<Map<String, Object>> productos, int idVenta) throws SQLException {
        String sqlDetalle = "INSERT INTO public.\"detalle_ventas\" (id_venta, id_producto, codigo_barras, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)";
        String sqlActualizar = "UPDATE public.\"productos\" SET stock_actual = stock_actual - ? WHERE id_producto = ?";
        for (Map<String, Object> producto : productos) {
            try (PreparedStatement sentenciaDetalle = conexion.prepareStatement(sqlDetalle)) {
                sentenciaDetalle.setInt(1, idVenta);
                sentenciaDetalle.setInt(2, ((Number) producto.get("id_producto")).intValue());
                sentenciaDetalle.setString(3, (String) producto.get("codigo_barras"));
                sentenciaDetalle.setInt(4, ((Number) producto.get("cantidad")).intValue());
                sentenciaDetalle.setDouble(5, ((Number) producto.get("precio_unitario")).doubleValue());
                sentenciaDetalle.setDouble(6, ((Number) producto.get("subtotal")).doubleValue());
                sentenciaDetalle.executeUpdate();
            }
            try (PreparedStatement sentenciaActualizar = conexion.prepareStatement(sqlActualizar)) {
                sentenciaActualizar.setInt(1, ((Number) producto.get("cantidad")).intValue());
                sentenciaActualizar.setInt(2, ((Number) producto.get("id_producto")).intValue());
                sentenciaActualizar.executeUpdate();
            }
        }
    }

    @Override
    public boolean actualizarStock(int idProducto, int nuevoStock) {
        String sql = "UPDATE public.\"productos\" SET stock_actual = ? WHERE id_producto = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setInt(1, nuevoStock);
            sentencia.setInt(2, idProducto);
            sentencia.executeUpdate();
            return true;
        } catch (SQLException error) {
            System.err.println("Error al actualizar stock: " + error.getMessage());
        }
        return false;
    }

    @Override
    //Sobrecarga
    public boolean actualizarStock(int idProducto, int cantidad, boolean incrementar) {
        String sql = incrementar
                ? "UPDATE public.\"productos\" SET stock_actual = stock_actual + ? WHERE id_producto = ?"
                : "UPDATE public.\"productos\" SET stock_actual = stock_actual - ? WHERE id_producto = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setInt(1, cantidad);
            sentencia.setInt(2, idProducto);
            sentencia.executeUpdate();
            return true;
        } catch (SQLException error) {
            System.err.println("Error al modificar stock: " + error.getMessage());
        }
        return false;
    }

    @Override
    public boolean eliminarProducto(int idProducto) {
        String sqlValidacion = "SELECT COUNT(*) FROM public.\"detalle_ventas\" WHERE id_producto = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sqlValidacion)) {
            sentencia.setInt(1, idProducto);
            ResultSet resultado = sentencia.executeQuery();
            if (resultado.next() && resultado.getInt(1) > 0) {
                System.err.println("Producto con ventas registradas, no se puede eliminar");
                return false;
            }
        } catch (SQLException error) {
            System.err.println("Error al validar producto: " + error.getMessage());
            return false;
        }
        String sql = "DELETE FROM public.\"productos\" WHERE id_producto = ?";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setInt(1, idProducto);
            sentencia.executeUpdate();
            return true;
        } catch (SQLException error) {
            System.err.println("Error al eliminar producto: " + error.getMessage());
        }
        return false;
    }

    @Override
    public List<Map<String, Object>> listarProductos() {
        List<Map<String, Object>> filas = new ArrayList<>();
        String sql = "SELECT * FROM public.\"productos\" ORDER BY nombre_producto";
        try (Statement sentencia = conexion.createStatement()) {
            ResultSet resultado = sentencia.executeQuery(sql);
            while (resultado.next()) {
                filas.add(mapearProducto(resultado));
            }
        } catch (SQLException error) {
            System.err.println("Error al listar productos: " + error.getMessage());
        }
        return filas;
    }

    @Override
    public List<Map<String, Object>> contabilidad(Integer ano) {
        List<Map<String, Object>> filas = new ArrayList<>();
        String sql = ano == null
                ? "SELECT DATE_TRUNC('month', v.fecha_venta)::date AS mes, SUM(v.total_venta) AS total_ingresos, SUM(dv.cantidad * p.valor_unitario) AS total_costos, SUM(dv.subtotal) AS total_subtotales, SUM(dv.cantidad) AS total_unidades FROM public.\"ventas\" v JOIN public.\"detalle_ventas\" dv ON v.id_venta = dv.id_venta JOIN public.\"productos\" p ON dv.id_producto = p.id_producto GROUP BY DATE_TRUNC('month', v.fecha_venta) ORDER BY mes"
                : "SELECT DATE_TRUNC('month', v.fecha_venta)::date AS mes, SUM(v.total_venta) AS total_ingresos, SUM(dv.cantidad * p.valor_unitario) AS total_costos, SUM(dv.subtotal) AS total_subtotales, SUM(dv.cantidad) AS total_unidades FROM public.\"ventas\" v JOIN public.\"detalle_ventas\" dv ON v.id_venta = dv.id_venta JOIN public.\"productos\" p ON dv.id_producto = p.id_producto WHERE EXTRACT(YEAR FROM v.fecha_venta) = ? GROUP BY DATE_TRUNC('month', v.fecha_venta) ORDER BY mes";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            if (ano != null) {
                sentencia.setInt(1, ano);
            }
            ResultSet resultado = sentencia.executeQuery();
            while (resultado.next()) {
                Map<String, Object> fila = new HashMap<>();
                fila.put("mes", resultado.getString("mes"));
                fila.put("total_ingresos", resultado.getDouble("total_ingresos"));
                fila.put("total_costos", resultado.getDouble("total_costos"));
                fila.put("total_subtotales", resultado.getDouble("total_subtotales"));
                fila.put("total_unidades", resultado.getInt("total_unidades"));
                filas.add(fila);
            }
        } catch (SQLException error) {
            System.err.println("Error en contabilidad: " + error.getMessage());
        }
        return filas;
    }

    @Override
    public List<String> listarCategorias() {
        List<String> categorias = new ArrayList<>();
        String sql = "SELECT DISTINCT categoria FROM public.\"productos\" ORDER BY categoria";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            ResultSet resultado = sentencia.executeQuery();
            while (resultado.next()) {
                categorias.add(resultado.getString("categoria"));
            }
        } catch (SQLException error) {
            System.err.println("Error al listar categorías: " + error.getMessage());
        }
        return categorias;
    }
}

