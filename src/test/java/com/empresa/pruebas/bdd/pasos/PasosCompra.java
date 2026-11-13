package com.empresa.pruebas.bdd.pasos;

import com.empresa.pruebas.modelo.Carrito;
import com.empresa.pruebas.modelo.Producto;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Definiciones de pasos (step definitions) del feature {@code compra.feature}.
 *
 * <p>Cada paso verifica una sola regla de negocio y se apoya en el {@link Contexto}
 * compartido del escenario (inyectado con PicoContainer).</p>
 */
public class PasosCompra {

    private final Contexto contexto;

    public PasosCompra(Contexto contexto) {
        this.contexto = contexto;
    }

    @Before
    public void prepararEscenario() {
        contexto.setCarrito(new Carrito());
        contexto.setPedido(null);
    }

    @Given("que el carrito está vacío")
    public void elCarritoEstaVacio() {
        contexto.setCarrito(new Carrito());
    }

    @When("agrego el producto {string} con precio {float} al carrito")
    public void agregoProducto(String sku, double precio) {
        contexto.getCarrito().agregar(new Producto(sku, "Producto " + sku, precio));
    }

    @When("aplico el código de descuento {string}")
    public void aplicoCodigoDeDescuento(String codigo) {
        contexto.getCarrito().aplicarCodigoDescuento(codigo);
    }

    @When("confirmo el pedido")
    public void confirmoElPedido() {
        contexto.setPedido(contexto.getServicioPedidos().confirmarPedido(contexto.getCarrito()));
    }

    @Then("el total del carrito es {float}")
    public void elTotalDelCarritoEs(double total) {
        assertThat(contexto.getCarrito().total()).isEqualTo(total);
    }

    @Then("el carrito tiene {int} items")
    public void elCarritoTieneItems(int items) {
        assertThat(contexto.getCarrito().cantidadItems()).isEqualTo(items);
    }

    @Then("el pedido se confirma con un total de {float}")
    public void elPedidoSeConfirmaConUnTotalDe(double total) {
        assertThat(contexto.getPedido()).as("El pedido debía confirmarse").isNotNull();
        assertThat(contexto.getPedido().getTotal()).isEqualTo(total);
    }

    @Then("el pedido tiene un identificador asignado")
    public void elPedidoTieneIdentificador() {
        assertThat(contexto.getPedido()).isNotNull();
        assertThat(contexto.getPedido().getId()).isNotBlank();
    }
}
