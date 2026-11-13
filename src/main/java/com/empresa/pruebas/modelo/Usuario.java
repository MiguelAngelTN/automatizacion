package com.empresa.pruebas.modelo;

/**
 * Usuario del sistema. Objeto inmutable (valores).
 */
public class Usuario {

    private final String nombreUsuario;
    private final String contrasena;
    private final boolean activo;

    public Usuario(String nombreUsuario, String contrasena, boolean activo) {
        this.nombreUsuario = nombreUsuario;
        this.contrasena = contrasena;
        this.activo = activo;
    }

    public String getNombreUsuario() {
        return nombreUsuario;
    }

    public String getContrasena() {
        return contrasena;
    }

    public boolean isActivo() {
        return activo;
    }
}
