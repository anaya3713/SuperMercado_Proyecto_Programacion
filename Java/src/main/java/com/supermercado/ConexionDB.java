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

public class ConexionDB {
    private Connection conn;
    private static final String URL = "jdbc:postgresql://localhost:5432/bd_productos_supermercado";
    private static final String USER = "supermercado";
    private static final String PASSWORD = "Super123";

    public ConexionDB() {
        try {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(URL, USER, PASSWORD);
            System.out.println("[DB] Conectado exitosamente a: " + URL);
        } catch (ClassNotFoundException | SQLException e) {
            System.err.println("[DB] Error al conectar a la BD: " + e.getMessage());
        }
    }

    public Connection getConnection() {
        return conn;
    }

    public void close() {
        try {
            if (conn != null && !conn.isClosed()) {
                conn.close();
            }
        } catch (SQLException e) {
            System.err.println("Error al cerrar conexión: " + e.getMessage());
        }
    }

    public Integer crearProductoInventario(String nombreProducto, String descripcion, String categoria,
                                           String marca, double valorUnitario, double precioVenta,
                                           int stockActual, String codigoBarras) {
        String sql = "INSERT INTO public.\"productos\" (nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras) VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id_producto";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, nombreProducto);
            pstmt.setString(2, descripcion);
            pstmt.setString(3, categoria);
            pstmt.setString(4, marca);
            pstmt.setDouble(5, valorUnitario);
            pstmt.setDouble(6, precioVenta);
            pstmt.setInt(7, stockActual);
            pstmt.setString(8, codigoBarras);

            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                return rs.getInt("id_producto");
            }
        } catch (SQLException e) {
            System.err.println("Error al insertar producto: " + e.getMessage());
        }
        return null;
    }

    public List<Map<String, Object>> busquedaCategoria(String categoria) {
        List<Map<String, Object>> resultados = new ArrayList<>();
        String sql = "SELECT * FROM public.\"productos\" WHERE categoria = ? ORDER BY nombre_producto";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, categoria);
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("id_producto", rs.getInt("id_producto"));
                row.put("nombre_producto", rs.getString("nombre_producto"));
                row.put("descripcion", rs.getString("descripcion"));
                row.put("categoria", rs.getString("categoria"));
                row.put("marca", rs.getString("marca"));
                row.put("valor_unitario", rs.getDouble("valor_unitario"));
                row.put("precio_venta", rs.getDouble("precio_venta"));
                row.put("stock_actual", rs.getInt("stock_actual"));
                row.put("codigo_barras", rs.getString("codigo_barras"));
                resultados.add(row);
            }
        } catch (SQLException e) {
            System.err.println("Error en busqueda_categoria: " + e.getMessage());
        }
        return resultados;
    }

    public Map<String, Object> busquedaProducto(String codigoBarras) {
        String sql = "SELECT * FROM public.\"productos\" WHERE codigo_barras = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, codigoBarras);
            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("id_producto", rs.getInt("id_producto"));
                row.put("nombre_producto", rs.getString("nombre_producto"));
                row.put("descripcion", rs.getString("descripcion"));
                row.put("categoria", rs.getString("categoria"));
                row.put("marca", rs.getString("marca"));
                row.put("valor_unitario", rs.getDouble("valor_unitario"));
                row.put("precio_venta", rs.getDouble("precio_venta"));
                row.put("stock_actual", rs.getInt("stock_actual"));
                row.put("codigo_barras", rs.getString("codigo_barras"));
                return row;
            }
        } catch (SQLException e) {
            System.err.println("Error en busqueda_producto: " + e.getMessage());
        }
        return null;
    }

    public Object generarFactura(String metodoPago, String nombreCliente, String cedulaCliente, List<Map<String, Object>> items) {
        if (items == null || items.isEmpty()) {
            return null;
        }

        try {
            conn.setAutoCommit(false);

            double totalVenta = 0;
            List<Map<String, Object>> productosAInsertar = new ArrayList<>();

            for (Map<String, Object> item : items) {
                Integer idProducto = null;
                String codigoBarras = null;
                int cantidad = ((Number) item.get("cantidad")).intValue();
                double precioUnitario = ((Number) item.get("precio_unitario")).doubleValue();

                if (item.containsKey("id_producto") && item.get("id_producto") != null) {
                    idProducto = ((Number) item.get("id_producto")).intValue();
                } else if (item.containsKey("codigo_barras") && item.get("codigo_barras") != null) {
                    codigoBarras = (String) item.get("codigo_barras");
                    String sql = "SELECT id_producto FROM public.\"productos\" WHERE codigo_barras = ?";
                    try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                        pstmt.setString(1, codigoBarras);
                        ResultSet rs = pstmt.executeQuery();
                        if (rs.next()) {
                            idProducto = rs.getInt("id_producto");
                        }
                    }
                }

                if (idProducto == null) {
                    conn.rollback();
                    conn.setAutoCommit(true);
                    return null;
                }

                String sql = "SELECT stock_actual, nombre_producto FROM public.\"productos\" WHERE id_producto = ? FOR UPDATE";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    pstmt.setInt(1, idProducto);
                    ResultSet rs = pstmt.executeQuery();
                    if (!rs.next()) {
                        conn.rollback();
                        conn.setAutoCommit(true);
                        return null;
                    }
                    int stockActual = rs.getInt("stock_actual");
                    if (stockActual < cantidad) {
                        conn.rollback();
                        conn.setAutoCommit(true);
                        return null;
                    }
                    
                    // Guardar el nombre del producto para usarlo después
                    String nombreProducto = rs.getString("nombre_producto");
                    
                    double subtotal = Math.round(cantidad * precioUnitario * 100.0) / 100.0;
                    totalVenta += subtotal;

                    Map<String, Object> producto = new HashMap<>();
                    producto.put("id_producto", idProducto);
                    producto.put("nombre_producto", nombreProducto);
                    
                    // Obtener el código de barras real del producto si no vino en el request
                    String codigoFinal = codigoBarras;
                    if (codigoFinal == null || codigoFinal.isEmpty()) {
                        String sqlCod = "SELECT codigo_barras FROM public.\"productos\" WHERE id_producto = ?";
                        try (PreparedStatement pstmtCod = conn.prepareStatement(sqlCod)) {
                            pstmtCod.setInt(1, idProducto);
                            ResultSet rsCod = pstmtCod.executeQuery();
                            if (rsCod.next()) {
                                codigoFinal = rsCod.getString("codigo_barras");
                            }
                        }
                    }
                    
                    producto.put("codigo_barras", codigoFinal == null ? "" : codigoFinal);
                    producto.put("cantidad", cantidad);
                    producto.put("precio_unitario", precioUnitario);
                    producto.put("subtotal", subtotal);
                    productosAInsertar.add(producto);
                }
            }

            String sqlVenta = "INSERT INTO public.\"ventas\" (fecha_venta, hora_venta, total_venta, metodo_pago, nombre_cliente, cedula_cliente) VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, ?, ?) RETURNING id_venta";
            int idVenta = 0;
            try (PreparedStatement pstmt = conn.prepareStatement(sqlVenta)) {
                pstmt.setDouble(1, totalVenta);
                pstmt.setString(2, metodoPago);
                pstmt.setString(3, nombreCliente);
                pstmt.setString(4, cedulaCliente);
                ResultSet rs = pstmt.executeQuery();
                if (rs.next()) {
                    idVenta = rs.getInt("id_venta");
                }
            }

            for (Map<String, Object> p : productosAInsertar) {
                String sqlDetalle = "INSERT INTO public.\"detalle_ventas\" (id_venta, id_producto, codigo_barras, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sqlDetalle)) {
                    pstmt.setInt(1, idVenta);
                    int idProd = ((Number) p.get("id_producto")).intValue();
                    pstmt.setInt(2, idProd);
                    
                    // Obtener el código de barras real del producto si no viene en el payload
                    String codigoDet = (String) p.get("codigo_barras");
                    if (codigoDet == null || codigoDet.isEmpty()) {
                        String sqlCodigo = "SELECT codigo_barras FROM public.\"productos\" WHERE id_producto = ?";
                        try (PreparedStatement pstmtCod = conn.prepareStatement(sqlCodigo)) {
                            pstmtCod.setInt(1, idProd);
                            ResultSet rsCod = pstmtCod.executeQuery();
                            if (rsCod.next()) {
                                codigoDet = rsCod.getString("codigo_barras");
                                if (codigoDet == null) codigoDet = "";
                            } else {
                                codigoDet = "";
                            }
                        }
                    }
                    pstmt.setString(3, codigoDet);
                    pstmt.setInt(4, ((Number) p.get("cantidad")).intValue());
                    pstmt.setDouble(5, ((Number) p.get("precio_unitario")).doubleValue());
                    pstmt.setDouble(6, ((Number) p.get("subtotal")).doubleValue());
                    pstmt.executeUpdate();
                }

                String sqlUpdate = "UPDATE public.\"productos\" SET stock_actual = stock_actual - ? WHERE id_producto = ?";
                try (PreparedStatement pstmt = conn.prepareStatement(sqlUpdate)) {
                    pstmt.setInt(1, ((Number) p.get("cantidad")).intValue());
                    pstmt.setInt(2, ((Number) p.get("id_producto")).intValue());
                    pstmt.executeUpdate();
                }
            }

            conn.commit();
            conn.setAutoCommit(true);

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
            respuesta.put("productos", productosAInsertar);

            return respuesta;

        } catch (SQLException e) {
            try {
                conn.rollback();
                conn.setAutoCommit(true);
            } catch (SQLException ex) {
                System.err.println("Error al hacer rollback: " + ex.getMessage());
            }
            System.err.println("Error al generar factura: " + e.getMessage());
        }
        return null;
    }

    public boolean actualizarStock(int idProducto, int nuevoStock) {
        String sql = "UPDATE public.\"productos\" SET stock_actual = ? WHERE id_producto = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, nuevoStock);
            pstmt.setInt(2, idProducto);
            pstmt.executeUpdate();
            return true;
        } catch (SQLException e) {
            System.err.println("Error al actualizar stock: " + e.getMessage());
        }
        return false;
    }


    public boolean eliminarProducto(int idProducto) {
        // Verificar si el producto tiene ventas registradas
        String sqlCheck = "SELECT COUNT(*) FROM public.\"detalle_ventas\" WHERE id_producto = ?";
        try (PreparedStatement pstmtCheck = conn.prepareStatement(sqlCheck)) {
            pstmtCheck.setInt(1, idProducto);
            ResultSet rs = pstmtCheck.executeQuery();
            if (rs.next() && rs.getInt(1) > 0) {
                System.err.println("No se puede eliminar: el producto tiene ventas registradas");
                return false;
            }
        } catch (SQLException e) {
            System.err.println("Error al verificar ventas del producto: " + e.getMessage());
            return false;
        }
        
        // Si no tiene ventas, proceder a eliminar
        String sql = "DELETE FROM public.\"productos\" WHERE id_producto = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, idProducto);
            pstmt.executeUpdate();
            return true;
        } catch (SQLException e) {
            System.err.println("Error al eliminar producto: " + e.getMessage());
        }
        return false;
    }

    public List<Map<String, Object>> listarProductos() {
        List<Map<String, Object>> resultados = new ArrayList<>();
        String sql = "SELECT * FROM public.\"productos\" ORDER BY nombre_producto";
        try (Statement stmt = conn.createStatement()) {
            ResultSet rs = stmt.executeQuery(sql);
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("id_producto", rs.getInt("id_producto"));
                row.put("nombre_producto", rs.getString("nombre_producto"));
                row.put("descripcion", rs.getString("descripcion"));
                row.put("categoria", rs.getString("categoria"));
                row.put("marca", rs.getString("marca"));
                row.put("valor_unitario", rs.getDouble("valor_unitario"));
                row.put("precio_venta", rs.getDouble("precio_venta"));
                row.put("stock_actual", rs.getInt("stock_actual"));
                row.put("codigo_barras", rs.getString("codigo_barras"));
                resultados.add(row);
            }
        } catch (SQLException e) {
            System.err.println("Error al listar productos: " + e.getMessage());
        }
        return resultados;
    }

    public List<Map<String, Object>> contabilidad(Integer ano) {
        List<Map<String, Object>> resultados = new ArrayList<>();
        String sql;
        if (ano == null) {
            sql = "SELECT DATE_TRUNC('month', v.fecha_venta)::date AS mes, SUM(v.total_venta) AS total_ingresos, SUM(dv.cantidad * p.valor_unitario) AS total_costos, SUM(dv.subtotal) AS total_subtotales, SUM(dv.cantidad) AS total_unidades FROM public.\"ventas\" v JOIN public.\"detalle_ventas\" dv ON v.id_venta = dv.id_venta JOIN public.\"productos\" p ON dv.id_producto = p.id_producto GROUP BY DATE_TRUNC('month', v.fecha_venta) ORDER BY mes";
        } else {
            sql = "SELECT DATE_TRUNC('month', v.fecha_venta)::date AS mes, SUM(v.total_venta) AS total_ingresos, SUM(dv.cantidad * p.valor_unitario) AS total_costos, SUM(dv.subtotal) AS total_subtotales, SUM(dv.cantidad) AS total_unidades FROM public.\"ventas\" v JOIN public.\"detalle_ventas\" dv ON v.id_venta = dv.id_venta JOIN public.\"productos\" p ON dv.id_producto = p.id_producto WHERE EXTRACT(YEAR FROM v.fecha_venta) = ? GROUP BY DATE_TRUNC('month', v.fecha_venta) ORDER BY mes";
        }

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            if (ano != null) {
                pstmt.setInt(1, ano);
            }
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("mes", rs.getString("mes"));
                row.put("total_ingresos", rs.getDouble("total_ingresos"));
                row.put("total_costos", rs.getDouble("total_costos"));
                row.put("total_subtotales", rs.getDouble("total_subtotales"));
                row.put("total_unidades", rs.getInt("total_unidades"));
                resultados.add(row);
            }
        } catch (SQLException e) {
            System.err.println("Error en contabilidad: " + e.getMessage());
        }
        return resultados;
    }

    public List<String> listarCategorias() {
        List<String> categorias = new ArrayList<>();
        String sql = "SELECT DISTINCT categoria FROM public.\"productos\" ORDER BY categoria";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                categorias.add(rs.getString("categoria"));
            }
        } catch (SQLException e) {
            System.err.println("Error al listar categorías: " + e.getMessage());
        }
        return categorias;
    }
}
