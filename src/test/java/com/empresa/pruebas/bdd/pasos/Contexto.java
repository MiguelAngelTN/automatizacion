package com.empresa.pruebas.bdd.pasos;

import com.empresa.pruebas.modelo.Carrito;
import com.empresa.pruebas.modelo.Pedido;
import com.empresa.pruebas.modelo.ServicioAutenticacion;
import com.empresa.pruebas.modelo.ServicioPedidos;
import com.empresa.pruebas.modelo.Token;
import com.empresa.pruebas.modelo.Usuario;


public class Contexto {

    private ServicioAutenticacion servicioAutenticacion = new ServicioAutenticacion();
    private final ServicioPedidos servicioPedidos = new ServicioPedidos();

    private Carrito carrito = new Carrito();
    private Token tokenEmitido;
    private String mensajeError;
    private Pedido pedido;

    public ServicioAutenticacion getServicioAutenticacion() {
        return servicioAutenticacion;
    }

    public ServicioPedidos getServicioPedidos() {
        return servicioPedidos;
    }

    /**
     * Reemplaza el servicio de autenticacion por uno nuevo que contenga unicamente el
     * usuario indicado.
     *
     * <p>Se usa en el setup de los escenarios para que la preparacion sea
     * <b>idempotente</b>: si el usuario ya existia (por ejemplo, porque lo creo un
     * {@code Antecedentes}), se reinicia el estado en lugar de fallar. La regla de
     * negocio "no se puede registrar dos veces el mismo usuario" se mantiene intacta en
     * {@link ServicioAutenticacion} y se verifica en las pruebas unitarias.</p>
     */
    public void reiniciarAutenticacion(String usuario, String contrasena, boolean activo) {
        ServicioAutenticacion servicioNuevo = new ServicioAutenticacion();
        servicioNuevo.registrar(new Usuario(usuario, contrasena, activo));
        this.servicioAutenticacion = servicioNuevo;
    }

    public Carrito getCarrito() {
        return carrito;
    }

    public void setCarrito(Carrito carrito) {
        this.carrito = carrito;
    }

    public Token getTokenEmitido() {
        return tokenEmitido;
    }

    public void setTokenEmitido(Token tokenEmitido) {
        this.tokenEmitido = tokenEmitido;
    }

    public String getMensajeError() {
        return mensajeError;
    }

    public void setMensajeError(String mensajeError) {
        this.mensajeError = mensajeError;
    }

    public Pedido getPedido() {
        return pedido;
    }

    public void setPedido(Pedido pedido) {
        this.pedido = pedido;
    }
}
