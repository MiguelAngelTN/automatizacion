package com.empresa.pruebas.modelo;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Carrito de compras.
 *
 * <p>Modela la funcionalidad de compra cubierta por {@code compra.feature}.</p>
 */
public class Carrito {

    /** Codigos de descuento soportados y su porcentaje aplicado. */
    private static final Map<String, Integer> CODIGOS_DESCUENTO = new LinkedHashMap<>();

    static {
        CODIGOS_DESCUENTO.put("NINGUNO", 0);
        CODIGOS_DESCUENTO.put("BIENVENIDA10", 10);
        CODIGOS_DESCUENTO.put("VERANO20", 20);
    }

    private final List<Producto> productos = new ArrayList<>();
    private int porcentajeDescuento;

    /**
     * Agrega un producto al carrito.
     *
     * @param producto producto a agregar
     */
    public void agregar(Producto producto) {
        productos.add(producto);
    }

    /**
     * Aplica un codigo de descuento conocido.
     *
     * @param codigo codigo de descuento
     * @throws IllegalArgumentException si el codigo no existe
     */
    public void aplicarCodigoDescuento(String codigo) {
        Integer porcentaje = CODIGOS_DESCUENTO.get(codigo);
        if (porcentaje == null) {
            throw new IllegalArgumentException("Codigo de descuento desconocido: " + codigo);
        }
        this.porcentajeDescuento = porcentaje;
    }

    /**
     * @return la suma de los precios de los productos, antes de descuentos
     */
    public double subtotal() {
        double total = 0.0d;
        for (Producto producto : productos) {
            total += producto.getPrecio();
        }
        return redondear(total);
    }

    /**
     * @return el total del carrito con el descuento aplicado
     */
    public double total() {
        double subtotal = subtotal();
        double descuento = subtotal * (porcentajeDescuento / 100.0d);
        return redondear(subtotal - descuento);
    }

    /**
     * @return la cantidad de items distintos agregados al carrito
     */
    public int cantidadItems() {
        return productos.size();
    }

    /**
     * @return los productos del carrito (vista de solo lectura)
     */
    public List<Producto> getProductos() {
        return Collections.unmodifiableList(productos);
    }

    /** Redondea a 2 decimales evitando errores de punto flotante (p. ej. 0.1 + 0.2). */
    private double redondear(double valor) {
        return Math.round(valor * 100.0d) / 100.0d;
    }
}
