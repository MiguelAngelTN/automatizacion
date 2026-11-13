package com.empresa.pruebas.modelo;

import java.util.Objects;


public class Producto {

    private final String sku;
    private final String nombre;
    private final double precio;

    public Producto(String sku, String nombre, double precio) {
        this.sku = sku;
        this.nombre = nombre;
        this.precio = precio;
    }

    public String getSku() {
        return sku;
    }

    public String getNombre() {
        return nombre;
    }

    public double getPrecio() {
        return precio;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Producto otro)) {
            return false;
        }
        return Objects.equals(sku, otro.sku);
    }

    @Override
    public int hashCode() {
        return Objects.hash(sku);
    }
}
