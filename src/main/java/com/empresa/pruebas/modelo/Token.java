package com.empresa.pruebas.modelo;

import java.time.LocalDateTime;
import java.util.Objects;


public class Token {

    /** Vigencia del token en minutos (criterio de aceptacion validado en BDD). */
    public static final int VIGENCIA_MINUTOS = 30;

    private final String valor;
    private final LocalDateTime emitidoEn;
    private final LocalDateTime expiraEn;

    public Token(String valor, LocalDateTime emitidoEn) {
        this.valor = valor;
        this.emitidoEn = emitidoEn;
        this.expiraEn = emitidoEn.plusMinutes(VIGENCIA_MINUTOS);
    }

    public String getValor() {
        return valor;
    }

    public LocalDateTime getEmitidoEn() {
        return emitidoEn;
    }

    public LocalDateTime getExpiraEn() {
        return expiraEn;
    }

    /** @return true si el token sigue dentro de su ventana de vigencia */
    public boolean estaVigente() {
        return LocalDateTime.now().isBefore(expiraEn);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Token otro)) {
            return false;
        }
        return Objects.equals(valor, otro.valor);
    }

    @Override
    public int hashCode() {
        return Objects.hash(valor);
    }
}
