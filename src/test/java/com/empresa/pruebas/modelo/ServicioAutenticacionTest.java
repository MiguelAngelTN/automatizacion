package com.empresa.pruebas.modelo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;


@Tag("unit")
@DisplayName("Servicio de autenticacion - Pruebas unitarias")
class ServicioAutenticacionTest {

    private ServicioAutenticacion servicio;

    @BeforeEach
    void prepararFixture() {
        servicio = new ServicioAutenticacion();
        servicio.registrar(new Usuario("mgomez", "Secret123", true));
    }

    @Test
    @DisplayName("Un usuario activo con credenciales validas obtiene un token")
    void usuarioActivoObtieneToken() {
        Token token = servicio.autenticar("mgomez", "Secret123");

        assertThat(token).isNotNull();
        assertThat(token.getValor()).isNotBlank();
        assertThat(token.estaVigente()).isTrue();
    }

    @Test
    @DisplayName("Una contrasena incorrecta produce un error de credenciales")
    void contrasenaIncorrectaProduceError() {
        assertThatThrownBy(() -> servicio.autenticar("mgomez", "Incorrecta"))
                .isInstanceOf(ExcepcionAutenticacion.class)
                .hasMessageContaining("Credenciales invalidas");
    }

    @Test
    @DisplayName("Un usuario inexistente produce un error de credenciales")
    void usuarioInexistenteProduceError() {
        assertThatThrownBy(() -> servicio.autenticar("desconocido", "Secret123"))
                .isInstanceOf(ExcepcionAutenticacion.class)
                .hasMessageContaining("Credenciales invalidas");
    }

    @Test
    @DisplayName("Un usuario inactivo no puede autenticarse")
    void usuarioInactivoNoPuedeAutenticarse() {
        servicio.registrar(new Usuario("mnunez", "Secret123", false));

        assertThatThrownBy(() -> servicio.autenticar("mnunez", "Secret123"))
                .isInstanceOf(ExcepcionAutenticacion.class)
                .hasMessageContaining("inactivo");
    }

    @Test
    @DisplayName("Registrar dos veces el mismo usuario es rechazado")
    void registrarUsuarioDuplicadoEsRechazado() {
        assertThatThrownBy(() -> servicio.registrar(new Usuario("mgomez", "Otra123", true)))
                .isInstanceOf(ExcepcionAutenticacion.class)
                .hasMessageContaining("ya se encuentra registrado");
    }

    @Test
    @DisplayName("El token emitido tiene una vigencia de 30 minutos")
    void tokenTieneVigenciaDe30Minutos() {
        Token token = servicio.autenticar("mgomez", "Secret123");

        assertThat(Token.VIGENCIA_MINUTOS).isEqualTo(30);
        assertThat(token.getExpiraEn()).isAfter(token.getEmitidoEn());
    }

    @Test
    @DisplayName("El token expone su valor, su emision y su expiracion")
    void elTokenExponeSusDatos() {
        LocalDateTime emision = LocalDateTime.now();

        Token token = new Token("abc-123", emision);

        assertThat(token.getValor()).isEqualTo("abc-123");
        assertThat(token.getEmitidoEn()).isEqualTo(emision);
        assertThat(token.getExpiraEn()).isEqualTo(emision.plusMinutes(30));
    }

    @Test
    @DisplayName("Dos tokens con el mismo valor se consideran iguales")
    void dosTokensConElMismoValorSonIguales() {
        Token tokenA = new Token("abc-123", LocalDateTime.now());
        Token tokenB = new Token("abc-123", LocalDateTime.now());

        assertThat(tokenA).isEqualTo(tokenB);
        assertThat(tokenA).hasSameHashCodeAs(tokenB);
        assertThat(tokenA).isNotEqualTo(new Token("otro-token", LocalDateTime.now()));
    }

    @Test
    @DisplayName("El servicio permite consultar cuantos usuarios estan registrados")
    void elServicioPermiteConsultarLaCantidadDeUsuarios() {
        servicio.registrar(new Usuario("mnunez", "Secret123", true));

        assertThat(servicio.cantidadUsuarios()).isEqualTo(2);
    }
}
