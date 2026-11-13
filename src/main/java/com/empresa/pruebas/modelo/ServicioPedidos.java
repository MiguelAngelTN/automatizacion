package com.empresa.pruebas.modelo;

/**
 * Servicio de pedidos: confirma la compra de un carrito.
 */
public class ServicioPedidos {

    /**
     * Confirma el pedido asociado a un carrito.
     *
     * @param carrito carrito con al menos un producto
     * @return el pedido confirmado
     * @throws IllegalStateException si el carrito esta vacio
     */
    public Pedido confirmarPedido(Carrito carrito) {
        if (carrito.cantidadItems() == 0) {
            throw new IllegalStateException("No se puede confirmar un pedido con el carrito vacio");
        }
        return Pedido.de(carrito);
    }
}
