package com.empresa.pruebas.modelo;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Pruebas unitarias atomicas sobre {@link Calculadora}.
 *
 * <p>Cada test verifica <b>una sola regla de negocio</b> y no depende del orden ni del
 * estado dejado por otros tests (atomicidad e independencia). Por eso, cada test
 * crea su propia instancia de {@link Calculadora} en lugar de compartirla como campo.</p>
 */
@Tag("unit")
@DisplayName("Calculadora - Pruebas unitarias")
class CalculadoraTest {

    @Test
    @DisplayName("La suma de dos valores devuelve el resultado correcto")
    void sumaDevuelveElResultadoCorrecto() {
        // Arrange
        Calculadora calculadora = new Calculadora();

        // Act
        double resultado = calculadora.suma(7.0d, 5.0d);

        // Assert
        assertThat(resultado).isEqualTo(12.0d);
    }

    @Test
    @DisplayName("La suma con valores negativos opera correctamente")
    void sumaConValoresNegativos() {
        Calculadora calculadora = new Calculadora();

        double resultado = calculadora.suma(-4.0d, -6.0d);

        assertThat(resultado).isEqualTo(-10.0d);
    }

    @Test
    @DisplayName("La resta de dos valores devuelve el resultado correcto")
    void restaDevuelveElResultadoCorrecto() {
        Calculadora calculadora = new Calculadora();

        double resultado = calculadora.resta(10.0d, 4.0d);

        assertThat(resultado).isEqualTo(6.0d);
    }

    @Test
    @DisplayName("La resta donde el minuendo es menor produce un resultado negativo")
    void restaProduceResultadoNegativo() {
        Calculadora calculadora = new Calculadora();

        double resultado = calculadora.resta(3.0d, 8.0d);

        assertThat(resultado).isEqualTo(-5.0d);
    }

    @Test
    @DisplayName("La multiplicacion de dos valores devuelve el producto")
    void multiplicacionDevuelveElProducto() {
        Calculadora calculadora = new Calculadora();

        double resultado = calculadora.multiplicacion(6.0d, 7.0d);

        assertThat(resultado).isEqualTo(42.0d);
    }

    @Test
    @DisplayName("La division entre dos valores devuelve el cociente")
    void divisionDevuelveElCociente() {
        Calculadora calculadora = new Calculadora();

        double resultado = calculadora.division(10.0d, 4.0d);

        assertThat(resultado).isEqualTo(2.5d);
    }

    @Test
    @DisplayName("La division entre cero lanza IllegalArgumentException")
    void divisionPorCeroLanzaExcepcion() {
        Calculadora calculadora = new Calculadora();

        assertThatThrownBy(() -> calculadora.division(10.0d, 0.0d))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("No se puede dividir por cero");
    }

    @Test
    @DisplayName("esPar identifica correctamente los numeros pares e impares")
    void esParIdentificaParesEImpares() {
        Calculadora calculadora = new Calculadora();

        assertThat(calculadora.esPar(4)).isTrue();
        assertThat(calculadora.esPar(7)).isFalse();
    }
}
