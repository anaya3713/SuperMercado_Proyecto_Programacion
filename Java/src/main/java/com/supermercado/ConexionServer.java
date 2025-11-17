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

public class ConexionServer {
    private static final int PORT = 5000;
    private static ConexionDB db;
    private static final Gson gson = new Gson();

    public static void main(String[] args) {
        db = new ConexionDB();
        System.out.println("Iniciando servidor en puerto " + PORT + "...");

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Servidor esperando conexiones...");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                new Thread(new ClientHandler(clientSocket)).start();
            }
        } catch (IOException e) {
            System.err.println("Error en el servidor: " + e.getMessage());
        } finally {
            db.close();
        }
    }

    public static Gson getGson() {
        return gson;
    }

    static class ClientHandler implements Runnable {
        private final Socket socket;

        ClientHandler(Socket socket) {
            this.socket = socket;
        }

        @Override
        public void run() {
            try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                 PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

                String request;
                while ((request = in.readLine()) != null) {
                    String response = procesarComando(request);
                    out.println(response);
                }
            } catch (IOException e) {
                System.err.println("Error con cliente: " + e.getMessage());
            } finally {
                try {
                    socket.close();
                } catch (IOException e) {
                    System.err.println("Error cerrando socket: " + e.getMessage());
                }
            }
        }

        private String procesarComando(String comando) {
            try {
                JsonObject json = gson.fromJson(comando, JsonObject.class);
                String accion = json.get("accion").getAsString();

                return switch (accion) {
                    case "CREAR_PRODUCTO" -> crearProducto(json);
                    case "BUSQUEDA_CATEGORIA" -> busquedaCategoria(json);
                    case "BUSQUEDA_PRODUCTO" -> busquedaProducto(json);
                    case "GENERAR_FACTURA" -> generarFactura(json);
                    case "ACTUALIZAR_STOCK" -> actualizarStock(json);
                    case "ELIMINAR_PRODUCTO" -> eliminarProducto(json);
                    case "LISTAR_PRODUCTOS" -> listarProductos();
                    case "LISTAR_CATEGORIAS" -> listarCategorias();
                    case "CONTABILIDAD" -> contabilidad(json);
                    default -> gson.toJson(new RespuestaError("Acción desconocida: " + accion));
                };
            } catch (JsonSyntaxException e) {
                return gson.toJson(new RespuestaError("Error procesando comando: " + e.getMessage()));
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

            Integer id = db.crearProductoInventario(nombre, descripcion, categoria, marca, valor, precio, stock, codigo);
            if (id != null) {
                JsonObject resp = new JsonObject();
                resp.addProperty("id_producto", id);
                return resp.toString();
            }
            return gson.toJson(new RespuestaError("No se pudo crear el producto"));
        }

        private String busquedaCategoria(JsonObject json) {
            String categoria = json.get("categoria").getAsString();
            List<Map<String, Object>> resultados = db.busquedaCategoria(categoria);
            return gson.toJson(resultados);
        }

        private String busquedaProducto(JsonObject json) {
            String codigo = json.get("codigo_barras").getAsString();
            Map<String, Object> resultado = db.busquedaProducto(codigo);
            if (resultado != null) {
                return gson.toJson(resultado);
            }
            return gson.toJson(new RespuestaError("Producto no encontrado"));
        }

        private String generarFactura(JsonObject json) {
            String metodo = json.get("metodo_pago").getAsString();
            String cliente = json.get("nombre_cliente").getAsString();
            String cedula = json.get("cedula_cliente").getAsString();

            JsonArray itemsArray = json.getAsJsonArray("items");
            List<Map<String, Object>> items = gson.fromJson(itemsArray, 
                new TypeToken<List<Map<String, Object>>>() {}.getType());

            Object resultado = db.generarFactura(metodo, cliente, cedula, items);
            if (resultado != null) {
                return gson.toJson(resultado);
            }
            return gson.toJson(new RespuestaError("No se pudo generar factura"));
        }

        private String actualizarStock(JsonObject json) {
            int id = json.get("id_producto").getAsInt();
            int stock = json.get("nuevo_stock").getAsInt();
            if (db.actualizarStock(id, stock)) {
                return gson.toJson(new RespuestaExito("Stock actualizado"));
            }
            return gson.toJson(new RespuestaError("No se pudo actualizar stock"));
        }

        private String eliminarProducto(JsonObject json) {
            int id = json.get("id_producto").getAsInt();
            if (db.eliminarProducto(id)) {
                return gson.toJson(new RespuestaExito("Producto eliminado"));
            }
            return gson.toJson(new RespuestaError("No se pudo eliminar producto"));
        }

        private String listarProductos() {
            List<Map<String, Object>> productos = db.listarProductos();
            return gson.toJson(productos);
        }

        private String contabilidad(JsonObject json) {
            Integer ano = json.has("ano") && !json.get("ano").isJsonNull() 
                ? json.get("ano").getAsInt() : null;
            List<Map<String, Object>> datos = db.contabilidad(ano);
            return gson.toJson(datos);
        }

        private String listarCategorias() {
            List<String> categorias = db.listarCategorias();
            return gson.toJson(categorias);
        }
    }

    static class RespuestaError {
        public String error;

        RespuestaError(String error) {
            this.error = error;
        }
    }

    static class RespuestaExito {
        public String mensaje;

        RespuestaExito(String mensaje) {
            this.mensaje = mensaje;
        }
    }
}
