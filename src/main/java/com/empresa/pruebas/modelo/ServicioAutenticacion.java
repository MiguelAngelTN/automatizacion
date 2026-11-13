package com.empresa.pruebas.modelo;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;


public class ServicioAutenticacion {

    private final Map<String, Usuario> usuarios = new java.util.LinkedHashMap<>();

    /**
     * Registra un usuario nuevo.
     *
     * @throws ExcepcionAutenticacion si el nombre de usuario ya existe
     */
    public void registrar(Usuario usuario) {
        if (usuarios.containsKey(usuario.getNombreUsuario())) {
            throw new ExcepcionAutenticacion(
                    "El usuario " + usuario.getNombreUsuario() + " ya se encuentra registrado");
        }
        usuarios.put(usuario.getNombreUsuario(), usuario);
    }

    /**
     * Autentica a un usuario.
     *
     * @param nombreUsuario usuario a autenticar
     * @param contrasena    contrasena suministrada
     * @return un {@link Token} valido
     * @throws ExcepcionAutenticacion si las credenciales son invalidas o la cuenta esta inactiva
     */
    public Token autenticar(String nombreUsuario, String contrasena) {
        Optional<Usuario> encontrado = Optional.ofNullable(usuarios.get(nombreUsuario));

        if (encontrado.isEmpty()) {
            throw new ExcepcionAutenticacion("Credenciales invalidas para el usuario " + nombreUsuario);
        }

        Usuario usuario = encontrado.get();

        if (!usuario.isActivo()) {
            throw new ExcepcionAutenticacion("El usuario " + nombreUsuario + " se encuentra inactivo");
        }

        if (!usuario.getContrasena().equals(contrasena)) {
            throw new ExcepcionAutenticacion("Credenciales invalidas para el usuario " + nombreUsuario);
        }

        return new Token(UUID.randomUUID().toString(), LocalDateTime.now());
    }

    /**
     * @return la cantidad de usuarios registrados (utilizado por los tests)
     */
    public int cantidadUsuarios() {
        return usuarios.size();
    }
}
