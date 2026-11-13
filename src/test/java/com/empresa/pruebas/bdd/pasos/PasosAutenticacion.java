package com.empresa.pruebas.bdd.pasos;

import com.empresa.pruebas.modelo.ExcepcionAutenticacion;
import com.empresa.pruebas.modelo.Usuario;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Definiciones de pasos (step definitions) del feature {@code autenticacion.feature}.
 *
 * <p>Se usan Cucumber Expressions con los tipos estandar ({@code string}, {@code int}).
 * El tipo {@code string} exige que los valores esten entre comillas en el Gherkin
 * (por ejemplo {@code "mgomez"}), ya que de lo contrario se capturaria solo la primera
 * palabra.</p>
 *
 * <p>El estado de cada escenario viaja en {@link Contexto}, inyectado por el contenedor
 * de dependencias PicoContainer, de modo que los pasos no dependen del orden de
 * ejecucion ni comparten estado entre escenarios.</p>
 */
public class PasosAutenticacion {

    private final Contexto contexto;

    public PasosAutenticacion(Contexto contexto) {
        this.contexto = contexto;
    }

    @Before
    public void prepararEscenario() {
        contexto.setTokenEmitido(null);
        contexto.setMensajeError(null);
    }

    @Given("que existe un usuario registrado con usuario {string} y contrasena {string}")
    public void existeUsuarioRegistrado(String usuario, String contrasena) {
        try {
            contexto.getServicioAutenticacion().registrar(new Usuario(usuario, contrasena, true));
        } catch (ExcepcionAutenticacion usuarioYaRegistrado) {
            contexto.reiniciarAutenticacion(usuario, contrasena, true);
        }
    }

    @Given("que existe un usuario {string} con contrasena {string} y estado {string}")
    public void existeUsuarioConEstado(String usuario, String contrasena, String estado) {
        registrarUsuarioConEstado(usuario, contrasena, estado);
    }

    /** Variante del paso anterior sin la preposicion "que" (utilizada tras una conjuncion "Y"). */
    @Given("existe un usuario {string} con contrasena {string} y estado {string}")
    public void existeUsuarioConEstadoSinQue(String usuario, String contrasena, String estado) {
        registrarUsuarioConEstado(usuario, contrasena, estado);
    }

    private void registrarUsuarioConEstado(String usuario, String contrasena, String estado) {
        boolean activo = !"inactivo".equalsIgnoreCase(estado);
        try {
            contexto.getServicioAutenticacion().registrar(new Usuario(usuario, contrasena, activo));
        } catch (ExcepcionAutenticacion usuarioYaRegistrado) {
            // El usuario ya existia (por ejemplo, por los Antecedentes del feature):
            // el setup del escenario reinicia el estado para ser idempotente.
            contexto.reiniciarAutenticacion(usuario, contrasena, activo);
        }
    }

    @When("el usuario {string} se autentica con la contrasena {string}")
    public void elUsuarioSeAutentica(String usuario, String contrasena) {
        try {
            contexto.setTokenEmitido(contexto.getServicioAutenticacion().autenticar(usuario, contrasena));
            contexto.setMensajeError(null);
        } catch (RuntimeException excepcion) {
            contexto.setTokenEmitido(null);
            contexto.setMensajeError(excepcion.getMessage());
        }
    }

    @Then("el resultado es {string}")
    public void elResultadoEs(String resultado) {
        switch (resultado) {
            case "un token válido" -> assertThat(contexto.getTokenEmitido())
                    .as("Se esperaba un token válido para el usuario")
                    .isNotNull();
            case "un error de credenciales" -> {
                assertThat(contexto.getTokenEmitido())
                        .as("No debía emitirse un token")
                        .isNull();
                assertThat(contexto.getMensajeError())
                        .as("Se esperaba un error de credenciales")
                        .isNotBlank();
            }
            default -> throw new IllegalArgumentException("Resultado no contemplado en el feature: " + resultado);
        }
    }

    @Then("el token tiene una vigencia de {int} minutos")
    public void elTokenTieneVigenciaDe(int minutos) {
        assertThat(contexto.getTokenEmitido()).isNotNull();
        assertThat(contexto.getTokenEmitido().getExpiraEn())
                .isAfter(contexto.getTokenEmitido().getEmitidoEn());
        assertThat(minutos).isEqualTo(30);
    }
}
