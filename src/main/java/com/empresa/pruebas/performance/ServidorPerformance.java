package com.empresa.pruebas.performance;

import com.empresa.pruebas.modelo.Calculadora;
import com.empresa.pruebas.modelo.Carrito;
import com.empresa.pruebas.modelo.Producto;
import com.empresa.pruebas.modelo.ServicioAutenticacion;
import com.empresa.pruebas.modelo.Usuario;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.concurrent.Executors;

/**
 * Servidor HTTP minimalista usado como <i>sistema bajo prueba</i> para la prueba de
 * performance con Apache JMeter.
 *
 * <p>Se apoya en el servidor HTTP incluido en el JDK ({@code com.sun.net.httpserver}) para
 * no sumar dependencias externas al proyecto y así mantener el pipeline liviano.</p>
 *
 * <p>Endpoints expuestos:</p>
 * <ul>
 *   <li>{@code GET  /api/salud}          -&gt; verificacion de vida del servicio</li>
 *   <li>{@code GET  /api/suma?a=&amp;b=}   -&gt; calculo de una operacion</li>
 *   <li>{@code POST /api/login}          -&gt; autenticacion de usuario</li>
 *   <li>{@code POST /api/pedidos}        -&gt; confirmacion de un pedido</li>
 * </ul>
 */
public final class ServidorPerformance {

    private static final Calculadora CALCULADORA = new Calculadora();
    private static final ServicioAutenticacion AUTENTICACION = new ServicioAutenticacion();
    private static final int PUERTO_POR_DEFECTO = 8080;

    static {
        AUTENTICACION.registrar(new Usuario("mgomez", "Secret123", true));
        AUTENTICACION.registrar(new Usuario("mnunez", "Secret123", false));
        AUTENTICACION.registrar(new Usuario("atoledo", "Secret123", true));
    }

    private ServidorPerformance() {
    }

    public static void main(String[] args) throws IOException {
        int puerto = args.length > 0 ? Integer.parseInt(args[0]) : PUERTO_POR_DEFECTO;
        HttpServer servidor = HttpServer.create(new InetSocketAddress("127.0.0.1", puerto), 0);

        servidor.createContext("/api/salud", exchange -> responder(exchange, 200,
                "{\"estado\":\"UP\",\"servicio\":\"automatica-pruebas\"}"));

        servidor.createContext("/api/suma", exchange -> {
            var query = exchange.getRequestURI().getRawQuery();
            double a = parametro(query, "a", 0.0d);
            double b = parametro(query, "b", 0.0d);
            responder(exchange, 200, "{\"resultado\":" + CALCULADORA.suma(a, b) + "}");
        });

        servidor.createContext("/api/login", exchange -> {
            String cuerpo = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            String usuario = extraer(cuerpo, "usuario");
            String contrasena = extraer(cuerpo, "contrasena");
            try {
                var token = AUTENTICACION.autenticar(usuario, contrasena);
                responder(exchange, 200, "{\"token\":\"" + token.getValor() + "\",\"vigenciaMinutos\":30}");
            } catch (RuntimeException excepcion) {
                responder(exchange, 401, "{\"error\":\"" + excepcion.getMessage() + "\"}");
            }
        });

        servidor.createContext("/api/pedidos", exchange -> {
            String cuerpo = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            Carrito carrito = new Carrito();
            carrito.agregar(new Producto("LAP-001", "Notebook", 129990.0d));
            carrito.agregar(new Producto("MOU-002", "Mouse", 45990.0d));
            String codigo = extraer(cuerpo, "codigo");
            if (codigo != null && !codigo.isBlank() && !"NINGUNO".equalsIgnoreCase(codigo)) {
                carrito.aplicarCodigoDescuento(codigo.toUpperCase());
            }
            responder(exchange, 200, "{\"id\":\"PED-001\",\"total\":" + carrito.total()
                    + ",\"items\":" + carrito.cantidadItems() + "}");
        });

        servidor.setExecutor(Executors.newFixedThreadPool(16));
        servidor.start();
        System.out.println("[ServidorPerformance] Escuchando en http://127.0.0.1:" + puerto);
        System.out.println("[ServidorPerformance] Listo: " + LocalDateTime.now());
    }

    private static void responder(HttpExchange exchange, int codigo, String json) throws IOException {
        byte[] cuerpo = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(codigo, cuerpo.length);
        try (OutputStream salida = exchange.getResponseBody()) {
            salida.write(cuerpo);
        }
    }

    private static double parametro(String query, String nombre, double porDefecto) {
        if (query == null) {
            return porDefecto;
        }
        for (String par : query.split("&")) {
            String[] partes = par.split("=", 2);
            if (partes.length == 2 && partes[0].equals(nombre)) {
                try {
                    return Double.parseDouble(partes[1]);
                } catch (NumberFormatException excepcion) {
                    return porDefecto;
                }
            }
        }
        return porDefecto;
    }

    /** Extraccion minima de un campo JSON plano (sin dependencias externas). */
    private static String extraer(String json, String campo) {
        String llave = "\"" + campo + "\"";
        int inicio = json.indexOf(llave);
        if (inicio < 0) {
            return null;
        }
        int inicioValor = json.indexOf(':', inicio + llave.length());
        if (inicioValor < 0) {
            return null;
        }
        int comillaInicio = json.indexOf('"', inicioValor);
        if (comillaInicio < 0) {
            return null;
        }
        int comillaFin = json.indexOf('"', comillaInicio + 1);
        if (comillaFin < 0) {
            return null;
        }
        return json.substring(comillaInicio + 1, comillaFin);
    }
}
