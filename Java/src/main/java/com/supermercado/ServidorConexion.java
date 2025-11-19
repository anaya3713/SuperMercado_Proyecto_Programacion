package com.supermercado;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;

public class ServidorConexion {
    private static final int PUERTO = 5000;
    //Polimorfismo
    private static OperacionesBaseDatos baseDatos;
    private static final Gson GSON = new Gson();

    public static void main(String[] argumentos) {
        baseDatos = new ConexionBaseDatos();
        System.out.println("Servidor escuchando en el puerto " + PUERTO);
        try (ServerSocket servidor = new ServerSocket(PUERTO)) {
            while (true) {
                Socket cliente = servidor.accept();
                new Thread(new ManejadorCliente(cliente)).start();
            }
        } catch (IOException error) {
            System.err.println("Error en el servidor: " + error.getMessage());
        } finally {
            baseDatos.close();
        }
    }

    private static String serializarRespuesta(RespuestaBase respuesta) {
        JsonObject json = new JsonObject();
        json.addProperty("tipo", respuesta.obtenerTipo());
        json.addProperty("mensaje", respuesta.obtenerMensaje());
        return json.toString();
    }

    static class ManejadorCliente implements Runnable {
        private final Socket socket;

        ManejadorCliente(Socket socket) {
            this.socket = socket;
        }

        @Override
        public void run() {
            try (BufferedReader entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                 PrintWriter salida = new PrintWriter(socket.getOutputStream(), true)) {
                String solicitud;
                while ((solicitud = entrada.readLine()) != null) {
                    salida.println(procesarComando(solicitud));
                }
            } catch (IOException error) {
                System.err.println("Error con el cliente: " + error.getMessage());
            } finally {
                try {
                    socket.close();
                } catch (IOException cierre) {
                    System.err.println("Error al cerrar socket: " + cierre.getMessage());
                }
            }
        }

        private String procesarComando(String comando) {
            try {
                JsonObject json = GSON.fromJson(comando, JsonObject.class);
                String accion = json.get("accion").getAsString();
                return switch (accion) {
                    case "CREAR_PRODUCTO" -> crearProducto(json);
                    case "BUSQUEDA_CATEGORIA" -> buscarCategoria(json);
                    case "BUSQUEDA_PRODUCTO" -> buscarProducto(json);
                    case "GENERAR_FACTURA" -> generarFactura(json);
                    case "ACTUALIZAR_STOCK" -> actualizarStock(json);
                    case "ELIMINAR_PRODUCTO" -> eliminarProducto(json);
                    case "LISTAR_PRODUCTOS" -> listarProductos();
                    case "LISTAR_CATEGORIAS" -> listarCategorias();
                    case "CONTABILIDAD" -> contabilidad(json);
                    default -> serializarRespuesta(new RespuestaError("Acción desconocida: " + accion));
                };
            } catch (JsonSyntaxException error) {
                return serializarRespuesta(new RespuestaError("Comando inválido: " + error.getMessage()));
            }
        }

        private String crearProducto(JsonObject json) {
            String nombre = json.get("nombre_producto").getAsString();
            String descripcion = json.get("descripcion").getAsString();
            String categoria = json.get("categoria").getAsString();
            String marca = json.get("marca").getAsString();
            double valor = json.get("valor_unitario").getAsDouble();
            double precio = json.get("precio_venta").getAsDouble();
            int stock = json.get("stock_actual").getAsInt();
            String codigo = json.has("codigo_barras") && !json.get("codigo_barras").isJsonNull()
                    ? json.get("codigo_barras").getAsString() : null;
            Integer id = baseDatos.crearProductoInventario(nombre, descripcion, categoria, marca, valor, precio, stock, codigo);
            if (id != null) {
                JsonObject respuesta = new JsonObject();
                respuesta.addProperty("id_producto", id);
                return respuesta.toString();
            }
            return serializarRespuesta(new RespuestaError("No se pudo crear el producto"));
        }

        private String buscarCategoria(JsonObject json) {
            String categoria = json.get("categoria").getAsString();
            List<Map<String, Object>> productos = baseDatos.busquedaCategoria(categoria);
            return GSON.toJson(productos);
        }

        private String buscarProducto(JsonObject json) {
            String codigo = json.get("codigo_barras").getAsString();
            Map<String, Object> producto = baseDatos.busquedaProducto(codigo);
            if (producto == null) {
                return serializarRespuesta(new RespuestaError("Producto no encontrado"));
            }
            return GSON.toJson(producto);
        }

        private String generarFactura(JsonObject json) {
            String metodo = json.get("metodo_pago").getAsString();
            String cliente = json.get("nombre_cliente").getAsString();
            String cedula = json.get("cedula_cliente").getAsString();
            JsonArray arreglo = json.getAsJsonArray("items");
            List<Map<String, Object>> items = GSON.fromJson(arreglo, new TypeToken<List<Map<String, Object>>>() {}.getType());
            Object resultado = baseDatos.generarFactura(metodo, cliente, cedula, items);
            if (resultado == null) {
                return serializarRespuesta(new RespuestaError("No se pudo generar la factura"));
            }
            return GSON.toJson(resultado);
        }

        private String actualizarStock(JsonObject json) {
            int id = json.get("id_producto").getAsInt();
            if (json.has("incrementar") && json.get("incrementar").getAsBoolean()) {
                int cantidad = json.get("cantidad").getAsInt();
                return baseDatos.actualizarStock(id, cantidad, true)
                        ? serializarRespuesta(new RespuestaExito("Stock incrementado"))
                        : serializarRespuesta(new RespuestaError("No se pudo incrementar"));
            }
            if (json.has("nuevo_stock")) {
                int nuevo = json.get("nuevo_stock").getAsInt();
                return baseDatos.actualizarStock(id, nuevo)
                        ? serializarRespuesta(new RespuestaExito("Stock actualizado"))
                        : serializarRespuesta(new RespuestaError("No se pudo actualizar"));
            }
            return serializarRespuesta(new RespuestaError("Parámetros insuficientes"));
        }

        private String eliminarProducto(JsonObject json) {
            int id = json.get("id_producto").getAsInt();
            return baseDatos.eliminarProducto(id)
                    ? serializarRespuesta(new RespuestaExito("Producto eliminado"))
                    : serializarRespuesta(new RespuestaError("No se pudo eliminar"));
        }

        private String listarProductos() {
            return GSON.toJson(baseDatos.listarProductos());
        }

        private String listarCategorias() {
            return GSON.toJson(baseDatos.listarCategorias());
        }

        private String contabilidad(JsonObject json) {
            Integer ano = json.has("ano") && !json.get("ano").isJsonNull()
                    ? json.get("ano").getAsInt() : null;
            return GSON.toJson(baseDatos.contabilidad(ano));
        }
    }

    //Herencia (de RespuestaBase)
    static class RespuestaError extends RespuestaBase {
        private final String mensaje;

        RespuestaError(String mensaje) {
            super("ERROR");
            this.mensaje = mensaje;
        }

        @Override
        public String obtenerMensaje() {
            return mensaje;
        }
    }

    //Herencia (de RespuestaBase)
    static class RespuestaExito extends RespuestaBase {
        private final String mensaje;

        RespuestaExito(String mensaje) {
            super("EXITO");
            this.mensaje = mensaje;
        }

        @Override
        public String obtenerMensaje() {
            return mensaje;
        }
    }
}

