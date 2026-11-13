package com.empresa.pruebas.modelo;

import java.time.LocalDateTime;
import java.util.UUID;


public class Pedido {

    private final String id;
    private final double total;
    private final LocalDateTime confirmadoEn;

    public Pedido(String id, double total, LocalDateTime confirmadoEn) {
        this.id = id;
        this.total = total;
        this.confirmadoEn = confirmadoEn;
    }

    public String getId() {
        return id;
    }

    public double getTotal() {
        return total;
    }

    public LocalDateTime getConfirmadoEn() {
        return confirmadoEn;
    }

    public static Pedido de(Carrito carrito) {
        return new Pedido(UUID.randomUUID().toString(), carrito.total(), LocalDateTime.now());
    }
}
