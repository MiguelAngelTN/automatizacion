package com.empresa.pruebas.modelo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Pruebas unitarias atomicas sobre {@link Carrito} y {@link ServicioPedidos}.
 */
@Tag("unit")
@DisplayName("Carrito y pedidos - Pruebas unitarias")
class CarritoTest {

    private Carrito carrito;
    private ServicioPedidos servicioPedidos;

    @BeforeEach
    void prepararFixture() {
        carrito = new Carrito();
        servicioPedidos = new ServicioPedidos();
    }

    @Test
    @DisplayName("Un carrito recien creado esta vacio y su total es cero")
    void carritoNuevoEstaVacio() {
        assertThat(carrito.cantidadItems()).isZero();
        assertThat(carrito.total()).isZero();
    }

    @Test
    @DisplayName("Agregar un producto incrementa los items y el total")
    void agregarProductoIncrementaItemsYTototal() {
        carrito.agregar(new Producto("LAP-001", "Notebook", 129990.0d));

        assertThat(carrito.cantidadItems()).isEqualTo(1);
        assertThat(carrito.total()).isEqualTo(129990.0d);
    }

    @Test
    @DisplayName("El subtotal suma los precios de todos los productos")
    void subtotalSumaTodosLosProductos() {
        carrito.agregar(new Producto("LAP-001", "Notebook", 129990.0d));
        carrito.agregar(new Producto("MOU-002", "Mouse", 45990.0d));

        assertThat(carrito.subtotal()).isEqualTo(175980.0d);
    }

    @Test
    @DisplayName("El codigo BIENVENIDA10 aplica un 10% de descuento")
    void codigoBienvenida10AplicaDescuento() {
        carrito.agregar(new Producto("X-1", "Producto", 100000.0d));
        carrito.aplicarCodigoDescuento("BIENVENIDA10");

        assertThat(carrito.total()).isEqualTo(90000.0d);
    }

    @Test
    @DisplayName("El codigo VERANO20 aplica un 20% de descuento")
    void codigoVerano20AplicaDescuento() {
        carrito.agregar(new Producto("X-1", "Producto", 100000.0d));
        carrito.aplicarCodigoDescuento("VERANO20");

        assertThat(carrito.total()).isEqualTo(80000.0d);
    }

    @Test
    @DisplayName("Un codigo de descuento desconocido es rechazado")
    void codigoDesconocidoEsRechazado() {
        assertThatThrownBy(() -> carrito.aplicarCodigoDescuento("INVENTADO"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Codigo de descuento desconocido");
    }

    @Test
    @DisplayName("Confirmar un pedido devuelve un pedido con el total del carrito")
    void confirmarPedidoDevuelvePedidoConElTotal() {
        carrito.agregar(new Producto("LAP-001", "Notebook", 129990.0d));

        Pedido pedido = servicioPedidos.confirmarPedido(carrito);

        assertThat(pedido.getId()).isNotBlank();
        assertThat(pedido.getTotal()).isEqualTo(129990.0d);
        assertThat(pedido.getConfirmadoEn()).isNotNull();
    }

    @Test
    @DisplayName("Los productos se identifican por su SKU")
    void losProductosSeIdentificanPorSuSku() {
        Producto notebook = new Producto("LAP-001", "Notebook", 129990.0d);
        Producto mismoSku = new Producto("LAP-001", "Otro nombre", 999.0d);

        assertThat(notebook).isEqualTo(mismoSku);
        assertThat(notebook).hasSameHashCodeAs(mismoSku);
        assertThat(notebook.getNombre()).isEqualTo("Notebook");
        assertThat(notebook.getPrecio()).isEqualTo(129990.0d);
    }

    @Test
    @DisplayName("La lista de productos del carrito es de solo lectura")
    void laListaDeProductosEsDeSoloLectura() {
        carrito.agregar(new Producto("X-1", "Producto", 1000.0d));

        assertThat(carrito.getProductos()).hasSize(1);
        assertThatThrownBy(() -> carrito.getProductos().add(new Producto("Y-2", "Otro", 10.0d)))
                .isInstanceOf(UnsupportedOperationException.class);
    }

    @Test
    @DisplayName("Confirmar un pedido con el carrito vacio falla")
    void confirmarPedidoVacioFalla() {
        assertThatThrownBy(() -> servicioPedidos.confirmarPedido(carrito))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("carrito vacio");
    }
}
