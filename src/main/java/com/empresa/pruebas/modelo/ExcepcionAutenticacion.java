package com.empresa.pruebas.modelo;

/**
 * Error de negocio lanzado cuando las credenciales no son validas.
 *
 * <p>Se usa una excepcion especifica (y no una {@link RuntimeException} generica) para que
 * los tests puedan verificar el <i>tipo</i> de falla y no solo el mensaje.</p>
 */
public class ExcepcionAutenticacion extends RuntimeException {

    private static final long serialVersionUID = 1L;

    public ExcepcionAutenticacion(String mensaje) {
        super(mensaje);
    }
}
